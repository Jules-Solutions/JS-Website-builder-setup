---
phase: 14
name: Wireframe per page
group: content-wireframes
pipeline_section: content-wireframes
skill: wb-content
prev_phase: 13
next_phase: 15
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - DESIGN-phase-contracts.md
  - DESIGN-architecture.md
  - DESIGN-project-scaffold.md
  - DESIGN-content-layers.md
  - ${CLAUDE_PLUGIN_ROOT}/reference-corpus/ECOSYSTEM-CATALOG.md
---

# Phase 14 — Wireframe per page

> Section order, hierarchy, and approximate layout — in text, before any pixel exists. The structural-anchoring phase. The one users most want to skip and the one whose skip costs the most. Wireframes are text-based / ASCII here, deliberately: structure is the conversation, not aesthetics.

## Mission

Phase 13 produced per-page briefs — what each page does and which sections compose it. Phase 14 decides how those sections are arranged: section order on the page, the visual hierarchy within and across sections, the approximate layout (full-bleed vs contained, single-column vs grid vs split), and the responsive intent (how the layout reflows on phone vs tablet vs desktop).

The wireframes are text-based — ASCII / Unicode box-drawing sketches, not visual mockups. This is deliberate, not a limitation. Text-based wireframes separate structure from design: the conversation at phase 14 is *"is the section order right, is the hierarchy clear, does the responsive reflow make sense"* — not *"what color is the button"*. Pixels invite aesthetic argument before the structure is settled. A text wireframe forces the user to react to layout intent without getting distracted by typeface and palette (those belong to phase 17, the design system). Text wireframes are also superior AI context: a language model parses exact structure, spacing intent, and component hierarchy from text far more reliably than from a screenshot.

The exit of phase 14 is, for each page, a wireframe block appended to `.website-builder/content/pages/{slug}.md` (under a `## Wireframe` heading or in a sibling `.website-builder/content/pages/{slug}.wireframe.md` per the project-scaffold convention). The wireframe is the structural contract phase 17 (design system) and phase 18 (component build) anchor against.

This is the phase users push hardest to skip — *"can't we just start designing?"* The skip cost is real and quantified (see `## Skip authorization`): skipping wireframing means phase 17/18 produces designs without structural anchoring, and rework probability runs around 60 percent. The agent refuses the skip once, surfaces the cost, and lets the user override with explicit confirmation.

## Entry conditions

- Phase 13 (content per page) complete. Every page in `.website-builder/sitemap.yaml.pages[]` has a brief file at `.website-builder/content/pages/{slug}.md` with frontmatter `purpose`, `sections[]`, `primary_cta`, `data_dependencies`.
- `.website-builder/content/sections.yaml` exists with every section type the briefs reference.
- Phase 2 (vision) complete. The reference URLs and feel statement from phase 2 are the primary input the agent uses to offer wireframe options muggles can react to (since most muggles cannot articulate layout from scratch).
- Phase 10 (information architecture) complete. The nav structure (primary / footer / utility) shapes the header and footer regions every page wireframe shares.

## What Claude must establish

For every page, a text-based wireframe capturing:

1. **Section order.** The vertical sequence of sections from top of page to bottom, drawn from the brief's `sections[]` array but now committed to a specific order (the brief listed them; the wireframe sequences them with intent — e.g., social-proof immediately after hero for trust-first pages, or after the value-proposition for explain-first pages).
2. **Per-section layout shape.** For each section: full-bleed vs contained-width; single-column vs multi-column-grid vs split (text-one-side / media-other); alignment (left / center); approximate vertical weight (is this a tall hero or a thin band).
3. **Hierarchy within sections.** What's the dominant element (the H1 in the hero, the headline in a feature block), what's secondary, what's tertiary. Expressed in the wireframe via box size + label emphasis, not via final type scale (that's phase 17).
4. **Responsive intent.** How each section reflows at the three reference breakpoints: mobile (~360px), tablet (~768px), desktop (~1280px). Captured as short directives per section ("desktop: 3-col grid → mobile: stacked 1-col"; "desktop: split text-left/image-right → mobile: image-top/text-below").
5. **Cross-page consistency.** Shared regions (header, footer, the signup-CTA band that appears on multiple pages) wireframed once and referenced, not redrawn per page.

The agent does NOT decide colors, typefaces, exact spacing values, motion, or imagery here. Those are phase 17 (design system). Phase 14 is structure-only. The agent enforces this separation — when the user starts arguing about button color during wireframing, the agent redirects: *"that's a phase-17 decision; right now we're settling whether the button goes here or there."*

The agent updates `.website-builder/project.yaml.current_phase` to `15` upon completion.

## Gating rules

The agent refuses to advance when:

- **A page has sections but no committed order.** The brief listed sections; the wireframe must sequence them with intent. An unordered section list is not a wireframe.
- **Responsive intent is missing.** Every section needs at least a one-line directive on how it reflows mobile/tablet/desktop. "We'll figure out mobile later" is the failure phase 20 (responsive pass) pays for; phase 14 forces the intent now. The agent refuses to advance with desktop-only wireframes.
- **The user is trying to skip into design.** The canonical failure. The user says *"this is taking too long, let's just start designing / building."* The agent refuses once, surfaces the rework cost (see `## Skip authorization`), offers the lowest-friction wireframe path (2-3 options the user reacts to rather than authors), and only overrides on explicit user confirmation logged to `.website-builder/decisions/skip-phase-14.md`.
- **A section's layout contradicts its content brief.** If phase 13's brief says a section holds 3 testimonials and the wireframe shows a single-column full-width text block, the agent surfaces the mismatch and reconciles (either the brief or the wireframe is wrong; the user decides which).
- **Header/footer wireframed inconsistently across pages.** Shared regions must be identical across pages (the IA from phase 10 is the contract). If page A's header wireframe differs from page B's, the agent surfaces the drift and unifies.

Override is available on the skip-into-design gate via explicit confirmation with the cost surfaced and logged. The other gates are not overridable — they are structural prerequisites for phase 15+.

## Tools and skills used

- **AskUserQuestion** — the primary tool. For users who cannot articulate layout (most muggles), the agent offers **2-3 wireframe options per page** drawn from the phase-2 vision references and asks the user to react ("option A leads with the manifesto; option B leads with social proof — which fits the visitor's state of mind when they land here?"). Reacting is far easier than authoring for non-designers.
- **Write** — the agent writes the wireframe block into each `content/pages/{slug}.md` (under `## Wireframe`) or a sibling `{slug}.wireframe.md` per the scaffold convention.
- **Edit** — iterating wireframes across review rounds.
- **Read** — agent reads `.website-builder/content/pages/{slug}.md` briefs (phase 13 output), `.website-builder/project.yaml.vision` (phase 2), `.website-builder/sitemap.yaml.navigation` (phase 10) to anchor wireframes.
- **WebFetch** — the agent loads phase-2 reference URLs and walks their layout structure with the user as wireframe inspiration ("the site you cited stacks the hero like this — want that, or the inverse?"). Per `DESIGN-templates-catalog.md`: templates and reference sites are *studied for layout patterns, never imported*.
- **WebSearch** — to surface current text-based-wireframe conventions so the wireframes the agent produces use the patterns developers and AI tools currently parse cleanly (Unicode box-drawing, labeled regions, breakpoint annotations).
- **Reference-data load** — `${CLAUDE_PLUGIN_ROOT}/reference-corpus/ECOSYSTEM-CATALOG.md` for per-stack inspiration sources; `${CLAUDE_PLUGIN_ROOT}/reference-corpus/component-patterns/` for canonical section-layout archetypes.

No `Write` / `Edit` on actual code files — those are gated until phase 18. The wireframe is a text artifact in `.website-builder/`, not stack code.

## Output artifacts

For every page, a wireframe block. Per the project-scaffold convention, the exit is `content/pages/<slug>.md.wireframe` — implemented as either a `## Wireframe` section appended to `content/pages/{slug}.md` or a sibling `content/pages/{slug}.wireframe.md`. The agent uses the sibling-file form when wireframes are long enough to clutter the brief; otherwise the appended-section form. Example (appended-section form):

```markdown
## Wireframe

### Desktop (~1280px)

```
┌─────────────────────────────────────────────────────────┐
│ [logo]            Home  Services  Essays  About  [Contact]│  ← header (shared; from phase 10 nav)
├─────────────────────────────────────────────────────────┤
│                                                           │
│   ███ HERO ███  (full-bleed, contained text, center)     │
│   ╔═══════════════════════════════════════════════════╗  │
│   ║   H1 headline (dominant)                           ║  │
│   ║   sub paragraph (secondary)                        ║  │
│   ║   [ Primary CTA ]   secondary-cta-link             ║  │
│   ╚═══════════════════════════════════════════════════╝  │
│                                                           │
├─────────────────────────────────────────────────────────┤
│   MANIFESTO (contained, single-col, left-aligned)         │
│   ┌───────────────────────────────────────────────────┐  │
│   │ H2  +  150-200 word prose body                     │  │
│   └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│   SOCIAL PROOF (contained, 3-col grid)                    │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐                   │
│   │ quote 1 │  │ quote 2 │  │ quote 3 │                   │
│   │ —attr   │  │ —attr   │  │ —attr   │                   │
│   └─────────┘  └─────────┘  └─────────┘                   │
├─────────────────────────────────────────────────────────┤
│   SIGNUP CTA band (full-bleed, center)                     │
│   ╔═══════════════════════════════════════════════════╗  │
│   ║  H2 headline + sub  +  [ email input ][ submit ]   ║  │
│   ╚═══════════════════════════════════════════════════╝  │
├─────────────────────────────────────────────────────────┤
│ footer: Site | Legal | Connect  (3 columns; from phase 10)│  ← footer (shared)
└─────────────────────────────────────────────────────────┘
```

### Mobile (~360px) — reflow directives

- header → hamburger drawer (per phase 10 mobile pattern)
- hero → text stacked, H1 size reduced (phase 17 sets exact scale), CTA full-width
- manifesto → unchanged single-col
- social proof → 3-col grid collapses to 1-col stacked
- signup CTA → input + button stack vertically
- footer → 3 columns collapse to accordion or stacked

### Hierarchy notes

- Page-level dominant element: hero H1 (only h1 on the page)
- Section-level: each section's heading is h2; sub-elements h3 where nested
- Visual weight order: hero > signup-CTA > manifesto > social-proof
```

