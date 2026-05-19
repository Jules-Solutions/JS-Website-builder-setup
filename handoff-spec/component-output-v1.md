# Handoff spec — `component-output-v1`

> The v1 contract for the **external tool → agent** return — what shape the pasted-back output should follow for the agent's phase-6.5 ingestion (via the AI-output parser) to process it cleanly. Companion to `handoff-spec/component-request-v1.md`. Per locked decisions 24 + 35 + 36 (halt-and-force-decision on conflict). **Stack-agnostic** — the return format adapts to whatever the external tool produces in the requested framework.
>
> Canonical anchors:
> - `Workstreams/website-builder/foundation/DESIGN-content-layers.md` Layer 5 ("Layer 5's outputs ingest into Layers 2 + 4")
> - `Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md` §"JSON handoff protocol (bidirectional)" → "In: external tool output ingest"
> - `skills/wb-component-build/references/json-handoff-protocol.md` §"Flow B — in"
> - `extraction/ai-output.md` — the parser this contract drives

## Version + schema identifier

```
$schema: spec/component-output-v1.json
$version: v1
```

Outputs are paired 1:1 with `component-request-v1` briefs by the round-trip `id`. v2 of the output spec ships when v2 of the request spec ships.

## What the output is

The output is **code in the requested framework**, plus a thin metadata wrapper. Three legitimate forms:

1. **Pure code** — raw `.tsx` / `.vue` / `.svelte` / `.astro` / `.php` / `.html` file body. Most common from coding-focused tools (v0, Cursor, Bolt).
2. **Code + metadata header** — code preceded by a JSON-formatted metadata header (binds output to brief).
3. **Multi-file output** — when `file_count_hint > 1`, output contains multiple `// File: <path>` markers.

The agent's AI-output parser handles all three forms.

## Form 1 — Pure code (most common)

Some tools just dump the code. No metadata.

```tsx
import { Button } from "@/components/ui/button"

export function HeroBlock({ headline, sub, cta_text, background_image }: HeroBlockProps) {
  return (
    <section className="relative min-h-screen flex items-center justify-center px-4 lg:px-16">
      {background_image && (
        <img src={background_image} alt="" className="absolute inset-0 w-full h-full object-cover -z-10" />
      )}
      <div className="max-w-4xl text-center">
        <h1 className="text-5xl md:text-7xl font-display font-bold leading-tight">
          {headline}
        </h1>
        <p className="mt-6 text-lg md:text-xl">{sub}</p>
        <Button className="mt-8" size="lg">{cta_text}</Button>
      </div>
    </section>
  )
}

type HeroBlockProps = {
  headline: string
  sub: string
  cta_text: string
  background_image?: string
}
```

User paste-backs into chat OR saves to `.website-builder/outputs/{component}-{ts}.{ext}`. **Filename binding is critical** — the agent matches `{component}` to the brief `id` to look up the round-trip context. If the filename doesn't bind (user named the file something else), the agent asks the user: *"which brief does this output correspond to?"*

Recommended filename pattern matches the brief `id`:

```
.website-builder/outputs/hero-block-2026-05-19T16-35-00Z.tsx
```

## Form 2 — Code + metadata header

Tools that respect the round-trip protocol prepend a JSON metadata header:

```tsx
/*
{
  "$schema": "spec/component-output-v1.json",
  "$version": "v1",
  "type": "component-output",
  "brief_id": "hero-block-2026-05-19T16-32-00Z",
  "tool_used": "v0",
  "timestamp": "2026-05-19T16:35:00Z",
  "files": [
    { "path": "components/HeroBlock.tsx", "content_below": true }
  ],
  "self_assessment": {
    "addressed_iteration_issues": true,
    "deviations_from_brief": []
  }
}
*/

import { Button } from "@/components/ui/button"
// ... rest of component code
```

Required metadata keys:

| Field | Notes |
|---|---|
| `$schema` | Always `spec/component-output-v1.json` |
| `$version` | Always `v1` |
| `type` | Always `component-output` |
| `brief_id` | Must match a brief in `.website-builder/briefs/` |
| `tool_used` | Free-form string (e.g. `v0`, `chatgpt-4`, `claude-3.7-sonnet`, `human-freelancer-{name}`) |
| `timestamp` | ISO 8601 UTC |
| `files` | Array of `{ path, content_below }` for multi-file output |
| `self_assessment` | Tool's claim about quality (informational; agent verifies regardless) |

Most external tools don't emit this metadata natively. The brief's `instructions_for_external_tool` can request it but tools often ignore. The agent falls back to Form 1 when metadata is absent.

## Form 3 — Multi-file output

When `file_count_hint > 1` in the brief, output may contain multiple files. Format:

```
// File: components/HeroBlock.tsx
import { Button } from "@/components/ui/button"
// ... component code

// File: components/HeroBlock.module.css
.hero {
  /* ... */
}

// File: components/types.ts
export type HeroBlockProps = { /* ... */ }
```

Agent parser identifies `// File: <path>` markers (or `/* File: <path> */` block comments) and splits.

For frameworks where multi-file is natural (Vue SFC bundles `<template>`, `<script>`, `<style>` into one file; Svelte similar), Form 1 is preferred.

## What the parser does with the output (Flow B inputs)

Per `skills/wb-component-build/references/json-handoff-protocol.md` §"Flow B" + `extraction/ai-output.md`:

1. **Identify modality** — pure code / metadata-headed / multi-file.
2. **Bind to brief** — match by filename (or metadata `brief_id`, or user clarification).
3. **Extract design tokens** — recognize colors / typography / spacing / motion used. Cross-check against `brand.yaml`.
4. **Palette validator** — flag any value that's NOT in the brand palette ("uses `indigo-500` but no brand token matches — drift").
5. **Extract content / strings** — text nodes → either `content/strings/{lang}.json` or inline (per phase-18 component-build discipline).
6. **Extract component shape** — confirm props match brief's `request.props`. Surface deviations.
7. **Write code** to user's project per `output_format.file_path_hint` (or user-confirmed location).
8. **Update `components.yaml`** entry with the new/revised shape.
9. **Append to brief's `iteration_history`** — record this round, issues found, next-iteration seed.
10. **Conflict resolution** — every conflict halts per locked decision 36 (palette drift, prop deviation, file-collision, etc.). No silent merge.

## Self-assessment + iteration loop

If the metadata includes `self_assessment.addressed_iteration_issues: true`, the agent verifies — re-runs the palette validator + checks that the previous round's `issues_found` are absent in the new output. Discrepancy surfaces to user: *"v0 claimed it addressed the indigo drift; still uses indigo-500. Want me to flag this for round 2 or accept?"*

If the metadata includes `deviations_from_brief`, the agent surfaces each deviation for user decision rather than silent-accepting.

## Token-fidelity discipline (post-ingest)

Per `json-handoff-protocol.md` line 38: even after ingestion, the ingested component passes through the **same token-fidelity self-review sweep** as agent-written code. External-tool output frequently:

- Uses the tool's default palette (indigo/slate from v0; gray/blue from ChatGPT) instead of brand tokens
- Hardcodes spacing values (`p-6`) instead of using the project's spacing scale
- Uses platform-default fonts instead of brand display + body
- Misses accessibility (missing alt, wrong heading level)

The sweep catches these. Issues caught get added to the brief's `iteration_history.issues_found` for the next round.

## File naming + storage

Outputs land at:

```
.website-builder/outputs/{brief-id-or-component-slug}-{iso-8601-ts}.{ext}
```

Recommended (and what the brief's `instructions_for_external_tool` requests):

```
.website-builder/outputs/hero-block-2026-05-19T16-35-00Z.tsx
.website-builder/outputs/hero-block-2026-05-19T17-10-00Z.tsx   # iteration 2
```

Gitignored at user's project level by default. Decision log in `.website-builder/decisions/ingest-{ts}.md` records the ingestion event including which brief id paired with which output file.

## Validation (during phase-6.5 ingestion)

The agent's AI-output parser validates:

1. Output file parses (valid for its `output_format.language`).
2. If metadata present: matches `spec/component-output-v1.json` shape.
3. `brief_id` (if present) resolves to a brief in `.website-builder/briefs/`.
4. Code structure matches brief's `request.props` (warning, not block — external tools often miss).
5. Palette validator runs — any non-brand-token color or spacing value flagged.
6. Accessibility audit runs — alt, heading hierarchy, contrast, keyboard nav.

Each violation surfaces per locked decision 36 (halt + force user decision).

## Failure modes (handle, don't paper over)

Per `json-handoff-protocol.md` lines 57-63:

| Failure | Cause | Recovery |
|---|---|---|
| External tool truncates the brief | ChatGPT > ~8k tokens limit | Agent emits a trimmed brief (drop `iteration_history`, subset `brand_context`); warn user |
| Output doesn't match brief | Tool went off-spec | Phase-6.5 surfaces mismatch per locked decision 36; user picks: keep / re-iterate / discard |
| External tool ignores brand tokens | Tool defaults override the brief's discipline | Palette validator flags; `iteration_history.issues_found` carries it to round 2 with explicit fix prompt |
| Two outputs reference same brief id | User pasted twice / saved two attempts | Surface: "two outputs for this brief — which do you want me to ingest?" |
| Brief id missing from output filename + no metadata | User saved with arbitrary name | Surface: "which brief does this correspond to?" — user picks |
| Output is in wrong framework | Tool ignored `output_format` | Surface deviation; offer to translate (if stack-adjacent: React→Vue) or re-iterate |
| Output is screenshots / images, not code | User pasted from a wrong source | Reject; ask for code |
| Imports reference non-existent packages | Tool hallucinated dep | Per `tool-dependency-discipline.md` Tier 3: agent never silent-installs; verifies legitimacy + asks user |
| Brand drift (specific) — hardcoded hex / rgb instead of OKLCH tokens | Tool default behavior | Palette validator flags every offending value; round 2 brief includes the specific fix |
| Multi-file output garbled (file markers wrong) | Tool inconsistent | Agent identifies what it can; surfaces remaining ambiguous chunks for user to split manually |

## Cross-stack portability (the round-trip's bonus)

Because the brief is stack-agnostic except for `output_format`, the round-trip naturally supports retargeting:

1. User emits a React+shadcn+Tailwind brief, runs it through v0.
2. Later, user decides to migrate to Vue. Same brief, swap `output_format.framework: vue`, `library: daisy-ui`, `language: vue-sfc`.
3. Re-run through any tool. Output ingests via the same `component-output-v1` contract.
4. Component-shape contract (`request.props`, `behavior`, `accessibility`) carries over identically.

This is the connective-tissue property the Phase 3 stack adapters all build against: **the protocol bridges them**, no per-stack output-shape divergence.

## See also

- `Workstreams/website-builder/foundation/DESIGN-content-layers.md` Layer 5 — design-doc anchor for the layer-5 protocol
- `Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md` §"JSON handoff protocol" → "In: external tool output ingest" — design-doc anchor
- `handoff-spec/component-request-v1.md` — the *out* counterpart
- `skills/wb-component-build/references/json-handoff-protocol.md` — phase-18 operational doc
- `extraction/ai-output.md` — the parser that processes `component-output-v1` outputs (load-bearing in MVP)
- `phase-contracts/06.5-artifact-ingestion.md` — the ingestion contract
- `adapters/stack-{name}.md#phase-18-component-build` — per-stack output expectations
