# Fixture — `greenfield`

## What this fixture represents

A user invokes Claude Code in an empty project directory. They have no existing site, no AI-generated artifact, no Framer project, no Figma file. They want to build a website from scratch.

This is the canonical "happy path" entry mode (per locked decision 15) — the user starts at phase 1 (idea) and walks the full pipeline.

## Fixture contents

```
fixture/
└── .gitignore   (empty — the project directory is bare)
```

A truly empty project directory cannot be checked into git (git doesn't track empty dirs); a zero-byte `.gitignore` is the placeholder that preserves the fixture in source control. The detection logic must treat `.gitignore` as a "trivial" file that does not disqualify the dir from `greenfield` classification — it's universally part of any new project.

The plugin's production hook (`hooks-handlers/session_start.py::is_effectively_empty`) treats `{README.md, LICENSE, .gitignore, .gitattributes}` as the trivial-file set; the reference detector in `tests/detector.py::META_FILES` matches that exact set so detection agrees across hook and reference implementations. (`.gitkeep` is NOT in either trivial set — using it as a fixture placeholder would cause a false `ambiguous` classification, which is why this fixture uses `.gitignore` instead.)

## Expected behavior

Per `Workstreams/website-builder/foundation/DESIGN-architecture.md` "Entry modes" section + `DESIGN-ingestion-and-extraction.md` §"Why ingestion is a re-runnable phase":

1. SessionStart hook (Captain C) detects empty/near-empty directory.
2. Hook reports `entry_mode: greenfield`.
3. `wb-bootstrap` skill (Captain D) initializes `.website-builder/` with `project.yaml` having `entry_mode: greenfield` + `current_phase: 1` (since no prior phases were run).
4. Agent routes to phase 1 (idea) — full pipeline from scratch.

Per `DESIGN-ingestion-and-extraction.md` line 47 ("Greenfield — nothing yet"), greenfield is the entry mode where phase 6.5 (artifact ingestion) does NOT fire at session start. It may still fire later mid-project per the re-runnable mechanic.

See `expected.yaml` for the asserted output shape.

## Detection signals (for the hook)

- Directory contains no `.html` / `.htm` files
- No `next.config.{js,ts,mjs}` / `astro.config.{js,ts,mjs}` / `gatsby-config.{js,ts}` / `vite.config.{js,ts}` / similar stack-config markers
- No `package.json` referencing a recognized website framework
- No `.framer/` directory
- No `.fig` files
- No `pages/` or `app/` or `src/pages/` directory with content
- Optional: `.gitkeep` or `README.md` only (these are pre-bootstrap meta-files, not project content)

If ALL of the above are true → `entry_mode: greenfield`.
