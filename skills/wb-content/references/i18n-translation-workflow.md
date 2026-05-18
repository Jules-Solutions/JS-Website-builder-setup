# Phase 16 — Multilingual Translation Workflow

The phase-16 multilingual procedure per locked decisions 38-41. Source of truth: `Workstreams/website-builder/foundation/DESIGN-i18n.md` (the canonical i18n design) + the phase-16 contract. i18n is a **default-on capability** in the website-builder, not an afterthought — Switzerland is natively multilingual (DE/FR/IT/EN); EU sites expect 2-4 languages. Single-language sites still work (one strings file); multi-language builds on the same scaffold.

## The four locked decisions phase 16 implements

| Decision | What it locks | Phase-16 effect |
|---|---|---|
| **38** | Prefix URL routing default (`example.com/de/about`) | Per-language file naming; `hreflang` generation |
| **39** | Pattern A pages-per-language default (shared structure, translated prose) | `content/pages/{slug}.{lang}.md` sharing frontmatter |
| **40** | Pattern 1 agent-translates-inline default | Agent translates at phase 16; Pattern 2 is the upgrade path |
| **41** | Missing-key-shows-default-language-string fallback | Render-time safety net + validation warning; NOT a license to ship incomplete |

Routing strategies (decision 38 default = prefix): `prefix` (`/de/about`, simplest, any host), `subdomain` (`de.example.com`, needs DNS per language), `tld` (`example.de`, needs per-language domain). Most users pick prefix; subdomain/tld are advanced.

## Layer 4 — page prose per language (two patterns)

### Pattern A — shared structure, translated prose (decision 39 default, most common)

```
.website-builder/content/pages/
├── about.en.md       # English prose
├── about.de.md       # German prose
└── about.fr.md       # French prose
```

All files share the same structural frontmatter (sections, sitemap reference); only the markdown body + `language` field differ. Use when the message is the same across languages, just translated.

### Pattern B — locale-specific content variation

Different prose, different examples, different sections per market (e.g., `pricing.en.md` USD/US-centric vs `pricing.de.md` CHF/Swiss-centric with different structure). Use when content must differ by market.

The agent asks the user **per page** which pattern fits. Most pages are Pattern A; pricing / market-specific pages may be Pattern B.

## Layer 3 — per-language strings

One `content/strings/{lang}.json` per configured language, structure mirrored, values translated. Every language file has the same key structure (validated). See `references/content-design-json.md` for the schema.

### ICU Message Format (use from the start)

Industry standard, supported by all major i18n libraries. Plurals are language-specific:

```
{count, plural, =0 {No items} one {# item} other {# items}}
```

Plural-form counts differ: **English 2, German 2, Polish 4, Arabic 6**. Use ICU from the first key declaration so plurals are correct per language — retrofitting plural logic after the fact is the failure mode. German example from `DESIGN-i18n.md`:

```json
"items_count": "{count, plural, =0 {Keine Einträge} one {# Eintrag} other {# Einträge}}"
```

Variable interpolation (`"Welcome back, {name}"`) is stack-agnostic at the strings layer; per-stack i18n integration handles render-time interpolation.

## The three translation patterns

### Pattern 1 (default, decision 40) — agent translates inline at phase 16

1. User picks languages at session-start or phase 11.
2. Agent generates source-language strings + page MD.
3. At phase 16, agent translates strings + prose into target languages.
4. User reviews + corrects per language.

Zero friction; multi-language site by phase 16 without external steps. "Good enough" for most muggle use cases (Swiss DE/EN/FR/IT, EU sites).

**Caveats the agent MUST surface at the translation step:**

- Idioms may not translate naturally.
- Brand-specific terms / proper nouns may need manual locking.
- Voice nuance (warm-direct vs warm-formal) may flatten.
- Commercial / legal / medical copy may need professional translation regardless.

### Pattern 2 (upgrade path) — translator handoff via brief

