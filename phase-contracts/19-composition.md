---
phase: 19
name: Composition (putting it together)
group: build-integration
pipeline_section: build-integration
skill: wb-build-integration
prev_phase: 18
next_phase: 20
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - DESIGN-phase-contracts.md
  - DESIGN-architecture.md
  - DESIGN-project-scaffold.md
  - DESIGN-content-layers.md
  - ${CLAUDE_PLUGIN_ROOT}/reference-corpus/ECOSYSTEM-CATALOG.md
  - DESIGN-context7-integration.md
---

# Phase 19 — Composition (putting it together)

> Assemble every page in the sitemap from the phase-18 components, wiring in the phase-16 content, in the user's chosen stack. The phase where the parts become a site. This is the assembly phase — there are no upstream-discipline gates here because the discipline already happened (phases 14, 16, 17, 18). The agent's job is faithful assembly plus catching the structural problems that only appear when real content meets real components at real page scale.

## Mission

Phases 14-18 produced everything a page is made of: the wireframe (section order + layout intent), the finalized copy, the design tokens, the built components. Phase 19 puts them together — for every page in `sitemap.yaml`, the agent composes the page from its phase-18 components, wires in its phase-16 content, follows its phase-14 wireframe, and produces a rendered page in the user's chosen stack.

The work product is assembled pages in the user's project: real routes, real components, real content, rendering. After phase 19, the site exists and can be looked at — it is not yet responsive-verified (phase 20), a11y-audited (phase 21), perf-audited (phase 22), or forms-wired (phase 23), but it is a coherent site, not a pile of components.

Phase 19 is deliberately **low-gating**. The discipline-heavy refusals live upstream: phase 14 refused to skip wireframing, phase 16 refused placeholder copy, phase 17 refused arbitrary color, phase 18 refused hardcoded values and inconsistent components. By phase 19 the inputs are correct by construction; the agent's job is faithful assembly, not re-litigation. The one thing phase 19 *does* catch is the class of problem that is invisible until assembly: content overflow, section-rhythm breakage, and wireframe-vs-reality mismatches that only surface when the real copy meets the real component at the real page width.

## Entry conditions

