# Per-CMS-adapter test fixtures — convention

> Where Phase 4 (and subsequent) CMS-adapter Captains place their CMS-adapter-specific test fixtures. **CMS-agnostic convention**; per-CMS fixtures land in subdirectories.
>
> Anchors: `Workstreams/website-builder/BUILD-strategy.md` Phase 4 DoD line 203 (*"Per-CMS adapter test fixtures pass"*) + `tests/adapters/README.md` § "How CMS / commerce adapter Captains use this convention (Phase 4+)" lines 131-135 (this file is the sibling that line predicts).
>
> Sibling convention: `tests/commerce-adapters/README.md` (Phase 4 sibling). Reference convention: `tests/adapters/README.md` (Phase 3 — same shape, different scope: stack adapters).

## Directory layout

```
tests/cms-adapters/
├── README.md                       # this file
├── none/
│   ├── fixture/                    # synthetic .website-builder/ scaffold at phase-12-complete
│   │   ├── project.yaml
│   │   ├── brand.yaml
│   │   ├── sitemap.yaml
│   │   ├── components.yaml
│   │   ├── content/
│   │   │   ├── pages/
│   │   │   │   └── home.md
│   │   │   └── strings/
│   │   │       └── en.json
│   │   └── ...
│   ├── expected.yaml               # per-phase expected adapter output
│   └── README.md                   # per-CMS fixture notes (gotchas, run instructions)
├── decap/
│   ├── fixture/
│   ├── expected.yaml
│   └── README.md
└── payload/
    ├── fixture/
    ├── expected.yaml
    └── README.md
```

Each CMS has its own subdirectory. Subdirectory name matches the adapter file basename **stripped of the `cms-` prefix**: `cms-none.md` → `none/`; `cms-decap.md` → `decap/`; `cms-payload.md` → `payload/`. This mirrors the Phase 3 convention (`stack-framer.md` → `framer/`) — the stack/cms/booking prefix is the type discriminator; the dir name is the concrete identity.

## Fixture baseline — `phase-12-complete`

CMS-adapter fixtures take the pipeline state ONE phase further than stack-adapter fixtures (which baseline at `phase-11-complete` per `tests/adapters/README.md`). The CMS-adapter baseline is **phase-12-complete**:

- Phase 11 (stack picked) ✓
- Phase 11 transactional-sibling decision ✓
- **Phase 12 (CMS picked) ✓** — the fixture's `project.yaml.cms` is set to this CMS adapter's identity (`none` / `decap` / `payload`)
- Ready for phase 17 (design system) + phase 18 (component build) + phase 22 (i18n / forms / transactional)

Rationale: CMS-adapter fixtures are about validating the CMS-adapter's content-layer mapping + authoring patterns + i18n integration + (when applicable) commerce integration. The agent's phase-12 dialogue has already locked the CMS choice; the fixture starts from there.

## Minimum contents per CMS

Each per-CMS subdirectory MUST contain:

### `fixture/`

A synthetic `.website-builder/` scaffold representing a minimal-but-realistic project state at the **phase-12-complete** point. Contents:

- `project.yaml` — minimal but valid (`stack: <stack-paired-with-this-cms>`, `cms: <cms-name>`, `transactional: false`, default-language `en`, entry-mode greenfield)
- `brand.yaml` — one tokenized palette (3-4 colors), one type scale (h1/h2/body), spacing scale, motion defaults (same shape as Phase 3 stack fixtures)
- `sitemap.yaml` — 3-5 pages (home, about, contact + one or two more) with `navigation:` block
- `components.yaml` — 2-3 components (HeroBlock, NavBar, FooterBlock at minimum) — these become the Blocks/Collections the CMS adapter exposes
- `content/pages/*.md` — minimal page MD per sitemap entry, in `default_language` only
- `content/strings/en.json` — minimal CDJSON with `nav`, `cta`, `errors` namespaces (per `i18n/strings-schema.md`)
- (Optional, when relevant) `content/strings/de.json` for multilingual coverage — strongly recommended at least one CMS fixture exercises i18n

The fixture is **synthetic** — no real brand, no real client data. Filler content; the contract is the *shape*, not the content quality.

### `expected.yaml`

A declarative spec of what the CMS adapter SHOULD produce at each pipeline phase. Schema:

