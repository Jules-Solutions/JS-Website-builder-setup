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

> Cross-reference: `adapters/stack-framer.md` §"i18n integration" + §"context7 lookups for this stack" + `i18n/hreflang.md#framer`. Verified-current API surface 2026-05-19 via context7 (`/websites/framer_developers`) + WebFetch (`https://www.framer.com/developers/components-reference`).

**Component file:** `code/LanguageSwitcher.tsx` (Framer Code Component; pushed via `framer push` or the Plugins API code-upload). The user drops the component into the header (or footer) Frame on the canvas; it auto-reads project locales + emits navigation per the project's routing strategy.

**Approach — prop-driven with `useLocaleInfo()` fallback:** the switcher reads locale labels + display pattern from `addPropertyControls` props (canvas-editable), and reads the active locale + locale list at runtime from Framer's `useLocaleInfo()` hook. This gives the user canvas-level control over labels/pattern AND keeps the locale-binding live with Framer's project state.

**Verified-current API note:** the hook is `useLocaleInfo()` (returns `{ activeLocale, locales, setLocale }`), NOT `useLocale()` (the older placeholder used in some pre-2026-04 docs including `DESIGN-stack-framer.md` line 117). The agent invokes context7 at phase 18 to re-confirm before generating.

```tsx
// code/LanguageSwitcher.tsx
import { addPropertyControls, ControlType } from "framer"
import { useLocaleInfo } from "framer"
import { useEffect } from "react"

type Props = {
  pattern: "inline" | "dropdown" | "auto"
  language_labels: Record<string, string>   // e.g. { en: "English", de: "Deutsch", fr: "Français" }
  aria_label: string                         // from strings.nav.language_switcher_label
}

export function LanguageSwitcher(props: Props) {
  const { activeLocale, locales, setLocale } = useLocaleInfo()

  // localStorage persistence — last-selected language
  useEffect(() => {
    if (activeLocale?.id) {
      try { window.localStorage.setItem("wb_lang_pref", activeLocale.id) } catch {}
    }
  }, [activeLocale?.id])

  if (!activeLocale || !locales?.length) return null   // gate: pre-hydration / single-locale projects

  // Pattern auto-pick: ≤3 → inline; ≥4 → dropdown (overridable via prop)
  const resolvedPattern =
    props.pattern === "auto" ? (locales.length <= 3 ? "inline" : "dropdown") : props.pattern

  const onSelect = (id: string) => {
    const target = locales.find((l) => l.id === id)
    if (target) setLocale(target)
  }

  if (resolvedPattern === "inline") {
    return (
      <nav aria-label={props.aria_label} role="navigation">
        {locales.map((locale) => (
          <button
            key={locale.id}
            onClick={() => onSelect(locale.id)}
            aria-current={locale.id === activeLocale.id ? "true" : undefined}
            style={{ minWidth: 44, minHeight: 44, padding: "8px 12px" }}
          >
            {props.language_labels[locale.id] ?? locale.name}
          </button>
        ))}
      </nav>
    )
  }

  return (
    <select
      aria-label={props.aria_label}
      value={activeLocale.id}
      onChange={(e) => onSelect(e.target.value)}
      style={{ minHeight: 44, padding: "8px 12px" }}
    >
      {locales.map((locale) => (
        <option key={locale.id} value={locale.id}>
          {props.language_labels[locale.id] ?? locale.name}
        </option>
      ))}
    </select>
  )
}

LanguageSwitcher.defaultProps = {
  pattern: "auto",
  language_labels: { en: "English", de: "Deutsch", fr: "Français", it: "Italiano" },
  aria_label: "Language",
}

addPropertyControls(LanguageSwitcher, {
  pattern: {
    type: ControlType.Enum,
    title: "Pattern",
    options: ["auto", "inline", "dropdown"],
    optionTitles: ["Auto (count-based)", "Inline chips", "Dropdown"],
    defaultValue: "auto",
  },
  language_labels: {
    type: ControlType.Object,
    title: "Locale labels",
    controls: {
      en: { type: ControlType.String, title: "English label", defaultValue: "English" },
      de: { type: ControlType.String, title: "German label", defaultValue: "Deutsch" },
      fr: { type: ControlType.String, title: "French label", defaultValue: "Français" },
      it: { type: ControlType.String, title: "Italian label", defaultValue: "Italiano" },
    },
  },
  aria_label: {
    type: ControlType.String,
    title: "ARIA label",
    description: "From strings.nav.language_switcher_label",
    defaultValue: "Language",
  },
})
```

