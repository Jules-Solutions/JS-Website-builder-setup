# Fixture — `has-Figma-file`

## What this fixture represents

A user has a Figma file (typically delivered by a designer or freelancer) and wants the website-builder to ingest the design system + page structure. Common scenario: a designer delivered a `.fig` export, or the user owns a Figma project and exported a static `.fig` file for offline reference.

Per locked decision 15 + `DESIGN-architecture.md` line 250:

> **`has-figma-file.md`** — user has a Figma file (often delivered by a designer). Figma design-to-json plugin extracts design tokens + structure; phase 6.5 ingests.

## Fixture contents

```
fixture/
└── still-humans.fig         # mock Figma file (zero-byte placeholder)
```

For v0.1 detection-only scope, an empty `.fig` file at project root suffices to trigger detection. Real Figma files are binary blobs; the fixture only needs the extension marker for the hook to recognize the entry mode.

Phase 3+ adapter work will need real Figma files (or exported JSON from the Figma design-to-json plugin per `extraction/DESIGN-extraction-figma-design-to-json.md`) for end-to-end ingestion testing — that's deferred per `BUILD-strategy.md` test order (Phase 7-8 cosplay/Ralph tests).

## Expected behavior

1. SessionStart hook (Captain C) detects `.fig` file at project root.
2. Hook reports `entry_mode: has-Figma-file`.
3. `wb-bootstrap` skill (Captain D) initializes `.website-builder/` with `project.yaml` having `entry_mode: has-Figma-file`.
4. Agent surfaces "I see a Figma file — please open it in Figma, run the design-to-json plugin (https://www.figma.com/community/plugin/1514601930647701205/design-to-json), and paste the JSON output to me. I'll run phase 6.5 to extract tokens." via AskUserQuestion.
5. On confirm + JSON paste, agent routes to phase 6.5 with the Figma extractor.

(Note: Figma extraction is currently user-in-the-loop — the design-to-json plugin runs inside Figma; the agent ingests its JSON output. Future: if a Figma API path becomes available, the agent calls it directly. See `DESIGN-ingestion-and-extraction.md` §"Figma design-to-json plugin".)

## Detection signals (for the hook)

Per `DESIGN-ingestion-and-extraction.md` line 50:

**Strong signals (any one triggers `has-Figma-file`):**
- `*.fig` file at project root (Figma binary export)
- `figma-design-to-json-output.json` (or similar) at project root — pre-extracted plugin output
- A `figma/` directory with `tokens.json` + `frames/` (Figma plugin's exported structure)

This fixture exercises the bare `.fig` file detection path.

## Distinguishing edge cases

- A `.fig` file inside a Next.js / Astro / Framer project: ambiguous; framework wins (`has-existing-site` or `has-Framer-attempt`).
- A `.fig` file with no other content: `has-Figma-file`.
- Multiple `.fig` files at project root: `has-Figma-file` with `multiple_figma_files: true`; bootstrap asks user which to ingest.

See `expected.yaml` for the asserted output shape.
