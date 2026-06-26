# `tests/cli/` — wb CLI dispatch tests (Captain O, Phase 5)

Tests for `scripts/wb.py` — the `wb` CLI dispatcher + its routing to Captain P's
library module, Captain Q's keys module, and the delegated Phase-1 scripts
(`install-skills.sh`, `wb-bootstrap.py`).

Per `tests/README.md` § Phase 5 test conventions + `scripts/README.md` §
Module boundary.

## What's tested

`test_wb_dispatch.py`:

| Class | Tier | What |
|---|---|---|
| `TestWbDispatch` | 1 (always runs) | In-process routing: `library *` → P, `keys *` → Q (argv + project_root passed per the locked `run(argv, *, project_root) -> int` contract); return-code propagation; leading-`--` stripping; clean exit 4 when P's/Q's module is absent; P/Q routing isolation; no-command help; bad-project-dir exit 2; `--help` at every level + `--version` via subprocess; unknown-command rejection. Import-safety guard (`import wb` has no side effects). |
| `TestWbDelegateIntegration` | 2 (skip-when-absent) | Real subprocess invocation of the delegate scripts through `wb.py`: `maintain install-skills` + `skills update` + `skills sync` → `install-skills.sh`; `maintain reconfig` → `wb-bootstrap.py`. Runs against an **isolated HOME** so `install-skills.sh` never touches the real `~/.claude/skills/`. Skips gracefully if a delegate script is missing. |

## Stub discipline (CRITICAL)

P's `wb_library.py` and Q's `wb_keys.py` are built in **parallel worktrees** —
they are NOT present in Captain O's worktree, and **must NEVER be committed into
`scripts/` by this test**. The real modules land at merge time (O merges last;
the General runs the real integration gate post-merge).

The Tier-1 routing tests therefore **inject stub modules into `sys.modules`** at
test time (`_inject_stub("wb_library", recorder)`), exercising `wb.py`'s lazy
imports against test doubles that record the call args. Stubs are removed in an
autouse-fixture teardown so nothing leaks between tests. This is exactly the
"test-local stubs, never commit stubs into scripts/" rule from the dispatch
INST.

When P's + Q's real modules merge, these same routing tests keep passing
(the stubs only stand in when the real module is absent), and the
missing-module-returns-4 tests still pass because they explicitly remove the
stub first.

## Cross-platform note

Subprocess tests invoke `wb.py` via `sys.executable` (not the `wb.sh` launcher
via `bash`). Per `tests/smoke_test.py`'s documented reasoning, invoking the
Python runner directly is portable across all subprocess/bash combinations;
`wb.sh`'s only job is interpreter resolution, which `sys.executable` already
provides. `wb.py`'s own bash-delegate calls resolve the *correct* bash via
`wb._resolve_bash()` (pinning Git-for-Windows bash over the WSL `System32` stub
that can't see the Windows filesystem) — see that function's docstring.

## Running

```bash
# From plugin root — runs everything (Tier 1 + Tier 2):
bash tests/run-tests.sh

# Or just these:
cd tests && uv run --with pyyaml --with pytest pytest cli/ -v
```
