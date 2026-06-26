# `tests/hooks/` — SessionStart hook wiring tests

Phase 6 (Lieutenant `wb-phase6-lt-t-1`). Authored 2026-06-14.

These tests cover the Phase-6 wiring that makes two Phase-5 runtime modules
actually fire at session start:

- `scripts/wb_library.py :: autoclone_for_state` (Captain P — resource auto-clone)
- `scripts/wb_keys.py :: resolve_keys` (Captain Q — secrets resolution)

Phase 5 shipped both **callable-but-unwired** (a ship-verification gap noted in
`RPT-phase-5-stage-completion.md` follow-up #1 + `RPT-phase-5-captain-q.md`
follow-up #1). Phase 6 wires them into `hooks-handlers/session_start.py`; this
suite is the proof the interlock works.

## What's asserted

| Class | Surface | Asserts |
|---|---|---|
| `TestWiringInvocation` | `session_start.main()` | both functions fire once on the mid-project path; neither fires on the fresh path; `autoclone_for_state` is called with `trigger="session-start"` |
| `TestRunAutoclone` | `session_start.run_autoclone` | candidates derived from `project.yaml`; empty project → no candidates; no state dir → non-fatal; import failure → non-fatal; runtime error → non-fatal |
| `TestRunResolveKeys` | `session_start.run_resolve_keys` | env keys resolve (NAMES only); **secret value never in the summary**; no `keys.yaml` → `no-registry`; missing required key → value-free fix-path; import failure → non-fatal; unexpected error → non-fatal |
| `TestHookSubprocessWiring` | the hook as a real subprocess | exit 0; machine-block carries `autoclone` + `keys`; **no secret value in stdout/stderr**; fresh project skips both; no-`keys.yaml` → `no-registry` |

## Tier-1 discipline (always runs)

- **No network, no real `op` CLI, no real secrets.** The two Phase-5 functions
  are monkeypatched on the hook module for invocation assertions; the subprocess
  tests run with an **isolated `HOME`** + a bogus `WB_OP_BIN` so `op` is never
  reachable, over a **synthetic `.website-builder/`** built in `tmp_path` with
  **placeholder-only** secret values.
- **No committed fixture dir.** The repo `.gitignore` ignores `.website-builder/`
  and only whitelists the per-Captain fixture subdirs (`tests/cli|library|keys|…`);
  there is no `tests/hooks/` whitelist, so a committed fixture would be silently
  gitignored. Building the state programmatically in `tmp_path` avoids that and
  keeps the change inside the Lieutenant write zone (no `.gitignore` edit).
- **`project_root` passed in explicitly** — the modules take it per the
  `scripts/README.md` interface contract; tests pass a `tmp_path` dir, never cwd.

## Non-fatal contract

`hooks-handlers/session_start.py` runs on **every** website-builder CC session.
A crash there breaks every user session. Every wiring path is defensive: guarded
imports (a missing module is reported, not raised), every call wrapped so no
exception escapes `main()`, and an encoding-safe `_emit()` so the stdout context
never raises `UnicodeEncodeError` on a Windows cp1252/cp437 console. These tests
exercise each of those failure modes and assert exit 0 throughout.

## Relationship to `smoke_test.py`

`smoke_test.py::TestHookIntegration` (Phase-1 entry-mode hook tests) is a
separate surface and stays 5/5 — these tests are purely additive.

## Run

```bash
# from plugin root — runs everything incl. this subdir (pytest recurses):
bash tests/run-tests.sh

# just this subdir:
cd tests && uv run --with pyyaml --with pytest pytest hooks/ -v
```

## See also

- `hooks-handlers/session_start.py` — the wired hook
- `scripts/wb_library.py` / `scripts/wb_keys.py` — the consumed modules (API
  consumers only; not modified by this Phase-6 work)
- `Workstreams/website-builder/RPT-phase-5-stage-completion.md` — follow-up #1
- `Workstreams/website-builder/RPT-phase-6-lt-t.md` — this work's RPT
- `tests/README.md` — Phase-5 test conventions (Tier 1 / Tier 2, fixture rules)
