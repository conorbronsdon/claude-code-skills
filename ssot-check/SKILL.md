---
name: ssot-check
description: Single-source-of-truth drift auditor for documentation-heavy repos. Finds facts hand-copied across files, builds a manifest of canonical locations, and verifies every copy still matches.
---

# /ssot-check — Fact-Copy Drift Auditor

Documentation-heavy repos repeat facts. An episode count lives in a README, then gets hand-copied into a media kit, a landing page, and a business plan. Someone updates the README. The copies drift. This skill finds those copies, records where the canonical value lives, and checks the copies against it on every run.

It complements `/reconcile`. Reconcile catches multi-session drift in state files. This skill catches fact-copy drift across documents: the same number or string living in several files, where exactly one file is allowed to be right.

## When to Use

- **Discover mode**: first run on a repo, or after adding a new doc surface (a media kit, a landing page, a pricing page)
- **Check mode**: before commits that touch docs, as a pre-commit habit, or any time a canonical number changed
- After a bulk find-and-replace, to confirm nothing was missed
- When a repo has a "grep for other files with the same number" rule that people forget to follow

## The Manifest: `.ssot.yaml`

A single YAML file at the repo root. It maps each fact to one canonical location and a list of known copies. Patterns are regexes with exactly one capture group, so values can be extracted and compared.

```yaml
# .ssot.yaml — single-source-of-truth manifest
# Each fact has ONE canonical location. Everything else is a copy.
# Patterns are regexes with exactly one capture group around the value.
facts:
  - name: episode-count
    note: Total published episodes. Canonical is the episode index.
    canonical:
      file: outputs/episodes/README.md
      pattern: 'Total Episodes:\s*\*?\*?(\d+)'
    copies:
      - file: sponsorship/media-kit.md
        pattern: '(\d+) published episodes'
      - file: ../cot-sponsor-page/index.html   # cross-repo copy, see below
        pattern: '<span class="stat-episodes">(\d+)</span>'

  - name: sponsor-price-single
    note: Single-episode sponsorship price.
    canonical:
      file: sponsorship/pricing.md
      pattern: 'Single episode:\s*\$([\d,]+)'
    copies:
      - file: ../cot-sponsor-page/index.html
        pattern: 'data-price-single="\$?([\d,]+)"'

  - name: newsletter-subscribers
    note: Substack subscriber count, updated monthly.
    canonical:
      file: analytics/goals.md
      pattern: 'Substack subscribers:\s*([\d,]+)'
    copies:
      - file: sponsorship/media-kit.md
        pattern: '([\d,]+) newsletter subscribers'
      - file: business-plan.md
        pattern: '([\d,]+) Substack subscribers'
```

Schema rules:

- `name`: short kebab-case identifier for the fact
- `canonical.file` + `canonical.pattern`: where the true value lives and how to extract it
- `copies[]`: every other place the value is written out, same `{file, pattern}` shape
- `note` (optional): what the fact is, update cadence, formatting conventions
- Exactly one capture group per pattern. The check compares captured strings, not whole lines.
- Comparison strips surrounding whitespace and thousands separators (`1,234` matches `1234`). Everything else must match exactly.

### Cross-repo copies

A copy may live in a sibling local clone (marketing pages often do). Use a relative path that escapes the repo root, like `../cot-sponsor-page/index.html`. Two rules:

1. **Pull the sibling fresh before checking.** Run `git -C ../cot-sponsor-page pull --rebase` first, or you are checking a stale copy. If the sibling has uncommitted changes or the pull fails, report that fact's status as UNVERIFIED rather than guessing.
2. **Fixes to a sibling repo are a separate commit.** Propose the edit, but note it lands in the other repo with its own commit and deploy path.

## Discover Mode (first run)

Goal: scan the repo for drift-prone facts and propose a `.ssot.yaml`. The human edits and approves it. Never write the manifest without approval.

### Instructions

1. **Confirm there is no `.ssot.yaml` yet.** If one exists, ask whether to extend it (discover new facts and append) or just run check mode.

