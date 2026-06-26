# Entry mode: has-figma-file

> The user has a Figma file — typically delivered by a designer or freelancer. The file may be a full design spec (all pages, all states, all tokens), a partial comp (hero only, homepage only), or a brand kit (tokens + component library, no page layouts). The agent ingests whatever is there and continues from that design foundation.

## Who this is for

- Someone who hired a designer on Toptal or Upwork and received a Figma file delivery
- Someone who got a Figma handoff from an agency and now needs the file turned into running code
- Someone whose company has a Figma brand kit and wants to use it as the design foundation without starting from scratch

The Figma file is the highest-fidelity input the agent can receive — it contains explicit design decisions, not inferred ones. The ingestion goal is to extract those decisions faithfully and route them into the correct state files.

## Onboarding flow

At session start:

1. The agent sets `project.yaml.entry_mode = "has-figma-file"`.
2. The user provides the Figma file — either:
   - **Via URL:** The user shares the Figma link and runs the design-to-json plugin themselves
   - **Via exported JSON:** The user runs the [design-to-json Figma plugin](https://www.figma.com/community/plugin/1514601930647701205/design-to-json) and pastes the output
3. The agent confirms what the file contains: full spec / partial comp / brand kit only.

Phase 6.5 fires immediately to ingest the Figma output before phase 1.

## Phase 6.5 ingestion strategy

### Primary extractor: Figma design-to-json plugin

**No API access required.** The user runs the design-to-json plugin in Figma (it takes 30-60 seconds for a typical 5-page file), copies the JSON output, and pastes it to the agent. The agent reads the JSON directly.

The JSON contains:
- **Design variables / styles:** Named color, typography, and spacing variables → seeds `brand.yaml.tokens` with named variables rather than inferred values (highest fidelity token extraction available)
- **Component definitions:** Figma components → seeds `components.yaml` with prop structures drawn from component variants
- **Frame layouts:** Page frames → seeds `sitemap.yaml.pages` and `content/pages/*.md` (section sequence + text content)
- **Text content:** All text layers → seeds `content/pages/*.md` and `content/strings/{lang}.json`
- **Layer / variant naming:** Component variant names ("Button/Primary/Large", "Hero/Dark/WithVideo") → normalized into the project component naming convention

### Secondary: Playwright (when Figma URL is publicly viewable)

If the Figma file is publicly shared (view link), the agent can Playwright-walk the viewer to capture page thumbnails for visual reference during the phase 2 vision conversation. This is supplemental — the JSON is the canonical extraction source.

### What always gets extracted

- Named design variables (colors, type, spacing) → `brand.yaml.tokens` (high confidence — named by the designer)
- Component library → `components.yaml` (draft — prop structures confirmed at phase 18)
- Page structure → `sitemap.yaml` and `content/pages/*.md` (draft)
- Text content → `content/strings/{lang}.json` (draft)
- Asset inventory → `media/` reference list (agent notes which images exist in Figma; sourcing is phase 8's job)

### What the agent flags for resolution

Figma files often contain:
- **Duplicate components** (e.g., `ButtonV1` and `ButtonV2` from design iteration) → agent asks which to canonicalize
- **Lorem ipsum text** → flagged as placeholder; flagged for phase 16 copywriting
- **Missing mobile frames** → noted; phase 14 and 20 will surface this for resolution
- **Desktop-only token values** (e.g., font sizes not on a fluid scale) → flagged at phase 17

### Conflict detection

If the user has additional context (a brand guidelines PDF, prior AI output, or a live site), the agent compares the Figma design against those inputs and surfaces divergences. The Figma file is treated as the higher-fidelity source for design decisions; conflicts from lower-fidelity sources (AI output, inferred CSS) resolve toward the Figma spec.

### Output files seeded

| Extracted artifact | Destination |
|---|---|
| Named color / type / spacing variables | `brand.yaml.tokens` (high confidence draft) |
| Component definitions | `components.yaml` (draft) |
| Page frames → section list | `sitemap.yaml.pages` (draft) |
| Text content | `content/pages/*.md` + `content/strings/{lang}.json` (draft) |
| Asset inventory | noted in `media/` reference |

## Resume point after ingestion

The Figma mode compresses the pipeline significantly. Phases 2 (vision) and 5 (brand voice) still run in full conversation mode — the Figma file shows what the designer decided, but the user must confirm the visual direction is correct and articulate the brand voice. Phases 17 (design system) and 18 (component build) start from the extracted token and component baseline rather than from scratch.

If the Figma file is a complete spec (all pages, all states), the user can move quickly through phases 2-16 by confirming rather than creating. The agent surfaces each Figma-derived decision with "Is this right?" rather than asking from scratch.
