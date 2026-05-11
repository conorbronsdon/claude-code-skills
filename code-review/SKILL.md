---
name: code-review
description: Multi-agent deep review for code PRs in any repo. Use when asked to "deep review this PR," "multi-agent review," "review #N with subagents," "thorough review of this branch," or "is this PR ready to merge." Orchestrates Copilot + parallel subagents (adversarial, operational, reference-comparison) with scope-based escalation, stale-finding triage, and a hard iteration cap.
---

# Code Review — Multi-Agent PR Review

User-invokable orchestrator for code-PR review across any repo. Validated on a Vercel-deployed Next.js app PR across 5 review rounds: Copilot caught ~10 line-level issues; parallel subagents caught the P0 architectural miss (Vercel `maxDuration`) Copilot missed across all 5 rounds, plus a persistent-replay vector and 4 operational issues.

If you have access to a paid multi-agent review service (e.g. `/ultrareview` in Claude Code), this skill is the in-flight free version of the same idea — useful when you want this depth without spinning up a billed cloud review.

---

## Step 1: Assess PR Scope

```bash
gh pr view N --json files,additions,deletions,title
```

Categorize:

| Tier | Examples | Treatment |
|---|---|---|
| **Trivial** | Typo, copy edit, single-line deps bump, README polish | Skip multi-agent. Copilot alone is enough. |
| **Standard** | Component refactor, single-feature bug fix, contained logic change | Copilot + 1 subagent (pick the angle that matches the risk shape) |
| **High-stakes** | Payment, auth, crypto/wallet, RPC, deployment configs, scale-relevant changes, new external SDK integrations | Copilot + 2 parallel subagents minimum (always include adversarial + operational) |

If trivial → stop reading this skill, just request Copilot review and ship.

---

## Step 2: Spawn Subagents in Parallel

Three angles that empirically work. Pick by risk shape:

- **Adversarial** — "Try to break it. What's the worst attack?" Finds security holes, abuse vectors, replay/race conditions, malformed-input handling.
- **Operational** — "What fails in production at scale? Latency, cost, observability, timeouts, env config, retries, cold-start?" Finds the architectural P0s Copilot misses (Vercel `maxDuration` was the canonical one).
- **Reference-comparison** — "Does this match the upstream reference impl exactly? Where does it diverge and why?" Use for third-party SDK / spec integration (Phantom deep-link, Stripe, OAuth providers, RPC clients).

Spawn all chosen subagents in **a single tool-call batch** so they run in parallel. Prompt templates live in `patterns/subagent-prompts.md`.

Every subagent prompt must specify:
1. Repo path (absolute) + branch + commit hash at HEAD
2. Files to focus on (paste the changed-files list from Step 1)
3. Confidence rating + critical findings first
4. Cap report length at ~500 words

---

## Step 3: Request Copilot Review (in parallel with subagents)

```bash
gh pr edit N --add-reviewer copilot-pull-request-reviewer
```

Don't wait for Copilot to start before spawning subagents. They run in parallel.

---

## Step 4: Triage Findings

Three buckets:

**Real findings** — fix now. Push fix to the PR branch.

**Stale re-flags** — Copilot will sometimes re-flag findings against unmoved diff lines after fixes ship at HEAD. **Always read the file at HEAD before re-fixing.** If the fix is already there, drop a one-line reply on the comment ("Fixed at <sha>") and move on. Do not re-fix.

**Deferred (filed)** — tests, refactors, or work outside scope. File as a GitHub issue, link the issue number in the merge commit message, move on. Don't expand the PR.

---

## Step 5: Iteration Cap

**Maximum 2 Copilot review rounds.** Empirically, by round 3 the signal-to-noise ratio collapses (~50% stale re-flags). Ship after round 2. If subagents flag genuinely new issues after round 2, those are issue-tracker items, not PR-blockers.

---

## Step 6: When NOT to Use This Skill

- **Already-merged PRs** → use Claude Code's built-in `/security-review` if you suspect a problem.
- **Trivial-tier PRs** (per Step 1) → just request Copilot, skip the multi-agent overhead.
- **PRs where a paid multi-agent service was already run** → don't double-spend.
- **Skill / prompt / instruction-file repos** (where the "code" is markdown) → multi-agent is overkill; a single review pass against the trigger-quality and instruction-quality dimensions is enough.

---

## Empirical Evidence

Validation case (5 rounds on a high-stakes PR):

- **Copilot caught ~10 real line-level issues** (null checks, error handling, type mismatches).
- **Subagents caught what Copilot missed across all 5 rounds:**
  - **P0:** Vercel `maxDuration` not set — function would time out under realistic load. Architectural miss invisible at the line level.
  - **Persistent-replay vector** in the auth flow.
  - **Transient poll tolerance** (no retry budget on flaky upstream).
  - **Env-configurable timeout** (hardcoded value).
  - **Structured logging** (string-concat logs, unparseable in production).
  - **`bodyParser` size limit** (DoS surface).
- **Round 3+ pattern:** Copilot re-flagged the same already-fixed lines. Confirmed the round-2 cap.

Subagents are not redundant with Copilot. They cover a different layer.

---

## Cross-references

- `patterns/subagent-prompts.md` — paste-ready prompt templates for the three angles.
