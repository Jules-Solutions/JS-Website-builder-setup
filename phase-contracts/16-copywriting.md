---
phase: 16
name: Copywriting
group: content-wireframes
pipeline_section: content-wireframes
skill: wb-content
prev_phase: 15
next_phase: 17
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/foundation/DESIGN-project-scaffold.md
  - Workstreams/website-builder/foundation/DESIGN-content-layers.md
  - Workstreams/website-builder/foundation/DESIGN-i18n.md
---

# Phase 16 — Copywriting

> Write the actual words. Every headline, subhead, body paragraph, CTA label, microcopy string — finalized, in the brand voice from phase 5, against the placeholders and string-keys phases 13-15 produced. The phase where the site stops being a structure and starts being a thing a person reads. The agent refuses placeholder copy and AI-generic LinkedIn-speak; it cross-checks voice against the phase-5 exemplars. For multilingual sites this is where translation happens, per the locked i18n decisions.

## Mission

Phases 13-15 built the scaffolding: page briefs, wireframes, component specs, content placeholders, declared string keys. Phase 16 fills it with finalized prose. Every content placeholder in `.website-builder/content/pages/{slug}.md` gets real copy. Every empty key in `.website-builder/content/strings/${default_language}.json` gets a real value. The output is a site whose every word is written, in the brand voice established at phase 5, ready for phase 17 (design system) to make it look like something.

The discipline of this phase is voice. Phase 5 captured the brand voice — a description, 3-5 attributes, say/never-say exemplars, 1-2 voice-exemplar brands. Phase 16 writes every word against that voice and cross-checks the result the way a writer reads aloud: does this sentence sound like the brand, or does it sound like generic AI marketing copy? The two specific failures the agent refuses are (1) placeholder copy surviving onto a deployed site (lorem ipsum, `[headline here]`, `TODO: write this`) and (2) AI-generic LinkedIn-speak ("Unlock your potential", "Optimize your wellness journey", "We help businesses succeed", "In today's fast-paced world") — the flattened, voiceless register that LLMs default to and that destroys brand distinctiveness.

For multilingual sites, phase 16 is also where translation happens, governed by the locked i18n decisions 38-41: prefix URL routing (decision 38), Pattern A pages-per-language as default (decision 39), Pattern 1 agent-translates-inline as default (decision 40), missing-key-shows-default-language-string fallback (decision 41). The agent generates source-language prose first, then runs the translation workflow. Translation review is human-required for production (the agent surfaces the caveats and recommends Pattern 2 — translator handoff — when translation quality materially affects business outcome).

## Entry conditions

- Phase 15 (content per section) complete. `.website-builder/components.yaml` has every component spec; `.website-builder/content/sections.yaml` maps sections to components; every `content/pages/{slug}.md` has content placeholders in section bodies; `.website-builder/content/strings/${default_language}.json` has every needed key declared (empty or stub values).
- Phase 5 (brand voice & tone) complete. `.website-builder/brand.yaml.voice` has the voice description, attributes, say/never-say exemplars, and exemplar brands. This is the contract phase 16 writes against.
- `.website-builder/project.yaml.languages` and `.default_language` are set. For multilingual sites, `.website-builder/project.yaml.language_routing` (prefix per decision 38) and `cms_i18n_strategy` (Pattern A per decision 39) are set from phase 12.
- Phase 6 (wild content capture) complete. `.website-builder/inbox/INVENTORY.md` lists the user's existing raw content (drafts, bios, prior-site copy, testimonials) the agent draws from rather than inventing.

## What Claude must establish

Finalized prose for every content slot on the site, in two layers:

1. **Page-level prose (Layer 4).** Every content placeholder in every `content/pages/{slug}.md` section body becomes finalized markdown prose: headlines, subheads, body paragraphs, captions, list content. Written in the phase-5 brand voice. Drawn from phase-6 source content where it exists; written fresh where it doesn't (the agent guides the user through generating raw material — voice notes, freewriting prompts — rather than inventing it, per the phase-6 fallback pattern). Each placeholder's spec (length, voice constraint, source, intent) from phase 15 is the brief.

2. **Content Design JSON values (Layer 3).** Every declared key in `.website-builder/content/strings/${default_language}.json` gets a real value: CTA labels (`cta.subscribe`, `cta.contact`), state strings (`cta.subscribe_loading`, `cta.subscribe_success`, `cta.subscribe_error`), error messages (`errors.network`, `errors.validation_email`), nav labels, form-validation copy, variable copy (`variables.welcome_back: "Welcome back, {name}"`). Microcopy carries voice too — the loading/success/error states are where most sites go voiceless ("An error occurred") and where a brand voice is most distinctive ("Hmm, that didn't work. Try again?").

