"""Retry policy is deterministic and never auto-upgrades to a costly model."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "skills" / "autopilot" / "tools"))
import retry_policy


class Triage(unittest.TestCase):
    def test_environment_errors_are_not_model_failures(self):
        self.assertEqual(retry_policy.classify("Permission denied: read /etc/app"), "environment")
        self.assertEqual(retry_policy.decide("environment")["action"], "blocked")

    def test_failing_assertion_repair_same_model(self):
        self.assertEqual(retry_policy.classify("AssertionError expected: 123"), "tests")
        advice = retry_policy.decide("tests")
        self.assertEqual((advice["action"], advice["model"]), ("repair", "same"))

    def test_reasoning_requires_review_not_auto_upgrade(self):
        self.assertEqual(retry_policy.decide("reasoning")["action"], "replan")
        self.assertNotEqual(retry_policy.decide("reasoning")["model"], "strong")

    def test_ambiguous_requirements_request_clarification(self):
        self.assertEqual(retry_policy.classify("Conflicting requirements"), "requirements")
        self.assertEqual(retry_policy.decide("requirements")["action"], "clarify")

    def test_unknown_requires_investigation(self):
        self.assertEqual(retry_policy.classify("something unrelated"), "unknown")
        self.assertEqual(retry_policy.decide("unknown")["model"], "same")

    def test_limits_are_absolute(self):
        self.assertEqual(retry_policy.decide("tests", retries=2)["action"], "stop")
        self.assertEqual(retry_policy.decide("tests", repairs=2)["action"], "stop")

    def test_invalid_arguments_rejected(self):
        with self.assertRaises(ValueError):
            retry_policy.decide("garbage")
        with self.assertRaises(ValueError):
            retry_policy.decide("tests", retries=-1)
        with self.assertRaises(ValueError):
            retry_policy.decide("tests", retries=True)


if __name__ == "__main__":
    unittest.main()
