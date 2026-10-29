"""Summarize Claude Code OTel data (<dir>/metrics.jsonl, logs.jsonl) as a compact table.

Usage: python otel_summary.py [--dir otel] [--all]
Rows: query_source x model x effort -> tokens in/out/cacheRead/cacheCreation + cost USD.
Default shows subagent rows only; --all adds main/auxiliary. The main-vs-subagent share line always
uses everything. Assumes delta temporality (Claude Code default). Costs are estimates, not charges.
Event query_source mapping: "agent:*" = subagent, "sdk"/"repl_main_thread" = main, others = auxiliary.
"""
import argparse
import collections
import glob
import json
import os

TOK = {"input": 0, "output": 1, "cacheRead": 2, "cacheCreation": 3}
EVT = ("input_tokens", "output_tokens", "cache_read_tokens", "cache_creation_tokens")


def attrs(lst):
    out = {}
    for a in lst or []:
        v = a.get("value", {})
        out[a["key"]] = next(iter(v.values()), None) if v else None
    return out


def records(d, name):
    for p in glob.glob(os.path.join(d, name + ".jsonl")):
        with open(p, encoding="utf-8") as f:
            for ln in f:
                ln = ln.strip()
                if ln:
                    yield json.loads(ln)


def event_source(qs):
    qs = str(qs)
    if qs.startswith("agent:"):
        return "subagent"
    if qs in ("sdk", "repl_main_thread", "main"):
        return "main"
    return "auxiliary"


def collect(d):
    """-> (metrics, events): {(source, model, effort): [in, out, cacheRead, cacheCreation, cost]}"""
    met = collections.defaultdict(lambda: [0.0] * 5)
    ev = collections.defaultdict(lambda: [0.0] * 5)
    for doc in records(d, "metrics"):
        for rm in doc.get("resourceMetrics", []):
            for sm in rm.get("scopeMetrics", []):
                for m in sm.get("metrics", []):
                    if m["name"] not in ("claude_code.token.usage", "claude_code.cost.usage"):
                        continue
                    for dp in (m.get("sum") or m.get("gauge") or {}).get("dataPoints", []):
                        a = attrs(dp.get("attributes"))
                        row = met[(a.get("query_source") or "?", a.get("model") or "?", a.get("effort") or "-")]
                        val = float(dp.get("asDouble", dp.get("asInt", 0)))
                        if m["name"].endswith("cost.usage"):
                            row[4] += val
                        elif a.get("type") in TOK:
                            row[TOK[a["type"]]] += val
    for doc in records(d, "logs"):
        for rl in doc.get("resourceLogs", []):
            for sl in rl.get("scopeLogs", []):
                for r in sl.get("logRecords", []):
                    a = attrs(r.get("attributes"))
                    name = a.get("event.name") or str((r.get("body") or {}).get("stringValue", ""))
                    if not name.endswith("api_request"):
                        continue
                    row = ev[(event_source(a.get("query_source")), a.get("model") or "?", a.get("effort") or "-")]
                    for i, k in enumerate(EVT):
                        row[i] += float(a.get(k) or 0)
                    row[4] += float(a.get("cost_usd") or 0)
    return met, ev


def table(title, data, show_all):
    print("== " + title)
    print("%-10s %-24s %-7s %11s %9s %12s %12s %10s"
          % ("source", "model", "effort", "in", "out", "cacheRead", "cacheCreate", "cost USD"))
    for k in sorted(data):
        if show_all or k[0] == "subagent":
            r = data[k]
            print("%-10s %-24s %-7s %11d %9d %12d %12d %10.4f" % (k + tuple(int(x) for x in r[:4]) + (r[4],)))
    tot = collections.defaultdict(float)
    for k, r in data.items():
        tot[k[0]] += r[4]
    s = sum(tot.values())
    pct = lambda n: (100 * tot[n] / s) if s else 0.0
    print("share of cost: main %.1f%% (%.4f)  subagent %.1f%% (%.4f)  auxiliary %.1f%% (%.4f)  total %.4f USD"
          % (pct("main"), tot["main"], pct("subagent"), tot["subagent"], pct("auxiliary"), tot["auxiliary"], s))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", default="otel")
    ap.add_argument("--all", action="store_true", help="show main and auxiliary rows too (default: subagent only)")
    a = ap.parse_args()
    met, ev = collect(a.dir)
    table("metrics (claude_code.token.usage / cost.usage)", met, a.all)
    table("api_request events", ev, a.all)


if __name__ == "__main__":
    main()
