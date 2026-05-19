# Extraction — Google Stitch

> AI-driven extraction of a design system from any URL or screenshot into a portable open-spec DESIGN.md (color palette, type scale, spacing, component-shape recognition). **MVP-primary extraction tool per locked decision 55** of the website-builder workstream. **Stack-agnostic** — adapters consume the normalized output identically.
>
> Anchor: `Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md` §"Google Stitch (primary URL extractor)" (lines 126-162) + `phase-contracts/06.5-artifact-ingestion.md`.
> External: https://stitch.withgoogle.com

## What it does

Stitch takes one of:

- **A URL** to a deployed site → walks the visible design surface
- **A screenshot** → vibe-extracts design tokens + component shapes
- **A natural-language prompt** → generates a design system from voice cues

…and produces a portable, AI-readable spec containing:

- Brand identity (name + voice descriptors, inferred)
- Design tokens: color palette (oklch), type scale, spacing scale, motion, dark-mode
- Component shape recognition: hero, nav, card, grid, list, form, footer, etc.

The output format is Stitch's own `DESIGN.md` schema — see "Output schema" below.

## When the agent invokes it

Stitch is the **MVP-primary path for URL/site/screenshot extraction**. The agent reaches for Stitch in:

- **Entry mode `has-existing-site`** — user has a deployed site to migrate (most common phase-6.5 trigger at session start).
- **Entry mode `has-Framer-attempt`** — partial Framer/Webflow/Wix project; Stitch walks the deployed preview.
- **Entry mode `has-ai-output`** — when the AI output is provided as a URL (rare; typically pasted code instead → AI-output parser).
- **User explicit invocation** at any phase: *"extract the design system from https://example.com"*.
- **Phase 17 (design system)** — the agent can use Stitch to seed initial palette + typography options when the user provides reference URLs/screenshots.

Stitch is paired with **Playwright walker** when the target site has dynamic state (hover effects, mobile-emulation variants, auth-walled content) Stitch's static URL crawl misses. See `extraction/playwright-walk.md`.

## Two invocation paths (per phase-6.5 contract)

### Path 1 — Browser-in-loop (MVP default, no API)

Stitch has no native API or MCP at authoring date. The MVP flow:

1. Agent prompts user: *"Open https://stitch.withgoogle.com, paste your URL (or upload your screenshot, or describe the design), let Stitch generate the DESIGN.md export, then paste it back here."*
2. User pastes the DESIGN.md content back into the chat.
3. Agent saves to `.website-builder/outputs/stitch-{ts}.md` and normalizes per the schema below.

The user-in-loop is annoying but reliable; Stitch's web UI is the canonical surface and produces high-quality output.

### Path 2 — SDK / CLI / MCP (evolution path; not yet available)

When Stitch ships an API surface, the agent will invoke programmatically:

```bash
# Speculative — verify via context7 / WebFetch at phase 6.5 invocation
export STITCH_API_KEY=...   # pulled via secrets-conventions.md from 1Password
stitch generate --url https://example.com --output design.md
```

Or via MCP if a Stitch MCP server lands. The agent's phase-6.5 mechanism invokes context7 (`/google/stitch` if listed) at each invocation to confirm current surface — Stitch evolves; training data is stale.

When path 2 is available, the user-in-loop step disappears. Until then, path 1 is the contract.

## Output schema (Stitch DESIGN.md)

Stitch emits markdown with a predictable structure (verbatim from `DESIGN-ingestion-and-extraction.md`):

```markdown
# DESIGN.md
## Brand Identity
**Name:** [extracted]
**Voice:** [extracted/inferred]

## Design Tokens
### Colors
- primary: oklch(...)
- secondary: oklch(...)
- neutral_900: oklch(...)
- semantic_error: oklch(...)
- ...

### Typography
- display: [font-family]
- body: [font-family]
- scale:
  - h1: { size: ..., lh: ..., weight: ... }
  - h2: { ... }
  - body: { ... }

### Spacing
- base_unit: ...
- scale: [...]

### Motion
- duration_med: ...
- easing_default: ...

### Dark Mode
- strategy: auto | manual | none

## Components
### Hero
- [recognized props + behaviors]
### Nav
- [...]
### Card
- [...]
...
```

Agent normalizes into:

| Stitch section | website-builder destination |
|---|---|
| Brand Identity → Voice | `project.yaml.voice_descriptors` + `voice/exemplars.md` (Layer 5 seed) |
| Design Tokens → Colors | `brand.yaml.tokens.colors` (Layer 1) |
| Design Tokens → Typography | `brand.yaml.tokens.typography` (Layer 1) |
| Design Tokens → Spacing | `brand.yaml.tokens.spacing` (Layer 1) |
| Design Tokens → Motion | `brand.yaml.tokens.motion` (Layer 1) |
| Design Tokens → Dark Mode | `brand.yaml.tokens.dark_mode` (Layer 1) |
| Components → Hero / Nav / etc. | `components.yaml` (Layer 2) — one entry per recognized component |

The normalization is the agent's responsibility — Stitch produces semi-structured markdown; the agent maps it onto YAML. Conflict-resolution (incoming vs existing) follows the phase-6.5 protocol.

## Configuration

```yaml
# project.yaml
extraction:
  stitch:
    enabled: true
    api_key_env: STITCH_API_KEY   # path 2 only; ignored on path 1
    pair_with_playwright: auto    # auto | always | never
```

`pair_with_playwright: auto` triggers a Playwright walk when Stitch's URL crawl is suspected to miss dynamic state (heuristic: site has reported hover states, scroll-triggered animations, or auth wall).

## Failure modes

| Failure | Cause | Recovery |
|---|---|---|
| Stitch output incomplete (missing sections) | Site's design system is sparse / inconsistent | Agent flags gaps; falls back to manual phase-17 design-system option generation |
| Tokens don't match site reality (visible drift) | Stitch hallucinated values | Agent surfaces drift via screenshot comparison; user picks corrected values |
| Components mis-identified (e.g. "Card" labeled "Hero") | Vibe-detection error | Agent surfaces per-component review at phase 17 / 18 ingestion gate |
| Output unparseable (free-form prose instead of structured markdown) | Stitch produced wrong format | Agent asks user to re-run Stitch with the "DESIGN.md export" option explicitly |
| URL extraction fails entirely (Stitch returns nothing) | Site is JS-heavy SPA without server-rendered content | Switch to Playwright walker → screenshot → Stitch screenshot mode |
| Auth-walled site | Stitch can't reach private content | Use Playwright walker with user-supplied auth; capture screenshots; pass screenshots to Stitch |

## Quality discipline

- **Always pair Stitch output with user review** before applying — token conflicts halt per phase-6.5 protocol.
- **Cache the raw Stitch output** at `.website-builder/outputs/stitch-{ts}.md` so re-extractions are auditable.
- **Log the ingestion** in `.website-builder/decisions/ingest-{ts}.md` per phase-6.5 schema.
- **Re-fetch context7 / WebFetch** on `https://stitch.withgoogle.com` if cached docs are >30 days old (Stitch capabilities continue to evolve).

## See also

- `Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md` — full extraction model
- `phase-contracts/06.5-artifact-ingestion.md` — invocation contract + 8-step flow
- `extraction/divmagic.md` — element-precision peer for targeted extracts
- `extraction/playwright-walk.md` — paired walker for dynamic-state sites
- `extraction/ai-output.md` — code-based artifact ingestion (different path)
- `handoff-spec/component-output-v1.md` — JSON-handoff round-trip uses the AI-output parser, not Stitch
- https://stitch.withgoogle.com — official site