**Routing rewrite:** delegated to Framer. `setLocale()` triggers Framer's internal locale-aware navigation — Framer rewrites the URL per the project's configured routing strategy (`prefix` default per locked decision 38; subdomain/TLD configured at the Framer project / DNS level). The switcher does NOT manually construct URLs; trust Framer's locale router.

**Display pattern auto-pick:** wired to the `pattern: ControlType.Enum` prop. The component switches to inline chips for ≤3 locales, dropdown for ≥4. User can override on the canvas.

**localStorage persistence:** the `useEffect` on `activeLocale.id` writes to `window.localStorage.wb_lang_pref` per the required-behavior contract. On root-path visit, a small initialization hook (separate `code/LocaleBootstrap.tsx` Code Component dropped on the root Frame) reads `wb_lang_pref` + `Accept-Language` header, calls `setLocale(...)` to redirect to the preferred locale.

**hreflang emission:** Framer's native localization layer auto-emits hreflang tags when project locales are configured (verify via context7 at phase 26). For Frames where native emission misses, see `i18n/hreflang.md#framer` for the manual head-injection escape hatch.

**Accessibility verification:** the component ships with:
- `role="navigation"` + `aria-label` on the inline variant (semantic landmark)
- `aria-current="true"` on the active locale (inline variant)
- Native `<select>` for dropdown variant (browser-provided keyboard + screen-reader semantics)
- 44×44 minimum tap target (CSS inline; verified at phase 22 a11y audit)
- Property controls expose `aria_label` for translation per `strings.nav.language_switcher_label`

Phase 22 Playwright walk verifies keyboard nav + screen reader announcement.

**Known Framer gotchas:**

- `useLocaleInfo()` returns `undefined` during static / pre-hydration render — the `if (!activeLocale || !locales?.length) return null` gate handles it.
- The hook is only available in Framer Code Components; CANNOT be used in a regular React app outside Framer's runtime.
- Locale `id` casing matches what's configured in Framer project settings (typically ISO 639-1: `en`, `de`, `fr`); the agent verifies casing at phase 11 setup.
- Canvas-composed Frames that hardcode locale-specific URLs (e.g. a Frame-level link element typed as `/de/about`) won't auto-switch — they need Framer's locale-aware Link wrapper. Agent flags any such bindings during phase 6.5 re-ingestion.
- Pre-launch on a single-locale project, `useLocaleInfo()` returns one-item list — the gate makes the switcher render nothing, which is correct (no switcher needed for monolingual sites).

### Next.js + shadcn

<!-- TODO — authored by Phase 3 Captain G per INST-wb-phase3-captain-nextjs.md.
     This section MUST cover:
     - Component file path (e.g. `components/LanguageSwitcher.tsx`)
     - next-intl `useLocale()` / `Link` / `usePathname` binding
     - App Router `[lang]/...` segment + `setRequestLocale()` integration
     - shadcn DropdownMenu primitive for ≥4 languages; inline buttons for 2-3
     - hreflang emission (server-rendered `<link rel="alternate">` in layout/head)
     - localStorage persistence via client component + useEffect hydration
     - Accessibility: Radix DropdownMenu primitives include keyboard + screen-reader support out of the box
     - Server vs client component split (switcher is a client component for localStorage; surrounding layout is server)
     - Cross-reference: `adapters/stack-nextjs.md#i18n-recipe`, `i18n/hreflang.md#nextjs`
-->

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
