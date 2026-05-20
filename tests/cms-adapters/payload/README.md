# tests/cms-adapters/payload — fixture README

> Per-CMS fixture for `cms-adapters/cms-payload.md` validation. Pairs with stack `nextjs` (the only Native pairing per the cross-CMS × stack table). Schema-only — no real Payload bootstrap required for Phase 4 manual verification.

## What this fixture tests

- **Adapter file:** `cms-adapters/cms-payload.md` (the 12-section schema authored by Captain K of Phase 4)
- **Paired stack:** `adapters/stack-nextjs.md` (Captain G's Phase 3 work; canonical pairing). Headless mode for Astro/SvelteKit (S3) is documented in cms-payload.md but NOT exercised here; fixtures for those pairings are Phase 10+ scope.
- **Pipeline phases exercised:** 12 (CMS decision) → 17 (design system / BrandTokens seed) → 18 (component build / Pages seed) → 22 (i18n integration). Phase 24a/b/c (commerce) deferred — `transactional: false` in fixture; companion `payload-commerce/` fixture is Phase 10+ scope.

## Fixture composition

```
tests/cms-adapters/payload/
├── README.md                       # this file
├── expected.yaml                   # per-phase expected adapter output (per tests/cms-adapters/README.md schema)
└── fixture/                        # synthetic .website-builder/ + Payload project state at phase-12-complete
    ├── project.yaml                # cms: payload, stack: nextjs, transactional: false, db_decision: vercel-marketplace-neon (S4 captured)
    ├── brand.yaml                  # OKLCH tokens — colors, typography, spacing, motion
    ├── sitemap.yaml                # 4 pages × 2 locales = 8 documents at phase 18 seed time
    ├── components.yaml             # Hero + RichText + FeaturesGrid + CallToAction (4 components → 4 Payload Blocks)
    ├── content/
    │   ├── pages/
    │   │   ├── home.en.md          # Pattern A (Decision 39): shared structure, translated prose
    │   │   ├── home.de.md
    │   │   ├── about.en.md
    │   │   └── about.de.md         # services.* and contact.* deferred for fixture brevity
    │   └── strings/
    │       ├── en.json             # CDJSON per i18n/strings-schema.md
    │       └── de.json
    ├── payload.config.ts           # master config — db: vercelPostgresAdapter; localization: en+de; collections + globals imports
    ├── collections/
    │   ├── Pages.ts                # canonical marketing pattern — Blocks-field layout; versions+drafts+livePreview+access+hooks
    │   ├── Users.ts                # auth: true; roles: admin|editor|author
    │   └── Media.ts                # uploads with imageSizes
    ├── blocks/
    │   ├── Hero.ts                 # headline+sub+CTA+background — Approach 2 (text fields localized inside)
    │   ├── RichText.ts             # Lexical-powered; content localized
    │   ├── FeaturesGrid.ts         # array of items with title+description+icon; variant select
    │   └── CallToAction.ts         # headline+sub+button+variant
    └── globals/
        ├── BrandTokens.ts          # bridges Layer 1 → Payload Global; afterChange ISR hook wired
        └── SiteSettings.ts         # siteName+tagline+logo+social array
```

## Phase-12 sub-decisions captured

| Decision | Value | Rationale |
|---|---|---|
| `db_decision` | `vercel-marketplace-neon` | Canonical muggle default per `DESIGN-cms-payload.md` line 564. Vercel-Marketplace-Neon = Neon-powered, billed via Vercel (Vercel deprecated its own Postgres December 2024). |
| `db_adapter` | `postgres` (`@payloadcms/db-vercel-postgres`) | Default for muggle marketing sites; relational + predictable backups + best ecosystem. |
| `hosting_decision` | `vercel` | Pairs with the canonical Next.js + Payload single-deploy. |
| `blocks_localization_approach` | `2` (Approach 2 — fields-inside-blocks localized) | Decision 39 Pattern A default (shared layout, translated prose). Surfaced explicitly in `cms-payload.md § i18n integration` so the agent picks consciously. |
| `strings_layer_option` | `A` (CDJSON in `messages/{lang}.json` via next-intl) | Default for muggle marketing; editors don't touch microcopy in admin. Option B (Strings global) surfaced for "non-tech editors changing button labels" use case. |

## S-risk coverage

### S3 — two-deploy headless mode (Astro/SvelteKit consuming Payload)

**Not exercised by this fixture.** The fixture uses Next.js native pairing only (single deploy). The headless-mode path is documented in:

- `cms-adapters/cms-payload.md § Stack pairings → Per-pairing recipe — Headless mode (Astro / SvelteKit consuming Payload)` — full setup recipe with CORS config, Payload API key user, Astro page consuming `/api/...`, deploy-hook from Payload `afterChange`
- Cross-CMS × stack table in `cms-adapters/README.md` marks Astro+Payload and SvelteKit+Payload as `Possible` (verdict: two-deploy)

Fixtures for `astro-payload-headless/` and `sveltekit-payload-headless/` are Phase 10+ scope per `tests/cms-adapters/README.md` line 186.

### S4 — three-way DB/hosting decision (Payload Cloud / Vercel-Marketplace-Neon / direct-Neon or other)

**Exercised by this fixture.** The decision is captured in:

- `fixture/project.yaml.cms_config.db_decision: vercel-marketplace-neon` (the canonical default; one of three explicit options)
- `fixture/payload.config.ts` uses `vercelPostgresAdapter` from `@payloadcms/db-vercel-postgres` (the Postgres adapter that targets Vercel-Marketplace-Neon)
- `expected.yaml.phase_12_cms.db_decision + hosting_decision` records the choice
- `cms-payload.md § Auth + setup → Database + hosting choice (Phase 12 decision)` documents the explicit three-way Phase 12 prompt with cost / DX / data-residency trade-offs

## What manual verification looks like

Phase 4 verification is **manual, schema-only** — no Postgres, no `pnpm install`, no `pnpm dev`. The reviewer walks the fixture mentally:

1. **Read `project.yaml`** — confirm `cms: payload, stack: nextjs, transactional: false` + the four `cms_config` sub-decisions.
2. **Read `brand.yaml` + `sitemap.yaml` + `components.yaml`** — confirm fixture realism + cross-references resolve (every section in sitemap exists in components.yaml; every token-name referenced in components.yaml exists in brand.yaml).
3. **Read `payload.config.ts`** — confirm:
   - `collections: [Pages, Users, Media]` + `globals: [BrandTokens, SiteSettings]` imports resolve
   - `localization: { locales: [{label: 'English', code: 'en'}, {label: 'Deutsch', code: 'de'}], defaultLocale: 'en', fallback: true }` matches Decisions 39/40/41
   - `db: vercelPostgresAdapter({pool: { connectionString: process.env.DATABASE_URI || '' }})` matches the S4 decision
   - `editor: lexicalEditor({features: ...})` is shape-valid
4. **Read `collections/Pages.ts`** — confirm:
   - `versions.drafts.autosave` + `versions.maxPerDoc: 50` (per common-pitfalls)
   - `access.read: ({req: {user}}) => user ? true : { _status: { equals: 'published' } }` (per common-pitfalls)
   - `admin.livePreview.url` callback resolves locale-aware URL
   - `fields.layout` is `type: 'blocks'` with `localized` NOT set at this level (Approach 2 — Decision 39 Pattern A)
   - `hooks.beforeChange` generates slug; `hooks.afterChange` calls `/api/revalidate`
5. **Read each `blocks/*.ts`** — confirm text fields (headline, sub, content, item.title, etc.) are `localized: true` while non-text fields (href, variant, icon, background-upload) are shared.
6. **Read `globals/BrandTokens.ts`** — confirm the Layer 1 bridge: token categories (colors, typography) map to Payload field groups; `afterChange` triggers `revalidateTag('brand-tokens')`.
7. **Read `expected.yaml`** — confirm every claim matches what the fixture files specify; no aspirational entries (i.e., everything claimed is verifiable in the fixture).

If any step surfaces a mismatch between the fixture and the adapter file's claims, the reviewer either:
- Updates the fixture to match the adapter (when the adapter is correct)
- Updates the adapter to match the fixture (when the fixture revealed an authoring gap)
- Surfaces the gap as an architectural concern requiring General review

## What's deliberately NOT in this fixture (Phase 10+ scope per `tests/cms-adapters/README.md` line 186)

- **No Postgres bootstrap.** Phase 5+ runner integration scope includes bootstrapping a real Payload instance with a sandboxed Neon Postgres free-tier project + running `pnpm payload migrate`.
- **No `pnpm install`.** Fixture is configuration shape; node_modules omitted. Schema-only validation.
- **No actual seed-script execution.** The seed pattern is documented in `cms-payload.md § Content layer mapping → Seed pattern`; manual verification confirms the seed script would produce documents matching `expected.yaml`.
- **No headless-mode fixtures** for Astro / SvelteKit consuming Payload (S3) — Phase 10+ scope.
- **No commerce fixture** (`payload-commerce/`) with `@payloadcms/plugin-stripe` wired — Phase 10+ scope per BUILD-strategy.md.
- **No real OAuth / API-key user** — Phase 5+ runner scope.
- **No media uploads** — Phase 5+ runner scope; `collections/Media.ts` is configured but no media files in fixture.

## External setup required for future runner integration (Phase 5+)

When the test runner is wired (a future INST per `tests/cms-adapters/README.md` line 207):

- **Node 20+** (Payload v3 baseline)
- **Postgres**: Neon free tier project (`https://neon.com/pricing` — 0.5 GB storage + 100 CU-hours/mo + scale-to-zero — sufficient for sandbox)
- **`pnpm install`** in fixture dir (resolves `payload`, `@payloadcms/next`, `@payloadcms/db-vercel-postgres`, `@payloadcms/richtext-lexical`)
- **Env vars**: `PAYLOAD_SECRET`, `DATABASE_URI` (the Neon connection string), `NEXT_PUBLIC_SITE_URL=http://localhost:3000`, `REVALIDATE_SECRET`
- **`pnpm payload migrate`** to apply schema migrations
- **`pnpm dev`** to spin up the Next.js + Payload dev server
- **First admin user**: `POST /api/users/first-register` (Payload's first-user flow)
- **Seed script**: `pnpm exec ts-node scripts/seed.ts` to populate from `fixture/.website-builder/` files

None of this is needed for Phase 4 manual verification.

## How to update this fixture when the adapter contract evolves

The fixture mirrors `cms-adapters/cms-payload.md`'s claims. When the adapter file changes:

1. **New decision added at phase 12?** Add the field to `project.yaml.cms_config` + record expected value in `expected.yaml.phase_12_cms.<field>`.
2. **New Block type recommended?** Add a `blocks/{Name}.ts` file + reference in `collections/Pages.ts.fields.layout.blocks` array + add to `expected.yaml.phase_18_component_build.components_generated`.
3. **i18n approach default changed (e.g., Approach 1 becomes default)?** Update `project.yaml.cms_config.blocks_localization_approach` + flip `collections/Pages.ts.fields.layout.localized` + update `expected.yaml`.
4. **DB hosting default changed?** Update `project.yaml.cms_config.db_decision` + swap the adapter in `payload.config.ts` + update `expected.yaml.phase_12_cms.db_decision`.
5. **New limitation surfaced?** Add to `expected.yaml.expected_limitations`.

The fixture is the executable contract for the adapter; keep them in lockstep.

## Cross-links

- Adapter file (the contract): `../../cms-adapters/cms-payload.md`
- Sibling fixture convention: `../README.md`
- Paired stack adapter + fixture: `../../adapters/stack-nextjs.md` + (no fixture for stack-nextjs in Phase 3 — only adapter; commerce + payment sibling adapter fixtures are at `../../commerce-adapters/`)
- Sibling Phase 4 fixtures (in parallel — may not exist at this Captain's writing time): `../none/` (Captain I) + `../decap/` (Captain J)
- Source design doc: `Workstreams/website-builder/cms/DESIGN-cms-payload.md`
- Sibling reference site (Payload production proof): `Workstreams/website-starter/` — SynSol + AWin Payload build with 12 collections + 6 globals + 13-15 blocks
- Tests README (the schema this fixture follows): `../README.md`
- Phase 4 DoD: `Workstreams/website-builder/BUILD-strategy.md` Phase 4
