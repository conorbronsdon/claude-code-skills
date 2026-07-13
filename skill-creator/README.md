# Skill Creator

Meta-skill that generates new Claude Code skills from plain-language descriptions. Beyond scaffolding the SKILL.md, it makes the design decisions most skill generators skip: invocation control (`disable-model-invocation` for user-only workflows — which also costs zero ambient context; `user-invocable: false` for background knowledge), arguments (`argument-hint`, `$ARGUMENTS`), and description budget (triggers in the description, detail in the body). Run with `/skill-creator`.

It stays current by design: [reference.md](reference.md) is a dated snapshot of the official frontmatter spec, and the skill re-fetches and diffs the docs whenever the snapshot is more than 3 months old — the fix for skill generators that rot as the spec evolves.

See [SKILL.md](SKILL.md) for full instructions.