- Phase 18 (component design / build) complete. `.website-builder/components.yaml` has a spec + reviewed code for every component the site needs; `project.yaml.component_library` is locked. Page composition was explicitly gated until every component existed (phase 18's hard gate) — so entering phase 19 means the parts are all built.
- Phase 16 (copywriting) complete. Every `content/pages/{slug}.md` has finalized prose; every `content/strings/*.json` key has a real value. Composition wires real content, not placeholders.
- Phase 14 (wireframe per page) complete. Every page has a wireframe (section order + per-section layout + responsive intent). The wireframe is the assembly blueprint; phase 19 follows it.
- Phase 11 (stack decision) complete. `project.yaml.stack` is set; the stack adapter's composition conventions (routing, layout nesting, Server/Client boundaries for Next App Router, island directives for Astro) govern how pages are assembled.
- Phase 9-10 (sitemap + IA) complete. `sitemap.yaml` lists every page + its route; `sitemap.yaml.navigation` defines the shared header/footer regions every page composes.

## What Claude must establish

Every page in `sitemap.yaml.pages[]`, assembled in the chosen stack:

1. **Route + page shell.** The page exists at its sitemap route, in the stack's routing convention (`app/{route}/page.tsx` for Next App Router, `src/pages/{route}.astro` for Astro, `content/{route}.md` + layout for Hugo, etc.). The shared header + footer (from phase-10 IA, built as components in phase 18) wrap every page consistently — wireframed once, referenced everywhere, never redrawn per page.
2. **Section composition per the wireframe.** Each page's sections appear in the phase-14 committed order, each rendered with its phase-18 component(s), at the phase-14 layout shape (full-bleed vs contained, single-col vs grid vs split).
3. **Content wired in.** Phase-16 prose from `content/pages/{slug}.md` flows into the section components; phase-16 string keys from `content/strings/{lang}.json` resolve into microcopy/CTA/state-label slots. For multilingual sites, per-language pages compose per the locked i18n pattern (Pattern A shared structure / Pattern B market variation, from phase 12/16).
4. **Token-faithful rendering.** Because phase-18 components are token-driven, assembled pages render in the phase-17 design system automatically — the agent verifies no composition-level hardcoding crept in (a one-off inline style at the page level instead of a component prop).
5. **Build passes.** The project builds in the chosen stack (`next build`, `astro build`, `hugo`, etc.) with no errors. A page that doesn't compile is not composed.

Output: assembled pages in the user's project source tree (per stack convention). `.website-builder/project.yaml.current_phase` updates to `20` upon a clean build + the user confirming the site renders as intended. Phase 20 (responsive / mobile pass) loads next.

## Gating rules

Phase 19 has **no upstream-discipline gate** — this is the assembly phase, and the discipline already happened. The agent does not re-refuse decisions phases 14-18 already locked. It does, however, refuse to advance when:

- **A sitemap page is not composed.** Every page in `sitemap.yaml.pages[]` must exist as a rendered route. A missing page is not advance-able (phase 20-30 all assume the full site exists).
- **The build fails.** The project must build cleanly in the chosen stack. Composition that doesn't compile is not composition. The agent fixes the build error (often a Server/Client boundary issue in Next, or a missing island directive in Astro — verified against current stack docs via context7) before advance.
- **Content overflows or breaks section rhythm and the agent has not surfaced it.** When real phase-16 copy is longer than the phase-14 wireframe assumed and a section visibly breaks, the agent must surface it and propose a fix (tighten copy → thin phase-16 re-touch; or adjust the section layout → thin phase-14 re-touch; the user decides which). Silently shipping a broken section is the failure phase 20/27 then pays for.
- **A page composes a component that isn't in `components.yaml`.** If assembly reveals a needed component nobody built, that is a phase-18 gap — the agent surfaces it and returns to phase 18 for that component (it does not improvise an unspecced component inline).

These are completeness/correctness gates, not discipline refusals. There is no override concept here — a site with a missing page or a failing build is not a site.

## Tools and skills used

- **`Edit` / `Write`** — the primary tools. The agent writes page/route files in the chosen stack's convention, composing the phase-18 components and wiring phase-16 content.
- **`Bash`** — for the stack's build command (`next build`, `astro build`, `hugo`, `vite build`, etc.) to verify the project compiles, and for the dev server when a live render is needed.
- **`mcp__context7__resolve-library-id` + `mcp__context7__query-docs`** — per `DESIGN-context7-integration.md`, phase 19 invokes context7 for stack-specific routing + composition patterns (Next App Router layout nesting + Server/Client rules, Astro dynamic-param routing + island hydration directives, Hugo content + layout pairing). Composition is where stale routing knowledge produces broken builds; the agent verifies current patterns.
- **Playwright MCP** — for a visual check of the assembled pages (the agent walks the rendered site, confirming sections appear in order, content is wired, nothing is obviously broken). This is a sanity render, not the formal responsive (phase 20) or QA (phase 27) pass.
- **`Read`** — `sitemap.yaml` (page list + routes + nav), `content/pages/{slug}.md` (the content + the phase-14 wireframe), `components.yaml` (the component contracts), `brand.yaml.tokens` (to verify token fidelity at composition level).
- **Reference-data load** — `${CLAUDE_PLUGIN_ROOT}/reference-corpus/component-patterns/` for canonical section-composition archetypes; the chosen `component-libraries/{stack}.md` for stack-specific composition idioms. Per `DESIGN-templates-catalog.md`, templates may be surfaced as composition-pattern inspiration (how a reference site sequences a page) but are never imported — the page is composed from *this* project's components.

The `wb-build-integration` phase-group skill is loaded at entry (and stays loaded through phases 19-23 — it is the single skill for the whole build-integration group per the canonical 11-skill scheme, Decision 64). It carries the cross-phase contract that phase 20 verifies the responsive behavior of exactly these assembled pages, phase 21 audits their a11y, phase 22 their performance, phase 23 their forms.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| Page/route files in the user's project | per chosen stack convention (`app/**/page.tsx`, `src/pages/**.astro`, `content/**.md` + layouts, etc.) | The assembled pages — real routes, real components, real content. The site itself. |
| Shared layout/region files | per stack convention (e.g. `app/layout.tsx`, `src/layouts/Base.astro`) | The header/footer/shared regions wrapping every page (from phase-10 IA, phase-18 components). |
| `.website-builder/project.yaml` | `current_phase: 20` on clean build + user confirm | Phase progression marker. |
| `.website-builder/decisions/19-composition-{note}.md` *(optional)* | standard decision-doc frontmatter | Created only when assembly surfaced a non-obvious structural decision (e.g. a section had to be re-laid-out because real content didn't fit the wireframe). |

The assembled pages + a passing build are the required outputs. A decision log is produced only when a structural reconciliation happened.

## Common failure modes

**Content overflow on long sections.** The canonical phase-19 failure. The phase-14 wireframe assumed a 2-line hero headline; the phase-16 copy is 4 lines; at desktop width the hero now pushes the next section below the fold awkwardly, or the text clips. The agent surfaces it — *"the real headline is longer than the wireframe assumed; this section breaks. Two fixes: tighten the headline to fit the layout, or adjust the section to hold the longer copy. Which?"* — and applies the user's choice (a thin phase-16 or phase-14 re-touch). It does not silently ship the broken section.

**Build breaks on a Server/Client boundary.** In Next App Router, a page (Server component) imports a phase-18 form component (Client component) without the boundary handled, and `next build` fails. The agent verifies the current App Router Server/Client rules via context7 and fixes the boundary (the form is `'use client'`; the page stays Server) rather than guessing from stale training data.

**Assembly reveals a missing component.** A section's wireframe needs a component nobody specced in phases 13-15 and nobody built in phase 18. The agent does NOT improvise an unspecced component inline — that bypasses the phase-18 discipline. It surfaces the gap and returns to phase 18 for that one component (specced, built, reviewed), then resumes composition.

**Hardcoding at the composition level.** The components are token-faithful, but the agent (or pasted code) drops a one-off inline style at the page level — `<section style={{ marginTop: 80 }}>` where a spacing token belongs. The agent's composition-level token sweep catches this; page assembly must be as token-faithful as the components.

**Per-page header/footer drift.** The agent re-implements the header slightly differently on one page. The shared regions are locked by phase-10 IA and built once in phase 18 — every page references the same shared layout. The agent unifies any drift (a consistent-navigation concern, WCAG 2.4.5/3.2.3, that phase 21 would otherwise flag).

**"Just assemble it, we'll see how it looks."** Composition without checking the build or the render produces a site that doesn't compile or has broken sections discovered three phases later. The agent builds + does a Playwright sanity-walk as part of phase 19, not as a deferred check.

**Treating the Playwright sanity-walk as the responsive pass.** Phase 19's visual check confirms sections render in order with content wired — it is not the phase-20 responsive verification (which snapshots at 360/768/1280 and confirms intentional layout at each). The agent surfaces, when needed, that "it renders" (phase 19) is not "it's responsive" (phase 20).

**Hidden assumption that composition is the finished site.** It is not. The agent surfaces that phase 19 produces a rendered site that still needs the responsive pass (20), a11y audit (21), perf audit (22), and forms wiring (23) before it is launch-ready. An assembled site that "looks done" on the agent's desktop is pre-responsive, pre-audited.

## Reference materials

Foundation docs:

- `DESIGN-phase-contracts.md` § 19 — the seed for this contract.
- `DESIGN-architecture.md` § Stack-agnostic output design (pre-phase-11 artifacts are stack-independent; phase 19 is where the stack adapter's composition conventions apply) / § Integration with Claude Code primitives.
- `DESIGN-project-scaffold.md` § page/route output conventions per stack; `sitemap.yaml` schema.
- `DESIGN-content-layers.md` — phase 19 is where Layers 2 (components), 3 (strings), 4 (page prose) compose into rendered pages.
- `${CLAUDE_PLUGIN_ROOT}/reference-corpus/ECOSYSTEM-CATALOG.md` — templates as composition-pattern inspiration only; never imported. Surfaced at phase 19 for "how does a reference site sequence this page" discussion.
- `DESIGN-context7-integration.md` — phase 19 invokes context7 for stack routing/composition patterns; the resolve→query pattern + caching.

context7 (at this phase — current as of the freshness date): the agent resolves + queries the chosen stack's current routing/composition docs at phase-19 entry — e.g. `/vercel/next.js` (App Router layout nesting + Server/Client component rules), `/withastro/docs` (dynamic params + island hydration directives), `/gohugoio/hugo` (content + layout pairing). Per `DESIGN-context7-integration.md` per-stack library-id manifest at `reference-corpus/seeds/{stack}.yaml`. The optional JSON handoff protocol (`DESIGN-handoff-protocol.md`) can emit a page-level brief at phase 19, though composition is usually agent-owned once components exist.

Freshness date for this contract's references: **2026-05-18**.
