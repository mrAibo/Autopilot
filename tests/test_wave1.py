"""Волна 1: отпечаток таска, accept-edit, пути машины, хук Bash, версия Claude Code, документы."""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import test_ap

SKILL = Path(test_ap.SKILL)
REPO = SKILL.parents[1]
TOOLS = SKILL / "tools"
sys.path.insert(0, str(TOOLS))
import agent_profiles  # noqa: E402
import ap  # noqa: E402
import claude_agent_guard as guard  # noqa: E402
import state_io  # noqa: E402

TEXT = "# 01 — Каркас\n\n**Зона:** `src/`\n"
USER_WIN = "C:" + "\\Users\\" + "bob\\proj\\a.py"      # собрано из частей: тест не содержит путей машины
USER_NIX = "/ho" + "me/bob/proj/a.py"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def doc(*parts):
    return (REPO.joinpath(*parts)).read_text(encoding="utf-8")


class Fingerprint(unittest.TestCase):
    def test_line_endings_bom_and_trailing_spaces_do_not_matter(self):
        lf = TEXT.encode()
        same = (TEXT.replace("\n", "\r\n")).encode()
        bom = b"\xef\xbb\xbf" + lf
        spaces = TEXT.replace("\n", "  \t\n").encode()
        self.assertEqual({state_io.ticket_fingerprint(x) for x in (lf, same, bom, spaces)},
                         {state_io.ticket_fingerprint(lf)})
        self.assertNotEqual(state_io.ticket_fingerprint(lf),
                            state_io.ticket_fingerprint((TEXT + "x\n").encode()))

    def test_old_raw_byte_and_crlf_variants_are_accepted(self):
        lf = TEXT.encode()
        crlf = TEXT.replace("\n", "\r\n").encode()
        self.assertTrue(state_io.fingerprint_matches(sha(lf), lf))
        self.assertTrue(state_io.fingerprint_matches(sha(crlf), lf))  # published CRLF, file is LF now
        self.assertTrue(state_io.fingerprint_matches(sha(lf), crlf))
        self.assertTrue(state_io.fingerprint_matches(sha(b"\xef\xbb\xbf" + crlf), lf))
        self.assertFalse(state_io.fingerprint_matches(sha(lf), (TEXT + "x\n").encode()))
        self.assertFalse(state_io.fingerprint_matches(None, lf))


