# Phase 14 — Wireframe Conventions

Detailed patterns for the phase-14 wireframe-per-page workflow. Source of truth: `Projects/Jules.Solutions/Subprojects/website-builder/phase-contracts/14-wireframe-per-page.md` + `Workstreams/website-builder/cross-cutting/DESIGN-templates-catalog.md`.

## Why text-based wireframes (not visual mockups)

Deliberate, not a limitation. Confirmed by current practice (WebSearch 2026-05-18):

- **Separates structure from design.** A text wireframe forces the user to react to layout intent without arguing about typeface and palette (those are phase 17). Pixels invite aesthetic argument before structure is settled.
- **Superior AI context.** Language models parse exact structure, spacing intent, and component hierarchy from labeled text far more reliably than from a screenshot — no vision model needed. (BareMinimum, Wyreframe, AsciiKit ecosystem all build on this.)
- **Portable + version-control friendly.** Editable in-place in any text surface; diffs cleanly; pastes into any review channel.
- **Low-fidelity-for-non-designers practice (Balsamiq / IxDF 2026):** lo-fi wireframes communicate the "big idea" and information architecture, not visual detail; no design skill required; the right stage to involve non-designers in shaping structure.

Current tooling landscape (surfaced 2026-05-18; for the agent's awareness, not for import): BareMinimum (AI ASCII generator → shadcn/Tailwind export), Mockdown (browser ASCII editor), Wyreframe (ASCII → working HTML), AsciiKit (Claude UX-design skill). The website-builder produces its own wireframes inline; these tools are context, not dependencies.

## The Unicode box-drawing convention

Use these characters so output parses cleanly for humans and downstream AI:

- Structure: `┌ ─ ┐ │ └ ┘ ├ ┤ ┬ ┴ ┼`
- Emphasis (dominant regions, CTA bands): `╔ ═ ╗ ║ ╚ ╝`
- Filled/visual-weight markers: `███` for high-weight blocks (hero, primary CTA)
- Labeled regions: `← header (shared; from phase 10 nav)` style trailing annotations
- Per-breakpoint sections: one diagram per breakpoint OR a desktop diagram + a reflow-directives list

Three required parts per page wireframe:

1. **Desktop (~1280px)** — the full box-drawing diagram with labeled regions, hierarchy via box size + label emphasis.
2. **Mobile (~360px) reflow directives** — one line per section ("social proof → 3-col grid collapses to 1-col stacked"; "header → hamburger drawer"). Tablet (~768px) where it materially differs.
3. **Hierarchy notes** — page-level dominant element (the single h1), section-level heading levels, visual-weight order.

The phase-14 contract `## Output artifacts` has a complete worked example. Reproduce that shape.

## Shared regions

Header, footer, and recurring bands (signup-CTA appearing on multiple pages) are wireframed **once** at `.website-builder/content/_shared/{region}.wireframe.md` and referenced from each page, never redrawn per page. Per-page header variation breaks navigation consistency (a WCAG 2.2 §3.2.3 consistent-navigation concern as well as UX). The phase-10 IA is the contract for shared-region structure.

## The 2-3-options-to-react-to method

Most users cannot author a layout from scratch — the most common honest answer is *"I can't picture it; I don't know what I want."* Do not ask them to author. Offer options to react to:

1. Read `.website-builder/project.yaml.vision` — the phase-2 reference URLs + feel statement + adjective set.
2. For each page, draw **2-3 wireframe options** inspired by how the cited references handle a page of that type. WebFetch a reference site and walk its structure with the user (studied for layout patterns, never imported — per `DESIGN-templates-catalog.md`).
3. Frame as a choice: *"option A leads with the manifesto; option B leads with social proof — which fits the visitor's state of mind when they land here?"*

Reaction is far easier than authorship for non-designers. This is the fast path; it is also the de-risked path.

## The skip gate — verbatim-shaped script

Phase 14 is the most-skipped and highest-skip-cost phase in the group. The user says *"this is taking forever — can we just start designing?"*

Refuse **once**, surface the quantified cost, offer the fast path, override only on explicit confirmation:

> *"I hear that. Here's what skipping wireframes does: the design phase produces visuals with no structural anchor, and when we hit the build phase we discover the layout doesn't hold the content — rework probability is around 60%. Wireframing the whole site is usually one focused session. I can make it fast: I'll give you 2-3 layout options per page and you just tell me which feels right. Want to do that, or override and accept the rework risk?"*

If the user overrides: log `.website-builder/decisions/skip-phase-14.md`. Even on skip, **still capture one-line per-section responsive intent** — phase 20 (responsive pass) is non-negotiable and needs something to verify against.

### `skip-phase-14.md` decision-doc schema

```yaml
---
type: decision
phase: 14
made_at: "<ISO 8601>"
alternatives_considered: ["full wireframing", "option-react fast path", "skip"]
chosen: skip
reasoning: "<user's stated reason>"
surfaced_cost: "rework probability ~60% at phases 17-20"
user_confirmation: "<verbatim user confirmation quote>"
---
```

Phases 17 and 18 read this log; if present they carry the elevated-rework-risk flag. At phase 19 (composition), if structural problems appear, re-surface: *"this is the structural issue I flagged when we skipped wireframing — here's the rework."*

## Common failure modes (phase 14)

| Failure | Recovery |
|---|---|
| "Can we just start designing?" | The skip script above. Refuse once, surface ~60%, offer fast path, log override. |
| "I can't picture a layout" | Expected. Options-to-react-to, not author-from-scratch. Draw 2-3 from phase-2 references. |
| "Why is it just text boxes? I want to see it" | *"Text on purpose — a visual now means an hour arguing about button color instead of button placement. Structure first; visuals at phase 17 with a design system to keep them consistent."* |
| "Just use a template's layout" | Surface the template's layout as a wireframe *option* to react to; do not import. The user's site composes from their own design system (phase 17), not a template's. |
| "Skip mobile, add it later" | No. Refuse desktop-only. Phase 20 pays full rework for desktop-only thinking; capture responsive intent now as one line per section. |
| Wireframe contradicts the content brief | Surface the mismatch (brief said 3-item grid; wireframe shows single column). User decides which is right; update the wrong one so phase 15 builds on consistent inputs. |
| User redesigns the header per page | Header is a shared region locked by phase-10 IA. Unify to one `_shared/header.wireframe.md`. Surface the consistency concern (WCAG 2.2 §3.2.3 + UX). |
| "The wireframe is the design" | It is not. Wireframe = structural skeleton; phase 17 adds color/type/spacing/motion; phase 18 writes code. A wireframe that "looks done" is still pre-design. |

## Legitimate skip-equivalents (not full skips)

1. **Explicit user authorization with cost acknowledged** — logged per the schema above. Refuse once, surface, respect the user's authority over their project.
2. **Phase-6.5 ingestion produced wireframe-equivalent structure** — `has-existing-site` / `has-Figma-file` extracted layout already. Phase 14 runs as a confirmation pass (the agent surfaces the ingested structure as a wireframe the user reviews/adjusts), not a skip.
3. **Single-section landing page** — a genuine one-section page has a trivial wireframe; produce it in one pass. Thin pass, not a skip.

Never skip *silently* and never skip responsive intent.
