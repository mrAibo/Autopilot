"""Доделки после аудита (R07): маршрут таска выбирает оценка планировщика (класс, риск, причина) и зона, а не слова в тексте."""
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

import test_ap
from test_ap_audit import harness

TOOLS = Path(__file__).resolve().parents[1] / "skills" / "autopilot" / "tools"
sys.path.insert(0, str(TOOLS))
import agent_profiles  # noqa: E402
import model_router as router  # noqa: E402


def ticket(zone, body="", klass=None, risk=None, why="одна фраза"):
    head = "# 09 — Таск\n\n**Зона:** " + " · ".join("`%s`" % z for z in zone) + "\n"
    if klass:
        head += "**Класс:** %s\n" % klass
    if risk:
        head += "**Риск:** %s\n" % risk
    if why is not None and klass:
        head += "**Причина класса:** %s\n" % why
    return head + "\n" + body + "\n"


def caps(model, *efforts):
    return {"provider": "anthropic", "model_selection": True, "models": {model: list(efforts)}}

CLASS_LINES = "**Класс:** обычный\n**Риск:** обычный\n**Причина класса:** типовая задача\n"


def rewrite_tickets(h, change):
    """Переписать файлы тасков харнесса: text -> change(text) (test_ap.ticket() уже пишет класс)."""
    for name in ("01-karkas.md", "02-priem.md"):
        path = os.path.join(h.dir, "tickets", name)
        text = test_ap.read(path)
        with open(path, "w", encoding="utf-8") as f:
            f.write(change(text))


class AssessmentFromHeaders(unittest.TestCase):
    def test_a_quoted_token_in_a_harmless_zone_is_not_high_risk(self):
        text = ticket(["src/report.py"], "Показать токен, секрет, ключ и подпись как в брифе: «токен».", "обычный")
        scores = router.assess_ticket(text)
        self.assertEqual(scores["risk"], 0)
        route = router.choose_route("anthropic", scores)
        self.assertIn("high-risk=False", route["reason"])

    def test_planner_high_risk_gives_risk_10(self):
        self.assertEqual(router.assess_ticket(ticket(["src/a.py"], "x", "обычный", "высокий"))["risk"], 10)
        self.assertEqual(router.assess_ticket(ticket(["src/a.py"], "x", "обычный", "обычный"))["risk"], 0)

    def test_complex_class_gives_algorithm_20_and_mechanical_stays_cheap(self):
        self.assertGreaterEqual(router.assess_ticket(ticket(["src/a.py"], "x", "сложный"))["algorithm"], 20)
        mech = router.assess_ticket(ticket(["src/a.py"], "x", "механический"))
        self.assertEqual(router.assess_scores(mech)[1], "cheap")

    def test_a_sensitive_zone_is_a_floor_the_class_cannot_lower(self):
        for zone in ("skills/autopilot/tools/gate_sign.py", "skills/autopilot/tools/claude_agent_guard.py",
                     "skills/autopilot/tools/model_router.py", "skills/autopilot/tools/state_io.py"):
            with self.subTest(zone=zone):
                scores = router.assess_ticket(ticket([zone], "x", "механический", "обычный"))
                self.assertGreaterEqual(scores["risk"], 10)

    def test_a_docs_only_zone_is_risk_zero(self):
        text = ticket(["README.md", "docs/autopilot/x.md"], "токен, ключ, подпись", "механический")
        self.assertEqual(router.assess_ticket(text)["risk"], 0)

    def test_no_headers_means_ordinary_with_risk_by_the_zone_alone(self):
        plain = router.assess_ticket(ticket(["src/a.py"], "Алгоритм, гонка, tbd, токен."))
        self.assertEqual((plain["risk"], plain["algorithm"], plain["uncertainty"]), (0, 5, 0))
        self.assertEqual(router.assess_ticket(ticket(["src/auth/login.py"], "x"))["risk"], 10)
        self.assertEqual(sorted(plain), sorted(router.WEIGHTS))

    def test_the_old_word_lists_are_gone_from_the_router(self):
        self.assertFalse(hasattr(router, "RISK_RE"))
        self.assertFalse(hasattr(router, "WORD_RISK_RE"))
        source = (TOOLS / "model_router.py").read_text(encoding="utf-8").lower()
        for word in ("race condition", "tbd", "to decide", "алгоритм", "гонк", "уточнить"):
            self.assertNotIn(word, source)
        self.assertIn("model_router.assess_ticket", (TOOLS / "agent_profiles.py").read_text(encoding="utf-8"))


