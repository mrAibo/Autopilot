#!/usr/bin/env python3
"""Fail-closed, provider-aware model routing for Autopilot task executors.

This module does NOT launch agents. The host must verify the proposed model and
effort against its capabilities and dispatch exactly that verified choice.
"""
import argparse
import json
import re
import sys
from pathlib import Path

WEIGHTS = {
    "algorithm": 25,
    "coupling": 20,
    "uncertainty": 15,
    "context": 15,
    "testing": 15,
    "risk": 10,
}
DEFAULT_POLICY = {
    "version": 1,
    "max_parallel": 2,
    "restricted": {
        "openai": ["gpt-6-astra"],
        "anthropic": ["fable", "claude-fable-5"],
    },
    "providers": {
        "openai": {
            "cheap": {"model": "gpt-6-luna", "effort": "low"},
            "balanced": {"model": "gpt-6-luna", "effort": "high"},
            "strong": {"model": "gpt-6.1-sol", "effort": "high"},
        },
        "anthropic": {
            "cheap": {"model": "haiku", "effort": "low"},
            "balanced": {"model": "sonnet", "effort": "medium"},
            "strong": {"model": "sonnet", "effort": "high"},
        },
    },
}


class PolicyError(ValueError):
    pass


def load_json(path):
    with Path(path).open(encoding="utf-8") as source:
        return json.load(source)


def load_policy(path=None):
    if not path:
        return DEFAULT_POLICY
    custom = load_json(path)
    if not isinstance(custom, dict):
        raise PolicyError("policy must be a JSON object")
    result = dict(DEFAULT_POLICY)
    result.update(custom)
    if not isinstance(result.get("providers"), dict):
        raise PolicyError("providers must be a mapping")
    return result


def assess_scores(scores):
    if not isinstance(scores, dict) or set(scores) != set(WEIGHTS):
        raise PolicyError("scores must contain exactly " + ", ".join(WEIGHTS))
    for name, maximum in WEIGHTS.items():
        value = scores[name]
        if type(value) is not int or not 0 <= value <= maximum:
            raise PolicyError("%s must be an integer from 0 to %s" % (name, maximum))
    score = sum(scores.values())
    profile = "cheap" if score <= 25 else "balanced" if score <= 55 else "strong"
    # Risk and dangerous operations demand stronger reasoning regardless of sum.
    if scores["risk"] >= 8 and profile == "cheap":
        profile = "balanced"
    if scores["risk"] >= 10 or scores["algorithm"] >= 20:
        profile = "strong"
    return score, profile


def assess_ticket(text):
    """Conservative, deterministic first-pass heuristic; annotations may refine it."""
    zones = re.findall(r"\`([^\`]+)\`", next((s for s in text.splitlines()
                                              if s.startswith("**Зона:**") or
                                              s.startswith("**Zone:**")), ""))
    lines = int(re.search(r"(?:^|\n)\*\*(?:Объём|Volume):\*\*\s*(\d+)", text).group(1)) \
        if re.search(r"(?:^|\n)\*\*(?:Объём|Volume):\*\*\s*(\d+)", text) else 0
    body = text.lower()
    important = any(k in body for k in (
        "auth", "session", "password", "credential", "secret", "payment",
        "migration", "delete data", "парол", "сесси", "платеж", "миграц",
        "удалени", "авторизац", "ключи доступа"))
    hard = any(k in body for k in (
        "algorithm", "race condition", "consistency", "distributed",
        "encryption", "алгоритм", "гонк", "шифрован", "конкурент"))
    vague = any(k in body for k in ("tbd", "to decide", "неизвестно", "уточнить"))
    return {
        "algorithm": 20 if hard else 5,
        "coupling": min(20, max(0, (len(zones) - 1) * 5)),
        "uncertainty": 15 if vague else 0,
        "context": 15 if lines > 2000 else 10 if lines > 900 else 5 if len(zones) > 2 else 0,
        "testing": 10 if hard or important else 5,
        "risk": 10 if important else 0,
    }


def choose_route(provider, scores, policy=None, capabilities=None):
    policy = policy or DEFAULT_POLICY
    score, profile = assess_scores(scores)
    if provider not in policy["providers"]:
        raise PolicyError("unknown provider %r" % provider)
    assignment = policy["providers"][provider].get(profile)
    if not isinstance(assignment, dict):
        raise PolicyError("missing profile %s for %s" % (profile, provider))
    model, effort = assignment.get("model"), assignment.get("effort")
    if not isinstance(model, str) or not model.strip():
        raise PolicyError("profile model is empty")
    if not isinstance(effort, str) or not effort.strip():
        raise PolicyError("profile effort is empty")
    denied = [str(m).lower() for m in policy.get("restricted", {}).get(provider, [])]
    costly_prefixes = {"openai": ("gpt-6-astra",),
                       "anthropic": ("fable", "claude-fable", "opus", "claude-opus")}
    restricted = (model.lower() in denied or
                  model.lower().startswith(costly_prefixes[provider]))
    if restricted and policy.get("allow_restricted_subagents") is not True:
        raise PolicyError("restricted model %s may not run as a subagent" % model)
    parallel = policy.get("max_parallel", 2)
    if type(parallel) is not int or not 1 <= parallel <= 3:
        raise PolicyError("max_parallel must be between 1 and 3")
    reason = ("score=%d; profile=%s; high-risk=%s" %
              (score, profile, scores["risk"] >= 8))
    route = {"provider": provider, "model": model, "effort": effort,
             "profile": profile, "score": score, "factors": scores,
             "reason": reason, "max_parallel": parallel,
             "requires_review": scores["risk"] >= 8 or profile == "strong",
             "status": "blocked", "error": "No verified host capabilities"}
    # Explicit host advertisement is mandatory. A skill prompt alone cannot
    # guarantee actual model/effort selection and must not imply it can.
    if capabilities is None:
        return route
    if not isinstance(capabilities, dict) or capabilities.get("provider") != provider:
        route["error"] = "Provider capabilities missing or mismatched"
        return route
    models = capabilities.get("models", {})
    supported = models.get(model) if isinstance(models, dict) else None
    if not isinstance(supported, list) or effort not in supported:
        route["error"] = "Model/effort unavailable in this harness"
        return route
    if capabilities.get("model_selection") is not True:
        route["error"] = "Host cannot enforce per-subagent model selection"
        return route
    route["status"] = "ready"
    route.pop("error")
    return route


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticket", type=Path, help="ticket Markdown file")
    parser.add_argument("--provider", required=True, choices=["openai", "anthropic"])
    parser.add_argument("--policy", type=Path)
    parser.add_argument("--capabilities", type=Path,
                        help="host-verified JSON (required to authorize dispatch)")
    parser.add_argument("--scores", help="JSON object with six scored factors")
    args = parser.parse_args(argv)
    try:
        text = args.ticket.read_text(encoding="utf-8")
        scores = json.loads(args.scores) if args.scores else assess_ticket(text)
        capabilities = load_json(args.capabilities) if args.capabilities else None
        route = choose_route(args.provider, scores,
                             load_policy(args.policy), capabilities)
    except (ValueError, OSError, json.JSONDecodeError, TypeError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(route, ensure_ascii=False, indent=2))
    return 0 if route["status"] == "ready" else 2


if __name__ == "__main__":
    sys.exit(main())
