---
name: ssot-check
description: Find facts copied across docs that no longer match.
version: 0.1.0
author: Conor Bronsdon (conorbronsdon)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [documentation, drift, audit, single-source-of-truth, maintenance]
    category: software-development
    related_skills: [code-wiki]
    requires_toolsets: [terminal]
---

# SSOT Check — Fact-Copy Drift Auditor

Documentation-heavy repos repeat facts. A user count lives in a README, then gets hand-copied into
a media kit, a landing page, and a pitch deck. Someone updates the README. The copies drift, and
nobody notices until a customer quotes the stale number back at you.

This skill finds those copies, records which one is allowed to be right, and checks the rest
against it. It does not fix anything on its own — every edit is proposed with an exact diff and
waits for you.

## When to Use

- First run on a repo, or after adding a new doc surface (a media kit, a landing page, a pricing page).
- Before commits that touch docs, as a pre-commit habit.
- Any time a canonical number changed and you need to know what else quotes it.
- After a bulk find-and-replace, to confirm nothing was missed.

Skip it when the repo has no duplicated facts, or when values legitimately differ per file — dated
snapshot series, goal targets versus current numbers, historical records. Those are not copies, and
tracking them only produces false positives.

## Prerequisites

- `search_files` and `read_file` for the audit, `patch` to apply approved fixes to existing files,
  `write_file` to create `.ssot.yaml` on a first run.
- `terminal` access to `git`, used read-only for cross-repo checks.
- A sibling clone on disk for any cross-repo copy.

No API keys and no external dependencies. Network access is needed only when a manifest declares a
cross-repo path, and only for `git fetch`.

## How to Run

```
Use the ssot-check skill to audit this repo for drift.
```

Mode is auto-detected: a `.ssot.yaml` at the repo root means check mode, its absence means discover
mode. Say "discover" or "check" to force one.

## Quick Reference

| Status | Meaning |
|---|---|
| `IN SYNC` | Copy matches the canonical value. |
| `DRIFTED` | Copy disagrees with canonical. Diff proposed. |
| `DRIFTED (canonical suspect)` | Monotonic count where the copy is *higher*. The canonical is probably the stale one — confirm before editing. |
| `CANONICAL MOVED` | The canonical pattern no longer matches. The manifest is stale. |
| `STALE ENTRY` | A copy pattern no longer matches. The copy was reworded or deleted. |

Manifest shape (`.ssot.yaml`, repo root):

```yaml
facts:
  - name: supported-languages
    note: Count of languages the parser handles. Excludes experimental grammars.
    canonical:
      file: docs/reference/languages.md
      pattern: 'Supported languages:\s*\*?\*?(\d+)'
    copies:
      - file: README.md
        pattern: '(\d+) supported languages'
      - file: ../marketing-site/index.html
        pattern: '<span class="stat-languages">(\d+)</span>'
```

Schema rules that matter:

- Exactly one capture group per pattern. The check compares captured strings, not whole lines.
- Patterns match whole file content, not line by line. HTML often splits a value from its label
  across lines — anchor on the nearest stable attribute and let `\s*` cross the break.
- The same file may appear in `copies[]` more than once. A landing page's stat block, meta
  description, and JSON-LD blob each carry the number separately and drift from each other.
- Comparison strips whitespace, thousands separators (`1,234` matches `1234`), and a trailing `+`
  on the copy. Everything else must match exactly.
