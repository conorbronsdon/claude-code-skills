---
name: guest-circuit
description: Podcast-appearance research for guest booking. Use when asked to "map someone's podcast circuit," "where has X podcasted," "research X before guest outreach," or "find an unclaimed angle for X." Sweeps Podcast Index, web search, and the guest's own channels in parallel, then delivers a circuit report: appearance timeline, stump speech, unclaimed angles, receptiveness signal, and a specific pitch angle.
---

# Guest Circuit — Podcast-Appearance Research for Booking

Before you pitch a prospective guest, answer two questions. Where have they already podcasted? And what has nobody asked them yet?

The first gates the booking decision. Someone on ten shows this quarter is podcast-receptive and easy to book. Someone on zero shows may need a warmer path than a cold email. The second shapes the pitch. Inviting a guest to retell the story they told three shows ago wastes the slot and bores their audience overlap with yours.

This skill maps the circuit and produces a report you can act on: appearance timeline, the "stump speech" they repeat everywhere, the angles no show has claimed, and a one-paragraph pitch built on the gap.

---

## Step 1: Disambiguate

Names collide. Before any search, confirm one anchor fact: company, role, or a known piece of work (book, project, paper).

- If the user provided an anchor ("Jane Doe, CTO at Acme"), proceed.
- If the user gave only a name, ask. Do not guess and do not search yet. A sweep on the wrong Jane Doe produces a confident, useless report.

Use the anchor to filter every result in later steps. A hit that cannot be tied to the anchor goes in "could not verify."

---

## Step 2: Appearance Sweep

Three source modalities. Run them as parallel subagents in a single tool-call batch (prompt templates in `patterns/subagent-prompts.md`). If subagents are unavailable, run the modalities sequentially in the same order.

### 2a. Podcast Index (canonical source, when configured)

Requires the [podcastindex-mcp](https://github.com/conorbronsdon/podcastindex-mcp) server. Tool names as exposed by that server:

- `search_by_person` with `q: "Full Name"`, `max: 50`, `fulltext: true` — episodes across all indexed podcasts where the person appeared.
- `podcast_by_feed_id` with `id: <feedId>` — show metadata for each hit worth keeping: episode count, categories, last update. This is the cheap audience signal.
- `episodes_by_feed_id` with `id: <feedId>` — only if you need surrounding episodes from one show (e.g. to check whether the person appeared more than once).

Caveats:
- `search_by_person` matches hosts and description mentions, not just guests. Filter to actual guest appearances using the episode title and description.
- `datePublished` fields are Unix timestamps. Convert before reporting.
- If the podcastindex tools are not configured, skip this modality, fall back to web search, and say so in the report's sources section ("Podcast Index not consulted").

### 2b. Web search

WebSearch queries, run all of them:
- `"[name]" podcast interview`
- `"[name]" "[company]" podcast episode`
- `"[name]" podcast guest`
- `site:youtube.com "[name]" podcast OR interview` — many appearances are YouTube-only and never reach podcast indexes.

### 2c. Their own trail

Guests promote their own appearances. Check:
- Personal site or company bio: press, speaking, or media page.
- LinkedIn and X posts (search `"[name]" site:linkedin.com podcast` if no direct access).
- Their newsletter or blog, which often links appearances.

### Recording appearances

For every appearance, capture: show name, episode title, publish date, link, and an audience signal if it is cheap to get (show episode count, known network, YouTube view count on the episode). Do not deep-research show size. A rough signal is enough.

Dedupe across modalities by episode link or show + title. Keep the best-sourced entry.

---

## Step 3: Content Map

Take the 3-5 most recent or most prominent appearances. For each, fetch the episode page or show notes. Show notes suffice. Do NOT fetch or summarize full transcripts; that is slow and the notes already list topics.

Extract:
- **Topics covered** per episode.
- **Repeated stories** — anecdotes, origin stories, or claims that appear across multiple shows. This is the stump speech. Your show should not re-ask it.

---

## Step 4: The Circuit Report

Deliver in this format:

```markdown
# Circuit Report: [Name] ([role], [company]) — [date]

## Appearance Timeline
| Date | Show | Episode | Link | Audience signal |
|------|------|---------|------|-----------------|
(newest first; "could not verify" entries in a separate short list below the table)

## Stump Speech (do not re-ask)
- [topic/story they covered on N shows, with which shows]

## Unclaimed Angles
- [expertise area from their recent work/writing that NO show on the circuit
  has explored, with the evidence: what they shipped/wrote vs. what the
  circuit covered]

## Receptiveness Signal
[cadence: N appearances in the last 6/12 months -> receptive / selective /
no visible circuit. One sentence on what that means for outreach.]

## Suggested Pitch Angle
[One paragraph. Specific. Names the unclaimed angle, why this guest is the
right person for it, and why your show is the right venue. Not "discuss AI."]

## Sources
- [URL] (fetched [date]) — what it verified
```

Derive unclaimed angles by contrast: list what their recent work, writing, and talks cover, then subtract what the circuit already covered. The remainder is the pitch material. If you cannot find their recent work, say so rather than inventing angles.

---

## Honesty Rules

These are hard requirements, not style preferences:

1. **Every appearance must be backed by a fetched page.** Model memory invents podcasts and misdates real ones. If you did not fetch a page (or get an index record) confirming the appearance, it does not go in the timeline.
2. **"Could not verify" is a real bucket.** A search snippet that mentions the person and a show is a lead, not a confirmed appearance. List unconfirmed leads separately and label them.
3. **Date everything.** Appearances, sources, and the report itself.
4. **A thin circuit is a finding, not a failure.** If the person has almost no podcast history, say so plainly. Then pivot: map their writing, conference talks, and interviews in text media instead. That report is just as useful for outreach; it changes the pitch from "another podcast" to "your first real podcast conversation about X."

---

## When NOT to Use This Skill

- The guest is already booked and you need interview prep. Use a talk-track or research workflow instead. This skill is for the booking decision and the pitch.
- You only need contact info or a bio. That is a single web search, not a circuit sweep.

---

## Cross-references

- `patterns/subagent-prompts.md` — paste-ready prompts for the three sweep modalities.
- [podcastindex-mcp](https://github.com/conorbronsdon/podcastindex-mcp) — the MCP server providing `search_by_person` and the other Podcast Index tools.
