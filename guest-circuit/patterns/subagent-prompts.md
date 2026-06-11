# Sweep Subagent Prompts — Guest Circuit

Three paste-ready templates, one per source modality. Fill in the bracketed slots, then spawn all three in a single tool-call batch so they run in parallel.

Every prompt:
- Carries the anchor fact (company/role/work) so the subagent filters out name collisions.
- Requires a verification URL per appearance. No fetched page, no entry.
- Caps report length at ~400 words plus the table.

---

## 1. Podcast Index Sweep

Use when: the podcastindex-mcp server is configured (tools like `search_by_person` are available). Skip this subagent entirely if it is not; do not let it fall back to memory.

```
You are researching the podcast appearances of [NAME] ([ANCHOR FACT: role,
company, or known work]).

Use the Podcast Index MCP tools:
1. search_by_person with q: "[NAME]", max: 50, fulltext: true.
2. For each plausible hit, confirm it is THIS person: the anchor fact must
   appear in the episode title or description. A matching subject area alone
   is not confirmation; that hit goes in the ambiguous list.
3. Confirm they are a GUEST, not the host and not merely mentioned. Guest
   markers: "with [NAME]", "featuring", "[NAME] on ...", "joins us", "our
   guest". Host marker: [NAME] across most of the feed's episodes (spot-check
   with episodes_by_feed_id) or in the feed author field; exclude. Mention-only
   (the episode's guest is someone else): exclude.
4. For each confirmed show, call podcast_by_feed_id with the feedId to get
   episode count and categories as a rough audience signal.

datePublished values are Unix timestamps. Convert to YYYY-MM-DD.

Return (cap ~400 words + table):
1. Table: date | show | episode title | link | audience signal.
2. Ambiguous hits you excluded and why (one line each).
3. One line: total confirmed appearances and date range.

Rules: only include entries returned by the index. Do not add podcasts from
memory. If the tools are unavailable or return nothing, say exactly that.
```

---

## 2. Web Sweep

Use always.

```
You are researching the podcast appearances of [NAME] ([ANCHOR FACT]).

Run ALL of these web searches:
- "[NAME]" podcast interview
- "[NAME]" "[COMPANY]" podcast episode
- "[NAME]" podcast guest
- site:youtube.com "[NAME]" podcast OR interview

For each candidate appearance, FETCH the episode page or video page to
confirm: it is this person (anchor fact), they are a guest, and the publish
date. Capture an audience signal if visible on the page (YouTube view count,
known network) without extra research.

Return (cap ~400 words + table):
1. Table: date | show | episode title | link | audience signal.
2. "Could not verify" list: leads where a snippet suggested an appearance but
   the fetched page did not confirm it (or could not be fetched).
3. One line: total confirmed appearances and date range.

Rules: an appearance only counts if you fetched a page confirming it. Search
snippets alone go in the could-not-verify list. Do not invent podcasts from
memory.
```

---

## 3. Own-Trail Sweep

Use always. Guests promote their own appearances; this catches what indexes and search miss, and feeds the unclaimed-angles analysis.

```
You are researching [NAME] ([ANCHOR FACT]) through their own channels.

Check, fetching each page you cite:
1. Their personal or company site: press, speaking, media, or about page.
2. Their recent work, roughly the last 12 months: blog and newsletter posts,
   papers (arXiv/Scholar), conference talks (event sites, YouTube), product
   launches or changelogs. List the 3-5 most recent items with dates.
3. Public social posts if reachable (search "[NAME]" site:linkedin.com
   podcast, and their X profile) for appearance announcements and substantive
   threads about their work.

Return (cap ~400 words + table):
1. Table of self-announced podcast appearances: date | show | episode | link.
2. Recent-work list: what they are currently building/writing about, with
   dates and links. This feeds the unclaimed-angles section, so be specific
   about topics.
3. One line: how actively they self-promote appearances (signal for
   receptiveness).

Rules: cite a fetched URL for every claim. If their site has no press page
and their socials are quiet, report that plainly.
```
