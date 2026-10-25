"""Account-resolved Codex catalog parsing; never use bundled fallback."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import subprocess

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "autopilot" / "tools"))
import codex_capabilities as cap


class ResolvedCatalogTests(unittest.TestCase):
    def test_only_supported_account_models_are_advertised(self):
        raw = json.dumps({"models": [
            {"slug": "gpt-6-luna", "supported_reasoning_levels": [
                {"effort": "low"}, {"effort": "medium"}]},
            {"slug": "gpt-6.1-sol", "supported_reasoning_levels": [
                {"effort": "low"}, {"effort": "ultra"}]},
            {"slug": "../unexpected", "supported_reasoning_levels": [{"effort": "high"}]},
            {"slug": "nothing", "supported_reasoning_levels": []}
        ]})
        result = cap.parse_catalog(raw)
        self.assertEqual(result, {"gpt-6-luna": ["low", "medium"],
                                  "gpt-6.1-sol": ["low", "ultra"]})

    def test_rejects_empty_or_malformed_resolved_catalog(self):
        for value in ("{}", "[]", "garbage", '{"models": []}',
                      '{"models": [{"slug": "test", "supported_reasoning_levels": []}]}'):
            with self.subTest(raw=value), self.assertRaises(cap.CatalogError):
                cap.parse_catalog(value)

    def test_no_bundled_flag_and_no_user_secret_logging(self):
        raw = json.dumps({"models": [
            {"slug": "gpt-6-luna", "supported_reasoning_levels": [{"effort": "low"}]}
        ]})
        with patch.object(cap.subprocess, "run", return_value=subprocess.CompletedProcess(
                args=[], returncode=0, stdout=raw, stderr="")) as proc:
            self.assertEqual(cap.discover("codex.exe")["gpt-6-luna"], ["low"])
        argv = proc.call_args.args[0]
        self.assertEqual(argv, ["codex.exe", "debug", "models"])
        self.assertNotIn("--bundled", argv)

    def test_network_errors_block_and_never_fallback_to_bundled(self):
        with patch.object(cap.subprocess, "run", return_value=subprocess.CompletedProcess(
                args=[], returncode=1, stdout="", stderr="sensitive auth")):
            with self.assertRaises(cap.CatalogError) as ctx:
                cap.discover("codex.exe")
        self.assertNotIn("sensitive", str(ctx.exception))

    def test_atomic_save_and_refuse_provider_overwrite(self):
        with tempfile.TemporaryDirectory() as root_str:
            root = Path(root_str)
            ap = root / ".autopilot"
            ap.mkdir()
            dest = ap / "model-capabilities.json"
            catalog = {"gpt-6-luna": ["low"]}
            got = cap.save_capabilities(root, catalog, "codex.exe")
            self.assertFalse(got["verified_execution"])
            self.assertEqual(json.loads(dest.read_text())["models"], catalog)
            with self.assertRaises(cap.CatalogError):
                cap.save_capabilities(root, catalog, "codex.exe")
            dest.write_text('{"provider": "anthropic"}', encoding="utf-8")
            with self.assertRaises(cap.CatalogError):
                cap.save_capabilities(root, catalog, "codex.exe", overwrite=True)

    def test_missing_run_blocked(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(cap.CatalogError):
                cap.save_capabilities(root, {"gpt-6-luna": ["low"]}, "codex.exe")

if __name__ == "__main__":
    unittest.main()
