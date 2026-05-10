# `tests/` — website-builder plugin test infrastructure

Phase 1 / Captain E scope. Authored 2026-05-10.

This directory holds the plugin-level test harness for the website-builder
Claude Code plugin. The harness validates entry-mode detection (Captain C's
SessionStart hook) and `.website-builder/` initialization (Captain D's
`wb-bootstrap` skill) against the spec from `Workstreams/website-builder/`.

## Quick start

```bash
# From plugin root:
./tests/run-tests.sh
```

Or directly via `uv` + `pytest`:

```bash
cd tests
uv run --with pyyaml --with pytest pytest -v
```

## Test tiers

| Tier | What it tests | When it runs |
|---|---|---|
| **Tier 1 — Reference detector** | The `detector.py` reference implementation classifies each fixture correctly per `expected.yaml`. Validates fixture / spec internal consistency. | Always (no upstream dependency). |
| **Tier 1 — Fixture completeness** | Every entry mode has `README.md` + `fixture/` + `expected.yaml`; YAML parses; required keys present. | Always. |
| **Tier 2 — Hook integration** | Captain C's SessionStart hook (at `hooks-handlers/session-start.{sh,py}`) classifies each fixture correctly. | Skipped until Captain C's branch merges. Auto-detected via filesystem probe. |
| **Tier 2 — Bootstrap-skill integration** | Captain D's `wb-bootstrap` skill correctly initializes `.website-builder/` against each fixture. Requires a runner script at `scripts/wb-bootstrap.{sh,py}`. | Skipped until Captain D's branch merges + a runner exists. |

A Tier 2 skip is NOT a failure — it's the expected pre-merge state. The General
runs the suite after merging all 4 Phase 1 feature branches to `dev`; Tier 2
skips become passes (or B/C/D iteration signals if they fail).

## What each fixture represents

```
walkthroughs/
├── greenfield/             # empty project — start at phase 1
├── has-existing-site/      # Next.js project — phase 6.5 ingestion at start
├── has-AI-output/          # one-shot AI landing page — phase 6.5 with ai-output extractor
├── has-Framer-attempt/     # partial Framer project — phase 6.5 with Framer adapter
└── has-Figma-file/         # Figma file delivered by designer — phase 6.5 with Figma extractor
```

Per locked decision 15 in `Workstreams/website-builder/website-builder.md`:

> 15. **AI-output ingestion** — entry-mode variant **plus** re-runnable phase 6.5
>     (mom's pattern: she generates a new section in ChatGPT mid-project, agent
>     runs phase 6.5 to integrate).

Each fixture has:

```
<entry-mode>/
├── README.md         # what this fixture represents + detection signals
├── fixture/          # the project state used as test input
└── expected.yaml     # asserted hook + bootstrap output
```

## v0.1 scope (this Captain's deliverable)

**In scope:**
- Entry-mode detection — does the hook correctly classify each of the 5 fixtures?
- Bootstrap initialization shape — does the skill correctly create `.website-builder/`?
- Fixture sanity — do the fixtures exist + parse + match their expected outputs?

**Out of scope (deferred):**
- Real ingestion flows (phase 6.5 actually extracting tokens from a live URL,
  parsing AI output, calling the Framer Server API, ingesting Figma JSON) —
  these are Phase 3+ adapter work covered by per-stack/per-extraction tests.
- End-to-end agent invocation — running real Claude Code against a fixture and
  watching the agent walk phase 1 (idea) end-to-end. Phase 7-8 cosplay/Ralph
  tests cover this.
- Multi-stack fixtures (Astro / SvelteKit / Hugo / WordPress / static-html
  variants of `has-existing-site`). Phase 10 expansion.
- Webflow / Wix / partial-WordPress variants of `has-Framer-attempt`. Phase 10.
- Edge-case fixtures (ambiguous inputs, multiple stack signals at once,
  corrupted Framer projects, etc.). Phase 7-8 surface real failure modes.

## How to add a new fixture

1. Create `walkthroughs/<name>/` with `README.md`, `fixture/`, and `expected.yaml`
2. Add `<name>` to the `ENTRY_MODES` list in `smoke_test.py`
3. Update the reference detector in `detector.py` if a new detection signal is needed
4. Run `./run-tests.sh` — Tier 1 should pass immediately if fixtures + spec align
5. Run `./run-tests.sh --tier1` to skip Tier 2 if you don't have hook/skill
   integration ready yet

## How to debug a failing test

**Tier 1 detector test fails** — either the detector is wrong (update `detector.py`)
or the fixture is wrong (update `fixture/` or `expected.yaml`). The error message
names which signal disagreed.

**Tier 2 hook test fails post-merge** — Captain C's hook output disagrees with
`expected.yaml`. Compare the hook's stdout to the expected dict; usually the
hook needs a one-line update to match the spec (or `expected.yaml` is wrong).

**Tier 2 bootstrap test fails post-merge** — Captain D's skill produced a
`.website-builder/` shape that disagrees with `expected.yaml`. Compare the
generated `project.yaml` to the expected dict.

## Files in this dir

| File | Purpose |
|---|---|
| `run-tests.sh` | Bash entry point with `--tier1` / `--verbose` flags |
| `smoke_test.py` | Pytest suite — Tier 1 + Tier 2 |
| `detector.py` | Pure-Python reference implementation of entry-mode detection |
| `pyproject.toml` | Test-suite pyproject (pytest + pyyaml deps) |
| `walkthroughs/` | Per-entry-mode fixture suite (5 dirs) |
| `README.md` | This file |

## See also

- `Workstreams/website-builder/foundation/DESIGN-architecture.md` — full plugin
  design including Entry Modes section
- `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` — the
  `.website-builder/` user-project layout that Tier 2 bootstrap tests assert
- `Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md` —
  detection signals and phase 6.5 mechanism this harness validates
- `Workstreams/website-builder/BUILD-strategy.md` — Phase 1 DoD lines 134-138
- `.claude/temp/ctx7-docs/claude-code-plugin-spec.md` — CC plugin spec (hooks,
  skills, manifest)
