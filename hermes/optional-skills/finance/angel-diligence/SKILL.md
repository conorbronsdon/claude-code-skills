---
name: angel-diligence
description: Research a startup and draft a cited deal memo.
version: 1.0.0
author: Conor Bronsdon (conorbronsdon)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [investing, due-diligence, startups, research, deal-memo, angel]
    category: finance
    related_skills: [osint-investigation, domain-intel]
---

# Angel Diligence — Pre-Investment Deal Memo

Given a company name, researches it from public sources and produces a nine-section deal memo.
Every factual claim is cited. Anything unverifiable is labeled as such. The memo ends in a verdict
scaffold, not a recommendation.

**This skill never outputs invest or pass.** Naming a price or a range is pricing the deal, which
is the recommendation in disguise. The memo is evidence; the decision is the reader's.

## When to use this skill

- "Diligence [company]" or "research [company] for an angel check".
- Before a founder call, to generate the highest-information questions.
- After receiving a deck, to check its claims against public evidence.

Skip it for public companies — use an equity research workflow — and for follow-on rounds where you
already hold a position and want a position review instead.

## Prerequisites

Web access for `web_extract`. No API keys, no paid data sources, no external dependencies. The memo
is written to a local file with `patch`.

## How to run

```
Use the angel-diligence skill to diligence Acme Corp.
```

Pass the website too if the name is ambiguous — many startups share names.

## Quick reference

**Six evidence rules. These override speed.** A short memo with real citations beats a long memo
with invented facts.

| # | Rule |
|---|---|
| 1 | Every factual claim needs a page you actually fetched. Model memory is not a source; it is stale by definition for startups. |
| 2 | "Could not verify" is a valid finding. Absence of evidence is itself a signal. Never fill a gap with a plausible guess. |
| 3 | Date everything. A 14-month-old headcount presented as current is a hallucination with a citation. |
| 4 | Separate **verified** from **claimed**. Company-sourced is claimed. Press counts as verified only when it quotes a customer or third party from their own experience. |
| 5 | No invented numbers. Market sizing is built bottom-up from cited inputs with the arithmetic shown. |
| 6 | Deck contents never enter a search query. |

**Rule 6 litmus test:** could someone who never saw the deck have written this query? If not, do not
run it. The company's name and public website are not confidential even when you learned them from
the deck; its numbers, customer names, and roadmap are.

**Funding data is the least reliable category.** Aggregator databases routinely miss the latest
round or conflate rounds. Prefer the primary announcement, and treat any funding fact older than
six months as possibly superseded.

## Procedure

### Step 1 — Intake, and two gates

Collect the company name (required) plus website, deck notes, founder names, and round details if
available. Note today's date; it anchors every recency judgment.

Two gates before any research begins:

- **Conflict of interest.** Ask whether the company competes with, partners with, or sits adjacent
  to the reader's employer, or any company where they hold inside information. If yes, say plainly
  that they should check their employment agreement and trading policy first, and proceed only on
  explicit confirmation. The memo header must then state that research used public sources only.
- **Deal structure.** Direct primary, SPV, or secondary? An SPV adds fees and carry and usually
  drops information rights. A secondary price is not the round valuation. Record the answer.

### Step 2 — Orient

Fetch the company website with `web_extract` and run one search for recent funding news. Establish
what they sell, roughly what stage, and founder names. This grounds the research prompts so they
cover the right company.

### Step 3 — Parallel research

Dispatch three `delegate_task` subagents in one batch:

- **Team** — founder backgrounds from public profiles, repos, talks, papers; prior companies and
  exits; red flags.
- **Product and traction** — shipped versus roadmap; repo activity, docs, changelog, demo
  availability; public customers, hiring velocity, press.
- **Market and competition** — who actually pays, bottom-up sizing inputs, direct and adjacent
  competitors, incumbent feature risk.

Every prompt carries the company name and website, today's date, the six evidence rules verbatim,
and a ~600-word cap including citations. If deck notes exist, pass only derived search targets
("verify whether they have enterprise customers") and never the deck text. A derived target passes
the same litmus test as a query.

If `delegate_task` is unavailable, run the three angles sequentially with the same prompts.

### Step 4 — Verification pass

Subagent output is unverified input. Before writing anything:

- Fetch the cited URL yourself for the 3–5 highest-stakes claims — prior exits, named customers,
  funding amounts, valuation, headline revenue, and anything a subagent upgraded from claimed to
  verified. If the page does not support the claim, demote it to "could not verify".
- Strip any claim that arrived without a URL.
- Flag any load-bearing fact older than six months as possibly stale.
- Report contradictions between subagents rather than picking a winner.

### Step 5 — Write the memo

Write to `diligence/{company-slug}-{YYYY-MM-DD}.md` using exactly these nine sections:

1. **Snapshot** — what they do in one plain sentence. Stage, round, ask, each marked
   provided/verified/unverified. Deal structure with its one-line consequence.
2. **Team** — each founder, cited. Red flags called out plainly: serial pivots, disputed departures,
   inflated titles, no public technical footprint for a "technical founder". If clean, write "no red
   flags found in public sources" rather than inventing praise.
3. **Market** — who actually pays (the buyer, not the user, when they differ). Bottom-up sizing with
   arithmetic shown and inputs cited, labeled an order-of-magnitude estimate. Timing thesis: why now
   and not two years ago.
4. **Product and moat** — real today versus roadmap, with evidence. Most AI startups have no moat
   beyond execution speed; when that is true here, say so in those words.
5. **Traction** — each signal labeled verified or claimed. Stars and downloads carry a standing
   caveat: gameable, weakly correlated with revenue.
6. **Competition** — direct, adjacent, and the incumbent question: why doesn't the obvious platform
   add this as a feature, and what happens if it does?
7. **Risks** — top five, ranked, each with one line of "what evidence would change my mind".
8. **Open questions for the founder call** — the 6–8 highest-information questions this research
   could not answer. Prefer ones whose answers are checkable later.
9. **Verdict scaffold** — strongest signal for, strongest signal against, and the 2–3 unknowns that
   move the price most. List the unknowns only; never state a range, a multiple, or an anchor. Close
   with: "Decision is yours. This memo is evidence, not advice."

End with a **Sources** list: every URL, with access date.

### Step 6 — Present for review

Show the memo path plus the Snapshot and Verdict scaffold inline, and report the count of "could
not verify" items so the reader knows the evidence coverage. The memo stays local. Do not send,
post, or share it anywhere.

## Pitfalls

- **Aggregator funding data is often wrong.** It misses unannounced rounds and conflates round
  labels. Chase the primary announcement.
- **Press that only quotes founders is still "claimed".** The label exists to catch exactly this.
- **Bottom-up sizing built on stale inputs is still stale.** Cite and date each input, and label the
  output an estimate.
- **The confidentiality rule fails quietly.** A query leaking deck detail looks like a normal query.
  Apply the litmus test to every one, including derived targets handed to subagents.
- **An undated fact about a startup is half a fact.** Startups change faster than the pages
  describing them.

## Verification

```
Use the angel-diligence skill to diligence a company you know is public.
```

Working correctly, it declines and points to an equity research workflow. On a real private
company it produces all nine sections, a Sources list where every claim traces to a fetched URL,
and a verdict scaffold containing no price and no invest/pass language.
