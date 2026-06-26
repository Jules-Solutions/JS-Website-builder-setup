# `tests/fanout/` — parallel-research fan-out substrate tests

Wave 3b scope (Captain `fanout-1`). Tests for `scripts/wb_fanout.py` + its `wb fanout`
dispatch route — the gap-#8 fan-out substrate from
`Workstreams/website-builder/foundation/DESIGN-orchestration-spine.md` § 8.

## What's covered

| Class | Surface |
|---|---|
| `TestWbFanoutImportSafety` | bare `import wb_fanout` is side-effect-free (the interface contract) |
| `TestBuildRun` | `build_run()` — a research brief → N per-subject sub-agent specs (the decompose core) |
| `TestSpawnRecipe` | `render_spawn_recipe()` — the markdown the agent executes (Agent + TaskCreate + aggregate) |
| `TestLedger` | `record_run()`/`_load_runs()` — the `.website-builder/tasks.yaml` fan-out ledger, round-trip + sibling-key preservation + idempotent replace |
| `TestAggregate` | `aggregate_results()` — N structured results → synthesis (matrix, per-dimension cross-cut, coverage gaps) |
| `TestCli` | `run()` — `decompose` / `aggregate` / `status` verb dispatch over a tmp_path project root |
| `TestDispatch` | `wb fanout ...` routes through `scripts/wb.py` to `wb_fanout.run` |

## Tier

All Tier 1 (per `tests/README.md` § Phase 5 conventions): pure input→output over
`tmp_path` project roots — no network, no external tools, no live agent. The
`Agent`/`TaskCreate` spawn is the in-session agent's job (a script cannot call those
tools — see `skills/wb-fanout/SKILL.md`); these tests cover everything the helper
deterministically owns. `project_root` is passed in explicitly (the interface
contract), so each test uses its own `tmp_path` — no committed `.website-builder/`
fixture is needed (and none is added; `.website-builder/` is gitignored at the repo
root and read-only for this Captain).

## Run

```bash
# from plugin root
./tests/run-tests.sh
# or just this file
cd tests && uv run --with pyyaml --with pytest pytest fanout/ -v
```

## See also

- `scripts/wb_fanout.py` — the substrate under test
- `skills/wb-fanout/SKILL.md` — the agent-facing surface that executes the spawn-recipe
- `Workstreams/website-builder/foundation/DESIGN-orchestration-spine.md` § 8 — the contract
