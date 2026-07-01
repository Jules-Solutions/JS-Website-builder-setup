# Content Design JSON — The Microcopy-as-Data Methodology

The canonical microcopy methodology phases 13-16 implement. Source: Prasaja Mukti, "How content designers can (and should) use JSON files", UX Content Collective, June 10, 2025 — [uxcontent.com/content-design-json](https://uxcontent.com/content-design-json/). Pairing design doc: `DESIGN-content-layers.md` § Layer 3. Methodology verified current as of 2026-05-18 via WebFetch + WebSearch ([Content design in 2026 — UXCC](https://uxcontent.com/content-design-in-2026/)).

## The core problem it solves

Mukti's methodology emerged from the breaking point of discovering **"FOUR different ways to say 'transaction failed'"** across one platform. Copy scattered across pages and components drifts into inconsistency that nobody can see because there's no single place to look. The solution: treat copy as developers treat config — structured, version-controlled, single-source-of-truth JSON. Copy stops being "isolated strings" and becomes "part of a larger ecosystem."

This is the same discipline as phase 15's content/component separation, one layer up: microcopy is data, not scattered string literals embedded in components and pages.

## Why it matters for this pipeline

- **Phase 13** declares the skeleton (the categorical structure with empty values).
- **Phase 15** declares the specific keys each section needs (still empty/placeholder values).
- **Phase 16** values every key, in the phase-5 brand voice.
- **Phase 18+** wires the references via stack-specific i18n integration.

The `{strings.path.to.key}` reference syntax in page bodies (Layer 4) resolves from these files at render time. A single "Cancel" label updates everywhere when changed once. Adding a language is "ship a new JSON file" — no code changes.

## Categorical structure

The methodology organizes copy into two file scopes:

1. **Global config files** — standard copy used throughout the application: button labels, common error messages, navigation items. (In this pipeline: the top-level `cta`, `errors`, `nav` categories.)
2. **Local config files** — feature-specific content (Mukti's examples: `biller_en.json`, `loan_application_id.json`). (In this pipeline: per-feature/per-section key groups within the strings file, or per-page sub-objects.)

Within files, organization follows functional grouping:

```json
{
  "buttons": { "primary": "Get Started" },
  "errors": { "network": "Connection failed. Check your internet and try again." }
}
```

The website-builder's canonical category set (per `DESIGN-content-layers.md` + the phase contracts): `cta`, `errors`, `nav`, `variables`, `dates`, `currency`. Extend with feature-specific categories as sections require (declared at phase 15).

## The four variable categories

The methodology treats copy as dynamic contextual systems, not static strings. Four variable categories:

1. **User variables** — profile data, behavioral history, account status (`{name}` in `"Welcome back, {name}"`).
2. **Contextual variables** — time, location, device, language preferences.
3. **System-status variables** — process states, error conditions, progress indicators (the loading/success/error microcopy triad).
4. **Data variables** — dynamic numbers, calculations, real-time availability (`{count}` in plural forms).

Variable copy uses interpolation (`{name}`) and ICU Message Format for plurals (`{count, plural, =0 {No items} one {# item} other {# items}}`) — stack-agnostic at the strings layer; per-stack i18n integration handles actual interpolation at render. See `references/i18n-translation-workflow.md` for ICU detail (German 2 plural forms, Polish 4, Arabic 6).

## Per-language folder model

Mukti's structure (the single-source-of-truth mirrored per language):

```
copydocs/
├── en/
│   ├── homepage.json
│   ├── onboarding.json
│   ├── errors.json
│   ├── settings.json
│   └── components/
├── id/
│   └── [same structure]
└── README.md
```

The website-builder's adaptation per `DESIGN-content-layers.md` + `DESIGN-project-scaffold.md`: `.website-builder/content/strings/{lang}.json` — one file per language, structure mirrored across languages, values translated. Every language file has the same key structure (validated at session-start hook + phase exit; missing-key fallback per decision 41 shows the default-language string + logs a warning — a safety net, not a license to ship incomplete translations).

## The pipeline schema

The canonical strings-file shape these phases write (per the phase-13/15/16 contracts):

```json
{
  "$language": "en",
  "$schema": "spec/strings-v1.json",
  "cta": {
    "subscribe": "", "subscribe_loading": "", "subscribe_success": "", "subscribe_error": "",
    "contact": "", "essays_read_more": ""
  },
  "errors": { "network": "", "validation_email": "" },
  "nav": {
    "skip_to_content": "", "language_switcher_label": "",
    "home": "", "essays": "", "about": "", "contact": ""
  },
  "variables": { "welcome_back": "", "items_count": "" },
  "dates": { "format_short": "", "format_long": "" },
  "currency": { "symbol": "", "format": "" }
}
```

Phase 13 writes this skeleton (categories present, mostly empty). Phase 15 fills in the specific keys each section declared. Phase 16 values every key in brand voice — including the system-status triad (`subscribe_loading`, `subscribe_success`, `subscribe_error`), which is exactly where voice is most distinctive and most often abandoned (see `references/voice-and-copy-discipline.md` § microcopy).

## 2026 currency of the methodology

Confirmed current (WebSearch 2026-05-18, [Content design in 2026 — UXCC](https://uxcontent.com/content-design-in-2026/)): structured formats like JSON are increasingly load-bearing because LLMs work more reliably when information is explicit, labeled, and predictable — content that "behaves well at scale" requires this structure. Localization-as-design (not translation-alone): plan information hierarchy and UI flexibility for varying word lengths; write source copy with simple sentence structure and consistent terms so downstream translation is smoother (applied in `references/i18n-translation-workflow.md` § writing-for-translatability).

## Stack-specific consumption (phase 18+, not phases 13-16)

For awareness; the wiring happens downstream:

- Astro → `astro-i18n` from `src/i18n/{lang}.json`
- Next.js → `next-intl` from `messages/{lang}.json`
- WordPress → WPML/Polylang strings + theme `lang/` po/mo
- Framer → Framer CMS Strings collection per locale
- Hugo → `i18n/{lang}.toml` (TOML conversion at build)

Phases 13-16 produce the stack-agnostic `strings/{lang}.json`; the per-stack adapter docs own the migration recipe.