class Wave1Run(unittest.TestCase):
    def setUp(self):
        self.h = test_ap.Run("test_skip_needs_a_reason")
        self.h.setUp()
        self.addCleanup(self.h.tearDown)
        self.h.plan(strict=True)
        self.path = os.path.join(self.h.dir, "tickets", "01-karkas.md")

    def raw(self):
        with open(self.path, "rb") as f:
            return f.read()

    def put(self, data):
        with open(self.path, "wb") as f:
            f.write(data)

    def mutate(self, fn):
        path = os.path.join(self.h.a, "state.js")
        state = state_io.read_state_file(path)
        fn({t["id"]: t for t in state["tickets"]})
        state_io.write_state_file(path, state)

    def publish_done(self):
        self.assertEqual(self.h.ap("tickets")[0], 0)
        self.mutate(lambda t: t["01"].update(status="done", commit="abc1234"))

    def tk(self):
        return {t["id"]: t for t in self.h.state()["tickets"]}["01"]

    def test_line_endings_do_not_reset_a_done_ticket(self):
        self.publish_done()
        fp = self.tk()["fingerprint"]
        lf = self.raw().replace(b"\r\n", b"\n")   # harness writes CRLF on Windows
        for data in (lf.replace(b"\n", b"\r\n"), b"\xef\xbb\xbf" + lf, lf.replace(b"\n", b"  \n")):
            self.put(data)
            code, out = self.h.ap("tickets")
            self.assertEqual(code, 0, out)
            self.assertEqual((self.tk()["status"], self.tk()["commit"], self.tk()["fingerprint"]),
                             ("done", "abc1234", fp))

    def test_ticket_published_by_old_code_stays_done_with_new_fingerprint(self):
        self.put(self.raw().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))   # published with CRLF
        crlf = self.raw()
        self.publish_done()
        for old in (sha(crlf), sha(crlf.replace(b"\r\n", b"\n"))):
            self.put(crlf.replace(b"\r\n", b"\n"))                              # file became LF
            self.mutate(lambda t, old=old: t["01"].update(fingerprint=old))
            code, out = self.h.ap("tickets")
            self.assertEqual(code, 0, out)
            self.assertEqual(self.tk()["status"], "done")
            self.assertEqual(self.tk()["fingerprint"], state_io.ticket_fingerprint(self.raw()))

    def test_edited_done_ticket_stops_until_accept_edit(self):
        self.publish_done()
        self.put(self.raw() + b"\n- [ ] new criterion\n")
        before = self.h.state()
        code, out = self.h.ap("tickets")
        self.assertNotEqual(code, 0)
        self.assertIn("ticket 01 accept-edit --note", out)
        self.assertEqual(self.h.state()["tickets"], before["tickets"])
        self.assertNotEqual(self.h.ap("ticket", "01", "accept-edit")[0], 0)              # no --note
        self.assertNotEqual(self.h.ap("ticket", "02", "accept-edit", "--note", "x")[0], 0)  # not done
        code, out = self.h.ap("ticket", "01", "accept-edit", "--note", "new criterion")
        self.assertEqual(code, 0, out)
        code, out = self.h.ap("tickets")
        self.assertEqual(code, 0, out)
        self.assertEqual((self.tk()["status"], self.tk()["commit"]), ("done", "abc1234"))
        self.assertNotIn("acceptedFingerprint", self.tk())
        self.assertEqual(self.tk()["fingerprint"], state_io.ticket_fingerprint(self.raw()))

    def test_edited_pending_ticket_still_resets(self):
        self.assertEqual(self.h.ap("tickets")[0], 0)
        self.mutate(lambda t: t["01"].update(status="review"))
        self.put(self.raw() + b"\n- [ ] more\n")
        self.assertEqual(self.h.ap("tickets")[0], 0)
        self.assertEqual(self.tk()["status"], "pending")

    def test_plan_models_accepts_old_fingerprint(self):
        self.assertEqual(self.h.ap("tickets")[0], 0)
        self.mutate(lambda t: t["01"].update(fingerprint=sha(self.raw())))        # old raw-byte value
        code, out = self.h.ap("plan-models", "--provider", "openai")
        self.assertEqual(code, 0, out)
        self.put(self.raw().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))      # CRLF, same meaning
        code, out = self.h.ap("plan-models", "--provider", "openai")
        self.assertEqual(code, 0, out)

    def test_machine_paths_refuse_publication_and_leave_state(self):
        self.assertEqual(self.h.ap("tickets")[0], 0)
        state_path = os.path.join(self.h.a, "state.js")
        with open(state_path, "rb") as f:
            before = f.read()
        for rel, bad in (("tickets/01-karkas.md", USER_WIN), ("spec.md", USER_NIX)):
            target = os.path.join(self.h.dir, rel)
            original = None
            if os.path.exists(target):
                with open(target, "rb") as f:
                    original = f.read()
            with open(target, "wb") as f:
                f.write(("строка\nпуть " + bad + "\n").encode())
            code, out = self.h.ap("tickets")
            self.assertNotEqual(code, 0)
            self.assertIn(os.path.basename(rel), out)
            self.assertIn("строка 2", out)
            with open(state_path, "rb") as f:
                self.assertEqual(f.read(), before)
            if original is None:
                os.unlink(target)
            else:
                with open(target, "wb") as f:
                    f.write(original)
        self.h.write("spec.md", "пример <repo>/src и <scratchpad>/out\n")
        self.assertEqual(self.h.ap("tickets")[0], 0)

    def test_machine_path_hits_returns_line_and_match(self):
        self.assertEqual(ap.machine_path_hits("ok\n<repo>/a\n" + USER_NIX)[0][0], 3)
        self.assertEqual(ap.machine_path_hits("<repo>/a <scratchpad>/b"), [])


class BashGuard(unittest.TestCase):
    def test_bash_decision(self):
        for cmd in ("git stash", "git stash pop", "git reset --hard", "git -C x stash",
                    "cd a && git reset HEAD~1", "ls | git stash", "git checkout -- a.py"):
            self.assertFalse(guard.bash_decision(cmd)[0], cmd)
        for cmd in ("git commit --only a b -m x", "git checkout main", "git diff --cached --stat",
                    "echo stash", "git status; ls",
                    'git commit -m "a; git reset notes"', 'git commit -m "x\nrun git stash later"',
                    "git commit -m 'a && git stash | b & c'", r'git commit -m "say \"; git stash\""'):
            self.assertTrue(guard.bash_decision(cmd)[0], cmd)
        for cmd in ('git commit -m "a b" && git stash', 'git commit -m "x;y"; git reset --hard',
                    "git commit -m 'x|y' | git stash pop", 'echo "a"\ngit stash', r'echo \"; git stash'):
            self.assertFalse(guard.bash_decision(cmd)[0], cmd)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / ".autopilot").mkdir()

    def save(self, **state):
        state_io.write_state_file(self.root / ".autopilot" / "state.js", dict({"tickets": []}, **state))

    def call(self, command, subagent=True):
        payload = {"tool_name": "Bash", "tool_input": {"command": command}}
        if subagent:
            payload["agent_id"] = "a1"
        return guard.decision(payload, self.root)[0]

    def test_decision_only_for_subagents_of_strict_run(self):
        self.save(strictRouting=True, finishedAt=None)
        self.assertFalse(self.call("git stash"))
        self.assertFalse(self.call("git stash pop"))
        self.assertFalse(self.call("git reset --hard"))
        self.assertTrue(self.call("git commit --only a b"))
        self.assertTrue(self.call("git stash", subagent=False))
        self.save(strictRouting=False, finishedAt=None)
        self.assertTrue(self.call("git stash"))
        self.save(strictRouting=True, finishedAt="2026-01-01")
        self.assertTrue(self.call("git stash"))

    def test_install_hook_adds_bash_matcher_once_and_keeps_foreign_hooks(self):
        settings = self.root / ".claude" / "settings.json"
        settings.parent.mkdir()
        foreign = {"matcher": "Read", "hooks": [{"type": "command", "command": "x"}]}
        settings.write_text(json.dumps({"hooks": {"PreToolUse": [foreign]}}), encoding="utf-8")
        guard.install_hook(self.root)
        first = settings.read_text(encoding="utf-8")
        entries = json.loads(first)["hooks"]["PreToolUse"]
        self.assertEqual(sorted(e["matcher"] for e in entries),
                         sorted(["Read", "Agent|Task", "|".join(guard.WRITE_TOOLS), "Bash"]))
        self.assertFalse(guard.install_hook(self.root)[1])
        self.assertEqual(settings.read_text(encoding="utf-8"), first)