```yaml
# tests/cms-adapters/{cms}/expected.yaml
fixture_baseline: phase-12-complete

expected_per_phase:
  phase_12_cms:
    cms_selected: <cms-name>            # none | decap | payload
    admin_url: <url or n/a for none>    # e.g. /admin for decap; /admin for payload; n/a for none
    auth_configured: true               # true if OAuth/API key/etc. configured at fixture; n/a for none
    first_content_item_created: <path or admin-action>
      # e.g. for none: "src/content/pages/about.md (committed)"
      # e.g. for decap: "admin → New Post → save (committed to src/content/blog/...)"
      # e.g. for payload: "payload.create({collection: 'pages', data: {...}})"
    schema_config_path: <path or n/a>
      # e.g. for none: "src/content/config.ts" (Zod)
      # e.g. for decap: "public/admin/config.yml"
      # e.g. for payload: "collections/Pages.ts + blocks/*.ts"

  phase_17_design_system:
    tokens_written_to: <stack-path + cms-path>
      # e.g. for none + Astro: "src/styles/tokens.css"
      # e.g. for decap + Astro: "src/styles/tokens.css (optionally BrandTokens file collection)"
      # e.g. for payload + Next.js: "BrandTokens global (in admin) + tokens.css (regenerated on global save)"
    drift_check: pass

  phase_18_component_build:
    components_generated: [HeroBlock, NavBar, FooterBlock]
    schema_validation: pass
      # for none: Zod schema validates
      # for decap: config.yml blocks types match components.yaml shapes
      # for payload: Block configs generate; migrations run; types regenerate
    palette_validator: pass
    a11y_audit: pass

  phase_22_i18n:                          # when fixture has multilingual
    per_locale_files_present: true        # for none: home.en.md + home.de.md (or per-locale folders)
                                          # for decap: i18n: multiple_files structure produces home.en.md + home.de.md
                                          # for payload: localized: true fields store per-locale values
    missing_string_fallback: documented   # per Decision 41
    language_switcher_added: true
    hreflang_emitted: true

  phase_24a_commerce: n/a                  # transactional=false in fixture; commerce branch not exercised
                                           # companion fixtures (e.g. payload-commerce/) are Phase 10+ scope

expected_limitations:                       # per CMS — what the adapter SHOULD surface as cannot-do
  # e.g. for none:
  #   - "No admin UI; editor must be comfortable in code editor"
  #   - "No live preview from separate admin"
  # e.g. for decap:
  #   - "Maintenance-mode upstream; active forks Sveltia CMS + Static CMS"
  #   - "No real API; content is files"
  # e.g. for payload:
  #   - "Requires Node runtime; static-only hosts cannot run admin"
  #   - "Migrations must run on every deploy"

expected_failure_modes_covered:              # per CMS — what failure paths the adapter handles
  # e.g. for none:
  #   - "Frontmatter typo → pre-commit lint blocks"
  #   - "Smart quotes from Word paste → pre-commit sanitizes"
  # e.g. for decap:
  #   - "OAuth setup forgotten → admin loads but cannot authenticate"
  # e.g. for payload:
  #   - "Migration forgotten in production deploy"
```

This is **executable test guidance** — Phase 4 Captains author it alongside the CMS adapter file. A future testing INST (Phase 5+ test-runner integration scope per `tests/adapters/README.md` line 116) wires `tests/run-tests.sh` to check adapter output against `expected.yaml`. For Phase 4 itself, `expected.yaml` is the contract that proves the adapter is complete (manual verification at General review).

### `README.md` (per-CMS)

A short orientation file explaining:

- Which adapter file this fixture tests (`cms-adapters/cms-{name}.md`)
- Which stack the fixture is paired with (CMS-stack pairings per `cms-adapters/README.md` cross-CMS × stack table — pick a `Native` pairing for the fixture)
- Any setup the test runner needs (OAuth credentials for Decap? Postgres for Payload? None for `cms-none`?)
- Known platform-specific gotchas the fixture doesn't cover (and where they're documented)
- How to update the fixture when the adapter's contract evolves

## Per-CMS fixture notes

### `none/` fixture — `cms-none.md`

