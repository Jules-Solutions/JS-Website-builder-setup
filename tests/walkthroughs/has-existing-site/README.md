# Fixture — `has-existing-site`

## What this fixture represents

A user already has a deployed website (any platform) — in this fixture's case a Next.js project with `app/` router. They want the website-builder to ingest the existing site so they can iterate on it with the agent's discipline.

Per locked decision 15 + `DESIGN-architecture.md` line 247:

> **`has-existing-site.md`** — user has a deployed website (any platform). Phase 6.5 walks the live site via Playwright + uses Stitch / divmagic to extract design tokens; backfills state; routes to remaining phases.

## Fixture contents

```
fixture/
├── package.json          # references Next.js — primary detection signal
├── next.config.js        # Next.js stack-config marker
├── app/
│   ├── layout.tsx        # App Router signal
│   └── page.tsx          # home page
└── public/
    └── .gitkeep
```

This is a minimal Next.js skeleton — the smallest set of files that unambiguously signals "this is a deployed (or deployable) Next.js site." Real Next.js projects have many more files (`tsconfig.json`, `tailwind.config.js`, `node_modules/`, etc.); detection only needs the markers.

## Expected behavior

1. SessionStart hook (Captain C) detects existing-site signals: `next.config.js` + `package.json` referencing `next` + `app/` (or `pages/`) directory with content.
2. Hook reports `entry_mode: has-existing-site`.
3. `wb-bootstrap` skill (Captain D) initializes `.website-builder/` with `project.yaml` having `entry_mode: has-existing-site`.
4. Agent surfaces "I see this is an existing Next.js project — should I run phase 6.5 to ingest the existing design system + content?" via AskUserQuestion.
5. On confirm, agent routes to phase 6.5 (artifact ingestion) before resuming the main pipeline.

## Detection signals (for the hook)

Per `DESIGN-ingestion-and-extraction.md` §"Phase 6.5 mechanism" + `DESIGN-architecture.md` Entry modes section:

**Strong signals (any one triggers `has-existing-site`):**
- `next.config.{js,ts,mjs}` present + `package.json` references `next` in `dependencies`
- `astro.config.{js,ts,mjs}` present + `package.json` references `astro`
- `gatsby-config.{js,ts}` present + `package.json` references `gatsby`
- `vite.config.{js,ts}` present + `package.json` references `vite` + framework component (`react`, `vue`, `svelte`)
- `svelte.config.{js,ts}` present + `package.json` references `@sveltejs/kit`
- `hugo.toml` / `config.toml` + `content/` dir with markdown
- `wp-config.php` (WordPress)
- `index.html` + `style.css` + `script.js` (static-html stack — multi-file structured site, NOT a one-shot AI artifact)

**This fixture exercises the Next.js + App Router detection path.** Other stack signals are documented but not separately fixtured in v0.1 scope; expansion in Phase 10 would add per-stack fixtures.

## Distinguishing from `has-AI-output`

A single `.html` file at the project root with no `package.json` and no build-config files is `has-AI-output` (one-shot landing page). Multiple files with framework configuration is `has-existing-site`.

If both signals are ambiguous (e.g., a single `index.html` + a `package.json` that doesn't reference a recognized framework), the hook reports `entry_mode: ambiguous` with both candidates and the bootstrap skill asks the user.

See `expected.yaml` for the asserted output shape.