- `note` should record **counting conventions** ("excludes experimental grammars", "installs not
  downloads"). Real drift is often a convention mismatch between two numbers that both look correct.
- `rounding` (optional, per copy) declares a deterministic transform applied to the *canonical*
  value before an exact comparison, for copies a script intentionally rounds:

  | Value | Transform |
  |---|---|
  | `floor-10` | Floor to the nearest multiple of 10. |
  | `floor-100` | Floor to the nearest multiple of 100. |
  | `floor-1000` | Floor to the nearest multiple of 1000. |
  | `floor-1000-as-K` | Floor to thousands, then compare against a value written as `NNNK` (canonical `156703` matches a copy reading `156K`). |

  The transform is exact, not fuzzy, so a mismatch after rounding still means something is wrong —
  usually sync lag.
- Forward slashes in paths on every platform. Regexes in single-quoted YAML so backslashes survive.

## Procedure

### Discover mode

1. **Confirm no `.ssot.yaml` exists.** If one does, ask whether to extend it or just run check mode.

2. **Scan for candidate facts** with `search_files` across markdown, HTML, and prose. Skip code,
   lockfiles, and vendored directories. Do *not* skip generated data files — a `data.json` a
   metrics script writes is usually the freshest value and the best canonical. Being generated does
   not exempt it from drifting: a script can write one counting convention to one file and a
   different one to another. Heuristics, in priority order:
   - The same distinctive number in 2+ prose files. Distinctive means 2+ digits with a unit noun
     nearby, any dollar amount, any percentage, any version string, date ranges.
   - Sentences containing "as of", "currently", "total", "more than", "over N".
   - Numbers appearing in multiple files **with different values** — that is live drift, found
     before the manifest exists.

3. **Group matches into facts.** Cluster occurrences describing the same real-world quantity even
   when formatted differently. Discard bare years, dependency versions, and anything appearing in
   one file only. Also discard **point-in-time records**: append-only snapshot tables, changelogs,
   dated session notes. A metrics table whose latest column lags the live value is not drift, it
   just has not been snapshotted. Targets and goals are not facts either.

4. **Propose a canonical for each fact.** Prefer, in order: a file the repo's own docs name as
   source of truth, an auto-generated data file, an analytics file, an index README. Marketing
   copies are almost never canonical — unless the docs explicitly delegate the surface to them, in
   which case the page is canonical and the repo holds the copies. One sanity check: when
   occurrences disagree and the fact is a count that only grows, the **lowest** value is the
   suspect one, even if it sits in the file the docs name as canonical.

5. **Present the draft, live drift first.** Drift found during the scan is the actionable part; the
   manifest is paperwork. If a value is sensitive and the report could leave the repo, mask it as
   `<redacted>` and keep the fact — a manifest with a hole in it protects nothing.

6. **Write `.ssot.yaml` with `write_file` only after explicit approval.** Report the discarded count
   alongside the proposal so the human can see what the scan chose to ignore.

### Check mode

1. **Read `.ssot.yaml`** with `read_file`. If absent, switch to discover mode.

2. **Refresh any sibling repos** named by cross-repo paths, following the read-only rules below.
   A stale sibling working tree silently poisons every comparison that touches it.

3. **For each fact**, extract the canonical value, then compare every copy. Apply any declared
   `rounding` to the canonical value first, then compare exactly. Assign one status per copy:

   - **IN SYNC** — values match.
   - **DRIFTED** — record the canonical value, the copy value, and the copy's `file:line`. Before
     proposing an edit, check direction: on a count that only grows, a copy *higher* than the
     canonical means the canonical is probably stale. Report **DRIFTED (canonical suspect)** and ask
     the human to confirm the live value rather than proposing an edit that would regress the copy.
   - **CANONICAL MOVED** — the canonical pattern does not match, or the canonical file is missing.
     The manifest is stale. Propose an updated pattern or file path if the value is findable nearby.
   - **STALE ENTRY** — a copy's pattern does not match at all. The copy was reworded or removed.
     Propose a manifest update.

4. **Report**, then apply fixes one fact at a time, showing the exact diff for each and waiting for
   approval. **Fixes route by status:** DRIFTED gets a content edit to the document with `patch`;
   CANONICAL MOVED and STALE ENTRY get an edit to `.ssot.yaml`, not to any document. Flag cross-repo
   edits as landing in the sibling repo with its own commit and deploy path.

   Always close with the exit summary line, even when everything is clean:

   ```
   8 facts checked, 1 drifted, 1 stale manifest entry.
   8 facts checked, all in sync.
   ```

### Cross-repo copies

A copy — or the canonical — may live in a sibling clone. Use a relative path that escapes the repo
root. Three rules:

1. **Never mutate the sibling to check it.** Run `git -C ../sibling fetch` through `terminal` and
   compare against the remote ref. Do not pull or rebase a repo you are only auditing. If you
   cannot establish a fresh value read-only, report `UNVERIFIED` rather than guessing.
2. **Fixes to a sibling are a separate commit** in that repo, with its own deploy path.
3. **A cross-repo canonical is legitimate**, and a stale one poisons every comparison for that fact.

## Pitfalls

- **Editorial rounding breaks exact comparison.** A human writing "11K subscribers" with no fixed
  rule is not mechanical rounding. Either standardize the copy to the exact value or drop it from
  the manifest and record the habit in `note`. Do not add fuzzy matching — a check that sometimes
  shrugs is worse than no check.
- **Auto-generated copies still drift.** List them with `note: auto-generated by X`. The check then
  doubles as a pipeline health check, but the fix goes in the script, not the file.
- **A pattern matching more than once** uses the first match and warns. Tighten the pattern if the
  warning recurs.
- **Direction matters on monotonic counts.** If the copy is higher than the canonical on a
  count that only grows, proposing the "fix" would regress the copy. Flag it instead.
- **Facts that legitimately differ per file are not one fact.** Drift checking only works for values
  that should be identical everywhere.

## Verification

```
Use the ssot-check skill in discover mode on this repo.
```

Working correctly, it reports candidate facts with a proposed canonical and one line of reasoning
each, and writes nothing to disk until you approve. On a repo with no duplicated facts it says so
and stops rather than inventing entries.
