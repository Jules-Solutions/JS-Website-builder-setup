# `component-libraries/` — landmark pointer (catalog content relocated)

> This directory is intentionally retained as a documented landmark. The
> component-library catalog content it was originally planned to hold (per
> `BUILD-strategy.md`) now lives inside the `wb-component-build` skill, where it
> load-bears at phase 18 (component build). This README is the signpost so the
> empty dir isn't a navigational dead end.

## Where the catalog content actually lives

`skills/wb-component-build/references/`:

- **`component-library-selection.md`** — the consolidated per-stack-class
  selection-decision layer (React / non-React-Tailwind / Vue / Svelte /
  headless): decision trees, the default + alternatives surfaced via
  `AskUserQuestion` at phase 18, and the composition rules (decision 46 — one
  primary library, max 1–2 complementary).
- **`per-stack-codegen.md`** — per-stack codegen patterns + the context7 IDs
  the agent fetches per stack at phase 18.

(`json-handoff-protocol.md` also lives in that `references/` dir but is the
component-request handoff protocol, not component-library catalog content.)

## Canonical sources behind the catalog

The selection/codegen references above are the consolidated runtime layer; the
canonical per-ecosystem design docs are in the workstream:

- `DESIGN-components-react.md`
- `DESIGN-components-tailwind.md`
- `DESIGN-components-headless.md`
- `DESIGN-components-vue.md`
- `DESIGN-components-svelte.md`

## Provenance

The path change (catalog content → `skills/wb-component-build/references/`) is
recorded in the website-builder STATE-doc decisions ledger
(`website-builder.md`). The capability was never
missing — it lives in skill prose where the agent load-bears it; only the
originally-planned home moved. Surfaced by the Phases 1–6 build-audit (F4,
`AUDIT-build-review-2026-06-15.md`) and recorded by INST-A pre-cosplay polish.
