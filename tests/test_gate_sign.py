"""gate_sign: HMAC key and signatures, key location via AUTOPILOT_HOME."""
import base64
import contextlib
import hashlib
import hmac
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "autopilot" / "tools"))
import gate_sign


def canonical(payload):
    body = {k: v for k, v in payload.items() if k != "sig"}
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")


def literal_signature(data, payload):
    """HMAC with the raw file bytes as the key: what a copy that does not know `dpapi:` would do."""
    return hmac.new(data, canonical(payload), hashlib.sha256).hexdigest()


class GateSignTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        patcher = mock.patch.dict(os.environ, {"AUTOPILOT_HOME": tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.home = Path(tmp.name)

    def test_key_path_follows_autopilot_home(self):
        self.assertEqual(gate_sign.key_path(), self.home / "gate.key")

    def test_no_key_is_not_created_silently(self):
        self.assertIsNone(gate_sign.load_key())
        self.assertFalse(gate_sign.verify({"a": 1}, "00"))
        self.assertFalse((self.home / "gate.key").exists())
        with self.assertRaises(ValueError):
            gate_sign.sign({"a": 1})

    def test_ensure_key_creates_once_with_private_mode(self):
        path = gate_sign.ensure_key()
        first = gate_sign.load_key()
        self.assertEqual(len(first), 32)
        self.assertEqual(gate_sign.load_key(), first)
        gate_sign.ensure_key()
        self.assertEqual(gate_sign.load_key(), first)
        if os.name == "posix":
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_empty_key_file_counts_as_missing_and_is_recreated(self):
        (self.home / "gate.key").write_bytes(b"")
        self.assertIsNone(gate_sign.load_key())
        gate_sign.ensure_key()
        self.assertEqual(len(gate_sign.load_key()), 32)

    def test_run_mark_covers_slug_and_start_but_not_the_renamed_dir(self):
        gate_sign.ensure_key()
        wip = {"slug": "s", "startedAt": "t0", "dir": "2026-11-03-s--wip"}
        self.assertEqual(gate_sign.run_mark(wip), gate_sign.run_mark(dict(wip, dir="2026-11-03-s")))
        self.assertNotEqual(gate_sign.run_mark(wip), gate_sign.run_mark(dict(wip, startedAt="t1")))
        self.assertEqual(gate_sign.run_status(dict(wip, gateMark=gate_sign.run_mark(wip), dir="renamed")),
                         "signed")

    def test_sign_verify_detects_tampering_and_ignores_sig_field(self):
        gate_sign.ensure_key()
        payload = {"b": 2, "a": [1, "x"]}
        sig = gate_sign.sign(payload)
        self.assertTrue(gate_sign.verify({"a": [1, "x"], "b": 2, "sig": sig}, sig))
        self.assertFalse(gate_sign.verify({"b": 3, "a": [1, "x"]}, sig))
        self.assertFalse(gate_sign.verify(payload, "0" * 64))
        self.assertFalse(gate_sign.verify(payload, None))

    def test_other_key_does_not_verify(self):
        gate_sign.ensure_key()
        sig = gate_sign.sign({"a": 1})
        (self.home / "gate.key").write_bytes(b"another key".ljust(32, b"!"))
        self.assertFalse(gate_sign.verify({"a": 1}, sig))


@unittest.skipUnless(os.name == "nt", "DPAPI exists only on Windows")
class DpapiKeyTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        patcher = mock.patch.dict(os.environ, {"AUTOPILOT_HOME": tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.path = Path(tmp.name) / "gate.key"

    def test_new_key_is_a_dpapi_block_that_reads_back_as_32_bytes(self):
        gate_sign.ensure_key()
        self.assertTrue(self.path.read_bytes().startswith(b"dpapi:"))
        key = gate_sign.load_key()
        self.assertEqual(len(key), 32)
        self.assertNotIn(key, self.path.read_bytes())          # the plain bytes are not in the file
        self.assertTrue(gate_sign.verify({"a": 1}, gate_sign.sign({"a": 1})))

    def test_old_plain_key_is_read_and_rewritten_by_ensure_key_with_the_same_bytes(self):
        plain = bytes(range(32))
        self.path.write_bytes(plain)
        self.assertEqual(gate_sign.load_key(), plain)           # a read alone never rewrites
        self.assertEqual(self.path.read_bytes(), plain)
        gate_sign.ensure_key()
        self.assertTrue(self.path.read_bytes().startswith(b"dpapi:"))
        self.assertEqual(gate_sign.load_key(), plain)           # signatures of old gates stay valid

    def test_dpapi_calls_from_many_threads_do_not_mix_their_prototypes(self):
        # R03: the ctypes prototypes are shared by all threads; a call used to meet another thread's Blob class
        # (ArgumentError), which read as "the key is unreadable" in a parallel init.
        errors = []

        def run():
            for _ in range(100):
                try:
                    self.assertEqual(gate_sign._dpapi(gate_sign._dpapi(b"k" * 32, True), False), b"k" * 32)
                except Exception as exc:  # noqa: BLE001 — the test collects any thread failure
                    errors.append(type(exc).__name__)

        threads = [threading.Thread(target=run) for _ in range(8)]
        interval = sys.getswitchinterval()
        sys.setswitchinterval(1e-6)                                             # widens the window, adds no wait
        try:
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=120)
        finally:
            sys.setswitchinterval(interval)
        self.assertEqual(errors, [])

    def test_dpapi_failure_keeps_the_plain_file_and_warns_once(self):
        gate_sign._warned.clear()
        err = io.StringIO()
        with mock.patch.object(gate_sign, "_dpapi", side_effect=OSError("no dpapi")), \
                contextlib.redirect_stderr(err):
            gate_sign.ensure_key()
            gate_sign._protected(b"x" * 32)
        self.assertEqual(len(self.path.read_bytes()), 32)
        self.assertEqual(len(gate_sign.load_key()), 32)
        self.assertEqual(len(err.getvalue().strip().splitlines()), 1)


class KeyRaceTests(unittest.TestCase):
    """An old empty key is initialized atomically: one whole key wins, a dead winner is retried."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        patcher = mock.patch.dict(os.environ, {"AUTOPILOT_HOME": tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.home = Path(tmp.name)
        self.path = self.home / "gate.key"
        gate_sign._warned.clear()

    def test_threads_racing_over_an_old_empty_key_end_up_with_one_whole_key(self):
        self.path.write_bytes(b"")
        workers = 8
        start, keys, errors = threading.Barrier(workers), [], []

        def run():
            try:
                start.wait(timeout=10)
                gate_sign.ensure_key()
                keys.append(gate_sign.load_key())
            except BaseException as exc:  # noqa: BLE001 — the test collects any thread failure
                errors.append(exc)

        threads = [threading.Thread(target=run) for _ in range(workers)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=60)
        self.assertEqual(errors, [])
        self.assertEqual(len(keys), workers)
        self.assertTrue(all(isinstance(key, bytes) and len(key) == 32 for key in keys), keys)
        self.assertEqual(len(set(keys)), 1)                                     # no empty or partial winner
        self.assertEqual([p.name for p in self.home.iterdir()], ["gate.key"])   # no temp files left

    def test_reinit_keeps_the_key_and_the_old_signatures(self):
        gate_sign.ensure_key()
        key = gate_sign.load_key()
        payload = {"ticket": "01", "routing": {"model": "haiku", "effort": "low"}}
        sig = gate_sign.sign(payload)
        gate_sign.ensure_key()
        self.assertEqual(gate_sign.load_key(), key)
        self.assertTrue(gate_sign.verify(payload, sig))
        self.assertEqual([p.name for p in self.home.iterdir()], ["gate.key"])

    def test_a_key_written_after_the_empty_check_is_given_back_not_lost(self):
        # The stale-empty interleaving: the racer stats an empty file, a winner writes a key,
        # then the racer renames that key aside. The claim must put the real key back.
        key = b"k" * 32
        self.path.write_bytes(key)
        self.assertFalse(gate_sign._claim_empty(self.path))
        self.assertEqual(self.path.read_bytes(), key)
        self.assertEqual([p.name for p in self.home.iterdir()], ["gate.key"])

    def test_a_racer_arriving_mid_claim_never_displaces_a_whole_key(self):
        # R03: a racer with a stale "the file is empty" finds the whole key already there. A third racer runs
        # ensure_key at the first directory change of the claim (whichever call makes it) and once more after
        # it; the key must stay and both racers must read that same key.
        key = b"k" * 32
        self.path.write_bytes(key)
        started, seen = [], []

        def racer():
            gate_sign.ensure_key()
            seen.append(gate_sign.load_key())

        def after(real):
            def wrapper(*args, **kwargs):
                result = real(*args, **kwargs)
                if not started:
                    started.append(True)
                    racer()
                return result
            return wrapper

        with contextlib.ExitStack() as stack:
            for name in ("link", "rename", "replace", "unlink", "remove"):
                stack.enter_context(mock.patch.object(os, name, after(getattr(os, name))))
            self.assertFalse(gate_sign._claim_empty(self.path))
        racer()
        self.assertEqual(seen, [key, key])
        self.assertEqual(gate_sign.load_key(), key)
        self.assertEqual([p.name for p in self.home.iterdir()], ["gate.key"])   # the claim is gone too

    def busy_claim(self, failures):
        """Path.unlink that refuses gate.key.claim `failures` times, as a Windows reader holding it would."""
        real, left = Path.unlink, [failures]

        def unlink(path, missing_ok=False):
            if path.name == "gate.key.claim" and left[0] > 0:
                left[0] -= 1
                raise PermissionError(13, "the file is in use")
            return real(path, missing_ok=missing_ok)

        return mock.patch.object(Path, "unlink", unlink)

    def test_a_claim_that_is_busy_for_a_moment_is_removed_by_retry(self):
        self.path.write_bytes(b"")
        with mock.patch.object(gate_sign.time, "sleep", lambda _seconds: None), self.busy_claim(3):
            gate_sign.ensure_key()
        self.assertEqual(len(gate_sign.load_key()), 32)
        self.assertEqual([p.name for p in self.home.iterdir()], ["gate.key"])   # the claim is gone

    def test_a_claim_that_stays_busy_is_a_clear_error_and_the_key_is_kept(self):
        key = b"k" * 32
        self.path.write_bytes(key)
        with mock.patch.object(gate_sign.time, "sleep", lambda _seconds: None), self.busy_claim(10 ** 6), \
                self.assertRaises(OSError) as caught:
            gate_sign._claim_empty(self.path)                                   # a stale racer under a whole key
        self.assertNotIsInstance(caught.exception, PermissionError)             # not the raw Windows error
        self.assertIn("gate.key.claim", str(caught.exception))
        self.assertEqual(self.path.read_bytes(), key)                           # the key is neither lost nor replaced

        self.path.write_bytes(b"")
        (self.home / "gate.key.claim").unlink()
        with mock.patch.object(gate_sign.time, "sleep", lambda _seconds: None), self.busy_claim(10 ** 6), \
                self.assertRaises(OSError) as caught:
            gate_sign.ensure_key()
        self.assertNotIsInstance(caught.exception, PermissionError)
        self.assertIn("gate.key.claim", str(caught.exception))

    def test_a_stuck_claim_over_a_key_that_became_whole_gives_the_key_back(self):
        # R03: the racer's stat saw an empty file, the claim stays busy, but the key is whole by now
        key = b"k" * 32
        self.path.write_bytes(b"")

        def stuck(path):
            path.write_bytes(key)                                               # the winner finishes meanwhile
            raise OSError("не удалось удалить заявку gate.key.claim")

        with mock.patch.object(gate_sign, "_claim_empty", stuck):
            self.assertEqual(gate_sign.ensure_key(), self.path)
        self.assertEqual(gate_sign.load_key(), key)                             # the key itself is unchanged

    def whole_key_after_claim(self, key):
        """os.link that, right after the claim link is made, lets a winner fill the key (same inode as the claim)."""
        real = os.link

        def link(src, dst, *args, **kwargs):
            real(src, dst, *args, **kwargs)
            if str(dst).endswith("gate.key.claim"):
                self.path.write_bytes(key)
        return mock.patch.object(os, "link", link)

    def test_a_claim_busy_over_a_whole_key_is_retried_once_more_and_the_key_is_kept(self):
        # R03: the claim stays busy through the whole retry, then frees up: ensure_key removes it on its own
        key = b"k" * 32
        self.path.write_bytes(b"")
        with mock.patch.object(gate_sign.time, "sleep", lambda _seconds: None), self.busy_claim(100), \
                self.whole_key_after_claim(key), contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(gate_sign.ensure_key(), self.path)
        self.assertEqual(gate_sign.load_key(), key)                             # same key bytes
        self.assertEqual([p.name for p in self.home.iterdir()], ["gate.key"])   # the claim is gone
        self.assertEqual(err.getvalue(), "")

    def test_a_claim_that_stays_busy_over_a_whole_key_is_named_in_one_stderr_line(self):
        # R03: the key comes back, the claim stays: one line with its name and the word "удали"
        key = b"k" * 32
        self.path.write_bytes(b"")
        with mock.patch.object(gate_sign.time, "sleep", lambda _seconds: None), self.busy_claim(10 ** 6), \
                self.whole_key_after_claim(key), contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(gate_sign.ensure_key(), self.path)
        self.assertEqual(gate_sign.load_key(), key)
        self.assertTrue((self.home / "gate.key.claim").exists())                # still there, for the user to remove
        lines = err.getvalue().strip().splitlines()
        self.assertEqual(len(lines), 1, lines)
        self.assertIn("gate.key.claim", lines[0])
        self.assertIn("удали", lines[0])

    def test_an_abandoned_claim_is_named_in_the_error_with_the_way_out(self):
        # R03: a killed claim holder leaves gate.key.claim; the error must say which file to delete.
        self.path.write_bytes(b"")
        (self.home / "gate.key.claim").write_bytes(b"")
        with mock.patch.object(gate_sign.time, "sleep", lambda _seconds: None), self.assertRaises(OSError) as caught:
            gate_sign.ensure_key()
        text = str(caught.exception)
        self.assertIn("gate.key.claim", text)
        self.assertIn("удал", text)                                             # "delete it" (убит / удали)
        self.assertIn("убит", text)
        self.assertEqual(self.path.read_bytes(), b"")                           # nothing was touched

    def test_a_held_claim_makes_every_other_racer_back_off(self):
        self.path.write_bytes(b"")
        (self.home / "gate.key.claim").write_bytes(b"")                         # someone else is removing the file
        self.assertFalse(gate_sign._claim_empty(self.path))
        self.assertTrue(self.path.exists())
        self.assertTrue((self.home / "gate.key.claim").exists())                # not ours: left for its holder

    def test_claiming_a_really_empty_file_removes_it_whole(self):
        self.path.write_bytes(b"")
        self.assertTrue(gate_sign._claim_empty(self.path))
        self.assertEqual(list(self.home.iterdir()), [])

    def test_a_winner_that_dies_after_claiming_the_empty_file_is_retried(self):
        self.path.write_bytes(b"")
        original = gate_sign._create_key_atomically
        calls = []

        def dies_once(target, data):
            calls.append(target)
            if len(calls) == 1:
                return  # claimed the empty file, then died before writing any key
            original(target, data)

        with mock.patch.object(gate_sign.time, "sleep", lambda _seconds: None), \
                mock.patch.object(gate_sign, "_create_key_atomically", side_effect=dies_once):
            gate_sign.ensure_key()
        self.assertEqual(len(calls), 2)                                         # the loser retried instead of returning
        self.assertEqual(len(gate_sign.load_key()), 32)
        self.assertEqual([p.name for p in self.home.iterdir()], ["gate.key"])


class KeyUnreadableTests(unittest.TestCase):
    """A damaged or foreign key is an explicit error, never raw bytes trusted as the HMAC key."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        patcher = mock.patch.dict(os.environ, {"AUTOPILOT_HOME": tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.home = Path(tmp.name)
        self.path = self.home / "gate.key"
        gate_sign._warned.clear()

    def assert_unreadable(self, stored):
        """The file is reported, cannot sign/verify, and ensure_key never silently replaces it."""
        self.path.write_bytes(stored)
        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(OSError):
            gate_sign.ensure_key()                                              # init stops with a clear reason
        self.assertIn("не читается", err.getvalue())
        self.assertEqual(self.path.read_bytes(), stored)                        # the broken key is kept, not replaced
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertIsNone(gate_sign.load_key())
            self.assertFalse(gate_sign.verify({"a": 1}, literal_signature(stored, {"a": 1})))
        with self.assertRaises(ValueError) as caught:
            gate_sign.sign({"a": 1})
        self.assertEqual(str(caught.exception), gate_sign.KEY_UNREADABLE_MESSAGE)
        self.assertEqual([p.name for p in self.home.iterdir()], ["gate.key"])   # and no temp files are left

    def test_short_plain_file_is_not_used_as_an_hmac_key(self):
        self.assert_unreadable(b"short-key")

    def test_truncated_plain_key_fails_closed(self):
        self.assert_unreadable(bytes(range(16)))

    def test_dpapi_block_on_another_os_is_unreadable(self):
        stored = gate_sign.DPAPI_PREFIX + base64.b64encode(b"windows blob")
        with mock.patch.object(gate_sign, "IS_WINDOWS", False), \
                mock.patch.object(gate_sign, "_dpapi", side_effect=AssertionError("must not touch DPAPI")):
            self.assert_unreadable(stored)

    def test_dpapi_block_of_another_windows_user_is_unreadable(self):
        stored = gate_sign.DPAPI_PREFIX + base64.b64encode(b"someone else's blob")
        with mock.patch.object(gate_sign, "IS_WINDOWS", True), \
                mock.patch.object(gate_sign, "_dpapi", side_effect=OSError("wrong user")):
            self.assert_unreadable(stored)

    def test_empty_file_is_missing_not_damaged(self):
        self.path.write_bytes(b"")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertIsNone(gate_sign.load_key())
        self.assertNotIn("не читается", err.getvalue())
        gate_sign.ensure_key()
        self.assertEqual(len(gate_sign.load_key()), 32)


class MockedDpapiTests(unittest.TestCase):
    """DPAPI behavior without the real Windows API: a reversible mock plus the platform flag."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        patcher = mock.patch.dict(os.environ, {"AUTOPILOT_HOME": tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.path = Path(tmp.name) / "gate.key"
        gate_sign._warned.clear()

    @staticmethod
    def fake_dpapi(data, protect):
        if protect:
            return b"MOCK:" + data
        if data.startswith(b"MOCK:"):
            return data[len(b"MOCK:"):]
        raise OSError("not this user's DPAPI block")

    def test_new_key_is_wrapped_and_signs_without_the_real_dpapi(self):
        with mock.patch.object(gate_sign, "IS_WINDOWS", True), \
                mock.patch.object(gate_sign, "_dpapi", side_effect=self.fake_dpapi):
            gate_sign.ensure_key()
            stored = self.path.read_bytes()
            self.assertTrue(stored.startswith(gate_sign.DPAPI_PREFIX))
            key = gate_sign.load_key()
            self.assertEqual(len(key), 32)
            self.assertNotIn(key, stored)                                       # the plain key is not in the file
            payload = {"b": 2, "a": 1}
            sig = gate_sign.sign(payload)
            self.assertTrue(gate_sign.verify(payload, sig))
            self.assertFalse(gate_sign.verify({"a": 2}, sig))
            self.assertEqual(gate_sign.load_key(), key)

    def test_old_plain_key_is_rewritten_but_its_signatures_stay_valid(self):
        plain = bytes(range(32))
        payload = {"ticket": "02", "routing": {"model": "x"}}
        self.path.write_bytes(plain)
        with mock.patch.object(gate_sign, "IS_WINDOWS", True), \
                mock.patch.object(gate_sign, "_dpapi", side_effect=self.fake_dpapi):
            self.assertEqual(gate_sign.load_key(), plain)                       # a read alone never rewrites
            sig = gate_sign.sign(payload)
            gate_sign.ensure_key()
            self.assertTrue(self.path.read_bytes().startswith(gate_sign.DPAPI_PREFIX))
            self.assertEqual(gate_sign.load_key(), plain)                       # same key: old gates stay valid
            self.assertTrue(gate_sign.verify(payload, sig))

    def test_the_rewrite_is_skipped_when_the_block_does_not_read_back(self):
        plain = bytes(range(32))
        self.path.write_bytes(plain)

        def broken(data, protect):
            if protect:
                return b"BROKEN" + data
            raise OSError("cannot unwrap")

        err = io.StringIO()
        with mock.patch.object(gate_sign, "IS_WINDOWS", True), \
                mock.patch.object(gate_sign, "_dpapi", side_effect=broken), \
                contextlib.redirect_stderr(err):
            gate_sign.ensure_key()
            self.assertEqual(self.path.read_bytes(), plain)                     # a working key is not replaced
            self.assertEqual(gate_sign.load_key(), plain)                       # signing keeps working
        self.assertIn("DPAPI", err.getvalue())


class RunRecordTests(unittest.TestCase):
    """The 'run started signed' fact lives under $AUTOPILOT_HOME/runs, keyed by project root."""

    def setUp(self):
        home, proj = tempfile.TemporaryDirectory(), tempfile.TemporaryDirectory()
        self.addCleanup(home.cleanup)
        self.addCleanup(proj.cleanup)
        patcher = mock.patch.dict(os.environ, {"AUTOPILOT_HOME": home.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.home, self.root = Path(home.name), proj.name
        gate_sign.ensure_key()
        self.state = {"slug": "s", "startedAt": "t0", "strictRouting": True, "finishedAt": None}
        self.state["gateMark"] = gate_sign.run_mark(self.state)

    def status(self, **edit):
        state = dict(self.state, **edit)
        return gate_sign.run_status(state, self.root)

    def test_record_lives_under_runs_keyed_by_root_hash(self):
        gate_sign.write_run_record(self.root, self.state)
        key = hashlib.sha256(os.path.normcase(os.path.realpath(self.root)).encode("utf-8")).hexdigest()
        self.assertTrue((self.home / "runs" / key).is_file())

    def test_no_record_is_unsigned_even_with_key_and_strict_state(self):
        # A key made for another project must not stop an old unsigned run here.
        self.assertEqual(self.status(gateMark=None), "unsigned")
        self.assertEqual(self.status(), "unsigned")  # moved or renamed project: lookup by hash misses

    def test_crash_between_write_and_replace_leaves_the_old_record_whole(self):
        gate_sign.write_run_record(self.root, self.state)
        path = gate_sign.record_path(self.root)
        before = path.read_text(encoding="utf-8")
        with mock.patch.object(gate_sign.state_io, "replace_with_retry", side_effect=OSError("crash")):
            with self.assertRaises(OSError):
                gate_sign.write_run_record(self.root, dict(self.state, finishedAt="2026-11-03"))
        self.assertEqual(path.read_text(encoding="utf-8"), before)
        self.assertEqual([p.name for p in path.parent.iterdir()], [path.name])   # no stray temp file
        self.assertEqual(self.status(), "signed")

    def test_crash_on_the_first_write_leaves_no_record_at_all(self):
        with mock.patch.object(gate_sign.state_io, "replace_with_retry", side_effect=OSError("crash")):
            with self.assertRaises(OSError):
                gate_sign.write_run_record(self.root, self.state)
        self.assertFalse(gate_sign.record_path(self.root).exists())
        self.assertEqual(self.status(), "unsigned")

    def test_matching_record_is_signed(self):
        gate_sign.write_run_record(self.root, self.state)
        self.assertEqual(self.status(), "signed")

    def test_state_that_disagrees_with_the_record_is_forged(self):
        gate_sign.write_run_record(self.root, self.state)
        for edit in ({"strictRouting": False}, {"gateMark": None}, {"gateMark": "00"},
                     {"finishedAt": "2026-11-03"}, {"startedAt": "t9"}, {"slug": "other"}):
            with self.subTest(edit=edit):
                self.assertEqual(self.status(**edit), "forged")

    def test_finish_record_allows_finished_state_and_reopen_record_restores(self):
        gate_sign.write_run_record(self.root, dict(self.state, finishedAt="2026-11-03"))
        self.assertEqual(self.status(finishedAt="2026-11-03"), "signed")
        self.assertEqual(self.status(), "forged")
        gate_sign.write_run_record(self.root, self.state)
        self.assertEqual(self.status(), "signed")

    def test_tampered_or_unreadable_record_is_forged(self):
        gate_sign.write_run_record(self.root, self.state)
        path = gate_sign.record_path(self.root)
        path.write_text(path.read_text(encoding="utf-8").replace("false", "true"), encoding="utf-8")
        self.assertEqual(self.status(), "forged")
        path.write_text("{", encoding="utf-8")
        self.assertEqual(self.status(), "forged")

    def test_remove_record_and_missing_key(self):
        gate_sign.write_run_record(self.root, self.state)
        gate_sign.remove_run_record(self.root)
        self.assertEqual(self.status(), "unsigned")
        gate_sign.remove_run_record(self.root)  # already gone: not an error
        (self.home / "gate.key").unlink()
        with self.assertRaises(ValueError):
            gate_sign.write_run_record(self.root, self.state)

    def test_without_root_only_the_state_mark_counts(self):
        self.assertEqual(gate_sign.run_status(self.state), "signed")
        self.assertEqual(gate_sign.run_status(dict(self.state, gateMark=None)), "unsigned")
        self.assertEqual(gate_sign.run_status(dict(self.state, gateMark="00")), "forged")


if __name__ == "__main__":
    unittest.main()
