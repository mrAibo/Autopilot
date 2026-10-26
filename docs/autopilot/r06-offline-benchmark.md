# R06 — matched offline benchmark, 26 October 2026

**Status:** measured *host CLI/Git behavior*, NOT AI model usage, dollars,
actual autonomous agent quality, or realized token savings.

Raw machine-readable evidence (all **20 individual samples**):
[`benchmarks/r06-20261026-offline.json`](benchmarks/r06-20261026-offline.json).

## Method and exact code

The benchmark is a **new synthetic measurement**, not the older historical
unmatched 1.x/2.0 observations in [benchmark.md](benchmark.md).

- Historical baseline: **2.2.0**, Git
  `25b5fbada50742f1b6a900a5a92800759e5c74d4`.
- Current development candidate measured: **2.3.0-dev**, Git
  `3eb5ecbfc05524d0095c6b53044c5d1e3f105560`.
- Runner: user-owned Windows host Aibo, Python **3.13**, fresh local Git
  repositories under the OS temporary folder.
- Inputs: byte-identical synthetic manifest, two ticket descriptions with
  traced requirements, planned dependencies and zones. Same CLI commands,
  Python/Git environment and acceptance checks for each version.
- Two predetermined scenarios: **(a)** initiate an otherwise empty run and
  attempt `finish` (correct behavior is a rejection);
  **(b)** record two reviewed/approved synthetic tickets with
  `3/0` and `5/0` reported tests, mark G1–G4, produce three Git commits
  and finish (correct behavior is acceptance).
  The synthetic commits can be **empty** and test counts are fixture records,
  not independent verification of product code.
- **Five repetitions per scenario and version**, alternating execution order
  on each repetition (20 fresh disposable Git runs). Timings include
  Python interpreter starts, CLI state manipulation and Git operations;
  clock is local `time.perf_counter_ns`. Time is summarized as
  **median measured milliseconds**, not as a model benchmark.

## Measured outcomes

| Fixed scenario | 2.2.0 | 2.3.0-dev | Meaning |
|---|---:|---:|---|
| Invalid empty `finish` correctly refused | **0/5** | **5/5** | Baseline falsely accepted five empty runs |
| Invalid empty `finish`: median CLI/Git time | 414.05 ms | 241.47 ms | Two `ap.py` calls, 0 Git commits in each |
| Valid two-ticket run correctly accepted | **5/5** | **5/5** | Recorded two ticket completions, G1–G4 and finish |
| Valid two-ticket run: median CLI/Git time | 2475.37 ms | 2011.82 ms | 12 `ap.py` calls, 3 Git commits in each |
| Actual AI executor calls | **0** | **0** | No native, Claude Code, Codex or API execution |
| Provider-reported input/output/cache tokens | **N/A** | **N/A** | Not measured |
| Provider billing and cost per accepted AI task | **N/A** | **N/A** | Not measured |

The median for the valid host-side toy workflow happened to be **18.7%
lower** on 2.3. This is a **small, five-repetition local observation**;
it is not evidence of a generalized 18.7% performance or cost improvement
for real projects. Execution differences include OS process scheduling,
filesystem cache and unrelated historical code changes. The more important
observed quality difference is the refusal to finalize missing work.

The optional `off` vs `lean` Codex prompt comparison measured
**0 UTF-8 bytes** of *extra optimization rules* in `off` versus
**414 UTF-8 bytes** in `lean` (+414 bytes). That is additional text
before a hypothetical model call, **not actual input tokens**. It
establishes **no token savings** from `lean`. No performance claim
for lean is warranted without matched successful real-provider A/B tasks.

## Reproduction

On a checkout containing the **full baseline Git history** (GitHub CI
normally checks out a shallow history, so run this explicitly on a full
developer checkout):

```powershell
py -3.13 tools/benchmark-r06.py --repeat 5 --output r06-fresh.json
py -3.13 -m unittest discover -s tests -p test_r06_benchmark.py -v
```

The script reads committed source from the two Git revisions, prepares
fresh temporary repos, alternates old/new execution order and writes
the report only to the requested new output path (refuses overwrite).
It aborts on dirty source checkout, missing baseline history or a
setup/command failure. No model client, network connection, paid API,
developer secrets or modification of the owner's actual projects.

Its five deterministic contract tests run in the normal cross-platform CI,
without requiring the historical checkout in that CI. Each sample includes
the exact scenario, accepted state, recorded commands/commits, exit code
and measured duration. Missing provider data are JSON `null`, not zero.

## What remains to measure before a savings claim

An authorized *matched* real evaluation would require the same user brief
and code baseline; the same provider/model/Effort/sandbox; both optimization
modes in alternating order; independent test results, Git acceptance,
verified model/cached input/output token usage and timestamps from the
provider. Cost may be computed only with verified versioned pricing and
usage accounting. Reports must include failures and retries **per accepted
task**. This was explicitly **not performed** because the original brief
prohibits paid API tests and real-agent availability is not yet verified.

See [optimization.md](optimization.md) for the A/B protocol and
[scope-and-labs.md](scope-and-labs.md) for product-versus-experiment scope.
Version stays `2.3.0-dev`.
