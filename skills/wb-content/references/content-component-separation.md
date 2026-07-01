# Phase 15 — Content/Component Separation

Detailed patterns for the phase-15 content-per-section workflow. The single load-bearing discipline of phase 15. Source of truth: `Projects/Jules.Solutions/Subprojects/website-builder/phase-contracts/15-content-per-section.md` + `DESIGN-content-layers.md` (the canonical separation reference).

## The separation, stated

- A section's **content** is *what it says* — the headline text, the body copy, the specific testimonials. Lives in: page bodies (`content/pages/{slug}.md` section bodies, Layer 4 placeholder, valued at phase 16) + Content Design JSON (`content/strings/{lang}.json`, Layer 3, valued at phase 16).
- A section's **component** is *the reusable shape that holds the content* — a `HeroBlock`, a `TestimonialGrid`. Lives in: `.website-builder/components.yaml` (Layer 2).

They live in separate layers **so each can change without breaking the other**: the German version reuses the same component with different words; the headline can be rewritten at phase 16 without touching the component; the component can be restyled at phase 17 without touching the words.

Phase 15 enforces this by **in-place correction, not by blocking advance**. Correct and explain each time until the pattern sticks (usually 2-3 corrections).

## The diagnostic table (from DESIGN-content-layers.md "What layer is what concern")

When something needs to change, which layer?

| Concern | Layer | File |
|---|---|---|
| Site colors / typography wrong | 1 | `brand.yaml` |
| Add a new page | 2 + 4 | `sitemap.yaml` + new page MD |
| Add a new section type | 2 | `sections.yaml` + `components.yaml` |
| Component *shape* needs to change | 2 | `components.yaml` |
| Button label inconsistent across pages | 3 | `strings.json` — was it inlined? move it. |
| Add a new language | 3 | new `{lang}.json` |
| Hero *copy* needs rewriting | 4 | page MD |
| About-page narrative reordering | 4 | page MD |
| ChatGPT component generation | 5 | emit brief |

This table is the agent's reference when correcting separation failures: name the concern, name the layer, move the misplaced thing there.

## Workflow

For every section type across the site (de-duplicated — a section on 3 pages is specced once):

1. **Component(s) the section uses.** Each section maps to one primary component type in `sections.yaml` (section `hero` → component `HeroBlock`). Composite sections compose multiple (`pricing` → `PricingTable` + `PricingFaq`).
2. **Component fields (props).** Name, type (`string | richtext | image | list | boolean | number | relationship`), constraints (`max_chars`, `required`, `default`), and which fields reference Content Design JSON strings (`references: "{strings.cta.x}"`) vs hold page-specific prose. Populates `components.yaml`.
3. **Data the section needs.** Static (user supplies → page-body placeholder, valued phase 16) vs dynamic (CMS collection / Stripe product list / recent-posts → a `data:` block in `components.yaml` with source/collection/filter/limit, wired phase 18). Getting this wrong builds the wrong data-fetching code at 18.
4. **Content placeholder per prose slot.** A spec, not prose: approximate length, voice constraint (phase 5), content source (phase 6 inventory). The brief phase 16 writes against.
5. **String-key declarations.** Every reusable microcopy slot gets its key declared in `strings/${default_language}.json` with empty/placeholder value. Phase 16 supplies values.

Propose first-draft specs from `.website-builder/library/component-patterns/` (the ~20 canonical types — hero, feature-grid, testimonial, pricing-table, faq-accordion, cta-band, logo-cloud, team-grid, blog-card, contact-form, etc.) and let the user adjust rather than author from scratch.

Reconcile reuse: a section type used on multiple pages is specced once; each page references it. Merge accidental near-duplicates; use component `variants` (per `sections.yaml`) when uses genuinely differ rather than creating near-duplicate components. Healthy component count for a 5-15 page site: **10-20 distinct types**; if component count approaches section count, force de-duplication.

## Gating

**No refuse-to-advance gating.** Phase 15 is structural build-up, not a decision phase. Two things only:

1. **Separation enforcement** — corrected in place, never blocks advance.
2. **Soft completeness sweep** — before advancing to 16, verify every section the wireframe shows has a `components.yaml` entry + a content placeholder. A sweep, not a refusal: an unspecced section surfaces loudly and locally at phase 16 (no placeholder to write into) and phase 18 (no component to build). Bounded, self-correcting drift — unlike the unbounded drift from a skipped wireframe.

## Common failure modes (phase 15)

| Failure | Recovery |
|---|---|
| "Just put the headline text in the component" | The most common failure. Move it: component gets `headline: {type: string, max_chars: 60}`; the literal sentence becomes a phase-16 placeholder in the page body. Explain once per occurrence (the German-version + change-words-without-touching-component rationale). Sticks after 2-3. |
| "This section needs a custom one-off component" | Often premature. Check `.website-builder/library/component-patterns/` + `components.yaml` for a reusable existing type first. Genuinely novel = fine; near-duplicate ("HeroBlockV2" differing only in content) = merge. |
| "I'll write the actual copy here" | Phase 15 is content *spec*, not copy. Allow drafting but flag phase-16 voice pass will re-touch it. Push back on vague placeholders — *"good copy here"* is not a spec; *"≤60 chars, warm-direct, communicates what-this-is in one line, sourced from phase-1 idea"* is. |
| "What data does the testimonial section pull?" | The static-vs-dynamic distinction. 3 fixed user-supplied quotes = static (page-body placeholders). CMS collection that grows = dynamic (`data:` block, wired phase 18). Spec accordingly — wrong here = wrong data-fetching code at 18. |
| Mixing components into content bodies | Inverse failure. `max_chars: 60` / `responsive: stacked` in a page-body placeholder → move to `components.yaml`. Page bodies hold content; `components.yaml` holds shapes. |
| Section reused with drift | `signup-cta` on `/`, `/essays`, `/about` specced 3× with slight differences → merge to one `CtaBlock`; each page references it. Genuine differences → component `variants`, not 3 components. |
| "String keys declared but I want to value them now" | Allow a draft value; flag phase 16's voice pass owns final values. Schema completeness (every needed key exists) matters more at 15 than the values. |
| "Is the CMS shape decided here?" | No. Phase 12 picked the CMS; phase 18 maps `components.yaml` onto CMS primitives. `components.yaml` stays stack/CMS-agnostic at 15. Surface only if asked. |

## Per-CMS structural mappings (relevant because components.yaml consumes CMS shape at phase 18)

Surface only when the user asks how a component becomes a CMS primitive — the answer is always "at phase 18; the phase-15 spec is the contract that primitive implements":

- **Payload** (`DESIGN-cms-payload.md` § Pages collection with Blocks field): each `components.yaml` entry → one Payload `Block`; props → Payload `fields`; `variants` → a `select` field.
- **Decap** (`cms/DESIGN-cms-decap.md` § list + types widget): `components.yaml` entries → Decap's typed-union `types` list.
- **none** (`cms/DESIGN-cms-none.md` § frontmatter section array): file-based markdown's `sections[]` discriminated-union schema (Zod-validated for Astro/static stacks).

## Output artifact schemas (phase 15)

- `.website-builder/components.yaml` — Layer 2, one entry per unique component: `name`, `props` (typed + constrained), `behavior[]`, `responsive` (per-breakpoint intent), `accessibility` (heading hierarchy, alt-text-required, contrast), optional `data` block for dynamic sections. **No literal content** — comment-flag that headline TEXT is a phase-16 placeholder and `cta_text` VALUE is a Content Design JSON string.
- `.website-builder/content/sections.yaml` — section→component mapping: `name`, `component_type`, `required_fields[]`, `optional_fields[]`, `used_in[]`.
- `.website-builder/content/pages/{slug}.md` section bodies — `[CONTENT PLACEHOLDER — phase 16 fills this]` with the per-slot spec (length, voice, source, string-key references).
- `.website-builder/content/strings/${default_language}.json` — keys declared, empty values.

Exact worked schemas in the phase-15 contract `## Output artifacts`.
