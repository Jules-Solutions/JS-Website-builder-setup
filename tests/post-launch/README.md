# `tests/post-launch/` — post-launch maintainer template tests

Phase 6 / Captain S scope. Authored 2026-06-14.

Validates the **post-launch maintainer template** (the "killer template" the website-builder materializes at deploy / phase 29, per locked decisions 28 / 37 / 45 / 49 and `Workstreams/website-builder/cross-cutting/DESIGN-post-launch-template.md`).

## What's tested

| Class | Tier | What it validates |
|---|---|---|
| `TestPostLaunchTemplate` | 1 | The plugin's `post-launch/` source tree — maintainer agent profile frontmatter (mirrors the main `website-builder.md` shape), all 8 `wb-maintain-*` SKILL.md presence + frontmatter + time-box, the 5 runbooks, exactly-8-skills lock (decision 49). |
| `TestConfigTemplate` | 1 | `config-template.yaml` parses + carries the 7 wizard sections + the skill-subset list. |
| `TestMaterializer` | 1 | `scripts/wb_postlaunch.py` run against an **isolated temp project dir**: config.yaml written with resolved identity, chosen skill subset materialized, maintainer profile placeholders resolved, subset honored, idempotent re-run, clean failure on missing state / invalid answers. |
| `TestMaterializerUnit` | 1 | In-process unit tests of `wb_postlaunch.py` pure functions (placeholder resolution, answer validation, config build) + the import-safety regression guard. |

All **Tier 1** — no network, no real `~/.claude` skills dir, no external tools. Deterministic + green when the `post-launch/` source + the runner align.

## Isolation discipline

The materializer tests follow the Phase-5 isolated-HOME discipline (mirroring `tests/cli/test_wb_dispatch.py` + `smoke_test.py`):

- Each test seeds a minimal `.website-builder/project.yaml` in a fresh `tempfile.mkdtemp()` dir and points the runner at it via `cwd`.
- The runner writes ONLY into that temp project's `.website-builder/post-launch/` — **never** the plugin repo's own `.website-builder/` (gitignored) and **never** the real user CC dir.
- The runner is invoked as `[sys.executable, "scripts/wb_postlaunch.py", ...]` (the .py directly, per the portable-invocation reasoning in `smoke_test.py`/`test_wb_dispatch.py`), with `CLAUDE_PLUGIN_ROOT` set so it resolves the template source.

No committed fixture `.website-builder/` dir is needed — the tests synthesize the project state in `tmp_path`, so no `.gitignore` un-ignore exception is required for this subdir.

## The wizard mechanism (what these tests exercise)

Per the INST option (a): the phase-29 wizard is **skill-prose-driven** (in `skills/wb-deploy/SKILL.md` § The post-launch maintainer wizard) + a **standalone materializer** `scripts/wb_postlaunch.py` (mirroring `scripts/wb-bootstrap.py`). The runner is NOT a `wb` CLI verb — the `wb` verb surface is locked (`scripts/wb.py` lines 72-77; adding a verb is a General-review change). `wb_postlaunch.py` ships standalone, invoked by the wb-deploy skill at phase 29 + re-runnable directly. These tests exercise the runner end-to-end against temp dirs.

## How `run-tests.sh` picks them up

`pytest` recurses over `testpaths = ["."]` with `python_files = ["smoke_test.py", "test_*.py"]` (see `tests/pyproject.toml`) — so `tests/post-launch/test_post_launch.py` is auto-discovered with no harness edit. Run via `bash tests/run-tests.sh` from the plugin root. Default mode (no `--tier1`) runs everything; these are all Tier 1 and run in both modes (the `--tier1` `-k` filter is folded in at the General's integration step, not race-edited here).

## See also

- Template source: `post-launch/` (README + agents/website-maintainer.md + skills/wb-maintain-* + runbooks/ + config-template.yaml)
- Materializer: `scripts/wb_postlaunch.py`
- Wizard procedure: `skills/wb-deploy/SKILL.md` § The post-launch maintainer wizard (phase 29)
- Phase 29 contract: `phase-contracts/29-hosting-deployment.md`
- Design: `Workstreams/website-builder/cross-cutting/DESIGN-post-launch-template.md`
- RPT: `Workstreams/website-builder/RPT-phase-6-captain-s.md`
