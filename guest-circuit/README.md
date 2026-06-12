# Guest Circuit

![guest-circuit demo](docs/demo.gif)

Podcast-appearance research for guest booking. Give it a name plus one anchor fact
(company, role, or known work) and it sweeps web search and the guest's own
channels — and Podcast Index when that MCP server is configured — then writes a
circuit report: an appearance timeline with verified URLs and dates, the "stump
speech" they repeat everywhere, the angles no show has claimed, a receptiveness
read, and a one-paragraph pitch built on the gap.

Two rules do most of the work: every appearance needs a fetched page or it goes in
"could not verify," and a thin circuit is a finding (bounded by your coverage), not
a failure. The skill never re-asks the stump speech — the pitch is always the
unclaimed angle.

See [SKILL.md](SKILL.md) for full instructions and [patterns/subagent-prompts.md](patterns/subagent-prompts.md)
for the three sweep-modality templates. A real, fully-cited run against a public
figure is in [examples/simon-willison-circuit.md](examples/simon-willison-circuit.md).
