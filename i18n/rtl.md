# i18n — RTL (Right-to-Left) Layout

> Discipline for Arabic / Hebrew / Persian / Urdu / etc. — **stack-agnostic**. The agent uses CSS logical properties from phase 18 onward, which makes RTL "free" for simple layouts. Per-stack hooks for setting `dir="rtl"` + locale binding live in `adapters/stack-{name}.md#i18n-recipe`.
>
> Anchor: `DESIGN-i18n.md` §"RTL support" (lines 256-267).

## When RTL applies

RTL languages declared in `project.yaml.rtl_languages`. Common RTL languages:

| Code | Language | Native script |
|---|---|---|
| `ar` | Arabic | العربية |
| `he` | Hebrew | עברית |
| `fa` | Persian / Farsi | فارسی |
| `ur` | Urdu | اردو |
| `yi` | Yiddish | ייִדיש |
| `dv` | Divehi | ދިވެހި |

Configured at session-start (or phase 11 when stack is decided). Example `project.yaml`:

```yaml
languages: [en, de, ar]
default_language: en
rtl_languages: [ar]
```

A language file with `"$language": "ar"` is automatically rendered RTL when this list contains `ar`.

## Discipline 1 — CSS logical properties (mandatory)

**From phase 18 onward, all component code uses CSS logical properties — never physical properties.** This makes most layouts adapt automatically when `dir="rtl"` is set.

| Physical (do NOT use) | Logical (use this instead) |
|---|---|
| `margin-left` | `margin-inline-start` |
| `margin-right` | `margin-inline-end` |
| `padding-left` | `padding-inline-start` |
| `padding-right` | `padding-inline-end` |
| `border-left` | `border-inline-start` |
| `border-right` | `border-inline-end` |
| `left: 0` | `inset-inline-start: 0` |
| `right: 0` | `inset-inline-end: 0` |
| `text-align: left` | `text-align: start` |
| `text-align: right` | `text-align: end` |
| `float: left` | `float: inline-start` |
| `float: right` | `float: inline-end` |

**Tailwind equivalents (Tailwind v3.3+ supports logical properties):**

| Physical (do NOT use) | Logical (use this instead) |
|---|---|
| `ml-4` / `mr-4` | `ms-4` / `me-4` |
| `pl-4` / `pr-4` | `ps-4` / `pe-4` |
| `border-l` / `border-r` | `border-s` / `border-e` |
| `left-0` / `right-0` | `start-0` / `end-0` |
| `text-left` / `text-right` | `text-start` / `text-end` |

Component code that respects logical properties needs **zero changes** to flip from LTR to RTL — the browser does the work when `dir="rtl"` is set on the HTML root or a containing element.

## Discipline 2 — `dir="rtl"` HTML attribute

For pages rendered in an RTL language, `<html dir="rtl">` (or `<html dir="rtl" lang="ar">`) must be set. Per-stack mechanism in `adapters/stack-{name}.md#i18n-recipe`:

- **Static / SSR stacks (Next.js / Astro / WordPress / Hugo):** locale-aware layout sets `dir` on `<html>` at render time per request locale.
- **SPA stacks:** locale switcher updates `document.documentElement.dir` on language change.
- **Canvas / visual stacks (Framer / Webflow):** native platform support (where present) sets `dir` automatically; gaps documented per-stack.

The session-start hook validates that every page rendered in an RTL language has `dir="rtl"` set somewhere in its render path.

## Discipline 3 — Direction-aware iconography

Icons that imply direction must flip in RTL contexts:

| Icon | LTR direction | RTL direction |
|---|---|---|
| Back arrow (`←`) | Points left | Points right |
| Forward arrow (`→`) | Points right | Points left |
| Chevron right (`›`) | "Next" | "Previous" |
| Chevron left (`‹`) | "Previous" | "Next" |
| Progress bar fill | Fills left→right | Fills right→left |
| Breadcrumb separator (`>`) | Points forward | Mirrors |

**Implementation pattern:** wrap directional icons in a CSS class that mirrors via transform:

```css
[dir="rtl"] .icon-directional {
  transform: scaleX(-1);
}
```

Or use icon libraries that ship LTR + RTL variants explicitly (Material Icons has `_rtl` suffixes for some glyphs).

**Icons that do NOT flip:** anything semantically neutral (magnifying glass, settings cog, user avatar, X close button). Flipping these is wrong — common bug in early RTL implementations.

## Discipline 4 — Bidirectional text (BiDi)

Pages may contain mixed LTR and RTL content (e.g. an Arabic page mentioning an English brand name). Browsers handle BiDi via the Unicode Bidirectional Algorithm, but a few gotchas:

### Form inputs with mixed content

