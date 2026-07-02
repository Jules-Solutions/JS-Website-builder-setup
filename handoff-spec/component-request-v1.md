# Handoff spec — `component-request-v1`

> The v1 contract for the **agent → external tool** brief. The agent emits a JSON file at `.website-builder/briefs/{component}-{ts}.json` matching this schema; the user pastes it into ChatGPT / Claude.ai / v0 / Cursor / Lovable / Bolt — or hands it to a human freelancer. Per locked decisions 24 (the protocol is fundamental) + 35 (default is agent-writes-code; brief-emit is opt-in per component). **Stack-agnostic** — the same brief format works for any output stack via the `output_format` block.
>
> Canonical anchors:
> - `DESIGN-content-layers.md` Layer 5 ("Component briefs (JSON handoff protocol)") + the full request schema example
> - `DESIGN-ingestion-and-extraction.md` §"JSON handoff protocol (bidirectional)"
> - `skills/wb-component-build/references/json-handoff-protocol.md` §"Flow A — out"

## Version + schema identifier

```
$schema: spec/component-request-v1.json
$version: v1
```

This spec is **v1**. Breaking changes ship as `component-request-v2` with migration notes. Round-trips that emit v1 briefs are ingested by `component-output-v1` outputs.

The **machine-validatable JSON Schema** lives at [`spec/component-request-v1.json`](../spec/component-request-v1.json) (JSON Schema Draft 2020-12). This markdown doc is the human-readable block-by-block SSOT; the JSON Schema is the concrete realisation of it, and the two are kept in lock-step. A brief's `$schema: "spec/component-request-v1.json"` field points VS Code's JSON validation at the schema when the plugin is installed; the plugin's session-start hook validates briefs in `.website-builder/briefs/` against it. Round-trip + validity tests at `tests/handoff-protocol/`.

## Top-level shape

```json
{
  "$schema": "spec/component-request-v1.json",
  "$version": "v1",
  "type": "component-request",
  "id": "hero-block-2026-05-19T16-32-00Z",
  "created": "2026-05-19T16:32:00Z",
  "iteration": 0,
  "subject": { ... },
  "brand_context": { ... },
  "request": { ... },
  "output_format": { ... },
  "iteration_history": [],
  "instructions_for_external_tool": "..."
}
```

Required top-level keys: `$schema`, `$version`, `type`, `id`, `created`, `iteration`, `subject`, `brand_context`, `request`, `output_format`, `iteration_history`, `instructions_for_external_tool`.

`id` is the round-trip binding key — output files reference it back. Format: `{component-slug}-{iso-8601-ts}` (no colons in filenames; Z-suffixed UTC).

`iteration` is integer ≥0. Round 0 = first emission; round 1 = first re-attempt with `iteration_history` populated.

## Block 1 — `subject`

What's being generated.

