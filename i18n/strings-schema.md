# i18n — strings-schema (Layer 3 — Content Design JSON)

> The Content Design JSON (CDJSON) format the website-builder uses for all microcopy + UI strings. **Stack-agnostic** — every adapter reads the same per-language files. Per-stack consumption recipes live in `adapters/stack-{name}.md#i18n-recipe`.
>
> Anchor design docs: `DESIGN-content-layers.md` Layer 3; `DESIGN-i18n.md`.
> Methodology source: https://uxcontent.com/content-design-json/ (Prasaja Mukti).

## File location

```
.website-builder/content/strings/{lang}.json
```

One file per supported language. Filename is the ISO 639-1 language code (e.g. `en.json`, `de.json`, `fr.json`, `it.json`).

Default language is set in `project.yaml.default_language`. Every other language file mirrors the default's key structure; values are translated.

## Top-level reserved keys

| Key | Type | Required | Purpose |
|---|---|---|---|
| `$language` | string (ISO 639-1) | yes | Self-identifying language code; cross-checked against filename |
| `$schema` | string | yes | Always `spec/strings-v1.json` — version-locked for future migrations |

Any key starting with `$` is reserved for protocol use. User-authored namespaces are bare identifiers (`cta`, `errors`, etc.).

## Key structure

The body is a nested-object tree. Conventions:

- **Top-level namespaces** group related strings: `cta`, `errors`, `nav`, `forms`, `variables`, `dates`, `currency`, `pages.{slug}`. Per-page pages.{slug} namespaces are allowed when a string is genuinely page-bound.
- **Two levels deep is the default.** Three levels (`nav.primary.home`) is the cap. Beyond three levels = the namespace is too granular; flatten.
- **Snake-case keys.** Underscores not hyphens. Predictable downstream — Python / JS / PHP / etc. all read it cleanly.
- **No string values at the top level.** Always wrap in a namespace. `subscribe: "Get the newsletter"` at top-level is invalid; `cta.subscribe` is correct.

## Variable interpolation

Per ICU Message Format (industry standard, supported by every major i18n library).

### Simple substitution

```json
"welcome_back": "Welcome back, {name}"
```

Consumed at render time with `name="Maya"` → `"Welcome back, Maya"`.

### Pluralization

```json
"items_count": "{count, plural, =0 {No items} one {# item} other {# items}}"
```

The Locale-data plugin handles plurals correctly per language (German has 2 plural forms; Polish has 4; Arabic has 6). Per-language string files override the plural categories appropriately:

```json
// pl.json
"items_count": "{count, plural, =0 {Brak elementów} one {# element} few {# elementy} many {# elementów} other {# elementów}}"
```

### Selectors

```json
"greeting_formal": "{formality, select, formal {Sehr geehrte/r {name}} casual {Hallo {name}} other {Hi {name}}}"
```

Variables are stack-agnostic at the strings layer; per-stack i18n integration handles the interpolation. Adapters note any platform-specific limitations in `adapters/stack-{name}.md#i18n-recipe`.

## Reserved namespace conventions

| Namespace | Purpose | Examples |
|---|---|---|
| `cta` | Call-to-action labels + loading/success/error states | `cta.subscribe`, `cta.subscribe_loading`, `cta.subscribe_success`, `cta.subscribe_error` |
| `errors` | User-facing error messages | `errors.network`, `errors.validation_email`, `errors.server_500` |
| `nav` | Navigation labels + accessibility strings | `nav.primary.home`, `nav.skip_to_content`, `nav.language_switcher_label` |
| `forms` | Form field labels, placeholders, helper text | `forms.email_label`, `forms.email_placeholder`, `forms.submit` |
| `variables` | Strings containing interpolated values | `variables.welcome_back`, `variables.items_count` |
| `dates` | Locale-specific date format strings (consumed by `Intl.DateTimeFormat`) | `dates.format_short`, `dates.format_long` |
| `currency` | Locale + currency display | `currency.symbol`, `currency.format` |
| `pages.{slug}` | Strings genuinely scoped to one page (rare — most strings are reusable) | `pages.about.section_bio_heading` |

## Fallback strategy

