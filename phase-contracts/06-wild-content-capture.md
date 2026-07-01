---
phase: 6
name: Wild unstructured content capture
group: content-foundation
pipeline_section: content-foundation
skill: wb-content-foundation
prev_phase: 5
next_phase: 7
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - DESIGN-phase-contracts.md
  - DESIGN-architecture.md
  - DESIGN-project-scaffold.md
  - DESIGN-content-layers.md
---

# Phase 6 — Wild unstructured content capture

> Dump everything the user already has. The opening phase of content-foundation; the permissive, inclusive capture phase that gathers raw material before any structural decisions get imposed on it. The discipline of phase 6 is *not refusing* — capture is greedy by design.

## Mission

The user almost always has more content than they remember. Google docs, Notion pages, prior-site exports, social-media bios, customer testimonials, photos, videos, sketches in their phone's notes, emails they've sent that contain copy worth lifting, voice notes, slide decks, half-finished blog posts, screenshots of compliments people sent them. Phase 6 is the inventory phase: surface all of it, drop it into `.website-builder/inbox/`, log provenance, and produce an inventory the downstream content phases (13-16) compose from.

The agent does not curate during phase 6. Curation is phase 7 (asset audit — rights + quality), phase 13 (content per page — selection per page), phase 16 (copywriting — voicing + tightening). Phase 6 is the *capture* — bring it all in, even the things the user is unsure about, because surfacing them is the only way to know they exist.

The user with the worst phase 6 experience is the one who thinks they have nothing. The agent's job there is to elicit. Voice notes prompts ("talk for two minutes about why you started this — record on your phone and send the audio"), freewriting prompts ("answer this question in 200 words, badly, no editing — what do you want clients to feel after a project ships?"), inventory-recall prompts ("what did you tell the last person who asked what you do? Type that here as a starting point"). Phase 6 generates raw material when the user has none; aggregates raw material when the user has plenty.

## Entry conditions

Phase 5 is complete. `.website-builder/brand.yaml.voice` exists with description + attributes + NN4D + say/never-say + exemplars; the user has confirmed it. `current_phase: 6` is set.

The `.website-builder/inbox/` directory may have been seeded by phase 4 — the existing-assets inventory in `project.yaml.entity.existing_assets` is the starting point. Phase 6 expands from that seed: every asset named there is followed up on; new assets surface; the inventory ends much richer than it started.

For non-greenfield entry modes, prior artifacts already discovered (existing site, AI output, Figma file, Framer attempt) are inbox-ed during phase 6 — the artifact is the starting point of the capture. Phase 6.5 (artifact ingestion) is a peer phase that may interleave: if the user pastes an artifact mid-phase-6, the agent can call out to 6.5 to ingest it into structured state and then return to phase 6 capture-mode for the rest of the wild content.

## What Claude must establish

The work product is `.website-builder/inbox/INVENTORY.md` — a structured inventory of everything the user has, with provenance, current location, format, and a one-line description.

The agent walks the user through a content-source elicitation routine:

1. **Existing online presence** — current site (URL, last-updated, what to keep / discard), social media bios (LinkedIn / Instagram / Twitter-X / Bluesky / Mastodon — pull each "about" text), GitHub README (for technical practitioners), portfolio platforms (Dribbble / Behance / Notion site / Webflow CMS exports / etc.).