```json
{
  "subject": {
    "kind": "component",
    "name": "HeroBlock",
    "purpose": "Top of home page; introduces project + drives subscribe CTA"
  }
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `kind` | enum | yes | `component` / `page` / `section` / `full-site`. Most briefs are `component`. |
| `name` | string | yes | PascalCase component name (or kebab-case page slug for `kind: page`). |
| `purpose` | string | yes | 1-2 sentences. Why this exists in the project. |

## Block 2 — `brand_context`

The brand the external tool must respect. Sourced from the user's project state at the point of brief emission. Layered:

```json
{
  "brand_context": {
    "voice": {
      "descriptors": ["warm", "direct", "contrarian"],
      "exemplars_say": ["We won't fight that; we make it work."],
      "exemplars_avoid": ["At Still Humans, we leverage synergies..."]
    },
    "color_palette": {
      "primary": "oklch(64% 0.18 30)",
      "neutral_900": "oklch(15% 0 0)",
      "neutral_50": "oklch(98% 0 0)",
      "semantic_error": "oklch(60% 0.20 25)"
    },
    "typography": {
      "display": "Fraunces, serif",
      "body": "Inter, sans-serif",
      "mono": "JetBrains Mono, monospace",
      "scale": {
        "h1": { "size": "64px", "lh": "1.0", "weight": 700 },
        "h2": { "size": "40px", "lh": "1.1", "weight": 600 },
        "body": { "size": "18px", "lh": "1.5", "weight": 400 }
      }
    },
    "spacing": {
      "base_unit": "4px",
      "scale": [0, 4, 8, 12, 16, 24, 32, 48, 64, 96]
    },
    "motion": {
      "duration_med": "300ms",
      "easing_default": "cubic-bezier(0.4, 0, 0.2, 1)",
      "preference": "subtle"
    },
    "dark_mode": "auto"
  }
}
```

| Field | Source | Notes |
|---|---|---|
| `voice` | Phase 5 (voice) outputs | `descriptors` + `exemplars_say` + `exemplars_avoid` |
| `color_palette` | `brand.yaml.tokens.colors` (Layer 1) | OKLCH always — perceptually uniform, predictable contrast |
| `typography` | `brand.yaml.tokens.typography` (Layer 1) | Display / body / mono + scale |
| `spacing` | `brand.yaml.tokens.spacing` (Layer 1) | Base unit + scale array |
| `motion` | `brand.yaml.tokens.motion` (Layer 1) | Duration + easing + preference (subtle / lively / none) |
| `dark_mode` | `brand.yaml.tokens.dark_mode` (Layer 1) | `auto` / `manual` / `none` |

The agent populates `brand_context` from `.website-builder/` at emission time. **Critical:** the external tool MUST use ONLY tokens from this block — that's enforced by `instructions_for_external_tool`. Drift detection happens at ingestion (palette validator).

## Block 3 — `request`

What's actually wanted. Sourced from `components.yaml` if the component exists; from a freshly-drafted spec if net-new at phase 18.

```json
{
  "request": {
    "props": {
      "headline": { "type": "string", "max_chars": 60, "required": true },
      "sub": { "type": "string", "max_chars": 120, "required": true },
      "cta_text": { "type": "string", "max_chars": 24, "required": true },
      "background_image": { "type": "image", "required": false }
    },
    "behavior": [
      "Headline + sub stack vertically; CTA below",
      "Background image (optional) covers full bleed; dark overlay for readability",
      "On hover, CTA gains 4px shadow + 2% scale"
    ],
    "responsive": {
      "mobile_360": { "headline_size": "32px", "layout": "stacked", "padding_inline": "16px" },
      "tablet_768": { "headline_size": "48px", "padding_inline": "32px" },
      "desktop_1280": { "headline_size": "64px", "padding_inline": "64px" }
    },
    "accessibility": {
      "heading_hierarchy": "headline = h1 (only on home), h2 elsewhere",
      "alt_text_required": "background_image",
      "contrast_ratio": "4.5:1 against headline color",
      "keyboard_nav": "CTA tabbable; focus ring visible"
    },
    "states": {
      "default": "as described",
      "loading": "skeleton outline for headline + sub",
      "hover": "CTA shadow + scale per behavior",
      "focus": "focus ring per design system phase 17"
    }
  }
}
```

| Field | Notes |
|---|---|
| `props` | Map of name → `{ type, max_chars, required, default? }`. `type` ∈ string / number / image / boolean / enum / array / object. |
| `behavior` | Bullet list of behavioral requirements. Plain prose. |
| `responsive` | Per phase-14 breakpoints. Object keys are `mobile_360` / `tablet_768` / `desktop_1280` (or whichever the project uses; sourced from `project.yaml.breakpoints`). |
| `accessibility` | Required: `heading_hierarchy` + `alt_text_required` (where images present) + `contrast_ratio` + `keyboard_nav`. Beyond that: per WCAG (phase 22 audit catches gaps). |
| `states` | Default / loading / hover / focus / error states as applicable. |

## Block 4 — `output_format`

What the external tool should produce. **This is the only block that varies by stack** — change this block to retarget the same brief to a different stack.

```json
{
  "output_format": {
    "framework": "react",
    "library": "shadcn",
    "style_system": "tailwind",
    "language": "tsx",
    "file_path_hint": "components/HeroBlock.tsx",
    "file_count_hint": 1
  }
}
```

| Field | Notes |
|---|---|
| `framework` | `react` / `vue` / `svelte` / `astro` / `solid` / `vanilla-js` / `php` (WP block / theme part) / `framer-custom-component` |
| `library` | `shadcn` / `radix` / `mantine` / `headless-ui` / `framer-stock` / `wp-gutenberg` / `none` |
| `style_system` | `tailwind` / `css-modules` / `vanilla-css` / `styled-components` / `emotion` / `framer-style` |
| `language` | `tsx` / `jsx` / `vue-sfc` / `svelte` / `astro` / `php` / `html-css-js` |
| `file_path_hint` | Suggestion only — external tools place files where they default; agent moves on ingest |
| `file_count_hint` | Integer — `1` for a single component; `>1` when multi-file output expected (e.g. Vue SFC + a `.css` file) |

**Stack adapter sources:** `adapters/stack-{name}.md#phase-18-component-build` (or equivalent section) provides the default `output_format` for that stack. Captains F/G/H populate these in Phase 3.

## Block 5 — `iteration_history`

Round-trip memory. Empty on round 0.

```json
{
  "iteration_history": [
    {
      "iteration": 0,
      "tool_used": "v0",
      "timestamp": "2026-05-19T16:35:00Z",
      "output_ingested_at": ".website-builder/outputs/HeroBlock-2026-05-19T16-35-00Z.tsx",
      "issues_found": [
        "Used indigo-500 instead of brand primary",
        "Missing alt on background_image",
        "Headline used <div> instead of <h1>"
      ]
    }
  ]
}
```

Each entry records: which iteration, which tool was used, when the output came back, where it was saved, what issues were caught by the palette validator + token-fidelity sweep. Round 1's `instructions_for_external_tool` references the issues so the next attempt addresses them.

## Block 6 — `instructions_for_external_tool`

