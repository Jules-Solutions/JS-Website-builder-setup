---
name: wb-content
description: >-
  This skill should be used when the website-builder agent reaches the
  content-and-wireframes stage of the pipeline (phases 13-16) — when the user
  says "write the page briefs", "what does each page do", "let's wireframe the
  site", "sketch the layout", "spec the sections", "what's in each section",
  "write the copy", "finalize the words", "the about page is just about us",
  "can we just start designing", or works on content-per-page,
  wireframe-per-page, content-per-section, or copywriting. Carries the
  cross-phase discipline linking phases 13 then 14 then 15 then 16 — every page
  gets a conversion-anchored brief, a text wireframe, per-section
  component-plus-content specs, and finalized brand-voiced prose, all in the
  same .website-builder/content/ files. Enforces page-purpose-over-page-topic,
  the wireframe anti-skip (about 60% rework cost), content/component
  separation, and the anti-LinkedIn-speak voice gate. Also covers Content
  Design JSON (microcopy as structured data) and multilingual translation per
  the locked i18n decisions.
version: 0.1.0
---

# wb-content — Content & Wireframes (phases 13-16)

> The stage where the site stops being a sitemap and becomes a thing a person reads. Phase 13 says what each page *does*; phase 14 sketches *how* its sections are arranged; phase 15 specs *what* each section contains; phase 16 writes *the actual words*. One skill, four phases, one continuous discipline: every artifact phase 13 produces gets a wireframe, a spec, and finalized prose in the same files — no re-architecting downstream.
>
> Design-doc primacy: this skill points at design docs and phase contracts; those are the source of truth. Read the cited paths — do not work from this summary alone.

## When this skill is active

Loads at the start of phase 13 and stays loaded through phase 16. The four phases are a unit — their outputs accumulate in `.website-builder/content/pages/{slug}.md`, `.website-builder/content/sections.yaml`, `.website-builder/components.yaml`, and `.website-builder/content/strings/{lang}.json`. Each phase reads the previous phase's output from those files. Treat the four as one workflow with four gates, not four independent tasks.

## The phase contracts are the substantive reference

Each phase has a verbatim contract. Read the relevant one in full before executing that phase — it carries the exact entry conditions, gating rules, output schemas, failure modes, and skip-authorization that this skill only summarizes:

| Phase | Contract path | What it owns |
|---|---|---|
| 13 — Content per page | `phase-contracts/13-content-per-page.md` | Per-page conversion-anchored brief; section list; cross-page links; CTAs; data deps; Content Design JSON skeleton declared |
| 14 — Wireframe per page | `phase-contracts/14-wireframe-per-page.md` | Text/ASCII wireframe; section order; per-section layout; hierarchy; responsive intent |
| 15 — Content per section | `phase-contracts/15-content-per-section.md` | Per-section component specs (`components.yaml`); content placeholders; string-key declarations |
| 16 — Copywriting | `phase-contracts/16-copywriting.md` | Finalized prose; Content Design JSON values; multilingual translation per i18n decisions |

For each phase: read the contract, run the workflow below, honor the gates, write the output artifacts to the exact schemas the contract gives.

## The cross-phase contract (why one skill, not four)

The discipline that links the four phases:

- **Phase 13's brief is phase 16's spec.** A vague brief produces drift at phase 16. The agent forces conversion-articulated briefs at 13 so the copy at 16 has a contract to write against.
- **Phase 14's wireframe is the structural anchor for phases 15-18.** Skipping it pushes structure-discovery into the build phase (about 60% rework). The wireframe constrains the section specs (15) and the copy length (16).
- **Phase 15's separation discipline (content vs component) is what makes phase 16 and phase 18 independent.** Words live in page bodies + strings JSON; shapes live in `components.yaml`. Mixing them breaks translation reuse and component reuse.
- **Phase 16 only changes words.** The structure is locked by 13-15. No re-architecting at 16 — if copy doesn't fit the wireframe, the agent surfaces the conflict and re-opens a thin 14, never silently restructures.

