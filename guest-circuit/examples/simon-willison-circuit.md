# Circuit Report: Simon Willison (creator of Datasette, co-creator of Django) — 2026-06-11

> **Worked example.** This is a real run of the guest-circuit skill, executed as
> written against a fully public figure (chosen because his entire circuit is
> public and he is not in any private booking pipeline). The Podcast Index
> modality (Step 2a) was **not available** in this run — the documented
> degradation path was exercised: skip it, fall back to web search, and say so in
> Sources. Everything below is backed by a fetched page; search-only leads are in
> the "Could not verify" bucket. The skill writes to `circuit/{slug}-{date}.md`
> by default; this copy lives in `examples/` as a reference artifact.
>
> **Anchor fact used for disambiguation (Step 1):** creator of Datasette,
> co-creator of Django, author of the `llm` CLI, blogs at simonwillison.net.
> Every hit below was tied to that anchor.

## Appearance Timeline

Newest first. "Audience signal" is the cheap-to-get signal only (network, format);
no deep audience research was done, per the skill.

| Date | Show | Episode | Link | Audience signal |
|------|------|---------|------|-----------------|
| 2026-05-06 | High Leverage (Heavybit) | Ep. #9 — The AI Coding Paradigm Shift | [heavybit.com](https://www.heavybit.com/library/podcasts/high-leverage/ep-9-the-ai-coding-paradigm-shift-with-simon-willison) | Heavybit dev-tools network |
| 2026-04-02 | Lenny's Podcast | An AI state of the union: we've passed the inflection point, dark factories are coming | [lennysnewsletter.com](https://www.lennysnewsletter.com/p/an-ai-state-of-the-union) · [YouTube](https://www.youtube.com/watch?v=wc8FBhQtdsA) | Large PM/founder audience; one of the bigger product podcasts |
| 2025-11-26 | Data Renegades (Heavybit) | Ep. #2 — Data Journalism Unleashed | [heavybit.com](https://www.heavybit.com/library/podcasts/data-renegades/ep-2-data-journalism-unleashed-with-simon-willison) | Heavybit data network |
| 2025-08-29 | Talk Python | #518 — Celebrating Django's 20th Birthday With Its Creators | [talkpython.fm](https://talkpython.fm/episodes/show/518/celebrating-djangos-20th-birthday-with-its-creators) | Long-running Python show; panel format |
| 2025-08-13 | Screaming in the Cloud | AI's Security Crisis: Why Your Assistant Might Betray You | [lastweekinaws.com](https://www.lastweekinaws.com/podcast/screaming-in-the-cloud/ai-s-security-crisis-why-your-assistant-might-betray-you/) | Established cloud/infra show |
| 2025-08-11 | Talking Postgres | AI for data engineers with Simon Willison | [talkingpostgres.com](https://talkingpostgres.com/episodes/ai-for-data-engineers-with-simon-willison) | Postgres/data-eng niche |
| 2025-07-11 | Generationship (Heavybit) | Ep. #39 — I Coined Prompt Injection | [heavybit.com](https://www.heavybit.com/library/podcasts/generationship/ep-39-simon-willison-i-coined-prompt-injection) · [YouTube](https://www.youtube.com/watch?v=_bW58o8l0os) | Heavybit AI network |
| 2025-04-01 | Half Stack Data Science | Programming with AI, with Simon Willison | [halfstackdatascience.com](https://halfstackdatascience.com/s4e2-programming-with-ai-with-simon-willison) | Data-science niche |
| 2025-03-02 | Accessibility + Gen AI | Ep. 6 — Simon Willison, Datasette | [simplecast](https://accessibility-and-gen-ai.simplecast.com/episodes/ep-6-simon-willison-datasette) · [YouTube](https://www.youtube.com/watch?v=zoxpEM6TLEU) | Niche accessibility show |
| 2025-01-24 | Real Python | #236 — Using LLMs for Python Development | [realpython.com](https://realpython.com/podcasts/rpp/236/) | Large Python audience |
| 2025-01-14 | Techmeme Ride Home | Simon Willison and swyx tell us where AI is in 2025 (Latent Space crossover) | [ridehome.info](https://www.ridehome.info/show/techmeme-ride-home/bns-simon-willison-and-swyx-tell-us-where-ai-is-in-2025/) | Large daily tech-news audience |
| 2024-12-02 | Around the Prompt | The Future of Open Source and AI | [YouTube](https://www.youtube.com/watch?v=rLcKbvmegag) | Niche AI show |
| 2024-09-25 | The Pragmatic Engineer | AI tools for software engineers, without the hype | [pragmaticengineer.com](https://newsletter.pragmaticengineer.com/p/ai-tools-for-software-engineers-simon-willison) · [YouTube](https://www.youtube.com/watch?v=uRuLgar5XZw) | Very large eng audience; was that podcast's launch episode |
| 2024-09-20 | TWIML AI | Supercharging Developer Productivity with ChatGPT and Claude | [twimlai.com](https://twimlai.com/podcast/twimlai/supercharging-developer-productivity-with-chatgpt-and-claude/) | Long-running ML show |
| 2024-09-10 | Software Misadventures | LLMs are like your weird, over-confident intern | [softwaremisadventures.com](https://softwaremisadventures.com/p/simon-willison-llm-weird-intern) | Eng-culture niche |
| 2024-01-24 | Django Chat | Datasette, LLMs, and Django | [djangochat.com](https://djangochat.com/episodes/datasette-llms-and-django-simon-willison) | Django niche |
| 2024-01-17 | Oxide and Friends | Talking about Open Source LLMs | [oxide.computer](https://oxide.computer/podcasts/oxide-and-friends/1692510) | Infra/hardware niche |
| 2023-12-05 | Newsroom Robots | How Datasette Helps With Investigative Reporting | [newsroomrobots.com](https://www.newsroomrobots.com/p/how-datasette-helps-with-investigative) | Data-journalism niche |
| 2023-11-08 | Latent Space | AGI is Being Achieved Incrementally (OpenAI DevDay) | [latent.space](https://www.latent.space/p/devday) | Large AI-engineering audience |
| 2023-09-29 | Rooftop Ruby | Ep. 26 — Large Language Models | [rooftopruby.com](https://www.rooftopruby.com/2108545/13676934-26-large-language-models-with-simon-willison) | Ruby niche |
| 2023-07-10 | Latent Space | Code Interpreter == GPT 4.5 | [latent.space](https://www.latent.space/p/code-interpreter) | Large AI-engineering audience |

Source of record for the timeline: Simon's own [podcast-appearances tag](https://simonwillison.net/tags/podcast-appearances/), which he curates and which links each appearance. Individual entries were spot-checked against the shows' own pages (see Sources).

### Could not verify (leads, not appearances)

- **News Nation — "Talking AI and jobs with Natasha Zouves" (2025-05-30).** Listed on his tag page but framed as a TV/video news segment, not a podcast, and no podcast page was fetched. Excluded from the timeline as a podcast appearance.
- **Ars Live / Ars Technica (2024-11-19), RedMonk Conversation (2023-12-20).** Video/livestream conversations on his tag page, not standard podcast feeds; left out of the podcast timeline.
- **YouTube watch pages frequently returned only the site footer/nav when fetched as HTML** (no description or transcript). Where a YouTube link is the *only* evidence, the appearance was confirmed via the show's own site instead; the Lenny's YouTube link confirmed via the newsletter page and Simon's own write-up.

## Stump Speech (do not re-ask)

These are the stories/claims Simon repeats across the recent circuit. A new show should not re-run them.

- **The "lethal trifecta" + prompt injection.** Private data access + exposure to untrusted content + an exfiltration path = the core AI-agent security failure. He coined "prompt injection," and tells the GitHub-MCP-public-issue exfiltration story. Covered on Screaming in the Cloud (2025-08), Generationship (titled "I Coined Prompt Injection," 2025-07), and recurs in the Lenny's and High Leverage 2026 episodes. Saturated.
- **The November 2025 inflection point.** GPT-5.1 / Claude Opus 4.5 made coding agents reliable enough for daily production use; "the code almost all of the time does what you told it to do." Covered on High Leverage (2026-05) and Lenny's (2026-04). Saturated.
- **Vibe coding vs. agentic engineering.** "Vibe coding for yourself, go wild; pause before you ship to others." The distinction between non-programmers prompting and experienced engineers supervising agents. High Leverage + Lenny's. Saturated.
- **Dark factories.** The end-state where "nobody writes the code, and eventually nobody reads it." Lenny's headline; reprised on High Leverage. Fresh-ish (2026) but now his signature line — do not make it the whole episode.
- **"LLMs are like an over-confident intern."** His standard framing for how to manage model output. Software Misadventures episode is literally titled this; recurs. Saturated.

## Unclaimed Angles

Derived by contrast: what his *recent work* (last ~6 months on simonwillison.net) covers, minus what the circuit already covered. Each cites the work behind it.

- **The economics of agentic coding inside a company — token budgets, not capability.** His recent blog work tracks the cost story concretely (e.g. the "Uber capped token spend at $1,500/month per tool after burning the budget in four months" anecdote, simonwillison.net, 2026). The circuit covers *can* agents code; nobody has done a focused episode on *what it costs to run them at org scale and how teams are rationing tokens.* That's a sharper, more operator-relevant conversation than "AI can code now."
- **Building agents that touch a database safely — the Datasette Agent / approval-flow design.** His current shipping work is Datasette Agent and `datasette-agent-micropython` (agentic SQL with user-approval flows, sandboxed Python via WebAssembly), per recent alpha releases on his blog (June 2026). The circuit talks about agent *risk* abstractly (lethal trifecta); no show has walked through his *concrete defensive design pattern* — approval gates + WASM sandboxing — as a how-to. This is the constructive flip side of the security stump speech and it's genuinely unclaimed.
- **"There is no feedback loop connecting AI enthusiasts with skeptics" inside teams.** A throwaway line in his recent writing that no episode has unpacked: the org-dynamics problem of AI adoption, not the tech. A people/process episode, not a tools episode.
- **The middle-career-engineer squeeze, as its own episode.** He raises it on Lenny's as one point among many ("mid-level engineers face the greatest disruption; seniors amplified, juniors' onboarding solved"). It deserves a dedicated conversation and hasn't gotten one.

## Receptiveness Signal

**Highly receptive.** Cadence in the last 12 months (2025-06 → 2026-06): roughly 8 verified podcast appearances, including two in the most recent ~10 weeks (High Leverage 2026-05, Lenny's 2026-04). He also *maintains a public index of his own appearances* — a strong tell that he treats podcasting as part of his work and will likely say yes to a well-targeted ask. The bar is the angle, not his willingness: a generic "come talk about AI coding" invitation competes with a packed, recent circuit and will read as redundant.

## Suggested Pitch Angle

Pitch the **constructive security build, not the warning.** Every recent show has had Simon deliver the lethal-trifecta warning and the "agents can code now" headline; none has had him sit down and walk through *how he actually builds an agent that can touch production data without getting exfiltrated* — the Datasette Agent approval-flow + WebAssembly-sandbox pattern he's shipping right now. For an AI-engineering podcast whose audience builds these systems, that's the highest-value hour available: it pairs his signature credibility (he coined prompt injection) with new, shippable, never-podcasted material (his current code), and it gives listeners a defensive design pattern they can copy on Monday rather than another reason to be scared. Secondary hook if you want range: the token-economics-at-org-scale conversation, which is operator-relevant and also unclaimed. Lead with the build; it's the gap.

## Sources

All fetched 2026-06-11.

- https://simonwillison.net/tags/podcast-appearances/ — Simon's curated appearance index; timeline source of record (dates + links for all entries).
- https://simonwillison.net/ — recent-work feed; basis for unclaimed angles (Datasette Agent, micropython-wasm sandboxing, token-budget anecdotes, enthusiast/skeptic line).
- https://simonwillison.net/2026/Apr/2/lennys-podcast/ — his own summary of the Lenny's talking points; confirmed the dark-factory / agentic-engineering / inflection-point stump speech.
- https://www.heavybit.com/library/podcasts/high-leverage/ep-9-the-ai-coding-paradigm-shift-with-simon-willison — confirmed High Leverage appearance (2026-05) and its topics.
- https://www.lastweekinaws.com/podcast/screaming-in-the-cloud/ai-s-security-crisis-why-your-assistant-might-betray-you/ — confirmed Screaming in the Cloud appearance (2025-08) and the lethal-trifecta / prompt-injection stump speech.
- https://talkpython.fm/episodes/show/518/celebrating-djangos-20th-birthday-with-its-creators — confirmed Talk Python Django-20th appearance (2025-08); showed his Django-history register vs. his LLM register.
- https://www.lennysnewsletter.com/p/an-ai-state-of-the-union — confirmed Lenny's episode (2026-04) title and topics.
- Web search (no Podcast Index): **Podcast Index was not consulted** — the podcastindex-mcp server was not configured in this run, so Step 2a was skipped and the web + own-trail modalities carried the sweep. A Podcast Index pass would mainly add machine-readable feed metadata and might surface small feeds the web search missed; it would not change the headline findings.
