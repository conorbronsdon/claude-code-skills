---
name: ssot-check
description: Single-source-of-truth drift auditor for documentation-heavy repos. Use when asked to "check for drift," "find copies of this number," "audit the docs for stale facts," or "set up an SSOT manifest." Finds facts hand-copied across files, builds a manifest of canonical locations, and verifies every copy still matches.
argument-hint: "[discover|check]"
---
<!-- Standalone prose skill. It shares a name and a problem statement with the
     tool-backed https://github.com/conorbronsdon/ssot-check, but it is not a
     synced copy of that repo's SKILL.md and does not track a commit there. -->

# /ssot-check — Fact-Copy Drift Auditor

Documentation-heavy repos repeat facts. An episode count lives in a README, then gets hand-copied into a media kit, a landing page, and a business plan. Someone updates the README. The copies drift. This skill finds those copies, records where the canonical value lives, and checks the copies against it on every run.

It complements `/reconcile`. Reconcile catches multi-session drift in state files. This skill catches fact-copy drift across documents: the same number or string living in several files, where exactly one file is allowed to be right.

**Invocation:** deliberately model-invocable — it belongs in pre-commit moments. No file is ever edited: fixes are proposed as diffs, never auto-applied. No repo being audited is ever modified — no pull, no rebase, no checkout, no commit, in this repo or a sibling.

Exactly one operation writes anything at all, and it is worth stating plainly rather than burying: `git fetch` in a sibling clone, which updates that clone's remote-tracking refs and `FETCH_HEAD` so a value can be compared against a live remote. It touches no working tree and no file. It is **off by default** and runs only on an explicit request from the user in that session. Absent that request, freshness comes from refs already on disk, or the fact is reported UNVERIFIED.

## When to Use

- **Discover mode**: first run on a repo, or after adding a new doc surface (a media kit, a landing page, a pricing page)
- **Check mode**: before commits that touch docs, as a pre-commit habit, or any time a canonical number changed
- After a bulk find-and-replace, to confirm nothing was missed
- When a repo has a "grep for other files with the same number" rule that people forget to follow

## When NOT to Use

- A repo with no duplicated facts — one source of record per value, nothing hand-copied. There is nothing to drift.
- Values that legitimately differ per file (dated snapshot series, goal targets vs. current numbers, historical records). Those are not copies; tracking them produces false positives. See Edge Cases.
- Multi-session state drift in working files. That is `/reconcile`'s job, not this skill's.

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

A full manifest produced by a real discover run (with the drift it found) is in [`examples/cot-production-discovery/`](examples/cot-production-discovery/).

Schema rules:

- `name`: short kebab-case identifier for the fact
- `canonical.file` + `canonical.pattern`: where the true value lives and how to extract it
- `copies[]`: every other place the value is written out, same `{file, pattern}` shape
- `note` (optional): what the fact is, update cadence, formatting conventions — and **counting conventions** (e.g. "excludes trailer", "downloads + views, not streams"). Real drift is often a convention mismatch between two correct-looking numbers, and the note is what lets the checker spot it.
- `rounding` (optional, per copy): a named deterministic transform applied to the canonical value before exact comparison, for copies a script intentionally rounds. Allowed: `floor-10`, `floor-100`, `floor-1000` (floor to that multiple), `floor-1000-as-K` (floor to thousands, compare against a value written as `NNNK`). This is not fuzzy matching — the transform is exact, so a mismatch still means something is wrong (usually sync lag).
- Exactly one capture group per pattern. The check compares captured strings, not whole lines.
- Patterns match against the whole file content, not line by line. HTML often puts the value and its label on different lines (`<span class="number">1,000+</span>` / `<span class="label">Newsletter subscribers</span>`); anchor on the nearest stable attribute or literal (an `href`, a `data-*` attribute, the label text) and let `\s*` cross the line break.
- The same file may appear in `copies[]` more than once with different patterns. Same-file copies are real: a landing page's stat block, meta description, and JSON-LD blob each carry the number separately and drift from each other.
- Comparison strips surrounding whitespace and thousands separators (`1,234` matches `1234`), and a trailing `+` on the copy (`62+` matches `62`). Everything else must match exactly.
- Use forward slashes in `file` paths, on every platform. Regexes go in single-quoted YAML strings so backslashes survive (`'\*\*Total Episodes:\*\* (\d+)'`).

