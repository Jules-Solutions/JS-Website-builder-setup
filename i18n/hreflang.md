# i18n — hreflang Tags

> The HTML metadata that signals language alternates to search engines. **Stack-agnostic intro + required behavior shared by all stacks; per-stack emission sections authored by the Phase 3 stack-adapter Captains.**
>
> Anchor: `Workstreams/website-builder/foundation/DESIGN-i18n.md` §"hreflang tags" (lines 240-253).
> External spec: https://developers.google.com/search/docs/specialty/international/localized-versions

## Overview

`hreflang` is the search-engine signal that says "this page has alternate versions in other languages". Without it, search engines may either pick the wrong language for a user's region or show duplicate-content penalties for translated pages. With it, Google / Bing / DuckDuckGo serve the right language to the right user automatically.

For every multilingual site, the agent emits a `<link rel="alternate" hreflang="...">` tag in the page `<head>` for every language version of the page — including the page itself + `x-default`. The tags are generated from `sitemap.yaml` + `project.yaml.languages`.

## What hreflang looks like

For a `/about` page on a site supporting English + German + French (prefix routing):

```html
<head>
  <link rel="alternate" hreflang="en" href="https://example.com/about">
  <link rel="alternate" hreflang="de" href="https://example.com/de/about">
  <link rel="alternate" hreflang="fr" href="https://example.com/fr/about">
  <link rel="alternate" hreflang="x-default" href="https://example.com/about">
</head>
```

Each tag means: "this page exists in language X at URL Y". `x-default` is the fallback shown to users whose language isn't matched.

## Required behavior (all stacks)

Every stack-specific emission MUST:

- **Emit one `<link rel="alternate" hreflang="...">` per language** the site supports — including the language of the current page itself (yes, the page lists itself in its own hreflang set; this is per spec).
- **Emit an `x-default` tag** pointing to the default-language version (per `project.yaml.default_language`). This is what search engines show to users whose `Accept-Language` doesn't match any specific tag.
- **Use absolute URLs** with the production hostname — never relative paths, never `localhost`. The hostname comes from `project.yaml.canonical_host` (set at phase 28 / deploy).
- **Use ISO 639-1 language codes** — `en`, `de`, `fr`, etc. Optionally with region: `en-US`, `de-CH`, `de-DE`. (See "Region-targeting" below.)
- **Be reciprocal** — if `/about` (en) links to `/de/about` (de) via hreflang, `/de/about` must link back to `/about` (en) via hreflang. Non-reciprocal hreflang is silently ignored by search engines.
- **Match URL routing strategy** — prefix / subdomain / TLD per `project.yaml.language_routing`. The URLs in hreflang tags MUST be the live URLs the page is actually served at.
- **Apply to every public page**, not just the home page. About, contact, blog posts, product pages — every translated page emits its own hreflang set.
- **Not be emitted on non-public pages** (admin dashboards, member-only pages, 404, 500). Search engines shouldn't see these.

## Region-targeting (when to use `en-US` vs `en`)

| Code shape | Meaning | When to use |
|---|---|---|
| `en` | English (no region preference) | Default for most sites — Google serves to any English-speaking user |
| `en-US` | English, US-targeted | When the site specifically targets US users (US pricing, US-specific examples) |
| `en-GB` | English, UK-targeted | When the site has a UK variant alongside US |
| `de-CH` | German, Switzerland | Swiss sites — distinguishes from `de-DE` (Germany) |
| `de-AT` | German, Austria | When content / pricing / examples are Austria-specific |
| `de` | German (no region) | Default for a single German-language site that doesn't differentiate by region |

For Swiss multilingual sites (DE/FR/IT/EN per `DESIGN-i18n.md`), region codes (`de-CH`, `fr-CH`, `it-CH`) are recommended — they prevent Google from sending Austrian or French-from-France users to a Swiss site that doesn't fit their region.

Configuration via `project.yaml.language_regions`:

```yaml
languages: [en, de, fr, it]
default_language: en
language_regions:
  en: en   # or en-US for US-targeted
  de: de-CH
  fr: fr-CH
  it: it-CH
```

When `language_regions` is set, hreflang uses the region-tagged code (`de-CH` instead of `de`). When unset, the bare language code is used.

## hreflang for RTL languages

RTL languages use the same hreflang format — there's nothing RTL-specific. `<link rel="alternate" hreflang="ar" href="https://example.com/ar/about">` works the same as any other language.

## Implementation strategies (high-level)

Hreflang is emitted in the page `<head>`. Mechanism varies by stack:

- **SSR / SSG stacks** (Next.js, Astro, Hugo): emitted by the layout / template per page render; reads current page + available languages from project state.
- **Canvas / visual stacks** (Framer): native localization emits hreflang automatically when enabled; manual injection via project-level "Custom Code" head panel as fallback.
- **CMS-driven stacks** (WordPress): the i18n plugin (Polylang / WPML) handles hreflang automatically — verify it's enabled.

Per-stack sections below carry the specific emission code + verification mechanism.

---

### Framer

<!-- TODO — authored by Phase 3 Captain F per INST-wb-phase3-captain-framer.md.
     This section MUST cover:
     - Framer's native localization auto-emits hreflang — confirm via context7 at phase 11 (auth behavior may evolve)
     - For Frames where Framer's native emission misses (e.g. canvas-composed pages with manual locale variants): inject via project-level "Custom Code" → head panel
     - Custom Component option: a `<HreflangTags />` component the user drops in the header section of each Frame
     - Reciprocal hreflang verification: paste the production URL into Google Search Console's International Targeting report (post-phase-30)
     - Known Framer gotchas: hreflang on draft Frames; hreflang on per-locale variant Frames
     - Cross-reference: `adapters/stack-framer.md#i18n-recipe`, `i18n/language-switcher.md#framer`
