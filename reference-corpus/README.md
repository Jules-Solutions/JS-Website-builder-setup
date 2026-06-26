# reference-corpus/

> Selectively cloneable reference docs that ship with the plugin. The agent reads from here at session-start or phase-trigger when content is load-bearing.

## What this directory holds

**Shipped reference content (committed; selectively cloneable into the user's project):**

- `design-systems/` — 5 reference docs on mature design systems (Material 3, Apple HIG, IBM Carbon, Tailwind, Radix/shadcn): token systems + principles + when-to-use. (`DESIGN-architecture.md` §329)
- `brand-examples/` — 7 complete, original brand systems (voice + OKLCH tokens + component patterns) across distinct archetypes. (`DESIGN-architecture.md` §328)
- `awesome-design-md-corpus/` — a curated 14-exemplar subset of `DESIGN.md`-style brand design specs, format adopted from the MIT-licensed `VoltAgent/awesome-design-md`. (`DESIGN-architecture.md` §333)

Each of those three has its own `README.md` index with provenance + which phases consume it. Primary consumer: **phase 17 (design system)**, with phases 2/5/18 sampling them.

**Runtime / seeds infrastructure (Phase 5 — Captain P):**

- `seeds/` — per-stack seed reference manifests describing which upstream docs to fetch on demand.
- Cloned upstream reference material (added at runtime by the bootstrap skill or by `wb library add <url>`, NOT committed at scaffold time).

## Clone-vs-fetch policy

The plugin's resource-curation pattern has two surfacing modes per resource:

- **Fetch-on-demand** — the agent reaches via WebFetch / context7 / API at the moment of need. Used for rare lookups and large/changing docs.
- **Clone-into-project** — local copy installed at session-start or phase trigger when the resource is load-bearing for the current phase. The user's `.website-builder/library/` ends up organically structured around what their project actually needed.

Both modes coexist; per-resource policy lives in `seeds/` manifests (Phase 5 work).

## Status

The three shipped reference dirs (`design-systems/`, `brand-examples/`, `awesome-design-md-corpus/`) are populated (corpus track — `RPT-corpus-1.md`). The `seeds/` manifests + runtime curation logic remain Captain P (Phase 5) work, authored per:

- `Workstreams/website-builder/cross-cutting/DESIGN-resource-curation.md`
- `Workstreams/website-builder/foundation/DESIGN-ecosystem-catalog.md`

## See also

- `../reference/` — exemplar inspiration data shipped with the plugin (brand examples, design system exemplars, component patterns, etc.).
