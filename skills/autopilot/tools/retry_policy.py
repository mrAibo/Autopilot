#!/usr/bin/env python3
"""Deterministic, conservative failure triage for Autopilot.

No language model calls, no automatic paid retry. The caller must verify and
re-authorize a model route when the advice requires a different strategy.
"""
import argparse
import json
import re
import sys

KINDS = ("environment", "dependency", "requirements", "tests", "reasoning", "security", "unknown")
PATTERNS = (
    ("security", ("secret leaked", "token exposed", "credential leak", "private key",
                  "секрет утек", "ключ доступа раскрыт")),
    ("environment", ("permission denied", "access denied", "connection refused",
                     "could not resolve host", "no space left", "disk full",
                     "timed out connecting", "доступ запрещен", "нет соединения")),
    ("dependency", ("modulenotfounderror", "cannot find module", "no module named",
                    "missing dependency", "missing package", "отсутствует модуль")),
    ("requirements", ("ambiguous requirement", "unspecified behavior", "needs clarification",
                      "conflicting requirements", "неясные требования", "нужны уточнения")),
    ("tests", ("assertionerror", "expected:", "tests failed", "test failed",
               "failed assertions", "тест не прошёл", "assert failed")),
    ("reasoning", ("algorithmic dead end", "incorrect algorithm", "design contradiction",
                   "алгоритм неверен", "архитектура не работает")),
)


def classify(text):
    """Explainable heuristics; ambiguity always defaults to unknown, not upgrade."""
    if not isinstance(text, str):
        raise ValueError("failure details must be text")
    lower = text.casefold()[:12000]
    for kind, words in PATTERNS:
        if any(word in lower for word in words):
            return kind
    return "unknown"


def decide(kind, retries=0, repairs=0):
    if kind not in KINDS:
        raise ValueError("unknown failure category")
    if type(retries) is not int or type(repairs) is not int or min(retries, repairs) < 0:
        raise ValueError("retry/repair counters must be nonnegative integers")
    if retries >= 2 or repairs >= 2:
        return {"category": kind, "action": "stop", "model": "none",
                "why": "attempt limit reached; report the remaining blocker"}
    responses = {
        "environment": ("blocked", "none", "repair permissions/network/disk first, not model"),
        "dependency": ("blocked", "none", "restore missing dependency or tool first"),
        "requirements": ("clarify", "none", "resolve ambiguity or replan before retry"),
        "tests": ("repair", "same", "fix failed assertion in the same context; run tests"),
        "reasoning": ("replan", "review", "reassess design; get a new approved model route if warranted"),
        "security": ("stop", "none", "security violation needs human review"),
        "unknown": ("investigate", "same", "find a reproducible cause before retrying"),
    }
    action, model, why = responses[kind]
    return {"category": kind, "action": action, "model": model, "why": why}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=KINDS, help="explicitly diagnosed category")
    parser.add_argument("--text", help="failure output (not persisted); use only sanitized excerpts")
    parser.add_argument("--retries", type=int, default=0)
    parser.add_argument("--repairs", type=int, default=0)
    args = parser.parse_args(argv)
    try:
        kind = args.kind or classify(args.text or "")
        answer = decide(kind, args.retries, args.repairs)
    except ValueError as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}))
        return 2
    print(json.dumps(answer, ensure_ascii=False, indent=2))
    return 0 if answer["action"] in ("repair", "investigate") else 2


if __name__ == "__main__":
    sys.exit(main())