For shared regions (header, footer, recurring signup-CTA band), the agent wireframes once in a `content/_shared/{region}.wireframe.md` and references it from each page's wireframe rather than redrawing.

## Common failure modes

**"This is taking forever — can we just start designing?"** The canonical skip pressure. The agent's response, verbatim-shaped: *"I hear that. Here's what skipping wireframes does: the design phase produces visuals with no structural anchor, and when we hit the build phase we discover the layout doesn't hold the content — rework probability is around 60%. Wireframing the whole site usually takes one focused session. I can make it fast: I'll give you 2-3 layout options per page and you just tell me which feels right. Want to do that, or override and accept the rework risk?"* If the user overrides, the agent logs `.website-builder/decisions/skip-phase-14.md` with the surfaced cost and the user's explicit confirmation.

**"I can't picture a layout — I don't know what I want."** The most common honest answer from muggles. This is exactly why the agent offers options to react to rather than asking the user to author. The agent draws 2-3 wireframes per page from the phase-2 vision references ("you cited these three sites; here are wireframe sketches inspired by how each handles a page like this — which one fits?"). Reaction is far easier than authorship.

**"Why is it just text boxes? I want to see it."** The agent surfaces the deliberate choice: *"this is text on purpose. If I show you a visual now, we'll spend the next hour arguing about the color of that button instead of whether the button goes above or below the testimonials. Structure first; visuals at phase 17, where we'll have a design system to make them consistent. The text wireframe is the fastest way to settle structure without the distraction."*

**"Just use a template's layout."** Per `DESIGN-templates-catalog.md`, templates are studied for inspiration, never imported. The agent surfaces a template's layout pattern as a wireframe option ("this template stacks hero / features / pricing / testimonials / CTA — want that order?") but does not import the template. The user's site composes from their own design system (phase 17), not a template's.

**"Can we skip mobile and add it later?"** No. The agent refuses desktop-only wireframes. Phase 20 (responsive pass) is the phase that pays for desktop-only thinking with full rework; phase 14 forces the responsive intent now as one line per section. Cheap now, expensive later.

**Wireframe contradicts the content brief.** Phase 13 said the section holds a 3-item grid; phase 14's wireframe shows a single text column. The agent surfaces the mismatch and asks which is right — sometimes the brief was wrong (it's actually a single narrative, not 3 items), sometimes the wireframe is (it should be a grid). The user decides; the agent updates whichever is wrong so phase 15 (per-section content) builds on consistent inputs.

**User keeps redesigning the header per page.** The header is a shared region locked by phase 10's IA. The agent surfaces that per-page header variation breaks navigation consistency (a WCAG 2.2 §3.2.3 consistent-navigation concern as well as a UX one) and unifies to one shared header wireframe referenced from all pages.

**Hidden assumption that the wireframe is the design.** It is not. The agent surfaces, when needed, that the wireframe is the structural skeleton; phase 17 (design system) gives it color / type / spacing / motion, and phase 18 (component build) writes the code. A wireframe that "looks done" is still pre-design.

## Reference materials

Foundation docs:

- `DESIGN-content-layers.md` § Layer 2 (structural specs) — the wireframe is the layout-intent layer between the brief (Layer 4 placeholder) and the component spec (Layer 2 components.yaml, phase 18).
- `DESIGN-project-scaffold.md` § `content/pages/{slug}.md.wireframe` — the exact output convention.
- `${CLAUDE_PLUGIN_ROOT}/reference-corpus/ECOSYSTEM-CATALOG.md` — templates and reference sites are studied for layout patterns, never imported. The agent surfaces template layouts as wireframe options the user reacts to.

