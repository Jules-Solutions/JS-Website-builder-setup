# `tests/keys/` — keys-module tests (Captain Q, Phase 5)

Executable tests for `scripts/wb_keys.py` — the secrets resolver + `wb keys`
migration verbs (per `Workstreams/website-builder/cross-cutting/DESIGN-secrets-and-keys.md`
and the module-boundary contract in `scripts/README.md`).

## What's tested

| Surface | Test class | Tier |
|---|---|---|
| `resolve_keys()` over `.env` source | `TestResolveKeysEnvSource` | 1 |
| `resolve_keys()` over 1Password source (`op` MOCKED) | `TestResolveKeysOnePasswordSource` | 1 |
| Unresolved-required-key error (typed error + fix path) | `TestResolveKeysErrorPath` | 1 |
| `run(["migrate-to-1password", ...])` (`op` MOCKED) | `TestMigrateTo1Password` | 1 |
| `run(["migrate-to-env"])` (`op` MOCKED) | `TestMigrateToEnv` | 1 |
| `run()` dispatch errors (no verb / unknown verb / missing keys.yaml) | `TestRunDispatch` | 1 |
| Import-safety (no side effects on import) | `TestWbKeysImportSafety` | 1 |

All Tier 1 — no real `op` CLI, no real 1Password account, no network. The `op`
subprocess is monkeypatched at the single `wb_keys._run_op` seam. A Tier 2
integration test against a real `op` install (DoD: "1Password CLI flow works for
opt-in users") is the General's merge-gate manual-verification step — see the
Captain Q RPT's manual-verification procedure.

## Secrets hygiene (absolute)

`fixture/` contains **placeholder values only** — obviously-fake tokens
(`placeholder-gemini-not-a-real-key`, etc.). Per `.claude/rules/secrets-conventions.md`
and `tests/README.md` Phase 5, NEVER put a real secret in a fixture. The tests
assert the *mechanism* (which source, which env var, fix-path on missing), not
real key values.

## Fixture layout (one-deep, per `.gitignore` Phase 5 exceptions)

```
tests/keys/
├── fixture/
│   ├── .env                          # source: env values (placeholders)
│   └── .website-builder/
│       ├── keys.yaml                 # references-only registry (env + onepassword mix + one optional)
│       └── .env.op                   # op:// references (mirrors onepassword entries)
├── test_wb_keys.py
└── README.md
```

Tests copy `fixture/` into a pytest `tmp_path` before running, so migrate verbs
(which mutate `keys.yaml` + `.env`) never touch the committed fixture, and the
module's `project_root` is passed in explicitly (never `cwd`).

## Run

```bash
bash tests/run-tests.sh          # full suite (default; runs everything, the canonical green)
cd tests && uv run --with pyyaml --with pytest pytest keys/ -v   # just this subdir
```
