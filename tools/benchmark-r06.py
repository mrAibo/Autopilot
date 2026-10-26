#!/usr/bin/env python3
"""R06 matched *offline* Autopilot 2.2 vs 2.3 comparison.

Runs the SAME scripted deterministic CLI/Git fixtures on pinned historical and
current code. Absolutely no agent spawn, LLM, API call, provider billing or
installed project changes. Wall-clock timings measure local CLI/Git overhead,
NOT model execution, active project duration or cost.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

BASELINE = "25b5fbada50742f1b6a900a5a92800759e5c74d4"
FILES = ("skills/autopilot/tools/ap.py",
         "skills/autopilot/phases/dashboard-template.html",
         "skills/autopilot/SKILL.md")
MANIFEST = """# Манифест требований

| ID | Из брифа (дословно) | Статус | Основание | Где |
|----|---------------------|--------|-----------|-----|
| R01 | «принимает заявки» | in-spec | — | spec §2 |
| R02 | «складывает в таблицу» | in-spec | — | spec §4 |
| R03 | «SMS» | dropped | «не надо» | — |
| R05 | «цвета студии» | in-spec | — | spec §6 |
"""


class BenchmarkError(RuntimeError):
    pass


def call(args, *, cwd, env=None, check=True):
    run = subprocess.run(args, cwd=cwd, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True, encoding="utf-8",
                         errors="replace", timeout=30)
    if check and run.returncode:
        raise BenchmarkError("Command failed (%s), exit=%d: %s" %
                             (args[0], run.returncode, run.stderr[-450:]))
    return run


def git(root, *args, check=True):
    return call(["git", "-C", str(root), *args], cwd=root, check=check)


def snapshot(repo, revision, dest):
    files = {}
    for f in FILES:
        out = subprocess.run(["git", "show", revision + ":" + f], cwd=repo,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             timeout=20)
        if out.returncode:
            raise BenchmarkError("Required historical source not available: " + f)
        files[f] = out.stdout
    skill = dest / "skill"
    for f, body in files.items():
        sub = f.removeprefix("skills/autopilot/")
        path = skill / sub
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    return skill


def task(tid, title, reqs, deps, zone, wave):
    return ("# %s — %s\n\n**Требования:** %s\n**Зависит от:** %s\n**Зона:** %s\n"
            "**Волна:** %s\n**Ревью:** нет\n**Модель:** обычная\n\n"
            "## Критерии приёмки\n\n- [ ] задача проверена\n" %
            (tid, title, reqs, deps, " · ".join("`%s`" % x for x in zone), wave))


def init_fixture(skill, location):
    git(location, "init", "-q")
    git(location, "-c", "user.email=benchmark@invalid",
        "-c", "user.name=R06", "commit", "-q", "--allow-empty", "-m", "init")
    ap = location / ".autopilot"
    ap.mkdir()
    shutil.copyfile(skill / "tools" / "ap.py", ap / "ap.py")
    shutil.copyfile(skill / "phases" / "dashboard-template.html",
                    ap / "dashboard.html")
    return ap


def run_fixture(skill, scenario):
    """Run one fresh Git repo and record only objective host observations."""
    with tempfile.TemporaryDirectory(prefix="autopilot-r06-", ignore_cleanup_errors=True) as root_name:
        root = Path(root_name)
        ap = init_fixture(skill, root)
        env = dict(os.environ, AUTOPILOT_NO_UPDATE_CHECK="1")
        counts = {"ap_commands": 0, "git_commits": 0}
        errors = []
        started = time.perf_counter_ns()
        def cmd(*args, allow_failure=False):
            counts["ap_commands"] += 1
            r = call([sys.executable, str(ap / "ap.py"), *args, "--no-serve"],
                     cwd=root, env=env, check=False)
            if r.returncode and not allow_failure:
                errors.append("ap:" + (args[0] if args else "empty"))
            return r
        def commit(subject, allow_empty=False):
            args = ["-c", "user.email=benchmark@invalid",
                    "-c", "user.name=R06", "commit", "-q"]
            if allow_empty:
                args.append("--allow-empty")
            r = git(root, *args, "-m", subject)
            counts["git_commits"] += 1
            return git(root, "rev-parse", "--short", "HEAD").stdout.strip()
        init = cmd("init", "--slug", "r06", "--title", "R06 identical fixture",
                   "--skill-dir", str(skill))
        if init.returncode:
            raise BenchmarkError("Baseline/current init failed")
        def state():
            raw = (ap / "state.js").read_text(encoding="utf-8")
            return json.loads(raw.split("=", 1)[1])
        if scenario == "empty-finish":
            result = cmd("finish", "--result", "should not accept", allow_failure=True)
            final = state()
            outcome = {
                "finish_exit": result.returncode,
                "accepted": bool(final.get("finishedAt")),
                "expected_acceptance": False,
                "correct_gate_behavior": result.returncode != 0 and not final.get("finishedAt"),
            }
        elif scenario == "valid-two-tickets":
            run_dir = ap / state()["dir"]
            (run_dir / "tickets").mkdir(parents=True, exist_ok=True)
            (run_dir / "manifest.md").write_text(MANIFEST, encoding="utf-8")
            (run_dir / "tickets" / "01-core.md").write_text(
                task("01", "Каркас", "R01, R05", "—", ["src/core/"], 1),
                encoding="utf-8")
            (run_dir / "tickets" / "02-service.md").write_text(
                task("02", "Приём", "R01.1, R02, A01", "01", ["src/bot/"], 2),
                encoding="utf-8")
            cmd("tickets")
            cmd("stage", "spec")
            cmd("coverage", "found=0", "fixed=0", "deferred=0")
            cmd("check-plan")
            cmd("ticket", "01", "start")
            sha1 = commit("T01 scoped synthetic task", allow_empty=True)
            cmd("ticket", "01", "done", "--tests", "3/0",
                "--commit", sha1, "--placeholder", "R05")
            cmd("ticket", "02", "start")
            sha2 = commit("T02 scoped synthetic task", allow_empty=True)
            cmd("ticket", "02", "done", "--tests", "5/0", "--commit", sha2)
            cmd("tests", "5/0")
            cmd("blind", "checked=4", "matched=4")
            git(root, "add", "-A")
            commit("fully recorded benchmark run")
            result = cmd("finish", "--result", "synthetic accepted",
                         allow_failure=True)
            final = state()
            gates = final.get("gates") or {}
            checked = all(isinstance(gates.get(k), dict)
                          and gates[k].get("ok") for k in ("G1", "G2", "G3", "G4"))
            accepted = bool(final.get("finishedAt"))
            outcome = {
                "finish_exit": result.returncode,
                "accepted": accepted,
                "expected_acceptance": True,
                "two_done": sum(t.get("status") == "done" for t in final.get("tickets", [])) == 2,
                "four_gates_ok": checked,
                "correct_gate_behavior": (
                    not errors and result.returncode == 0 and accepted
                    and checked and sum(t.get("status") == "done" for t in final["tickets"]) == 2),
            }
        else:
            raise BenchmarkError("Unknown fixed scenario")
        outcome.update(counts)
        outcome["elapsed_ms"] = round((time.perf_counter_ns() - started) / 1e6, 2)
        outcome["host_failures"] = errors
        return outcome


def prompt_proxy(repo):
    path = repo / "skills" / "autopilot" / "tools" / "codex_dispatch.py"
    # Avoid importing optional dispatch modules, provider tools or model clients.
    # Read-only byte measurement from the shipped static optimization rules.
    src = path.read_text(encoding="utf-8")
    import ast
    tree = ast.parse(src)
    function = next(n for n in tree.body
                    if isinstance(n, ast.FunctionDef) and n.name == "optimization_rules")
    expression = ast.Module(body=[function], type_ignores=[])
    scope = {"DispatchError": BenchmarkError}
    exec(compile(expression, str(path), "exec"), scope)
    off, lean = scope["optimization_rules"]("off"), scope["optimization_rules"]("lean")
    return {
        "off_utf8_bytes": len(off.encode("utf-8")),
        "lean_utf8_bytes": len(lean.encode("utf-8")),
        "incremental_utf8_bytes": len(lean.encode("utf-8")) - len(off.encode("utf-8")),
        "measured_provider_tokens": None, "measured_provider_cost": None,
        "interpretation": "prompt bytes only; NOT tokens, savings or billed money",
    }


def benchmark(repo, repetitions=2):
    if not 1 <= repetitions <= 5:
        raise BenchmarkError("Repeat count must be between 1 and 5")
    repo = repo.resolve()
    if git(repo, "status", "--porcelain").stdout.strip():
        raise BenchmarkError("Benchmark requires a clean source checkout")
    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    if head == BASELINE:
        raise BenchmarkError("Current and baseline must be different")
    scenarios = ("empty-finish", "valid-two-tickets")
    runs = []
    with tempfile.TemporaryDirectory(prefix="r06-sources-", ignore_cleanup_errors=True) as scratch:
        base = snapshot(repo, BASELINE, Path(scratch) / "old")
        latest = snapshot(repo, head, Path(scratch) / "new")
        for i in range(repetitions):
            # Alternate order to avoid systematically advantaging the second run.
            for scenario in scenarios:
                versions = (("2.2", base), ("2.3-dev", latest))
                if i % 2:
                    versions = tuple(reversed(versions))
                for label, skill in versions:
                    result = run_fixture(skill, scenario)
                    result.update({"iteration": i + 1, "version": label,
                                   "scenario": scenario})
                    runs.append(result)
    summary = {}
    for scenario in scenarios:
        summary[scenario] = {}
        for version in ("2.2", "2.3-dev"):
            rows = [r for r in runs if r["scenario"] == scenario and
                    r["version"] == version]
            summary[scenario][version] = {
                "correct": sum(bool(r["correct_gate_behavior"]) for r in rows),
                "runs": len(rows),
                "accepted": sum(bool(r["accepted"]) for r in rows),
                "median_elapsed_ms": round(statistics.median(r["elapsed_ms"] for r in rows), 2),
                "ap_commands_per_run": rows[0]["ap_commands"],
                "git_commits_per_run": rows[0]["git_commits"],
            }
    return {
        "kind": "paired-offline-synthetic-host-benchmark",
        "baseline_git_sha": BASELINE,
        "current_git_sha": head,
        "repetitions": repetitions,
        "python_version": sys.version.split()[0],
        "os_name": os.name,
        "runner": "host subprocess / Git / no model",
        "provider_model": None, "provider_effort": None,
        "actual_input_tokens": None, "actual_output_tokens": None,
        "actual_cached_input_tokens": None, "actual_cost_currency": None,
        "actual_cost": None, "live_executor_count": 0,
        "prompt_bytes_off_vs_lean": prompt_proxy(repo),
        "summary": summary, "samples": runs,
        "limitations": [
            "Only deterministic tiny synthetic host workflows, NOT a model coding benchmark",
            "Synthetic Git commits may be empty; no model-generated source reviewed",
            "CLI timing includes Python startup and OS scheduling; few repeats, no causal speed claim",
            "No provider usage, pricing, model identity, quality of AI output or ROI is measured",
            "Old and new behavior intentionally differ on unsafe finish; not matched accepted outputs",
        ],
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--repeat", type=int, default=2)
    p.add_argument("--output", type=Path, help="Optional JSON report (refuse overwrite)")
    args = p.parse_args(argv)
    result = benchmark(args.repo, args.repeat)
    data = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as f:
            f.write(data)
    else:
        print(data)
    return 0 if all(
        result["summary"][scenario]["2.3-dev"]["correct"] == args.repeat
        for scenario in result["summary"]) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, subprocess.TimeoutExpired, BenchmarkError) as exc:
        print("R06 BENCHMARK STOPPED: " + str(exc), file=sys.stderr)
        raise SystemExit(2)
