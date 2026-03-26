---
name: session-management
description: Structured session lifecycle for Claude Code — start, checkpoint, end, and daily heartbeat commands that maintain project state across conversations.
---

# Session Management for Claude Code

A system of four commands that give Claude Code a memory across sessions. Instead of starting every conversation cold, these skills maintain state files that capture what you're working on, what decisions you've made, and what's next.

## Why This Exists

Claude Code conversations are ephemeral — close the terminal and the context is gone. These skills solve that by:
- **`/start`** loads your project state so Claude knows where you left off
- **`/update`** saves progress mid-session without closing
- **`/end`** captures everything from the session before you close
- **`/today`** runs a morning check-in that catches staleness, surfaces deadlines, and proposes memory updates

The system compounds over time. Session logs become an episodic record. State files stay fresh. Decisions are logged. Nothing falls through the cracks.

## Setup

### Required file structure

Create these files in your project root (or wherever makes sense for your workflow):

```
state/
  current.md          # Active priorities, open threads, recent context
  decisions.md        # Decision log (date, decision, rationale)
  weekly-priorities.md # What matters this week
  blockers.md         # Things waiting on external dependencies
  heartbeat-log.md    # Record of /today check-ins (auto-created)
sessions/
  {YYYY-MM-DD}.md     # Daily session logs (auto-created)
```

### Minimal `state/current.md` to start

```markdown
# Current State

Last updated: [date]

## Active Priorities
1. [Your top priority]
2. [Second priority]

## Active Context
- [Open thread or thing you're working on] *(created M/D)*

## Recently Completed
- [Last thing you finished] *(M/D)*
```

### Minimal `state/decisions.md` to start

```markdown
# Decision Log

Key decisions with date, context, and rationale.

| Date | Decision | Context / Rationale |
|------|----------|---------------------|
```

### Add to your CLAUDE.md

```markdown
## Session Management
| Command | What it does |
|---------|-------------|
| `/start` | Load state, check what changed, give a briefing |
| `/end` | Log the session, update state, check for uncommitted work |
| `/update` | Mid-session checkpoint (quick save) |
| `/today` | Morning heartbeat — staleness check, deadlines, memory curation |
```

---

## /start — Begin Session

### Instructions

1. **Get today's date.** Run `date +%Y-%m-%d`. Note the day of week.

2. **Check what changed since last session.** Find the most recent session log and run:
   ```bash
   git log --oneline --since="<last session date>"
   ```
   Flag any state or context files modified since last session — these may contain updates from other sessions or manual edits.

3. **Load context (read in order):**
   - `state/current.md` — active priorities, open threads
   - `state/decisions.md` — scan last 5 entries for awareness
   - `state/weekly-priorities.md` — what matters this week
   - `state/blockers.md` — things waiting on dependencies
   - `sessions/{TODAY}.md` — if it exists, you're resuming today

4. **Check state freshness.** Flag files that haven't been updated recently:
   - `current.md` >3 days stale — flag it
   - `weekly-priorities.md` >5 days — flag it
   - `blockers.md` >7 days — flag it

5. **Give a briefing.** Keep it short:
   - Date and day of week
   - State freshness (one line if all fresh, individual flags if stale)
   - Files changed since last session
   - Top 2-3 priorities from current.md
   - Any time-sensitive open threads
   - Any blockers worth flagging
   - Ask: "What's the focus today?"

   If resuming today's session, acknowledge what was already covered.

---

## /update — Quick Checkpoint

### Instructions

1. **Scan recent conversation.** Identify in 30 seconds: what was worked on, any decisions made, any state changes needed.

2. **Append to session log.** Add to `sessions/{TODAY}.md`:
   ```markdown
   ## Update: {TIME}
   - {what was worked on, 1-3 bullets max}
   ```

3. **Update state if something changed.** Only touch `current.md` if a priority shifted, a thread opened/closed, or a task completed. Skip otherwise.

4. **Confirm.** One line: "Checkpointed: {brief description}"

---

## /end — Close Session

### Instructions

1. **Auto-extract session summary.** Scan the full conversation and extract:
   - **Topics covered** — what was worked on
   - **Decisions made** — anything concluded or chosen, with rationale
   - **State changes** — priorities that shifted, threads that opened or closed
   - **Open threads** — unfinished items or things waiting on someone
   - **Next actions** — what needs to happen next session

   Present the summary for quick confirmation before writing.

