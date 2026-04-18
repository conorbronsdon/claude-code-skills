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
| [Reconcile](reconcile/) | `/reconcile` | Parallel sessions cause state drift — this detects it |
| [Recover](recover/) | `/recover` | Crashed sessions leave orphaned worktrees — this cleans them |
| [Skill Creator](skill-creator/) | `/skill-creator` | Writing skills from scratch is slow — this scaffolds them |

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
- **`/end`** — Auto-extract session summary, update state, check for uncommitted work
- **`/update`** — Mid-session checkpoint (quick save)
- **`/today`** — Morning heartbeat: staleness check, deadlines, memory curation

Includes setup guide with the required file structure and minimal starter templates.

### [Reconcile](reconcile/)

Tripwire check for multi-session drift. Scans recent commits, state files, and cross-references for inconsistencies caused by parallel Claude Code sessions.

Use after merging worktree branches, after crashes, or whenever something feels off.

### [Recover](recover/)

Scan for orphaned worktrees and stale branches left behind by crashed or abandoned sessions. Read-only by default — reports findings and waits for your approval before any cleanup.

### [Skill Creator](skill-creator/)

Meta-skill: describe what you want a skill to do in plain language, and it generates the SKILL.md, command routing file, and CLAUDE.md additions. Good for bootstrapping new skills quickly.

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