The single sentence the agent can always fall back on: *"the words and the shape live in different places, on purpose, so each can change without breaking the other."*

## Phase 13 — Content per page

**Goal:** every page gets a brief at `.website-builder/content/pages/{slug}.md` (frontmatter + body) capturing conversion role, ordered section list, cross-page links, primary/secondary CTAs, data dependencies, and SEO preview. Also declare the Content Design JSON skeleton at `.website-builder/content/strings/${default_language}.json`.

**Workflow:** for each page in `.website-builder/sitemap.yaml.pages[]`, use `AskUserQuestion` to extract: what does this page *do* (conversion role, not topic)? primary CTA (anchored to phase-3 conversion outcome)? what sections compose it? what data does it pull? what links in, what links out? Read `.website-builder/inbox/INVENTORY.md` (phase-6 sources) and `.website-builder/brand.yaml.voice` (phase-5 voice) to anchor draft brief language. Write one brief per page; append new section types to `content/sections.yaml`; write the strings skeleton (`cta`, `errors`, `nav`, `variables`, `dates`, `currency` keys, empty values).

**The load-bearing discipline:** page *purpose*, not page *topic*. "About page = our story" is the canonical failure. Force the conversion answer — *after someone reads this, what should they want to do next?* See `references/page-purpose-discipline.md` for the full conversion-anchoring patterns and the audience-page-purpose triangle.

**Gates (refuse to advance):** a page with no clear conversion purpose; a page with no path to the primary CTA (override allowed for explicitly non-conversion pages — legal/imprint/404 — with logged reason); a section type not in `sections.yaml` (add it intentionally or re-map); a page referencing uncaptured content; the Content Design JSON skeleton not declared. Purpose-clarity gate is overridable with explicit user confirmation.

## Phase 14 — Wireframe per page

**Goal:** for each page, a text-based wireframe (Unicode box-drawing, not pixels) capturing section order, per-section layout shape, in-section hierarchy, and responsive intent at ~360/768/1280px. Write under a `## Wireframe` heading in the page file, or a sibling `{slug}.wireframe.md` when long. Shared regions (header/footer/recurring CTA band) wireframed once in `content/_shared/{region}.wireframe.md` and referenced.

**Workflow:** most users cannot author a layout from scratch. Offer **2-3 wireframe options per page** drawn from the phase-2 vision references and ask the user to react ("option A leads with the manifesto; option B leads with social proof — which fits the visitor's mindset here?"). Reaction beats authorship for non-designers. Use `WebFetch` to walk a phase-2 reference site's structure as inspiration (studied, never imported — per `cross-cutting/DESIGN-templates-catalog.md`). Use the Unicode box-drawing convention in `references/wireframe-conventions.md` so the output parses cleanly for humans and downstream AI.

**The load-bearing discipline:** structure only — no color, type, spacing, motion, imagery (those are phase 17). When the user argues button color, redirect: *"that's a phase-17 decision; right now we're settling whether the button goes above or below the testimonials."*

**Gates (refuse to advance):** sections without committed order; missing responsive intent (refuse desktop-only wireframes); wireframe contradicting the phase-13 content brief; header/footer inconsistent across pages. **The skip gate:** the user pushes to "just start designing." Refuse *once*, surface the quantified cost (*"skipping wireframing means the design phase produces designs without structural anchoring; rework probability ~60%"*), offer the fast option-react path, and override only on explicit confirmation logged to `.website-builder/decisions/skip-phase-14.md` (still capture one-line per-section responsive intent even on skip — phase 20 needs it). Full skip-handling script + the decision-doc frontmatter in `references/wireframe-conventions.md`.

## Phase 15 — Content per section

**Goal:** for every section across the site (de-duplicated by type), spec the component(s) it uses, the component fields/props with constraints, the data it needs (static vs dynamic), a content placeholder per prose slot, and the Content Design JSON string keys it needs. Write `components.yaml` (Layer 2), update `sections.yaml`, add content placeholders to page bodies (Layer 4 placeholder), declare string keys in `strings/{default_language}.json` (Layer 3).

