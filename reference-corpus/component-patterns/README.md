# `reference-corpus/component-patterns/`

> Canonical specs for the 20 most common website component types. The agent reads these to learn the *shape* of a component — its anatomy, the content it needs, its accessibility contract, and the variants worth knowing — before designing or building one. Each spec is **stack-agnostic**: it describes the pattern, not a framework's implementation. The plugin emits the actual code (React/Tailwind/Astro/etc.) at phase 18; these docs are the blueprint that code is held to.

## What's here

The canonical 20, grouped by role:

| Group | Files |
|---|---|
| **Structure & navigation** | `hero.md`, `nav.md`, `footer.md`, `breadcrumb.md`, `banner.md` |
| **Content display** | `card.md`, `feature-grid.md`, `stat-block.md`, `gallery.md`, `logo-cloud.md` |
| **Social proof & conversion** | `testimonial.md`, `pricing-table.md`, `cta.md`, `team-grid.md`, `newsletter-signup.md` |
| **Interactive & disclosure** | `form.md`, `modal.md`, `tabs.md`, `accordion.md`, `faq.md` |

Every file follows one fixed shape: **Purpose → When to use / when not → Anatomy → Content slots → Accessibility requirements → Common variants → Pitfalls**. The `Content slots` table maps each slot onto one of the plugin's 5 content layers (`brand.yaml` / `sitemap.yaml` / `components.yaml` / `content/strings` / `content/pages` / `media`), so a spec doubles as a fill-in checklist when the agent assembles the component from project state.

## Why these twenty

These are the components that appear on essentially every brochure, marketing, portfolio, or small-business site — the set a freelancer assembles 90% of pages from. The four interactive patterns (`form`, `modal`, `tabs`, `accordion`, plus `faq` which is built on the disclosure model) are the ones most often shipped broken, so their specs are the heaviest and are written to the **WAI-ARIA Authoring Practices Guide (APG)** patterns verbatim (Dialog, Tabs, Accordion, Disclosure). The corpus deliberately stops at 20: rarer components (data tables, date pickers, command palettes, carousels-as-primary-nav) are out of the brochure-site sweet spot and are reached for via the design-skill flavors + component-library docs at phase 18, not pre-specified here.

## How the agent uses this dir

- **Phase 9 (sitemap):** when deciding what a page contains, consult `## Purpose` + `## When to use / when not` to challenge whether a proposed component earns its place against the page's conversion goal.
- **Phase 17 (design system):** read `## Anatomy` + `## Common variants` to decide which variants the project's design system needs tokens and rules for.
- **Phase 18 (component design / build):** the working contract. Read `## Content slots` to know what to fill and from where; treat `## Accessibility requirements` as a hard checklist the emitted code must satisfy; pick from `## Common variants`; check the build against `## Pitfalls` before declaring the component done.

The component-library reference docs (shadcn, DaisyUI, Radix, etc.) cloned at phase 18 tell the agent *how a specific library implements* a pattern; these specs tell it *what the pattern must be* regardless of library. Read this dir for the contract; read the library docs for the API.

## Provenance & licensing

Every file is **original reference prose** written for the website-builder plugin — plugin-owned and freely usable. The accessibility sections summarize the *publicly documented* WAI-ARIA Authoring Practices Guide and WCAG 2.2 success criteria (W3C, © W3C; referenced, not copied). No third-party component code, design assets, or copyrighted documentation is bundled here.

## See also

- `../design-systems/` — foundational *design systems* (token taxonomies + principles) vs. these per-*component* specs.
- `../brand-examples/` — complete brand systems whose `## Component patterns` sections show these components dressed in a specific brand.
- `../voice-archetypes/` — the verbal-identity side; component microcopy slots (CTA labels, form errors) inherit voice from the chosen archetype.
- `Workstreams/website-builder/foundation/DESIGN-architecture.md` §331 — the spec this dir satisfies.
- WAI-ARIA Authoring Practices Guide: https://www.w3.org/WAI/ARIA/apg/patterns/ — the canonical source for the interactive patterns.
