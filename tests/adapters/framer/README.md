# tests/adapters/framer/ — Framer stack adapter fixture

> Verifies `adapters/stack-framer.md` against the `tests/adapters/README.md` convention.
> Phase 3 manual-verification scope per `BUILD-strategy.md`. Test-runner integration is Phase 5+ scope — these fixtures are the contract; the runner ships later.

## What this fixture tests

A synthetic `.website-builder/` project state at the **phase-11-complete** point (stack=`framer`, transactional=false, default-language=`en`, second language=`de`, entry-mode greenfield) walked through pipeline phases 11 → 27. The fixture's `expected.yaml` declares what the adapter SHOULD produce at each phase; manual verification confirms `adapters/stack-framer.md` matches.

### Coverage

| Adapter section | Fixture-exercised aspect |
|---|---|
| §3 Migration recipe | `brand.yaml` → Color/Text Styles; `sections.yaml` → Code Components; `content/strings/en.json` + `de.json` → CMS Strings collection (flat-field schema validates the S6 flattening recipe) |
| §4 Content layer mapping | All 5 layers represented in the fixture; per-layer destination paths verified |
| §5 i18n integration | Multilingual fixture (`en` + `de`); LanguageSwitcher + HreflangTags Code Components expected in `phase_22_i18n` |
| §6 Phase 6.5 ingestion | Not directly exercised by greenfield fixture (no existing site to ingest); covered by walkthroughs/ sibling tests in Phase 5+ |
| §7 Commerce | `transactional: false` in fixture; commerce branch not exercised. Companion fixture `framer-commerce/` is Phase 4+ scope when commerce adapters ship. |
| §8 CMS pairing | Default `framer-cms`; recorded in `phase_12_cms` |
| §9 Component library pairing | 3 Code Components generated (HeroBlock, NavBar, FooterBlock); per-stack codegen verified vs `skills/wb-component-build/references/per-stack-codegen.md#framer` |
| §10 Deploy | `framer-publish` target; DNS handoff readiness recorded |
| §11 Post-launch | Out-of-scope for fixture (post-deploy phases 31-34 are not part of phase-11-complete baseline) |
| §12 Limitations | Recorded in `expected_limitations` |
| §13 context7 lookups | Lookup pattern documented in the adapter; freshness check is a per-session concern, not a per-fixture one |

## Pre-Phase-5 manual verification

Per the convention's `expected.yaml` contract, the fixture is **executable test guidance**. Manual verification walks the agent through the pipeline mentally with the fixture as starting state, then checks the adapter file:

1. Open `adapters/stack-framer.md` § "Migration recipe" — confirm each row of the fixture's `brand.yaml`, `sitemap.yaml`, `components.yaml`, `content/strings/*.json`, `content/pages/*.md` maps to a destination the recipe describes.
2. Walk § "Phase 11 stack decision" → `expected.yaml.phase_11_baseline` is `phase-11-complete` — fixture's `project.yaml.stack: framer` matches.
3. Walk § "i18n integration" → fixture has `languages: [en, de]`, `default_language: en`, `language_routing: prefix` — matches Pattern A default.
4. Walk § "Component library pairing" → fixture's `components.yaml` lists `HeroBlock`, `NavBar`, `FooterBlock` — confirm adapter recipe + `per-stack-codegen.md#framer` produce 3 `.tsx` files at `code/HeroBlock.tsx`, etc.
5. Walk § "i18n integration" + `i18n/language-switcher.md#framer` + `i18n/hreflang.md#framer` → confirm a `LanguageSwitcher` + `HreflangTags` Code Component would be generated per the multilingual fixture state.

## Setup required by the future test runner (Phase 5+)

When `tests/run-tests.sh` is extended to load adapter fixtures (future INST), the Framer runner will need:

- **`FRAMER_API_TOKEN`** — pulled from 1Password; tests run against a sandbox Framer project (not a real client project). The sandbox project ID + token live in a CI-scoped 1P item. The runner asserts CMS items + Color Styles + Code Components seed correctly per the migration recipe.
- **`framer-cli`** installed in CI runner (`npm install -g framer-cli` — verify package name at runner-setup time via context7).
- **Optional: Playwright** for the phase-22 / phase-29 verification walks against a published preview Frame.

For Phase 3 manual verification, none of this setup is needed — the fixture + expected.yaml + README.md are read by hand against `adapters/stack-framer.md`.

## Platform-specific gotchas the fixture doesn't cover

- **Auth-walled site walking** (phase 6.5 deep path) — needs a real Framer site behind login; documented in `extraction/playwright-walk.md` instead. Phase 5+ walkthrough fixture covers this.
- **Animation perf at scale** — documented in `adapters/stack-framer.md` §12 + §9 trade-offs; not in this baseline fixture.
- **Headless CMS pairing** (Sanity / Payload via Code Components) — escape-hatch path; this baseline tests the default Framer CMS pairing. Phase 4+ CMS adapter fixtures cover headless paths.
- **RTL language coverage** — fixture is `en` + `de` (both LTR). RTL coverage lands in a future `framer-rtl/` companion fixture when Arabic / Hebrew is exercised in walkthroughs.
- **Plan-tier limitations** — the fixture assumes Pro plan; some features (Localization API, Code Components) require Pro. Documented in adapter §2 + §12; verified at session-setup, not fixture-time.

## How to update this fixture when the adapter contract evolves

1. Identify the section of `adapters/stack-framer.md` that changed (e.g. a new ControlType added to `per-stack-codegen.md#framer` after Framer ships a new API).
2. Update `expected.yaml` to reflect the new expected output (e.g. a Code Component now uses `ControlType.NewType`).
3. Re-walk the manual verification — confirm fixture inputs produce the new expected outputs per the updated adapter.
4. If fixture inputs need to grow (e.g. new field in `brand.yaml`), add minimally — keep the fixture lean.
5. Commit the fixture changes alongside the adapter change in the same INST; CI runner (when shipped) will catch drift.

## See also

- `tests/adapters/README.md` — fixture convention this fixture follows
- `adapters/stack-framer.md` — adapter file this fixture tests
- `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` — `.website-builder/` schema the `fixture/` directory mirrors
- `i18n/language-switcher.md#framer` + `i18n/hreflang.md#framer` — i18n outputs the multilingual fixture exercises
