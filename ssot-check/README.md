# SSOT Check

![ssot-check demo](docs/demo.gif)

Canonical home is now [ssot-check](https://github.com/conorbronsdon/ssot-check) — tool-backed standalone: deterministic stdlib CLI (45 tests), JSON Schema, pre-commit hook, and GitHub Action. This skill-only copy tracks it.

Single-source-of-truth drift auditor for documentation-heavy repos. Facts like an episode count, a price, or a subscriber number are canonical in one file but hand-copied into others (media kits, READMEs, landing pages). Copies drift. `/ssot-check` discovers those facts, records canonical locations in a `.ssot.yaml` manifest, and verifies every copy on each run. Drifted copies get proposed diffs, never silent edits.

Two modes: **discover** (first run, proposes the manifest) and **check** (every run after, verifies copies and emits a one-line exit summary suitable for a pre-commit habit).

See [SKILL.md](SKILL.md) for full instructions and the manifest schema. A worked example from a real discover run — the proposed manifest plus the live drift it surfaced — is in [examples/cot-production-discovery/](examples/cot-production-discovery/).