**Workflow:** for each section type ask: what component holds this? what fields? what data (static the user supplies, or dynamic from CMS/Stripe/recent-posts)? what must the prose in each slot accomplish? Propose first-draft specs from `reference/component-patterns/` and let the user adjust rather than author from scratch. Reconcile reuse — a section used on 3 pages is specced once; merge accidental near-duplicates.

**The load-bearing discipline:** content/component separation. A section's *content* is what it says (the headline text). A section's *component* is the reusable shape that holds it (`HeroBlock` with `headline: {type: string, max_chars: 60}`). They live in separate layers. When the user puts a literal string into a component spec, move it out to a phase-16 placeholder or a string key; when they put `max_chars`/`responsive` into a content body, move it to `components.yaml`. Correct in place and explain — do not block advance over it. Full separation patterns + the diagnostic table in `references/content-component-separation.md`.

**Gates:** phase 15 has **no refuse-to-advance gating** — it is structural build-up. The only enforced discipline is the separation (corrected in place, not blocked). One soft completeness check: every section the wireframe shows has a `components.yaml` entry + a content placeholder before advancing (a sweep, not a refusal — unspecced sections surface loudly at 16/18).

## Phase 16 — Copywriting

**Goal:** every content placeholder in every `content/pages/{slug}.md` becomes finalized prose in the phase-5 brand voice; every declared key in `strings/${default_language}.json` gets a real value. For multilingual sites, per-language prose + per-language strings per the locked i18n decisions.

**Workflow:** mostly `Edit` work against the structure 13-15 built. Re-read `.website-builder/brand.yaml.voice` per section for the voice cross-check. Draw from `.website-builder/inbox/INVENTORY.md` (phase-6 source content) where it exists; where it doesn't, use the phase-6 fallback (guided freewriting, voice-note transcription, structured questions) to get the user's raw material — never invent the brand's substance. Microcopy carries voice too: loading/success/error states are where sites go voiceless and where brand voice is most distinctive. `WebFetch` the phase-5 exemplar-brand site to calibrate the voice cross-check against a real example.

**The load-bearing discipline:** voice. Two refusals: (1) placeholder copy on a deployed site (lorem ipsum, `[headline here]`, `TODO`, empty string-keys); (2) AI-generic LinkedIn-speak ("unlock your potential", "in today's fast-paced world", "leverage", "seamless", "cutting-edge"). The agent reads the whole site against the phase-5 exemplars ("read it aloud") and rewrites drift to the locked voice. See `references/voice-and-copy-discipline.md` for the LinkedIn-speak phrase bank, the voice cross-check procedure, and the before/after teaching pattern.

**Multilingual:** translation happens here per locked decisions 38-41 — prefix URL routing (38), Pattern A pages-per-language default (39), Pattern 1 agent-translates-inline default (40), missing-key-shows-default-language fallback (41). Pattern A files: `content/pages/{slug}.{lang}.md` sharing structural frontmatter, translated body. Per-language `strings/{lang}.json` with ICU plurals correct per language (German 2 forms, Polish 4, Arabic 6). Recommend Pattern 2 (translator handoff via `briefs/translation-{lang}-{ts}.json`) when translation quality materially affects business outcome. Translation review is human-required for production. Full multilingual procedure + ICU patterns + the writing-for-translatability rules in `references/i18n-translation-workflow.md`.

**Gates (refuse to advance):** any placeholder copy remains (not overridable); voice drift between sections (overridable with explicit confirmation); AI-generic LinkedIn-speak (overridable); copy contradicts the phase-15 spec/phase-14 wireframe; multilingual file with missing keys or untranslated values (not overridable).

## Content Design JSON — the microcopy-as-data layer