For **multilingual sites**, additionally:

3. **Per-language prose** (Layer 4, per the i18n pattern). Pattern A (decision 39 default): same structural frontmatter across languages, prose translated — `content/pages/about.en.md`, `content/pages/about.de.md`, etc., sharing `sections[]` / sitemap reference, differing in body + `language` field. Pattern B (per-market structural variation): different prose, different examples, different sections per market; the agent asks per page which pattern fits (most pages are Pattern A; pricing / market-specific pages may be Pattern B).

4. **Per-language strings** (Layer 3). One `content/strings/{lang}.json` per configured language, mirroring the default-language structure with translated values. ICU Message Format preserved for plurals (`{count, plural, =0 {No items} one {# item} other {# items}}`) — German has 2 plural forms, Polish 4, Arabic 6; the agent uses ICU from the start so plurals are correct per language.

The agent updates `.website-builder/project.yaml.current_phase` to `17` upon completion. Phase 17 (design system) loads next.

## Gating rules

The agent refuses to advance when:

- **Any placeholder copy remains.** Lorem ipsum, `[headline here]`, `TODO`, `(write this)`, empty string-keys, or any slot still holding a phase-15 placeholder spec instead of finalized prose. Every content slot must have real words. The agent sweeps every `content/pages/*.md` and every `strings/*.json` before allowing advance. This gate is not overridable — a site cannot ship with placeholder copy, and phase 17+ would design around holes.
- **Voice drift between sections.** The agent reads the whole site's copy against the phase-5 voice exemplars (the "read it aloud" cross-check). If section A sounds warm-direct and section B sounds corporate-formal, the voice is drifting. The agent surfaces the drifting sections and rewrites them to the locked voice. The exit isn't "every section has words"; it's "every section sounds like the same brand."
- **AI-generic LinkedIn-speak.** The agent refuses copy that pattern-matches the voiceless LLM-default register: "unlock your potential", "optimize your X journey", "we help businesses succeed", "in today's fast-paced world", "take your X to the next level", "seamless / cutting-edge / innovative / robust / leverage / synergy" as filler. The agent surfaces the specific phrases and rewrites them in the brand voice. The phase-5 `never_say` exemplars are the explicit reference; the agent also catches the generic register even when it's not in the explicit never-say list.
- **Copy contradicts the content spec.** If phase 15's placeholder said "≤60 chars, communicates what-this-is in one line" and the written headline is 140 chars of feature list, the agent surfaces the mismatch and rewrites to spec. The placeholder is the contract.
- **Multilingual: a language file has missing keys or untranslated values.** Every configured language's `strings/{lang}.json` must have the same key structure as the default (per decision 41's validation), and every value must be translated (not a copy of the default-language string left untranslated). The agent's cross-language validation sweep catches both. Missing-key fallback (decision 41) is a render-time safety net, not a license to ship incomplete translations — the agent surfaces every gap.

Override is available only on the voice-drift and LinkedIn-speak gates via explicit user confirmation (the user may want a deliberately different register for a specific section, or may accept a phrase the agent flagged). The placeholder-copy gate and the multilingual-completeness gate are not overridable — they are correctness prerequisites for shipping.

## Tools and skills used

- **Edit** — the primary tool. The agent edits content placeholders into finalized prose across `content/pages/{slug}.md` files and edits string values into `content/strings/{lang}.json`. Most of phase 16 is edit work against the structure phases 13-15 built.
- **Read** — agent reads `.website-builder/brand.yaml.voice` continuously (the voice contract; re-read per section to cross-check), `.website-builder/inbox/INVENTORY.md` (phase-6 source content to draw from), each page's phase-15 content placeholders (the per-slot brief).
- **AskUserQuestion** — used when the agent needs the user's actual words (the brand voice is theirs, not the agent's to invent) — *"this section needs your origin story; tell me in your own words what happened in 2019, and I'll shape it to the voice without flattening it."* Also used for per-page Pattern A vs Pattern B decisions on multilingual sites, and for the Pattern 1 vs Pattern 2 translation-workflow choice when translation quality is high-stakes.
- **WebSearch** — to surface current copywriting / voice-and-tone best-practice and current Content Design JSON microcopy conventions, so the agent's voice cross-check reflects current professional practice, not stale training data.
- **WebFetch** — to load a phase-5 voice-exemplar brand's live site and study its actual register (the agent reads the exemplar's microcopy and headlines to calibrate the voice cross-check against a real example, per `DESIGN-templates-catalog.md`: studied for voice, never copied).
- **Write** — for multilingual sites, the agent writes per-language `content/pages/{slug}.{lang}.md` files (Pattern A) and per-language `content/strings/{lang}.json` files; for translator-handoff (Pattern 2), the agent writes `briefs/translation-{lang}-{ts}.json`.
- **Reference-data load** — `reference/voice-archetypes/` for voice calibration; `reference/brand-examples/` for how mature brands carry voice through microcopy.

