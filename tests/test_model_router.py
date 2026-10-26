"""Contract tests for fail-closed provider routing."""
import importlib.util
import json
import pathlib
import tempfile
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

    def test_premium_alias_cannot_bypass_restrictions(self):
        scores = {name: 0 for name in router.WEIGHTS}
        policy = dict(router.DEFAULT_POLICY)
        policy["providers"] = {"anthropic": dict(router.DEFAULT_POLICY["providers"]["anthropic"])}
        policy["providers"]["anthropic"]["cheap"] = {"model": "claude-opus-4-8", "effort": "low"}
        with self.assertRaises(router.PolicyError):
            router.choose_route("anthropic", scores, policy=policy,
                                capabilities=self.capabilities("anthropic", "claude-opus-4-8", "low"))

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
        scores = router.assess_ticket("**Зона:** `src/auth/`\nImplement password hashing and sessions")
        self.assertEqual(scores["risk"], 10)

    def policy_from(self, value):
        with tempfile.TemporaryDirectory(prefix="router-policy-") as folder:
            path = pathlib.Path(folder) / "policy.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            return router.load_policy(path)

    def test_partial_profile_override_keeps_other_tiers_and_provider(self):
        policy = self.policy_from({
            "providers": {"openai": {"cheap": {"effort": "medium"}}},
            "max_parallel": 1})
        scores = {name: 0 for name in router.WEIGHTS}
        result = router.choose_route(
            "openai", scores, policy=policy,
            capabilities=self.capabilities("openai", "gpt-6-luna", "medium"))
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["max_parallel"], 1)
        self.assertEqual(policy["providers"]["openai"]["balanced"],
                         router.DEFAULT_POLICY["providers"]["openai"]["balanced"])
        self.assertEqual(policy["providers"]["anthropic"],
                         router.DEFAULT_POLICY["providers"]["anthropic"])
        self.assertEqual(router.DEFAULT_POLICY["providers"]["openai"]["cheap"]["effort"],
                         "low")

    def test_custom_restricted_list_adds_to_not_erases_default(self):
        policy = self.policy_from({
            "restricted": {"openai": ["gpt-6-luna"]}})
        self.assertIn("gpt-6-astra", policy["restricted"]["openai"])
        self.assertIn("gpt-6-luna", policy["restricted"]["openai"])
        scores = {name: 0 for name in router.WEIGHTS}
        with self.assertRaisesRegex(router.PolicyError, "restricted"):
            router.choose_route(
                "openai", scores, policy=policy,
                capabilities=self.capabilities("openai", "gpt-6-luna", "low"))
        blank = self.policy_from({"restricted": {"openai": []}})
        self.assertIn("gpt-6-astra", blank["restricted"]["openai"])

    def test_policy_must_reject_invalid_or_unknown_settings(self):
        invalid = [
            {"providers": {"openai": {"cheap": None}}},
            {"providers": {"openai": {"cheap": {}}}},
            {"providers": {"openai": {"cheap": {"model": " gpt-6-astra"}}}},
            {"providers": {"openai": {"cheap": {"model": False}}}},
            {"providers": {"openai": {"superfast": {"model": "foo"}}}},
            {"providers": {"unknown": {}}},
            {"providers": []},
            {"restricted": {"openai": False}},
            {"restricted": {"openai": [False]}},
            {"restricted": {"unknown": ["x"]}},
            {"max_parallel": True},
            {"max_parallel": 4},
            {"version": 99},
            {"allow_restricted_subagents": 1},
            {"unsupported_option": True},
        ]
        for value in invalid:
            with self.subTest(policy=value):
                with self.assertRaises(router.PolicyError):
                    self.policy_from(value)

    def test_default_policy_is_not_mutated_by_custom_overrides(self):
        first = self.policy_from({"providers": {
            "anthropic": {"strong": {"model": "some-host-model"}}}})
        second = router.load_policy()
        self.assertEqual(second, router.DEFAULT_POLICY)
        self.assertNotEqual(first["providers"]["anthropic"]["strong"],
                            second["providers"]["anthropic"]["strong"])
        first["providers"]["openai"]["cheap"]["model"] = "mutated"
        self.assertEqual(router.DEFAULT_POLICY["providers"]["openai"]["cheap"]["model"],
                         "gpt-6-luna")

    def test_direct_policy_cannot_bypass_baseline_premium_deny_with_whitespace(self):
        policy = self.policy_from({"providers": {
            "openai": {"cheap": {"model": "gpt-6-luna"}}}})
        policy["providers"]["openai"]["cheap"]["model"] = " gpt-6-astra "
        scores = {name: 0 for name in router.WEIGHTS}
        with self.assertRaisesRegex(router.PolicyError, "exact"):
            router.choose_route("openai", scores, policy=policy,
                                capabilities=self.capabilities(
                                    "openai", " gpt-6-astra ", "low"))
        policy["providers"]["openai"]["cheap"]["model"] = "gpt-6-astra"
        policy["restricted"] = {"openai": []}
        with self.assertRaisesRegex(router.PolicyError, "restricted"):
            router.choose_route(
                "openai", scores, policy=policy,
                capabilities=self.capabilities("openai", "gpt-6-astra", "low"))

    def policy_from(self, value):
        with tempfile.TemporaryDirectory(prefix="router-policy-") as folder:
            path = pathlib.Path(folder) / "policy.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            return router.load_policy(path)

    def test_partial_profile_override_keeps_other_tiers_and_provider(self):
        policy = self.policy_from({
            "providers": {"openai": {"cheap": {"effort": "medium"}}},
            "max_parallel": 1})
        scores = {name: 0 for name in router.WEIGHTS}
        result = router.choose_route(
            "openai", scores, policy=policy,
            capabilities=self.capabilities("openai", "gpt-6-luna", "medium"))
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["max_parallel"], 1)
        self.assertEqual(policy["providers"]["openai"]["balanced"],
                         router.DEFAULT_POLICY["providers"]["openai"]["balanced"])
        self.assertEqual(policy["providers"]["anthropic"],
                         router.DEFAULT_POLICY["providers"]["anthropic"])
        self.assertEqual(router.DEFAULT_POLICY["providers"]["openai"]["cheap"]["effort"],
                         "low")

    def test_custom_restricted_list_adds_to_not_erases_default(self):
        policy = self.policy_from({
            "restricted": {"openai": ["gpt-6-luna"]}})
        self.assertIn("gpt-6-astra", policy["restricted"]["openai"])
        self.assertIn("gpt-6-luna", policy["restricted"]["openai"])
        scores = {name: 0 for name in router.WEIGHTS}
        with self.assertRaisesRegex(router.PolicyError, "restricted"):
            router.choose_route(
                "openai", scores, policy=policy,
                capabilities=self.capabilities("openai", "gpt-6-luna", "low"))
        blank = self.policy_from({"restricted": {"openai": []}})
        self.assertIn("gpt-6-astra", blank["restricted"]["openai"])

    def test_policy_must_reject_invalid_or_unknown_settings(self):
        invalid = [
            {"providers": {"openai": {"cheap": None}}},
            {"providers": {"openai": {"cheap": {}}}},
            {"providers": {"openai": {"cheap": {"model": " gpt-6-astra"}}}},
            {"providers": {"openai": {"cheap": {"model": False}}}},
            {"providers": {"openai": {"superfast": {"model": "foo"}}}},
            {"providers": {"unknown": {}}},
            {"providers": []},
            {"restricted": {"openai": False}},
            {"restricted": {"openai": [False]}},
            {"restricted": {"unknown": ["x"]}},
            {"max_parallel": True},
            {"max_parallel": 4},
            {"version": 99},
            {"allow_restricted_subagents": 1},
            {"unsupported_option": True},
        ]
        for value in invalid:
            with self.subTest(policy=value):
                with self.assertRaises(router.PolicyError):
                    self.policy_from(value)

    def test_default_policy_is_not_mutated_by_custom_overrides(self):
        first = self.policy_from({"providers": {
            "anthropic": {"strong": {"model": "some-host-model"}}}})
        second = router.load_policy()
        self.assertEqual(second, router.DEFAULT_POLICY)
        self.assertNotEqual(first["providers"]["anthropic"]["strong"],
                            second["providers"]["anthropic"]["strong"])
        first["providers"]["openai"]["cheap"]["model"] = "mutated"
        self.assertEqual(router.DEFAULT_POLICY["providers"]["openai"]["cheap"]["model"],
                         "gpt-6-luna")

    def test_direct_policy_cannot_bypass_baseline_premium_deny_with_whitespace(self):
        policy = self.policy_from({"providers": {
            "openai": {"cheap": {"model": "gpt-6-luna"}}}})
        policy["providers"]["openai"]["cheap"]["model"] = " gpt-6-astra "
        scores = {name: 0 for name in router.WEIGHTS}
        with self.assertRaisesRegex(router.PolicyError, "exact"):
            router.choose_route("openai", scores, policy=policy,
                                capabilities=self.capabilities(
                                    "openai", " gpt-6-astra ", "low"))
        policy["providers"]["openai"]["cheap"]["model"] = "gpt-6-astra"
        policy["restricted"] = {"openai": []}
        with self.assertRaisesRegex(router.PolicyError, "restricted"):
            router.choose_route(
                "openai", scores, policy=policy,
                capabilities=self.capabilities("openai", "gpt-6-astra", "low"))


if __name__ == "__main__":
    unittest.main()
