# Extraction — AI-output parser

> The plugin's built-in HTML/JSX/Vue/Svelte parser for **entry mode `has-ai-output`** + the **phase-18 JSON-handoff round-trip**. Takes raw code (typically from ChatGPT / Claude.ai / v0 / Lovable / Cursor / Bolt / a human freelancer) and extracts design tokens + content/strings + component shapes + external dependencies. **Load-bearing in MVP** (per phase-6.5 contract). **Stack-agnostic** — output normalizes to the same `.website-builder/` layers regardless of input language.
>
> Anchor: `DESIGN-ingestion-and-extraction.md` §"AI-output parser" (lines 184-201).

## What it does

Takes one of:

- **HTML** (plain or with `<style>` blocks)
- **React JSX / TSX** (with or without Tailwind classes / shadcn imports / CSS-in-JS)
- **Vue SFC** (`.vue` single-file components)
- **Svelte component** (`.svelte` files)
- **Astro component** (`.astro` files)
- **Mixed snippets** — partial code from a one-shot AI tool

…and extracts:

- **Design tokens** from inline styles + CSS classes (recognized Tailwind utilities → token candidates; shadcn class patterns → component-library-aware token mapping; custom CSS → raw tokens with naming inference)
- **Content / strings** from text nodes — distinguishes page-prose (substantive, per-page) from reusable strings (button labels, error messages, microcopy)
- **Component shapes** from JSX / template structure — props, children pattern, conditional rendering, event handlers
- **External dependencies** from import statements — libraries used (`react`, `lucide-react`, `@radix-ui/*`, `next-intl`, etc.), framework signals

## When the agent invokes it

- **Entry mode `has-ai-output`** at session start — user pasted a one-shot ChatGPT/v0/Lovable landing page during phase-6 wild content capture. Phase 6.5 invokes the AI-output parser.
- **Phase 18 component-build round-trip** — agent emitted a `component-request-v1` brief (see `handoff-spec/component-request-v1.md`); user generated externally; user paste-backs the output; phase 6.5 fires; AI-output parser is the entry point.
- **User explicit invocation at any phase** — *"ingest this hero section from ChatGPT"* → user pastes the code → AI-output parser runs.
- **Human freelancer delivery** — mom's pattern. Freelancer delivers HTML / React component. User paste-backs to agent. AI-output parser is the same path.

## Invocation path

In-process. No external service. The agent uses its own reasoning + light AST parsing to extract structure.

The user provides input one of two ways:

1. **Paste directly into chat** — agent extracts inline.
2. **Save to file** in `.website-builder/outputs/{name}-{ts}.{ext}` — phase 6.5 trigger picks it up via the "detected file in outputs/" route.

For per-tool quirks (ChatGPT truncates long code; v0 emits React+Tailwind+shadcn by default; Cursor delivers in a file with file-comment annotations), see `handoff-spec/component-output-v1.md` "Per-tool adapter quirks" + `skills/wb-component-build/references/json-handoff-protocol.md`.

## Extraction targets

### 1. Design tokens

Tokens are recognized in three forms:

- **Inline styles** (`<div style="background-color: rgb(99, 91, 255); padding: 24px;">`) → token candidates: `colors.primary` (or matches existing token), `spacing.lg`
- **Tailwind classes** (`<div class="bg-indigo-500 p-6 text-white">`) → mapped to project tokens via Tailwind config (default Tailwind palette mapped to OKLCH equivalents); known shadcn class patterns recognized as component-library-aware
- **CSS-in-JS** (`styled-components`, `emotion`, `vanilla-extract`) → extracted via pattern matching on css template literals
- **CSS Modules** (imported `.module.css`) → file referenced + classes mapped

The agent normalizes to `brand.yaml.tokens.{colors,typography,spacing,motion}` with phase-6.5 conflict protocol on each.

### 2. Content / strings

Text nodes in HTML / JSX / etc. The parser distinguishes:

- **Page prose** — substantive paragraphs, headings, long-form copy → flagged for `content/pages/{slug}.md`
- **Reusable strings** — short button labels, error messages, microcopy → flagged for `content/strings/{lang}.json`

The split rule of thumb: prose ≥ 80 chars or ≥ 1 sentence + period → page. Short (< 80 chars, button-shaped) → strings. Agent asks the user on ambiguous cases.

Multi-language input: if the incoming artifact's text is not in `default_language`, agent flags + asks ("this looks like German prose — should it ingest as `de.json` strings + `pricing.de.md`?").

### 3. Component shapes

The parser walks the JSX / template structure:

- **Root component** → `components.yaml` entry (name inferred from filename, export name, or user prompt)
- **Props** → from React props destructuring, Vue `defineProps`, Svelte `export let`, etc.
- **Children / slots** → `components.yaml.children_slot` annotation
- **Conditional rendering** → `components.yaml.variants` candidates
- **Event handlers** → `components.yaml.behavior` notes (e.g. `onClick → CTA action`)
- **Responsive specs** → from Tailwind responsive variants (`sm:`, `md:`, `lg:`) or media queries

