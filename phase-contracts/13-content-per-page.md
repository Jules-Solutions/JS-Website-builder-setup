---
phase: 13
name: Content per page
group: content-wireframes
pipeline_section: content-wireframes
skill: wb-content
prev_phase: 12
next_phase: 14
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/foundation/DESIGN-project-scaffold.md
  - Workstreams/website-builder/foundation/DESIGN-content-layers.md
  - Workstreams/website-builder/foundation/DESIGN-i18n.md
  - Workstreams/website-builder/cross-cutting/DESIGN-templates-catalog.md
library_clones_at_entry:
  - resource: component-patterns
    as: component-patterns
    note: "canonical specs for the ~20 most common component types; agent draws first-draft page section specs from these"
---

# Phase 13 — Content per page

> Every page on the site gets a brief — what it does, who it's for, the section list, the cross-page links — *before* anyone writes a wireframe or a word of prose. The phase that names what each page is doing in the user's journey. Also where Content Design JSON enters the project as the canonical microcopy schema for phases 13-16.

## Mission

The sitemap from phase 9 lists pages and the IA from phase 10 names how users move between them. Phase 13 fills in what each page is actually doing — its conversion contribution, the sections that compose it, the cross-page links pointing in and out, the audience-page-purpose triangle.

The exit of phase 13 is one markdown file per page in `.website-builder/content/pages/{slug}.md`, each with structured frontmatter and a body. The body at this stage is not finalized prose (phase 16 owns that); it is a brief that captures intent — *what this page accomplishes, who reads it, the section order, the data each section needs*. Phase 14 turns these briefs into wireframes; phase 15 fills in section-level content; phase 16 writes the actual prose.

This is also where **Content Design JSON** (per locked decision 25) enters the project as the canonical microcopy schema. Phase 13 declares that every reusable string the site needs — CTAs, error messages, nav labels, form validation, variable copy — will live at `.website-builder/content/strings/{lang}.json` and be referenced from page briefs via the `{strings.path.to.key}` syntax. Phase 13 does not yet write the strings file (phase 16 does); it declares the reference pattern and stubs out the schema so phases 14-16 can build on it.

The agent's discipline in this phase is forcing the user to articulate page purpose in conversion terms. "About page = our story" is the canonical failure — *what conversion does the about page drive?* might be read-more (route to services) / contact (route to inquiry form) / subscribe (route to newsletter signup). Each page has a primary CTA from phase 3's conversion outcome; phase 13 names how each page contributes to that outcome.

## Entry conditions

- Phases 9-12 complete. `.website-builder/sitemap.yaml` exists with `pages[]` and `navigation` fully populated; `project.yaml.stack`, `project.yaml.cms`, and `project.yaml.transactional` are set; `project.yaml.languages` lists configured languages.
- Phases 3 (requirements) and 5 (brand voice) complete. The primary conversion outcome from phase 3 anchors every page's `primary_cta`; the voice attributes from phase 5 shape draft brief language.
- Phase 6 (wild content capture) complete. `.website-builder/inbox/INVENTORY.md` lists existing content sources the agent can draw from when populating each page's brief.
- Phase 6.5 (artifact ingestion) may have already populated some `content/pages/{slug}.md` files if entry mode was `has-existing-site` / `has-ai-output` / `has-Figma-file`. Phase 13 picks up where phase 6.5 left off, completing missing pages and reconciling existing briefs with the locked structural decisions from phases 9-12.

## What Claude must establish

For every page listed in `.website-builder/sitemap.yaml.pages[]`, the agent and user produce a brief file at `.website-builder/content/pages/{slug}.md` containing:

1. **Page purpose (one paragraph).** Not the deliverable ("about page", "services page") but the conversion role — *what user state changes between landing on this page and leaving it*. The phase 3 conversion outcome anchors this: every page either drives the primary conversion directly, prepares the user for it (warming), or supports it (proof / objections-handling / friction-removal).
2. **Section list (ordered).** The sections the page is composed of, in render order, named by their `type` (drawn from `.website-builder/content/sections.yaml` if it exists, or proposed for first-creation). Header and footer are shared globals (referenced, not enumerated per page). Common section types for marketing sites: `hero`, `manifesto`, `feature-grid`, `social-proof`, `pricing`, `testimonial`, `faq`, `signup-cta`, `latest-essays`, `team-grid`, `case-study-grid`, `contact-form`. Each section is one entry; ordered top-to-bottom.
3. **Cross-page links.** Which other pages this page links to, with the link text shape (final prose at phase 16). Drives the site's internal-link graph; surfaces at phase 26 (SEO) for crawlability + internal-link signaling.
4. **Primary and secondary CTAs.** The primary CTA aligns with phase 3's conversion outcome (book / buy / read / contact / subscribe). Secondary CTAs are page-specific (e.g., the about page's primary is *contact*; secondary might be *read more about our approach*).
5. **Data the page needs.** What dynamic data, if any, the page renders — recent blog posts (`pull 3 most recent from /essays`), product catalog (`Stripe product list filtered by category-X`), testimonial set (`featured testimonials from CMS`). Drives the phase-18 component-build instructions.
6. **SEO surface (preview).** Title tag, meta description, social-share image intent. The agent does not finalize SEO content here (phase 26 owns that) but declares the shape so phase 16 (copywriting) can draft.

