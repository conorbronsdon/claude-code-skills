# Session Management

Four commands that give Claude Code memory across conversations. `/start` loads project state and gives a briefing, `/end` auto-extracts decisions, updates state, and proposes auto-memory updates, `/update` does a mid-session checkpoint, and `/today` runs a morning heartbeat with staleness checks, deadline surfacing, and memory curation.

Requires a `state/` directory with `current.md`, `decisions.md`, and `weekly-priorities.md` files. See [SKILL.md](SKILL.md) for the full setup guide and starter templates.
