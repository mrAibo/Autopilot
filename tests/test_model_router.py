"""Contract tests for fail-closed provider routing."""
import importlib.util
import pathlib
import unittest

SRC = pathlib.Path(__file__).resolve().parents[1] / "skills/autopilot/tools/model_router.py"
spec = importlib.util.spec_from_file_location("model_router", SRC)
router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(router)


class RouterTests(unittest.TestCase):
    def capabilities(self, provider, model, effort):
        return {"provider": provider, "model_selection": True,
                "models": {model: [effort]}}

    def test_cheap_openai(self):
        scores = {name: 0 for name in router.WEIGHTS}
        r = router.choose_route("openai", scores, capabilities=self.capabilities("openai", "gpt-6-luna", "low"))
        self.assertEqual((r["status"], r["model"], r["effort"]), ("ready", "gpt-6-luna", "low"))

    def test_cheap_anthropic(self):
        scores = {name: 0 for name in router.WEIGHTS}
        r = router.choose_route("anthropic", scores, capabilities=self.capabilities("anthropic", "haiku", "low"))
        self.assertEqual((r["status"], r["model"]), ("ready", "haiku"))

    def test_strong_anthropic_uses_sonnet_not_opus_or_fable(self):
        scores = {"algorithm": 25, "coupling": 20, "uncertainty": 15,
                  "context": 15, "testing": 15, "risk": 10}
        r = router.choose_route("anthropic", scores, capabilities=self.capabilities("anthropic", "sonnet", "high"))
        self.assertEqual((r["status"], r["model"], r["profile"]), ("ready", "sonnet", "strong"))

    def test_high_risk_forces_strong(self):
        scores = {name: 0 for name in router.WEIGHTS}
        scores["risk"] = 10
        self.assertEqual(router.assess_scores(scores)[1], "strong")

    def test_restricted_models_are_denied_even_when_advertised(self):
        scores = {name: 0 for name in router.WEIGHTS}
        policy = dict(router.DEFAULT_POLICY)
        policy["providers"] = {"openai": dict(router.DEFAULT_POLICY["providers"]["openai"])}
        policy["providers"]["openai"]["cheap"] = {"model": "gpt-6-astra", "effort": "low"}
        with self.assertRaises(router.PolicyError):
            router.choose_route("openai", scores, policy=policy,
                                capabilities=self.capabilities("openai", "gpt-6-astra", "low"))

    def test_fail_closed_without_capabilities(self):
        scores = {name: 0 for name in router.WEIGHTS}
        self.assertEqual(router.choose_route("anthropic", scores)["status"], "blocked")

    def test_host_without_enforced_selection_is_blocked(self):
        scores = {name: 0 for name in router.WEIGHTS}
        capabilities = self.capabilities("openai", "gpt-6-luna", "low")
        capabilities["model_selection"] = False
        self.assertEqual(router.choose_route("openai", scores, capabilities=capabilities)["status"], "blocked")

    def test_missing_effort_is_blocked(self):
        scores = {name: 0 for name in router.WEIGHTS}
        capabilities = self.capabilities("anthropic", "haiku", "high")
        self.assertEqual(router.choose_route("anthropic", scores, capabilities=capabilities)["status"], "blocked")

    def test_out_of_range_score_fails(self):
        scores = {name: 0 for name in router.WEIGHTS}
        scores["algorithm"] = 26
        with self.assertRaises(router.PolicyError):
            router.assess_scores(scores)

    def test_heuristic_flags_credentials(self):
        scores = router.assess_ticket("**Зона:** \`src/auth/\`\nImplement password hashing and sessions")
        self.assertEqual(scores["risk"], 10)


if __name__ == "__main__":
    unittest.main()
