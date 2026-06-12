<div align="center">

# Claude Code Skills

Production-tested skills for Claude Code. Drop-in markdown files that teach Claude specific workflows.

[![GitHub stars](https://img.shields.io/github/stars/conorbronsdon/claude-code-skills?style=social)](https://github.com/conorbronsdon/claude-code-skills/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Podcast](https://img.shields.io/badge/Podcast-Chain_of_Thought-purple?style=flat-square)](https://chainofthought.show)
[![X](https://img.shields.io/badge/X-@ConorBronsdon-black?style=flat-square&logo=x)](https://x.com/ConorBronsdon)

</div>

---


These are patterns I built for my own daily work and generalized for anyone to use. They work with Claude Code out of the box and follow the [agentskills.io](https://agentskills.io) standard where applicable.

## At a Glance

| Skill | Commands | What it solves |
|-------|----------|---------------|
| [Session Management](session-management/) | `/start`, `/end`, `/update`, `/today` | Claude Code has no memory between sessions — this adds it |
| [Code Review](code-review/) | `/code-review` | Single-pass reviews miss architectural P0s — this orchestrates Copilot + parallel subagents |
| [Eval Integrity](eval-integrity/) | `/eval-integrity` | Benchmark numbers get dismissed in review — this audits an eval repo across 7 credibility dimensions |
| [Reconcile](reconcile/) | `/reconcile` | Parallel sessions cause state drift — this detects it |
| [SSOT Check](ssot-check/) | `/ssot-check` | Facts hand-copied across docs drift — this tracks the canonical value and audits every copy |
| [Recover](recover/) | `/recover` | Crashed sessions leave orphaned worktrees — this cleans them |
| [Skill Creator](skill-creator/) | `/skill-creator` | Writing skills from scratch is slow — this scaffolds them |
| [Guest Circuit](guest-circuit/) | `/guest-circuit` | Pitching a podcast guest blind re-asks what three other shows asked — this maps their circuit and finds the unclaimed angle |
| [Angel Diligence](angel-diligence/) | `/angel-diligence` | Startup diligence is ad hoc and easy to hallucinate; this produces a cited deal memo with a verdict scaffold, not a recommendation |
| [avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) ↗ | `/clean-ai-writing` | AI writing has tells — 90+ checks across vocabulary, structure, rhythm |

## Quick Start

Prerequisites: [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed, a project with a `.claude/commands/` directory.

```bash
# 1. Copy a skill into your project
cp -r session-management/SKILL.md your-project/skills/session-management/SKILL.md

# 2. Create a command routing file
cat > your-project/.claude/commands/start.md << 'EOF'
---
name: start
description: Start a session — load state and get a briefing
---

Load and follow the instructions in `skills/session-management/SKILL.md`, section "/start — Begin Session".
EOF

# 3. Use it
# Type /start in Claude Code
```

Repeat for each skill/command you want. See each skill's SKILL.md for the full setup details.

## Skills

### [Session Management](session-management/)

A system of four commands (`/start`, `/end`, `/update`, `/today`) that give Claude Code memory across conversations. Maintains state files so every session picks up where the last one left off.

- **`/start`** — Load project state, check what changed, get a briefing
- **`/end`** — Auto-extract session summary, update state, propose auto-memory updates, check for uncommitted work
- **`/update`** — Mid-session checkpoint (quick save)
- **`/today`** — Morning heartbeat: staleness check, deadlines, memory curation

Includes setup guide with the required file structure and minimal starter templates.

### [Code Review](code-review/)

Multi-agent orchestrator for code-PR review. Spawns Copilot plus parallel subagents (adversarial, operational, reference-comparison) sized to PR risk, with stale-finding triage and a hard 2-round iteration cap. Built because line-level review consistently misses architectural failures (Vercel `maxDuration`, persistent-replay vectors, missing retry budgets) that only surface when a reviewer is asked the right operational question.

Use for: high-stakes PRs touching auth, payment, crypto, deploy configs, or external SDK integrations. Skip for typos and trivial changes.

### [Eval Integrity](eval-integrity/)

Credibility audit for LLM evaluation and benchmark repos. Greps the target repo for evidence across seven integrity dimensions (pre-registration, contamination, holdout hygiene, judge validity, statistical honesty, reproducibility, leaderboard exclusions), spawns one auditor subagent per dimension in parallel, and emits a scored report: PRESENT / PARTIAL / ABSENT with `file:line` evidence and a concrete fix for every gap. Each gap is tagged INVALIDATING (a reviewer can throw out the published number) or HARDENING. Read-only — it reports and offers fixes, never edits the benchmark or re-runs an eval. The checks were extracted from hardening a real agent benchmark for external grant review.

Use before submitting a benchmark to a grant, conference, or public leaderboard, or whenever someone says "I don't trust those numbers."

### [Reconcile](reconcile/)

Tripwire check for multi-session drift. Scans recent commits, state files, and cross-references for inconsistencies caused by parallel Claude Code sessions.

Use after merging worktree branches, after crashes, or whenever something feels off.

### [SSOT Check](ssot-check/)

Drift auditor for facts that are canonical in one file but hand-copied into others (episode counts, prices, subscriber numbers, versions). Discover mode scans the repo for drift-prone values and proposes a `.ssot.yaml` manifest mapping each fact to its canonical file and known copies, with regex capture groups so values can be extracted and compared. Check mode reads the manifest, verifies every copy against the canonical value, and reports IN SYNC / DRIFTED / CANONICAL MOVED with `file:line` evidence and proposed diffs. Never auto-applies fixes. Handles cross-repo copies (a landing page in a sibling clone) and ends with a one-line summary built for a pre-commit habit.

Use before commits that touch docs, after updating any canonical number, or on any repo with a "grep for other files with this number" rule that people forget to follow.

### [Recover](recover/)

Scan for orphaned worktrees and stale branches left behind by crashed or abandoned sessions. Read-only by default — reports findings and waits for your approval before any cleanup.

### [Skill Creator](skill-creator/)

Meta-skill: describe what you want a skill to do in plain language, and it generates the SKILL.md, command routing file, and CLAUDE.md additions. Good for bootstrapping new skills quickly.

### [Guest Circuit](guest-circuit/)

Podcast-appearance research for guest booking. Give it a prospective guest's name plus one anchor fact, and it maps their podcast circuit: every show they've appeared on, how recently, what they covered, and what angle is still unclaimed for your show. Uses [podcastindex-mcp](https://github.com/conorbronsdon/podcastindex-mcp) (`search_by_person`) as the canonical source when configured, degrading to web search when not. Every appearance is verified by a fetched page; nothing comes from model memory.

Abbreviated example output:

```markdown
# Circuit Report: Jane Doe (CTO, Acme) — 2026-06-11

## Appearance Timeline
| Date       | Show            | Episode                      | Audience signal |
|------------|-----------------|------------------------------|-----------------|
| 2026-05-02 | Infra Weekly    | "Scaling Acme's eval stack"  | 410 eps, indie  |
| 2026-03-18 | The Stack Pod   | "Jane Doe on agent testing"  | 38K YT views    |
| 2026-01-09 | DevTools Radio  | "From monolith to agents"    | network show    |

## Stump Speech (do not re-ask)
- The Acme founding story and the monolith rewrite (told on all 3 shows)

## Unclaimed Angles
- Her March post on eval dataset rot — no show has touched it

## Receptiveness Signal
3 appearances in 5 months: actively podcast-receptive, cold outreach viable.

## Suggested Pitch Angle
[one specific paragraph built on the unclaimed angle]
```

Use before outreach, not for interview prep of an already-booked guest.

## How to Use

### Quick start (single skill)

1. Copy the `SKILL.md` from the skill directory you want
2. Place it in your project (e.g., `skills/session-management/SKILL.md`)
3. Reference it in your `CLAUDE.md` or `.claude/commands/` directory
4. Use the slash command (e.g., `/start`, `/end`, `/reconcile`)

### Full setup (all skills)

1. Clone this repo or copy the skill directories into your project
2. Add command routing files to `.claude/commands/` for each skill:

```markdown
---
name: start
description: Start a session — load state and get a briefing
---

Load and follow the instructions in `skills/session-management/SKILL.md`, section "/start — Begin Session".
```

3. Add the commands to your `CLAUDE.md` slash command table

### Works with other AI tools

These skills follow the [agentskills.io](https://agentskills.io) format and work with Cursor, Windsurf, Cline, OpenHands, and 40+ other AI coding tools. Check each tool's docs for how to load custom instruction files.

## Related

- **[AI Tools for Creators](https://github.com/conorbronsdon/ai-tools-for-creators)** — Collection of skills, MCP servers, and workflow tools
- **[avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing)** — Catch and fix AI writing patterns (90+ checks)
- **[AI Learning Resources](https://github.com/conorbronsdon/ai-learning-resources)** — Curated learning path from "what is AI?" to building with Claude Code

## Contributing

Found a bug or have an improvement? Open an issue or PR. If you've built a skill that others would find useful, I'm happy to consider adding it.

---

## Disclaimer

*All views, opinions, and statements expressed on this account are solely my own and are made in my personal capacity. They do not reflect, and should not be construed as reflecting, the views, positions, or policies of Modular. This account is not affiliated with, authorized by, or endorsed by Modular in any way.*

## License

MIT — see [LICENSE](LICENSE).

## About

Built by [Conor Bronsdon](https://github.com/conorbronsdon). These skills were developed through daily use while running [Chain of Thought](https://chainofthought.show), a podcast about AI infrastructure and developer tools.
