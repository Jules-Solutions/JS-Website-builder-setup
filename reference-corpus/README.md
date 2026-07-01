# reference-corpus/

> Selectively cloneable reference docs that ship with the plugin. The agent reads from here directly (at `${CLAUDE_PLUGIN_ROOT}/reference-corpus/<dir>/`) at session-start or phase-trigger when content is load-bearing — no vault, no network required.
>
> **The menu:** `ECOSYSTEM-CATALOG.md` (this directory) is the shipped, self-contained catalogue of every tool / library / platform / inspiration source the agent surfaces across the pipeline, each tagged with its surfacing mode (`bundled` / `clone-into-project` / `fetch-on-demand`). Read it to hand the user options; hand it to the user for inspiration.

## What this directory holds

**The shipped catalogue (the menu):**

- `ECOSYSTEM-CATALOG.md` — the curated, self-contained catalogue distilled from the website-builder workstream's `DESIGN-ecosystem-catalog.md` + `DESIGN-templates-catalog.md` (the authoring SSOT, vault-side). Synced from them per the catalogue-update workflow in `DESIGN-resource-curation.md`.

**Shipped reference content (committed; the agent reads these directly; also selectively cloneable into the user's project):**

- `design-systems/` — 5 reference docs on mature design systems (Material 3, Apple HIG, IBM Carbon, Tailwind, Radix/shadcn): token systems + principles + when-to-use. (`DESIGN-architecture.md` §329)
- `brand-examples/` — 7 complete, original brand systems (voice + OKLCH tokens + component patterns) across distinct archetypes. (`DESIGN-architecture.md` §328)
- `awesome-design-md-corpus/` — a curated 14-exemplar subset of `DESIGN.md`-style brand design specs, format adopted from the MIT-licensed `VoltAgent/awesome-design-md`. (`DESIGN-architecture.md` §333)
- `voice-archetypes/` — 8 reference voices spanning the verbal-identity spectrum, each grounded in NN4D + Aaker + Jung with attributes, say/never-say, and sample copy. (`DESIGN-architecture.md` §330)
- `component-patterns/` — canonical specs for the 20 most common component types (purpose + anatomy + content slots + a11y + variants). (`DESIGN-architecture.md` §331)
- `seo-checklists/` — Lighthouse-mapped performance (phase 22) + SEO (phase 26) checklists, each item → audit id → fix path. (`DESIGN-architecture.md` §332)

Each of these six dirs has its own `README.md` index with provenance + which phases consume it. The design trio (`design-systems/`, `brand-examples/`, `awesome-design-md-corpus/`) is consumed primarily at **phase 17 (design system)**, with phases 2/5/18 sampling them. The remaining three serve **phase 5 (voice)** for `voice-archetypes/`, **phase 18 (component build)** for `component-patterns/` (with 9/17 sampling), and **phases 22/26 (performance + SEO)** for `seo-checklists/`.

**Runtime / seeds infrastructure (Phase 5 — Captain P):**

- `seeds/` — per-stack seed reference manifests describing which upstream docs to fetch on demand.
- Cloned upstream reference material (added at runtime by the bootstrap skill or by `wb library add <url>`, NOT committed at scaffold time).

## Clone-vs-fetch policy

The plugin's resource-curation pattern has two surfacing modes per resource:

- **Fetch-on-demand** — the agent reaches via WebFetch / context7 / API at the moment of need. Used for rare lookups and large/changing docs.
- **Clone-into-project** — local copy installed at session-start or phase trigger when the resource is load-bearing for the current phase. The user's `.website-builder/library/` ends up organically structured around what their project actually needed.

Both modes coexist; per-resource policy lives in `seeds/` manifests (Phase 5 work).

## Status

All six shipped reference dirs are populated (corpus track): `design-systems/`, `brand-examples/`, `awesome-design-md-corpus/` (`RPT-corpus-1.md`) plus `voice-archetypes/`, `component-patterns/`, `seo-checklists/` (`RPT-corpus-2.md`). The `seeds/` manifests + runtime curation logic remain Captain P (Phase 5) work, authored per:

- `DESIGN-resource-curation.md`
- `${CLAUDE_PLUGIN_ROOT}/reference-corpus/ECOSYSTEM-CATALOG.md`

## See also

- `.website-builder/library/` — runtime destination for corpora after `autoclone_for_state` copies them in at phase entry.