### Cross-repo copies

A copy — or the canonical itself — may live in a sibling local clone (marketing pages often do). Use a relative path that escapes the repo root, like `../cot-sponsor-page/index.html`. Three rules:

1. **Never mutate the sibling to check it.** Read its working tree as-is. When freshness matters, compare against the remote-tracking ref the sibling *already has on disk*. Resolve that ref before using it — do not assume `origin/HEAD` exists, because it is set by `git clone` but not by `git remote add` + `git fetch`:

   ```bash
   S=../cot-sponsor-page
   REF=$(git -C $S rev-parse --abbrev-ref '@{upstream}' 2>/dev/null) \
     || REF=$(git -C $S for-each-ref --format='%(refname:short)' refs/remotes | head -1)
   # No REF at all? The sibling has no remote-tracking ref. Report UNVERIFIED.
   git -C $S show "$REF:index.html"          # the value
   git -C $S log -1 --format=%cs "$REF"      # its as-of date
   ```

   Every command above reads local refs and makes no network call. Quote the as-of date next to the value: a remote-tracking ref is a local mirror and can lag the real remote, and a value whose as-of date you can't state is not a fresh value. Report divergence between the sibling's working tree and that ref as a finding.

   Do **not** fetch, pull, rebase, checkout, or commit in a repo you are only auditing. `git fetch` is not exempt: it writes the sibling's remote-tracking refs, `FETCH_HEAD`, and packfiles, and makes an unsolicited network call on the user's behalf. `git pull` additionally moves the sibling's working tree, which can clobber uncommitted work. If you cannot establish a value read-only — no remote-tracking ref on disk, or the file is absent from it — report the fact as **UNVERIFIED** rather than guessing or fetching.

   Run `git fetch` in a sibling only when the user explicitly asks for a live-remote comparison in that session. Name the repo you are about to fetch before running it, and treat the request as covering that session only.

2. **Fixes to a sibling repo are a separate commit.** Propose the edit, but note it lands in the other repo with its own commit and deploy path.
3. **A cross-repo canonical is legitimate.** When the audited repo's own docs delegate a surface to the sibling ("the media kit we send sponsors is the live page"), the sibling file is the canonical and the audited repo holds the copies. The freshness rule applies doubly: a stale canonical poisons every comparison for that fact. If you cannot establish the sibling canonical's value read-only, mark the whole fact **UNVERIFIED** — do not compare its copies against a canonical you are unsure of, because every copy will then be reported wrongly in one direction or the other.

**Mode selection:** if $ARGUMENTS is `discover` or `check`, run that mode. Otherwise auto-detect: `.ssot.yaml` present → check mode, absent → discover mode.

## Discover Mode (first run)

Goal: scan the repo for drift-prone facts and propose a `.ssot.yaml`. The human edits and approves it. Never write the manifest without approval.

### Instructions

1. **Confirm there is no `.ssot.yaml` yet.** If one exists, ask whether to extend it (discover new facts and append) or just run check mode.

2. **Scan for candidate facts.** Search markdown, HTML, and plain-text prose files. Skip code, lockfiles, and vendored dirs. Do NOT skip generated data files (a `data.json` a metrics script writes, a README line a pipeline updates) — scan them and mark them as auto-generated, because they are usually the freshest value and the best canonical for auto-pipelined facts. The thing being generated does not exempt it from drifting: a script can write an internally inconsistent value (one counting convention to one file, another to a second), and only a scan that includes both surfaces catches it. For a large repo, spawn a subagent with `patterns/discovery-prompt.md` so the grep noise stays out of the main thread. Heuristics, in priority order:
   - The same distinctive number in 2+ prose files. Distinctive means: 2+ digits with a unit noun nearby (episodes, subscribers, downloads, users, stars), any dollar amount, any percentage, any version string (`v1.2.3`, `2.4.x`), date ranges.
   - Sentences containing "as of", "currently", "total", "more than", "over N". These phrases mark facts that age.
   - Stat-bearing proper-noun phrases ("61 episodes", "11K subscribers", "40% of downloads").
   - Numbers that appear in multiple files **with different values** are the highest-priority candidates: that is live drift, found before the manifest even exists.

