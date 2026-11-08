#!/usr/bin/env python3
"""Fail-closed, provider-aware model routing for Autopilot task executors.

This module does NOT launch agents. The host must verify the proposed model and
effort against its capabilities and dispatch exactly that verified choice.
"""
import argparse
from copy import deepcopy
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
            "critical": {"model": "gpt-6.1-sol", "effort": "high"},
        },
        "anthropic": {
            "cheap": {"model": "haiku", "effort": "low"},
            "balanced": {"model": "sonnet", "effort": "medium"},
            "strong": {"model": "sonnet", "effort": "high"},
            "critical": {"model": "sonnet", "effort": "xhigh"},
            # Exceptional tier, never picked by assess_scores: only choose_route(premium=True),
            # which the caller may set only after the user's signed Opus approval.
            "premium": {"model": "opus", "effort": "high"},
        },
    },
}


class PolicyError(ValueError):
    pass


PREMIUM_FAMILIES = ("opus", "fable")
# Exact shape of an allowed Anthropic subagent model after normalization:
# haiku / sonnet, optionally claude-, a leading 3-5 / 3 and trailing version or date.
ALLOWED_SUBAGENT_RE = re.compile(
    r"(claude-)?(\d+([.-]\d+)*-)?(haiku|sonnet)(-\d+([.-]\d+)*)?(\[\w+\])?")
# Same shape for opus (plus the `-latest` alias); only reachable through premium_ok / premium.
OPUS_RE = re.compile(
    r"(claude-)?(\d+([.-]\d+)*-)?opus(-\d+([.-]\d+)*)?(-latest)?(\[\w+\])?")


def normalize_model_name(name):
    """Casefold and drop provider/region prefixes and version suffixes.

    `us.anthropic.claude-opus-4-1-20250805-v1:0`, `bedrock/anthropic.claude-opus-4`
    and `claude-opus-4-1@20250805` all lose their wrappers; the family stays visible.
    """
    value = str(name).strip().casefold().rsplit("/", 1)[-1]
    value = value.rsplit("anthropic.", 1)[-1]
    value = re.sub(r"@[\w.-]+$", "", value)
    return re.sub(r"-v\d+(:\d+)?$", "", value)


def is_premium_model(name):
    """Premium family anywhere in the raw or normalized name (`claude-opus-4/haiku` hides it from the latter)."""
    raw = str(name).casefold()
    return any(f in raw or f in normalize_model_name(name) for f in PREMIUM_FAMILIES)


def is_opus_model(name):
    """True for the opus family in any spelling (bedrock prefixes, `@date`, `[1m]`).

    Fable never counts, even hidden elsewhere in the raw name; hybrids such as
    `opusplan` and names that show a different family after a `/` are not opus.
    """
    if not isinstance(name, str):
        return False
    raw = name.casefold()
    if any(f in raw for f in PREMIUM_FAMILIES if f != "opus"):
        return False
    return OPUS_RE.fullmatch(normalize_model_name(name)) is not None


def is_allowed_subagent_model(name, policy=None, *, premium_ok=False):
    """True only for haiku/sonnet families that no policy list restricts.

    Opus, fable and everything unrecognized are refused in any spelling, except that
    `premium_ok=True` (the caller holds the user's verified Opus approval) also admits
    opus. Fable is refused whatever the flag says. `policy` stays the second argument.
    """
    if not isinstance(name, str) or not name.strip():
        return False
    normalized = normalize_model_name(name)
    opus = premium_ok is True and is_opus_model(name)
    if is_premium_model(name) and not opus:
        return False
    denied = [m.casefold() for m in (policy or DEFAULT_POLICY).get("restricted", {}).get("anthropic", [])]
    if name.strip().casefold() in denied or normalized in denied:
        return False
    return opus or ALLOWED_SUBAGENT_RE.fullmatch(normalized) is not None


def load_json(path):
    with Path(path).open(encoding="utf-8") as source:
        return json.load(source)