### 4. External dependencies

Imports are parsed:

- **Framework signals** — `from 'react'`, `defineComponent` from Vue, etc. → identifies stack hint (verify against `project.yaml.stack`)
- **Library imports** — `from 'lucide-react'` (icon lib), `from '@radix-ui/...'` (primitive lib), `from 'next-intl'` (i18n lib) → flags to surface at phase 18
- **Style imports** — `import './styles.css'` → flag to surface the .css alongside

The agent surfaces unrecognized dependencies + asks: "this code imports `xyz-ui` — do you have this library installed? should we add it to project dependencies, or rewrite without it?"

## Output: normalized state + decision log

The AI-output parser writes:

- Tokens → `brand.yaml.tokens` (with conflict resolution per phase-6.5)
- Strings → `content/strings/{lang}.json` (with conflict resolution)
- Page prose → `content/pages/{slug}.md` (with conflict resolution — page conflict patterns documented in `DESIGN-ingestion-and-extraction.md`)
- Component shape → `components.yaml` (with conflict resolution)
- Imports / deps → notes in `.website-builder/decisions/ingest-{ts}.md` "external_dependencies_detected"

Plus the raw input is preserved at `.website-builder/outputs/{name}-{ts}.{ext}` for audit.

## Edge cases (per design-doc lines 196-200)

- **Incomplete code** (broken JSX, missing imports, mid-function paste) → agent surfaces gaps + asks: *"this snippet looks incomplete; missing closing tag on line 14 + import for `Button` — should I infer or do you want to paste the full file?"*
- **Inline styles vs Tailwind vs CSS-in-JS in the same file** → agent extracts to tokens regardless of source; normalizes inconsistent units (`16px` vs `1rem` vs `text-base` → single token reference)
- **Unknown framework** → agent asks: *"this looks like neither React nor Vue — is it Solid? Qwik? Hand-written templating?"* — and either learns the framework via context7 or routes to the user for translation
- **Mixed-language code** (e.g. JSX with TypeScript generics + Tailwind + CSS Modules) → standard; parser handles all three
- **Image references** (`<img src="...">` or `<Image src=... />`) → URLs preserved; binary assets not extracted (user delivers separately or links externally — see `consumers/image-gen.md` for image-gen pairing)
- **Auth / API calls** in the snippet — flagged + asked: *"this component calls /api/checkout — that's commerce logic; is this transactional flow already configured (phase 24a-c)?"*

## Configuration

```yaml
# project.yaml
extraction:
  ai_output:
    enabled: true   # MVP default — load-bearing for has-ai-output entry mode
    prose_split_threshold_chars: 80   # below = string, above = page prose
    auto_detect_language: true        # detect incoming language, route to right strings file
    framework_detection_required: false  # warn instead of halt if framework unknown
```

## Failure modes

| Failure | Cause | Recovery |
|---|---|---|
| Output parses but tokens drift wildly from existing brand | User pasted code from a different brand entirely | Phase-6.5 token-conflict halt; user decides per-token |
| Component name collision (`HeroBlock` already exists) | Same name, different shape | Phase-6.5 component-conflict halt; user picks: rename, replace, merge |
| Prose-vs-string split incorrect | Threshold heuristic wrong | User overrides per text node; agent learns + adjusts session-local |
| Unknown framework | Code from Solid / Qwik / Marko / etc. | Agent invokes context7 for the framework; if not enough info, surfaces to user |
| Imports reference non-existent packages | Typo / hallucinated package from AI tool | Agent flags + asks; never silently `npm install` (per `tool-dependency-discipline.md` Tier 3) |
| Pasted code is screenshots / images of code | Not actually code | Agent surfaces: *"that looks like an image of code — re-paste as text"* |

## Quality discipline

- **Conflict protection is non-negotiable.** Every conflict halts per phase-6.5 protocol (locked decision 36). The AI-output parser is *not* allowed to silent-merge incoming tokens with existing.
- **Reference preservation:** raw input at `.website-builder/outputs/{name}-{ts}.{ext}` is the audit trail.
- **Ingest decision log** at `.website-builder/decisions/ingest-{ts}.md` per phase-6.5 schema (`extractor: ai-output-parser`).
- **Brand validation:** the agent cross-checks incoming tokens against `voice/exemplars.md` + design-skill flavor (phase 17 outputs); flags brand drift before applying.

## See also

- `DESIGN-ingestion-and-extraction.md` §"AI-output parser" — design-doc anchor
- `phase-contracts/06.5-artifact-ingestion.md` — invocation contract + 8-step flow
- `handoff-spec/component-request-v1.md` — the brief shape that drives the round-trip
- `handoff-spec/component-output-v1.md` — the ingestion contract the AI-output parser implements
- `skills/wb-component-build/references/json-handoff-protocol.md` — per-tool adapter quirks (ChatGPT / v0 / Cursor / Claude.ai / Lovable / human freelancer)
- `extraction/stitch.md` — peer for URL-based extraction (different path)
- `extraction/figma-design-to-json.md` — peer for Figma artifacts
