"""gate_sign: HMAC key and signatures, key location via AUTOPILOT_HOME."""
import hashlib
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "autopilot" / "tools"))
import gate_sign


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
        first = path.read_bytes()
        self.assertEqual(len(first), 32)
        self.assertEqual(gate_sign.ensure_key().read_bytes(), first)
        if os.name == "posix":
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_empty_key_file_counts_as_missing_and_is_recreated(self):
        (self.home / "gate.key").write_bytes(b"")
        self.assertIsNone(gate_sign.load_key())
        self.assertEqual(len(gate_sign.ensure_key().read_bytes()), 32)
        self.assertIsNotNone(gate_sign.load_key())

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
        (self.home / "gate.key").write_bytes(b"another key")
        self.assertFalse(gate_sign.verify({"a": 1}, sig))


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
