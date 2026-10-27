"""Trusted offline Cargo integration-test gate in temporary standalone Git crates."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / "skills" / "autopilot" / "tools"
sys.path.insert(0, str(TOOLS))
import test_evidence
import worktrees
import controller


@unittest.skipUnless(shutil.which("cargo"), "Rust Cargo not installed on CI host")
class CargoEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Autopilot Cargo Test")
        self.git("config", "user.email", "test@example.invalid")
        (self.root / ".gitignore").write_text(
            ".autopilot/worktrees/\ntarget/\n", encoding="utf-8")
        (self.root / "Cargo.toml").write_text(
            '[package]\nname = "autopilot_fixture"\nversion = "0.1.0"\nedition = "2021"\n',
            encoding="utf-8")
        (self.root / "src").mkdir()
        (self.root / "src" / "lib.rs").write_text(
            "pub fn add(a: i32, b: i32) -> i32 { a - b }\n", encoding="utf-8")
        (self.root / "tests").mkdir()
        (self.root / "tests" / "smoke.rs").write_text(
            "use autopilot_fixture::add;\n"
            "#[test]\nfn adds() { assert_eq!(add(2, 3), 5); }\n",
            encoding="utf-8")
        generate = subprocess.run(
            ["cargo", "generate-lockfile", "--offline",
             "--manifest-path", str(self.root / "Cargo.toml")],
            cwd=self.root, capture_output=True, text=True, timeout=30)
        self.assertEqual(generate.returncode, 0, generate.stderr)
        self.git("add", ".gitignore", "Cargo.toml", "Cargo.lock",
                 "src/lib.rs", "tests/smoke.rs")
        self.git("commit", "-qm", "Cargo test baseline")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()
        self.wt = Path(worktrees.create(self.root, "01")["cwd"])
        self.good_code()

    def git(self, *args):
        result = subprocess.run(
            ["git", "-C", str(self.root), *args], text=True,
            capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def good_code(self):
        (self.wt / "src/lib.rs").write_text(
            "pub fn add(a: i32, b: i32) -> i32 { a + b }\n",
            encoding="utf-8")

    def test_green_is_actual_host_run_and_rechecked(self):
        proof = test_evidence.verify(self.root, "01", self.base, "cargo:smoke")
        self.assertEqual(proof["runner"], "cargo-test")
        self.assertEqual(proof["passed"], 1)
        self.assertEqual(test_evidence.check(self.root, "01", self.base, proof),
                         {"passed": 1, "failed": 0})
        self.assertEqual(controller.verified_tests({"testEvidence": proof}), 1)
        self.assertFalse((self.wt / "target").exists())

    def test_failing_source_blocks_verification(self):
        (self.wt / "src/lib.rs").write_text(
            "pub fn add(a: i32, b: i32) -> i32 { a - b }\n", encoding="utf-8")
        with self.assertRaisesRegex(test_evidence.EvidenceError, "did not pass"):
            test_evidence.verify(self.root, "01", self.base, "cargo:smoke")

    def test_changed_source_or_forged_positive_count_cannot_reuse_receipt(self):
        proof = test_evidence.verify(self.root, "01", self.base, "cargo:smoke")
        with self.assertRaisesRegex(test_evidence.EvidenceError, "count"):
            test_evidence.check(self.root, "01", self.base, dict(proof, passed=999))
        (self.wt / "src/lib.rs").write_text(
            "pub fn add(a: i32, b: i32) -> i32 { a - b }\n", encoding="utf-8")
        with self.assertRaisesRegex(test_evidence.EvidenceError, "changed after tests"):
            test_evidence.check(self.root, "01", self.base, proof)

    def test_baseline_manifest_lock_and_test_must_be_unchanged(self):
        for path, addition in (("Cargo.toml", "# changed\n"),
                               ("Cargo.lock", "# changed\n"),
                               ("tests/smoke.rs", "// changed\n")):
            with self.subTest(path=path):
                target = self.wt / path
                original = target.read_text(encoding="utf-8")
                target.write_text(original + addition, encoding="utf-8")
                with self.assertRaisesRegex(
                        test_evidence.EvidenceError, "Modified Cargo"):
                    test_evidence.verify(self.root, "01", self.base, "cargo:smoke")
                target.write_text(original, encoding="utf-8")

    def test_cargo_dependencies_and_build_scripts_require_separate_review(self):
        manifest = self.wt / "Cargo.toml"
        original = manifest.read_text(encoding="utf-8")
        # Manifest itself is baseline-pinned: any addition is automatically
        # rejected before the parser can authorize arbitrary dependencies.
        for addition in ("\\n[dependencies]\\nserde = \"1\"\\n",
                         "\\n[build-dependencies]\\nhelper = \"1\"\\n"):
            manifest.write_text(original + addition, encoding="utf-8")
            with self.assertRaisesRegex(test_evidence.EvidenceError, "Modified Cargo"):
                test_evidence.verify(self.root, "01", self.base, "cargo:smoke")
        manifest.write_text(original, encoding="utf-8")
        (self.wt / "build.rs").write_text("fn main() {}\\n")
        with self.assertRaisesRegex(test_evidence.EvidenceError, "build scripts"):
            test_evidence.verify(self.root, "01", self.base, "cargo:smoke")

    def test_baseline_committed_dependency_or_custom_target_is_denied(self):
        for suffix, pattern in (
                ("\n[dev-dependencies]\nexternal = \"1\"\n",
                 "external dependencies"),
                ("\n[[test]]\nname = \"smoke\"\npath = \"tests/smoke.rs\"\n",
                 "external dependencies")):
            with self.subTest(suffix=suffix):
                # Create a different deliberately reviewed baseline; the
                # previous prepared worktree remains untouched.
                manifest = self.root / "Cargo.toml"
                original = manifest.read_text(encoding="utf-8")
                manifest.write_text(original + suffix, encoding="utf-8")
                self.git("add", "Cargo.toml")
                self.git("commit", "-qm", "test noneligible tracked Cargo baseline")
                sha = self.git("rev-parse", "HEAD").stdout.strip()
                ticket = "02" if "dependencies" in suffix else "03"
                worktrees.create(self.root, ticket)
                with self.assertRaisesRegex(test_evidence.EvidenceError, pattern):
                    test_evidence.verify(self.root, ticket, sha, "cargo:smoke")
                manifest.write_text(original, encoding="utf-8")
                self.git("add", "Cargo.toml")
                self.git("commit", "-qm", "return to normal Cargo baseline")

    def test_invalid_target_names_and_arguments_are_rejected(self):
        for name in ("cargo:../smoke", "cargo:smoke;echo", "cargo:smoke -- --ignored",
                     "cargo:", "cargo:-smoke", "cargo:smoke/other", "cargo:smoke.rs"):
            with self.subTest(name=name), self.assertRaises(
                    test_evidence.EvidenceError):
                test_evidence.verify(self.root, "01", self.base, name)

    def test_ignored_rust_source_blocks_verification(self):
        ignore = self.wt / ".gitignore"
        ignore.write_text(".autopilot/worktrees/\ntarget/\nhidden_helper.rs\n")
        (self.wt / "hidden_helper.rs").write_text("pub fn hidden() {}\n")
        with self.assertRaisesRegex(test_evidence.EvidenceError, "Ignored Cargo"):
            test_evidence.verify(self.root, "01", self.base, "cargo:smoke")

    def test_ignored_rust_after_success_invalidates_evidence(self):
        proof = test_evidence.verify(self.root, "01", self.base, "cargo:smoke")
        ignore = self.wt / ".gitignore"
        ignore.write_text(".autopilot/worktrees/\ntarget/\nhidden.rs\n")
        (self.wt / "hidden.rs").write_text("pub fn bypass() {}\n")
        with self.assertRaises(test_evidence.EvidenceError):
            test_evidence.check(self.root, "01", self.base, proof)

    def test_cargo_project_config_is_denied_even_when_tracked(self):
        directory = self.wt / ".cargo"
        directory.mkdir()
        (directory / "config.toml").write_text("[build]\n", encoding="utf-8")
        with self.assertRaisesRegex(test_evidence.EvidenceError, "project config"):
            test_evidence.verify(self.root, "01", self.base, "cargo:smoke")

    def test_environment_flags_cannot_replace_fixed_command(self):
        with patch.dict(os.environ, {"CARGO_ENCODED_RUSTFLAGS": "-Zbad",
                                      "CARGO_TARGET_DIR": str(self.root / "hijacked"),
                                      "CARGO_HOME": str(self.root / "hijacked-home")}):
            proof = test_evidence.verify(self.root, "01", self.base, "cargo:smoke")
        self.assertEqual(proof["passed"], 1)
        self.assertFalse((self.root / "hijacked").exists())
        self.assertFalse((self.root / "hijacked-home").exists())

    def test_receipt_runner_mismatch_is_rejected(self):
        proof = test_evidence.verify(self.root, "01", self.base, "cargo:smoke")
        with self.assertRaises(test_evidence.EvidenceError):
            test_evidence.check(self.root, "01", self.base,
                                dict(proof, runner="python-unittest"))
        with self.assertRaises(test_evidence.EvidenceError):
            test_evidence.check(self.root, "01", self.base,
                                dict(proof, runner="cargo-any-command"))

    def test_timeout_and_missing_baseline_integration_file_are_rejected(self):
        with self.assertRaisesRegex(test_evidence.EvidenceError, "timeout"):
            test_evidence.verify(self.root, "01", self.base, "cargo:smoke", timeout=3)
        (self.wt / "tests/smoke.rs").unlink()
        with self.assertRaises(test_evidence.EvidenceError):
            test_evidence.verify(self.root, "01", self.base, "cargo:smoke")


if __name__ == "__main__":
    unittest.main()