3. **Group matches into facts.** Cluster occurrences that describe the same real-world quantity, even when formatted differently (`1,234` vs `1234`, `$5,000` vs `$5000`). Discard noise: bare years, dates that are just timestamps, version numbers of dependencies, anything appearing in only one file. Also discard **point-in-time records**: append-only snapshot tables, changelogs, dated session notes, and dated proposals or pitch drafts. A metrics table whose latest column lags the live value is not drift — it just has not been snapshotted since the value moved. If the repo's own docs name such a file as a copy that "must stay in sync," surface the tension for the human instead of forcing it into the manifest. Targets and goals ("8,000 subs by Dec 2026") are not facts either.

4. **Propose a canonical for each fact.** Prefer, in order: a file the repo's CLAUDE.md already names as source of truth, an auto-generated data file maintained by a pipeline, an analytics file, an index README. Marketing copies (media kits, landing pages) are almost never canonical — UNLESS the repo's docs explicitly delegate the surface to them ("the real media kit is the live page"), in which case the page is the canonical and the in-repo files are the copies. Mark each proposal with one line of reasoning. The human confirms or reassigns. One sanity check before proposing: when occurrences disagree and the fact is a count that only grows (followers, episodes, downloads), the LOWEST value is the suspect one — do not let the canonical-file heuristic override that. If the file the oracle names holds the stale value, propose it as canonical but flag "canonical appears stale; confirm live value before approving."

5. **Present the draft manifest, live drift first.** Drift found during the scan is the actionable part of the report; the proposed manifest is paperwork. Lead with it:

   ```
   SSOT DISCOVER — [DATE]

   LIVE DRIFT FOUND:
   - newsletter-subscribers: analytics/goals.md says 1,240 but business-plan.md says 1,100
   - [fact]: [where] says [X] but [where] says [Y] — [root cause if known: hand-copy
     drift, pipeline bug, sync lag, stale canonical]

   PROPOSED FACTS (N):
   - episode-count: 61 — canonical guess: outputs/episodes/README.md (CLAUDE.md names it SSOT)
     copies: sponsorship/media-kit.md, ../cot-sponsor-page/index.html
   - [fact]: [value] — canonical guess: [file] ([reasoning])

   DISCARDED (low confidence): [count, one-line summary]

   Draft .ssot.yaml below. Edit canonical assignments, then approve to write.
   ```

   If anything in the report could leave the repo (a worked example, a shared doc) and a value is sensitive by the repo's own rules, keep the fact entry and mask the value as `<redacted>` with a note. Mask values, never delete facts — a manifest with a hole in it protects nothing.

6. **Write `.ssot.yaml` only after explicit approval.** Then offer to run check mode immediately to fix the live drift.

## Check Mode (every subsequent run)

Goal: verify every copy still matches its canonical value. Main-thread, fast, read-only. Propose fixes, never auto-apply.

### Instructions

1. **Read `.ssot.yaml`.** If it does not exist, switch to discover mode.

2. **Establish freshness for sibling repos read-only.** For each cross-repo path in the manifest, read the sibling's working tree, and — when freshness matters — compare against the remote-tracking ref already on disk via `git show`, noting its tip date (see the cross-repo rules above). Do not fetch and do not pull — unless the user explicitly asked for a live-remote comparison this session, which is the one exception in cross-repo rule 1. If neither the working tree nor an existing remote-tracking ref yields a value you can stand behind, mark those facts **UNVERIFIED** and continue with the rest of the manifest.

