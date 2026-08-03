---
name: eval-integrity
description: Check whether a benchmark's numbers survive review.
version: 0.1.0
author: Conor Bronsdon (conorbronsdon)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [benchmarks, evaluation, llm-eval, reproducibility, contamination, audit, research-integrity]
    category: research
    related_skills: [ssot-check, subagent-driven-development]
    requires_toolsets: [terminal]
---

# Eval Integrity — Benchmark Credibility Audit

Answers one question about an LLM evaluation or benchmark repo: **if you published these numbers,
would they survive an adversarial reviewer?**

Most benchmark repos have a runner and a leaderboard but lack the integrity scaffolding that makes
a published score mean what it appears to mean. This skill checks for that scaffolding across seven
dimensions, cites `file:line` evidence for every rating, and separates gaps that *invalidate
published numbers* from gaps that are merely nice to close.

It is read-only. It reports and offers fixes; it never edits the benchmark, re-runs an eval, or
touches a leaderboard.

## When to Use

- Before submitting a benchmark to a grant, conference, or public leaderboard.
- When someone says "I don't trust those numbers" and you need to know whether they are right.
- After building an eval, before publishing the first headline result.
- Periodically, as a benchmark accretes models and the leaderboard becomes load-bearing.

Skip it for a repo that is not an eval — no scoring, no leaderboard, no judge — and for a toy eval
nobody relies on. Integrity scaffolding is overhead until someone depends on the score.

## Prerequisites

None beyond a local clone of the benchmark. The audit uses `search_files` to find evidence,
`read_file` to check it, `terminal` for `git rev-parse` and `gh`, and `delegate_task` to run the
seven dimensions in parallel. No API keys required.

Listing the target's open pull requests is a **standing step, not optional** — in-flight fixes are
excluded from the gap counts, so skipping it inflates the verdict. That needs `terminal` access to
an authenticated `gh`. Without it, say so in the report and count every finding as a live gap.

## How to Run

```
Use the eval-integrity skill to audit ./path-to-benchmark.
```

With no path given, the current directory is assumed.

## Quick Reference

| # | Dimension | The question it asks |
|---|---|---|
| 1 | Pre-registration | Is the run's definition (corpus hash, judge panel, seeds, temps) fixed on disk *before* results exist? |
| 2 | Contamination | Are corpus authors and their model family barred from being contestants? Is per-scenario authorship recorded? Is there a private holdout with a published public-vs-holdout gap? |
| 3 | Holdout hygiene | Can holdout content leak via CI logs, workflow artifacts, committed transcripts, or error messages? |
| 4 | Judge validity | Is the judge pinned to the model actually served? Are multi-judge agreement stats reported? Are judge-family-vs-contestant conflicts, length bias, and halo effects controlled? |
| 5 | Statistical honesty | Do headline numbers carry confidence intervals? Is micro-vs-macro stated, pass@k vs pass^k disambiguated, seeds fixed and multiple-comparison risk acknowledged? |
| 6 | Reproducibility | Is there a deterministic re-run path, cost caps and resume for expensive runs, and a pinned environment? |
| 7 | Leaderboard exclusions & publish mechanics | Are null-agent baselines, holdout rows, and non-default configs kept out of public aggregates, enforced by tripwire tests rather than stated intent? And does the publish path actually ship what the docs promise? |

Ratings: **PRESENT** (implemented *and* enforced in code or test, not just prose) · **PARTIAL**
(documented, not enforced) · **ABSENT** (no evidence anywhere) · **N/A** (the dimension does not
apply — an eval with no LLM judge rates judge validity N/A, it does not rate it ABSENT).

Ratings are per dimension. A dimension whose sub-checks disagree takes the **weakest** rating any
sub-check earned, and the report names which sub-check set it.

Severity: **INVALIDATING** (a reviewer who finds this can dismiss the result) · **HARDENING**
(weakens credibility without invalidating a number).

## Procedure

### Step 1 — Confirm the target is gradable

Establish the repo is a benchmark, then map where the audit will look:

- `search_files` for `judge|rubric|score|grade|leaderboard|eval` to find scoring.
- `search_files` for `leaderboard|results|latest\.csv|\.parquet` to find where results live.
- `search_files` for `methodology|governance|contamination|pre.?registration` to find stated policy.

If none of these hit, the repo is probably not a benchmark. Say so and stop.

