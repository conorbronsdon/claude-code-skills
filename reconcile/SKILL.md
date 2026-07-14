---
name: reconcile
description: Tripwire check for multi-session drift. Scans state files, recent commits, and file conflicts caused by parallel Claude Code sessions.
---
<!-- x-source: agent-workspace/SKILL.md @ 7b7211e -->

# /reconcile — Multi-Session Drift Check

When running multiple Claude Code sessions in parallel (especially with worktrees), files can drift out of sync. This skill scans for inconsistencies and proposes fixes.

**Invocation:** deliberately model-invocable — the scan is read-only and auto-triggering when drift smells is the point. Anything that changes files is proposed, never applied.

## When to Use

- After merging worktree branches back to the default branch
- When something "feels off" after parallel work
- After a crash where multiple sessions were open
- As a periodic sanity check during heavy parallel workflows

## Instructions

### 0. Detect the default branch

```bash
git rev-parse --git-dir >/dev/null 2>&1 || { echo "not a git repository — nothing to reconcile"; exit 0; }
DEFAULT=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')
DEFAULT=${DEFAULT:-main}   # no remote configured — fall back and say so in the report
```

### 1. Scan recent commit history across all branches

```bash
git log --all --oneline --since="24 hours ago" --graph
```

Look for:
- Multiple branches touching the same files
- Commits on branches that haven't been merged
- Conflicting changes (same file modified differently on different branches)

### 2. Check for file-level conflicts

For each file modified on multiple branches, diff the versions:

```bash
git diff "$DEFAULT"..<branch> -- <file>
```

Flag files where:
- Both branches modified the same lines (merge conflict risk)
- One branch deleted what another modified
- Timestamps or "Last Updated" fields diverged

### 3. Check state file consistency

If your project uses state files (TODO lists, priority files, decision logs, session logs), check:

- **Duplicate entries**: Same task or decision logged twice from different sessions
- **Contradictory state**: One session marked something complete, another added it as in-progress
- **Timestamp drift**: "Last Updated" dates that don't match the most recent actual edit
- **Orphaned references**: Files or sections referencing things that were removed in another session

### 4. Check for SSOT violations

If your project has single-source-of-truth rules (facts that should only live in one file):

- Scan for duplicated facts across files
- Flag any case where the same information appears in multiple locations with different values
- Check that cross-references point to files that still exist

### 5. Report

```
RECONCILE — [DATE]

BRANCHES CHECKED:
- [branch list with last commit date]

FILE CONFLICTS:
- [file] — modified on [branch1] and [branch2] — [conflict type]

STATE DRIFT:
- [issue description]

SSOT VIOLATIONS:
- [duplicated fact] — found in [file1] and [file2]

PROPOSED FIXES:
1. [fix description]

OVERALL: [CLEAN / N issues found]
```

### 6. Apply fixes (with approval only)

Present each fix individually. Wait for approval before applying. Common fixes:
- Merge the newer version of a conflicting file
- Remove duplicate entries (keep the more detailed one)
- Update timestamps to match actual last-edit dates
- Resolve SSOT violations by keeping the canonical source and updating references

## Design Principles

- **Read-only by default.** Report, wait for approval.
- **Prefer evidence of intent over timestamps.** When two versions conflict, look at which change the surrounding work depends on (commit messages, linked edits, whether other files reference the new value). A stale session can easily produce the *newer* timestamp. Use recency only as a tie-breaker when intent is unreadable.
- **Preserve intent.** Don't auto-resolve — different sessions may have had different goals.
- **Fast.** Git commands and file reads only. Under 30 seconds for a full scan.
