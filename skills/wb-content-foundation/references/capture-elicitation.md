# Phase 6 — Capture elicitation reference

> Loaded when running phase 6 (wild content capture). The full per-category elicitation prompt catalog, the fresh-generation prompts for thin-content users, and the failure-mode reframes. Source of truth: `${CLAUDE_PLUGIN_ROOT}/phase-contracts/06-wild-content-capture.md` + `Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md`.

## The 6-category elicitation routine

Walk the user through each category with `AskUserQuestion`. Capture is greedy — log everything; reject nothing at phase 6 (phase 7 audits, phases 13-16 curate).

### 1. Existing online presence

Ask what exists and where:
- Current site (URL, last-updated, what to keep vs discard) — WebFetch the pages the user authorizes; save to `inbox/existing-site/`.
- Social bios — LinkedIn / Instagram / Twitter-X / Bluesky / Mastodon "about" text. Pull each; save to `inbox/social/`.
- GitHub README (technical practitioners), portfolio platforms (Dribbble / Behance / Notion site / Webflow CMS exports).

### 2. Written sources

- Google Docs / Notion pages (drafts about the project / offering / philosophy).
- Prior site exports (HTML download / WordPress export / Webflow JSON).
- Blog posts (own or guest), newsletter archives (Substack / Mailchimp / Beehiiv / Buttondown).
- Books / excerpts / talks / podcast transcripts (creators); academic papers (if relevant).
- Client deliverable letters (PDF/DOCX — often contain reusable framing about what the user does → recommend `document-skills:pdf` for extraction).

### 3. Visual sources

- Logo files (per `entity.existing_assets.logo`), photography (cleared portfolios, on-disk libraries, Instagram-extracted, photographer deliveries).
- Screenshots of prior work, sketchbook scans, brand/mood boards.

### 4. Testimonials / social proof

- LinkedIn recommendations, client thank-you emails, Twitter/X mentions, podcast clips, conference recordings, Slack screenshots (with permission), case-study PDFs.

### 5. Email + correspondence

- Pinned client emails — they contain the *language clients used* to describe the value (gold for phase-16 copywriting). Ask for *examples* (5-10 emails with reusable phrasing), not a bulk inbox export.

### 6. Conversational / fresh-generated

- For thin-content users. Voice notes + freewriting (see below). Output → `inbox/voice-notes/{topic}-{date}.m4a` / `inbox/freewrites/{topic}-{date}.md`.

Each item records: original location, copy-path in `inbox/`, format, provenance (own-creation / client-supplied / commissioned-photographer / AI-generated / scraped-with-permission), one-line description, `use_for` hint (which downstream phase consumes it).

## Fresh-generation prompts ("I have nothing")

When the user claims emptiness, run the elicitation pass first (almost always 2-4 items surface):

> *"Let's walk through five categories briefly — even one item per category is enough. (1) Where do people find you online today? Even one URL. (2) Have you ever written anything about what you do — a LinkedIn post, an email to a friend, a paragraph in your phone's notes? (3) Do you have any photos taken of you for work — even a single LinkedIn headshot? (4) Has anyone ever sent you a positive message about your work? (5) Has a client ever sent an email describing what they liked about working with you?"*

If genuinely empty, shift to fresh-generation. The methodology (Peter Elbow's freewriting, 1973 — write continuously without editing, judging, or correcting; verified via WebSearch 2026-05-18):

- **Voice-note prompt:** *"Record a 2-minute voice note about why you started this — talk to yourself, no editing. Use whatever language you think in most comfortably (the technique works best in your home language)."* → `inbox/voice-notes/`. Transcription deferred to phase 13/16, not phase 6.
- **Freewriting prompt:** *"Write 200 badly-written words answering: 'when someone like Maya is reading my site at 11pm on a Sunday, what is true about her life right after she leaves the site?' No editing. If you get stuck, literally write 'I don't know what to say' and keep going — that's a valid start (Elbow's method)."* → `inbox/freewrites/`.
- **Focused freewrite:** put a specific question/fragment at the top; the user freewrites around it for a fixed duration; thoughts orbit the topic, straying is fine.

The discipline: the agent does NOT let the user skip phase 6 by claiming emptiness unverified. Capture happens — either by surfacing what exists or by generating fresh.

## Failure-mode reframes

| Situation | Reframe |
|---|---|
| **Too much** ("12 yrs LinkedIn, 60k-word blog, 400 client emails") | Don't extract everything. Capture top-level inventory ("LinkedIn — 12 yrs; Substack — 80 issues; emails — 400"). Then representative samples (10 proud posts, 5 rereadable issues, 10 reusable-language emails). Full archive = `status: archived-available`; samples = `status: inboxed`. |
| **Promised-but-not-sent** ("I'll send the logo later") | Record `status: pending` + target date. Flag: phase 7 can't audit pending items; if it doesn't arrive by phase 7 that phase pauses or proceeds with a placeholder revisited later. |
| **Privacy on correspondence** ("client emails are private") | Don't share the emails — share the *language patterns*. "Read 3 emails to yourself, type me 3-5 phrases clients used." → `inbox/correspondence-extracts.md`. Copy seeds without privacy violation. |
| **1,200-page old WordPress** | Don't download all. Inventory top-level architecture (categories, hub pages, most-trafficked per analytics). Full archive stays at old URL; phase 16 surfaces best-20 for voicing; rest become redirects. |
| **Unprocessable formats** (PSD, free-tier Figma, 4GB Drive video) | Record asset + format + access path; defer processing to the consuming phase (7 audits, 17 visual seed, 6.5 ingests Figma, 8 decides on video). |
| **6.5 fires mid-phase-6** (user pastes an artifact) | Expected — 6.5 is re-runnable. Call out to 6.5 to ingest, then return to phase-6 capture mode. 6.5 does NOT advance to phase 7. Surface what 6.5 did, then "what else do you have?" |
| **Dual-language, one language only** | Record: inbox-ed German content seeds DE pages; phase 16 chooses translation pattern (DESIGN-i18n.md Pattern 1 inline / Pattern 2 translator handoff). Phase 6 just captures. |
| **Captured content contradicts phase-5 voice** | Flag, don't refuse. Inbox it as raw material (phase 16 revoices). Or surface: "is this your real voice and phase 5 aspirational?" — sometimes a genuine voice re-think. |

## Gating

The single refusal: never flip `INVENTORY.md` frontmatter `status:` from `capture-in-progress` to `capture-complete` without explicit user confirmation that there is nothing else. Override path: the user can advance to phase 7 with a thin inventory; the agent flags the cost (phase 13-16 will hit empty-content-slots; fresh content written under phase-16 pressure). Items located only in the user's head get the "promised items stall phase 7" surface.