The `wb-content` phase-group skill (loaded since phase 13) carries the cross-phase contract: the prose phase 16 writes goes into the same files phase 13-15 specced, and phase 19 (composition) renders them into stack code. No re-architecting at phase 16 — only the words change; the structure is locked.

## Output artifacts

Finalized `.website-builder/content/pages/{slug}.md` — placeholders replaced with prose:

```markdown
---
type: page
slug: /about
status: active                        # promoted from draft once copy is final
language: en
title: "About"
seo_title: "About — Still Humans"     # phase 26 may refine; finalized prose here
seo_description: "The story behind a weekly essay project about staying human in an AI-saturated world."
purpose: "Convert qualified prospects into discovery-call bookings via credibility + friction-reduction."
primary_cta: "{strings.cta.contact}"
sections: [bio, philosophy, social-proof, contact-cta]
relates_to:
  - .website-builder/brand.yaml
---

## Bio section

The story starts in 2019, in a kitchen at 6am, with a half-written essay and the realization
that nobody was writing the thing I wanted to read. So I started writing it myself. Six years
later it's a weekly habit and a few thousand people who read it on Monday mornings before the
world gets loud.

## Philosophy section

The premise is simple and slightly contrarian: in a world optimized for your attention, the
most radical thing you can do is pay attention on purpose. This isn't a productivity project.
It's the opposite. It's a weekly argument for staying a person while everything around you
tries to turn you into a metric.

## Social proof section

(Renders 3 featured testimonials from the CMS — TestimonialGrid component, data per components.yaml.
Quote prose is editor-supplied via the CMS, not authored here; the section copy below is the heading.)

**Section heading:** What readers say

## Contact CTA section

**Headline:** {strings.cta.contact_headline}
**Sub:** {strings.cta.contact_sub}
**Button:** {strings.cta.contact}
```

Finalized `.website-builder/content/strings/en.json` — keys valued, in voice:

```json
{
  "$language": "en",
  "$schema": "spec/strings-v1.json",
  "cta": {
    "subscribe": "Get the Monday essay",
    "subscribe_loading": "Signing you up…",
    "subscribe_success": "You're in. Check your inbox — there's a confirmation waiting.",
    "subscribe_error": "Hmm, that didn't work. Try again?",
    "contact": "Start a conversation",
    "contact_headline": "Got a project worth doing well?",
    "contact_sub": "One reply, one honest read of whether I'm the right person for it.",
    "essays_read_more": "Read the latest"
  },
  "errors": {
    "network": "Connection dropped. Check your internet and try once more.",
    "validation_email": "That doesn't look like an email — mind checking it?"
  },
  "nav": {
    "skip_to_content": "Skip to content",
    "language_switcher_label": "Language",
    "home": "Home", "essays": "Essays", "about": "About", "contact": "Contact"
  },
  "variables": {
    "welcome_back": "Welcome back, {name}",
    "items_count": "{count, plural, =0 {No essays yet} one {# essay} other {# essays}}"
  },
  "dates": { "format_short": "MMM d, yyyy", "format_long": "MMMM d, yyyy" },
  "currency": { "symbol": "$", "format": "{symbol}{amount}" }
}
```

For multilingual sites — additionally:

- `content/pages/{slug}.{lang}.md` per configured non-default language (Pattern A: shared frontmatter, translated body; Pattern B where market variation requires it).
- `content/strings/{lang}.json` per configured language, structure mirrored, values translated, ICU plurals correct per language.
- For Pattern 2 (translator handoff): `briefs/translation-{lang}-{ts}.json` containing source strings + source prose + voice guidelines + glossary of do-not-translate terms (brand names, technical terms) + voice exemplars.

## Common failure modes

