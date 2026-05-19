# tests/adapters/wordpress/ — fixture notes

> Phase-3 Captain-H test fixture for `adapters/stack-wordpress.md`. **Manual verification only at Phase 3** — Phase 5+ wires `tests/run-tests.sh` to load fixtures and diff against `expected.yaml`.
>
> Anchor: `tests/adapters/README.md` (canonical fixture convention) + `Workstreams/website-builder/BUILD-strategy.md` Phase 3 DoD line 179.

## What this fixture tests

Adapter file: `adapters/stack-wordpress.md` (this Captain's exclusive write zone).

The fixture is a synthetic `.website-builder/` project state at the **phase-11-complete** point — stack picked (`wordpress`), transactional sibling decided (`false`), default language `en` + secondary `de` (exercises Polylang i18n integration), entry-mode `greenfield`. Tests:

1. **theme.json v3 mapping (L1 brand.yaml.tokens → theme.json):** the fixture's `brand.yaml` includes 3 colors, 2 font families, 3 type-scale entries, a 5-step spacing scale. The expected adapter output translates each into the correct `theme.json` `settings.*` shape with proper slugs + naming.
2. **REST POST migration (L4 content/pages/*.md → wp_posts via POST):** the fixture's `content/pages/home.en.md` + `home.de.md` exercise Pattern A (shared structure, translated prose); `content/pages/about.en.md` exercises a single-language page (Polylang treats `de.md` as missing translation per the configured fallback).
3. **Polylang sample (L3 strings/{lang}.json → Polylang strings translation + theme `.po` files):** the fixture's `content/strings/en.json` + `content/strings/de.json` cover `cta`, `nav`, `errors` namespaces — translated into `theme.pot` + `theme-de.po`.
4. **Custom Gutenberg block brief format (L5):** the fixture's `components.yaml` includes 3 components (HeroBlock, NavBar, FooterBlock); expected output is one custom block per component scaffolded via `@wordpress/create-block` with `apiVersion: 3` + dynamic-render variant.
5. **Hosting decision separated from CMS choice (Risk S4):** the fixture's `project.yaml` deliberately omits `hosting` (the decision the adapter forces explicitly at §10) — verifies the adapter file's `## Deploy` H2 has the H3 split (hosting decision vs CMS-pairing H2 §8).
6. **Multilingual i18n (Polylang default):** fixture's `project.yaml.languages = [en, de]`, `language_routing: prefix`, default `en`. Exercises the §5 `## i18n integration` Polylang path + `i18n/language-switcher.md#wordpress` + `i18n/hreflang.md#wordpress` cross-references.

The fixture does **not** test:

- WPML path (Polylang is the default; WPML is the upgrade — Phase 5+ test).
- WooCommerce (`transactional: false` here; the commerce path is exercised by a separate `transactional-true` fixture variant — Phase 4+).
- Page-builder fallback (Elementor / Divi / Beaver) — out of MVP scope.
- Headless WordPress (out of MVP scope per §8).

## Setup the test runner needs (Phase 5+ — not Phase 3 itself)

Phase 3 verification is manual. The Phase 5+ test runner will need:

- **`@wordpress/env`** installed (`npm install -g @wordpress/env`) to spin up a local WP for live REST testing.
- **Polylang plugin** installed in the test WP instance.
- **WordPress 6.6+** (the theme.json v3 + Block API v3 + Block Bindings + FSE baseline this adapter targets).

For Phase-3 manual walk-through, the agent reads `adapters/stack-wordpress.md` end-to-end and mentally walks the fixture through pipeline phases 11 → 27, confirming the adapter would produce what `expected.yaml` claims.

## Manual run instructions (Phase 3)

1. Read `adapters/stack-wordpress.md` against `adapters/README.md` 14-section schema — verify all 14 H2 sections present in exact order.
2. Read the §4 Content layer mapping table — verify row labels are verbatim `L1 brand.yaml.tokens` / `L2 sitemap.yaml + sections.yaml` / `L3 strings/{lang}.json` / `L4 content/pages/*.md` / `L5 briefs/{component}.json` + the "WordPress native concept" column is filled per row.
3. Read the §10 `## Deploy` H2 — verify hosting decision is split into ≥4 H3 sub-decisions (managed-WP / self-hosted / WordPress.com / containerized) and that hosting is explicitly separate from §8 `## CMS pairing` (which covers WordPress-core vs ACF vs headless).
4. Walk `fixture/` against the expected output table — does the adapter file describe behavior that would produce these outputs?
5. Cross-check `i18n/language-switcher.md#wordpress` + `i18n/hreflang.md#wordpress` — verify they're filled, reference `adapters/stack-wordpress.md` correctly.

## Known platform-specific gotchas the fixture doesn't cover

| Gotcha | Where documented |
|---|---|
| Caching plugins serve wrong-locale hreflang | `i18n/hreflang.md#wordpress` "Caching plugin interaction" |
| Block editor caches theme.json (toggle theme to refresh) | `adapters/stack-wordpress.md` §12 Failure modes table |
| Application Password expiry / revocation | §2 Auth + setup + §12 Failure modes |
| Plugin restrictions on WordPress.com lower plans | §10 Deploy / WordPress.com sub-section |
| Page-builder mid-project pivot = structural pivot | §11 Post-launch + §12 Limitations |
| MySQL `latin1` → `utf8mb4` migration on some shared hosts | §12 Failure modes |
| 2FA-walled admin can't be auto-walked by Playwright | §6 Phase 6.5 ingestion → Auth-walled site handling |

## How to update the fixture

When the adapter's contract evolves (new WP version, theme.json bump, new MVP CMS pairing, etc.):

1. Update `brand.yaml` / `components.yaml` / `content/` to reflect the new contract minimums.
2. Update `expected.yaml` with the new expected outputs per phase.
3. Update this README's "Known gotchas" if a new failure path is documented.
4. Re-run manual verification per the instructions above.

The fixture is **synthetic** — names ("Still Humans" placeholder; oklch colors; common page slugs) are filler. Don't tie tests to real client data.
