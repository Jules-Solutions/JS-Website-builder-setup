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

**Emission mechanism:** Next.js Metadata API — `generateMetadata()` exported from each page (`app/[lang]/{slug}/page.tsx`) OR from `app/[lang]/layout.tsx` for layout-level coverage. The Metadata API's `alternates.languages` map renders to `<link rel="alternate" hreflang="...">` tags in the `<head>` server-side per request. No manual `<head>` injection; no Client Component plumbing.

**Pattern — per-page hreflang (preferred for explicit per-route control):**

```tsx
// app/[lang]/about/page.tsx — Server Component
import type { Metadata } from 'next';
import { routing } from '@/i18n/routing';

const BASE = process.env.NEXT_PUBLIC_CANONICAL_HOST || 'https://example.com';

// Optional region-targeted hreflang codes when project.yaml.language_regions is set
const HREFLANG_CODES: Record<string, string> = {
  en: 'en',
  de: 'de-CH',
  fr: 'fr-CH',
  it: 'it-CH',
};

function buildLanguagesMap(slug: string) {
  const languages: Record<string, string> = {};
  for (const loc of routing.locales) {
    const code = HREFLANG_CODES[loc] ?? loc;
    languages[code] = `${BASE}/${loc}/${slug}`;
  }
  // x-default per Google spec — points to default-language URL
  languages['x-default'] = `${BASE}/${routing.defaultLocale}/${slug}`;
  return languages;
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ lang: string }>;
}): Promise<Metadata> {
  const { lang } = await params;
  return {
    title: 'About',
    description: 'About page description',
    alternates: {
      canonical: `${BASE}/${lang}/about`,
      languages: buildLanguagesMap('about'),
    },
  };
}

export default async function AboutPage() {
  return <div>About content</div>;
}
```

**Pattern — layout-level hreflang (when slug is parameter-driven and dynamic):**

```tsx
// app/[lang]/[slug]/layout.tsx — for dynamic routes (blog posts, products)
import type { Metadata } from 'next';
import { routing } from '@/i18n/routing';

const BASE = process.env.NEXT_PUBLIC_CANONICAL_HOST || 'https://example.com';
const HREFLANG_CODES: Record<string, string> = { en: 'en', de: 'de-CH', fr: 'fr-CH', it: 'it-CH' };

export async function generateMetadata({
  params,
}: {
  params: Promise<{ lang: string; slug: string }>;
}): Promise<Metadata> {
  const { lang, slug } = await params;
  const languages: Record<string, string> = {};
  for (const loc of routing.locales) {
    const code = HREFLANG_CODES[loc] ?? loc;
    languages[code] = `${BASE}/${loc}/${slug}`;
  }
  languages['x-default'] = `${BASE}/${routing.defaultLocale}/${slug}`;
  return {
    alternates: {
      canonical: `${BASE}/${lang}/${slug}`,
      languages,
    },
  };
}

export default function DynamicLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
```

**Pattern — shared helper (recommended for projects ≥10 pages):**

Extract the language-map builder into `lib/hreflang.ts` to keep per-page boilerplate down + ensure reciprocity:

```ts
// lib/hreflang.ts
import { routing } from '@/i18n/routing';

const BASE = process.env.NEXT_PUBLIC_CANONICAL_HOST || 'https://example.com';
const HREFLANG_CODES: Record<string, string> = {
  en: 'en', de: 'de-CH', fr: 'fr-CH', it: 'it-CH',
};

export function hreflangMap(slug: string): Record<string, string> {
  const out: Record<string, string> = {};
  for (const loc of routing.locales) {
    const code = HREFLANG_CODES[loc] ?? loc;
    out[code] = `${BASE}/${loc}/${slug}`;
  }
  out['x-default'] = `${BASE}/${routing.defaultLocale}/${slug}`;
  return out;
}

export function canonicalUrl(lang: string, slug: string): string {
  return `${BASE}/${lang}/${slug}`;
}
```

Then every page's `generateMetadata` uses the same helper — reciprocity is guaranteed by construction (every page emits the SAME hreflang set per slug across locales).

**Per-page hreflang for dynamic routes (blog posts, product pages):**

Same pattern via `generateStaticParams()` + per-locale generation. Example for blog posts:

```tsx
// app/[lang]/blog/[slug]/page.tsx
import { routing } from '@/i18n/routing';
import { hreflangMap, canonicalUrl } from '@/lib/hreflang';
import { getAllBlogSlugs, getBlogPost } from '@/lib/content';

export async function generateStaticParams() {
  const params = [];
  for (const lang of routing.locales) {
    const slugs = await getAllBlogSlugs(lang);
    for (const slug of slugs) params.push({ lang, slug });
  }
  return params;
}

export async function generateMetadata({ params }) {
  const { lang, slug } = await params;
  const post = await getBlogPost(lang, slug);
  return {
    title: post.title,
    alternates: {
      canonical: canonicalUrl(lang, `blog/${slug}`),
      languages: hreflangMap(`blog/${slug}`),
    },
  };
}
```

