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
        scores = {"algorithm": 15, "coupling": 20, "uncertainty": 15,
                  "context": 15, "testing": 15, "risk": 10}
        # No user approval of Opus: the premium flag is off, stated explicitly.
        r = router.choose_route("anthropic", scores, premium=False,
                                capabilities=self.capabilities("anthropic", "sonnet", "high"))
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
        for premium in (False, True):  # the Opus flag never opens Astra
            with self.subTest(premium=premium), self.assertRaises(router.PolicyError):
                router.choose_route("openai", scores, policy=policy, premium=premium,
                                    capabilities=self.capabilities("openai", "gpt-6-astra", "low"))

    def test_premium_alias_cannot_bypass_restrictions(self):
        scores = {name: 0 for name in router.WEIGHTS}
        policy = dict(router.DEFAULT_POLICY)
        policy["providers"] = {"anthropic": dict(router.DEFAULT_POLICY["providers"]["anthropic"])}
        policy["providers"]["anthropic"]["cheap"] = {"model": "claude-opus-4-8", "effort": "low"}
        with self.assertRaises(router.PolicyError):  # without approval: premium=False, explicit
            router.choose_route("anthropic", scores, policy=policy, premium=False,
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

    def test_model_only_host_accepts_unenforceable_effort_as_advisory(self):
        scores = {name: 0 for name in router.WEIGHTS}
        for provider, model in (("openai", "gpt-6-luna"),
                                ("anthropic", "haiku")):
            with self.subTest(provider=provider):
                caps = {"provider": provider, "model_selection": True,
                        "effort_selection": False, "models": {model: []}}
                route = router.choose_route(provider, scores, capabilities=caps)
                self.assertEqual(route["status"], "ready")
                self.assertFalse(route["effort_enforced"])
                self.assertEqual(route["effort_status"], "advisory")
                self.assertTrue(route["effort"])

    def test_model_only_still_requires_exact_model_and_host_control(self):
        scores = {name: 0 for name in router.WEIGHTS}
        base = {"provider": "anthropic", "model_selection": True,
                "effort_selection": False, "models": {"wrong": []}}
        self.assertEqual(router.choose_route(
            "anthropic", scores, capabilities=base)["status"], "blocked")
        base["models"] = {"haiku": []}
        base["model_selection"] = False
        self.assertEqual(router.choose_route(
            "anthropic", scores, capabilities=base)["status"], "blocked")
        base["model_selection"] = True
        base["effort_selection"] = "false"
        self.assertEqual(router.choose_route(
            "anthropic", scores, capabilities=base)["status"], "blocked")

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

    def test_partial_profile_override_keeps_other_tiers_and_provider_first_copy(self):
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

    def test_custom_restricted_list_adds_to_not_erases_default_first_copy(self):
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

    def test_policy_must_reject_invalid_or_unknown_settings_first_copy(self):
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

    def test_default_policy_is_not_mutated_by_custom_overrides_first_copy(self):
        first = self.policy_from({"providers": {
            "anthropic": {"strong": {"model": "some-host-model"}}}})
        second = router.load_policy()
        self.assertEqual(second, router.DEFAULT_POLICY)
        self.assertNotEqual(first["providers"]["anthropic"]["strong"],
                            second["providers"]["anthropic"]["strong"])
        first["providers"]["openai"]["cheap"]["model"] = "mutated"
        self.assertEqual(router.DEFAULT_POLICY["providers"]["openai"]["cheap"]["model"],
                         "gpt-6-luna")

    def test_direct_policy_cannot_bypass_baseline_premium_deny_with_whitespace_first_copy(self):
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

    def critical_scores(self, risk, algorithm):
        scores = {name: 0 for name in router.WEIGHTS}
        scores.update(risk=risk, algorithm=algorithm)
        return scores

    def test_risk_and_algorithm_max_selects_critical(self):
        r = router.choose_route("anthropic", self.critical_scores(10, 25),
                                capabilities=self.capabilities("anthropic", "sonnet", "xhigh"))
        self.assertEqual((r["status"], r["profile"], r["model"], r["effort"]),
                         ("ready", "critical", "sonnet", "xhigh"))

    def test_strong_unchanged_for_high_risk_only(self):
        self.assertEqual(router.assess_scores(self.critical_scores(10, 5))[1], "strong")

    def test_custom_policy_can_override_critical(self):
        policy = self.policy_from({"providers": {"anthropic": {
            "critical": {"model": "some-host-model", "effort": "max"}}}})
        r = router.choose_route("anthropic", self.critical_scores(10, 25), policy=policy,
                                capabilities=self.capabilities("anthropic", "some-host-model", "max"))
        self.assertEqual((r["status"], r["model"], r["effort"]),
                         ("ready", "some-host-model", "max"))

    def test_critical_blocked_without_xhigh_capability(self):
        caps = {"provider": "anthropic", "model_selection": True,
                "models": {"sonnet": ["low", "medium", "high"]}}
        r = router.choose_route("anthropic", self.critical_scores(10, 25), capabilities=caps)
        self.assertEqual((r["status"], r["error"]),
                         ("blocked", "Model/effort unavailable in this harness"))


class SubagentAllowlistTests(unittest.TestCase):
    DENIED = (
        "opus", "Opus", "claude-opus-4-8", "claude-opus-4-1-20250805",
        "claude-3-opus-20240229", "claude-3-opus-latest",
        "us.anthropic.claude-opus-4-1-20250805-v1:0", "eu.anthropic.claude-opus-4-v1:0",
        "anthropic.claude-3-opus-20240229-v1:0", "bedrock/anthropic.claude-opus-4-1-20250805-v1:0",
        "vertex_ai/claude-opus-4-1@20250805", "opusplan", " OPUS ",
        "fable", "claude-fable-5", "us.anthropic.claude-fable-5-v1:0",
        "inherit", "", "   ", "gpt-6-luna", "some-host-model", "claude", "sonnet-opus",
        "claude-sonnet-4-5; opus", None, 5,
        "claude-opus-4-1/haiku", "anthropic.opus/sonnet", "bedrock/claude-fable-5/sonnet")
    ALLOWED = (
        "haiku", "sonnet", "Haiku", "SONNET", "claude-haiku-5-5", "claude-sonnet-4-5",
        "claude-sonnet-4-5-20250929", "claude-3-5-haiku-20241022", "claude-3-haiku",
        "us.anthropic.claude-sonnet-4-5-20250929-v1:0", "anthropic.claude-3-haiku-20240307-v1:0",
        "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0", "vertex_ai/claude-sonnet-4@20250929",
        "sonnet[1m]")

    OPUS = (
        "opus", "Opus", "claude-opus-4-8", "claude-opus-4-1-20250805",
        "claude-3-opus-20240229", "claude-3-opus-latest",
        "us.anthropic.claude-opus-4-1-20250805-v1:0", "eu.anthropic.claude-opus-4-v1:0",
        "anthropic.claude-3-opus-20240229-v1:0", "bedrock/anthropic.claude-opus-4-1-20250805-v1:0",
        "vertex_ai/claude-opus-4-1@20250805", " OPUS ")

    def test_premium_and_unknown_names_are_refused_in_every_spelling(self):
        for name in self.DENIED:  # no approval: premium_ok=False, stated explicitly
            with self.subTest(name=name):
                self.assertFalse(router.is_allowed_subagent_model(name, premium_ok=False))
                self.assertFalse(router.is_allowed_subagent_model(name))

    def test_premium_ok_admits_opus_in_every_spelling_and_nothing_else(self):
        for name in self.OPUS:
            with self.subTest(name=name):
                self.assertTrue(router.is_opus_model(name))
                self.assertTrue(router.is_allowed_subagent_model(name, premium_ok=True))
        for name in self.DENIED:
            if name not in self.OPUS:  # fable, astra, hybrids, hidden opus, junk stay closed
                with self.subTest(name=name):
                    self.assertFalse(router.is_allowed_subagent_model(name, premium_ok=True))
        for name in self.ALLOWED:
            with self.subTest(name=name):
                self.assertTrue(router.is_allowed_subagent_model(name, premium_ok=True))

    def test_is_opus_model_is_false_for_fable_sonnet_haiku_and_mixed_names(self):
        for name in ("fable", "claude-fable-5", "us.anthropic.claude-fable-5-v1:0",
                     "sonnet", "haiku", "claude-sonnet-4-5", "gpt-6-luna", "opusplan",
                     "sonnet-opus", "claude-opus-4-1/haiku", "anthropic.opus/sonnet",
                     "claude-fable-5/claude-opus-4", "claude-opus-4/claude-fable-5",
                     "", "   ", "inherit", None, 5):
            with self.subTest(name=name):
                self.assertFalse(router.is_opus_model(name))

    def test_premium_ok_must_be_literally_true_and_policy_can_still_deny_opus(self):
        self.assertFalse(router.is_allowed_subagent_model("opus", premium_ok=1))
        self.assertFalse(router.is_allowed_subagent_model("opus", premium_ok="yes"))
        policy = router.load_policy()
        policy["restricted"]["anthropic"].append("opus")
        self.assertFalse(router.is_allowed_subagent_model("opus", policy, premium_ok=True))

    def test_haiku_and_sonnet_are_allowed_in_every_spelling(self):
        for name in self.ALLOWED:
            with self.subTest(name=name):
                self.assertTrue(router.is_allowed_subagent_model(name))

    def test_policy_restricted_list_can_remove_an_allowed_family(self):
        policy = router.load_policy()
        policy["restricted"]["anthropic"].append("claude-sonnet-4-5")
        self.assertFalse(router.is_allowed_subagent_model("claude-sonnet-4-5", policy))
        self.assertTrue(router.is_allowed_subagent_model("sonnet", policy))

    def test_normalize_drops_wrappers_and_keeps_family(self):
        self.assertEqual(router.normalize_model_name("US.Anthropic.Claude-Opus-4-1-20250805-V1:0"),
                         "claude-opus-4-1-20250805")
        self.assertEqual(router.normalize_model_name("vertex_ai/claude-sonnet-4@20250929"),
                         "claude-sonnet-4")

    def test_route_refuses_opus_hidden_before_a_slash(self):
        for model in ("claude-opus-4-1/haiku", "anthropic.opus/sonnet"):
            with self.subTest(model=model):
                policy = router.load_policy()
                policy["providers"]["anthropic"]["cheap"] = {"model": model, "effort": "low"}
                with self.assertRaises(router.PolicyError):
                    router.choose_route("anthropic", {n: 0 for n in router.WEIGHTS},
                                        policy=policy, premium=False)

    def test_route_refuses_bedrock_style_opus(self):
        policy = router.load_policy()
        policy["providers"]["anthropic"]["cheap"] = {
            "model": "us.anthropic.claude-opus-4-1-20250805-v1:0", "effort": "low"}
        with self.assertRaises(router.PolicyError):
            router.choose_route("anthropic", {n: 0 for n in router.WEIGHTS},
                                policy=policy, premium=False)


class PremiumRouteTests(unittest.TestCase):
    """The exceptional Opus tier: reachable only with premium=True, never Fable or Astra."""

    @staticmethod
    def caps(provider, model, effort):
        return {"provider": provider, "model_selection": True, "models": {model: [effort]}}

    @staticmethod
    def scores(**changes):
        return dict({name: 0 for name in router.WEIGHTS}, **changes)

    def policy_with(self, **premium):
        policy = router.load_policy()
        policy["providers"]["anthropic"]["premium"] = premium
        return policy

    def test_default_policy_has_a_premium_profile_that_scoring_never_picks(self):
        self.assertEqual(router.DEFAULT_POLICY["providers"]["anthropic"]["premium"],
                         {"model": "opus", "effort": "high"})
        for risk in (0, 10):
            for algorithm in (0, 20, 25):
                with self.subTest(risk=risk, algorithm=algorithm):
                    profile = router.assess_scores(self.scores(risk=risk, algorithm=algorithm))[1]
                    self.assertNotEqual(profile, "premium")

    def test_premium_true_routes_anthropic_to_opus_with_the_usual_status(self):
        scores = self.scores(risk=10)
        route = router.choose_route("anthropic", scores, premium=True,
                                    capabilities=self.caps("anthropic", "opus", "high"))
        self.assertEqual((route["status"], route["model"], route["effort"]),
                         ("ready", "opus", "high"))
        self.assertTrue(router.is_opus_model(route["model"]))
        self.assertEqual(route["effort_status"], "enforced")
        self.assertEqual(route["factors"], scores)
        # without a host that advertises opus the route is blocked like any other
        blocked = router.choose_route("anthropic", scores, premium=True,
                                      capabilities=self.caps("anthropic", "sonnet", "high"))
        self.assertEqual((blocked["status"], blocked["error"]),
                         ("blocked", "Model unavailable in this harness"))
        self.assertEqual(router.choose_route("anthropic", scores, premium=True)["status"], "blocked")

    def test_premium_false_is_what_it_was_before(self):
        for provider, model, effort in (("anthropic", "sonnet", "high"), ("openai", "gpt-6.1-sol", "high")):
            scores = self.scores(risk=10)
            caps = self.caps(provider, model, effort)
            plain = router.choose_route(provider, scores, capabilities=caps)
            self.assertEqual((plain["status"], plain["model"]), ("ready", model))
            self.assertEqual(router.choose_route(provider, scores, premium=False, capabilities=caps), plain)
        # opus advertised by the host does not make a non-premium route use it
        r = router.choose_route("anthropic", self.scores(risk=10), premium=False,
                                capabilities=self.caps("anthropic", "opus", "high"))
        self.assertEqual((r["status"], r["model"]), ("blocked", "sonnet"))

    def test_premium_true_leaves_openai_routes_alone(self):
        scores = self.scores(risk=10, algorithm=25)
        caps = self.caps("openai", "gpt-6.1-sol", "high")
        plain = router.choose_route("openai", scores, capabilities=caps)
        self.assertEqual(router.choose_route("openai", scores, premium=True, capabilities=caps), plain)
        self.assertNotIn("astra", plain["model"])

    def test_fable_is_closed_even_as_the_premium_profile(self):
        for model in ("fable", "claude-fable-5", "us.anthropic.claude-fable-5-v1:0"):
            with self.subTest(model=model), self.assertRaises(router.PolicyError):
                router.choose_route("anthropic", self.scores(risk=10),
                                    policy=self.policy_with(model=model, effort="high"), premium=True,
                                    capabilities=self.caps("anthropic", model, "high"))

    def test_premium_profile_cannot_smuggle_a_hidden_family(self):
        for model in ("claude-opus-4-1/claude-fable-5", "claude-fable-5/claude-opus-4"):
            with self.subTest(model=model), self.assertRaises(router.PolicyError):
                router.choose_route("anthropic", self.scores(risk=10),
                                    policy=self.policy_with(model=model, effort="high"), premium=True,
                                    capabilities=self.caps("anthropic", model, "high"))

    def test_policy_can_still_restrict_opus(self):
        policy = router.load_policy()
        policy["restricted"]["anthropic"].append("opus")
        with self.assertRaisesRegex(router.PolicyError, "restricted"):
            router.choose_route("anthropic", self.scores(risk=10), policy=policy, premium=True,
                                capabilities=self.caps("anthropic", "opus", "high"))

    def test_a_policy_without_a_premium_profile_fails_closed(self):
        policy = router.load_policy()
        del policy["providers"]["anthropic"]["premium"]
        with self.assertRaisesRegex(router.PolicyError, "premium"):
            router.choose_route("anthropic", self.scores(risk=10), policy=policy, premium=True,
                                capabilities=self.caps("anthropic", "opus", "high"))

    def test_premium_candidate_needs_high_risk_or_critical_profile(self):
        self.assertTrue(router.premium_candidate(self.scores(risk=10)))
        self.assertTrue(router.premium_candidate(self.scores(risk=10, algorithm=25)))
        self.assertFalse(router.premium_candidate(self.scores(risk=9)))
        self.assertFalse(router.premium_candidate(self.scores(algorithm=25)))  # strong, not critical
        self.assertFalse(router.premium_candidate(self.scores()))
        caps = self.caps("anthropic", "sonnet", "xhigh")
        critical = router.choose_route("anthropic", self.scores(risk=10, algorithm=25), capabilities=caps)
        self.assertEqual(critical["profile"], "critical")
        self.assertTrue(router.premium_candidate(critical))
        self.assertTrue(router.premium_candidate({"profile": "critical"}))
        plain = router.choose_route("anthropic", self.scores(coupling=5),
                                    capabilities=self.caps("anthropic", "haiku", "low"))
        self.assertFalse(router.premium_candidate(plain))
        for junk in (None, "risk", {}, {"risk": "10"}, {"risk": True}):
            with self.subTest(junk=junk):
                self.assertFalse(router.premium_candidate(junk))


class RiskWordTests(unittest.TestCase):
    def ticket(self, title):
        return "# 01 — %s\n\n**Зона:** `src/a.py`\n\n## Критерии приёмки\n\n- [ ] работает\n" % title

    def profile(self, title):
        scores = router.assess_ticket(self.ticket(title))
        return scores["risk"], router.assess_scores(scores)[1]

    def test_risky_words_in_russian_and_english_are_not_cheap(self):
        for title in (
                "Проверка токена webhook-подписи", "Verify the API key", "Rotate credentials",
                "Check webhook signature", "Run subprocess safely", "Open a shell",
                "Deploy to production", "Выкатить в прод", "Деплой на сервер", "Шифрование файла",
                "Хранение секрета", "Новый ключ доступа", "Вебхук от банка", "Проверка подписи",
                "encrypt the backup", "Secret store", "Token refresh"):
            with self.subTest(title=title):
                risk, profile = self.profile(title)
                self.assertEqual(risk, 10)
                self.assertNotEqual(profile, "cheap")

    def test_everyday_words_stay_cheap(self):
        for title in ("Продолжить заявку", "Включить кнопку", "Исключение в форме",
                      "Product list", "Продукты в каталоге", "Fix button colour"):
            with self.subTest(title=title):
                self.assertEqual(self.profile(title), (0, "cheap"))


if __name__ == "__main__":
    unittest.main()
