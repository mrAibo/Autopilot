"""gate_sign: HMAC key and signatures, key location via AUTOPILOT_HOME."""
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


if __name__ == "__main__":
    unittest.main()
