#!/usr/bin/env python3
"""Fail-closed provider-cap admission and read-only recorded-token audit.

A host ledger threshold, elapsed-time timeout, estimated token count, and
Codex CLI config are NOT a provider-side enforced per-call cap. No external
provider has furnished a verifiable hard-cap integration here. Consequently
real Codex model execution is disallowed by both dispatch entry points.
This module exposes NO flag, file, environment override or self-attestation.
Synthetic offline tests patch assert_enforced_cap in their own process.
"""
import argparse
import json
from pathlib import Path
import re
import sys


class CapUnavailable(ValueError):
    """Provider-side hard cap is absent; deny before any paid call."""


CAP_REASON = "no-verifiable-provider-enforced-per-call-budget"
MAX_RECORDED = 10 ** 15


def assert_enforced_cap(config=None):
    """Fail closed until a verified independent provider hard-cap API exists.

    Neither local timeouts nor tracked tokens can enforce a per-request cap.
    This function is intentionally unconditional, and must not be bypassed
    by caller-supplied arguments, files or environment variables.
    """
    raise CapUnavailable(
        "Paid Codex execution blocked: " + CAP_REASON +
        ". Preflight token threshold and process timeout are not hard caps.")


def _nonnegative(value, name):
    if type(value) is not int or not 0 <= value <= MAX_RECORDED:
        raise ValueError("Invalid recorded token field: " + name)
    return value


def usage_summary(root, ticket):
    """Analyze recorded usage and current ticket receipt, without actions."""
    root = Path(root).resolve()
    if not re.fullmatch(r"[0-9]{2,4}", ticket):
        raise ValueError("Invalid ticket ID")
    state_path = root / ".autopilot" / "state.js"
    if state_path.is_symlink() or not state_path.is_file():
        raise ValueError("Unsafe or missing state ledger")
    content = state_path.read_text(encoding="utf-8")
    if content.startswith("window.STATE"):
        content = content.split("=", 1)[1]
    state = json.loads(content)
    if not isinstance(state, dict) or not isinstance(state.get("usageEvents"), list):
        raise ValueError("Invalid usage ledger")
    budget = state.get("budgetTokens")
    if budget is not None:
        _nonnegative(budget, "budgetTokens")
    events = state["usageEvents"]
    input_sum, output_sum, cache_sum = 0, 0, 0
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("Invalid usage ledger entry")
        inp = _nonnegative(event.get("input"), "input")
        out = _nonnegative(event.get("output"), "output")
        cache = _nonnegative(event.get("cacheRead", 0), "cacheRead")
        if cache > inp:
            raise ValueError("Cached input exceeds recorded total input")
        input_sum += inp
        output_sum += out
        cache_sum += cache

    receipts_dir = root / ".autopilot" / "gui-dispatch"
    receipt_path = receipts_dir / (ticket + ".json")
    if receipts_dir.is_symlink() or receipt_path.is_symlink():
        raise ValueError("Redirected dispatch receipts")
    receipt = None
    if receipt_path.exists():
        try:
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            raise ValueError("Uncertain/corrupt receipt requires manual review") from exc
        if not isinstance(receipt, dict) or receipt.get("ticket") != ticket:
            raise ValueError("Receipt identity mismatch")
    used = input_sum + output_sum
    exceeded = budget is not None and used > budget
    return {
        "status": "read-only-audit",
        "ticket": ticket,
        "execution_permitted": False,
        "reason": CAP_REASON,
        "provider_hard_cap_verified": False,
        "budget_type": "ledger-preflight-soft-threshold",
        "recorded_threshold_tokens": budget,
        "recorded_input_tokens": input_sum,
        "recorded_cached_input_tokens": cache_sum,
        "recorded_output_tokens": output_sum,
        "recorded_total_tokens": used,
        "recorded_events": len(events),
        "recorded_threshold_exceeded": exceeded,
        "recorded_overage_tokens": max(0, used - budget) if budget is not None else None,
        "remaining_recorded_threshold_tokens": max(0, budget - used) if budget is not None else None,
        "existing_receipt": receipt is not None,
        "receipt_status": receipt.get("status") if receipt else None,
        "worker_commit": bool(receipt.get("worker_commit")) if receipt else False,
        "turn_completed": receipt.get("turn_completed") if receipt else None,
        "usage_recorded_on_receipt": receipt.get("usage_recorded") if receipt else None,
        "no_automatic_retry": True,
        "cost_currency": None,
        "cost_amount": None,
        "model_invoked_by_audit": False,
        "note": "No billing invoice or actual server-side model identity attested",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--ticket", required=True)
    args = parser.parse_args(argv)
    try:
        result = usage_summary(args.root, args.ticket)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, TypeError, OSError, KeyError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)[:240],
                          "model_invoked_by_audit": False}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
