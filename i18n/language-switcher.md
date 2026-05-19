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

The WordPress language switcher lives in `parts/header.html` (or the alternative footer location per phase-10 / phase-17 decision) inside the block theme. Two implementation paths — pick at phase 12 based on the i18n plugin choice:

**Plugin choice + widget vs custom-template trade-off.** Polylang is the default per the §5 framing in `adapters/stack-wordpress.md` (free, ~80% of WPML's features). WPML is the upgrade path for commercial sites. Both ship a native language-switcher widget (or shortcode); both can be overridden with a custom theme template part. Pick the native widget for minimum agent code; pick the custom template part for full brand control over markup + accessibility.

**Pattern auto-pick (inline vs dropdown):** the agent counts `project.yaml.languages` at phase 18. 2-3 languages → inline (small chips: `EN | DE | FR`). 4+ → dropdown. Plugin widgets honor this when configured; custom template parts implement the pattern directly. Override in `project.yaml.language_switcher.pattern` if user prefers otherwise.

**Path A — Polylang widget (default for muggle sites):**

The Polylang widget is registered via the standard WP widget API. Drop into the header via the block editor's Widget Block (FSE-compatible) OR call the function directly from a custom template part:

```php
<?php
/**
 * parts/language-switcher.html — Polylang custom block wrapper
 * Renders the inline pattern; brand-styled via theme.json color/typography presets.
 */
if ( function_exists( 'pll_the_languages' ) ) {
    $languages = pll_the_languages( array(
        'show_flags'     => 0,                  // brand-controlled — no plugin flags
        'show_names'     => 1,
        'display_names_as' => 'name',           // 'Deutsch' not 'de'
        'force_home'     => 0,                  // deep-link to same page in target language
        'hide_current'   => 0,                  // show active language highlighted
        'hide_if_empty'  => 0,
        'echo'           => 0,
        'raw'            => 1,                  // returns array — we control markup
    ) );

    if ( $languages ) {
        $current_lang = pll_current_language();
        ?>
        <nav class="wb-lang-switcher" aria-label="<?php esc_attr_e( 'Language', 'still-humans' ); ?>">
          <ul role="list">
            <?php foreach ( $languages as $lang ) : ?>
              <li>
                <a
                  href="<?php echo esc_url( $lang['url'] ); ?>"
                  hreflang="<?php echo esc_attr( $lang['locale'] ); ?>"
                  lang="<?php echo esc_attr( $lang['slug'] ); ?>"
                  aria-current="<?php echo $lang['slug'] === $current_lang ? 'true' : 'false'; ?>"
                  class="<?php echo $lang['slug'] === $current_lang ? 'is-active' : ''; ?>"
                >
                  <?php echo esc_html( $lang['name'] ); ?>
                </a>
              </li>
            <?php endforeach; ?>
          </ul>
        </nav>
        <?php
    }
}
?>
```

The `pll_the_languages()` call returns the list of available locales with deep-linked URLs (Polylang resolves the target-language path automatically per `project.yaml.language_routing`).

**Path B — WPML widget:**

Same shape; different API. Replace with the `wpml_active_languages` filter:

```php
<?php
$languages = apply_filters( 'wpml_active_languages', null, array(
    'skip_missing' => 0,                       // include languages even if no translation
    'orderby'      => 'custom',
    'order'        => 'asc',
) );
// Same `<nav><ul>...` shape as Path A.
```

**Path C — Custom block (alternative for full design control):**

When the agent's `sections.yaml` calls for a LanguageSwitcher as its own component, register a custom Gutenberg block (`wp-content/plugins/{slug}-blocks/blocks/language-switcher/`). The block's `render.php` reads the plugin's language list (Polylang OR WPML — detect at runtime) and emits the same brand-styled `<nav>` markup. Allows the user to drop the switcher into any page via the block editor.

**hreflang emission via plugin.** Polylang auto-emits hreflang on every public page when "URL Modifications" is enabled (verify at `wp-admin/admin.php?page=mlang_settings`). WPML auto-emits via its SEO module. Per `i18n/hreflang.md#wordpress` for the detail + manual fallback when plugin output is wrong.

**localStorage persistence pattern.** WordPress doesn't ship with client-side state; the persistence layer is implemented as an inline script enqueued in the theme's `wp_footer` action:

```php
<?php
add_action( 'wp_footer', function () {
    $current_lang = function_exists( 'pll_current_language' )
        ? pll_current_language()
        : ( defined( 'ICL_LANGUAGE_CODE' ) ? ICL_LANGUAGE_CODE : null );

    if ( ! $current_lang ) {
        return;
    }
    ?>
    <script id="wb-lang-pref">
      (function () {
        try {
          var current = <?php echo wp_json_encode( $current_lang ); ?>;
          var stored = localStorage.getItem('wb_lang_pref');
          // On click of any switcher link, store the chosen language
          document.querySelectorAll('.wb-lang-switcher a').forEach(function (a) {
            a.addEventListener('click', function () {
              try { localStorage.setItem('wb_lang_pref', a.getAttribute('lang')); } catch (e) {}
            });
          });
          // If user lands on root with a stored pref different from current, redirect
          var path = location.pathname;
          var isRoot = path === '/' || path === '';
          if (isRoot && stored && stored !== current) {
            // routing-prefix navigation — Polylang's pll_home_url maps to the target
            var target = (<?php echo wp_json_encode( pll_home_url( $current_lang ) ); ?>)
              .replace('/' + current + '/', '/' + stored + '/');
            if (target !== location.href) { location.replace(target); }
          }
        } catch (e) {}
      })();
    </script>
    <?php
}, 50 );
?>
```

Adapt the WPML branch similarly using `wpml_language_url` filter.

**Accessibility verification.** The custom-template-part path (above) ships WCAG-compliant markup by construction (`<nav aria-label>`, `aria-current` on active language, real `<a>` elements with proper `lang` + `hreflang`, 44×44px tap targets via theme.json spacing presets, focus ring from design system phase 17). The plugin widgets vary in a11y quality — Polylang's default widget is mostly clean; WPML's stock widget needs explicit overrides for `aria-current`. The agent runs phase 22 (a11y audit) verification regardless of which path the user picked.

**i18n string source.** `strings.json` (Layer 3) ships as the theme's `lang/{slug}.pot` source bundle + per-locale `lang/{slug}-{lang}.po`/`.mo` files (per §5 in `adapters/stack-wordpress.md`). The `strings.nav.language_switcher_label` key becomes the `aria-label="<?php esc_attr_e( 'Language', 'still-humans' ); ?>"` PHP call. Polylang + WPML both ship a String Translation panel for in-admin string overrides; the agent's default is `.po`-file-based translation (phase 16 inline OR Pattern 2 handoff).

**Known WP gotchas:**

- **Caching plugins must vary cache by locale.** WP Rocket, W3 Total Cache, LiteSpeed Cache all need explicit per-locale-cache-key configuration. Without it, all visitors see the same cached language regardless of switcher action. Verify at phase 28 deploy + after every cache flush.
- **CDN configuration.** Cloudflare's "Always Online" or "Page Rules" may bypass WordPress entirely and serve a stale locale. Set Cloudflare "Cache Level: Standard" + use Cache Rules to vary by `Accept-Language` header OR by URL prefix.
- **URL rewriting.** Polylang + WPML both write `.htaccess` rules for routing. Conflicts with other rewrite plugins (Redirection, custom Yoast rewrites) can break the switcher. Test routing-strategy switches in staging before prod cutover.
- **Permalink structure.** The switcher's deep-link logic depends on the permalink structure (`/%postname%/` is the canonical WP setting for prefix routing). `/?p={id}` URLs break the prefix-rewrite contract — verify at phase 28.
- **Default-language URL ambiguity.** Polylang's default is "hide URL language information for default language" → `/about` (EN) + `/de/about` (DE). Decide at phase 12: keep the toggle on for cleaner URLs OR force `/en/about` for consistency. Either is valid; consistency matters more than choice.

**Cross-reference:** `adapters/stack-wordpress.md` §"i18n integration" (this Captain's authored §5), `i18n/hreflang.md#wordpress` (paired hreflang emission), `i18n/strings-schema.md` (CDJSON contract), `i18n/rtl.md` (RTL switcher mirroring is automatic via CSS logical properties).

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
