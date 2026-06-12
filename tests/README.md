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

## Phase 5 test conventions (Captain-0 prep — added 2026-06-12)

> Phase 5 (skill-flavor + extraction + cross-cutting infrastructure — `BUILD-strategy.md` lines 209-230) introduces the **first code-behavior tests** in this harness. Phases 1-4 tested entry-mode detection (`smoke_test.py`), pre-tool-use gating (`test_pre_tool_use.py`), and shipped **data-only adapter fixtures** (`tests/adapters/`, `tests/cms-adapters/`, `tests/commerce-adapters/` — fixture/expected.yaml/README.md, not yet pytest-wired). Phase 5's `wb` CLI dispatcher + library module + keys module + skill-bundle manifest + Stitch extraction need **executable** tests. This section is the contract for where they land + how `run-tests.sh` picks them up.

### Where each Phase 5 Captain's tests land

One subdirectory per Phase 5 Captain, mirroring the per-adapter subdir convention but holding **executable `test_*.py` files** (not just fixtures):

```
tests/
├── cli/                      # Captain O — wb dispatcher + slash-wrapper + maintain/skills routing
│   ├── test_wb_dispatch.py   # dispatch routing: `library *`→P, `keys *`→Q, `skills *`/`maintain *`→delegated scripts
│   ├── fixture/              # synthetic .website-builder/ project root for invocation tests (if needed)
│   └── README.md             # per-Captain test notes
├── library/                  # Captain P — wb_library.run() verbs + autoclone_for_state() runtime
│   ├── test_wb_library.py    # list/add/remove/refresh/refresh-all/prune/inspect + autoclone (defensive-read)
│   ├── fixture/              # synthetic .website-builder/library/ + project.yaml + a phase-17 contract w/ library_clones_at_entry
│   └── README.md
├── keys/                     # Captain Q — wb_keys.resolve_keys() + migrate verbs
│   ├── test_wb_keys.py       # resolver (.env + op layers), migrate-to-1password, migrate-to-env
│   ├── fixture/              # synthetic .website-builder/keys.yaml + .env + .env.op (NO real secrets — placeholder values only)
│   └── README.md
├── skills-bundle/            # Captain M — ui-ux-pro-max.md manifest schema validation
│   └── ui-ux-pro-max/
│       ├── test_manifest.py  # frontmatter has all canonical fields (per skills-bundle/README.md schema) + body H2s present
│       └── README.md
└── extraction/               # Captain N — Stitch URL→DESIGN.md end-to-end (BUILD-strategy DoD line 225)
    └── stitch/
        ├── test_stitch.py    # normalization of a Stitch DESIGN.md export → project state; input→output contract
        ├── fixture/          # a sample Stitch DESIGN.md export + expected normalized output
        └── README.md
```

**Subdir naming** matches the write-zone tables in `scripts/README.md` + `skills-bundle/README.md`: `tests/cli/`, `tests/library/`, `tests/keys/`, `tests/skills-bundle/ui-ux-pro-max/`, `tests/extraction/stitch/`. Each Captain writes ONLY inside its own subdir (collision-free per Decision 78b).

### How `run-tests.sh` picks them up

The harness is `uv run --with pyyaml --with pytest pytest` over `testpaths = ["."]` with `python_files = ["smoke_test.py", "test_*.py"]` (see `pyproject.toml`). **pytest recurses** — any `test_*.py` anywhere under `tests/` is auto-discovered with no `pyproject.toml` change needed. So a new `tests/library/test_wb_library.py` runs automatically under `bash tests/run-tests.sh`.

**Two-tier semantics carry forward from Phase 1:**

