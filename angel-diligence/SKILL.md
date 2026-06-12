---
name: angel-diligence
description: Pre-investment research and deal-memo generation for angel investors. Use when asked to "diligence [company]", "research this startup for an investment", "build a deal memo", or to prep for a founder call. Runs parallel web research with strict citation rules and produces a nine-section memo that separates verified facts from claims. Never outputs an invest/pass recommendation.
---

# /angel-diligence: Pre-Investment Deal Memo

Given a company name (plus optional deck notes, founder names, round details), research the company from public sources and produce a structured deal memo. Every factual claim is cited. Anything unverifiable is labeled. The memo ends in a verdict scaffold, not a recommendation. The human decides.

## When to Use

- "Diligence [company]" / "research [company] for an angel check"
- "Build a deal memo for [company]"
- Before a founder call, to generate the highest-information questions
- After receiving a deck, to check the claims in it against public evidence

Skip for public companies (use an equity research workflow) and for follow-on rounds where you already hold a position and want a position review.

## Evidence Rules (read before researching)

These rules override speed. A short memo with real citations beats a long memo with invented facts.

1. **Every factual claim needs a fetched source.** A claim goes in the memo only if you fetched a page that supports it. Cite the URL inline next to the claim. Model memory is not a source; it is stale by definition for startups.
2. **"Could not verify" is a valid finding.** If a search comes up empty, write "could not verify" next to the claim. Do not fill gaps with plausible guesses. An absence of evidence is itself a signal worth reporting.
3. **Date everything.** Every cited fact gets the date of the source page (or "undated"). Funding databases, team pages, and pricing pages go stale fast. A 14-month-old headcount number presented as current is a hallucination with a citation. Funding data is the worst offender: aggregator databases (Crunchbase mirrors, Tracxn) often miss the latest round or conflate rounds. Prefer the primary announcement, and treat any funding fact older than 6 months as possibly superseded by an unannounced round.
4. **Separate verified from claimed.** Anything sourced only from the company itself (deck, website, founder posts) is "claimed." Anything confirmed by an independent source (customer post, public repo, conference talk by a user) is "verified." Press is verified only when it quotes a customer or third party speaking from their own experience; an article that only quotes the founders or investors is still "claimed." Label each traction item as one or the other.
5. **No invented numbers.** Never state a TAM, ARR, valuation, or growth rate that does not appear in a fetched source. Market sizing must be built bottom-up from cited inputs (number of potential buyers x plausible contract value), with the arithmetic shown.
6. **Confidentiality: never paste deck contents into web searches.** Deck notes the user provides may be under NDA or simply private. Use them to know what to look for, then search in generic terms ("[company] pricing", "[company] customers"). Never put deck numbers, customer names from the deck, or roadmap details into a search query or any other external tool. The company's name and public website are not confidential; use them freely even if you learned them from the deck. Litmus test for any query: could someone who never saw the deck have written it? If not, do not run it.

## Instructions

### Step 1: Intake

Collect what the user has. Required: company name. Optional: website, deck notes, founder names, round details (stage, raise amount, valuation, lead). Ask for the website if the name is ambiguous (many startups share names); if the user has only a deck, the website named in it is fine to use, per evidence rule 6. Note today's date at the top of your scratch state; it anchors every recency judgment.

Two gates before any research starts:

- **Conflict of interest.** Ask whether the company competes with, partners with, or sits adjacent to the user's employer, or any company where they hold inside information. If yes, pause and say so plainly: they should check their employment agreement and trading policy before going further, and the memo header must state that research used public sources only. Proceed only on explicit confirmation. Do not silently research a competitor of the user's employer.
- **Deal structure.** Ask whether the check is direct primary, via an SPV, or a secondary. An SPV adds fees and carry and usually drops information rights. A secondary price is not the round valuation. Record the answer; it goes in the Snapshot.

### Step 2: Orient (5 minutes, main thread)

Fetch the company website and one search of "[company] funding" news. Establish: what they sell, roughly what stage, founder names if not provided. This grounds the subagent prompts so they research the right company.

### Step 3: Parallel research

Spawn research subagents in a single batch so they run in parallel. Prompt templates live in `patterns/research-prompts.md`. Standard split:

- **Team**: founder backgrounds from LinkedIn, GitHub, talks, papers; prior companies and exits; red flags.
- **Product & traction**: what is shipped vs roadmap; GitHub activity, docs, changelog, demo availability; public customers, stars/downloads, hiring velocity, press.
- **Market & competition**: who pays, bottom-up sizing inputs, direct and adjacent competitors, incumbent feature risk.

Every subagent prompt must include: the company name and website, today's date, the shared evidence block from `patterns/research-prompts.md` pasted verbatim (it is the compact form of the six rules above; paste the block, do not re-summarize it), and a report cap (~600 words, citations included). If the user provided deck notes, pass only derived search targets ("verify whether they have enterprise customers"), never the deck text itself. A derived target passes the same litmus test as a query: nothing in it that someone who never saw the deck could not have written.