2. **Write session log.** Append to `sessions/{TODAY}.md`:
   ```markdown
   ## Session: {TIME}

   ### Topics
   - {topic}

   ### Decisions
   - {decision}

   ### Open Threads
   - {thread}

   ### Next Actions
   - {action}
   ```

3. **Update state files:**
   - **Always update `current.md`**: Add new threads, remove completed items, update timestamps on touched items. Update "Last Updated" date.
   - **Update `blockers.md` if needed**: Add new dependencies, move resolved blockers to "Recently Unblocked."
   - **Update `weekly-priorities.md` if needed**: Check off completed items. Only touch if meaningful progress was made.

4. **Update decision log.** If decisions were made, append to `decisions.md`:
   ```markdown
   | {TODAY} | {decision} | {context / rationale} |
   ```
   Only log decisions that future sessions need to know about.

5. **Git safety check (do not skip).** Run `git status` and check for uncommitted or unpushed work:
   - Uncommitted changes? Show the files and ask whether to commit.
   - Unpushed commits? Show the count and ask whether to push.
   - Clean and pushed? Skip silently.

6. **Confirm.** Two-line summary: what was logged, and the top open thread or next action.

---

## /today — Morning Heartbeat

A daily check-in that catches staleness, surfaces deadlines, and proposes updates. Designed to run in under 60 seconds.

### Instructions

1. **Establish context.** Get today's date. Read the heartbeat log (`state/heartbeat-log.md`) to find the last check-in date.

2. **Scan recent activity.** Run:
   ```bash
   git log --oneline --since="3 days ago"
   ```
   Check `sessions/` for recent logs. This captures work even from sessions that closed without `/end`.

3. **Check state freshness.** Same thresholds as `/start` step 4.

4. **Surface deadlines.** Read `TODO.md` or your task file and scan for:
   - Items with dates in the next 7 days
   - Items marked urgent or time-sensitive

5. **Age-check open items.** Read `current.md` and check dates on open threads:
   - Items >7 days old: flag as "stale — still relevant?"
   - Items >14 days old: escalate as "likely stale — remove or convert to task?"
   Present proposals. **Do not auto-update.**

6. **Identify memory gaps.** Compare git log activity against state files:
   - Decisions committed but not in `decisions.md`?
   - Completed work not reflected in `current.md`?
   List proposed updates. **Do not auto-update. Wait for approval.**

7. **Output format:**
   ```
   MORNING CHECK-IN — [DATE] ([day of week])
   Last heartbeat: [date] ([N] days ago)

   SINCE LAST CHECK-IN:
   - [N] commits: [brief themes]
   - Session logs: [found/none]

   STATE:
   - current.md — [fresh/N days stale]
   - weekly-priorities.md — [fresh/N days stale]
   - blockers.md — [fresh/N days stale]

   DEADLINES (next 7 days):
   - [items, most urgent first]

   [If stale items found:]
   STALE ITEMS:
   - [item] — [N] days old. [Propose: remove / convert to task]

   [If memory gaps found:]
   MEMORY GAPS:
   - [proposed update]
   ```

8. **Log the heartbeat.** Append to `state/heartbeat-log.md`:
   ```markdown
   ## [DATE]
   - Commits since last: [N]
   - State staleness: [summary]
   - Deadlines flagged: [count]
   - Stale items flagged: [count]
   - Memory gaps found: [count]
   - Updates applied: [list or "none — awaiting response"]
   ```

9. **Transition.** Ask: "What's the focus today?"

## Design Principles

- **Fast.** Under 60 seconds. If it's slow, it won't get used.
- **Propose, don't act.** State updates from `/end` are presented for confirmation. Memory updates from `/today` require explicit approval. Never silently edit state files during heartbeat.
- **Skip what's clean.** If everything is fresh and no deadlines are near, say so in one line.
- **Compound over time.** Session logs and heartbeat logs become an episodic record. Over weeks, they show patterns.
- **Graceful degradation.** If state files don't exist yet, create them. If a session closes without `/end`, `/today` catches the gaps. Nothing is catastrophic.