| Tier | Phase 5 meaning | When it runs |
|---|---|---|
| **Tier 1** | Module-unit tests with NO upstream/network/external-tool dependency — pure input→output over synthetic `.website-builder/` fixtures. CLI dispatch routing (mock P/Q), `wb_library` verbs over a fixture dir, `resolve_keys` over a fixture `keys.yaml`+`.env`, manifest-schema validation, Stitch DESIGN.md *normalization* (parse a canned export → expected output). | Always. No upstream dependency = always green when code + fixture align. |
| **Tier 2** | Integration tests that touch a real external surface — `op` CLI resolution (real 1Password), `install-skills.sh` fetching a real upstream, `git clone` of a real repo, a live Stitch URL crawl. | **Skipped** until the external surface is available; auto-detected via a filesystem/binary probe (mirror `smoke_test.py`'s `TestHookIntegration` skip-when-absent pattern). A Tier 2 skip is NOT a failure — it's the expected pre-integration state. |

**To make a Phase 5 Tier-1 class run under `bash tests/run-tests.sh --tier1`:** add its class name to the `-k` expression in `run-tests.sh` line 68 (currently `"TestReferenceDetector or TestFixtureCompleteness"`). Example: `"TestReferenceDetector or TestFixtureCompleteness or TestWbLibrary or TestWbKeys or TestWbDispatch or TestStitchNormalize or TestUiuxManifest"`. Editing `run-tests.sh` is a **shared-substrate edit** — a single Captain doing it races the others. **Convention: each Captain's tests are Tier-1-by-default and run under the no-filter `all` mode (which is the default `bash tests/run-tests.sh`); the `--tier1` `-k` expansion is folded into the General's integration/merge step (or Captain O's integration work if the General directs), NOT race-edited by individual Captains.** Default `bash tests/run-tests.sh` (no `--tier1`) runs everything and is the canonical green check.

### Fixture conventions for Phase 5

Phase 5 fixtures are **synthetic `.website-builder/` project roots** (same spirit as the Phase 3/4 adapter fixtures, different baseline — Phase 5 tests exercise CLI/runtime, not adapter content-mapping):

- **`tests/<captain>/fixture/`** — a minimal-but-valid `.website-builder/` scaffold the module operates on. For `library/`: `project.yaml` (stack/cms/component_library/flavors) + a `library/` dir + at least one phase contract carrying a `library_clones_at_entry` frontmatter field (see `scripts/README.md` § `library_clones_at_entry` schema) so `autoclone_for_state` has something to read. For `keys/`: a `keys.yaml` + `.env` + `.env.op` — **placeholder values ONLY, never real secrets** (per `secrets-conventions.md`; the resolver test asserts the *mechanism*, not real key values).
- **`expected.yaml` / expected-output files** — where the module's output is non-trivial (e.g. Stitch normalization), commit an `expected` artifact and assert against it (same shape as the Phase 3/4 adapter `expected.yaml`).
- **`project_root` is passed in, not discovered** — Phase 5 modules take `project_root: Path` explicitly (per the `scripts/README.md` interface contract), so tests pass a `tmp_path`-copied fixture dir rather than relying on `cwd`. Mirrors `smoke_test.py`'s `tempfile.mkdtemp` + cwd-via-contract pattern (lines 85, 414).
- **Import-safety check** — because the interface contract requires P's/Q's modules to be import-safe (no network/file-write/`op` calls at import time), each module's test SHOULD include a bare `import wb_library` / `import wb_keys` assertion that succeeds with no side effects (the cheapest regression guard for the import-safety rule).
- **gitignore exceptions** — `.website-builder/` is gitignored at the repo level, so fixture `.website-builder/` dirs need `!tests/<captain>/fixture/.website-builder/**` un-ignore lines. Captain-0 adds the Phase 5 exception patterns to `.gitignore` as part of this prep (see the repo-root `.gitignore`); Phase 5 Captains do NOT edit `.gitignore`.

### Why Phase 5 tests are code-tests, not fixture-data

The Phase 3/4 adapter "tests" are **contract fixtures** — data that adapter *documentation* references; they validate that the schema's content-layer mapping is internally consistent, read by humans + (eventually) by a phase-12/18 skill at runtime. Phase 5 ships **executable Python modules** (`wb_library.py`, `wb_keys.py`, the dispatcher) — those have real input→output behavior that must be asserted with `assert`, not just shape-checked. This is the harness's first true unit-test surface; per `.claude/rules/testing.md`, every public module surface (`run()`, `autoclone_for_state()`, `resolve_keys()`) gets ≥1 test.

## Files in this dir

| File | Purpose |
|---|---|
| `run-tests.sh` | Bash entry point with `--tier1` / `--verbose` / `--no-uv` flags |
| `smoke_test.py` | Pytest suite — Phase 1 entry-mode detection + bootstrap (Tier 1 + Tier 2) |
| `test_pre_tool_use.py` | Pytest suite — pre-tool-use gating (Captain C hook logic) |
| `detector.py` | Pure-Python reference implementation of entry-mode detection |
| `pyproject.toml` | Test-suite pyproject (pytest + pyyaml deps) |
| `walkthroughs/` | Per-entry-mode fixture suite (5 dirs) — Phase 1 |
| `adapters/`, `cms-adapters/`, `commerce-adapters/` | Per-adapter data fixtures (fixture/expected.yaml/README.md) — Phase 3/4 |
| `cli/`, `library/`, `keys/`, `skills-bundle/`, `extraction/` | Per-Captain Phase 5 code-test subdirs (created by Captains M-Q; see § Phase 5 test conventions) |
| `README.md` | This file |

## See also

- `Workstreams/website-builder/foundation/DESIGN-architecture.md` — full plugin
  design including Entry Modes section
- `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` — the
  `.website-builder/` user-project layout that Tier 2 bootstrap tests assert
- `Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md` —
  detection signals and phase 6.5 mechanism this harness validates
- `Workstreams/website-builder/BUILD-strategy.md` — Phase 1 DoD lines 134-138;
  Phase 5 DoD lines 223-228
- `.claude/temp/ctx7-docs/claude-code-plugin-spec.md` — CC plugin spec (hooks,
  skills, manifest)
- `scripts/README.md` — Phase 5 `wb` CLI + module-boundary contract +
  `library_clones_at_entry` schema (Captains O/P/Q test their modules per § Phase 5)
- `skills-bundle/README.md` — Phase 5 skill-manifest schema (Captain M's
  `tests/skills-bundle/ui-ux-pro-max/` validates against it)
- `.claude/rules/testing.md` — testing discipline (every public module surface
  gets ≥1 test; Tier 1 vs Tier 2 semantics)