The agent also declares (at this phase, written to `.website-builder/content/strings/${default_language}.json` as a stub) the **Content Design JSON skeleton**: the categorical structure for reusable strings — `cta`, `errors`, `nav`, `variables`, `dates`, `currency` — with empty values to be filled at phase 16. Per the methodology at [uxcontent.com/content-design-json](https://uxcontent.com/content-design-json/) (Prasaja Mukti, June 2025): the JSON schema mirrors design-system thinking — copy as reusable, structured, version-controlled data, not as scattered strings across pages and components.

The agent updates `.website-builder/project.yaml.current_phase` to `14` upon completion.

## Gating rules

The agent refuses to advance when:

- **A page's purpose isn't clear.** When the user describes a page as *"our story"* or *"about us"* without a conversion role, the agent refuses to capture it and reflects: *"that's what's on the page. What does it do for the user reading it? After they finish, what should they want to do next?"* The exit isn't perfect copy; it's a clear conversion intent.
- **A page has no path to the primary CTA.** If phase 3's primary conversion is *book a discovery call* and a page's brief has no link to the contact / booking page (and isn't itself the contact page), the agent surfaces the gap. Every page connects to the conversion path or has explicit reason to be the exception (e.g., legal pages don't drive the primary CTA; they support it).
- **A section type appears that isn't defined.** If a brief names a section type not in `content/sections.yaml`, the agent surfaces it and either (a) adds it as a new section type to `sections.yaml` (with stub fields for phase 14 to fill), or (b) re-maps to an existing section type. The agent does not silently invent section types — every type must be intentional.
- **A page references content not yet captured.** If a brief lists "testimonials from CMS" but phase 6 didn't capture any testimonials and the CMS isn't yet populated, the agent surfaces the gap and either re-opens phase 6 briefly or flags the section as `status: blocked-on-content` so phase 16 (copywriting) catches it.
- **The Content Design JSON skeleton isn't declared.** Before advancing to phase 14, the agent confirms the strings-file schema exists at `.website-builder/content/strings/${default_language}.json` with at least empty `cta`, `errors`, `nav`, `variables` keys. Phase 16 populates; phase 13 declares.

Override is available on the purpose-clarity gate via explicit user confirmation. The page-without-CTA-path gate is overridable for explicitly non-conversion pages (legal / imprint / 404) with a logged reason.

## Tools and skills used

- **AskUserQuestion** — the primary tool. For each page, the agent asks a series of questions: *what does this page accomplish? what's the primary CTA? what sections compose it? what data does it pull? what's it linked from, and what does it link to?*
- **Read** — agent reads `.website-builder/inbox/INVENTORY.md` from phase 6 to surface available source content per page; reads `.website-builder/project.yaml.requirements` for audience / conversion / competitor positioning; reads `.website-builder/brand.yaml.voice` for voice anchoring in brief drafts.
- **Write** — the agent writes one `content/pages/{slug}.md` file per page in the sitemap; updates `.website-builder/content/sections.yaml` with any new section types; writes the Content Design JSON skeleton to `.website-builder/content/strings/${default_language}.json`.
- **Edit** — the agent iterates on brief content across rounds (user reviews, agent refines, user confirms).
- **Reference-data load** — agent reads `Workstreams/website-builder/cross-cutting/DESIGN-templates-catalog.md` to surface relevant template-as-inspiration for each page-type (per phase 11's stack); `.website-builder/library/awesome-design-md/` for page-archetype examples; `.website-builder/library/brand-examples/` for voice-consistency-in-page-briefs reference.
- **WebFetch** — sparingly, when the user wants to compare a competitor's page-of-same-type for inspiration.

The phase-group skill `wb-content` (per canonical 11-skill scheme) loads at the start of phase 13 and stays loaded through phase 16. The skill carries the discipline that links phases 13-16 together: every brief that phase 13 produces gets a wireframe (phase 14), section-level content (phase 15), and finalized prose (phase 16), all in the same files.

## Output artifacts

For every page in the sitemap, one file at `.website-builder/content/pages/{slug}.md`:

```markdown
---
type: page
slug: /about
status: draft                          # draft | active | published | archived
created: 2026-05-18
updated: 2026-05-18
language: en                           # default language; per-locale variants ship at phase 16
title: "About"                         # display title used in nav / breadcrumbs
seo_title: "About — {strings.site.name}"  # phase 26 finalizes; placeholder here
seo_description: "..."                 # phase 26 finalizes
purpose: |
  Convert qualified prospects browsing the site into discovery-call bookings.
  Visitors arriving here are typically mid-evaluation; they need credibility (track record,
  who we are) and friction-reduction (clear contact path, predictable next step) more
  than additional features.
primary_cta: "{strings.cta.contact}"   # references Content Design JSON; resolved at render
secondary_cta: "{strings.cta.essays_read_more}"
audience: primary                      # primary | secondary — references project.yaml.requirements.audiences
sections: [bio, philosophy, social-proof, contact-cta]   # ordered render list
cross_page_links:
  inbound: [/, /services]              # pages that link TO this one
  outbound: [/contact, /essays]         # pages this one links to
data_dependencies:                     # what dynamic data this page renders
  - source: cms-collection
    collection: testimonials
    filter: { featured: true }
    section: social-proof
relates_to:
  - .website-builder/sitemap.yaml      # parent decision
  - .website-builder/brand.yaml        # voice anchor
---

## Bio section

[Brief: 80-100 words of warm-direct prose; origin story emphasis. Voice attributes from phase 5
apply (warm, direct, contrarian). Content source: phase 6 inventory item `bio-draft-2026-05-10.md`.]

[Placeholder for prose draft at phase 16.]

## Philosophy section

[Brief: 150-200 words. The core thesis — why this project exists, the underlying point of view.
Reference phase 1 idea + phase 2 vision; this section is the public-facing version of those.]

[Placeholder for prose draft at phase 16.]

## Social proof section

[Brief: 3 featured testimonials from the CMS. Each: 1-sentence quote + attribution + headshot.
Section component: TestimonialGrid (defined in components.yaml at phase 18). Data pulled from
{cms-collection: testimonials, filter: {featured: true}}.]

## Contact CTA section

[Brief: end-of-page CTA driving primary conversion. Headline from {strings.cta.contact_headline};
sub from {strings.cta.contact_sub}; button label from {strings.cta.contact}. Form: handled at phase 23.]
```

And `.website-builder/content/strings/${default_language}.json` skeleton:

```json
{
  "$language": "en",
  "$schema": "spec/strings-v1.json",
  "cta": {},
  "errors": {},
  "nav": {},
  "variables": {},
  "dates": {},
  "currency": {}
}
```

If a page brief surfaces a new section type, the agent appends to `.website-builder/content/sections.yaml`:

```yaml
sections:
  - name: bio
    component_type: BioBlock        # the component spec; finalized at phase 18
    required_fields: [headline, body, portrait_image]
    used_in: [/about]
  - name: philosophy
    component_type: TextBlock
    required_fields: [headline, body]
    used_in: [/about, /]
  # ... etc, one entry per unique section type across the site
```

## Common failure modes

**"The about page is just about us."** The canonical failure described in the seed. The agent's response: *"that's the topic. What's the page for? After someone reads it, what should they want to do next? Read more, contact, subscribe — pick one."* The brief then drives prose at phase 16; the agent enforces that the page's structure actually accomplishes the named purpose.

**"Every page has the same primary CTA."** Possible but usually a mistake. If the site's primary conversion is *book a discovery call*, every page can drive toward that — but the *secondary* CTAs differ by page (essays → read more; services → see case study; about → see philosophy). Identical primary + secondary across all pages reads as template-shaped. The agent surfaces per-page differentiation.

**"I'll write the actual copy later."** Phase 13 is *brief-writing*, not *copywriting*. The agent confirms — *yes, the brief is the spec for phase 16; you don't write final copy here* — but pushes back when the brief itself is vague. *"Write your manifesto"* is not a brief; *"150 words explaining why this project exists in warm-direct voice, referenced to phase 1 idea and phase 2 vision"* is.

**"What's a section?"** Surfaces when the user has never thought about pages as section-composed. The agent walks through 2-3 example pages from reference (`.website-builder/library/brand-examples/` if populated; otherwise context7 / WebFetch for stack-appropriate templates per `DESIGN-templates-catalog.md`'s framing: *templates as inspiration, never imported*). The user gradually recognizes that every page is a stack of named, reusable parts.

**Section type proliferation.** Common when the user iterates rapidly — each page invents a new section type. The agent surfaces the inverse — *"this section has the same shape as `philosophy` on the about page; same type, different content"* — and merges duplicates. The healthy section count for a typical 5-15 page marketing site is 8-15 distinct section types; if section types exceed page count, the agent forces de-duplication.

**"What about pages I'll add later?"** Phase 13 captures briefs for every page currently in the sitemap. Future pages (added in phase 32 iteration-roadmap or via the post-launch maintainer skill `wb-postlaunch:page-add`) re-run a thin phase 13 for the new page only. The agent surfaces this so the user doesn't try to pre-emptively brief pages they haven't decided to build.

**Multilingual brief language drift.** When the project is multilingual (per `project.yaml.languages`), the agent writes briefs in the default language at phase 13. Per-language brief variants surface at phase 16 (copywriting) per the translation pattern (Pattern 1 inline, Pattern 2 translator-handoff, Pattern 3 user-driven external tool). Phase 13 does NOT pre-emptively duplicate briefs in every language — that's churn.

**Hidden assumption that the CMS picks which fields are available.** When CMS is Payload, the agent surfaces that section types map onto Payload Blocks at phase 18 — the brief defines the shape, the Block config implements it. When CMS is Decap, section types map onto Decap's `list` + `types` widget. When CMS is `none`, section types map onto frontmatter `sections[]` arrays in markdown files. The agent surfaces this only when the user asks; the brief itself stays stack/CMS-agnostic at phase 13.

## Reference materials

Foundation docs:

- `Workstreams/website-builder/foundation/DESIGN-content-layers.md` § Layer 2 (structural specs) + Layer 3 (Content Design JSON) + Layer 4 (page-level prose). Phase 13 is where Layer 3 enters the project as a declared schema; Layer 2 (sections.yaml + components.yaml) gets populated; Layer 4 placeholders get drafted.
- `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` § `content/pages/{slug}.md` + `content/sections.yaml` — the exact schemas this phase writes to.
- `Workstreams/website-builder/foundation/DESIGN-i18n.md` — Pattern A vs Pattern B for per-language page prose (relevant when project is multilingual).
- `Workstreams/website-builder/cross-cutting/DESIGN-templates-catalog.md` — templates as inspiration sources (never imported); referenced for page-archetype-by-page-type.

Content Design JSON canonical source:

- **[How content designers can (and should) use JSON files](https://uxcontent.com/content-design-json/)** — Prasaja Mukti, UX Content Collective, June 10, 2025. The canonical methodology source. Core principles: copy as structured version-controlled data; categorical structure (component-level, feature-specific, system messaging, dynamic); variables (user, contextual, system-status, data); per-language folder structure mirrors single source-of-truth. Cited in this contract because phase 13 is where the methodology enters the project.
- Pairing source: `Workstreams/website-builder/foundation/DESIGN-content-layers.md` § Layer 3.

Per-page-type inspiration corpus:

- `.website-builder/library/awesome-design-md/` (cloned from VoltAgent/awesome-design-md at phase 17 if not earlier) — 60+ DESIGN.md exemplars surfacing how mature brands shape page-types.
- `.website-builder/library/brand-examples/` — 5-8 complete brand systems showing voice + tokens + component patterns; relevant references for phase-13 brief language.
- Per-stack template catalog (per `DESIGN-templates-catalog.md`) — for the stack picked at phase 11, the agent surfaces curated templates as inspiration when the user asks for examples.

Per-CMS structural mappings (relevant at phase 13 because section types lock here and consume CMS shape at phase 18):

- `Workstreams/website-builder/cms/DESIGN-cms-payload.md` § Pages collection with Blocks field — Payload's `blocks` array maps directly onto `sections[]` from this phase.
- `Workstreams/website-builder/cms/DESIGN-cms-decap.md` § list + types widget — Decap's typed-union maps onto `sections[]`.
- `Workstreams/website-builder/cms/DESIGN-cms-none.md` § frontmatter section array — file-based markdown's `sections[]` in frontmatter is the direct shape.

WebSearch / WebFetch (recommended at this phase):

- WebSearch *"content brief templates for marketing site pages 2026"* — confirms current professional-content-design practice; cited in any briefs that surface novel page-type patterns.
- WebSearch *"page-purpose vs page-topic content strategy"* — surfaces current writing about the conversion-anchored vs subject-anchored framing the agent enforces.

Freshness date for this contract's references: **2026-05-18**.

## Skip authorization

Phase 13 is not skippable. The briefs it produces are the spec phases 14-16 build on. Without briefs, phase 14 (wireframes) has nothing to shape into layout, phase 15 (per-section content) has nothing to populate, and phase 16 (copywriting) writes drift.

Two narrow legitimate paths:

1. **Mid-project page addition via `wb-postlaunch:page-add` skill.** The post-launch maintainer template (per locked decision 49) includes a `page-add` skill that re-runs a thin phase 13 for the new page only. Not a skip; a scoped replay.
2. **Phase-6.5 ingestion seeded the briefs.** When entry mode was `has-existing-site` and phase 6.5 ingested a deployed site, briefs for existing pages may already exist. Phase 13 still runs as a confirmation + completion pass: the agent verifies the ingested briefs satisfy the schema and completes any missing pages.

Skipping phase 13 entirely is not authorized. If the user requests it, the agent surfaces that without per-page briefs, the agent has no instructions on what each page is supposed to accomplish, and routes back to the per-page conversation.
