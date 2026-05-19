# i18n — Language Switcher

> The visible UI control that lets users pick their language. **Stack-agnostic intro + required behavior shared by all stacks; per-stack implementation sections authored by the Phase 3 stack-adapter Captains.**
>
> Anchor: `Workstreams/website-builder/foundation/DESIGN-i18n.md` §"Language switcher component" (lines 218-238).

## Overview

The language switcher is the user-facing UI for picking a language. On any multilingual site (≥2 languages in `project.yaml.languages`), the switcher is **mandatory** — it lives in the header or footer (user choice at phase 10 / 17) and is keyboard- and screen-reader-accessible.

The switcher is a component the agent generates at phase 18 per the chosen stack. Implementation details vary by stack (native widget in WordPress via Polylang vs. custom React component in Next.js vs. Framer Custom Component); the required behavior + accessibility contract does not.

The switcher reads `current_language`, `available_languages`, and `language_labels` from project state (props sourced from `project.yaml.languages` + a hardcoded label map shipped with the project). On select, it navigates to the same page in the target language by rewriting the URL per the configured routing strategy (`prefix` / `subdomain` / `tld` per `DESIGN-i18n.md` §"Routing strategies").

## Required behavior (all stacks)

Every stack-specific implementation MUST satisfy:

- **Detect current language** — read from URL prefix (or subdomain, or TLD) per `project.yaml.language_routing`. The switcher reflects the active language in its display (highlighted item, checkmark, etc.).
- **List all available languages** — read from `project.yaml.languages`. Display order matches the array order in `project.yaml`.
- **Set `hreflang` on each language link** — so search engines understand the alternates (see `i18n/hreflang.md`). The switcher's `<a>` elements include `hreflang="..."` attributes.
- **Deep-link to the same page in the target language** — clicking "Deutsch" from `/en/about` navigates to `/de/about`, not `/de/`. The switcher resolves the current path → target-locale path per routing strategy.
- **Persist preference** — store the user's last-selected language in `localStorage` under `wb_lang_pref` (or per-stack equivalent). On next visit to root `/`, redirect to the stored preference (or to the user's `Accept-Language` header if no preference stored, falling back to `default_language`).
- **Accessibility:**
  - `aria-label` set from `strings.nav.language_switcher_label` (e.g. "Language" / "Sprache" / "Langue")
  - Keyboard navigable (Tab to focus; Arrow keys to navigate options in dropdown variant; Enter to select)
  - Screen-reader-announces the current language + that switching navigates to a different page
  - Focus ring visible (per design system phase 17)
- **Touch-friendly** — minimum 44×44px tap target per WCAG 2.2 Success Criterion 2.5.8.
- **Display pattern auto-pick:**
  - 2-3 languages → inline (small chips: `EN | DE | FR`)
  - 4+ languages → dropdown menu
  - Override in `project.yaml.language_switcher.pattern` if user prefers otherwise

## Component shape (stack-agnostic)

The `LanguageSwitcher` component contract:

```
Props:
  current_language: string         # e.g. "en"
  available_languages: string[]    # e.g. ["en", "de", "fr"]
  language_labels: { [code]: string }   # e.g. { en: "English", de: "Deutsch", fr: "Français" }
  current_path: string             # e.g. "/about" (without locale prefix)
  pattern: "inline" | "dropdown"   # auto-picked by count, overridable

Emits:
  Navigation to "{routing-strategy-applied-path}" in the chosen language
```

The agent generates this component at phase 18; per-stack implementation per the sections below.

## Implementation strategies (high-level)

The implementation differs per stack but converges on the same behavior:

- **SSR / SSG stacks** (Next.js, Astro, WordPress, Hugo): server renders the switcher with locale-bound links per request; no client-side state needed for the switcher itself.
- **Canvas / visual stacks** (Framer, Webflow): native localization widget where available, else a Custom Component wrapping the platform's locale API.
- **SPA-like stacks**: client component reads route + writes to history API on select; persists preference to `localStorage`.

Per-stack sections below carry the specific component code, library bindings, routing-rewrite logic, and known platform gotchas.

---

### Framer

<!-- TODO — authored by Phase 3 Captain F per INST-wb-phase3-captain-framer.md.
     This section MUST cover:
     - Custom Component file path (e.g. `code/LanguageSwitcher.tsx`)
     - Framer-CMS-driven vs prop-driven approach
     - useLocale() / Link-with-locale binding
     - hreflang emission via Framer's project-level locale config (or manual in head injection)
     - Pattern auto-pick (inline vs dropdown) wired to Framer prop control
     - localStorage persistence pattern (Framer-CMS-aware)
     - Accessibility verification (Framer canvas + property controls)
     - Known Framer gotchas
     - Cross-reference: `adapters/stack-framer.md#i18n-recipe`, `i18n/hreflang.md#framer`
