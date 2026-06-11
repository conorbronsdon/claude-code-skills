# Angel Diligence

Pre-investment research and deal-memo generation for angel investors. Give it a company name (plus optional deck notes, founders, round details) and it runs parallel web research under strict citation rules, then writes a nine-section memo: Snapshot, Team, Market, Product & moat, Traction, Competition, Risks, Open questions for the founder call, and a Verdict scaffold. It never outputs an invest/pass call. The human decides.

Two rules do most of the work: every factual claim needs a fetched URL or gets marked "could not verify", and everything sourced only from the company itself is labeled "claimed" rather than "verified". Deck contents never go into web searches.

See [SKILL.md](SKILL.md) for full instructions and [patterns/research-prompts.md](patterns/research-prompts.md) for the subagent templates.

## Example output (abbreviated)

```markdown
## 5. Traction
- [verified] Acme listed as a customer: Acme eng blog post describes production use
  (acme.dev/blog/llm-evals, 2026-03-12)
- [claimed] "200+ teams" on homepage; could not verify independently (vectorgate.io, 2026-05)
- [verified] 4.1k GitHub stars, 38 contributors, last release 2026-05-28. Caveat:
  stars are gameable and weakly correlated with revenue (github.com/vectorgate/core)
- [verified] 6 open roles, 4 engineering (vectorgate.io/careers, accessed 2026-06-11)

## 7. Risks (top 5)
1. Incumbent feature risk: LangChain shipped overlapping evals tooling 2026-04.
   Changes my mind: win rate vs incumbents in the next 2 quarters, from references.
2. Single design partner drives most usage. Changes my mind: a second verified
   production customer outside the partner's network.
...

## 9. Verdict scaffold
- Strongest signal for: verified production use at Acme within 4 months of launch.
- Strongest signal against: no moat found beyond execution speed; incumbents are
  one release away.
- Valuation-moving unknowns: real revenue vs design-partner credits, and
  whether the data flywheel claim survives the founder call.
- Decision is yours. This memo is evidence, not advice.
```
