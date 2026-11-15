"""Аудит 2026-11-15: риск по зоне и целым словам, класс таска, профили cheap_read / cheap_code."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "autopilot" / "tools"))
import agent_profiles  # noqa: E402
import model_router as router  # noqa: E402


def ticket(zone, body="", klass=None):
    head = "# 09 — Таск\n\n**Зона:** " + " · ".join("`%s`" % z for z in zone) + "\n"
    if klass:
        head += "**Класс:** %s\n**Причина класса:** одна строка\n" % klass
    return head + "\n" + body + "\n"


def caps(model, *efforts):
    return {"provider": "anthropic", "model_selection": True, "models": {model: list(efforts)}}


class RiskByZoneTests(unittest.TestCase):
    def test_docs_zone_ignores_risky_words(self):
        text = ticket(["README.md", "docs/autopilot/run-log.md"],
                      "Опиши подписи, author, session, token и ключ в документации.")
        self.assertEqual(router.assess_ticket(text)["risk"], 0)

    def test_sensitive_zone_is_max_risk_even_without_words(self):
        for zone in ("skills/autopilot/tools/gate_sign.py", "skills/autopilot/tools/claude_agent_guard.py",
                     "skills/autopilot/tools/model_router.py", "skills/autopilot/tools/state_io.py",
                     "src/auth/login.py", "src/payments/charge.py", "db/migrations/001.sql"):
            with self.subTest(zone=zone):
                self.assertEqual(router.assess_ticket(ticket([zone], "Переименовать функцию."))["risk"], 10)

    def test_words_in_the_body_never_raise_the_risk_in_a_code_zone(self):
        for word in ("auth", "authentication", "session_id", "password", "migration", "author", "token", "подпись", "ключ"):
            with self.subTest(word=word):
                self.assertEqual(router.assess_ticket(ticket(["src/app.py"], "Поправить " + word + "."))["risk"], 0)

    def test_the_planners_high_risk_gives_risk_10_in_a_code_zone(self):
        text = ticket(["src/app.py"], "Читать token из .env.").replace("**Зона:**", "**Риск:** высокий\n**Зона:**")
        self.assertEqual(router.assess_ticket(text)["risk"], 10)
        normal = ticket(["src/app.py"], "Читать token из .env.").replace("**Зона:**", "**Риск:** обычный\n**Зона:**")
        self.assertEqual(router.assess_ticket(normal)["risk"], 0)

    def test_plain_code_ticket_is_low_risk(self):
        self.assertEqual(router.assess_ticket(ticket(["src/app.py"], "Поправить опечатку."))["risk"], 0)


class TicketClassTests(unittest.TestCase):
    def test_mechanical_class_gets_cheap_scores(self):
        scores = router.assess_ticket(ticket(["src/app.py"], "Переименовать поле.", "механический"))
        self.assertEqual(router.assess_scores(scores)[1], "cheap")

    def test_complex_class_gets_strong_scores(self):
        scores = router.assess_ticket(ticket(["src/app.py"], "Переименовать поле.", "сложный"))
        self.assertEqual(router.assess_scores(scores)[1], "strong")

    def test_class_never_lowers_zone_risk(self):
        scores = router.assess_ticket(ticket(["skills/autopilot/tools/gate_sign.py"], "Правка.", "механический"))
        self.assertEqual(scores["risk"], 10)
        self.assertEqual(router.assess_scores(scores)[1], "strong")

    def test_mechanical_class_never_lowers_computed_scores(self):
        body = "Переименовать поле."
        plain = router.assess_ticket(ticket(["a.py", "b.py", "c.py", "d.py"], body))
        mech = router.assess_ticket(ticket(["a.py", "b.py", "c.py", "d.py"], body, "механический"))
        # `обычный` adds its own floor (algorithm, uncertainty); the zone-derived scores are never lowered
        self.assertTrue(all(mech[k] >= plain[k] for k in ("coupling", "context", "testing", "risk")))
        self.assertNotEqual(router.assess_scores(mech)[1], "cheap")

    def test_ordinary_and_missing_class_score_the_same(self):
        plain = router.assess_ticket(ticket(["src/app.py"], "Правка."))
        self.assertEqual(router.assess_ticket(ticket(["src/app.py"], "Правка.", "обычный")), plain)
        self.assertEqual(sorted(plain), sorted(router.WEIGHTS))


class CheapProfilesTests(unittest.TestCase):
    def test_policy_declares_both_cheap_profiles(self):
        anthropic = router.DEFAULT_POLICY["providers"]["anthropic"]
        self.assertEqual(anthropic["cheap_read"], {"model": "haiku", "effort": "low"})
        self.assertEqual(anthropic["cheap_code"], {"model": "haiku", "effort": "high"})

    def test_mechanical_executor_gets_haiku_high(self):
        scores = router.assess_ticket(ticket(["src/app.py"], "Правка.", "механический"))
        route = router.choose_route("anthropic", scores, capabilities=caps("haiku", "low", "high"))
        self.assertEqual((route["status"], route["model"], route["effort"]), ("ready", "haiku", "high"))

    def test_scout_and_docs_only_unclassed_get_haiku_low_but_code_does_not(self):
        zero = {name: 0 for name in router.WEIGHTS}
        route = router.choose_route("anthropic", zero, capabilities=caps("haiku", "low", "high"))
        self.assertEqual((route["model"], route["effort"]), ("haiku", "low"))
        docs = router.assess_ticket(ticket(["docs/a.md"], "Правка."))
        self.assertEqual(router.choose_route("anthropic", docs)["effort"], "low")
        plain = router.assess_ticket(ticket(["src/app.py"], "Правка."))
        self.assertEqual(router.choose_route("anthropic", plain)["model"], "sonnet")

    def test_explorer_profile_is_cheap_read_even_for_mechanical_ticket(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "tickets" / "09-x.md"
            path.parent.mkdir()
            path.write_text(ticket(["src/app.py"], "Правка.", "механический"), encoding="utf-8")
            capsfile = root / "caps.json"
            capsfile.write_text(json.dumps(caps("haiku", "low", "high")), encoding="utf-8")
            explorer = agent_profiles.prepare(root, path, "anthropic", capsfile, "explorer")
            executor = agent_profiles.prepare(root, path, "anthropic", capsfile, "executor")
        self.assertEqual(explorer["effort"], "low")
        self.assertEqual(executor["effort"], "high")

    def test_legacy_cheap_override_in_policy_file_still_applies(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "p.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"providers": {"anthropic": {"cheap": {"effort": "medium"}}}}, f)
            policy = router.load_policy(path)
        self.assertEqual(policy["providers"]["anthropic"]["cheap_read"]["effort"], "medium")

    def test_fable_and_unapproved_opus_stay_blocked_in_cheap_code(self):
        scores = router.assess_ticket(ticket(["src/app.py"], "Правка.", "механический"))
        for model in ("fable", "opus", "claude-opus-4-8"):
            policy = router.load_policy()
            policy["providers"]["anthropic"]["cheap_code"] = {"model": model, "effort": "high"}
            with self.subTest(model=model), self.assertRaises(router.PolicyError):
                router.choose_route("anthropic", scores, policy, caps(model, "high"))
        self.assertFalse(router.is_allowed_subagent_model("fable", premium_ok=True))
        self.assertFalse(router.is_allowed_subagent_model("opus"))


if __name__ == "__main__":
    unittest.main()
