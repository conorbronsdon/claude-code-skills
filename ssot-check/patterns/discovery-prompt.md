# Subagent Prompt Template — SSOT Discovery Scan

One paste-ready template. Use it in discover mode when the repo is large enough that grep output would flood the main thread. Fill in the bracketed slots before spawning. Check mode never needs a subagent.

The prompt:
- Names the repo path and the file types in scope.
- Asks for clustered facts, not raw grep hits.
- Caps the report so the main thread can turn it straight into a draft manifest.

---

## Candidate-Fact Scanner

```
You are a fact-copy scanner. Your job is to find values that are hand-copied
across prose files in this repo, so they can be tracked in a drift manifest.

Repo: [absolute path]
Files in scope: *.md, *.html, *.txt, plus stat-bearing data files a pipeline
writes (data.json etc.). Skip code, lockfiles, node_modules, and vendored
dirs. Do NOT skip auto-generated files — scan them and tag each occurrence
from one as AUTO-GEN: [paste known generated files, e.g. from CLAUDE.md].
They are often the freshest value, and pipelines drift too.
Sibling repos to include, if any: [relative paths, e.g. ../cot-sponsor-page]

Find values that appear in 2 or more files:
- Numbers with a unit noun nearby (episodes, subscribers, downloads, users,
  stars, customers)
- Dollar amounts and percentages
- Version strings (v1.2.3 style) that describe THIS project, not dependencies
- Date ranges and "as of [date]" claims
- Sentences containing "as of", "currently", "total", "more than", "over"

Cluster occurrences that describe the same real-world quantity even when
formatted differently (1,234 vs 1234, $5,000 vs $5000, "11K" vs "11,432").
Count multiple occurrences within ONE file (a stat block, a meta description,
and a JSON-LD blob in the same HTML page are three separate copies).
Discard: bare years, timestamps, dependency versions, anything in one
occurrence only, goal/target tables, and point-in-time records — append-only
snapshot tables, changelogs, dated session notes, dated proposals/pitch
drafts. A dated table whose latest row lags the live value is history, not
drift.

Report format (cap ~600 words):
1. CANDIDATE FACTS — one block per fact:
   - suggested kebab-case name
   - current value(s)
   - every occurrence as file:line with the surrounding phrase (verbatim,
     trimmed to ~80 chars)
   - DRIFT flag if occurrences disagree right now
2. CANONICAL GUESS per fact — one file plus one line of reasoning
   (prefer files the repo's CLAUDE.md names as source of truth, then
   auto-generated data files, then analytics files, then index READMEs;
   marketing copies are never canonical UNLESS the repo's docs explicitly
   delegate the surface to them). If occurrences disagree on a count that
   only grows, the lowest value is the suspect — say so even when the
   canonical-file heuristic points at it.
3. DISCARDED — one line per discarded cluster, with the reason.

Do not write any files. Do not propose fixes. Report only.
```