2. **Scan for candidate facts.** Search markdown, HTML, and plain-text prose files. Skip code, lockfiles, vendored dirs, and generated files (anything marked auto-generated, or written by a script per the repo's CLAUDE.md). For a large repo, spawn a subagent with `patterns/discovery-prompt.md` so the grep noise stays out of the main thread. Heuristics, in priority order:
   - The same distinctive number in 2+ prose files. Distinctive means: 2+ digits with a unit noun nearby (episodes, subscribers, downloads, users, stars), any dollar amount, any percentage, any version string (`v1.2.3`, `2.4.x`), date ranges.
   - Sentences containing "as of", "currently", "total", "more than", "over N". These phrases mark facts that age.
   - Stat-bearing proper-noun phrases ("61 episodes", "11K subscribers", "40% of downloads").
   - Numbers that appear in multiple files **with different values** are the highest-priority candidates: that is live drift, found before the manifest even exists.

3. **Group matches into facts.** Cluster occurrences that describe the same real-world quantity, even when formatted differently (`1,234` vs `1234`, `$5,000` vs `$5000`). Discard noise: bare years, dates that are just timestamps, version numbers of dependencies, anything appearing in only one file.

4. **Propose a canonical for each fact.** Prefer, in order: a file the repo's CLAUDE.md already names as source of truth, a data or analytics file, an index README. Marketing copies (media kits, landing pages) are almost never canonical. Mark each proposal with one line of reasoning. The human confirms or reassigns.

5. **Present the draft manifest** plus any live drift found during the scan:

   ```
   SSOT DISCOVER — [DATE]

   PROPOSED FACTS (N):
   - episode-count: 61 — canonical guess: outputs/episodes/README.md (CLAUDE.md names it SSOT)
     copies: sponsorship/media-kit.md, ../cot-sponsor-page/index.html
   - [fact]: [value] — canonical guess: [file] ([reasoning])

   LIVE DRIFT FOUND:
   - newsletter-subscribers: analytics/goals.md says 1,240 but business-plan.md says 1,100

   DISCARDED (low confidence): [count, one-line summary]

   Draft .ssot.yaml below. Edit canonical assignments, then approve to write.
   ```

6. **Write `.ssot.yaml` only after explicit approval.** Then offer to run check mode immediately to fix the live drift.

## Check Mode (every subsequent run)

Goal: verify every copy still matches its canonical value. Main-thread, fast, read-only. Propose fixes, never auto-apply.

### Instructions

1. **Read `.ssot.yaml`.** If it does not exist, switch to discover mode.

2. **Pull fresh any sibling repos** referenced by cross-repo copy paths (see rules above).

3. **For each fact:**
   - Open the canonical file, apply the canonical pattern, extract the captured value.
   - Pattern does not match, or the file is missing: status **CANONICAL MOVED**. The manifest is stale. Propose an updated pattern or file path if the value is findable nearby.
   - For each copy, apply its pattern and compare captured values (whitespace-trimmed, thousands separators stripped).
     - Match: **IN SYNC**
     - Mismatch: **DRIFTED**. Record canonical value, copy value, and `file:line` of the copy.
     - Copy pattern does not match at all: **STALE ENTRY**. The copy was reworded or removed. Propose a manifest update.

4. **Report:**

   ```
   SSOT CHECK — [DATE]

   IN SYNC (6): episode-count, sponsor-price-single, ...

   DRIFTED (1):
   - newsletter-subscribers — canonical says 1,240, copy says 1,100
     canonical: analytics/goals.md:14
     copy:      business-plan.md:52 ("over 1,100 Substack subscribers")
     proposed edit:
       - over 1,100 Substack subscribers
       + over 1,240 Substack subscribers

   CANONICAL MOVED (1):
   - sponsor-price-single — pattern no longer matches sponsorship/pricing.md
     nearest match: "Single episode rate: $1,500" at line 9
     proposed manifest fix: pattern: 'Single episode rate:\s*\$([\d,]+)'

   8 facts checked, 1 drifted, 1 stale manifest entry.
   ```

   The last line is the exit summary. Always emit it, even when everything is clean ("8 facts checked, all in sync").

5. **Apply fixes only after approval, one fact at a time.** Show the exact diff for each edit. Drifted copies get content edits. CANONICAL MOVED and STALE ENTRY get manifest edits. Cross-repo edits are flagged as landing in the sibling repo.

## Edge Cases

- **Intentional rounding.** If a copy deliberately rounds ("11K subscribers" vs a canonical 11,432), exact comparison will flag it every run. Either standardize the copy to the exact value, or remove that copy from the manifest and record the rounding rule in the fact's `note`. Do not add fuzzy matching; a check that sometimes shrugs is worse than no check.
- **Auto-generated copies.** If a script already writes some copies (a metrics pipeline updating a README line), list them in the manifest anyway with a `note: auto-generated by X`. The check then doubles as a pipeline health check, but fix proposals should point at the script, not the file.
- **Multiple matches for one pattern.** If a pattern matches more than once in a file, use the first match and warn. Tighten the pattern if the warning recurs.
- **Facts that legitimately differ per file.** A "subscribers" number quoted at different dates in different docs is not one fact. Do not force it into the manifest; drift checking only works for facts that should be identical everywhere.

## Design Principles

- **One canonical, everything else is a copy.** The manifest encodes that decision so no one has to remember it.
- **Propose, never auto-apply.** Report drift with exact diffs and wait for approval. Same contract as `/reconcile` and `/recover`.
- **Greppable manifest.** Plain YAML, plain regexes. A human can verify any entry with one grep.
- **Fast enough for a pre-commit habit.** Check mode is file reads and regex matches. Seconds, not minutes.
- **Exact match or flagged.** No fuzzy comparison. Ambiguity gets surfaced to the human, not resolved silently.
