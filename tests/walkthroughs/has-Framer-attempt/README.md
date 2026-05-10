# Fixture — `has-Framer-attempt`

## What this fixture represents

A user has started a Framer / Webflow / Wix / WordPress project (or has a partial Framer file) and wants the website-builder to ingest it as the starting point. Sister's "Still Humans" Framer project (the cosplay test target per locked decision 10 + 57) is the canonical use case.

Per locked decision 15 + `DESIGN-architecture.md` line 249:

> **`has-framer-attempt.md`** — user has a partial Framer / Webflow / Wix / WordPress project. Phase 6.5 + corresponding stack adapter walk the artifact; agent decides what's keepable.

This fixture exercises the Framer detection path specifically, since Framer is the highest-stakes v1 stack (sister's cosplay test). Detection of Webflow / Wix / partial WordPress is the same shape (presence of stack-specific marker files / dirs) and would be added as separate fixtures in Phase 10 expansion.

## Fixture contents

```
fixture/
├── .framer/
│   ├── project.json            # mock Framer project metadata
│   └── pages.json              # mock Framer pages list
└── README.md                    # user-authored notes (irrelevant to detection)
```

The `.framer/` directory is the primary detection signal. Real Framer projects have substantially more structure inside it (binary asset blobs, page snapshots, version history); the fixture's `project.json` + `pages.json` are minimal stand-ins that mirror schema-shape but contain no proprietary data.

## Expected behavior

1. SessionStart hook (Captain C) detects `.framer/` directory at project root.
2. Hook reports `entry_mode: has-Framer-attempt`.
3. `wb-bootstrap` skill (Captain D) initializes `.website-builder/` with `project.yaml` having `entry_mode: has-Framer-attempt` + `stack: framer` (pre-detected).
4. Agent surfaces "I see an existing Framer project — should I run phase 6.5 to walk the Framer pages via Framer Server API + extract design tokens?" via AskUserQuestion.
5. On confirm, agent routes to phase 6.5 with the Framer adapter (per `stacks/DESIGN-stack-framer.md` Phase 6.5 ingestion section, authored by Phase 3's Captain F).

## Detection signals (for the hook)

Per `DESIGN-ingestion-and-extraction.md` line 49:

**Strong signals (any one triggers `has-Framer-attempt`):**
- `.framer/` directory at project root (Framer)
- `framer-config.json` or `framer.json` at project root
- `webflow-export/` directory + `style.css` + `index.html` (Webflow export)
- `wix-export.json` (Wix exported artifact)
- `wp-content/themes/` + `wp-config-sample.php` (WordPress incomplete; distinct from full deployed WP)

This fixture exercises the `.framer/` detection path. The other variants are documented but not separately fixtured in v0.1.

## Distinguishing edge cases

- A `.framer/` dir nested deep inside another project (e.g., `assets/.framer/`) is NOT `has-Framer-attempt` — only the root-level marker counts.
- A Framer project AND a Next.js `package.json`: ambiguous; bootstrap asks user.

See `expected.yaml` for the asserted output shape.
