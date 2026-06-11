# Subagent Prompt Templates for Angel Diligence

Three paste-ready templates. Fill the bracketed slots, then spawn all three in a single tool-call batch so they run in parallel.

Every prompt:
- Names the company, website, and today's date.
- Carries the evidence rules. Subagents hallucinate too; the rules travel with the prompt. The shared block below is the compact form of SKILL.md's six rules and is the exact text that travels: paste it unmodified into every prompt.
- Caps the report at ~600 words including citations.
- Forbids passing deck contents into searches. If the orchestrator has deck notes, it passes derived search targets only ("verify whether they claim enterprise customers"), never the deck text. Litmus test: a derived target contains nothing that someone who never saw the deck could not have written.

Shared evidence block to paste into every prompt:

```
EVIDENCE RULES (non-negotiable):
1. Every factual claim needs a URL you actually fetched this session. No URL, no claim.
2. If you cannot verify something, write "could not verify: [claim]". That is a useful finding.
3. Date every fact with the source page's date, or mark it "undated". For funding facts,
   prefer the primary announcement over aggregator databases; they lag and conflate rounds.
4. Label each item "verified" (independent source) or "claimed" (company's own materials).
   Press that only quotes founders or investors counts as "claimed".
5. Never state a number (TAM, ARR, headcount, valuation) that does not appear in a fetched source.
6. Never put any text I gave you from private materials into a search query or any other
   external tool. The company's name and website are fine; their numbers, customers, and
   roadmap are not.
Report cap: ~600 words including citations. Findings first, then "could not verify" list.
```

---

## 1. Team Research

```
You are researching the founding team of [company] ([website]) for angel investment
diligence. Today's date: [date].

Founders (if known): [names, else "identify them first from the company site/LinkedIn"].

For each founder, find and cite:
- Current role and how long at this company
- Prior roles and companies; any exits (acquired? IPO? shut down?) with outcome
- Public technical footprint: GitHub profile and activity, papers, conference talks
- Public writing or talks that show how they think about this market

Red flags to check explicitly (report findings either way):
- Serial pivots: has this same entity/team relaunched under different products?
- Disputed departures from prior companies (lawsuits, public fallouts)
- Title inflation: "founder" of things that were projects, not companies
- A "technical founder" with no findable technical footprint

If a founder is clean, say "no red flags found in public sources." Do not pad with praise.

[PASTE SHARED EVIDENCE BLOCK]
```

---

## 2. Product & Traction Research

```
You are researching the product and traction of [company] ([website]) for angel
investment diligence. Today's date: [date].

Product reality check (shipped vs roadmap):
- Public GitHub org/repos: commit recency, contributor count, release cadence
- Docs: do they cover a real product surface, or a thin landing layer?
- Changelog or release notes: dates and substance of recent entries
- Demo: publicly available, gated behind sales, or absent?
- Pricing page: self-serve, "contact us", or none?

Traction signals (label every item "verified" or "claimed"):
- Named customers (logos on site = claimed; customer's own post/talk = verified)
- GitHub stars / package downloads, with the standing caveat that both are gameable
- Hiring velocity: open roles count and seniority mix, recent joins visible on LinkedIn
- Press: note whether coverage has named sources or is rewritten PR
- Community: Discord/Slack size if public, forum activity

Specific things to verify (from the investor's private notes; do NOT put this text
in any search query, search in generic terms instead): [derived targets or "none"].

[PASTE SHARED EVIDENCE BLOCK]
```

---

## 3. Market & Competition Research

```
You are researching the market and competition for [company] ([website]) for angel
investment diligence. Today's date: [date]. They sell: [one-line description from
the orient step].

Market:
- Who pays? Identify the buyer persona and budget line, not just the user
- Bottom-up sizing inputs with citations: how many potential buying orgs exist,
  and what comparable products charge. Show inputs only; the orchestrator does
  the arithmetic. Do NOT quote top-down TAM figures unless you fetched the source,
  and label any vendor/analyst TAM as such.
- Timing: what changed (model capability, cost curve, regulation, platform shift)
  that makes this buildable or sellable now?

Competition:
- Direct competitors: name, funding if findable, how they differ
- Adjacent players one pivot away from this space
- The incumbent question: which large platform is most likely to ship this as a
  feature, have they announced anything adjacent, and what is the company's
  survival story if they do?

[PASTE SHARED EVIDENCE BLOCK]
```