- `project.yaml.cms: none`
- **Paired stack:** Astro (the default `Native` pairing per `cms-adapters/README.md` cross-CMS × stack table — Astro Content Collections + Zod is the gold standard for file-based content). Other paired-stack fixtures (Hugo + `none`, 11ty + `none`) are Phase 10+ scope.
- **Admin URL:** `n/a` (no admin UI)
- **Auth configured:** `n/a` (no auth surface)
- **First content item created:** `content/pages/about.md` committed to git (the fixture includes the file but not the actual `.git/` — manual verification confirms the adapter's CRUD vocabulary maps "create page" to filesystem + git per S1)
- **Schema config:** `src/content/config.ts` (Zod schema) generated from `components.yaml` block types
- **Phase 22 i18n coverage:** include `content/pages/about.de.md` + `content/strings/de.json` to exercise per-language-file naming pattern (per `DESIGN-cms-none.md` § "i18n in this CMS" lines 354-414)
- **No external setup required** — fixture is fully self-contained markdown

### `decap/` fixture — `cms-decap.md`

- `project.yaml.cms: decap`
- **Paired stack:** Astro (per `cms-adapters/README.md` cross-CMS × stack table — Astro + Decap is the `Native` default for "Astro + a CMS"). Other paired-stack fixtures (Hugo + Decap, Eleventy + Decap, Next.js static export + Decap) are Phase 10+ scope.
- **Admin URL:** `/admin` (Decap's standard mount point)
- **Auth configured:** OAuth not actually wired in fixture (no real OAuth provider) — document the gap so `expected.yaml.phase_12_cms.auth_configured: schema-only-not-runtime`. The fixture's `public/admin/config.yml` is shape-valid but the OAuth flow would fail at runtime without real GitHub OAuth App credentials. Phase 5+ runner integration scope includes setting up a real OAuth App in a sandbox GitHub org.
- **First content item created:** admin action → save → Decap commits to `src/content/blog/2026-05-10-launch.md` (fixture includes the committed file as the "after" state; the admin action itself is documented in `expected.yaml` but not actually runnable for Phase 4 manual verification)
- **Schema config:** `public/admin/config.yml` (Decap's master config) generated from `components.yaml` block types via list+types pattern
- **Phase 22 i18n coverage:** include `i18n: multiple_files` structure → `content/pages/about.en.md` + `about.de.md` (per `DESIGN-cms-decap.md` § "i18n integration" lines 326-378)
- **Maintenance-mode disclosure:** the fixture's per-CMS `README.md` MUST link to `cms-adapters/cms-decap.md` § "Limitations + escape hatches" Decap-maintenance-mode row (S2 callout) — so the fixture context surfaces the upstream-velocity caveat
- **External setup required:** real Decap fixture-runner integration (Phase 5+) needs a GitHub OAuth App + a sandbox repo. Phase 4 manual verification does NOT need this; the fixture's `config.yml` shape-validity is what's verified by hand.

### `payload/` fixture — `cms-payload.md`

- `project.yaml.cms: payload`
- **Paired stack:** Next.js + shadcn (per `cms-adapters/README.md` cross-CMS × stack table — Next.js is the only `Native` pairing for Payload v3). The two-deploy headless mode with Astro / SvelteKit (S3 callout) is documented in the adapter file but NOT exercised by the Phase 4 fixture (Phase 10+ scope).
- **Admin URL:** `/admin` (Payload's standard mount inside the Next.js app via the `(payload)` route group)
- **Auth configured:** schema-only — the fixture's `payload.config.ts` + `collections/*.ts` are shape-valid (TypeScript compiles, schema is well-formed) but Postgres + Node runtime are NOT required for Phase 4 manual verification. Phase 5+ runner integration includes bootstrapping a real Payload instance with a sandboxed Neon Postgres + running migrations.
- **First content item created:** documented as `payload.create({collection: 'pages', data: {...}, locale: 'en'})` in `expected.yaml`; fixture is config/schema only (no actual Payload bootstrap required for Phase 4)
- **Schema config:** `payload.config.ts` + `collections/Pages.ts` + `blocks/Hero.ts` + `blocks/RichText.ts` + `blocks/FooterBlock.ts` + `globals/SiteSettings.ts` + `globals/BrandTokens.ts` — all generated from `components.yaml` block types per `DESIGN-cms-payload.md` § "Authoring patterns" lines 53-228
- **Database + hosting decision (S4):** fixture's `expected.yaml.phase_12_cms.db_hosting_choice` records one of the three Phase 12 prompts (Payload Cloud / Vercel Postgres / Neon); pick Vercel Postgres as the fixture default (matches `DESIGN-cms-payload.md` line 564 muggle default). Fixture's `payload.config.ts` references env vars `POSTGRES_URI` + `PAYLOAD_SECRET` but doesn't invoke them — schema-only.
- **Phase 22 i18n coverage:** include `localization: { locales: [{label: 'English', code: 'en'}, {label: 'Deutsch', code: 'de'}], defaultLocale: 'en', fallback: true }` in `payload.config.ts`; `Pages.ts` fields use `localized: true` on text fields per Decision 39 default (shared layout, translated prose — Approach 2 per `DESIGN-cms-payload.md` lines 474-515)
- **Two-deploy headless mode (S3):** NOT exercised by this fixture (Next.js native pairing only). The adapter file's `## Stack pairings` documents the headless mode for Astro/SvelteKit; fixtures for those pairings are Phase 10+ scope.
- **External setup required:** Phase 5+ runner integration needs Postgres (Neon free tier or Docker) + Node 20+ + `pnpm payload migrate` execution. Phase 4 manual verification does NOT need this.

## What lives OUTSIDE per-CMS subdirectories

- **Shared fixtures** for protocol-level tests (handoff-spec JSON validation, i18n key sync) live at `tests/walkthroughs/` or `tests/` root — not here.
- **Plugin-level tests** (PreToolUse gating, phase-detection) live at `tests/test_pre_tool_use.py`. Not here.
- **Skill-level tests** live alongside their skills (`skills/wb-{group}/tests/`) when authored. Not here.
- **Stack-adapter fixtures** live at `tests/adapters/` (Phase 3 surface). Not here.
- **Commerce / booking adapter fixtures** live at `tests/commerce-adapters/` (Phase 4 sibling). Not here.

`tests/cms-adapters/` is **specifically for CMS-adapter-output validation**.

## Out-of-scope for Phase 4 itself

The full **test runner integration** (CI hook wiring `tests/run-tests.sh` to load CMS fixtures, invoke adapter phases, diff against `expected.yaml`) is **Phase 5+ scope** per `BUILD-strategy.md`. Phase 4 Captains:

- Author the `fixture/` + `expected.yaml` + `README.md` per their CMS
- Run **manual** verification: walk the fixture through pipeline phases 12 → 22 mentally, confirm the adapter file would produce what `expected.yaml` claims
- Surface gaps in their adapter file (or the fixture) and resolve them before commit

Captains do **not** need to wire the runner. That's a future INST.

## File naming

- Subdirectory names: kebab-case matching CMS slug (`none` / `decap` / `payload`).
- Fixture file names: standard `.website-builder/` conventions (per `DESIGN-project-scaffold.md`).
- `expected.yaml`: exactly that filename.
- `README.md`: exactly that filename.

## How commerce / booking adapter Captains use the sibling convention

Same pattern, different scope. `tests/commerce-adapters/` (the sibling Phase 4 README) governs commerce + booking adapter fixtures. The two READMEs share the `fixture/` + `expected.yaml` + `README.md` triple convention but diverge on baseline (CMS: `phase-12-complete`; commerce: `phase-24a-complete` or `phase-24-complete` depending on whether payment + legal are also exercised). See `tests/commerce-adapters/README.md` for the commerce/booking specifics + the TWINT-required fixture rule for CHF-region simulation.

## See also

- `Workstreams/website-builder/BUILD-strategy.md` Phase 4 DoD — the contract this fixture convention satisfies
- `cms-adapters/README.md` — the per-CMS adapter contract these fixtures test (sibling Phase 4 Captain 0 prep file)
- `tests/adapters/README.md` — Phase 3 stack-adapter fixture convention; this file follows the same shape
- `tests/commerce-adapters/README.md` — sibling Phase 4 commerce + booking fixture convention
- `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` — `.website-builder/` layout the fixtures mirror
- `Workstreams/website-builder/foundation/DESIGN-content-layers.md` — the 5-layer structure each fixture must contain
- `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` — phase 12 (CMS decision) + phase 22 (forms / i18n / transactional) — the phases this fixture's `expected.yaml` validates
- `Workstreams/website-builder/cms/DESIGN-cms-none.md` — `cms-none.md` source design doc
- `Workstreams/website-builder/cms/DESIGN-cms-decap.md` — `cms-decap.md` source design doc
- `Workstreams/website-builder/cms/DESIGN-cms-payload.md` — `cms-payload.md` source design doc
- `tests/walkthroughs/` — sibling test surface (end-to-end pipeline dogfood, not per-adapter)
- `tests/run-tests.sh` — current Python test runner (does not yet load CMS-adapter fixtures; future INST)