**Configuration source for `HREFLANG_CODES`:** read from `project.yaml.language_regions` at scaffold time. When `language_regions` is set (e.g., `de: de-CH`), the agent codegens `HREFLANG_CODES` with those values; when unset, bare ISO 639-1 codes (`de`, `fr`, `it`) are used. Agent regenerates `lib/hreflang.ts` whenever `project.yaml.language_regions` changes.

**`x-default` discipline:** the agent points `x-default` at the `default_language` URL (per `project.yaml.default_language`), NOT at the apex unprefixed root (unless `routing.default_language_at_root` is set — see below). Spec-compliant; matches the language-switcher's preference-detection behavior.

**Hosting URL discipline:** `BASE` reads from `NEXT_PUBLIC_CANONICAL_HOST` env var (set in Vercel Project Settings → Environment Variables at phase 28). The agent NEVER hardcodes `https://example.com` in production code — the placeholder above is only for clarity in the snippet. Production env: `NEXT_PUBLIC_CANONICAL_HOST=https://stillhumans.com` (or per project). Localhost dev: env-var unset → falls through to localhost-safe placeholder (which won't satisfy the absolute-URL rule, but dev pages shouldn't be search-indexed anyway — `robots.txt` blocks dev via `app/robots.ts` conditional logic).

**Apex unprefixed root (when configured):**

Some projects serve the default-language version at `/` AND `/{default_lang}/`. When `project.yaml.routing.default_language_at_root: true`, the agent additionally emits an apex variant in the hreflang map:

```ts
// For routing.default_language_at_root === true
out[HREFLANG_CODES[routing.defaultLocale] ?? routing.defaultLocale] =
  `${BASE}/${slug}`;  // apex URL (no /en/ prefix)
out['x-default'] = `${BASE}/${slug}`;
```

The agent reads this config at the helper's load + adjusts. Without it, the canonical URL is always locale-prefixed.

**Validation (production):**

1. **Build verification:** `pnpm build` produces a successful build with no Next.js Metadata warnings.
2. **Production curl:** `curl -s https://example.com/en/about | grep -E 'rel=.alternate.*hreflang'` returns ≥(locale-count + 1) lines (one per locale + x-default).
3. **Reciprocity check:** for each page across all locales, `curl` + `grep` + compare hreflang sets — all locale-variants of the same slug MUST emit the SAME hreflang set. The agent's `hreflangMap()` helper guarantees this by construction; a deviation indicates a per-page override that bypassed the helper.
4. **`x-default` presence:** `grep 'x-default'` returns one line per page.
5. **Absolute URLs:** `grep 'href="/' page.html` returns ZERO matches inside hreflang tags (all hreflang `href` values start with `http://` or `https://`).

**Phase 26 (SEO audit) verification:**

The agent automates the curl-grep loop at phase 26 — walks every page in `sitemap.yaml`, fetches the production URL, extracts `<link rel="alternate" hreflang="...">` tags via regex, asserts:

- Count = locale-count + 1 (the +1 is x-default)
- All URLs are absolute + match `BASE`
- All URLs resolve (HTTP 200)
- All locale-variants of the same slug emit identical hreflang sets

Failures surface to the user with the diff + the canonical fix path.

**Phase 30 (post-deploy) verification:**

The agent submits sitemap.xml (auto-generated via `app/sitemap.ts`) to Google Search Console. After 24-72 hours, the agent (or user) reviews Search Console → International Targeting report for hreflang errors. Common findings: missing reciprocity (caught earlier by build-time check; should be empty here), non-200 hreflang URLs (deploy-time issue), region-mismatch warnings (cosmetic if `language_regions` config matches user's audience).

**Known Next.js gotchas:**

- **Metadata API requires the function to be ASYNC** when accessing `params` (Next.js 15+ — `params` is a Promise). Synchronous `generateMetadata` ignored without runtime error.
- **`alternates.canonical`** is the per-page canonical URL — the agent ALWAYS sets it alongside `alternates.languages` (both are spec-recommended). Missing canonical hurts SEO independently of hreflang.
- **Static export (`output: 'export'`)** emits all hreflang tags at build time — fine. But the `BASE` env var MUST be set at BUILD time (not runtime) for static export — agent passes via `NEXT_PUBLIC_CANONICAL_HOST=https://... pnpm build` in the deploy script.
- **Trailing slashes:** Vercel's default is no trailing slash; if user opts into `trailingSlash: true` in `next.config.mjs`, the hreflang URLs MUST match (otherwise Vercel redirects + Search Console flags the mismatch). The agent verifies config consistency.
- **Locale-fallback collisions:** if `routing.defaultLocale = 'en'` and a route is missing the English version (only `/de/about` exists, no `/en/about`), the hreflang map points `en` AND `x-default` at a 404. The agent's content-validation hook flags missing per-locale content before deploy.
- **`searchParams` change does NOT re-emit metadata** in static rendering — agent always uses path-based hreflang, never query-string-based.

**Cross-references:**

- `adapters/stack-nextjs.md` §"i18n integration" — the per-stack setup this section consumes (routing config, default-language pattern)
- `i18n/language-switcher.md#next-js--shadcn` — paired switcher component (uses the same locale set)
- `Workstreams/website-builder/foundation/DESIGN-i18n.md` §"hreflang tags" — the design-doc anchor

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