-->

### Next.js + shadcn

<!-- TODO — authored by Phase 3 Captain G per INST-wb-phase3-captain-nextjs.md.
     This section MUST cover:
     - App Router `app/[lang]/layout.tsx` or root layout `<head>` injection via Next.js `<Head>` / metadata API
     - next-intl + `generateMetadata()` pattern: emit `alternates.languages` map
     - Code snippet:
       ```ts
       export async function generateMetadata({ params }): Promise<Metadata> {
         return {
           alternates: {
             languages: {
               'en': `${BASE}/about`,
               'de-CH': `${BASE}/de/about`,
               // ...
               'x-default': `${BASE}/about`,
             },
           },
         };
       }
       ```
     - Per-page hreflang for dynamic routes (blog posts, product pages) — same pattern via `generateStaticParams()` + per-locale generation
     - Verification: production build → curl `<head>` → grep `hreflang` → cross-check reciprocity
     - Cross-reference: `adapters/stack-nextjs.md#i18n-recipe`, `i18n/language-switcher.md#nextjs`
-->

### WordPress

<!-- TODO — authored by Phase 3 Captain H per INST-wb-phase3-captain-wordpress.md.
     This section MUST cover:
     - Polylang: hreflang auto-emitted; verify via Polylang Settings → URL Modifications → enabled
     - WPML: hreflang auto-emitted via WPML SEO module
     - When the plugin's hreflang is wrong/missing: manual emission via theme `header.php` reading from `pll_languages_list()` (Polylang) or `apply_filters('wpml_active_languages', ...)` (WPML)
     - x-default handling: Polylang adds it by default; WPML configurable in WPML → Languages
     - Region codes: configure per plugin (Polylang Settings → Languages → Locale; WPML → Languages → Edit)
     - Verification: WP admin → Polylang/WPML report; production curl `<head>`; Google Search Console
     - Known WP gotchas: caching plugins (WP Rocket, W3 Total Cache) can serve stale hreflang to the wrong locale — clear cache after locale changes
     - Cross-reference: `adapters/stack-wordpress.md#i18n-recipe`, `i18n/language-switcher.md#wordpress`
-->

---

## Validation (session-start hook + phase 26 SEO)

The hook checks:

1. Every page rendered in a multilingual site has a `<link rel="alternate" hreflang="...">` tag for every available language.
2. Every page has an `x-default` tag pointing to the `default_language` version.
3. hreflang URLs are absolute (start with `http://` or `https://`).
4. hreflang URLs resolve to existing pages (no broken language-page combinations).
5. Reciprocity: page A's hreflang to page B implies page B's hreflang to page A.

Phase 26 (SEO audit) re-verifies post-deploy:

1. Production curl `<head>` of each page → extract hreflang → compare against expected set.
2. Google Search Console International Targeting report (manual at phase 30 — first crawl).
3. Schema.org structured data (separate from hreflang but related) reflects per-locale variants.

## Common failure modes

| Failure | Cause | Fix |
|---|---|---|
| hreflang missing entirely | Plugin / framework integration not enabled at deploy | Verify per-stack section's emission code is actually rendering |
| hreflang URLs are relative | Code uses `<link rel="alternate" hreflang="de" href="/de/about">` (relative) | Switch to absolute URLs with `canonical_host` |
| hreflang points to localhost | `canonical_host` not set in `project.yaml` | Set at phase 28 |
| hreflang missing x-default | Plugin / code only emits `lang` codes, not `x-default` | Add x-default per spec |
| hreflang missing region | Site targets specific regions but config uses bare codes | Add `language_regions` to `project.yaml` |
| hreflang non-reciprocal | Different pages emit different hreflang sets | Ensure all pages emit the SAME hreflang set for the page's slug across languages |
| Search engines still don't index in target region | hreflang correct but `Content-Language` HTTP header conflicts | Verify HTTP response headers match hreflang language |
| Caching plugin serves wrong-locale hreflang | Cache key doesn't include locale | Configure cache plugin to vary by locale (per-stack instructions) |

## Useful tools

- **Google Search Console** → International Targeting report (post-phase-30)
- **hreflang.org** — online hreflang validator (paste URL + URLs of alternates → flags reciprocity errors)
- **Screaming Frog SEO Spider** — crawls site + reports hreflang chains
- **Lighthouse** (built into Chrome DevTools) — flags missing `lang` attribute (a related signal)

## See also

- `Workstreams/website-builder/foundation/DESIGN-i18n.md` §"hreflang tags" — design-doc anchor
- `i18n/language-switcher.md` — visible UI counterpart to hreflang metadata
- `i18n/strings-schema.md` — strings layer (not directly related to hreflang but adjacent)
- `i18n/rtl.md` — RTL languages emit hreflang the same way as LTR
- `adapters/stack-{name}.md#i18n-recipe` — per-stack i18n integration
- https://developers.google.com/search/docs/specialty/international/localized-versions — Google's spec
- https://rfc-editor.org/rfc/rfc5646 — BCP 47 language tag spec (what hreflang uses)
