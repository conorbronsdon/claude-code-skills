# eval-integrity

Audit an LLM evaluation or benchmark repo for the integrity practices that make a published score mean what it appears to mean. Run with `/eval-integrity` pointed at a benchmark repo. It greps the repo for evidence across seven dimensions, spawns one auditor subagent per dimension in parallel, and emits a scored report: per-dimension PRESENT / PARTIAL / ABSENT, with `file:line` evidence, a severity tag, and a concrete fix for every gap.

The seven dimensions:

1. **Pre-registration** — corpus hash, judge panel, seeds, and temps fixed on disk before results exist, so runs can't be cherry-picked.
2. **Contamination** — corpus authors (and their model family) barred as contestants; per-scenario authorship recorded; private holdout with a published public-vs-holdout gap.
3. **Holdout hygiene** — no holdout leak via CI logs, workflow artifacts, committed transcripts, or error messages.
4. **Judge validity** — judge pinned to the model actually served; chance-corrected multi-judge agreement; same-lab, length-bias, and halo controls.
5. **Statistical honesty** — confidence intervals on headline numbers; micro vs macro stated; pass@k vs pass^k disambiguated; seeds fixed; multiple-comparison risk acknowledged.
6. **Reproducibility** — deterministic re-run path, cost caps / resume for expensive runs, pinned environment.
7. **Leaderboard exclusions** — null-agent baselines, holdout rows, and non-default configs kept out of public aggregates, enforced by tripwire tests rather than intent.

Each gap is rated **INVALIDATING** (a reviewer can throw out the published number) or **HARDENING** (weakens credibility, doesn't invalidate). The report leads with the invalidating gaps.

Auditing is read-only. The skill never edits the benchmark, re-runs an eval, or touches a leaderboard. It offers fixes; applying them is the author's call.

The checks were extracted from hardening a real agent benchmark, [cot-bench](https://github.com/conorbronsdon/cot-bench), for external grant review. cot-bench file names appear in the dimension briefs as examples of what good looks like, not as paths the skill expects to find in your repo.

## Setup

Copy the skill into your project and add a command routing file:

```bash
cp -r eval-integrity/ your-project/skills/eval-integrity/

cat > your-project/.claude/commands/eval-integrity.md << 'EOF'
---
name: eval-integrity
description: Audit an LLM eval/benchmark repo for integrity and credibility practices
---

Load and follow the instructions in `skills/eval-integrity/SKILL.md`.
EOF
```

Then run `/eval-integrity` from (or pointed at) a benchmark repo.

See [SKILL.md](SKILL.md) for the full audit workflow and [patterns/dimension-prompts.md](patterns/dimension-prompts.md) for the paste-ready per-dimension audit briefs.