```html
<input type="text" dir="auto" value="...">
```

`dir="auto"` lets the browser detect direction per input value. Use for email fields, URL fields, any input that might contain LTR content in an otherwise RTL form.

### Inline language switches

Use the `lang` attribute on inline spans:

```html
<p>الموقع مبني باستخدام <span lang="en" dir="ltr">React</span> و <span lang="en" dir="ltr">Tailwind</span>.</p>
```

Browsers render `<span lang="en" dir="ltr">` LTR within the RTL paragraph.

### CSS isolation for unknown-direction content

```css
.user-generated-content {
  unicode-bidi: isolate;
}
```

Prevents adjacent text from getting reordered when the content's direction differs.

## Discipline 5 — Layout mirroring

Page structure mirrors automatically when logical properties are used everywhere. Specific patterns:

- **Nav bar:** logo flips to the right; nav links flow right-to-left. Logical properties handle this if the nav is implemented as `display: flex; gap: ...` with logical margins.
- **Hero with image + text side-by-side:** flex order reverses naturally. If the design intent requires image-left-in-LTR / image-right-in-RTL, use `flex-direction: row` + logical properties (correct). If the design intent requires image-always-on-the-physical-left regardless of language, use `flex-direction: row` + force `[dir="rtl"]` to `flex-direction: row-reverse` (rare).
- **Sidebar layouts:** sidebar flows to the inline-start (visually-left in LTR, visually-right in RTL) by default. Logical properties handle this.
- **Breadcrumbs:** order reverses naturally with `display: flex` + logical separators.
- **Dropdowns / tooltips / popovers:** anchor logic must respect direction. Most modern libraries (Radix, Headless UI) do this correctly; verify per component.

## Discipline 6 — Typography for RTL scripts

Arabic / Hebrew / Persian / Urdu fonts have different metrics from Latin fonts:

- **Line height:** RTL scripts often need 1.5-1.8 line height (Latin typically 1.3-1.5). Apply via `lang`-scoped CSS:
  ```css
  :lang(ar), :lang(he), :lang(fa), :lang(ur) {
    line-height: 1.7;
  }
  ```
- **Font selection:** generic `serif` / `sans-serif` may not include RTL glyphs. Use explicit fallbacks:
  ```css
  body {
    font-family: "Inter", "Noto Sans Arabic", "Noto Sans Hebrew", sans-serif;
  }
  ```
- **Letter spacing:** never apply tracking (`letter-spacing`) to Arabic — it breaks ligatures. Use `letter-spacing: 0` for `:lang(ar)`.

## Validation (session-start hook + phase 20)

Cross-checks the hook enforces:

1. Every page rendered in an RTL language has `dir="rtl"` set in its render path.
2. No physical-property CSS (`margin-left`, `padding-right`, etc.) in component code on phase-18-output paths. (Lint surfaces violations.)
3. Per-locale Playwright walk at phase 20 (responsive) captures RTL screenshots for visual regression.

Phase 20 (responsive / mobile pass) explicitly tests each RTL language. Phase 26 (SEO) verifies `hreflang` tags for RTL languages.

## Common failure modes

| Failure | Cause | Fix |
|---|---|---|
| Layout looks fine in LTR; broken in RTL | Component code uses physical properties | Refactor to logical properties; lint should have caught this |
| Icons point wrong way in RTL | Directional icons not in `.icon-directional` class | Add the class + `[dir="rtl"]` transform |
| Mixed-content paragraph rendered with wrong direction | Missing `lang`/`dir` on inline spans | Add per-language spans for LTR brand names / code / URLs |
| Form input with email shows reversed text | Missing `dir="auto"` on input | Add `dir="auto"` |
| Arabic text has weird gaps between letters | `letter-spacing` applied globally | Scope `letter-spacing: 0` for `:lang(ar)` |
| Dropdown menu opens on the wrong side | Anchor logic doesn't respect direction | Verify the component library supports RTL; switch to one that does (Radix, Headless UI) |
| Site looks correct but Lighthouse flags missing `lang` | `<html lang="...">` not set per locale | Wire per-stack — see `adapters/stack-{name}.md#i18n-recipe` |

## See also

- `DESIGN-i18n.md` §"RTL support" — design-doc anchor
- `i18n/strings-schema.md` — string format (RTL languages mirror the schema)
- `i18n/language-switcher.md` — switcher behavior + per-stack implementation
- `i18n/hreflang.md` — hreflang for RTL languages
- `adapters/stack-{name}.md#i18n-recipe` — per-stack `dir="rtl"` wiring + locale hooks
- https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_logical_properties_and_values — MDN reference
- https://rtlstyling.com/ — practical RTL CSS guide