Record for the dimension auditors: absolute repo path, branch and HEAD SHA (`git rev-parse HEAD`
via `terminal`), the scoring entry points, the results directory, and any methodology docs. Also
list open PRs — a finding an in-flight PR already fixes is reported as known, not as a gap, and is
excluded from the counts. Verify the PR against its actual diff, not its title.

### Step 2 — Run the seven dimensions in parallel

Dispatch seven `delegate_task` subagents in a single batch. Each receives the repo path, the HEAD
SHA, the located parts from Step 1, its dimension's brief from
[`references/dimension-briefs.md`](references/dimension-briefs.md), and the report contract below,
capped at ~400 words. Each brief carries that dimension's sub-checks, its search vocabulary, and its
own severity rule — several are conditional and do not reduce to the global heuristic in Step 4.

On a small target — one scoring file, no CI, no leaderboard — running the dimensions inline is
cheaper than seven subagents and loses nothing.

If `delegate_task` is unavailable, run the dimensions inline one after another in the same order,
with the same evidence bar. Note in the report that the audit ran sequentially. Do not thin it.

### Step 3 — Hold every rating to the evidence bar

A rating with no `file:line` — or no explicit "searched X, Y, Z, found nothing" — is a guess.
Reject it and send the dimension back.

**A search miss alone does not establish ABSENT.** The briefs in `references/dimension-briefs.md`
carry one repo's vocabulary; the
target may name the same concept differently. Search by concept — read the scoring entry points,
the CI workflows, the docs — before rating any sub-check ABSENT.

### Step 4 — Assign severity by consequence, not effort

Ask: *can a critic use this gap to throw out the headline number?* If yes, INVALIDATING.

INVALIDATING looks like: no author-is-contestant guard; judge not pinned to the served model;
holdout content reachable in CI artifacts; no confidence intervals on a ranking built from few
scenarios; null-agent or holdout rows in the public board with no tripwire test.

HARDENING looks like: agreement stats present but not chance-corrected; no resume or cost cap on
expensive runs; environment pinned in prose rather than a lockfile.

### Step 5 — Assemble the report

```
EVAL-INTEGRITY AUDIT — <repo> @ <short-sha> — <date>

VERDICT: <PUBLISH-READY | N INVALIDATING GAP(S) | NOT A BENCHMARK>
Score: <n>/7 PRESENT · <n> PARTIAL · <n> ABSENT · <n> N/A

INVALIDATING GAPS (fix before publishing)
- [<dimension>] <one line>. Evidence: <file:line, or "absent: searched X, Y, Z">. Fix: <concrete change>.

HARDENING GAPS (raise credibility)
- [<dimension>] <one line>. Evidence: <…>. Fix: <…>.

KNOWN / IN-FLIGHT
- [<dimension>] fixed by PR #<n> (verified against diff). Excluded from counts.

PER-DIMENSION
1. Pre-registration    — PRESENT | PARTIAL | ABSENT — <evidence> — <fix>
   … through 7 …

STRENGTHS
- <one line each>
```

Lead with what invalidates. Every gap carries a concrete fix — name the file to add, the guard to
write, the test to add, not "consider improving X". Never propose "add more scenarios" unless low
scenario count is the specific finding.

### Step 6 — Offer fixes, do not apply them

Applying a fix changes the benchmark's methodology. That is the author's call, one gap at a time,
with explicit approval.

## Pitfalls

- **Prose is not enforcement.** A `governance.md` promising a holdout gap with no code computing it
  is PARTIAL, not PRESENT. This is the most common misrating.
- **Vocabulary mismatch produces false ABSENTs.** The target may call pre-registration a "run
  manifest" or contamination control an "authorship guard". Read before concluding.
- **Subagent output is unverified input.** Spot-check the highest-stakes ratings yourself before
  they reach the report.
- **In-flight fixes are not gaps**, but only when verified against the diff. PR titles lie.
- **Auditing a repo you also maintain** invites grading your own homework. The evidence bar exists
  precisely for that case — cite or drop it.

## Verification

```
Use the eval-integrity skill to audit ./some-non-benchmark-repo.
```

Working correctly, it reports `NOT A BENCHMARK` and stops rather than producing seven empty
dimensions. On a real benchmark it returns a verdict line, a count across the three ratings, and at
least one `file:line` citation per dimension.