class Docs(unittest.TestCase):
    def test_executor_rules_in_prompt_and_profile(self):
        _, body = agent_profiles.definition("anthropic", "autopilot-executor-01-x", "executor",
                                            {"model": "haiku", "effort": "low"}, "t.md")
        for text in (doc("skills", "autopilot", "prompts", "executor.md"), body):
            for needle in ("git stash", "git reset", "git checkout -- ",
                           "git commit --only", "git diff --cached --stat"):
                self.assertIn(needle, text)
        _, reviewer = agent_profiles.definition("anthropic", "autopilot-reviewer-01-x", "reviewer",
                                                {"model": "haiku", "effort": "low"}, "t.md")
        self.assertNotIn("git stash", reviewer)

    def test_advisor_rule_documented(self):
        for name in ("claude-code.md", "model-routing.md"):
            text = doc("docs", "autopilot", name)
            for needle in ("server-side tool", "advisorModel", "is_allowed_subagent_model"):
                self.assertIn(needle, text, name)
        text = doc("docs", "autopilot", "claude-code.md")
        for needle in ("R04b", "attestations.jsonl", "eval"):
            self.assertIn(needle, text)
        pre = doc("skills", "autopilot", "phases", "0-preflight.md")
        self.assertIn("advisorModel", pre)
        self.assertIn("CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1", pre)
        self.assertLess(pre.index("ap.py claude-version"), pre.index("## 4. Instruments"))

    def test_limit_resume_rule_documented(self):
        for name in ("0-resume.md", "5-repair.md"):
            text = doc("skills", "autopilot", "phases", name)
            for needle in ("git status", "git diff", "SendMessage", "do not start a new one",
                           "Uncommitted edits", "5-hour", "weekly", "Ultra"):
                self.assertIn(needle, text, name)

    def test_changelog_has_unreleased_entry_for_each_requirement(self):
        text = doc("CHANGELOG.md")
        unreleased = text[text.index("## Unreleased"):text.index("## 2.7.0")]
        for r in ("R01", "R01a", "R01b", "R02", "R02a", "R03", "R03a", "R04", "R04a",
                  "R05", "R05a", "R06", "R06a", "R00i"):
            self.assertRegex(unreleased, r"\b" + r + r"\b")


class ClaudeVersion(unittest.TestCase):
    def run_cli(self, text):
        r = subprocess.run([sys.executable, str(TOOLS / "ap.py"), "claude-version", "--text", text],
                           capture_output=True, text=True, encoding="utf-8")
        return r.returncode, r.stdout

    def test_parse(self):
        self.assertEqual(ap.parse_claude_version("2.1.302 (Claude Code)"), (2, 1, 302))
        self.assertEqual(ap.parse_claude_version("2.1.311"), (2, 1, 311))
        self.assertIsNone(ap.parse_claude_version("garbage"))
        self.assertIsNone(ap.parse_claude_version(""))

    def test_report_levels(self):
        self.assertEqual(ap.claude_version_report((2, 1, 294))[0], "refuse")
        self.assertEqual(ap.claude_version_report((2, 1, 295))[0], "warn")
        self.assertEqual(ap.claude_version_report((2, 1, 310))[0], "warn")
        self.assertEqual(ap.claude_version_report((2, 1, 311))[0], "ok")
        self.assertEqual(ap.claude_version_report(None)[0], "unknown")

    def test_cli_exit_codes_and_output(self):
        code, out = self.run_cli("2.1.302 (Claude Code)")
        self.assertEqual(code, 0)
        self.assertIn("2.1.305", out)                      # known problems listed
        self.assertEqual(self.run_cli("2.1.294")[0], 2)
        self.assertEqual(self.run_cli("2.1.311"), (0, ""))
        for junk in ("junk", ""):
            code, out = self.run_cli(junk)
            self.assertEqual((code, len(out.strip().splitlines())), (0, 1))


if __name__ == "__main__":
    unittest.main()
