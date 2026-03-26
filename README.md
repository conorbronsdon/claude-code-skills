# Claude Code Skills

Production-tested skills for Claude Code. Each skill is a drop-in markdown file that teaches Claude how to handle a specific workflow.

These are patterns I built for my own daily work and generalized for anyone to use. They work with Claude Code out of the box and follow the [agentskills.io](https://agentskills.io) standard where applicable.

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

- **[AI Tools for Creators](https://github.com/conorbronsdon/ai-tools-for-creators)** — Curated collection of skills, MCP servers, and workflow tools
- **[avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing)** — Catch and fix AI writing patterns (90+ checks)
- **[AI Learning Resources](https://github.com/conorbronsdon/ai-learning-resources)** — Curated learning path from "what is AI?" to building with Claude Code

## Contributing

Found a bug or have an improvement? Open an issue or PR. If you've built a skill that others would find useful, I'm happy to consider adding it.

## License

MIT — see [LICENSE](LICENSE).

## About

Built by [Conor Bronsdon](https://github.com/conorbronsdon). These skills were developed through daily use while running [Chain of Thought](https://chainofthought.show), a podcast about AI infrastructure and developer tools.