Recommended when translation quality materially affects business outcome — carefully-crafted brand voice, commercial sites in high-stakes markets, regulatory copy. The agent flags Pattern 2 as recommended when the site has any of: commercial transactions, legal/regulatory copy, distinctive brand voice, or explicit user translation-quality requirements.

1. Agent generates source-language strings + prose (same as Pattern 1).
2. Agent emits `briefs/translation-{lang}-{ts}.json` containing: source strings, source prose, voice guidelines, glossary of do-not-translate terms (brand names, technical terms), voice exemplars in the source language.
3. User sends briefs to a professional translator OR a high-quality tool (DeepL Pro, etc.).
4. Translator returns translated files.
5. User pastes back; phase 6.5 ingests into `strings/{lang}.json` + `content/pages/{slug}.{lang}.md`.

### Pattern 3 — user-driven external tool

Same brief as Pattern 2; the user drives translation with their own tool (their ChatGPT/Claude.ai/DeepL workflow). The agent doesn't endorse or evaluate the tool choice.

## Translation review is human-required for production

The agent does **not** declare translated copy final without the user (or a translator) reviewing it. This is a correctness prerequisite, not a preference. The decision-41 missing-key fallback (shows default-language string + logs warning) is a render-time safety net — not permission to ship a half-translated site. The phase-16 multilingual-completeness gate (every configured language's file has the same key structure AND every value translated, not a copy of the default) is **not overridable**.

## Writing for translatability (applied when writing source prose on multilingual sites)

Per current content-design practice (WebSearch 2026-05-18, [Content design in 2026 — UXCC](https://uxcontent.com/content-design-in-2026/)): effective localization is not translation alone — design patterns that adapt to linguistic/cultural differences. When writing source-language prose for a site that will be translated:

- Simple sentence structure; consistent terminology.
- Avoid idioms, wordplay, culturally-complex phrasing — they don't translate cleanly.
- Plan information hierarchy + UI flexibility for varying word lengths (German runs ~30% longer than English; this interacts with the phase-14 wireframe's space budget).
- Add clear intent notes where a phrase's meaning is non-obvious so the translator (Pattern 2) preserves intent, not just words.

This makes both Pattern 1 (inline) and Pattern 2 (handoff) smoother, and reduces the voice-flattening caveat.

## Validation (session-start hook + phase exit)

- All language files have the same key structure (no missing translations within the schema).
- All `{strings.x.y.z}` references in page MD resolve in **every** language file (or the configured fallback is in effect).
- All RTL languages have `dir="rtl"` on relevant pages (RTL = Arabic/Hebrew/Persian/Urdu; handled via CSS logical properties from phase 18 — not phase-16 territory but the strings + prose must exist).
- All `hreflang` tags resolve to existing pages (generated from `sitemap.yaml` + project languages; phase 26 verifies).

## Common failure modes (phase-16 multilingual)

| Failure | Recovery |
|---|---|
| "The German translation can wait until after launch" | Decision 39 = all configured-language pages exist at launch. Decision 41 fallback is a safety net, not a license. Recommend Pattern 2 for high-stakes copy. Not overridable. |
| Translator returns inconsistent voice | The Pattern 2 brief includes glossary + voice exemplars; review + flag inconsistencies on ingest (phase 6.5). |
| Plural forms break in non-English | ICU Message Format from the start; test edge cases (zero/one/two/many) per language. |
| Pattern 1 flattens voice in a high-stakes market | Surface the caveat proactively; recommend Pattern 2 before the user discovers the flattening post-launch. |

## References

- `Workstreams/website-builder/foundation/DESIGN-i18n.md` — full i18n design (routing, RTL, locale formatting, language switcher, hreflang, authoring-effort estimates).
- `Workstreams/website-builder/foundation/DESIGN-content-layers.md` § Layer 3/4.
- `references/content-design-json.md` — the strings schema this workflow translates.
- ICU Message Format: https://unicode-org.github.io/icu/userguide/format_parse/messages/
- hreflang spec: https://developers.google.com/search/docs/specialty/international/localized-versions
