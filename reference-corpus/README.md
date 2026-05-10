# reference-corpus/

> Selectively cloneable reference docs that ship with the plugin. The agent reads from here at session-start or phase-trigger when content is load-bearing.

## What this directory holds

- `seeds/` — per-stack seed reference manifests describing which upstream docs to fetch on demand.
- Cloned upstream reference material (added at runtime by the bootstrap skill or by `wb library add <url>`, NOT committed at scaffold time).

## Clone-vs-fetch policy

The plugin's resource-curation pattern has two surfacing modes per resource:

- **Fetch-on-demand** — the agent reaches via WebFetch / context7 / API at the moment of need. Used for rare lookups and large/changing docs.
- **Clone-into-project** — local copy installed at session-start or phase trigger when the resource is load-bearing for the current phase. The user's `.website-builder/library/` ends up organically structured around what their project actually needed.

Both modes coexist; per-resource policy lives in `seeds/` manifests (Phase 5 work).

## Status as of Phase 1 scaffold

Stub. Captain P (Phase 5) authors the `seeds/` manifests and the runtime curation logic per:

- `Workstreams/website-builder/cross-cutting/DESIGN-resource-curation.md`
- `Workstreams/website-builder/foundation/DESIGN-ecosystem-catalog.md`

## See also

- `../reference/` — exemplar inspiration data shipped with the plugin (brand examples, design system exemplars, component patterns, etc.).