Current text-based-wireframe convention (so the agent produces wireframes that humans and AI tools parse cleanly):

- **WebSearch** *"text-based ASCII wireframing patterns website layouts 2026"* — confirms current tooling and conventions. Findings cited in this contract: text wireframes separate structure from design (no aesthetic argument before structure is settled); text outperforms screenshots as AI context (LLMs parse exact structure / spacing / hierarchy from text without a vision model); editable in-place in any text surface. Current tools in the ecosystem: BareMinimum (AI ASCII wireframe generator → shadcn/Tailwind export), Mockdown (browser ASCII wireframe editor), Wyreframe (ASCII → working HTML), the Claude wireframe-generator skill via mcpmarket. The agent uses Unicode box-drawing (`┌─┐│└┘├┤┬┴┼` + `╔═╗║╚╝` for emphasis) + labeled regions + per-breakpoint reflow directives.
- Sources: [BareMinimum](https://bareminimum.design/), [Mockdown](https://www.mockdown.design/), [Wyreframe](https://github.com/wickedev/wyreframe), [Generating ASCII wireframes with Claude](https://32pixels.co/blog/generating-ascii-wireframes-and-flowcharts-with-claude).

Inspiration corpus:

- `${CLAUDE_PLUGIN_ROOT}/reference-corpus/component-patterns/` — canonical section-layout archetypes (hero variants, feature-grid variants, pricing-table variants) the agent draws wireframe options from.
- `${CLAUDE_PLUGIN_ROOT}/reference-corpus/brand-examples/` — complete brand systems showing how mature brands sequence and lay out page-types.
- Per-stack template catalog (per `DESIGN-templates-catalog.md`) — the agent surfaces the stack's curated templates (from phase 11's stack pick) as layout inspiration the user reacts to, never imports.

Phase-2 vision input:

- `.website-builder/project.yaml.vision` — the reference URLs + feel statement + adjective set captured at phase 2. This is the primary input for the 2-3-options-to-react-to approach since most muggles cannot author layout from scratch.

Freshness date for this contract's references: **2026-05-18**.

## Skip authorization

**Phase 14 is the most-skipped and highest-skip-cost phase in the content-wireframes group. The agent allows the skip only under explicit user authorization with the cost surfaced and logged.**

**The skip cost, quantified:** Skipping wireframing means the design phase (17) and component-build phase (18) produce designs and code without structural anchoring. The structure gets discovered during build instead of decided before it. **Rework probability is approximately 60%** — most sites that skip wireframing hit a structural problem at phase 19 (composition) or phase 20 (responsive pass) that requires going back and rebuilding sections, which is far more expensive than wireframing would have been. The agent surfaces this number explicitly: *"skipping wireframing means the design phase produces designs without structural anchoring; rework probability ~60%."*

**When the skip is legitimately allowed:**

1. **Explicit user authorization with cost acknowledged.** The user, having heard the ~60% rework cost, explicitly confirms they want to skip. The agent logs `.website-builder/decisions/skip-phase-14.md` with: the surfaced cost, the user's verbatim confirmation, the date, and a note that phases 17-20 carry elevated rework risk. The agent does not refuse forever — it refuses once, surfaces, and respects the user's authority over their own project.
2. **Phase-6.5 ingestion produced wireframe-equivalent structure.** When entry mode was `has-existing-site` / `has-Figma-file`, phase 6.5 may have extracted the existing layout structure into per-page structure already. Phase 14 still runs as a confirmation pass against the ingested structure (the agent surfaces it as a wireframe the user reviews and adjusts) — not a full skip.
3. **Single-section landing page.** A genuinely single-section page (one hero, nothing else) has a trivial wireframe; the agent produces it in one pass without extended wireframing dialogue. Thin pass, not a skip.

**When the skip is NOT allowed even on user request:**

- The agent will not skip wireframing *silently*. The cost must be surfaced and the override logged.
- The agent will not skip responsive intent. Even in the option-1 explicit-skip case, the agent captures a one-line per-section reflow note, because phase 20 (responsive pass) is non-negotiable per the VISION anti-skip lock and needs *some* responsive intent to verify against.

The skip log at `.website-builder/decisions/skip-phase-14.md` follows the standard decision-doc frontmatter (`type: decision`, `phase: 14`, `made_at`, `alternatives_considered`, `chosen: skip`, `reasoning`) plus a `surfaced_cost: "rework probability ~60% at phases 17-20"` field and the user's confirmation quote. Phases 17 and 18 read this log; if present, they carry the elevated-rework-risk flag and the agent re-surfaces it at phase 19 (composition) if structural problems appear: *"this is the structural issue I flagged when we skipped wireframing — here's the rework."*
