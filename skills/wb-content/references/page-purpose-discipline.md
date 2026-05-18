# Phase 13 — Page-Purpose Discipline

Detailed patterns for the phase-13 content-per-page workflow. The SKILL.md summarizes; this file carries the recovery scripts and the conversion-anchoring detail. Source of truth: `Projects/Jules.Solutions/Subprojects/website-builder/phase-contracts/13-content-per-page.md` + `Workstreams/website-builder/foundation/DESIGN-content-layers.md` § Layer 2/4.

## The audience-page-purpose triangle

Every page brief resolves three things together; none alone is a brief:

1. **Audience** — `primary` or `secondary` per `project.yaml.requirements.audiences` (phase 3). Who lands on this page and in what mental state (cold / evaluating / ready).
2. **Page purpose** — the conversion role: what user-state changes between landing and leaving. Every page either *drives* the primary conversion, *warms* toward it, or *supports* it (proof / objection-handling / friction-removal).
3. **Primary CTA** — anchored to phase 3's single conversion outcome (book / buy / read / contact / subscribe). Secondary CTAs are page-specific.

A brief that names the topic but not the conversion role is incomplete. The exit of the per-page conversation is a clear conversion intent, not perfect copy.

## The "about page is just about us" recovery

The canonical failure. The user describes a page by its subject ("our story", "about us", "what we do") with no conversion role.

Recovery script (shape, not verbatim — adapt to the user's voice):

> *"That's what's on the page — the topic. What does it do for the person reading it? They land on the about page mid-evaluation; after they finish reading, what should they want to do next? Read more (route to services), contact (route to the inquiry form), subscribe (route to newsletter)? Pick the one that matters most — that's the page's job, and it's what the copy at phase 16 will be written to accomplish."*

Then capture: `purpose:` (the conversion paragraph), `primary_cta:` (the routed action), `secondary_cta:` (the page-specific alternative).

## Every page connects to the conversion path

Gate: if phase 3's primary conversion is *book a discovery call* and a page's brief has no link to the contact/booking page (and isn't itself that page), surface the gap. Every page connects to the conversion path or has an explicit logged reason to be an exception.

Legitimate exceptions (override with logged reason): legal / imprint / privacy / 404. These *support* the conversion (trust, compliance) rather than drive it — that's a valid purpose, just declare it explicitly rather than leaving the page purposeless.

## Section-type proliferation

Common when the user iterates fast — each page invents a new section type. Healthy count for a 5-15 page marketing site: **8-15 distinct section types**. If section types exceed page count, force de-duplication.

The merge prompt (shape): *"this section has the same shape as `philosophy` on the about page — same type, different content. One section type, reused."* Append merged types to `content/sections.yaml` with `used_in: [...]` listing every page.

The inverse — a genuinely novel section type — is fine. Add it to `sections.yaml` with stub fields for phase 14 to fill. The discipline is intentionality, not minimalism: every section type is deliberate, not accidental.

## Common failure modes (phase 13)

| Failure | Recovery |
|---|---|
| "The about page is just about us" | The recovery script above — force the conversion answer. |
| "Every page has the same primary + secondary CTA" | Primary can be shared (one site conversion); secondary must differ per page (essays→read more; services→case study; about→philosophy). Identical both = template-shaped; surface per-page differentiation. |
| "I'll write the actual copy later" | Correct — phase 13 is brief-writing, not copywriting. But push back on vague briefs: *"write your manifesto"* is not a brief; *"150 words on why this project exists, warm-direct voice, ref phase-1 idea + phase-2 vision"* is. |
| "What's a section?" | Walk through 2-3 example pages from `reference/brand-examples/` (or WebFetch a stack-appropriate template per `DESIGN-templates-catalog.md`, studied not imported). The user learns pages are stacks of named reusable parts. |
| "What about pages I'll add later?" | Phase 13 briefs only pages currently in the sitemap. Future pages re-run a thin phase 13 via `wb-postlaunch:page-add`. Surface this so the user doesn't pre-emptively brief undecided pages. |
| Multilingual brief-language drift | Write briefs in the default language only at phase 13. Per-language variants surface at phase 16. Do NOT pre-duplicate briefs per language — that's churn. |
| "Which CMS fields are available?" | Section types map onto CMS primitives at phase 18 (Payload Blocks / Decap list+types / file-based frontmatter `sections[]`). Brief stays stack/CMS-agnostic at 13. Surface only if asked. |

## The Content Design JSON skeleton (declared at phase 13)

Before advancing to phase 14, confirm `.website-builder/content/strings/${default_language}.json` exists with at least empty `cta`, `errors`, `nav`, `variables` keys (also `dates`, `currency`). Phase 13 *declares* the schema; phase 15 declares specific keys; phase 16 values them. Skeleton:

```json
{
  "$language": "en",
  "$schema": "spec/strings-v1.json",
  "cta": {}, "errors": {}, "nav": {}, "variables": {}, "dates": {}, "currency": {}
}
```

See `references/content-design-json.md` for why the categorical structure looks like this.

## Output artifact schema (phase 13)

One `.website-builder/content/pages/{slug}.md` per sitemap page. Frontmatter: `type, slug, status (draft), created, updated, language, title, seo_title, seo_description, purpose (the conversion paragraph), primary_cta ({strings.cta.x}), secondary_cta, audience (primary|secondary), sections[] (ordered), cross_page_links {inbound[], outbound[]}, data_dependencies[], relates_to[]`. Body: one `## {Section} section` heading per section with a `[Brief: ...]` note + `[Placeholder for prose draft at phase 16.]`. Exact schema in the phase-13 contract `## Output artifacts`.
