---
name: guest-circuit
description: Podcast-appearance research for guest booking. Use when asked to "map someone's podcast circuit," "where has X podcasted," "research X before guest outreach," or "find an unclaimed angle for X." Sweeps Podcast Index, web search, and the guest's own channels in parallel, then delivers a circuit report: appearance timeline, stump speech, unclaimed angles, receptiveness signal, and a specific pitch angle.
argument-hint: "[guest-name] [anchor-fact]"
---

# Guest Circuit — Podcast-Appearance Research for Booking

Before you pitch a prospective guest, answer two questions. Where have they already podcasted? And what has nobody asked them yet?

The first gates the booking decision. Someone on ten shows this quarter is podcast-receptive and easy to book. Someone on zero shows may need a warmer path than a cold email. The second shapes the pitch. Inviting a guest to retell the story they told three shows ago wastes the slot and bores their audience overlap with yours.

This skill maps the circuit and produces a report you can act on: appearance timeline, the "stump speech" they repeat everywhere, the angles no show has claimed, and a one-paragraph pitch built on the gap.

---

**Invocation:** deliberately model-invocable — "research X before outreach" is the trigger. It spends web-search calls, so invoke consciously on big sweeps.

## When to Use

- "Map [person]'s podcast circuit" / "where has [person] podcasted?"
- "Research [person] before I send guest outreach"
- "Find an unclaimed angle for [person]"
- Before pitching a prospective guest, to gate the booking decision and shape the pitch

(See "When NOT to Use" below for the cases this skill is wrong for.)

---

## Step 1: Disambiguate

Input: $ARGUMENTS (guest name, plus an anchor fact if given).

Names collide. Before any search, confirm one anchor fact: company, role, or a known piece of work (book, project, paper).

- If the user provided an anchor ("Jane Doe, CTO at Acme"), proceed.
- If the user gave only a name, ask. Do not guess and do not search yet. A sweep on the wrong Jane Doe produces a confident, useless report.

Use the anchor to filter every result in later steps. A hit that cannot be tied to the anchor goes in "could not verify."

---

## Step 2: Appearance Sweep

Three source modalities. Run them as parallel subagents in a single tool-call batch (prompt templates in `patterns/subagent-prompts.md`). If subagents are unavailable, run the modalities sequentially in the same order. If web access is unavailable entirely, stop and say the sweep cannot run — never populate the timeline from model memory.

### 2a. Podcast Index (canonical source, when configured)

