---
phase: 15
name: Content per section
group: content-wireframes
pipeline_section: content-wireframes
skill: wb-content
prev_phase: 14
next_phase: 16
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/foundation/DESIGN-project-scaffold.md
  - Workstreams/website-builder/foundation/DESIGN-content-layers.md
library_clones_at_entry:
  - resource: component-patterns
    as: component-patterns
    note: "canonical specs for the ~20 most common component types (hero, feature-grid, testimonial, pricing-table, faq, etc.); agent draws first-draft component specs from these"
---

# Phase 15 — Content per section

> Zoom in one level. Phase 13 said what each page does; phase 14 sequenced and laid out the sections; phase 15 specifies what each section *contains* — the components in it, the data it needs, the content placeholders — without writing the final prose yet. The structural-content phase. No gating; this is build-up work. The discipline here is one rule: content and components stay separate.

## Mission

By phase 15 every page has a brief (phase 13) and a wireframe (phase 14). Phase 15 fills the wireframe's boxes with structural content specifications: for every section across the whole site, the components that compose it, the data the section needs to render, and a content placeholder describing what prose will go there (the prose itself comes at phase 16).

This is the phase that turns "the hero section" into a precise spec: a `HeroBlock` component with `headline` (string, ≤60 chars), `sub` (string, ≤120 chars), `cta_text` (string, ≤24 chars, references `{strings.cta.subscribe}`), optional `background_image`. The spec names the component, the fields, the constraints, the data source, and the content intent — everything phase 18 (component build) needs to write code and everything phase 16 (copywriting) needs to write prose.

The single load-bearing discipline of phase 15 is the **content/component separation**. A section's *content* is what it says (headline text, body copy, the specific testimonials). A section's *components* are the reusable shapes that hold the content (a `HeroBlock`, a `TestimonialGrid`, a `FaqAccordion`). Phase 15 keeps these in separate layers: components and their field shapes go to `.website-builder/components.yaml` (Layer 2); content placeholders go in `.website-builder/content/pages/{slug}.md` section bodies (Layer 4 placeholder, finalized phase 16); reusable strings get their keys declared in `.website-builder/content/strings/{lang}.json` (Layer 3, valued at phase 16). When a user mixes these — putting a literal headline string into a component spec, or putting component props into a content body — the agent enforces the separation.

Phase 15 has **no gating rules** beyond the separation enforcement. This is build-up structural work, not a decision phase. The agent moves the user through it section by section without refusing-to-advance behavior, because there is no anti-pattern that breaks downstream work the way an unclear page purpose (phase 13) or skipped wireframe (phase 14) does. The one thing the agent enforces is the content/component separation, and it does so by correcting in place, not by blocking.

## Entry conditions

- Phase 14 (wireframe per page) complete. Every page has a wireframe (in `content/pages/{slug}.md` under `## Wireframe` or a sibling `.wireframe.md`) with section order, per-section layout shape, and responsive intent.
- `.website-builder/content/sections.yaml` exists with every section type the wireframes reference.
- `.website-builder/content/strings/${default_language}.json` skeleton exists (declared at phase 13) with the categorical structure (`cta`, `errors`, `nav`, `variables`, `dates`, `currency`).
- Phase 13 briefs are in scope: each page's `purpose`, `sections[]`, `data_dependencies`, `primary_cta` anchor the per-section specs.

## What Claude must establish

For every section across the entire site (de-duplicated by section type — a section used on 3 pages is specified once), the agent and user produce a content brief specifying:

1. **The component(s) the section uses.** Each section maps to one primary component type from `.website-builder/content/sections.yaml` (e.g., section `hero` → component `HeroBlock`). Composite sections may compose multiple components (a `pricing` section might use a `PricingTable` + `PricingFaq`). The agent names every component the section needs.
2. **The component's fields (props).** For each component, the structured fields it exposes: name, type (string / richtext / image / list / boolean / number / relationship), constraints (max chars, required vs optional, default), and which fields reference Content Design JSON strings (`{strings.path.to.key}`) vs hold page-specific prose. This populates `.website-builder/components.yaml` (Layer 2).
3. **The data the section needs.** Static (content the user supplies) vs dynamic (pulled from CMS collection / Stripe product list / recent-posts query). Drawn from phase 13's `data_dependencies` and specified precisely: source, collection, filter, limit. Drives phase 18's data-fetching code.
4. **A content placeholder per content slot.** For each prose slot the section has (headline, body, caption), a placeholder describing what the prose must accomplish, its approximate length, its voice constraint (from phase 5), and any content source from phase 6's inventory. The placeholder is the brief phase 16 (copywriting) writes against. It is NOT the prose; it is the spec for the prose.
5. **String-key declarations.** Every reusable microcopy slot (CTA labels, error messages, form validation, nav labels) gets its Content Design JSON key declared in `.website-builder/content/strings/${default_language}.json` with an empty or placeholder value. Phase 16 supplies the values. Phase 15 declares the keys so phase 16 has a complete schema to fill and phase 18 has a complete set of references to wire.