Phases 13-16 treat reusable microcopy (CTAs, errors, nav labels, form validation, variable copy) as structured version-controlled data at `.website-builder/content/strings/{lang}.json`, referenced from page bodies via `{strings.path.to.key}`. This is the Content Design JSON methodology (Prasaja Mukti, UX Content Collective, June 2025 — [uxcontent.com/content-design-json](https://uxcontent.com/content-design-json/)): phase 13 declares the skeleton, phase 15 declares the keys, phase 16 values them. The methodology's core win is preventing the "four different ways to say 'transaction failed'" inconsistency — one source of truth makes drift visible. Full categorical structure, the four variable categories, and the per-language folder model are in `references/content-design-json.md`.

## Recommended composables (the user MAY invoke; not bundled)

- **`document-skills:doc-coauthoring`** — recommend at phase 16 when the user wants a structured co-authoring loop for long-form prose (about-page narrative, manifesto, philosophy sections). It complements this skill's voice discipline with an iteration workflow. Surface it: *"for the longer prose sections, you can also invoke `document-skills:doc-coauthoring` via the Skill tool — it gives us a tighter draft/refine loop. I'll keep enforcing the phase-5 voice on top."* Do not vendor or embed it; point to it.

## Additional resources

Reference files (loaded on demand — keep this SKILL.md lean):

- **`references/page-purpose-discipline.md`** — phase-13 conversion-anchoring patterns, the audience-page-purpose triangle, the "about page is just about us" recovery script, section-type proliferation handling.
- **`references/wireframe-conventions.md`** — phase-14 Unicode box-drawing convention, the 2-3-options-to-react-to method, the skip-handling verbatim script, the `skip-phase-14.md` decision-doc schema, ASCII-wireframe tooling landscape.
- **`references/content-component-separation.md`** — phase-15 content/component separation patterns, the diagnostic table, per-CMS structural mappings (Payload Blocks / Decap list+types / file-based frontmatter), component-pattern corpus usage.
- **`references/voice-and-copy-discipline.md`** — phase-16 voice cross-check procedure, the AI-generic LinkedIn-speak phrase bank, the placeholder-copy exit sweep, the before/after teaching pattern, microcopy voicing.
- **`references/content-design-json.md`** — the full Content Design JSON methodology: categorical structure, four variable categories, per-language folder model, the schema this pipeline writes.
- **`references/i18n-translation-workflow.md`** — the multilingual workflow per locked decisions 38-41: Pattern A/B prose, Pattern 1/2/3 translation, ICU Message Format, writing-for-translatability, the translation brief schema.

Foundation design docs (the source of truth — read directly):

- `Workstreams/website-builder/foundation/DESIGN-content-layers.md` — the 5-layer content stack; Layer 2 (structural specs), Layer 3 (Content Design JSON), Layer 4 (page prose). The `## What layer is what concern` diagnostic table is the agent's separation reference.
- `Workstreams/website-builder/foundation/DESIGN-i18n.md` — decisions 38-41, routing strategies, Pattern A/B, the three translation patterns, ICU pluralization, RTL.
- `Workstreams/website-builder/cross-cutting/DESIGN-templates-catalog.md` — templates and reference sites are studied for layout/voice, never imported. The phase-14 option-react method and phase-16 voice calibration draw from this.
- `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` — the exact `.website-builder/content/` schemas these phases write.

External methodology sources (cited because phases 13-16 implement them):

- Content Design JSON: [How content designers can (and should) use JSON files — Prasaja Mukti, UX Content Collective, June 2025](https://uxcontent.com/content-design-json/); [Content design in 2026 — UXCC](https://uxcontent.com/content-design-in-2026/).
- Text/ASCII wireframing: [BareMinimum](https://bareminimum.design/), [Wyreframe](https://github.com/wickedev/wyreframe), [Generating ASCII wireframes with Claude — 32pixels](https://32pixels.co/blog/generating-ascii-wireframes-and-flowcharts-with-claude). Low-fidelity-for-non-designers: [Balsamiq — what are wireframes](https://balsamiq.com/blog/what-are-wireframes/), [IxDF — wireframing 2026](https://ixdf.org/literature/topics/wireframe).

Freshness date for this skill's external references: **2026-05-18**.
