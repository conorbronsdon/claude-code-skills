---
name: eval-integrity
description: Audit an LLM evaluation or benchmark repo for integrity and credibility practices. Use when asked to "audit my benchmark," "is my eval trustworthy," "check my leaderboard for contamination," "review this benchmark's methodology," or "what would a reviewer attack in my eval." Greps the target repo for evidence across seven dimensions (pre-registration, contamination, holdout hygiene, judge validity, statistical honesty, reproducibility, leaderboard exclusions) and emits a scored report with file:line evidence, severity, and concrete fixes. Spawns one subagent per dimension in parallel.
---

# eval-integrity — Benchmark Credibility Audit

User-invokable auditor for LLM evaluation and benchmark repos. It answers one question: **if you published this benchmark's numbers, would they survive an adversarial reviewer?**

Most benchmark repos have a runner and a leaderboard but lack the integrity scaffolding that makes a published score mean what it appears to mean. This skill checks for that scaffolding, names what is missing, and rates whether each gap *invalidates published numbers* or is *nice-to-have*.

The checks below were extracted from hardening a real agent benchmark ([cot-bench](https://github.com/conorbronsdon/cot-bench)) for an external grant review. Where a check needs a concrete example, cot-bench file names appear as illustrations — they are hints for what good looks like, not paths the auditor expects to find in your repo.

This is the static-analysis cousin of `code-review`: same parallel-subagent orchestration, but the subagents audit eval methodology instead of code correctness.

---

## When to Use

- Before submitting a benchmark to a grant, conference, or public leaderboard.
- When someone says "I don't trust those numbers" and you need to know if they're right.
- After building an eval, before publishing the first headline result.
- Periodically, as a benchmark accretes models and the leaderboard becomes load-bearing.

## When NOT to Use

- A repo that is not an eval or benchmark (no scoring, no leaderboard, no judge). This skill has nothing to grade.
- A toy eval with no published numbers and no intent to publish. Integrity scaffolding is overhead until someone relies on the score.

---

## Step 1: Confirm the target is a benchmark and locate its parts

Establish the repo is gradable, then map where the audit will look. Run from the target repo root:

```bash
# Scoring / judging present?
rg -l --hidden -g '!.git' "judge|rubric|score|grade|leaderboard|eval" .
# Where do results / leaderboards live?
rg -l "leaderboard|results|latest\.csv|\.parquet" .
# Is there a stated methodology or governance doc?
rg -l -i "methodology|governance|contamination|pre.?registration" .
```

If none of these hit, the repo is probably not a benchmark. Stop and say so.

Record for the subagents:
- Absolute repo path.
- Branch + HEAD commit SHA (`git rev-parse HEAD`).
- The scoring entry point(s), the results directory, and any methodology/governance docs.

## Step 2: Spawn one subagent per dimension, in parallel

Spawn the seven dimension auditors in **a single tool-call batch** so they run in parallel. Each gets the repo path, HEAD SHA, the located parts from Step 1, and its dimension's audit brief. The paste-ready briefs live in `patterns/dimension-prompts.md` — one per dimension, each already carrying its grep patterns, severity rule, and report contract.

The seven dimensions:

| # | Dimension | The question it asks |
|---|-----------|----------------------|
| 1 | **Pre-registration** | Is the run's definition (corpus hash, judge panel, seeds, temps) fixed on disk *before* results exist, so a maintainer cannot re-run until the numbers look good? |
| 2 | **Contamination** | Are corpus authors (and their model family) barred from being contestants? Is per-scenario authorship recorded? Is there a private holdout with a published public-vs-holdout gap? |
| 3 | **Holdout hygiene** | Can holdout content leak — via CI logs, workflow artifacts, committed transcripts, or error messages? |
| 4 | **Judge validity** | Is the judge model pinned to the model *actually served*? Are multi-judge agreement stats reported? Are judge-family-vs-contestant conflicts, length/verbosity bias, and halo effects controlled? |
| 5 | **Statistical honesty** | Do headline numbers carry confidence intervals? Is micro-vs-macro aggregation stated? Is pass@k vs pass^k disambiguated? Are seeds fixed and multiple-comparison risk acknowledged? |
| 6 | **Reproducibility** | Is there a deterministic re-run path, cost caps / resume for expensive runs, and pinned environment? |
| 7 | **Leaderboard exclusions** | Are null-agent baselines, holdout rows, and non-default configs kept out of public aggregates — enforced by **tripwire tests**, not just stated intent? |

Each subagent prompt must specify:
1. Repo path (absolute), branch, HEAD SHA.
2. The located scoring/results/docs from Step 1.
3. The dimension brief from `patterns/dimension-prompts.md`.
4. The exact report contract (Step 3 format), capped at ~400 words.

If the repo is small (one scoring file, no CI, no leaderboard), you may run the dimensions inline yourself instead of spawning subagents. Parallel subagents pay off on a real benchmark with CI, a results pipeline, and a methodology doc.

## Step 3: Scoring rule each subagent applies

Every dimension returns one rating, with evidence:

- **PRESENT** — the practice is implemented AND enforced (code or test, not just prose). Cite the file:line.
- **PARTIAL** — documented or half-built. The intent exists; the enforcement does not (e.g. governance.md promises a holdout gap, but no code computes it; a comment says "authors excluded" but no guard blocks it).
- **ABSENT** — no evidence in code, tests, or docs.

Evidence is mandatory. A rating with no `file:line` (or an explicit "searched X, Y, Z — found nothing") is not a finding, it's a guess. Reject it.

## Step 4: Assign severity

Severity is about consequence, not effort. Two levels:

- **INVALIDATING** — the gap means a published number could be wrong, gamed, or non-comparable, and a reviewer who finds it can dismiss the result. Examples: no author-is-contestant guard (contamination), judge not pinned to the served model (silent drift), holdout content reachable in CI artifacts (leak), no CIs on a headline ranking built from few scenarios (noise sold as signal), null-agent or holdout rows in the public leaderboard with no tripwire test (gameability / overfitting hidden).
- **HARDENING** — the gap weakens credibility or auditability but does not by itself invalidate a number. Examples: agreement stats present but not chance-corrected (within-0.2 rate instead of Krippendorff's alpha), no resume/cost-cap on expensive runs, environment pinned in prose but not a lockfile, multiple-comparison risk unacknowledged in an otherwise CI'd board.

When unsure, ask: *can a critic use this gap to throw out the headline number?* If yes, INVALIDATING.

## Step 5: Assemble the report

Collect the seven subagent reports into one scored audit. Lead with the verdict and the invalidating gaps — those are what the author needs to fix before publishing.

```
EVAL-INTEGRITY AUDIT — <repo> @ <short-sha> — <date>

VERDICT: <PUBLISH-READY | N INVALIDATING GAP(S) | NOT A BENCHMARK>
Score: <count PRESENT>/7 present, <count PARTIAL> partial, <count ABSENT> absent

INVALIDATING GAPS (fix before publishing)
- [<dimension>] <one line>. Evidence: <file:line or "absent: searched X,Y,Z">. Fix: <concrete change>.

HARDENING GAPS (raise credibility)
- [<dimension>] <one line>. Evidence: <…>. Fix: <…>.

PER-DIMENSION
1. Pre-registration    — PRESENT | PARTIAL | ABSENT  — <evidence> — <fix if not PRESENT>
2. Contamination       — …
3. Holdout hygiene     — …
4. Judge validity      — …
5. Statistical honesty — …
6. Reproducibility     — …
7. Leaderboard excl.   — …

STRENGTHS (what's already solid — one line each)
- …
```

Rules for the report:
- **Lead with what invalidates.** Hardening gaps go below. Strengths last.
- **Every gap carries a concrete fix**, not "consider improving X." Name the file to add, the guard to write, the test to add. If cot-bench solves it a particular way, that pattern is a fair suggested fix.
- **No fix is "add more scenarios"** unless low scenario count is the specific finding (e.g. CIs so wide the ranking is noise).
- **Plain and direct.** Short sentences. No hype. State the gap, the evidence, the fix.

## Step 6: Offer the fixes (do not auto-apply)

Auditing is read-only. After the report, ask which gaps to fix. Applying a fix changes the target repo's methodology — that is the author's call, one gap at a time, with their approval. Do not edit the benchmark, re-run any eval, or touch a leaderboard as part of the audit.

---

## Why these seven

Each dimension maps to a way a benchmark's numbers get dismissed in review:

- **Pre-registration** defeats run cherry-picking ("you re-ran until it looked good").
- **Contamination** defeats "the author's model graded the author's exam."
- **Holdout hygiene** defeats "your private set isn't private — it's in the CI logs."
- **Judge validity** defeats "your judge drifted / favors its own family / rewards length."
- **Statistical honesty** defeats "that ranking is sampling noise."
- **Reproducibility** defeats "no one can re-run this."
- **Leaderboard exclusions** defeats "a do-nothing agent ranks mid-board" and "you trained on what you published."

A benchmark that passes all seven is one whose headline number a skeptical reviewer has to take seriously.

## Cross-references

- `patterns/dimension-prompts.md` — paste-ready audit brief per dimension, with grep patterns, severity rule, and report contract.
