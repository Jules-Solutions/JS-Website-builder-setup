---
phase: 17
group: design
skill: ui-ux-pro-max
prev_phase: 16
next_phase: 18
re_runnable: true
relates_to:
  - Workstreams/website-builder/cross-cutting/DESIGN-resource-curation.md
  - Workstreams/website-builder/foundation/DESIGN-ecosystem-catalog.md
# library_clones_at_entry — the WORKING EXAMPLE for Captain P's autoclone_for_state(trigger="phase-entry", phase=17).
# Schema: scripts/README.md § library_clones_at_entry. Per the Phase-5 contract, the field is back-filled
# into the real 17/18/24a/24b/28/29 contracts by a FUTURE follow-up INST — this fixture is the one demonstration.
library_clones_at_entry:
  - resource: awesome-design-md
    as: awesome-design-md
    note: "10-20 most-relevant DESIGN.md exemplars based on chosen aesthetic (phase 17)"
  - resource: shadcn-components
    when: component_library == "shadcn"
    as: docs
    note: "component-library reference for the phase 18 build"
  - resource: stripe-checkout
    when: transactional == true
    as: docs
    note: "only clone Stripe docs when the project is transactional"
---

# Phase 17 — Design System Creation (fixture contract)

> This is a **test fixture** copy of the phase-17 contract, carrying the
> `library_clones_at_entry` frontmatter field as the working example for the
> auto-clone runtime. It exists so `tests/library/test_wb_library.py` can
> exercise `autoclone_for_state(trigger="phase-entry", phase=17)` against a real
> contract that declares clone triggers — both unconditional (the
> awesome-design-md corpus) and `when:`-gated (shadcn docs gated on the chosen
> component library; Stripe docs gated on `transactional`).
>
> The full phase-17 contract body (the design-system creation pipeline) is out
> of scope for this fixture — only the machine-read frontmatter matters to the
> auto-clone runtime. See `Workstreams/website-builder/cross-cutting/DESIGN-resource-curation.md`
> lines 234-242 for the design-doc source of these triggers.

At phase-17 entry, the agent seeds the project's design system. The resources
above become load-bearing: the awesome-design-md exemplar corpus (always), the
chosen component library's reference docs (only if shadcn was picked), and the
Stripe Checkout docs (only if the project is transactional).