def load_policy(path=None):
    """Overlay only specified settings without erasing unrelated safe defaults.

    A partial provider/profile customization must never implicitly remove
    the other provider or the default premium-model deny list.
    """
    result = deepcopy(DEFAULT_POLICY)
    if path is None:
        return result
    custom = load_json(path)
    if not isinstance(custom, dict):
        raise PolicyError("policy must be a JSON object")
    unknown = set(custom) - {
        "version", "max_parallel", "providers", "restricted",
        "allow_restricted_subagents"}
    if unknown:
        raise PolicyError("unknown policy keys: " + ", ".join(sorted(unknown)))
    if "version" in custom and (type(custom["version"]) is not int
                                or custom["version"] != result["version"]):
        raise PolicyError("unsupported policy version")
    if "max_parallel" in custom:
        count = custom["max_parallel"]
        if type(count) is not int or not 1 <= count <= 3:
            raise PolicyError("max_parallel must be between 1 and 3")
        result["max_parallel"] = count
    if "allow_restricted_subagents" in custom:
        if type(custom["allow_restricted_subagents"]) is not bool:
            raise PolicyError("allow_restricted_subagents must be a boolean")
        result["allow_restricted_subagents"] = custom["allow_restricted_subagents"]
    if "providers" in custom:
        providers = custom["providers"]
        if not isinstance(providers, dict):
            raise PolicyError("providers must be a mapping")
        for provider, profiles in providers.items():
            if provider not in result["providers"] or not isinstance(profiles, dict):
                raise PolicyError("unknown or malformed provider: " + str(provider))
            for tier, selection in profiles.items():
                if tier not in result["providers"][provider] or not isinstance(selection, dict):
                    raise PolicyError("unknown or malformed profile: " + str(tier))
                if not selection or set(selection) - {"model", "effort"}:
                    raise PolicyError("profile allows only model and effort settings")
                for field, value in selection.items():
                    if (not isinstance(value, str) or not value or
                            value != value.strip()):
                        raise PolicyError("model and effort must be nonempty exact names")
                    result["providers"][provider][tier][field] = value
    if "restricted" in custom:
        restricted = custom["restricted"]
        if not isinstance(restricted, dict):
            raise PolicyError("restricted must be a provider mapping")
        for provider, names in restricted.items():
            if provider not in result["restricted"] or not isinstance(names, list):
                raise PolicyError("unknown provider or invalid restricted-model list")
            for name in names:
                if not isinstance(name, str) or not name or name != name.strip():
                    raise PolicyError("restricted model names must be exact strings")
                if name.casefold() not in {x.casefold() for x in result["restricted"][provider]}:
                    result["restricted"][provider].append(name)
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
    if scores["risk"] >= 10 and scores["algorithm"] >= 20:
        profile = "critical"
    return score, profile


# Whole words only: "продолжить" and "включить" must not look like prod / ключ.
RISK_RE = re.compile(
    r"\b(?:tokens?|secrets?|api[ _-]?keys?|credentials?|signatures?|webhooks?|subprocess(?:es)?|"
    r"shell|deploy\w*|prod|production|encrypt\w*)\b|"
    r"\b(?:токен\w*|секрет\w*|вебхук\w*|деплой\w*|деплои\w*|шифр\w*|"
    r"ключ(?:а|и|е|ом|ей|ам|ами|ах|у)?|подпис(?:ь|и|ью|ей)|"
    r"прод(?:а|е|у|ом|акшен\w*|акшн\w*)?)\b")


