# Fixture — `has-AI-output`

## What this fixture represents

A user has generated a one-shot landing page using ChatGPT / Claude.ai / v0 / Lovable / Bolt.new / Cursor. They have a single self-contained `.html` file (often with embedded `<style>` + `<script>` and Tailwind-class-laden markup, or React-flavored output saved as HTML). They want the website-builder to ingest it as the starting point for their project.

Per locked decision 15 + `DESIGN-architecture.md` line 248:

> **`has-ai-output.md`** — user has a one-shot landing page from ChatGPT / Claude.ai / v0 / Lovable / etc. Phase 6.5 ingests the artifact (HTML / React / Vue), extracts tokens + content + structure, integrates.

## Fixture contents

```
fixture/
└── landing.html       # single self-contained AI-output file with React-flavored / Tailwind-laden markup
```

The fixture is a single HTML file with hallmarks of an AI-generated landing page:
- Tailwind utility classes (recognized by the AI-output extractor per `extraction/ai-output.md`)
- Inline `<style>` block with custom CSS variables
- Inline `<script>` for interactive bits
- React-style component structure (semantic-ish `<section>` blocks with class-based styling)
- One file, no `package.json`, no build config

## Expected behavior

1. SessionStart hook (Captain C) detects single `.html` file with AI-output signature: no build configs, no `package.json` referencing a framework, but recognizable Tailwind / React-component / inline-style patterns.
2. Hook reports `entry_mode: has-AI-output`.
3. `wb-bootstrap` skill (Captain D) initializes `.website-builder/` with `project.yaml` having `entry_mode: has-AI-output`.
4. Agent surfaces "I see a single HTML artifact with AI-tool output signature — should I run phase 6.5 to extract tokens + content?" via AskUserQuestion.
5. On confirm, agent routes to phase 6.5 with `extraction/ai-output.md` parser.

## Detection signals (for the hook)

Per `DESIGN-ingestion-and-extraction.md` §"AI-output parser":

**AI-output detection (must match enough of these):**
- Exactly one `.html` / `.htm` file at project root (or in a top-level subdir)
- File contains Tailwind utility-class patterns (`class="flex items-center gap-4 ..."` densely; ≥10 distinct utility classes)
- OR file contains React/JSX-like structures saved as HTML (`<div className="...` — note `className` not `class`)
- OR file contains inline `<style>` with CSS custom properties + a single page section structure
- No `package.json` referencing a framework (eliminates `has-existing-site`)
- No `.framer/` directory (eliminates `has-Framer-attempt`)
- No `.fig` files (eliminates `has-Figma-file`)

This fixture's `landing.html` is intentionally Tailwind-heavy to trigger the strongest signal.

## Distinguishing edge cases

- A static-html site with multiple linked HTML pages + separate CSS / JS files = `has-existing-site` (multi-file structured site).
- A single HTML file with NO Tailwind / NO inline styles (just plain prose) = ambiguous; bootstrap asks user.
- An HTML file embedded inside a Next.js / Astro / etc. project = `has-existing-site` (framework wins).

See `expected.yaml` for the asserted output shape.
