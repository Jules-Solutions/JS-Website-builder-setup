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

> Cross-reference: `adapters/stack-framer.md` §"i18n integration" + §"context7 lookups for this stack" + `i18n/language-switcher.md#framer`. Verified-current API surface 2026-05-19 via context7 (`/websites/framer_developers`) + WebFetch (`https://www.framer.com/developers/components-reference`).

**Default mechanism — Framer native auto-emit:** when project locales are configured in the Framer Editor (Project Settings → Localization), Framer's runtime auto-emits `<link rel="alternate" hreflang="...">` tags in the page `<head>` for every locale + `x-default`. The agent confirms this is active at phase 26 via context7 + a Playwright walk on the published site that curls the `<head>` and greps for `hreflang`. Auto-emit behavior is the recommended path — minimum custom code, evolves with Framer's locale model.

**Escape hatch 1 — project-level "Custom Code" head injection** (use when native auto-emit misses, e.g. canvas-composed pages with per-locale variant Frames, or Frames where Framer's locale routing diverges from the project's `language_routing` strategy):

1. Project Settings → "Custom Code" → "Head" panel.
2. Inject a `<script>` tag that builds hreflang `<link>` tags dynamically per page based on the page's slug + the locale list. The agent generates this script from `sitemap.yaml` + `project.yaml.languages` + `project.yaml.canonical_host` + (optional) `project.yaml.language_regions`.

Reference shape:

```html
<!-- injected into Framer project's Custom Code → head -->
<script>
(function () {
  var host = "https://example.com";         // from project.yaml.canonical_host
  var defaultLocale = "en";                 // from project.yaml.default_language
  var locales = ["en", "de", "fr"];         // from project.yaml.languages
  var regions = { en: "en", de: "de-CH", fr: "fr-CH" };  // optional from project.yaml.language_regions

  // Detect current path (strip locale prefix per "prefix" routing)
  var path = window.location.pathname.replace(/^\/(?:de|fr|it)(?=\/|$)/, "") || "/";

  locales.forEach(function (l) {
    var lp = (l === defaultLocale) ? path : "/" + l + path;
    var link = document.createElement("link");
    link.rel = "alternate";
    link.hreflang = regions[l] || l;
    link.href = host + lp;
    document.head.appendChild(link);
  });

  // x-default
  var xd = document.createElement("link");
  xd.rel = "alternate";
  xd.hreflang = "x-default";
  xd.href = host + path;
  document.head.appendChild(xd);
})();
</script>
```

**Escape hatch 2 — `<HreflangTags />` Code Component dropped in each Frame's header section.** Same logic as the head script but rendered via React. The agent generates the component; user drops on each Frame. Useful when the user wants per-page hreflang overrides (e.g. a `pricing.en.md` page that exists ONLY in English and intentionally has NO de/fr alternates):

```tsx
// code/HreflangTags.tsx (Framer Code Component)
import { addPropertyControls, ControlType } from "framer"
import { useLocaleInfo } from "framer"
import { useEffect } from "react"

type Props = {
  canonical_host: string
  locales: string[]
  default_locale: string
  language_regions: Record<string, string>   // optional region map
  page_path: string                          // e.g. "/about" — sourced from Frame slug per sitemap.yaml
  emit_x_default: boolean
}

export function HreflangTags(props: Props) {
  useEffect(() => {
    if (typeof document === "undefined") return
    const created: HTMLLinkElement[] = []

    props.locales.forEach((l) => {
      const lp = l === props.default_locale ? props.page_path : `/${l}${props.page_path}`
      const link = document.createElement("link")
      link.rel = "alternate"
      link.hreflang = props.language_regions?.[l] || l
      link.href = `${props.canonical_host}${lp}`
      document.head.appendChild(link)
      created.push(link)
    })

    if (props.emit_x_default) {
      const xd = document.createElement("link")
      xd.rel = "alternate"
      xd.hreflang = "x-default"
      xd.href = `${props.canonical_host}${props.page_path}`
      document.head.appendChild(xd)
      created.push(xd)
    }

    return () => created.forEach((el) => document.head.removeChild(el))
  }, [props.canonical_host, props.default_locale, props.page_path, props.emit_x_default])

  return null   // emits to head only; no visible render
}

HreflangTags.defaultProps = {
  canonical_host: "https://example.com",
  locales: ["en", "de", "fr"],
  default_locale: "en",
  language_regions: {},
  page_path: "/",
  emit_x_default: true,
}

addPropertyControls(HreflangTags, {
  canonical_host: { type: ControlType.String, title: "Canonical host", placeholder: "https://example.com" },
  locales: { type: ControlType.Array, title: "Locales", control: { type: ControlType.String } },
  default_locale: { type: ControlType.String, title: "Default locale" },
  language_regions: {
    type: ControlType.Object,
    title: "Region overrides (optional)",
    controls: {
      en: { type: ControlType.String, title: "en →", placeholder: "en or en-US" },
      de: { type: ControlType.String, title: "de →", placeholder: "de-CH" },
      fr: { type: ControlType.String, title: "fr →", placeholder: "fr-CH" },
    },
  },
  page_path: { type: ControlType.String, title: "Page path", placeholder: "/about", description: "Path without locale prefix" },
  emit_x_default: { type: ControlType.Boolean, title: "Emit x-default", defaultValue: true },
})
```

