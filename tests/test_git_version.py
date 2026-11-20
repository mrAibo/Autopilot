"""R19: `doctor` печатает версию git и предупреждает ниже 2.22 (трейлер Autopilot-Ticket); `--git-text` подменяет `git --version`."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

AP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "skills", "autopilot", "tools", "ap.py")


class DoctorGit(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="ap-gv-")
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        subprocess.run(["git", "-C", self.root, "init", "-q"], check=True)

    def doctor(self, git_text):
        env = dict(os.environ, AUTOPILOT_NO_UPDATE_CHECK="1", CLAUDE_CONFIG_DIR=self.root)
        r = subprocess.run([sys.executable, AP, "doctor", "--text", "2.1.320", "--git-text", git_text],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, cwd=self.root)
        return r.returncode, r.stdout

    def test_new_git_prints_the_version_without_a_warning(self):
        code, out = self.doctor("git version 2.43.0.windows.1")
        self.assertIn("git: версия 2.43", out)
        self.assertNotIn("ниже 2.22", out)

    def test_old_git_warns_and_does_not_add_code_two(self):
        with_new = self.doctor("git version 2.43.0")[0]
        code, out = self.doctor("git version 2.20.1")
        self.assertIn("git: версия 2.20", out)
        self.assertIn("git ниже 2.22", out)
        self.assertEqual(code, with_new)

    def test_unreadable_version_is_a_line(self):
        code, out = self.doctor("что-то")
        self.assertIn("git: версия не определена", out)


if __name__ == "__main__":
    unittest.main()