**"Just write all the copy for me — you know what's good."** The premature-handoff move (the same anti-pattern phase 1 names). The agent refuses to invent the brand's voice wholesale: *"the words have to be yours or they'll read like every other AI-written site. Give me the raw material — what actually happened, in your words — and I'll shape it to the voice without flattening it. The shaping is mine; the substance is yours."* For sections where the user genuinely has nothing (a value proposition they've never articulated), the agent uses the phase-6 fallback: freewriting prompts, voice-note transcription, structured questions — generating raw material the agent then shapes, never inventing substance.

**AI-generic LinkedIn-speak slipping in.** The most insidious failure because it reads as "professional" to muggles. *"We help businesses unlock their potential through innovative solutions."* The agent surfaces it explicitly: *"this sentence could be on any of ten thousand sites — it says nothing specific and sounds like nobody. Your voice (from phase 5) is warm and direct and slightly contrarian. What does this section actually mean, said the way you'd say it to a friend?"* The agent rewrites against the phase-5 voice and shows the before/after so the user learns to catch it themselves.

**Voice drift across the site.** The hero sounds warm; the about page sounds corporate; the FAQ sounds like a legal disclaimer. Common because different sections feel like they "should" sound different. The agent reads the whole site aloud (figuratively — cross-checks every section against the phase-5 exemplars) and surfaces the drift: *"the hero sounds like you; the FAQ sounds like a different company wrote it. Same brand, same voice, everywhere — even the error messages."* The agent rewrites drifting sections to the locked voice.

**Placeholder copy surviving to deploy.** `[Your headline here]`, `Lorem ipsum`, `TODO: write this`. The agent's phase-16-exit sweep catches every one. This gate is not overridable — a deployed site with placeholder copy is a broken site, and phase 17 would design around the hole. The agent surfaces every remaining placeholder and refuses to advance until all are resolved.

**"The German translation can wait until after launch."** For multilingual sites, this is a structural-completeness failure. The agent surfaces that decision 39 (Pattern A default) means all configured-language pages exist at launch, and decision 41's missing-key fallback is a render-time safety net (shows the default-language string + logs a warning) — not a license to ship a half-translated site. The agent recommends Pattern 2 (translator handoff) when translation quality materially affects the business (commercial / legal / regulatory copy, distinctive brand voice in a high-stakes market) and surfaces the Pattern 1 caveats explicitly: idioms may not translate naturally, brand-specific terms need manual locking, voice nuance may flatten, commercial/legal/medical copy may need professional translation regardless. Translation review is human-required for production — the agent does not declare translated copy final without the user (or a translator) reviewing it.