Requires the [podcastindex-mcp](https://github.com/conorbronsdon/podcastindex-mcp) server. Tool names as exposed by that server:

- `search_by_person` with `q: "Full Name"`, `max: 50`, `fulltext: true` — episodes across all indexed podcasts where the person appeared.
- `podcast_by_feed_id` with `id: <feedId>` — show metadata for each hit worth keeping: episode count, categories, last update. This is the cheap audience signal.
- `episodes_by_feed_id` with `id: <feedId>` — only if you need surrounding episodes from one show (e.g. to check whether the person appeared more than once).

Caveats:
- `search_by_person` matches hosts and description mentions, not just guests. Filter with concrete markers, not vibes. Guest markers: interview framing in the title or description ("with [Name]", "featuring", "[Name] on ...", "joins us", "our guest"). Host marker: the same name across most of the feed's episodes (spot-check with `episodes_by_feed_id`) or in the feed's author field; exclude those. Mention-only: the name appears but the episode's guest is someone else; exclude. If the markers are ambiguous, fetch the episode page; if it still cannot be settled, it is a lead for the "could not verify" list, not an appearance.
- `datePublished` fields are Unix timestamps. Convert before reporting.
- If the podcastindex tools are not configured, skip this modality, fall back to web search, and say so in the report's sources section ("Podcast Index not consulted").

### 2b. Web search

WebSearch queries, run all of them:
- `"[name]" podcast interview`
- `"[name]" "[company]" podcast episode`
- `"[name]" podcast guest`
- `site:youtube.com "[name]" podcast OR interview` — many appearances are YouTube-only and never reach podcast indexes.

YouTube caveat: a `youtu.be/...` short link redirects to `youtube.com/watch?v=...`, and the watch page often returns only the site nav/footer when fetched as plain HTML — no description, no transcript. Do not let that silently drop a real hit. When a YouTube URL is the only evidence, confirm the appearance from the show's own site or show-notes page instead; if no other page exists and the video page won't yield a description, the hit goes in "could not verify," not the timeline.

### 2c. Their own trail

Guests promote their own appearances. Check:
- A dedicated appearances index. Many prolific guests (especially technical ones) maintain a literal page or blog tag listing every podcast they've been on — search `"[name]" podcast appearances` and check their site for a `/podcasts`, `/press`, `/now`, or tag page. When it exists it collapses most of the sweep into one fetch: it gives you dated, linked entries straight from the source. Treat it as the timeline's source of record, then spot-check individual entries against each show's own page rather than re-deriving the whole list.
- Personal site or company bio: press, speaking, or media page.
- LinkedIn and X posts (search `"[name]" site:linkedin.com podcast` if no direct access).
- Their newsletter or blog, which often links appearances.

### Recording appearances

For every appearance, capture: show name, episode title, publish date, link, and an audience signal if it is cheap to get (show episode count, known network, YouTube view count on the episode). Do not deep-research show size. A rough signal is enough.

Dedupe across modalities by episode link or show + title. Keep the best-sourced entry.

---

## Step 3: Content Map

Take the 3-5 most recent or most prominent appearances, preferring those from the last 18 months. Older episodes stay in the timeline but say little about the current stump speech; people retire stories. For each, fetch the episode page or show notes. Show notes suffice. Do NOT fetch or summarize full transcripts; that is slow and the notes already list topics.

Extract:
- **Topics covered** per episode.
- **Repeated stories** — anecdotes, origin stories, or claims that appear across multiple shows. This is the stump speech. Your show should not re-ask it.

---

## Step 4: The Circuit Report

Write the report to `circuit/{name-slug}-{YYYY-MM-DD}.md` (or the user's stated location) and show the Appearance Timeline and Suggested Pitch Angle inline for review. Use this format:

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
no visible circuit (in indexed sources; see honesty rule 4). One sentence
on what that means for outreach.]

## Suggested Pitch Angle
[One paragraph. Specific. Names the unclaimed angle, why this guest is the
right person for it, and why your show is the right venue. Not "discuss AI."]

## Sources
- [URL] (fetched [date]) — what it verified
```

Derive unclaimed angles by contrast. "Recent work" means, concretely: papers (arXiv, Google Scholar), blog and newsletter posts, conference talks (event sites, YouTube), product launches and changelogs, and substantive social threads, all from roughly the last 12 months. The own-trail sweep gathers most of this. List what that work covers, then subtract what the circuit already covered. The remainder is the pitch material. Cite the specific work item behind each angle. If you cannot find their recent work, say so rather than inventing angles.

Receptiveness cadence is computed from the last 12 months. Treat appearances older than 18 months as weak signal: they prove the person has podcasted, not that they currently say yes.

---

## Honesty Rules

These are hard requirements, not style preferences:

1. **Every appearance must be backed by a fetched page.** Model memory invents podcasts and misdates real ones. If you did not fetch a page (or get an index record) confirming the appearance, it does not go in the timeline.
2. **"Could not verify" is a real bucket.** A search snippet that mentions the person and a show is a lead, not a confirmed appearance. List unconfirmed leads separately and label them.
3. **Date everything.** Appearances, sources, and the report itself.
4. **A thin circuit is a finding, not a failure. But bound the claim by your coverage.** Podcast Index misses YouTube-only shows and many small feeds; web search misses badly titled episodes. Zero findings means "no appearances found in indexed and searchable sources," never "they have not done podcasts." The inference runs one way: a busy circuit proves receptiveness; an empty one does not prove its absence. Report a thin circuit plainly with that coverage caveat, then pivot: map their writing, conference talks, and interviews in text media instead. That report is just as useful for outreach; it changes the pitch from "another podcast" to "your first real podcast conversation about X."

---

## When NOT to Use

- The guest is already booked and you need interview prep. Use a talk-track or research workflow instead. This skill is for the booking decision and the pitch.
- You only need contact info or a bio. That is a single web search, not a circuit sweep.

---

## Worked example

[`examples/simon-willison-circuit.md`](examples/simon-willison-circuit.md) is a real
run of this skill against a fully public figure (Simon Willison — creator of
Datasette, co-creator of Django). It shows the full output shape: a 20-plus-entry
appearance timeline with verified URLs and dates, the repeated stump speech to
avoid, unclaimed angles derived from his current work, a receptiveness read, and a
specific pitch angle for a hypothetical AI-engineering podcast. It also exercises
the Step 2a degradation path — Podcast Index was not configured in that run, so the
sweep fell back to web search and the report says so.

## Cross-references

- `patterns/subagent-prompts.md` — paste-ready prompts for the three sweep modalities.
- `examples/simon-willison-circuit.md` — a real, fully-cited circuit report.
- [podcastindex-mcp](https://github.com/conorbronsdon/podcastindex-mcp) — the MCP server providing `search_by_person` and the other Podcast Index tools.