The agent also reconciles section reuse: a section type used on multiple pages (e.g., `signup-cta` on `/`, `/essays`, `/about`) is specified once in `components.yaml` + `sections.yaml`; each page's brief references it. The agent surfaces and merges accidental duplicates (two near-identical section specs that should be one reusable type).

The agent updates `.website-builder/project.yaml.current_phase` to `16` upon completion.

## Gating rules

Phase 15 has **no refuse-to-advance gating rules** — it is structural build-up work, not a decision phase. The one discipline the agent enforces (by in-place correction, not by blocking advance) is:

- **Content/component separation.** When the user puts a literal content string into a component spec (`headline: "Welcome to our amazing site"` in `components.yaml`), the agent moves it out: the component spec gets `headline: { type: string, max_chars: 60 }`; the literal string becomes a phase-16 content placeholder in the page body or a Content Design JSON key. Conversely, when the user puts component props (`max_chars`, `variant`, `responsive`) into a content body, the agent moves them to `components.yaml`. The agent corrects and explains the separation each time until the pattern sticks; it does not block phase progression over it.

There is one soft check the agent performs but does not hard-gate:

- **Every section the wireframe shows has a spec.** Before advancing to phase 16, the agent verifies every section across every page wireframe has a corresponding entry in `components.yaml` + `sections.yaml` and a content placeholder in the page body. If a section is unspecced, the agent surfaces it and completes it — but this is a completeness sweep, not a refusal. (The reason this isn't a hard gate: an unspecced section surfaces loudly at phase 16 when there's no placeholder to write prose into and at phase 18 when there's no component to build, so the cost of missing it is bounded and self-correcting, unlike the unbounded drift from a skipped wireframe.)

## Tools and skills used

- **AskUserQuestion** — the primary tool. For each section type the agent asks: *what component holds this? what fields does it need? what data does it pull? what does the prose in each slot need to accomplish?* For sections the user can't spec from scratch, the agent proposes a spec drawn from `.website-builder/library/component-patterns/` and asks the user to confirm or adjust.
- **Write / Edit** — the agent writes `.website-builder/components.yaml` (component specs, Layer 2), updates `.website-builder/content/sections.yaml` (section→component mapping), adds content placeholders to each `content/pages/{slug}.md` section body (Layer 4 placeholder), and declares string keys in `.website-builder/content/strings/${default_language}.json` (Layer 3).
- **Read** — agent reads phase-13 briefs, phase-14 wireframes, `.website-builder/inbox/INVENTORY.md` (phase 6 content sources), `.website-builder/brand.yaml.voice` (phase 5 voice constraints for placeholders).
- **Reference-data load** — `.website-builder/library/component-patterns/` for canonical component specs (the 20 most common component types — hero, feature-grid, testimonial, pricing, faq, etc.); the agent draws first-draft component specs from these and adjusts to the project.
- **WebFetch / WebSearch** — sparingly. The agent may search current component-spec conventions for a novel section type, or fetch a reference site's component to study its field shape (per `DESIGN-templates-catalog.md`: studied, never imported).

The `wb-content` phase-group skill (loaded since phase 13) carries the cross-phase discipline: every section specced here gets prose at phase 16 and code at phase 18 from the same `components.yaml` + page-body files.

## Output artifacts

`.website-builder/components.yaml` — Layer 2 component specs (one entry per unique component type):

```yaml
components:
  - name: HeroBlock
    props:
      headline:    { type: string, max_chars: 60, required: true }
      sub:         { type: string, max_chars: 120, required: false }
      cta_text:    { type: string, max_chars: 24, references: "{strings.cta.subscribe}" }
      cta_href:    { type: string, required: true }
      background_image: { type: image, optional: true, dark_overlay: true }
    behavior:
      - "headline + sub stack vertically; CTA below"
      - "background image (if present) covers full bleed; dark overlay for readability"
    responsive:
      mobile_360:  { headline_size_intent: small, layout: stacked }
      tablet_768:  { headline_size_intent: medium, layout: stacked }
      desktop_1280:{ headline_size_intent: large, layout: stacked }
    accessibility:
      heading_hierarchy: "headline = h1 on home, h2 elsewhere"
      alt_text_required: background_image
      contrast_required: "dark overlay must achieve 4.5:1 against headline color"
    # note: no literal content here. headline TEXT is a phase-16 placeholder in the page body;
    # cta_text VALUE is a Content Design JSON string at strings.cta.subscribe.

  - name: TestimonialGrid
    props:
      heading:     { type: string, max_chars: 48, required: false }
      items:       { type: list, of: TestimonialCard, min: 1, max: 6 }
    data:
      source: cms-collection
      collection: testimonials
      filter: { featured: true }
      limit: 3
    responsive:
      desktop_1280: { layout: "3-col grid" }
      mobile_360:   { layout: "1-col stacked" }
```

`.website-builder/content/sections.yaml` — section→component mapping (updated, not replaced):

```yaml
sections:
  - name: hero
    component_type: HeroBlock
    required_fields: [headline, sub, cta_text, cta_href]
    optional_fields: [background_image]
    used_in: [/, /about]
  - name: social-proof
    component_type: TestimonialGrid
    required_fields: [items]
    used_in: [/, /about]
```

`.website-builder/content/pages/{slug}.md` — section bodies get content placeholders (Layer 4 placeholder, NOT final prose):

```markdown
## Hero section

[CONTENT PLACEHOLDER — phase 16 fills this]
- headline: ≤60 chars. Voice: warm, direct (phase 5). The single sharpest sentence on the site.
  Must communicate what-this-is in one line. Source: phase-1 idea + phase-2 vision.
- sub: ≤120 chars. One supporting line; concrete, not aspirational.
- cta_text: from {strings.cta.subscribe} (declared in strings.json; valued at phase 16)
```

`.website-builder/content/strings/${default_language}.json` — string keys declared (empty values; phase 16 fills):

```json
{
  "$language": "en",
  "$schema": "spec/strings-v1.json",
  "cta": {
    "subscribe": "",
    "subscribe_loading": "",
    "subscribe_success": "",
    "subscribe_error": "",
    "contact": "",
    "essays_read_more": ""
  },
  "errors": {
    "network": "",
    "validation_email": ""
  },
  "nav": {
    "skip_to_content": "",
    "language_switcher_label": "",
    "home": "", "essays": "", "about": "", "contact": ""
  },
  "variables": {},
  "dates": {},
  "currency": {}
}
```

## Common failure modes

**"Just put the headline text in the component."** The most common separation failure. The user wants to write `headline: "Still Humans — essays on staying a person in 2026"` directly into the component spec. The agent moves it: the component spec gets `headline: { type: string, max_chars: 60 }`; the literal sentence becomes a phase-16 content placeholder in the page body. The agent explains once per occurrence: *"the component is the shape; the words are content. They live in different places so you can change the words at phase 16 without touching the component, and so the German version reuses the same component with different words."* The pattern usually sticks after 2-3 corrections.

**"This section needs a custom one-off component."** Sometimes true, often premature. The agent checks `.website-builder/library/component-patterns/` and `components.yaml` for an existing component the section can reuse with different content before creating a new type. A genuinely novel component is fine; a near-duplicate of an existing one (a "HeroBlockV2" that differs from `HeroBlock` only in content) is not — the agent merges. The healthy component count for a typical 5-15 page marketing site is 10-20 distinct types; if component types approach section count, the agent forces de-duplication.

**"I'll write the actual copy here."** Phase 15 is content *spec*, not copy. The agent confirms — *yes, the placeholder is the spec; phase 16 writes the words* — and pushes back if the user starts writing finished prose into placeholders (it's not wrong to draft, but the agent flags that phase-16 voice-consistency pass will re-touch it, so heavy investment now may be redone). Conversely, the agent pushes back on vague placeholders — *"good copy here"* is not a spec; *"≤60 chars, warm-direct voice, communicates what-this-is in one line, sourced from phase-1 idea"* is.

**"What data does the testimonial section pull?"** Surfaces the static-vs-dynamic distinction. If testimonials are 3 fixed quotes the user supplies, they're static content (placeholders in the page body, valued at phase 16). If they're pulled from a CMS collection that grows over time, they're dynamic (a `data:` block in `components.yaml` specifying source / collection / filter / limit, wired at phase 18). The agent surfaces which and specs accordingly. Getting this wrong here means phase 18 builds the wrong data-fetching code.

**Mixing components into content bodies.** The inverse separation failure. The user writes `max_chars: 60` and `responsive: stacked` into a page-body content placeholder. The agent moves these to `components.yaml` — they are component-spec, not content. Page bodies hold content placeholders; `components.yaml` holds shapes.

**Section specced for one page, reused on another with drift.** The `signup-cta` section appears on `/`, `/essays`, `/about`. The user specs it three times with slightly different fields. The agent surfaces the drift, merges to one `CtaBlock` component spec, and each page references it. If the three uses genuinely differ (different headline lengths, different form endpoints), the agent uses component `variants` (per `sections.yaml` `variants:`) rather than three separate components.

**String keys declared but the user wants to value them now.** Phase 15 declares string keys with empty values; phase 16 fills them. The user sometimes wants to write the CTA label here. The agent allows a draft value but flags that phase 16's voice pass owns final string values, and partial values now may be rewritten. The schema completeness (every needed key exists) matters more at phase 15 than the values.

**Hidden assumption that the CMS shape is decided here.** It is not — phase 12 picked the CMS; phase 18 maps `components.yaml` onto the CMS's primitives (Payload Blocks, Decap `list`+`types`, file-based frontmatter `sections[]`). Phase 15's `components.yaml` is stack/CMS-agnostic. The agent surfaces this only when the user asks how a component becomes a Payload Block — the answer is "at phase 18; the spec here is the contract that Block implements."

## Reference materials

Foundation docs:

- `Workstreams/website-builder/foundation/DESIGN-content-layers.md` — the canonical source for the content/component separation this phase enforces. Layer 2 (structural specs → `components.yaml`, `sections.yaml`), Layer 3 (Content Design JSON → string-key declarations), Layer 4 (page-level prose → content placeholders, valued at phase 16). The `## What layer is what concern` diagnostic table is the agent's reference when correcting separation failures.
- `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` § `components.yaml` + `content/sections.yaml` + `content/pages/{slug}.md` — the exact schemas this phase writes.

Content Design JSON methodology (string-key declaration):

- **[How content designers can (and should) use JSON files](https://uxcontent.com/content-design-json/)** — Prasaja Mukti, UX Content Collective, June 10, 2025. Phase 15 declares the Content Design JSON keys; phase 16 values them. The methodology's categorical structure (component-level / feature-specific / system-messaging / dynamic) is the schema the agent uses when declaring keys. The methodology's core discipline — copy as structured reusable data, not scattered strings — is exactly the content/component separation phase 15 enforces.

Component-pattern corpus:

- `.website-builder/library/component-patterns/` — canonical specs for the ~20 most common component types (hero, feature-grid, testimonial, pricing-table, faq-accordion, cta-band, logo-cloud, team-grid, blog-card, contact-form, etc.). The agent draws first-draft component specs from these and adjusts to the project. Reduces the chance of inventing a near-duplicate of a well-understood pattern.
- `.website-builder/library/brand-examples/` — complete brand systems showing how mature brands shape component field sets and reuse components across pages.

Per-CMS structural mappings (relevant because `components.yaml` from this phase consumes CMS shape at phase 18):

- `Workstreams/website-builder/cms/DESIGN-cms-payload.md` § Pages collection with Blocks field — each `components.yaml` entry maps to one Payload `Block`; props map to Payload `fields`; `variants` map to a `select` field.
- `Workstreams/website-builder/cms/DESIGN-cms-decap.md` § list + types widget — `components.yaml` entries map to Decap's typed-union `types` list.
- `Workstreams/website-builder/cms/DESIGN-cms-none.md` § frontmatter section array — file-based markdown's `sections[]` discriminated-union schema (Zod-validated for Astro/static stacks).

WebSearch (recommended for novel section types):

- WebSearch *"component spec / props contract conventions for marketing site sections 2026"* — confirms current professional component-spec practice when the project has a section type not in the pattern corpus.

Freshness date for this contract's references: **2026-05-18**.

## Skip authorization

Phase 15 is not generally skippable, but it has the lowest skip-cost of the content-wireframes group because an unspecced section surfaces loudly and locally (no placeholder to write prose into at phase 16; no component to build at phase 18). The drift is bounded and self-correcting, unlike the unbounded drift from skipping wireframes.

Two narrow legitimate paths:

1. **Phase-6.5 ingestion produced component specs.** When entry mode was `has-existing-site` / `has-ai-output` / `has-Figma-file`, phase 6.5 may have extracted component shapes into `components.yaml` already (Stitch / divmagic / Figma-design-to-json / AI-output parser do this). Phase 15 runs as a completion + reconciliation pass: the agent verifies ingested component specs satisfy the schema, completes any sections the wireframe shows but the ingestion missed, and enforces the content/component separation on the ingested specs (one-shot AI tools commonly mash content into component code; phase 15 separates it). Not a skip; a reconciliation pass.
2. **Mid-project section addition via `wb-postlaunch:section-add` skill.** The post-launch maintainer template (per locked decision 49) includes a `section-add` skill that re-runs a thin phase 15 for the new section only. Not a skip; a scoped replay.

Skipping phase 15 entirely is not authorized. If the user requests it, the agent surfaces that without component specs and content placeholders, phase 16 (copywriting) has nothing to write prose into and phase 18 (component build) has nothing to build from — and offers the fastest path through phase 15 (the agent proposes specs from the component-pattern corpus and the user confirms or adjusts, rather than authoring from scratch). Because phase 15 has no decision-gating, this fast path is genuinely fast; the agent surfaces that skipping it does not save the time the user thinks it does.