def assess_ticket(text):
    """Conservative, deterministic first-pass heuristic; annotations may refine it."""
    zones = re.findall(r"\`([^\`]+)\`", next((s for s in text.splitlines()
                                              if s.startswith("**Зона:**") or
                                              s.startswith("**Zone:**")), ""))
    lines = int(re.search(r"(?:^|\n)\*\*(?:Объём|Volume):\*\*\s*(\d+)", text).group(1)) \
        if re.search(r"(?:^|\n)\*\*(?:Объём|Volume):\*\*\s*(\d+)", text) else 0
    body = text.lower()
    important = RISK_RE.search(body) is not None or any(k in body for k in (
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


def premium_candidate(route_or_scores):
    """True when a ticket may be offered the Opus tier: risk >= 10 or a critical profile.

    Takes a route from choose_route (reads `profile` and `factors`) or a plain scores dict.
    Only a proposal for the user; it never selects Opus by itself.
    """
    if not isinstance(route_or_scores, dict):
        return False
    if route_or_scores.get("profile") == "critical":
        return True
    scores = route_or_scores.get("factors", route_or_scores)
    risk = scores.get("risk") if isinstance(scores, dict) else None
    return type(risk) is int and risk >= 10


def choose_route(provider, scores, policy=None, capabilities=None, premium=False):
    """Pick model and effort. `premium=True` (anthropic only) uses the opus tier instead of
    the scored one; the caller sets it only for a ticket the user approved. Fable and Astra
    stay closed, and without the flag the result is what it always was."""
    policy = policy or DEFAULT_POLICY
    score, profile = assess_scores(scores)
    use_premium = premium is True and provider == "anthropic"
    if not isinstance(policy, dict) or not isinstance(policy.get("providers"), dict):
        raise PolicyError("policy providers must be a mapping")
    if provider not in DEFAULT_POLICY["providers"] or provider not in policy["providers"]:
        raise PolicyError("unknown provider %r" % provider)
    provider_profiles = policy["providers"][provider]
    if not isinstance(provider_profiles, dict):
        raise PolicyError("provider profiles must be a mapping")
    tier = "premium" if use_premium else profile
    assignment = provider_profiles.get(tier)
    if not isinstance(assignment, dict):
        raise PolicyError("missing profile %s for %s" % (tier, provider))
    model, effort = assignment.get("model"), assignment.get("effort")
    if not isinstance(model, str) or not model or model != model.strip():
        raise PolicyError("profile model must be an exact nonempty name")
    if not isinstance(effort, str) or not effort or effort != effort.strip():
        raise PolicyError("profile effort must be an exact nonempty name")
    restricted_by_provider = policy.get("restricted", {})
    if not isinstance(restricted_by_provider, dict):
        raise PolicyError("restricted must be a provider mapping")
    denied_names = restricted_by_provider.get(provider, [])
    if not isinstance(denied_names, list) or any(
            not isinstance(item, str) for item in denied_names):
        raise PolicyError("restricted names must be a list of strings")
    # A direct caller passing a crafted partial policy cannot remove baseline
    # restricted entries just by replacing the restricted mapping.
    denied = [m.casefold() for m in DEFAULT_POLICY["restricted"][provider]]
    denied += [m.casefold() for m in denied_names]
    restricted = (model.lower() in denied or
                  (provider == "openai" and model.lower().startswith("gpt-6-astra")) or
                  (provider == "anthropic" and is_premium_model(model) and
                   not (use_premium and is_opus_model(model))))
    if restricted and policy.get("allow_restricted_subagents") is not True:
        raise PolicyError("restricted model %s may not run as a subagent" % model)
    parallel = policy.get("max_parallel", 2)
    if type(parallel) is not int or not 1 <= parallel <= 3:
        raise PolicyError("max_parallel must be between 1 and 3")
    reason = ("score=%d; profile=%s; high-risk=%s" %
              (score, profile, scores["risk"] >= 8))
    if use_premium:
        reason += "; premium tier"
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
    if not isinstance(supported, list):
        route["error"] = "Model unavailable in this harness"
        return route
    if type(capabilities.get("effort_selection", True)) is not bool:
        route["error"] = "Invalid effort_selection capability"
        return route
    effort_enforced = capabilities.get("effort_selection", True)
    if effort_enforced and effort not in supported:
        route["error"] = "Model/effort unavailable in this harness"
        return route
    if capabilities.get("model_selection") is not True:
        route["error"] = "Host cannot enforce per-subagent model selection"
        return route
    route["status"] = "ready"
    route["effort_enforced"] = effort_enforced
    route["effort_status"] = "enforced" if effort_enforced else "advisory"
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