**Microcopy left voiceless.** The user writes brand-voiced headlines but leaves the loading/error/success states as "Loading…", "An error occurred", "Success". Microcopy is where voice is most distinctive and most often abandoned. The agent surfaces: *"these three strings are the moments a user is most frustrated or most relieved — they're exactly where your voice matters most. 'An error occurred' is nobody's voice. What does your brand say when something breaks?"* (Mukti's canonical example — "FOUR different ways to say 'transaction failed' across one platform" — is the inconsistency a single Content Design JSON source prevents; phase 16 is where that single source gets its voiced values.)

**Copy that contradicts the wireframe's space.** Phase 14's wireframe gave the hero headline a single line; phase 16's copy is a 3-line paragraph. The agent surfaces the structural conflict — the copy doesn't fit the layout intent — and either tightens the copy to the wireframe or flags a wireframe revision (re-opening a thin phase 14). Copy and structure must agree before phase 17 designs against both.

**Hidden assumption that phase 17 will "fix" weak copy with design.** It will not. The agent surfaces, when the user leans on this, that design amplifies copy — strong copy designed well is strong; weak copy designed well is weak copy that looks expensive. Phase 16's words have to carry their own weight before phase 17 makes them look good.

## Reference materials

Foundation docs:

- `Workstreams/website-builder/foundation/DESIGN-content-layers.md` — Layer 4 (page-level prose) + Layer 3 (Content Design JSON values). Phase 16 is where Layer 4 placeholders become prose and Layer 3 keys become values. The `## Why a separate layer` rationale (localization-ready, variable copy, reuse, auditing, translation handoff) is why microcopy lives in `strings/{lang}.json` and gets voiced here.
- `Workstreams/website-builder/foundation/DESIGN-i18n.md` — the canonical source for the multilingual behavior of this phase. Decisions 38-41 are implemented here: decision 38 (prefix URL routing — affects per-language file naming), decision 39 (Pattern A pages-per-language default — shared structure, translated prose), decision 40 (Pattern 1 agent-translates-inline default; Pattern 2 translator-handoff via brief is the upgrade path; Pattern 3 user-driven external tool), decision 41 (missing-key-shows-default-language-string fallback with validation warning). The `## Translation workflow` section's caveats (idioms, brand terms, voice nuance, commercial/legal copy) are what the agent surfaces when recommending Pattern 2.
- `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` § `content/pages/{slug}.md` + `content/strings/{lang}.json` + Pattern A/B file-naming — the exact output conventions.
- `.website-builder/brand.yaml.voice` (phase-5 output) — the voice contract phase 16 writes against. Re-read per section for the voice cross-check.

Content Design JSON methodology (the microcopy-as-system discipline):

- **[How content designers can (and should) use JSON files](https://uxcontent.com/content-design-json/)** — Prasaja Mukti, UX Content Collective, June 10, 2025. The canonical methodology. Phase 16 values the keys phase 15 declared. Core principles applied here: copy as single-source-of-truth structured data (prevents the "four ways to say transaction failed" inconsistency); variable copy (`{name}`, `{count}` with ICU plurals) for context-sensitive strings; per-language folder structure mirrors the single source. The methodology's "content designers become system architects, not wordsmiths" framing is exactly the discipline: voice is systematic here, not ad-hoc per slot.
- Localization-with-translation-in-mind: per the 2026 content-design practice surfaced via WebSearch (uxcontent.com 2026 guidance), copy written for translatability avoids idioms / wordplay / culturally-complex phrasing — the agent applies this when writing source-language prose on multilingual sites so the downstream translation (Pattern 1 inline or Pattern 2 handoff) is smoother.

Voice corpus:

- `reference/voice-archetypes/` — exemplars across the verbal-identity spectrum, for calibrating the phase-5 voice cross-check.
- `reference/brand-examples/` — complete brand systems showing how mature brands carry one voice through headlines, body, and microcopy consistently.
- Phase-5 `exemplar_brands` — the agent WebFetches the live sites of the 1-2 voice-exemplar brands from `brand.yaml.voice.exemplar_brands` and studies their actual microcopy + headline register to calibrate the cross-check against a real example (studied for voice, never copied, per `DESIGN-templates-catalog.md`).

WebSearch / WebFetch (recommended at this phase):

- WebSearch *"brand voice copywriting microcopy best practice 2026"* — current professional voice-and-tone practice so the cross-check reflects current standards, not stale training data.
- WebSearch *"Content Design JSON microcopy localization 2026"* — current Content Design JSON + localization practice (the 2026 uxcontent.com guidance on writing-for-translatability is cited above).
- WebFetch phase-5 exemplar-brand sites — for live voice calibration.
- Sources: [How content designers can (and should) use JSON files — UXCC](https://uxcontent.com/content-design-json/), [Content design in 2026 — UXCC](https://uxcontent.com/content-design-in-2026/), [AI in Content Design and UX Writing — UXCC](https://uxcontent.com/ai-in-content-design-ux-writing/).

Freshness date for this contract's references: **2026-05-18**.

## Skip authorization

Phase 16 is not skippable. A site without finalized copy is not a site — it is a structure with holes. Phase 17 (design system) and phase 18 (component build) design and code against real content; designing around placeholders produces layouts that break when real copy arrives (the same structural-anchoring problem phase 14's skip causes, one layer up).

Two narrow legitimate paths:

1. **Phase-6.5 ingestion produced finalized copy.** When entry mode was `has-existing-site`, phase 6.5 may have extracted real, already-written copy from the deployed site into `content/pages/{slug}.md`. Phase 16 runs as a voice-reconciliation pass: the agent reads the ingested copy against the phase-5 voice (the ingested copy was written before the voice was articulated, so it may drift), surfaces inconsistencies, and rewrites to the locked voice with the user's confirmation. Not a skip; a voice pass over existing prose.
2. **Mid-project content addition via `wb-postlaunch:content-add` skill.** The post-launch maintainer template (per locked decision 49) includes a `content-add` skill that re-runs a thin phase 16 for new copy only, applying the locked voice. Not a skip; a scoped replay.

Skipping phase 16 entirely is not authorized. If the user requests it (usually as *"the design matters more than the words, let's just get to the design"*), the agent surfaces the inversion: *design amplifies copy; it does not replace it*. Weak or placeholder copy designed beautifully is weak copy that looks expensive — and phase 17/18 will have to be redone when the real words arrive and don't fit. The agent offers the fastest honest path through phase 16 instead: draw from phase-6 source content where it exists, use guided freewriting where it doesn't, and let the agent do the voice-shaping while the user supplies the substance.