-->

### Next.js + shadcn

**Component file path:** `components/LanguageSwitcher.tsx` (Client Component — `'use client'` at file top).

**Library bindings:** `next-intl` for locale awareness (`useLocale()`, `usePathname()` from `next-intl/navigation`, `<Link>` from `next-intl/navigation` for locale-prefixed routing). `next/navigation` for `useRouter()` when programmatic navigation is needed (e.g., after persisting preference). shadcn `DropdownMenu` primitive (Radix-backed; install via `npx shadcn@latest add dropdown-menu`) for the ≥4-language variant; raw shadcn `Button` with `<Link>` children for the 2-3-language inline variant.

**App Router segment integration:** the switcher reads the current locale from `useLocale()` (next-intl client hook); reads the locale-less pathname via `next-intl/navigation`'s `usePathname()` (which strips the `[lang]` prefix automatically); renders one link per target locale using `next-intl`'s `Link` (locale-prefix rewriting handled). The surrounding `app/[lang]/layout.tsx` calls `setRequestLocale(lang)` per the canonical next-intl App Router pattern.

**Pattern auto-pick:**

- **2-3 languages → inline buttons.** Rendered as shadcn `Button` (variant `ghost`, `size="sm"`) wrapping next-intl `<Link>`. Current locale visually highlighted via `variant="default"`. Compact horizontal flex layout (`gap-1`) in the header or footer.
- **4+ languages → shadcn `DropdownMenu`.** `DropdownMenuTrigger` shows the current locale's label + chevron icon; `DropdownMenuContent` lists all locales as `DropdownMenuRadioGroup` items; current locale is the active radio.

Override via `project.yaml.language_switcher.pattern` ("inline" | "dropdown") when the user prefers.

**Implementation (inline variant, 2-3 languages):**

```tsx
'use client';

import { useLocale, useTranslations } from 'next-intl';
import { Link, usePathname } from '@/i18n/navigation';
import { routing } from '@/i18n/routing';
import { Button } from '@/components/ui/button';

const LANGUAGE_LABELS: Record<string, string> = {
  en: 'English',
  de: 'Deutsch',
  fr: 'Français',
  it: 'Italiano',
  rm: 'Rumantsch',
};

export function LanguageSwitcher() {
  const currentLocale = useLocale();
  const pathname = usePathname();
  const t = useTranslations('nav');

  return (
    <nav aria-label={t('language_switcher_label')} className="flex gap-1">
      {routing.locales.map((loc) => (
        <Button
          key={loc}
          asChild
          size="sm"
          variant={loc === currentLocale ? 'default' : 'ghost'}
          className="min-w-[44px] min-h-[44px]"
        >
          <Link href={pathname} locale={loc} hrefLang={loc}>
            {loc.toUpperCase()}
            <span className="sr-only">— {LANGUAGE_LABELS[loc]}</span>
          </Link>
        </Button>
      ))}
    </nav>
  );
}
```

**Implementation (dropdown variant, ≥4 languages):**

```tsx
'use client';

import { useEffect } from 'react';
import { useLocale, useTranslations } from 'next-intl';
import { Link, usePathname } from '@/i18n/navigation';
import { useRouter } from 'next/navigation';
import { routing } from '@/i18n/routing';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { ChevronDown } from 'lucide-react';

const LANGUAGE_LABELS: Record<string, string> = {
  en: 'English', de: 'Deutsch', fr: 'Français', it: 'Italiano', rm: 'Rumantsch',
  es: 'Español', pt: 'Português', nl: 'Nederlands', pl: 'Polski', ja: '日本語',
  'zh-CN': '中文', ko: '한국어', ar: 'العربية', he: 'עברית',
};

export function LanguageSwitcher() {
  const currentLocale = useLocale();
  const pathname = usePathname();
  const router = useRouter();
  const t = useTranslations('nav');

  // Persist locale on mount whenever currentLocale shifts (hydration-safe)
  useEffect(() => {
    try {
      localStorage.setItem('wb_lang_pref', currentLocale);
    } catch {/* localStorage blocked — fail silently */}
  }, [currentLocale]);

  function handleSelect(loc: string) {
    try { localStorage.setItem('wb_lang_pref', loc); } catch {/* ignore */}
    // next-intl Link is preferred for declarative; router.push for programmatic
    router.push(`/${loc}${pathname}`);
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          aria-label={t('language_switcher_label')}
          className="min-w-[44px] min-h-[44px] gap-1"
        >
          {currentLocale.toUpperCase()}
          <ChevronDown className="h-4 w-4" aria-hidden="true" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuRadioGroup value={currentLocale} onValueChange={handleSelect}>
          {routing.locales.map((loc) => (
            <DropdownMenuRadioItem
              key={loc}
              value={loc}
              asChild
            >
              <Link href={pathname} locale={loc} hrefLang={loc}>
                {LANGUAGE_LABELS[loc] ?? loc.toUpperCase()}
              </Link>
            </DropdownMenuRadioItem>
          ))}
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
```