**Default (per locked decision):** `missing-key-shows-default-and-warn`.

When a key is missing from the current language file:
1. Render the value from the `default_language` file (set in `project.yaml.default_language`).
2. Emit a visible-in-dev console warning identifying the missing key + language. (Adapters wire this per platform — see `adapters/stack-{name}.md#i18n-recipe`.)
3. The session-start hook's cross-language validation surfaces ALL missing keys at session boundary for batch resolution.

Configurable alternatives in `project.yaml.fallback_strategy`:

| Strategy | Behavior |
|---|---|
| `missing-key-shows-default-and-warn` (default) | Show default-language value + warn |
| `missing-key-shows-key` | Show the literal key (`cta.subscribe`) — useful in dev to find gaps |
| `missing-key-throws` | Hard error — useful in CI / pre-release validation |

## Required key contract

For every multilingual site, **every language file MUST have the same key tree** as the default-language file. The session-start hook's cross-language validation enforces this.

Adding a key to `en.json` without adding it to `de.json` + `fr.json` + etc. = validation failure. The agent's phase 16 (copywriting) workflow includes a sync-after-edit step that propagates new keys to all language files (initially as the default-language value, flagged for translation).

## Example: `en.json` (canonical reference)

```json
{
  "$language": "en",
  "$schema": "spec/strings-v1.json",

  "cta": {
    "subscribe": "Get the newsletter",
    "subscribe_loading": "Subscribing...",
    "subscribe_success": "You're in. Check your inbox.",
    "subscribe_error": "Something didn't work. Try again?"
  },

  "errors": {
    "network": "Connection failed. Check your internet and try again.",
    "validation_email": "That doesn't look like a valid email.",
    "server_500": "Our side broke. Please retry in a moment."
  },

  "nav": {
    "primary": {
      "home": "Home",
      "essays": "Essays",
      "about": "About",
      "contact": "Contact"
    },
    "skip_to_content": "Skip to content",
    "language_switcher_label": "Language"
  },

  "forms": {
    "email_label": "Email address",
    "email_placeholder": "you@example.com",
    "submit": "Submit"
  },

  "variables": {
    "welcome_back": "Welcome back, {name}",
    "items_count": "{count, plural, =0 {No items} one {# item} other {# items}}"
  },

  "dates": {
    "format_short": "MMM d, yyyy",
    "format_long": "MMMM d, yyyy"
  },

  "currency": {
    "symbol": "$",
    "format": "{symbol}{amount}"
  }
}
```

## Referencing strings from other layers

- **Layer 4 (page MD)** uses `{strings.x.y.z}` placeholder syntax:
  ```markdown
  primary_cta: "{strings.cta.subscribe}"
  ```
- **Layer 2 (components.yaml)** can reference strings for default prop values:
  ```yaml
  - name: SubscribeButton
    props:
      label: { type: string, default: "{strings.cta.subscribe}" }
  ```
- **Layer 5 (briefs/handoff)** embeds strings inline (briefs are point-in-time snapshots).

All `{strings.x.y.z}` references resolve to the current rendering language at build/render time.

## Validation rules (session-start hook enforces)

1. File parses as valid JSON.
2. `$language` matches filename (e.g. `en.json` has `"$language": "en"`).
3. `$schema` matches expected value (`spec/strings-v1.json`).
4. Key tree matches default-language file's key tree (no missing or extra keys).
5. All ICU Message Format expressions parse correctly.
6. All `{strings.x.y.z}` references in other layers resolve to existing keys.

Validation failures surface to the user with diagnostic + suggested fix.

## See also

- `DESIGN-content-layers.md` Layer 3 — full content-stack context
- `DESIGN-i18n.md` — full i18n model (routing, fallback, RTL, translation workflow)
- `i18n/language-switcher.md` — per-stack switcher implementation
- `i18n/hreflang.md` — per-stack hreflang emission
- `i18n/rtl.md` — RTL layout discipline
- `adapters/stack-{name}.md#i18n-recipe` — per-stack consumption recipe
- https://uxcontent.com/content-design-json/ — methodology source
- https://unicode-org.github.io/icu/userguide/format_parse/messages/ — ICU Message Format spec