class PlanProblems(unittest.TestCase):
    def test_a_ticket_without_class_and_reason_is_named(self):
        got = router.plan_problems(ticket(["src/a.py"], "x"))
        self.assertEqual(len(got), 2)
        self.assertTrue(any("Класс" in p for p in got) and any("Причина класса" in p for p in got))

    def test_empty_unknown_and_too_long_are_refused(self):
        self.assertEqual(router.plan_problems(ticket(["a.py"], "x", "сложный")), [])
        self.assertTrue(router.plan_problems(ticket(["a.py"], "x", "сложный", why="")))
        self.assertTrue(router.plan_problems(ticket(["a.py"], "x", "ужасный")))
        self.assertTrue(router.plan_problems(ticket(["a.py"], "x", "сложный", why="я" * 201)))
        self.assertEqual(router.plan_problems(ticket(["a.py"], "x", "сложный", why="я" * 200)), [])
        self.assertTrue(router.plan_problems(ticket(["a.py"], "x", "сложный", "страшный")))

    def test_check_plan_names_tickets_without_class_and_lets_g3_through_once_fixed(self):
        h = harness(self)
        h.plan()
        rewrite_tickets(h, lambda text: text.replace(CLASS_LINES, ""))
        h.ap("tickets")
        code, out = h.ap("check-plan")
        self.assertEqual(code, 2, out)
        self.assertIn("таск 01", out)
        self.assertIn("таск 02", out)
        self.assertIn("Класс", out)
        self.assertIn("Причина класса", out)
        self.assertFalse(h.state()["gates"]["G3"]["ok"])
        rewrite_tickets(h, lambda text: text.replace("**Волна:**", CLASS_LINES + "**Волна:**"))
        h.ap("tickets")
        code, out = h.ap("check-plan")
        self.assertEqual(code, 0, out)
        self.assertTrue(h.state()["gates"]["G3"]["ok"])

    def test_check_plan_refuses_a_reason_over_200_characters(self):
        h = harness(self)
        h.plan()
        rewrite_tickets(h, lambda text: text.replace("типовая задача", "я" * 201))
        h.ap("tickets")
        code, out = h.ap("check-plan")
        self.assertEqual(code, 2, out)
        self.assertIn("длиннее 200", out)


class RouteReason(unittest.TestCase):
    def test_reason_carries_class_risk_and_the_planners_phrase(self):
        text = ticket(["src/a.py"], "x", "сложный", "высокий", "запись в общий кэш с гонками")
        route = router.choose_route("anthropic", router.assess_ticket(text), note=router.planner_note(text))
        for part in ("class=сложный", "risk=высокий", "why=запись в общий кэш с гонками", "score="):
            self.assertIn(part, route["reason"])

    def test_without_headers_the_note_says_ordinary(self):
        note = router.planner_note(ticket(["src/a.py"], "x"))
        self.assertEqual(note, "class=обычный; risk=обычный")

    def test_the_agent_profile_takes_the_assessment_and_the_note_from_the_ticket(self):
        with tempfile.TemporaryDirectory(prefix="ap-prof-") as root:
            (Path(root) / "tickets").mkdir()
            path = Path(root) / "tickets" / "09-task.md"
            path.write_text(ticket(["src/a.py"], "x", "механический", why="переименование"), encoding="utf-8")
            capabilities = Path(root) / "caps.json"
            capabilities.write_text(json.dumps(caps("haiku", "low", "high")), encoding="utf-8")
            result = agent_profiles.prepare(root, path, "anthropic", capabilities, "executor", install=False)
        self.assertEqual(result["model"], "haiku")
        self.assertIn("class=механический", result["reason"])
        self.assertIn("why=переименование", result["reason"])


if __name__ == "__main__":
    unittest.main()
