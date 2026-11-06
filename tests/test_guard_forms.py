"""Bash guard forms (R22a, R22o): git paths, bash -c wrappers, restore/checkout ., clean -f."""
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "skills" / "autopilot" / "tools"
sys.path.insert(0, str(TOOLS))
import claude_agent_guard as guard  # noqa: E402


def denied(command):
    return not guard.bash_decision(command)[0]


class GitPathForms(unittest.TestCase):
    def test_git_executable_and_path_forms_are_denied(self):
        for cmd in ("git.exe stash", "GIT.EXE stash", "/usr/bin/git stash",
                    "C:/Program Files/Git/cmd/git.exe stash",
                    '"C:/Program Files/Git/cmd/git.exe" stash'):
            self.assertTrue(denied(cmd), cmd)


class ShellWrappers(unittest.TestCase):
    def test_bash_c_wrappers_are_denied(self):
        for cmd in ('bash -c "git stash"', "sh -c 'git reset --hard'",
                    'bash -lc "git stash"', "bash -c \"sh -c 'git stash'\""):
            self.assertTrue(denied(cmd), cmd)

    def test_shell_text_without_git_command_passes(self):
        for cmd in ('echo "bash -c git"', "bash script.sh"):
            self.assertFalse(denied(cmd), cmd)


class RestoreCheckoutClean(unittest.TestCase):
    def test_whole_tree_restore_and_checkout_are_denied(self):
        for cmd in ("git restore .", "git restore --staged .", "git checkout ."):
            self.assertTrue(denied(cmd), cmd)

    def test_clean_force_forms_are_denied(self):
        for cmd in ("git clean -fd", "git clean -df", "git clean -xdf", "git clean --force"):
            self.assertTrue(denied(cmd), cmd)

    def test_clean_dry_run_passes(self):
        for cmd in ("git clean -n", "git clean --dry-run"):
            self.assertFalse(denied(cmd), cmd)


class AllowedGit(unittest.TestCase):
    def test_everyday_git_commands_pass(self):
        for cmd in ("git commit --only a.py -m x", "git status", "git diff",
                    "git diff --cached --stat", "git log --oneline -3",
                    "git restore a.py", "git checkout main"):
            self.assertFalse(denied(cmd), cmd)


class QuotedAndMessages(unittest.TestCase):
    def test_quoted_or_message_text_passes(self):
        for cmd in ('git commit -m "no git stash here"', 'echo "git clean -fd"',
                    'echo "git restore ."'):
            self.assertFalse(denied(cmd), cmd)


class SeparatorsOutsideQuotes(unittest.TestCase):
    def test_forms_after_separators_are_denied(self):
        for cmd in ("echo a && git.exe stash", 'ls; bash -c "git restore ."',
                    "git status | git clean -fd"):
            self.assertTrue(denied(cmd), cmd)


if __name__ == "__main__":
    unittest.main()