**Routing-rewrite logic:** delegated to `next-intl/navigation`'s `Link` + `usePathname` — next-intl strips the current `[lang]` prefix from `pathname` and the `locale` prop on `<Link>` re-applies the target prefix. The agent does NOT hand-roll path manipulation; next-intl owns this and handles edge cases (trailing slash, query-string preservation, search params, hash fragments).

**i18n navigation helper file** (referenced by the snippets above as `@/i18n/navigation`):

```ts
// i18n/navigation.ts
import { createNavigation } from 'next-intl/navigation';
import { routing } from './routing';

export const { Link, redirect, usePathname, useRouter, getPathname } =
  createNavigation(routing);
```

This is the canonical next-intl App Router navigation surface — wraps Next.js `next/navigation` with locale awareness.

**Server vs Client split:** the switcher is a **Client Component** because it uses `localStorage` (persistence) + `useEffect` (hydration-safe write). The surrounding `app/[lang]/layout.tsx` is a **Server Component** that renders `<LanguageSwitcher />` in the header/footer. The Client/Server boundary is the switcher's import point — only the switcher itself joins the client bundle, not the surrounding layout. **`'use client'` directive MUST be at file top before any imports** (per the cross-cutting discipline in `adapters/stack-nextjs.md` §"Component library pairing" → Server / Client component boundary).

**localStorage persistence:**

