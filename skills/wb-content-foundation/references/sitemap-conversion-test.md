# Phase 9 — Sitemap + conversion-test reference

> Loaded when running phase 9. The conversion-test challenge patterns, page-count-rationale construction, legal-page reservation rules, page-vs-section disambiguation, non-greenfield extracted-sitemap handling. Source of truth: `${CLAUDE_PLUGIN_ROOT}/phase-contracts/09-sitemap.md` + `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` § sitemap.yaml + `DESIGN-content-layers.md` § Layer 2.

## What phase 9 produces

`.website-builder/sitemap.yaml` — every page with `slug` / `type` (home | about | service-index | service-detail | work-index | work-detail | blog-index | blog-post | contact | pricing | legal | landing | utility) / `title` / `purpose` (one sentence) / `conversion_contribution` / `primary_cta` / `parent` (breadcrumb tree) + a `page_count_rationale`. `sections:` per page is deferred to phase 13; `navigation:` zones are phase 10's job.

**Stack-independent by design** — per the architecture's stack-late-binding property, the sitemap survives a later phase-11 stack change. Bake NO stack assumption (no `.astro`/`.tsx` route hints).

## The gating test: the phase-3 conversion outcome

Reread `project.yaml.requirements.conversion_outcome` before opening the phase-9 conversation. It is the test every proposed page must pass. Every page must either directly drive the conversion, build trust toward it, or be legally/structurally mandatory. "Informational only" is challenged.

The discipline is NOT minimalism for its own sake — it is the recognition that every page is a maintenance liability + a content debt (phase 13-16) + an attention split against the phase-3 1:1 conversion. A 5-page site that converts beats a 30-page site nobody finishes building. But under-structuring is challenged with the same test.

## Conversion-test challenge patterns

| Situation | Challenge |
|---|---|
| **47 pages** (every idea became a page) | Surface the cost concretely: "47 pages = 47 content briefs, 47 wireframes, 47 copywriting passes, 47 pages to keep current forever — most don't move the conversion." Test each. Services sprawl → one strong "how I work" + work examples. Aspirational blog → phase-32 roadmap (empty blog hurts more than no blog). Team page for a solo practice → that's about. Press/careers/glossary → roadmap. "I think this is a 6-8 page site. Let's find which 6-8." |
| **"Every page is essential"** | Don't override authority — make cost undeniable, reframe around the conversion: "For each page you call essential, tell me the one sentence: how does this move someone toward [conversion]? If you can say it cleanly, it earns its place + that sentence becomes its `purpose`. If it's a stretch, that's the signal the page's job isn't clear — which makes phase 13-16 unanchored." Converts "fewer pages" (agent preference) into "every page has a clear job" (the discipline). |
| **Blog, no content, no cadence** | "A blog at launch with two posts + no cadence reads worse than no blog — signals 'abandoned' by the third visit. (a) no blog, add at phase 32 with a real cadence + backlog; (b) blog only if you commit a cadence now + treat the first 6-8 posts as phase-16 deliverables. Aspirational blogs are the most common post-launch rot." Record in the scope doc as a *planned* deferral. |
| **Under-structuring** (one-pager for something deep) | Same conversion test: "Can a prospect evaluating you find the proof they need before they lose patience? If proof is deep, it usually wants its own surface (a /work index + detail) the home points to. Not 30 pages — but probably more than 1." |
| **Non-greenfield: 6.5 extracted 30 pages** | "That extraction is a record of what *was*, not a constraint on what *should be*. Most rebuilds are also a structure-prune: which earned visits + moved conversions (your analytics know)? Run the 30 through the conversion test as if they were proposals." No special preservation weight. |
| **Pages whose content doesn't exist + isn't planned** | "This needs content not in the phase-6 inventory or phase-8 plan. (a) created as phase-16 deliverables (real scope — committing to writing the 5 case studies?); (b) deferred to phase-32 roadmap; (c) drop. A page with no path to content is a phase-13 dead end." |
| **Page-vs-section confusion** | Disambiguate: testimonials usually stronger as a *section next to the work it describes*; process often a section on about/service; pricing a page if a conversion-relevant decision surface, a section if one number; team a section on about for a small practice. "The test: would a visitor navigate *to* this deliberately, or encounter it *within* a page they came for?" Pages → sitemap; sections → feed phase 13-15. |

## Legal-page reservation (non-negotiable — part of the anti-vision lock)

Driven by phase-4 `entity.location.jurisdiction`:
- **Privacy policy** — always (GDPR / revFADP / CCPA when the audience includes those regions).
- **Imprint** — mandatory in DACH (CH/DE/AT).
- **Cookie-consent** — when tracking integrations are planned (phase-3 requirements).

Phase 9 *reserves the slugs* (`/privacy`, `/imprint`, `/cookie-consent` as needed); phase 25 authors the content with the user's actual data-handling facts. The override path does NOT apply to legally-mandatory pages — the agent can only adjust *when* their content is authored (phase 25), never *whether* they exist. Surface: *"Your phase-4 jurisdiction is Switzerland — imprint is legally mandatory, not optional. I'm reserving `/imprint` + `/privacy` now; phase 25 writes their content. These can't be dropped."*

## page_count_rationale construction

A short prose rationale: why this many pages, why not fewer, why not more. Surfaced (and required to survive scrutiny) when the count is contested — which is most of the time, since page sprawl is the default failure. Records the collapse/defer decisions so phase 13+ and the post-launch maintainer's `page-add` skill know what was *deliberately deferred* vs *forgotten*. Example pattern: "7 pages: 1 home (conversion surface), 1 work-index + 1 representative work-detail (credibility), 1 about (de-risk), 1 contact (conversion endpoint), 2 legal (jurisdiction-mandatory). User initially wanted 5 service pages + blog + testimonials; collapsed services into home+about narrative, deferred blog to phase-32 roadmap, folded testimonials into work-detail."

## Output + gating

`.website-builder/sitemap.yaml` (required, per the phase-9 contract schema). `.website-builder/decisions/09-sitemap-scope.md` (conditional — created when page count was contested, which is most of the time; records alternatives + reasoning so phase 32 + the maintainer know intentional-deferral vs out-of-scope-forever).

Refuse to advance to phase 10 under: (1) a page with no conversion contribution (challenge it — fold / give it a conversion job / defer to roadmap); (2) page sprawl without a scrutiny-surviving `page_count_rationale` + the agent's cost-surfacing on record; (3) missing legally-mandatory pages. Override applies to page-count (recorded rationale + cost on record) and non-mandatory pages (weak-conversion page can stay if the user insists, recorded as such) — NOT to legal pages. On lock (`status: sitemap-locked` + every page has a conversion contribution or recorded override + legal slugs reserved), advance to phase 10 (architecture group — a different skill's territory; the sitemap is the hand-off artifact between this skill's batch and the next).

`AskUserQuestion` is the dominant tool — every proposed page interrogated, every collapse/defer the user's decision, the rationale built conversationally. `WebFetch` to load competitor sitemaps (from phase-3 competitor URLs) to ground page-convention expectations (a consulting site is expected to have a work/case-study surface; a SaaS pricing) — to inform, not copy.
