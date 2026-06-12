# SSOT DISCOVER — 2026-06-11 (cot-production)

Real discover-mode run against the repo the skill was designed from. CLAUDE.md's
"Single Source of Truth" section served as the canonical-file oracle. Sibling repo
`../cot-sponsor-page` was pulled fresh before checking (it had only untracked files,
which don't block the pull). Some internal values are masked per house rules; the
fact entries are kept.

## LIVE DRIFT FOUND (surfaced first — this is the actionable part)

1. **episode-count — pipeline convention bug, not a stale edit.**
   Canonical `outputs/episodes/README.md` says **62** (excludes trailer, per repo
   convention). `docs/data.json` says `episodes_published: 63` and the live sponsor
   page shows **63+**. Root cause: `scripts/podcast-metrics.py` computes both
   `published_episodes` (trailer-inclusive) and `published_episodes_no_trailer`,
   writes the no-trailer count to the README, but writes the trailer-INCLUSIVE
   count into data.json's `episodes_published` (the `build` dict near the
   `write_data_json` section). The sponsor-page sync consumes data.json, so the
   public page overstates by one. **Fix lands in the script** (auto-generated-copies
   rule): use `published_episodes_no_trailer` for the exported stat.

2. **newsletter-subscribers — hand-copy drift in host-context.md.**
   Canonical `docs/data.json` says **1,000**; `host-context.md` ("Audience & Reach")
   still says **870+** — a value from roughly three months earlier. Proposed edit:
   `- **Substack:** 870+ subscribers` → `+ **Substack:** 1,000+ subscribers`.

3. **linkedin-followers — drift where the PROPOSED CANONICAL is the stale side.**
   `host-context.md` (named by CLAUDE.md for host background) says **10,000+**;
   the sponsor page says **12,000+**. Follower counts are effectively monotonic, so
   the higher copy is almost certainly fresher than the canonical. Do NOT "fix" the
   sponsor page down to 10,000+; confirm the live value and update host-context.md.
   (This run is what added the stale-canonical guidance to the skill.)

4. **sponsor pricing — stale tier table inside a generator template.**
   Live sponsor page (canonical for pricing — `sponsorship/media-kit.md` explicitly
   delegates the media kit to the page): Starter 4 eps at $450/ep, 8 eps at $400/ep,
   Presenting 12 eps at $400/ep ($4,800 total; the Cisco package draft matches).
   `skills/cot-sponsor-package/SKILL.md` still embeds the PREVIOUS tier table —
   old tier names and old per-episode rates (values masked: `<redacted — internal
   historical rates>`). This is the worst kind of copy: a template, so every newly
   generated sponsor package quotes superseded pricing. Similar old-rate tables in
   `sponsorship/pricing-strategy.md` and `sponsorship/sponsor-package-gtc-2026.md`
   are labeled historical/blueprint and were left out of the manifest.

5. **all-time-reach — in tolerance, but shows sync lag (pipeline health).**
   Canonical `docs/data.json`: **156,703**. README headline: 156,000+ (script-floored,
   consistent). Sponsor page: **155K+** — two days behind because the page only
   re-syncs on deploy. Not hand-drift; tracked with `rounding:` transforms so check
   mode flags real lag without false-positives on the rounding itself.

## PROPOSED FACTS (8)

- **episode-count**: 62 — canonical: `outputs/episodes/README.md` (CLAUDE.md names it SSOT)
  copies: `docs/data.json` (auto-gen), `../cot-sponsor-page/index.html` (auto-synced, 3 occurrences)
- **all-time-reach**: 156,703 — canonical: `docs/data.json` (CLAUDE.md: AUTO-GENERATED, never hand-edit)
  copies: `outputs/episodes/README.md` (floor-1000), `../cot-sponsor-page/index.html` (floor-1000-as-K)
- **youtube-subscribers**: 2,860 — canonical: `docs/data.json` (dashboard source per media-kit.md)
  copies: sponsor page stat (auto-synced, floor-10) + hand-written meta description + JSON-LD
- **newsletter-subscribers**: 1,000 — canonical: `docs/data.json`
  copies: sponsor page stat grid + meta/JSON-LD (floor-100), `host-context.md` (DRIFTED, 870+)
- **linkedin-followers**: 10,000+ vs 12,000+ — canonical guess: `host-context.md` (CLAUDE.md
  names it for host background) — DRIFTED, canonical suspected stale (monotonic metric)
- **sponsor-price-starter**: $450/ep — canonical: `../cot-sponsor-page/index.html` (cross-repo
  canonical; media-kit.md delegates to the live page) — copy in `skills/cot-sponsor-package/SKILL.md` STALE
- **sponsor-price-presenting**: $400/ep ($4,800/12) — same canonical — copy in
  `skills/cot-sponsor-package/SKILL.md` STALE
- **listeners-per-episode**: 1,000+ — canonical: sponsor page stat grid; copies are the
  hand-written meta description and JSON-LD in the same file

## DISCARDED (low confidence / out of scope)

- `analytics/goals.md` snapshot table (episodes 61, YT subs 2,790, etc.) — append-only
  dated snapshot series, not copies; a "stale" latest column just means no snapshot has
  run since the value moved. CLAUDE.md lists goals.md as an episode-count copy that
  "must stay in sync," but its occurrences are historical records — excluded per the
  facts-that-legitimately-differ rule. Worth a human decision.
- `business-plan.md` YouTube subs — CLAUDE.md warns this is a common drift point, but
  the file currently contains only goal targets and dated milestones, no live copy.
  Already deduplicated; nothing to track.
- Per-episode download metrics — sponsor-sensitive by house policy; excluded from the
  manifest and this report entirely.
- Apple/Spotify review counts ("5.0 across 144+ reviews"), 58% US audience — single
  surface (sponsor page only).
- Galileo YouTube views component (~92,460) — appears twice in one README but has its
  own refresh script and documented floor; the headline reach fact already covers the
  aggregate. Borderline; revisit if it drifts.
- `production/drafts/listicle-pitches-2026-05-16.md`, session notes, dated sponsor
  package drafts (GTC, Cisco) — point-in-time outreach artifacts, not living copies.
- Bare years, dependency versions, target tables (8,000 subs by Dec 2026 etc. are
  goals, not facts).

Draft `.ssot.yaml` in `proposed-ssot.yaml`. Edit canonical assignments (especially
linkedin-followers), then approve to write. Not written to cot-production — this run
was read-only.

8 facts proposed; 4 live drifts + 1 pipeline-lag observation found before the manifest exists.
