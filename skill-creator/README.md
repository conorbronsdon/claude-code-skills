# Skill Creator

Meta-skill that generates new Claude Code skills from plain-language descriptions. Beyond scaffolding the SKILL.md, it makes the design decisions most skill generators skip: invocation control (`disable-model-invocation` for user-only workflows — which also costs zero ambient context; `user-invocable: false` for background knowledge), arguments (`argument-hint`, `$ARGUMENTS`), and description budget (triggers in the description, detail in the body). Run with `/skill-creator`.

It stays current by design: [reference.md](reference.md) is a pinned, dated snapshot of the official frontmatter spec. The canonical version of this skill lives at [agent-skill-builder](https://github.com/conorbronsdon/agent-skill-builder) — standalone repo with a machine-checkable validator (`validate_skill.py`) and weekly spec-drift CI that opens an issue when the upstream spec changes. This copy tracks it.

See [SKILL.md](SKILL.md) for full instructions.