- **On select:** `localStorage.setItem('wb_lang_pref', loc)` inside `handleSelect` (dropdown) OR on click + before navigation (inline variant — handled by next-intl `Link`'s native nav; persistence done in `useEffect` after route change).
- **On first visit to root `/`:** a separate Server Component reads `Accept-Language` header via `headers()` API + checks `cookies()` for `wb_lang_pref` (if mirrored to a cookie for SSR access), redirects to the preferred locale. Pure-`localStorage` reads are client-only — for SSR-aware preference, the agent mirrors `localStorage` to a cookie via a thin Client Component on mount. Pattern:
  ```tsx
  // app/page.tsx (root — no [lang] segment) — Server Component
  import { redirect } from 'next/navigation';
  import { headers, cookies } from 'next/headers';
  import { routing } from '@/i18n/routing';

  export default async function RootRedirect() {
    const cookieStore = await cookies();
    const stored = cookieStore.get('wb_lang_pref')?.value;
    if (stored && routing.locales.includes(stored)) {
      redirect(`/${stored}`);
    }
    const headerList = await headers();
    const acceptLang = headerList.get('accept-language') || '';
    const matched = routing.locales.find((loc) => acceptLang.toLowerCase().startsWith(loc.toLowerCase()));
    redirect(`/${matched ?? routing.defaultLocale}`);
  }
  ```
- **Client-side cookie mirror** (one-liner Client Component mounted in layout):
  ```tsx
  'use client';
  import { useEffect } from 'react';
  import { useLocale } from 'next-intl';
  export function LocaleCookieMirror() {
    const locale = useLocale();
    useEffect(() => {
      document.cookie = `wb_lang_pref=${locale}; path=/; max-age=31536000; SameSite=Lax`;
    }, [locale]);
    return null;
  }
  ```

**Accessibility:** Radix `DropdownMenu` primitives (under shadcn) include keyboard + screen-reader support out of the box — Tab to focus trigger, Enter/Space to open, Arrow keys to navigate items, Escape to close, focus trap inside the menu, ARIA roles auto-applied. The agent verifies:

- `aria-label` set from `strings.nav.language_switcher_label` (`t('language_switcher_label')` in the snippets above)
- `min-h-[44px] min-w-[44px]` Tailwind utilities on both the trigger button (dropdown) and each inline button — satisfies WCAG 2.2 SC 2.5.8 (Target Size)
- Current locale visually distinguished (button variant for inline; radio-checked state for dropdown)
- Focus ring visible per the phase-17 design system (shadcn's default ring tokens — `--ring` OKLCH variable in `globals.css`)
- Screen-reader announces target language via `sr-only` span (inline variant) or full label (dropdown variant)

**Known Next.js gotchas:**

- **Don't use `next/link` directly for locale-aware navigation** — it doesn't know about the `[lang]` segment. Always use the next-intl `Link` from `i18n/navigation.ts`. Wrong import is a silent bug — the URL changes but the locale doesn't.
- **`usePathname()` from `next/navigation` includes the locale prefix** (e.g., `/en/about`); `usePathname()` from `next-intl/navigation` strips it (e.g., `/about`). The switcher MUST use the next-intl version — otherwise the locale-switch URL becomes `/de/en/about`.
- **Static export (`output: 'export'`) requires all locales pre-generated** via `generateStaticParams` in `app/[lang]/layout.tsx` returning `routing.locales.map((lang) => ({ lang }))`. Missing this yields 404 on direct locale-URL access.
- **Middleware locale-detection** via next-intl's `createMiddleware` is the alternative to the root-page redirect pattern above; pick one approach and stick with it (agent picks middleware by default for SSR-aware locale detection; root-page redirect is the static-export fallback).

**Cross-references:**

- `adapters/stack-nextjs.md` §"i18n integration" — the per-stack setup this section consumes (`next-intl` config, `i18n/request.ts`, `i18n/routing.ts`, `app/[lang]/layout.tsx`)
- `i18n/hreflang.md#next-js--shadcn` — paired hreflang emission for the same multilingual pages
- `i18n/strings-schema.md` — the `nav.language_switcher_label` key contract
- `i18n/rtl.md` — RTL locales mirror the switcher visually (right-to-left flex order)

### WordPress

<!-- TODO — authored by Phase 3 Captain H per INST-wb-phase3-captain-wordpress.md.
     This section MUST cover:
     - Polylang vs WPML widget choice + rationale
     - Native widget vs custom theme template part
     - Where in the theme to render (`header.php` / template part)
     - hreflang emission via plugin (Polylang/WPML auto-emit) — verify per plugin
     - Pattern auto-pick (Polylang/WPML widget vs custom template)
     - localStorage persistence via inline JS (WP doesn't ship with state management — inline script in `wp_footer`)
     - Accessibility: verify the plugin's widget meets WCAG; custom-fallback when it doesn't
     - i18n string source — strings.json shipped as theme `lang/*.po` files vs inline (Polylang strings translation panel)
     - Known WP gotchas: caching plugins must vary by locale; CDN configuration; URL rewriting
     - Cross-reference: `adapters/stack-wordpress.md#i18n-recipe`, `i18n/hreflang.md#wordpress`
-->

---

## Routing strategy quick-reference

The switcher's URL rewrite depends on `project.yaml.language_routing`:

| Strategy | Rewrite example (English `/about` → German) |
|---|---|
| `prefix` (default) | `/about` → `/de/about` (default-language root or `/en/about`) |
| `subdomain` | `example.com/about` → `de.example.com/about` |
| `tld` | `example.com/about` → `example.de/about` |

Per-stack section above documents how the rewrite is implemented in that stack.

## Validation (session-start hook + phase 22 a11y)

1. Multilingual site (≥2 languages) has a language switcher in header OR footer (read from sitemap.yaml).
2. Switcher's accessibility tree includes `aria-label` from `strings.nav.language_switcher_label`.
3. Switcher's link targets resolve to existing pages per language (no broken language-page combinations).
4. Phase 22 (a11y audit) verifies keyboard navigation + screen reader announcement.

## Common failure modes

| Failure | Cause | Fix |
|---|---|---|
| Switcher missing on multilingual site | Component not added at phase 18 | Add per-stack instructions in this file's relevant section |
| Switcher deep-links to wrong page | URL rewrite logic doesn't strip / replace locale prefix correctly | Verify per-stack section's URL rewrite logic against `project.yaml.language_routing` |
| Preference not persisted across visits | `localStorage` not set on select OR not read on root visit | Add to per-stack section's behavior |
| Inaccessible (no keyboard nav) | Custom dropdown without Radix / Headless UI primitive | Use platform primitives that ship a11y by default |
| Wrong language pre-selected | Detection logic reads default instead of URL | Verify per-stack section's detection logic |

## See also

- `Workstreams/website-builder/foundation/DESIGN-i18n.md` §"Language switcher component" — design-doc anchor
- `i18n/strings-schema.md` — `strings.nav.language_switcher_label` source
- `i18n/hreflang.md` — per-stack hreflang emission paired with switcher
- `i18n/rtl.md` — RTL languages in the switcher (mirror order)
- `adapters/stack-{name}.md#i18n-recipe` — per-stack i18n integration