**Reciprocal hreflang verification (post-phase-30):**

1. Manual: paste each published URL into Google Search Console → International Targeting report; verify the reciprocity map matches expected.
2. Automated (Playwright at phase 29): walk each page, curl the `<head>`, extract hreflang tags, build a reciprocity matrix in-memory, surface any non-reciprocal entries to the user.

**Region codes (when to use):** per the parent doc's "Region-targeting" table, Swiss multilingual sites (DE/FR/IT/EN) typically use `de-CH`, `fr-CH`, `it-CH` — configured via `project.yaml.language_regions` and consumed by the head-script / Code Component as shown above. Framer's native auto-emit MAY use bare codes; if region codes are required, fall back to the head-script escape hatch.

**Known Framer gotchas:**

- **hreflang on draft Frames:** Framer doesn't emit hreflang for unpublished Frames (correct behavior — search engines shouldn't see drafts). If the user has a draft that NEEDS to be discoverable, publish it (or move the discoverable content to a published Frame).
- **hreflang on per-locale variant Frames:** when Frames are per-locale variants (Pattern B), Framer's auto-emit binds each variant to its locale automatically — verify at phase 26 via curl.
- **Cached hreflang via Framer's edge:** Framer's CDN may cache hreflang for ~minutes after locale config changes. If a fresh-curl shows stale hreflang post-change, wait + re-curl OR force-publish the site.
- **`canonical_host` mismatch with Framer-assigned subdomain:** Framer projects get a default `<project>.framer.app` subdomain. hreflang URLs MUST use the user's `project.yaml.canonical_host` (the custom domain configured at deploy), NOT the framer.app subdomain. The head-script / Code Component sources `canonical_host` from project config; the agent flags any mismatch at phase 28.
- **Sites Framer's localization plan-tier doesn't cover:** verify the user's Framer plan supports localization at phase 11 (Pro recommended; lower tiers may not expose locale config). If unsupported, the agent surfaces "localization unavailable on this plan" — either upgrade or accept single-language (which still emits a self-referential hreflang via the head-script escape hatch).

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