If subagents are unavailable, run the three angles sequentially in the main thread using the same prompts.

### Step 4: Verification pass (main thread)

Before writing the memo, audit the subagent reports. Subagent output is unverified input.

- Spot-check the 3-5 highest-stakes claims by fetching the cited URL yourself. Highest-stakes means: any claim that would change the verdict scaffold if it turned out false. In practice that is prior exits, named customers, funding amounts and valuation, headline revenue or usage numbers, and anything a subagent upgraded from "claimed" to "verified." If the page does not support the claim, demote it to "could not verify."
- Strip any claim that arrived without a URL.
- Check dates: flag any load-bearing fact older than 6 months as possibly stale.
- Cross-check contradictions between subagents (e.g., team page headcount vs LinkedIn count) and report the discrepancy rather than picking one.

### Step 5: Write the memo

Write to a local file (suggest `diligence/{company-slug}-{YYYY-MM-DD}.md`). Use exactly these nine sections:

1. **Snapshot**: what they do in one plain sentence a non-specialist understands. Stage, round, ask (mark each as provided-by-user, verified, or could not verify). Deal structure from intake: direct, SPV, or secondary, with the one-line consequence (SPV: fees, carry, and usually no information rights; secondary: the quoted round valuation is not the user's price). If the conflict-of-interest gate fired, the header states: built from public sources only.
2. **Team**: each founder: background, prior exits, public footprint, all cited. Red flags called out plainly: serial pivots, disputed departures, inflated titles, no public technical footprint for a "technical founder." If clean, say "no red flags found in public sources" rather than inventing praise.
3. **Market**: who actually pays (the buyer, not the user, when they differ). Bottom-up sizing with arithmetic shown and each input cited; label the result an order-of-magnitude estimate, not a market fact, since cited inputs can still be stale or wrong. Timing thesis: why this is buildable/sellable now and was not two years ago. No top-down TAM quotes unless cited, and even then label them vendor-reported.
4. **Product & moat**: what is real today vs roadmap, with evidence (repo commits, changelog dates, docs depth, whether a demo is publicly available or gated). Defensibility honestly assessed. Most AI startups have no moat beyond execution speed; when that is true here, say so in those words. List candidate moats (data flywheel, workflow lock-in, distribution, regulatory) and the evidence for or against each.
5. **Traction**: only verifiable signals, each labeled **verified** or **claimed** per the evidence rules. Stars and download counts carry a standing caveat: gameable and weakly correlated with revenue. Hiring velocity (open roles, recent joins) and press with named customers count; deck metrics repeat as "claimed" only.
6. **Competition**: direct competitors, adjacent players who could pivot in, and the incumbent question: why doesn't [obvious platform] add this as a feature, and what happens to the company if it does.
7. **Risks**: top 5, ranked. Each risk gets one line of "what evidence would change my mind" so the founder call and follow-up research have a target.
8. **Open questions for the founder call**: the 6-8 highest-information questions this research could not answer. Prefer questions whose answers are checkable later. Skip anything already answered by public sources.
9. **Verdict scaffold**: NOT a recommendation. Three parts: strongest signal for, strongest signal against, and valuation-moving unknowns (the 2-3 unknowns that move the price most). List the unknowns only. Never state a range, a multiple, or an anchor number; naming a price is pricing the deal, which is the recommendation in disguise. Close with: "Decision is yours. This memo is evidence, not advice."

End the memo with a **Sources** list: every URL cited, with access date.

### Step 6: Present for review

Show the memo path and the Snapshot + Verdict scaffold inline. Flag the count of "could not verify" items so the user knows the evidence coverage. Do not send, post, or share the memo anywhere; it stays local unless the user explicitly asks.

## Design Principles

- **Evidence or absence, never filler.** The memo's value is that every line is either cited or labeled unverifiable.
- **The model researches; the human decides.** No invest/pass language anywhere in the output.
- **Recency is part of truth.** An undated fact about a startup is half a fact.
- **Deck contents never leave the session.** Confidential input shapes the search plan; it never appears in a query.
- **Honest moat assessment.** "No durable moat found" is a finding, not a failure of the research.

## Setup

Copy this directory into your project, then create `.claude/commands/angel-diligence.md`:

```markdown
---
name: angel-diligence
description: Research a startup and build a cited deal memo
allowed-tools: WebSearch, WebFetch, Read, Write, Task
---

Load and follow the instructions in `skills/angel-diligence/SKILL.md`.
```

## Cross-references

- `patterns/research-prompts.md`: paste-ready subagent prompt templates for the three research angles.
- `examples/illustrative-memo.md`: a full nine-section memo on GitLab's Series A era (2015), reconstructed from public sources and clearly labeled illustrative.
- `README.md`: abbreviated example memo excerpt showing the output shape.