2. **Written sources** — Google Docs (any drafts about the project / the offering / the philosophy), Notion pages (workspace dumps that aren't private), prior site exports (HTML download / WordPress export / Webflow JSON export), blog posts (own or guest), newsletter archives (if the user has a Substack / Mailchimp / Beehiiv / Buttondown / personal mailer), books / book excerpts / talks / podcast transcripts (when the user is a creator), academic papers (if relevant), client deliverable letters (PDF / DOCX — often contain reusable framing about what the user does).

3. **Visual sources** — logo files (per `entity.existing_assets.logo`), photography (cleared portfolios, on-disk image libraries, Instagram-extracted photos, professional photographer deliveries), screenshots of prior work, sketchbook scans, brand boards / mood boards.

4. **Testimonials / social proof** — LinkedIn recommendations, client emails ("hey thanks for that work, here's what landed for us..."), Twitter/X mentions, podcast interview clips, conference talk recordings, Slack screenshots (with permission), case-study PDFs.

5. **Email + correspondence** — pinned emails from clients (often contain the *language* clients used to describe the value, which is gold for phase 16 copywriting). The agent asks for *examples*, not bulk export — the goal is to find the 5-10 emails that contain reusable phrasing, not to ingest an inbox.

6. **Conversational / fresh-generated** — when the user has thin existing content, the agent prompts voice-note recording + freewriting prompts (catalogued below in "Common failure modes"). Output goes directly into `inbox/` as `voice-notes/{topic}.m4a` or `freewrites/{topic}.md`.

For each item, the inventory records: original location (URL or file path), copy-path inside `inbox/`, format (markdown / docx / pdf / m4a / mp4 / jpg / png / svg / etc.), provenance (own-creation / client-supplied / commissioned-photographer / AI-generated / scraped-with-permission), one-line description, and a "use_for" hint (which downstream phase is most likely to consume this — phase 13 content brief, phase 15 section content, phase 16 copywriting, phase 17 design seed, etc.).

Output schema (`inbox/INVENTORY.md` is markdown with structured frontmatter + a table):

```markdown
---
type: inbox-inventory
captured_at: 2026-05-18T16:42:00Z
total_items: 47
status: capture-in-progress  # capture-in-progress | capture-complete
phase: 6
---

# Inbox inventory

## Existing online presence

| # | Source | Local path | Format | Provenance | Use for | Notes |
|---|---|---|---|---|---|---|
| 1 | https://old.example.com (existing site) | inbox/existing-site/scrape-2026-05-18.html | html | own-creation | phase-6.5 ingest | Last updated 2024-03 |
| 2 | LinkedIn About section | inbox/social/linkedin-about.md | md | own-creation | phase-16 copy seed | Current — 247 words |
| 3 | Instagram bio (@example) | inbox/social/instagram-bio.txt | txt | own-creation | phase-16 microcopy | Short — 150 chars |

## Written sources

| ... |

## Visual sources

| ... |

## Testimonials

| ... |

## Email + correspondence

| ... |

## Fresh-generated

| # | Source | Local path | Format | Provenance | Use for | Notes |
|---|---|---|---|---|---|---|
| 47 | Voice note — "why I started this" | inbox/voice-notes/origin-2026-05-18.m4a | m4a | own-creation | phase-16 copy + about-page | 2min 14s; needs transcription |
```

The agent does not curate during this phase. Items get added; items do not get rejected at phase 6. The `status` field flips from `capture-in-progress` to `capture-complete` when the user explicitly confirms there is nothing else.

## Gating rules

This phase is permissive by design. The agent refuses **only one** thing: silent capture-completion without user confirmation. The transition to phase 7 (asset audit) requires explicit *"yes, that's everything I have right now"* from the user.

Specifically, the agent does NOT refuse:
- Items of unclear quality (phase 7 owns quality audit)
- Items of unclear rights (phase 7 owns rights audit)
- Items in formats the agent doesn't know how to read yet (notes the format; downstream phases handle conversion)
- Items the user is "not sure if useful" (capture greedy; phase 13-16 select; the agent's bias here is keep-it)
- Duplicate items across sources (different versions of the same content can have different downstream value)
- Items in languages other than the project's primary language (multi-language is handled by phase 16; capture phase doesn't translate)

The agent DOES gently refuse:
- **Capture-completion claimed without elicitation.** When the user opens phase 6 with *"I don't have anything — just write the site from scratch"* and refuses any inventory walk, the agent gently insists on the elicitation routine: *"Almost everyone has more than they think. Let's just walk through five categories — current online presence, written stuff, photos, testimonials, emails — and see what surfaces."* If the user genuinely has nothing in any category, the agent shifts to fresh-generation mode (voice-note prompts, freewriting) — capture happens; the agent does not let the user skip phase 6 by claiming emptiness without verification.
- **Items located only in user's head.** When the user says *"I'll send you that file later"* repeatedly, the agent surfaces: *"Phase 7 needs the actual asset to audit quality + rights; phase 13-16 need the actual content to compose pages from. Promised items that don't materialize stall those phases. Want to capture the missing items now via voice-note or freewrite, or note them as `status: pending` with a target date?"* Items can be `pending`; the schema accommodates them; phase 7 does not advance with `pending` items still outstanding.

The override path applies — the user can advance to phase 7 with a thin inventory, and the agent flags the cost: phase 13-16 will hit empty-content-slots more often; the user will be writing fresh content under phase-16 pressure rather than curating existing material.

## Tools and skills used

- **`AskUserQuestion`** — heavy use. The elicitation routine is a structured conversation: per category, the agent asks what exists, where, in what format.
- **`Read`** — to read items the user provides as file paths or URLs that resolve locally. To read `.website-builder/project.yaml` (entity assets) at phase entry as the inventory seed.
- **`Bash`** — for file inventory operations: `ls`, `file`, `du`, `mkdir -p inbox/{social,written,visual,testimonials,email,voice-notes,freewrites,existing-site}` to scaffold the inbox subdirs; `cp` / `mv` to move user-provided files into `inbox/` with provenance-preserving names.
- **`Write` / `Edit`** — to author and update `.website-builder/inbox/INVENTORY.md`. The inventory grows incrementally as the user surfaces new items.
- **`WebFetch`** — to scrape the user's existing online presence (LinkedIn About, Instagram bio, current site pages, social-platform bios) when the user authorizes it. The agent saves fetched content into `inbox/social/` and `inbox/existing-site/` with provenance recorded.
- **`Glob`** — to search the user's local file system for assets when the user authorizes it ("look in `~/Documents/clients/` for any PDF I might have forgotten about") — agent reports findings; user confirms which to inbox.

`WebSearch` is generally not needed at this phase (the goal is what the user already has, not what's out there). `context7` is not needed. Playwright is not needed (phase 6.5 owns site walks; phase 6 uses WebFetch for surface scrapes).

No subagent spawn by default. When the user has a sprawling existing online presence (active across 6+ platforms with years of history), the agent may spawn a research subagent to do parallel WebFetches across platforms. The default is in-conversation walkthrough.

The agent does NOT invoke any tool that exfiltrates user content beyond their explicit confirmation — `inbox/` is local; nothing is uploaded; WebFetches happen only on URLs the user names.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/inbox/INVENTORY.md` | Inbox inventory per schema above | Master inventory; load-bearing for phases 7, 13-16 |
| `.website-builder/inbox/{category}/{filename}.{ext}` | Raw asset files, organized by category subdir | The actual content; referenced from INVENTORY.md |
| `.website-builder/inbox/voice-notes/{topic}-{date}.m4a` | Audio files when user records fresh material | Transcription happens at phase 13 or 16 when needed (not phase 6) |
| `.website-builder/inbox/freewrites/{topic}-{date}.md` | Markdown freewrites when user generates fresh material | Raw copy seed for phase 16 |
| `.website-builder/decisions/06-content-strategy.md` *(optional)* | Standard decision-doc frontmatter + body | Created when phase 6 surfaced a content-strategy decision (e.g., user has 50 testimonials and decides "use 6 representative; archive the rest") — decision belongs in decisions/, not in INVENTORY.md |

The INVENTORY.md is the required artifact. The category subdirs and raw files are the substance; INVENTORY.md is the map.

The agent updates `.website-builder/project.yaml.current_phase` to `7` upon user confirmation that capture is complete (`status: capture-complete` in INVENTORY frontmatter). Phase 7 (media refinement / asset audit) loads next.

## Common failure modes

**The user says "I have nothing."** The agent does not accept this without an elicitation pass: *"Let's walk through five categories briefly — even one item per category is enough. (1) Where do people find you online today? Even one URL. (2) Have you ever written anything about what you do — a LinkedIn post, an email to a friend, a paragraph in your phone's notes? (3) Do you have any photos taken of you for work purposes — even a single LinkedIn headshot? (4) Has anyone ever sent you a positive message about your work? (5) Has a client ever sent an email that described what they liked about working with you?"* Almost always 2-4 items surface from this pass. If genuinely nothing exists, agent shifts to fresh-generation: *"OK, we generate from scratch. Two prompts: record a 2-minute voice note about why you started this — talk to yourself, no editing. Then write 200 badly-written words answering: 'when someone like Maya is reading my site at 11pm on a Sunday, what is true about her life right after she leaves the site?'"*

**The user has TOO much.** *"I have 12 years of LinkedIn posts, a 60,000-word blog, a Substack archive of 80 issues, 400 client emails I want to mine."* The agent reframes scope: *"We're not extracting *everything* — we're collecting *available* material so phase 13-16 can curate from a known surface. Capture the top-level inventory: 'LinkedIn — 12 years; Substack — 80 issues; client emails — 400.' Then we focus on representative samples — 10 LinkedIn posts you remember being proud of; 5 Substack issues you'd reread; 10 client emails that contain language you'd reuse. The agent will use the rest as searchable corpus at phase 16 if relevant."* The full archive can be `status: archived-available`; the representative samples are `status: inboxed`.

**The user keeps promising to send items.** *"Yeah I'll send that logo file later."* / *"The photos are on my other laptop, I'll grab them this week."* The agent records these as `status: pending` with a target date, but flags: *"Phase 7 audits assets for quality + rights — pending items can't be audited. If the photo / logo / etc. doesn't arrive by phase 7, that phase either pauses or proceeds with a placeholder we revisit when the asset lands. Want to set a deadline?"* The user picks a date; the inventory records it.

**The user is uncomfortable sharing personal correspondence.** *"I don't want to share client emails — they're private."* The agent honors: *"You don't share the emails themselves; you share the *language patterns* they contain. Read three emails to yourself, then type me 3-5 phrases or sentences clients used to describe your work. The phrases go in `inbox/correspondence-extracts.md`; the actual emails stay with you."* This produces phase-16 copy seeds without privacy violation.

**The existing site has thousands of pages.** Old WordPress blog with 1,200 posts. The agent does not download all 1,200: *"We don't need every page. The agent runs phase 6.5 to extract the design tokens + site shape; for content, we inventory the top-level architecture (categories, hub pages, most-trafficked posts per analytics). The full archive stays at the old URL; phase 13-16 references it by URL when needed. Phase 16's translation pattern is to surface the 'best 20 posts' for phase-16 voicing, and the rest live as redirects from the new site to the archive."* Inventory captures the top-level structure; the deep archive is referenced not duplicated.

**The user has assets in formats the agent can't directly process.** Sketchbook pages photographed with a phone; an old Photoshop PSD; a Figma file in a free-tier account; a video that's 4GB on Google Drive. Agent records the asset with format + access path; defers processing to the consuming phase. *"Phase 7 will assess the sketchbook scans for quality + rights; phase 17 may use them as visual seeds. The Photoshop PSD will need extraction at phase 17 (or via Stitch / divmagic if applicable). The Figma file can be ingested via phase 6.5 if you want — separate phase. The video — we'll see what phase 8 (image / video strategy) decides about it; for now it's catalogued."*

**Phase 6.5 fires mid-phase-6 (user pastes a one-shot artifact for ingestion).** This is expected behavior — phase 6.5 is re-runnable. The agent invokes phase 6.5 to ingest the artifact (extract tokens to `brand.yaml`, content to `content/pages/`, etc.), returns to phase 6 capture mode for the remaining wild content. The agent surfaces: *"Phase 6.5 just ingested the v0 output. The hero copy from that output went to `content/pages/index.md` as a draft. The palette got logged to `brand.yaml` (will be reviewed at phase 17). Let's keep going — what else do you have?"* Phase 6.5 does NOT advance the project to phase 7; the agent returns to phase 6.

**The user is dual-language but only has content in one language.** *"All my prior content is in German; the new site will be EN + DE."* Agent records: *"Inbox-ed German content is the seed for DE pages. Phase 16 will produce EN translations (per `DESIGN-i18n.md` Pattern 1 — agent translates inline at phase 16) OR you can plan to use Pattern 2 (translator handoff via brief) at phase 16 for higher-stakes copy. Phase 6 just captures; phase 16 chooses the translation pattern."*

**The user produces content during phase 6 that contradicts phase 5 voice.** A captured LinkedIn post reads stiff-corporate; phase 5 locked warm-direct voice. The agent flags but does NOT refuse: *"This post is in a different voice from what we locked at phase 5. It can still be inbox-ed as raw material — phase 16 (copywriting) will revoice it. Or, if this post represents your actual voice and phase 5 was aspirational, that's worth surfacing now — should we revisit phase 5?"* Most often the user clarifies "no, the LinkedIn voice was stiff because I copied a template; the warm voice is the real one"; sometimes it surfaces a genuine voice re-think.

## Reference materials

- **Design doc — phase pipeline source:** `DESIGN-phase-contracts.md` § 6 (seed for this contract)
- **Design doc — pipeline integration:** `DESIGN-architecture.md` § Phase contracts
- **Design doc — inbox layout:** `DESIGN-project-scaffold.md` § `.website-builder/inbox/` (the directory structure phase 6 populates)
- **Design doc — content-layer consumption:** `DESIGN-content-layers.md` § Layer 3 (CDJSON) + § Layer 4 (page prose) — phases 13-16 lift from inbox/ into these layers
- **Design doc — multi-language content:** `DESIGN-i18n.md` § Translation workflow (when inbox items are in non-primary languages)
- **Design doc — phase 6.5 interleave:** `DESIGN-ingestion-and-extraction.md` § Phase 6.5 mechanism (when the user pastes a structured artifact during phase 6, 6.5 fires; this contract's "Common failure modes" surfaces the interleave behavior)
- **Plugin corpus — voice exemplars** (for fresh-generation prompts): `.website-builder/library/voice-archetypes/` — agent uses representative voice-guide phrasings as model when prompting the user to freewrite or voice-note
- **External (catalogued in `DESIGN-ecosystem-catalog.md`):**
  - Audio transcription tools (Whisper / OpenAI's audio-transcription / on-device) — referenced when voice notes need transcription at phase 13 or 16
  - Content Design JSON methodology — https://uxcontent.com/content-design-json/ (load-bearing at phase 16 when CDJSON layer 3 is written from inbox material)