WordPress's i18n plugins auto-emit hreflang on every public page when properly configured. The agent's job is verification + manual fallback when plugin output is wrong (broken caching, custom routes the plugin doesn't see, plugin disabled mid-project).

**Polylang — hreflang auto-emit.** Enabled by default when "URL Modifications" is on (`wp-admin/admin.php?page=mlang_settings` → "URL modifications" tab → verify "Hide URL language information for default language" + "Modifications" settings match the `project.yaml.language_routing` choice). Polylang emits one `<link rel="alternate" hreflang="...">` per language per public page including the current page's own hreflang + an `x-default` pointing at the `default_language` version.

Verification:

```bash
# Production verification
curl -s https://example.com/about | grep -i 'hreflang'

# Expected (for site supporting en + de + fr, default en, prefix routing):
# <link rel="alternate" hreflang="en" href="https://example.com/about" />
# <link rel="alternate" hreflang="de" href="https://example.com/de/about" />
# <link rel="alternate" hreflang="fr" href="https://example.com/fr/about" />
# <link rel="alternate" hreflang="x-default" href="https://example.com/about" />
```

**WPML — hreflang auto-emit.** Enabled via WPML's SEO module (`wp-admin/admin.php?page=sitepress-multilingual-cms/menu/languages.php` → "SEO" tab → "Add hreflang tag" → On). x-default behavior is configurable here (default = `default_language`; can be set to a specific language or omitted). Region codes (Swiss `de-CH` / `fr-CH` / `it-CH` etc.) configured at the per-language level via "Edit Languages" → "Default Locale".

**Region codes — both plugins.** When `project.yaml.language_regions` is set (e.g. Swiss multilingual: `de: de-CH`, `fr: fr-CH`, `it: it-CH`), the agent configures each plugin's per-language locale field to emit the region-tagged code:

- **Polylang:** Settings → Languages → Edit → "Locale" field → set to `de_CH` (underscore in WP convention; converted to `de-CH` in hreflang output).
- **WPML:** Languages → Edit Languages → "Default Locale" → set to `de-CH` directly.

**Manual emission fallback (when plugin output is wrong or missing).** Emit hreflang directly from the theme's `wp_head` hook using the plugin's API. Use this when (a) Polylang/WPML disabled mid-project; (b) custom post types that the plugin doesn't include in its default scope; (c) caching plugin serving stale plugin output.

Polylang variant:

```php
<?php
/**
 * functions.php — manual hreflang emission fallback for WordPress + Polylang.
 * Use ONLY when Polylang's auto-emit is missing or wrong; otherwise rely on plugin.
 */
add_action( 'wp_head', function () {
    if ( is_admin() || ! function_exists( 'pll_the_languages' ) ) {
        return;
    }

    // Skip non-public pages
    if ( is_404() || is_user_logged_in() ) {
        // Drop the is_user_logged_in() check if you serve hreflang for logged-in too
    }

    $langs = pll_the_languages( array(
        'raw'           => 1,
        'hide_if_empty' => 0,
    ) );

    if ( empty( $langs ) ) {
        return;
    }

    $default_lang = pll_default_language();

    foreach ( $langs as $lang ) {
        printf(
            "<link rel=\"alternate\" hreflang=\"%s\" href=\"%s\" />\n",
            esc_attr( $lang['locale'] ),                       // e.g. de-CH if configured
            esc_url( $lang['url'] )
        );
    }

    // x-default — points to default-language version
    $default = isset( $langs[ $default_lang ] ) ? $langs[ $default_lang ] : null;
    if ( $default ) {
        printf(
            "<link rel=\"alternate\" hreflang=\"x-default\" href=\"%s\" />\n",
            esc_url( $default['url'] )
        );
    }
}, 5 );
?>
```

WPML variant:

```php
<?php
add_action( 'wp_head', function () {
    if ( is_admin() ) {
        return;
    }

    $languages = apply_filters( 'wpml_active_languages', null, array(
        'skip_missing' => 0,
    ) );

    if ( empty( $languages ) ) {
        return;
    }

    $default_code = apply_filters( 'wpml_default_language', null );

    foreach ( $languages as $lang ) {
        printf(
            "<link rel=\"alternate\" hreflang=\"%s\" href=\"%s\" />\n",
            esc_attr( $lang['default_locale'] ),
            esc_url( $lang['url'] )
        );
    }

    if ( isset( $languages[ $default_code ]['url'] ) ) {
        printf(
            "<link rel=\"alternate\" hreflang=\"x-default\" href=\"%s\" />\n",
            esc_url( $languages[ $default_code ]['url'] )
        );
    }
}, 5 );
?>
```

Both fallbacks check `is_admin()` to avoid emitting on `/wp-admin/*` pages.

**x-default handling.** Polylang adds x-default automatically pointing at `default_language` when "URL Modifications" is on. WPML's behavior is configurable in `wp-admin/admin.php?page=sitepress-multilingual-cms/menu/languages.php` → "SEO" → "x-default". If neither plugin is emitting x-default OR pointing it at the wrong language, use the manual-emission fallback above (it includes x-default by default).

**Caching plugin interaction (this is the failure mode users hit most often).** WP Rocket, W3 Total Cache, LiteSpeed Cache, and managed-host page caches (Kinsta, WP Engine, SiteGround) all cache the rendered `<head>` per URL. If the cache key doesn't include locale, the wrong-locale hreflang gets served:

- **WP Rocket:** Settings → "Add-ons" → enable "WPML" or "Polylang" add-on; cache keys vary by locale automatically. Verify after every plugin update.
- **W3 Total Cache:** Performance → "Page Cache" → "Cache by user agent group" + create a group per language (more brittle than the WP Rocket path; consider switching).
- **LiteSpeed Cache:** Cache → "Cache" → "Vary by Language" → set per Polylang/WPML; works cleanly with LiteSpeed-hosted servers.
- **Cloudflare:** Add a Cache Rule that varies by URL prefix (`/de/*`, `/fr/*`, etc.) OR by `Accept-Language` header. "Always Online" must be off OR explicitly per-language to avoid cross-locale serving.

After ANY locale config change (Polylang/WPML settings, language added/removed, routing-strategy switch), purge ALL caches: plugin + Cloudflare + managed-host. Verify with the curl check above on three random pages, one per language.

**Region targeting — Swiss + multi-region case study.** For Swiss multilingual sites (DE/FR/IT/EN), the canonical region map is `de-CH`, `fr-CH`, `it-CH`, `en`. Configure in `project.yaml`:

```yaml
languages: [en, de, fr, it]
default_language: en
language_routing: prefix
language_regions:
  en: en           # not Swiss-targeted; bare 'en' so Google serves to English-speakers globally
  de: de-CH
  fr: fr-CH
  it: it-CH
```

Then in Polylang Settings → Languages → Edit for each → set "Locale" to `de_CH` / `fr_CH` / `it_CH` (note WP's underscore convention internally; plugin renders to dash-form in HTML).

**Common WordPress hreflang failure modes (in addition to the general failure-modes table above):**

| WP-specific failure | Cause | Fix |
|---|---|---|
| hreflang appears in `view-source` but not in browser inspector | A plugin (often a "minify HTML" plugin like Autoptimize) is stripping `<link>` tags | Configure the minify plugin to preserve `<link rel="alternate">` tags |
| hreflang for one language only (current page) | i18n plugin not active OR "URL Modifications" off | Activate plugin + enable URL Modifications |
| All pages emit `<example.com/wp-admin/...>` for hreflang | `home_url()` returns wrong base | Verify Settings → General → WordPress Address + Site Address are correct |
| Custom post type pages have no hreflang | i18n plugin not configured for that CPT | Polylang: Settings → Languages → "Custom post types and Taxonomies" — enable the CPT. WPML: WPML → Settings → "Post Types Translation" — enable. |
| Sitemap.xml lists translated URLs but hreflang missing | Yoast/RankMath sitemap separate from plugin's hreflang | Verify Yoast's "Languages" XML sitemap extension is active (if using Yoast WPML SEO) |
| Page passes browser hreflang check but Google Search Console flags reciprocity error | One language's page links to translations; the translation's page doesn't link back | Audit each language's HTML head; ensure ALL pages emit the SAME set of hreflang tags (per the §29 spec line: hreflang must be reciprocal) |

**Verification — post-deploy.** Phase 26 (SEO audit) + phase 29 (deploy verification):

1. `curl -s https://example.com/about | grep hreflang` — expect every language + x-default.
2. Same for `/de/about` and `/fr/about` — reciprocity check (must emit identical set).
3. WP admin: Polylang Settings → URL Modifications → reads the live state; WPML → Languages → "SEO" tab shows hreflang status.
4. Google Search Console (post first Google crawl, ~phase 30) → International Targeting report → flags reciprocity errors.
5. https://hreflang.org online validator — paste production URL + alternates; reports broken chains.

**Cross-reference:** `adapters/stack-wordpress.md` §"i18n integration" (this Captain's authored §5), `i18n/language-switcher.md#wordpress` (paired switcher implementation that ships matching `hreflang=` attributes on `<a>` links), `i18n/strings-schema.md` (CDJSON layer that doesn't touch hreflang directly — adjacent).

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