Templated string. The agent generates this from the other blocks. Default template (Captains may extend per `output_format`):

```
You are generating a {request.kind} named {subject.name}.

Purpose: {subject.purpose}.

You MUST use ONLY the design tokens provided in brand_context — do not invent colors, fonts, or spacing values. The brand voice is {brand_context.voice.descriptors joined with ", "} (avoid: {brand_context.voice.exemplars_avoid examples}).

Framework: {output_format.framework} + {output_format.library} + {output_format.style_system}.

Return code only — no prose, no markdown fences, no explanations. Single file unless file_count_hint > 1, then output each file with a clear `// File: <path>` header.

{if iteration_history.length > 0}
This is iteration {iteration}. Previous attempt issues to address:
{iteration_history[last].issues_found bulleted}
{end}

Accessibility requirements:
- Heading hierarchy: {request.accessibility.heading_hierarchy}
- Alt text on: {request.accessibility.alt_text_required}
- Contrast ratio: {request.accessibility.contrast_ratio}
- Keyboard: {request.accessibility.keyboard_nav}

Component props (typed):
{request.props formatted as table}

Behavior:
{request.behavior bulleted}

Responsive:
{request.responsive formatted}

States to handle:
{request.states bulleted}
```

The user is free to edit the instructions before pasting into their tool — but the agent surfaces a warning if they remove the `MUST use ONLY` discipline clause (it's the load-bearing constraint).

## Stack-agnostic guarantee

A `component-request-v1` brief is **portable across stacks**. Re-target by editing only `output_format`:

```diff
- "framework": "react",
- "library": "shadcn",
- "style_system": "tailwind",
- "language": "tsx",
+ "framework": "vue",
+ "library": "daisy-ui",
+ "style_system": "tailwind",
+ "language": "vue-sfc",
```

`subject` + `brand_context` + `request` + `iteration_history` survive the migration. This makes the protocol the connective tissue across the Phase 3 stack adapters — same shape, three stacks, one contract.

## File naming + storage

Briefs land at:

```
.website-builder/briefs/{component-slug}-{iso-8601-ts}.json
```

Examples:

- `briefs/hero-block-2026-05-19T16-32-00Z.json`
- `briefs/pricing-table-2026-05-19T17-15-00Z.json`

Gitignored at the user's project level by default (briefs accumulate; they're round-trip artifacts, not source-of-truth). Decision logs in `.website-builder/decisions/ingest-{ts}.md` reference the brief id for full provenance.

## Validation

The session-start hook validates briefs in `.website-builder/briefs/`:

1. JSON parses.
2. `$schema` matches `spec/component-request-v1.json`.
3. Required top-level keys present.
4. `id` is well-formed (slug-isoformat).
5. `brand_context` references tokens that exist in `brand.yaml`.
6. `output_format.framework` matches `project.yaml.stack` (or surfaces an explicit cross-stack note).

Lint failures surface to the user with diagnostic + suggested fix.

## Adapter fixtures (per external tool)

Per-tool example briefs + tool-specific quirks live in [`handoff-spec/adapter-fixtures/`](adapter-fixtures/). Each fixture documents:

- How to paste the brief into that tool's interface
- Tool-specific quirks (ChatGPT output-cap truncation + fence-stripping, Claude.ai Artifacts panel, v0 React+shadcn defaults, Cursor file-comment, Lovable / Bolt.new whole-app scope-down)
- Expected output format
- How to capture the output for paste-back
- Known issues
- A sample brief + sample output pair

The **7 shipped fixtures** cover ChatGPT / Claude.ai / v0 / Cursor / Lovable / Bolt.new (the 6 AI tools) + human-freelancer:
[`chatgpt.md`](adapter-fixtures/chatgpt.md) · [`claude-ai.md`](adapter-fixtures/claude-ai.md) · [`v0.md`](adapter-fixtures/v0.md) · [`cursor.md`](adapter-fixtures/cursor.md) · [`lovable.md`](adapter-fixtures/lovable.md) · [`bolt-new.md`](adapter-fixtures/bolt-new.md) · [`human-freelancer.md`](adapter-fixtures/human-freelancer.md). Each fixture's sample brief validates against `spec/component-request-v1.json`; the AI-tool fixtures' sample output pairs drive the round-trip ingestion tests at `tests/handoff-protocol/`.

## See also

- `DESIGN-content-layers.md` Layer 5 — design-doc anchor (full example + rationale)
- `DESIGN-ingestion-and-extraction.md` §"JSON handoff protocol (bidirectional)" — design-doc anchor (out + in flows)
- `handoff-spec/component-output-v1.md` — the *return* contract (the shape the pasted-back output should follow)
- `skills/wb-component-build/references/json-handoff-protocol.md` — phase-18 operational doc (Flows A + B + per-tool quirks)
- `extraction/ai-output.md` — the parser that ingests `component-output-v1` outputs back into project state
- `adapters/stack-{name}.md#phase-18-component-build` — per-stack `output_format` defaults