3. **For each fact:**
   - Open the canonical file, apply the canonical pattern, extract the captured value.
   - Pattern does not match, or the file is missing: status **CANONICAL MOVED**. The manifest is stale. Propose an updated pattern or file path if the value is findable nearby.
   - For each copy, apply its pattern and compare captured values (whitespace-trimmed, thousands separators stripped, trailing `+` on the copy ignored). If the copy declares `rounding`, apply that transform to the canonical value first, then compare exactly.
     - Match: **IN SYNC**
     - Mismatch: **DRIFTED**. Record canonical value, copy value, and `file:line` of the copy. Before proposing the edit, check direction: if the fact is a monotonic count and the COPY is higher than the canonical, the canonical is probably the stale one — report **DRIFTED (canonical suspect)** and ask the human to confirm the live value instead of proposing an edit that would regress the copy.
     - Copy pattern does not match at all: **STALE ENTRY**. The copy was reworded or removed. Propose a manifest update.
     - Value could not be read at all — a cross-repo path with no readable working tree and no remote-tracking ref on disk: **UNVERIFIED**. Report it and move on. Never substitute a remembered, inferred, or previously-seen value for one you could not read, and never fetch to resolve it unless the user asked (see cross-repo rule 1). An UNVERIFIED fact is a smaller problem than a confidently wrong one.

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

   UNVERIFIED (1):
   - hero-episode-count — ../cot-sponsor-page/index.html not readable and the
     clone has no remote-tracking ref on disk. Not compared.
     to resolve: fetch that repo yourself, or re-run after updating the clone.

   8 facts checked, 1 drifted, 1 stale manifest entry, 1 unverified.
   ```

   The last line is the exit summary. Always emit it, even when everything is clean ("8 facts checked, all in sync"). Count UNVERIFIED facts separately — never fold them into "in sync", because "I could not check this" and "this matches" are opposite results.

5. **Apply fixes only after approval, one fact at a time.** Show the exact diff for each edit. Drifted copies get content edits. CANONICAL MOVED and STALE ENTRY get manifest edits. Cross-repo edits are flagged as landing in the sibling repo.

## Edge Cases

- **Intentional rounding.** Two kinds, handled differently. **Mechanical rounding** — a script floors the value before writing it ("156,000+" from a canonical 156,703) — is deterministic: declare it with the copy's `rounding` field and the comparison stays exact. **Editorial rounding** — a human wrote "11K subscribers" with no fixed rule — is not: either standardize the copy to the exact value, or remove that copy from the manifest and record the rounding habit in the fact's `note`. Do not add fuzzy matching; a check that sometimes shrugs is worse than no check.
- **Auto-generated copies.** If a script already writes some copies (a metrics pipeline updating a README line), list them in the manifest anyway with a `note: auto-generated by X`. The check then doubles as a pipeline health check, but fix proposals should point at the script, not the file. Two failure modes this catches: **sync lag** (a deploy-triggered copy that has not redeployed since the last metrics run) and **convention bugs** (the script writes one counting convention to one surface and a different one to another — e.g. a trailer-inclusive episode count to the exported JSON and a trailer-exclusive count to the README). The second one looks like ordinary drift but no document edit will fix it; the diff goes in the script.
- **Multiple matches for one pattern.** If a pattern matches more than once in a file, use the first match and warn. Tighten the pattern if the warning recurs.
- **Facts that legitimately differ per file.** A "subscribers" number quoted at different dates in different docs is not one fact. Do not force it into the manifest; drift checking only works for facts that should be identical everywhere.

## Design Principles

- **One canonical, everything else is a copy.** The manifest encodes that decision so no one has to remember it.
- **Propose, never auto-apply.** Report drift with exact diffs and wait for approval. Same contract as `/reconcile` and `/recover`.
- **Greppable manifest.** Plain YAML, plain regexes. A human can verify any entry with one grep.
- **Fast enough for a pre-commit habit.** Check mode is file reads and regex matches. Seconds, not minutes.
- **Exact match or flagged.** No fuzzy comparison. Ambiguity gets surfaced to the human, not resolved silently.

## Cross-references

- `patterns/discovery-prompt.md` — paste-ready subagent template for the discover-mode scan on large repos.
- `examples/cot-production-discovery/` — a real discover-mode run: the proposed `.ssot.yaml` plus the live drift it surfaced.
