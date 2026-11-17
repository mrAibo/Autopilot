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
            "cheap_read": {"model": "gpt-6-luna", "effort": "low"},
            "cheap_code": {"model": "gpt-6-luna", "effort": "low"},
            "balanced": {"model": "gpt-6-luna", "effort": "high"},
            "strong": {"model": "gpt-6.1-sol", "effort": "high"},
            "critical": {"model": "gpt-6.1-sol", "effort": "high"},
        },
        "anthropic": {
            # `cheap` is the legacy name of cheap_read (load_policy keeps them in step);
            # choose_route takes cheap_code for the mechanical-ticket score band, see CODE_MIN_SCORE.
            "cheap": {"model": "haiku", "effort": "low"},
            "cheap_read": {"model": "haiku", "effort": "low"},
            "cheap_code": {"model": "haiku", "effort": "high"},
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
# haiku / sonnet, optionally claude-, a leading 3-5 / 3, trailing version or date, or the `-latest` alias.
ALLOWED_SUBAGENT_RE = re.compile(
    r"(claude-)?(\d+([.-]\d+)*-)?(haiku|sonnet)(-\d+([.-]\d+)*)?(-latest)?(\[\w+\])?")
# Same shape for opus; only reachable through premium_ok / premium.
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
                # `cheap` and `cheap_read` are one profile under two names
                for src, dst in (("cheap", "cheap_read"), ("cheap_read", "cheap")):
                    if src in profiles and dst not in profiles:
                        result["providers"][provider][dst] = dict(result["providers"][provider][src])
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


# Cheap scores above this sum mean a coding ticket (cheap_code); at or below it, reading (cheap).
CODE_MIN_SCORE = 10
# A planner's `**Класс:** механический`: cheap, and above the reading band.
MECHANICAL = {"algorithm": 5, "coupling": 5, "uncertainty": 0, "context": 0, "testing": 5}


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


# Zones that are sensitive by where they live, whatever the ticket text says: whole path segments
# (split on / \ . _ - and space) and exact file names, never a substring (`secretary` is not `secret`).
SENSITIVE_WORDS = frozenset(
    "auth payment payments migration migrations secret secrets credential credentials env "
    "авторизация платеж платежи миграция миграции ключ ключи секрет секреты".split())
SENSITIVE_FILES = frozenset(("claude_agent_guard", "gate_sign", "model_router", "state_io"))
_SEGMENT_SPLIT = re.compile(r"[/\._\- ]")


def sensitive_zone(zone):
    path = zone.replace("\\", "/").lower()
    name = path.rsplit("/", 1)[-1]
    return (name == "gate.key" or name.rsplit(".", 1)[0] in SENSITIVE_FILES
            or any(w in SENSITIVE_WORDS for w in _SEGMENT_SPLIT.split(path)))


CLASS_RE = re.compile(r"^\*\*(?:Класс|Class):\*\*[ \t]*(\S*)", re.M)
RISK_HEADER_RE = re.compile(r"^\*\*(?:Риск|Risk):\*\*[ \t]*(\S*)", re.M)
WHY_RE = re.compile(r"^\*\*(?:Причина класса|Class reason):\*\*[ \t]*(.*?)[ \t]*$", re.M)
CLASS_VALUES = {"механический": "mechanical", "mechanical": "mechanical", "обычный": "normal", "normal": "normal",
                "сложный": "complex", "complex": "complex"}
RISK_VALUES = {"обычный": False, "normal": False, "высокий": True, "high": True}
WHY_MAX = 200


def docs_only(zones):
    """True when every zone path is Markdown or under docs/ (no zones: not docs-only)."""
    return bool(zones) and all(z.lower().endswith(".md") or z.replace("\\", "/").lower().startswith("docs/")
                               for z in zones)


def _header(rx, text):
    found = rx.search(text)
    return found.group(1).casefold().strip(".,;") if found else ""


def ticket_headers(text):
    """The planner's three headers: (class, high_risk, why). Unknown or missing class is `normal`,
    a missing risk is not high; `why` is the one phrase after `**Причина класса:**` ("" if absent)."""
    found = WHY_RE.search(text)
    return (CLASS_VALUES.get(_header(CLASS_RE, text), "normal"),
            RISK_VALUES.get(_header(RISK_HEADER_RE, text), False),
            found.group(1) if found else "")


def plan_problems(text):
    """What a new plan must still say about one ticket (empty list = fine): a valid class, a reason of 1..200 characters,
    and, if present, a valid risk. Old runs are not checked by assess_ticket, only `check-plan` asks for this."""
    problems = []
    if _header(CLASS_RE, text) not in CLASS_VALUES:
        problems.append("нет `**Класс:** механический|обычный|сложный`")
    why = WHY_RE.search(text)
    if not why or not why.group(1):
        problems.append("нет `**Причина класса:**` (одна фраза)")
    elif len(why.group(1)) > WHY_MAX:
        problems.append("`**Причина класса:**` длиннее %d знаков" % WHY_MAX)
    if RISK_HEADER_RE.search(text) and _header(RISK_HEADER_RE, text) not in RISK_VALUES:
        problems.append("`**Риск:**` — обычный или высокий")
    return problems


def assess_ticket(text):
    """Deterministic score from what the planner wrote, not from words in the ticket.

    Reads the zone, `**Объём:**`, `**Класс:** механический|обычный|сложный` and `**Риск:** обычный|высокий`.
    Risk 10 comes from `**Риск:** высокий` or from a sensitive zone (a floor the class cannot lower);
    a docs-only zone without a planner's high risk is risk 0. `сложный` sets algorithm to 20,
    `механический` keeps the cheap band. No headers: `обычный`, risk by the zone alone.
    """
    zones = re.findall(r"\`([^\`]+)\`", next((s for s in text.splitlines()
                                              if s.startswith("**Зона:**") or
                                              s.startswith("**Zone:**")), ""))
    volume = re.search(r"(?:^|\n)\*\*(?:Объём|Volume):\*\*\s*(\d+)", text)
    lines = int(volume.group(1)) if volume else 0
    klass, planner_risk, _why = ticket_headers(text)
    risky = planner_risk or (not docs_only(zones) and any(sensitive_zone(z) for z in zones))
    scores = {
        "algorithm": 20 if klass == "complex" else 5,
        "coupling": min(20, max(0, (len(zones) - 1) * 5)),
        "uncertainty": 0,
        "context": 15 if lines > 2000 else 10 if lines > 900 else 5 if len(zones) > 2 else 0,
        "testing": 10 if klass == "complex" or risky else 5,
        "risk": 10 if risky else 0,
    }
    if klass == "normal" and not docs_only(zones):
        # ordinary code is never Haiku: 10 + 11 + the rest (5) is 26, the first sum above `cheap`
        scores.update(algorithm=10, uncertainty=11)
    if klass == "mechanical":
        # never below what the zone already scored
        scores.update({k: max(scores[k], v) for k, v in MECHANICAL.items()})
    return scores


def planner_note(text):
    """`class=…; risk=…; why=…` for routing.reason: what the planner decided, in one line."""
    klass, planner_risk, why = ticket_headers(text)
    risk = assess_ticket(text)["risk"] >= 10 or planner_risk
    note = "class=%s; risk=%s" % ({"mechanical": "механический", "normal": "обычный", "complex": "сложный"}[klass],
                                  "высокий" if risk else "обычный")
    return note + ("; why=" + why.replace(";", ",") if why else "")


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


def choose_route(provider, scores, policy=None, capabilities=None, premium=False, note=""):
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
    if tier == "cheap" and score > CODE_MIN_SCORE and "cheap_code" in provider_profiles:
        tier = "cheap_code"
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
    if note:  # planner_note(): class, risk and the planner's phrase
        reason += "; " + str(note)
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
