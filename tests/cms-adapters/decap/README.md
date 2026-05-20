# Decap CMS adapter — test fixture

> Tests: `cms-adapters/cms-decap.md` (the Decap CMS adapter authored in Phase 4 by Captain J).
> Per the fixture convention in `tests/cms-adapters/README.md` (Phase 4 Captain 0 prep).

## What this fixture is

A synthetic `.website-builder/` scaffold at the **phase-12-complete** baseline, representing a minimal-but-realistic project state where:

- Phase 11 (stack picked) ✓ — `stack: astro`
- Phase 11 transactional-sibling decision ✓ — `transactional: false`
- Phase 12 (CMS picked) ✓ — `cms: decap`

The fixture exercises the Decap CMS adapter's contract: Astro + Decap (the `Native` default pairing per `cms-adapters/README.md` cross-CMS × stack table), 2 locales (en/de) per Decision 39 Pattern A (`multiple_files` structure with shared layout + translated text), 3 representative section types (hero, rich_text, cta), 2 file collections (Pages + Strings).

## Paired stack

**Astro** — the `Native` default per `cms-adapters/README.md`. Other paired-stack fixtures (Hugo + Decap, Eleventy + Decap, Jekyll + Decap, Next.js static export + Decap) are Phase 10+ scope.

## Setup the test runner would need

**Phase 4 manual verification** (current scope): nothing beyond reading the fixture files. The contract is:

- `public/admin/config.yml` is well-formed YAML
- The `types` list matches `components.yaml` shapes
- The `i18n:` block matches Decision 39 Pattern A defaults (`multiple_files` + `en` default + `de` secondary)
- The Strings file collection has both `en` and `de` files
- Pages collection has the `home.en.md` / `home.de.md` (or `home.md` / `home.de.md` per `multiple_files` convention) per-locale exercise

**Phase 5+ runner integration** (future INST scope): a real Decap admin run would need:

- A real GitHub OAuth App (sandbox GitHub org account)
- A real sandbox GitHub repo (write access)
- The Decap admin loaded via a local dev server (`pnpm dev` on the Astro fixture) at `http://localhost:4321/admin/`
- An OAuth proxy serverless function (or Netlify Identity + Git Gateway) — see the adapter's `## Auth + setup` section

These are explicitly **OUT OF SCOPE for Phase 4 manual verification**. Per `tests/cms-adapters/README.md` § "decap/ fixture" line 169: *"OAuth not actually wired in fixture (no real OAuth provider) — document the gap so `expected.yaml.phase_12_cms.auth_configured: schema-only-not-runtime`."*

## OAuth gap disclosure

**Important:** this fixture is **schema-valid but NOT runtime-runnable.** The `config.yml` shape is correct; the Decap admin would load. The `backend: github` config references `jules-solutions/synthetic-decap-fixture` — a placeholder repo name; the real repo does not exist. Attempting to actually authenticate would fail with an OAuth-redirect error.

Phase 4's manual verification confirms:

- [x] `public/admin/config.yml` parses as YAML
- [x] `collections[].fields[].widget` values are valid Decap widget names
- [x] `i18n.structure` is one of `multiple_files | multiple_folders | single_file`
- [x] Field-level `i18n` values are `true | duplicate | false` (Decap's three modes)
- [x] `types` list under `layout` has correct shape (each type is a `widget: object` with `fields`)
- [x] Strings file collection has one file per locale
- [x] Per-locale page files exist matching the `multiple_files` convention (`home.de.md` + `home.md`)

Phase 4 does NOT verify: actual OAuth login, actual git commits from admin saves, actual Astro build with the fixture content. Those are Phase 5+ runner scope.

## Maintenance-mode disclosure cross-link (S2)

Per `tests/cms-adapters/README.md` § "decap/ fixture" line 173 — this fixture README must link to the adapter's maintenance-mode disclosure so the fixture context surfaces the upstream-velocity caveat:

→ See `cms-adapters/cms-decap.md` § "Limitations + escape hatches" → **Project maintenance status disclosure (S2 — REQUIRED prominent)** row.

**Status verified 2026-05-20:**

- **Decap CMS itself** — **active maintenance again.** v3.12.2 released April 2026 (npm + GitHub releases); Plate-based richtext widget added; npm cadence ≥1 release per 3 months ("sustainable" per cadence-monitoring services). The original `DESIGN-cms-decap.md` line 403 framing (written 2026-05-10) said "Decap is in maintenance mode" — that framing is outdated; agent's phase 12 surfaces the current state.
- **Sveltia CMS** — **active fork.** https://github.com/sveltia/sveltia-cms · 559 releases · latest v0.162.3 (2026-05-20) · 4,361 commits · 2.4k stars. "De facto successor to Netlify CMS" per project README; "high compatibility with existing config format" — near-drop-in path. Migration guide at https://sveltiacms.app/en/docs/migration.
- **Static CMS** — **archived 2024-09-09.** https://github.com/StaticJsCMS/static-cms · Final release v4.3.0 (April 2024). README states "Decap CMS has been revitalized" and recommends alternatives (Tina CMS) — explicitly **NO LONGER A VALID FORK PICK.** The agent's phase 12 surfaces this so users don't accidentally adopt an archived project.

The fixture's `expected.yaml` records `phase_12_cms.maintenance_status_disclosed: true` and `forks_named: [Sveltia, Static]` so the adapter contract is tested for this disclosure path.

## How to update the fixture when the adapter's contract evolves

1. **Adapter-file change** in `cms-adapters/cms-decap.md` (e.g. a new H3 pattern, a new context7 lookup) → reflect in `expected.yaml` if the change adds verifiable contract terms.
2. **Schema change** in `cms-adapters/README.md` (e.g. a 13th H2 section) → reflect in `expected.yaml` per-phase block.
3. **Stack-pairing addition** (e.g. Decap + 11ty fixture for Phase 10+) → create a new `tests/cms-adapters/decap-11ty/` subdirectory; don't change THIS fixture (which is the Native Astro pairing).
4. **Decap version bump** (e.g. v4.x lands with breaking config changes) → bump `expected_per_phase.phase_12_cms.adapter_version` field (add this when v4 is real); update `public/admin/index.html` script URL; re-verify all widget names.
5. **Sveltia compatibility shift** (e.g. Sveltia diverges from Decap config substantially) → update the S2 disclosure in both the adapter and this README.

## Related fixtures

- `tests/cms-adapters/none/` — Captain I's filesystem + git CMS fixture
- `tests/cms-adapters/payload/` — Captain K's Payload CMS fixture
- `tests/commerce-adapters/stripe/` — Captain L's Stripe commerce fixture
- `tests/adapters/astro/` (when authored) — Phase 3 stack-adapter fixture for Astro (the pairing this fixture inherits)

## See also

- `cms-adapters/cms-decap.md` — the adapter being tested
- `cms-adapters/README.md` — the 12-section schema + cross-CMS × stack anchor
- `tests/cms-adapters/README.md` — the fixture convention + decap-specific notes
- `Workstreams/website-builder/cms/DESIGN-cms-decap.md` — primary design-doc source
- `Workstreams/website-builder/foundation/DESIGN-i18n.md` — i18n model + Decisions 38-41
- `Workstreams/website-builder/foundation/DESIGN-content-layers.md` — 5-layer content stack
