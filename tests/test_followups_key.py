"""Доделки после аудита (R03): `gate.key` создаётся целиком или не создаётся."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock

TOOLS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "skills", "autopilot", "tools")
sys.path.insert(0, TOOLS)
import gate_sign  # noqa: E402


class AtomicKey(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        patcher = mock.patch.dict(os.environ, {"AUTOPILOT_HOME": tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.home = Path(tmp.name)
        self.path = self.home / "gate.key"

    def race(self, workers, job):
        gate, results, errors = threading.Barrier(workers), [], []

        def run():
            try:
                gate.wait(timeout=10)
                results.append(job())
            except Exception as exc:  # noqa: BLE001 — тест собирает любой сбой потока
                errors.append(exc)
        threads = [threading.Thread(target=run) for _ in range(workers)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)
        self.assertEqual(errors, [])
        return results

    def test_threads_calling_ensure_key_end_up_with_one_key(self):
        keys = self.race(16, lambda: (gate_sign.ensure_key(), gate_sign.load_key())[1])
        self.assertEqual(len(set(keys)), 1)
        self.assertEqual(len(keys[0]), 32)
        self.assertEqual(gate_sign.load_key(), keys[0])
        self.assertEqual([p.name for p in self.home.iterdir()], ["gate.key"])      # временные файлы убраны

    def test_processes_calling_ensure_key_end_up_with_one_key(self):
        code = ("import sys; sys.path.insert(0, sys.argv[1]); import gate_sign; gate_sign.ensure_key(); "
                "print(gate_sign.load_key().hex())")
        procs = [subprocess.Popen([sys.executable, "-c", code, TOOLS], stdout=subprocess.PIPE, text=True,
                                  env=dict(os.environ, AUTOPILOT_HOME=str(self.home))) for _ in range(6)]
        keys = {p.communicate(timeout=60)[0].strip() for p in procs}
        self.assertEqual(len(keys), 1)
        self.assertEqual(len(next(iter(keys))), 64)

    def test_a_parallel_reader_sees_no_key_or_the_whole_key_never_an_empty_file(self):
        stop, seen, sizes = threading.Event(), set(), set()

        def read():
            while not stop.is_set():
                seen.add(gate_sign.load_key())
                try:
                    sizes.add(self.path.stat().st_size)
                except OSError:
                    pass
        readers = [threading.Thread(target=read) for _ in range(4)]
        for t in readers:
            t.start()
        try:
            self.race(8, gate_sign.ensure_key)
        finally:
            stop.set()
            for t in readers:
                t.join(timeout=10)
        self.assertNotIn(0, sizes)
        self.assertTrue(all(k is None or len(k) == 32 for k in seen), seen)

    def test_a_crash_in_the_middle_of_the_write_leaves_no_key_file(self):
        def broken(fd, *args, **kw):
            os.close(fd)
            raise RuntimeError("диск пропал")
        with mock.patch("gate_sign.os.fdopen", broken):
            with self.assertRaises(RuntimeError):
                gate_sign.ensure_key()
        self.assertFalse(self.path.exists())
        self.assertEqual(list(self.home.iterdir()), [])
        gate_sign.ensure_key()                                                      # и дальше всё работает
        self.assertEqual(len(gate_sign.load_key()), 32)

    def test_an_old_empty_file_is_replaced_by_a_full_key(self):
        self.path.write_bytes(b"")
        self.assertIsNone(gate_sign.load_key())
        gate_sign.ensure_key()
        self.assertEqual(len(gate_sign.load_key()), 32)
        self.assertEqual([p.name for p in self.home.iterdir()], ["gate.key"])

    def test_an_existing_key_is_kept(self):
        gate_sign.ensure_key()
        first = gate_sign.load_key()
        self.race(8, gate_sign.ensure_key)
        self.assertEqual(gate_sign.load_key(), first)


if __name__ == "__main__":
    unittest.main()
