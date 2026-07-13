---
name: recover
description: Scan for orphaned worktrees and stale branches after crashes or abandoned sessions. Offers safe cleanup options.
---

# /recover — Worktree & Branch Cleanup

Scan for orphaned worktrees, stale branches, and partial work left behind by crashed or abandoned Claude Code sessions. Read-only by default — reports findings and waits for approval before cleanup.

**Invocation:** deliberately model-invocable — scanning is read-only. Every cleanup action is gated on explicit user approval.

## When to Use

- After a system crash or forced session termination
- When parallel session hooks warn about stale processes
- When you find commits on unknown branches
- Periodic hygiene (monthly or after heavy parallel work)

## Instructions

### 0. Detect the default branch

Don't assume `main`. Resolve it once and use it everywhere below:

```bash
DEFAULT=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')
DEFAULT=${DEFAULT:-$(git remote show origin 2>/dev/null | sed -n 's/.*HEAD branch: //p')}
DEFAULT=${DEFAULT:-main}   # no remote at all — fall back and note it in the report
```

### 1. List all worktrees

```bash
git worktree list --porcelain
```

Identify:
- **Recently touched worktrees**: files or `.git` metadata modified in the last hours — treat as *possibly live*. `git worktree list` cannot tell whether a session is actually running; without a lock/heartbeat file or process evidence, classify as **unknown activity** and never as orphaned.
- **Candidate-orphaned worktrees**: no recent modification and no activity signal — proceed to inspection, still gated on user approval before any cleanup
- **Stale entries**: Git tracks a worktree but the directory is gone

### 2. Inspect orphaned worktrees

For each orphaned worktree:

```bash
git -C <worktree-path> status --short
git -C <worktree-path> branch --show-current
git -C <worktree-path> log --oneline -3
git log "$DEFAULT"..<branch-name> --oneline
```

Classify each as:
- **CLEAN**: No unmerged commits, no uncommitted changes — safe to remove
- **HAS COMMITS**: Unmerged commits exist — needs merge decision
- **HAS CHANGES**: Uncommitted work — needs save decision
- **BOTH**: Unmerged commits AND uncommitted changes — needs careful handling

### 3. List stale branches

```bash
git branch --no-merged "$DEFAULT"
git remote prune origin --dry-run
git for-each-ref --sort=-committerdate --format='%(refname:short) %(committerdate:relative) %(subject)' refs/heads/
```

Classify:
- **MERGED**: Already in the default branch — safe to delete
- **STALE**: Last commit >7 days ago, not merged — flag for review
- **ACTIVE**: Recent commits — leave alone

### 4. Check for prunable git state

```bash
git worktree prune --dry-run
```

### 5. Report

```
RECOVER — [DATE]

WORKTREES:
- Active: [N]
- Orphaned: [N]
  - [path] — [status] — [branch] — [last commit]
- Stale entries: [N]

BRANCHES:
- Merged (safe to delete): [list]
- Stale (>7 days, not merged): [list]
- Active: [list]

PROPOSED ACTIONS:
1. [action] — [target] — [reason]

OVERALL: [CLEAN / N items need attention]
```

### 6. Cleanup (with approval only)

**Only proceed when explicitly approved.** Options:
- Remove orphaned worktree (CLEAN): `git worktree remove <path>`
- Merge unmerged commits: `git merge <branch> --no-ff`
- Cherry-pick specific commits: `git cherry-pick <hash>`
- Delete merged branches: `git branch -d <branch>`
- Delete stale branches (confirmed discard): `git branch -D <branch>`
- Prune stale entries: `git worktree prune`
- Prune remote refs: `git remote prune origin`

## Design Principles

- **Read-only by default.** Report, wait for approval.
- **Preserve work.** Default to merge/cherry-pick over discard.
- **Specific.** Show exact commit hashes, file lists, branch names.
- **Fast.** Git commands only. Under 15 seconds for scan.
