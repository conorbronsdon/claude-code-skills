# Code Review

Multi-agent PR review orchestrator. Sizes the PR first, then runs GitHub Copilot and parallel Claude subagents (adversarial, operational, and reference-comparison lenses) at the same time, triages the combined findings into fix-now / stale re-flag / file-as-issue buckets, and caps Copilot at two rounds because round three is mostly stale re-flags. Run with `/code-review [pr-number-or-branch]`.

Built from a real deployment: across five review rounds on a Vercel-hosted Next.js PR, Copilot caught the line-level issues while the subagents caught the P0 architectural miss (`maxDuration`) Copilot missed in every round.

See [SKILL.md](SKILL.md) for the full workflow and [patterns/subagent-prompts.md](patterns/subagent-prompts.md) for the paste-ready subagent briefs.
