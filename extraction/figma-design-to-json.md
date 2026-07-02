# Extraction — Figma design-to-json plugin

> Figma plugin that exports a Figma file as structured JSON. **Expansion path beyond MVP** (per locked decision 55). Used in entry mode `has-figma-file` — the common scenario where a designer or freelancer hands the muggle a Figma file and the muggle wants a site that matches.
>
> Anchor: `DESIGN-ingestion-and-extraction.md` §"Figma design-to-json plugin" (lines 174-182).
> External: https://www.figma.com/community/plugin/1514601930647701205/design-to-json

## What it does

A user-in-loop extraction path. The user opens their Figma file, runs the `design-to-json` plugin, gets a structured JSON output, pastes the JSON to the agent. The agent normalizes the JSON into project state — design tokens to `brand.yaml`, component shapes to `components.yaml`, page-level structure to `sitemap.yaml` + `content/pages/`.

The plugin extracts:

- **Frames** — Figma's top-level layout containers (often correspond to pages or major sections)
- **Components** — reusable design elements with variants (correspond to `components.yaml` entries)
- **Styles** — color styles, text styles, effect styles (correspond to `brand.yaml.tokens`)
- **Fills, strokes, effects** — per-element styling data
- **Layout properties** — auto-layout, constraints, dimensions

## When the agent invokes it

Specifically for **entry mode `has-figma-file`**:

- Designer-delivered Figma file: muggle has hired a designer, has a `.fig` file, wants their site to match the design.
- Self-designed Figma file: muggle has prototyped their own design in Figma and wants the site implemented.
- Designer-handoff scenario: freelance designer delivers a Figma file as the artifact for implementation.

Less commonly:

- User invokes Figma extraction explicitly at any phase: *"I designed this hero section in Figma; ingest it."*

**MVP runtime support:** the v1 plugin documents the Figma flow but doesn't ship a Figma-API-direct path. The user runs the community plugin, pastes the JSON output. Future expansion: direct Figma API integration via MCP when one ships, or via Figma's REST API with personal access token.

## Invocation path (user-in-loop)

No automation in MVP. The agent prompts the user:

1. *"Open your Figma file."*
2. *"Run the 'design-to-json' plugin from the Figma Community."* (Link: https://www.figma.com/community/plugin/1514601930647701205/design-to-json)
3. *"Configure the plugin's export options if needed (the default 'export all frames + components + styles' is fine for most cases)."*
4. *"Copy the JSON output."*
5. *"Paste it here."*

Agent saves the pasted JSON to `.website-builder/outputs/figma-{ts}.json` and processes per the output schema.

**Alternative path:** if the user exports the JSON from the plugin to a file, they can put it in `.website-builder/inbox/` and the agent picks it up via the phase-6.5 trigger ("detected file in outputs/").

## Output schema (Figma plugin's JSON)

The community plugin emits a tree-shaped JSON. The full schema is plugin-versioned (verify via the plugin's docs at invocation time); the load-bearing structure is approximately:

```json
{
  "file_name": "...",
  "exported_at": "...",
  "styles": {
    "colors": [
      { "name": "Primary/500", "value": "rgba(99, 91, 255, 1)", "key": "..." },
      { "name": "Neutral/900", "value": "rgba(15, 15, 20, 1)", "key": "..." }
    ],
    "text": [
      { "name": "Display/H1", "font_family": "Inter", "font_size": 64, "line_height": 70, "font_weight": 700 }
    ],
    "effects": [ /* shadows, blurs */ ]
  },
  "components": [
    {
      "name": "HeroBlock",
      "id": "...",
      "variants": [ /* variant specs */ ],
      "props": [ /* documented props if author used Figma Variables */ ],
      "children": [ /* nested element tree */ ]
    }
  ],
  "frames": [
    {
      "name": "Home / Desktop",
      "id": "...",
      "width": 1440,
      "height": 4200,
      "children": [ /* sections, components */ ]
    }
  ]
}
```

(Verify exact structure by running the plugin once per session — schema evolves.)

## Normalization to website-builder state

| Figma plugin output | website-builder destination |
|---|---|
| `styles.colors` | `brand.yaml.tokens.colors` (convert rgba → oklch where possible — agent uses CSS color spec or library to translate) |
| `styles.text` | `brand.yaml.tokens.typography.scale` (one entry per text style — `Display/H1` → `tokens.typography.scale.h1`) |
| `styles.effects` | `brand.yaml.tokens.shadow` + `brand.yaml.tokens.motion` |
| `components` (top-level) | `components.yaml` entries (one per top-level Figma component) |
| `components.children` | Nested element tree → component composition |
| `frames` (top-level) | Candidate `sitemap.yaml` pages (Home / Desktop, About / Desktop, etc.) |
| `frames.children` | Section composition for pages (folds into `content/sections.yaml`) |

**Critical normalization gotchas:**

- **Figma's rgba → CSS oklch:** the agent uses a color-space conversion library (or Anthropic's reasoning) to map. Lossy in edge cases — verify per palette.
- **Component variants:** Figma Variables (if author used them) become props in `components.yaml`. Without Variables, the agent infers props from visible variants (e.g. "primary / secondary / tertiary" buttons → `variant: enum`).
- **Frame ≠ page** always: some frames are mobile/tablet variants of the same page (auto-layout responsive). Agent asks the user to confirm page-vs-variant mapping.
- **Auto-layout properties:** Figma's auto-layout (Flex/Grid analogs) maps to responsive specs in `components.yaml.responsive`. Direct translation when possible.

## Configuration

```yaml
# project.yaml
extraction:
  figma_design_to_json:
    enabled: true
    plugin_url: https://www.figma.com/community/plugin/1514601930647701205/design-to-json
    pair_with_screenshot: true   # ask user to paste screenshots of frames alongside JSON for visual reference
```

## Failure modes

| Failure | Cause | Recovery |
|---|---|---|
| JSON unparseable | User pasted truncated output | Ask for full output; large Figma files may exceed clipboard limits — user exports to file in `.website-builder/inbox/` instead |
| Missing styles section | Author didn't use Figma Styles (used local colors) | Agent extracts colors from element-level fills; flags drift; recommends author refactor to Figma Styles for future iterations |
| Components mis-identified | Author used "Components" loosely — Figma Components vs Frames | Agent surfaces all top-level frames + lets user mark which are components vs pages |
| rgba → oklch conversion drift | Color-space conversion lossy | Surface diff: original rgba vs converted oklch; user confirms |
| Multiple frame variants overlap | Mobile/tablet/desktop frames of same page | Agent groups by name pattern (`Home / Desktop`, `Home / Mobile`) → single sitemap entry with responsive specs |
| Figma Variables present (newer files) | Plugin may or may not extract Variables depending on version | Verify per plugin version; if missing, surface as gap; user can manually map Variables to tokens |

## Quality discipline

- **Pair JSON ingest with screenshots** when possible — visual reference catches mis-mapping (a "Hero" component that visually doesn't match its JSON props).
- **Cache the raw JSON** at `.website-builder/outputs/figma-{ts}.json` for audit.
- **Log invocations** in `.website-builder/decisions/ingest-{ts}.md` per phase-6.5 schema (`extractor: figma-design-to-json`).
- **Re-verify plugin URL + capabilities** at phase 6.5 via WebFetch — Figma community plugins evolve.

## See also

- `DESIGN-ingestion-and-extraction.md` §"Figma design-to-json plugin" — design-doc anchor
- `phase-contracts/06.5-artifact-ingestion.md` — invocation contract
- `extraction/stitch.md` — peer for non-Figma extraction (URLs, screenshots)
- `extraction/ai-output.md` — peer for code-based artifacts
- https://www.figma.com/community/plugin/1514601930647701205/design-to-json — plugin home
