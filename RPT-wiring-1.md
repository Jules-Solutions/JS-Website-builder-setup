---
type: RPT
workstream: website-builder
title: Wave 3a (wiring-1) — post-launch wizard invocation (gap #6) + project-root CLAUDE.md (gap #2)
status: complete
author: wiring-1 (Captain)
created: 2026-06-26
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-orchestration-spine.md
  - Workstreams/website-builder/cross-cutting/DESIGN-post-launch-template.md
---

# RPT — Wave 3a (`wiring-1`)

> Two call-site wirings the build left unconnected, both hung off the orchestration spine:
> **gap #6** (the phase-29 deploy flow now invokes `wb_postlaunch.py`) and **gap #2** (`wb-bootstrap`
> writes a standing project-root `CLAUDE.md`; the spine keeps its phase line fresh).
> Branch `wiring-1` off `dev`. Merge target `dev` only (master held through Wave 5). **Did not merge.**

## Summary

Both gaps are closed and shipped on branch `wiring-1`. Gap #6: the `wb-deploy` SKILL.md now carries a
robust `python3 || python || py` fallback invocation of `${CLAUDE_PLUGIN_ROOT}/scripts/wb_postlaunch.py`
at the phase-29 post-deploy-verify step (it previously used a bare `python`, which fails on machines
where only `python3` or `py` is on PATH). Gap #2: a new leaf module `scripts/wb_claudemd.py` owns a
**delimited managed-block** project-root `CLAUDE.md`; `wb-bootstrap.py` creates it after the `.gitignore`
write, and `wb_orchestrate.py` refreshes its phase line (and stack/CMS) on every phase entry
(`run_post_tool_use` + `run_session_start`), defensively — never creating the file, never clobbering
user edits, never crashing. Full suite **437 passed** (413 baseline + 24 new); pyright **0/0/0**.

## What was done

**Files changed (4) + added (2):**

| File | Change |
|---|---|
| `skills/wb-deploy/SKILL.md` (edit) | Phase-29 Step B bash block rewired from bare `python …` to the `python3 \|\| python \|\| py` fallback the hooks use; step-6 prose updated to point at `${CLAUDE_PLUGIN_ROOT}` + the fallback. |
| `scripts/wb_claudemd.py` (**new**) | Leaf module owning the project-root `CLAUDE.md` managed block: `render_managed_block`, `upsert_managed_block`, `write_project_claudemd` (bootstrap CREATE), `refresh_project_claudemd` (spine REFRESH). Import-safe, no stdout, LF-normalized UTF-8 byte-write. |
| `scripts/wb-bootstrap.py` (edit) | Imports `wb_claudemd` (scripts/ on sys.path); new Step 7.5 calls `write_project_claudemd(project_root, proj)` right after the `.gitignore` write. |
| `scripts/wb_orchestrate.py` (edit) | Soft-imports `wb_claudemd` (guarded — peripheral to injection); new `_refresh_project_claudemd` helper; called in `run_post_tool_use` + `run_session_start` after the marker write. |
| `tests/post-launch/test_post_launch.py` (edit) | New `TestDeploySkillWiring` (4 tests) — contract test over the SKILL.md wb_postlaunch wiring. |
| `tests/claudemd/test_wb_claudemd.py` (**new**) | 20 tests — managed-block unit, bootstrap subprocess, spine refresh integration, defensive. |

**Commands run:** `bash tests/run-tests.sh` (uv) → 437 passed; `npx pyright@latest` → 0/0/0; an
end-to-end demo (greenfield bootstrap → advance phase → wb_postlaunch materialize) in an isolated temp dir.

## DoD evidence

### 1. Fresh greenfield bootstrap → `.website-builder/` scaffold **and** project-root `CLAUDE.md` exist

```
[wb-bootstrap] Created …/.website-builder/ with sub-dirs: content/pages, …, post-launch
[wb-bootstrap] .gitignore: created
[wb-bootstrap] project-root CLAUDE.md: created
[wb-bootstrap] Wrote .website-builder/README.md
scaffold present: True
project-root CLAUDE.md present: True
```

`ls` of the project root after bootstrap: `.gitignore`, `.website-builder/`, `CLAUDE.md`.
The generated `CLAUDE.md` (verbatim):

```markdown
<!-- BEGIN website-builder (managed orientation — auto-updated on phase change; add your own notes OUTSIDE these markers) -->
# (project name set at phase 1)

> Built with the **website-builder** Claude Code plugin. The plugin keeps this block
> current as your project advances — edits *inside* the markers are overwritten on
> phase change. Put your own project notes **outside** the markers; those are never touched.

- **Project:** (project name set at phase 1)
- **Current phase:** 0
- **Stack:** (not yet chosen)
- **CMS:** (not yet chosen)
- **State:** `.website-builder/` — `project.yaml` is the canonical project state.

## How to resume

Open this project in Claude Code with the website-builder plugin installed. Its
SessionStart hook reads `.website-builder/project.yaml` and resumes at the current
phase; the orchestration spine re-injects that phase's resources, skill discipline,
and stack/CMS adapter guidance. Tell the agent what you want to do next — it knows
where you are in the build.

If the plugin isn't loaded, `.website-builder/project.yaml` still records your phase,
stack, CMS, and locked choices so any agent can orient from it.
<!-- END website-builder (managed orientation) -->
```

### 2. Advance phase → the spine refreshes the project `CLAUDE.md` phase line (before/after)

Project advanced `project.yaml.current_phase` 0→11 (+ identity filled: name `demo-site`, stack `nextjs`),
then `wb_orchestrate.run_post_tool_use(root)` fired:

```
# BEFORE (seeded at phase 0)
- **Project:** (project name set at phase 1)
- **Current phase:** 0
- **Stack:** (not yet chosen)

spine fired for phase: 11

# AFTER (refreshed by the spine)
- **Project:** demo-site
- **Current phase:** 11
- **Stack:** nextjs

managed-block count (must stay 1): 1
```

The phase line, project name, and stack all refresh; the managed block stays singular (no duplication);
user content outside the markers is untouched (covered by `test_spine_leaves_unmanaged_claudemd_untouched`
+ `test_upsert_replaces_in_place_preserving_user_content`).

### 3. Phase-29 deploy path invokes `wb_postlaunch.py` → `.website-builder/post-launch/` materializes

SKILL.md wiring (`skills/wb-deploy/SKILL.md:92-94`):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wb_postlaunch.py" --answers "$ANSWERS_JSON" \
  || python "${CLAUDE_PLUGIN_ROOT}/scripts/wb_postlaunch.py" --answers "$ANSWERS_JSON" \
  || py "${CLAUDE_PLUGIN_ROOT}/scripts/wb_postlaunch.py" --answers "$ANSWERS_JSON"
```

Real materializer run (the runner the SKILL.md invokes), against the demo project:

```
[wb-postlaunch] Wrote .website-builder/post-launch/config.yaml
[wb-postlaunch] Materialized agents/website-maintainer.md (placeholders resolved)
[wb-postlaunch] Materialized 8 maintainer skill(s): wb-maintain-content, …, wb-maintain-escalate
[wb-postlaunch] Materialized 5 runbook(s)
[wb-postlaunch] Post-launch maintainer materialized at .website-builder/post-launch for project demo-site.
post-launch/ materialized: True
  config.yaml: True
  website-maintainer.md: True
  skills materialized: [all 8 wb-maintain-*]
```

### 4. Full `tests/` suite green

```
============================ 437 passed in 16.44s =============================
```

413 (Wave-2 baseline) + 24 new (`TestDeploySkillWiring` 4 + `tests/claudemd/` 20).

### 5. `npx pyright@latest` from repo root → 0/0/0

```
0 errors, 0 warnings, 0 informations
```

(Baseline was also 0/0/0; the new module + edits keep it clean.)

## Decisions made

1. **Managed-block, NOT write-once (the §9 idempotency design — load-bearing).** The mission flagged
   this as a potential pause-and-report point. It is **not** ambiguous: write-once-whole-file is
   *incompatible* with the requirement that "the spine keeps the phase line fresh on phase entry" — you
   cannot refresh a line you never touch after creation. A delimited managed block (HTML-comment markers,
   mirroring the existing `.gitignore` `GITIGNORE_START/END` pattern in the same `wb-bootstrap.py`) is the
   only design that satisfies **both** requirements simultaneously: user edits live *outside* the markers
   (never clobbered), and the spine rewrites the block *inside* them (phase line always fresh). No pause
   was warranted; building per the design's own §9 "managed/delimited block" option.

2. **The spine REFRESHES the whole managed block, not just a single phase line.** Re-rendering the block
   from `project.yaml` (via the same `render_managed_block`) keeps stack + CMS + project-name fresh too
   (stack is picked at phase 11, CMS at 12, name at phase 1), and keeps a single SSOT for the block
   content. The block render is **deterministic (no timestamp)** so an unchanged identity re-renders to
   identical bytes → no git churn.

3. **Refresh lives in the CALLERS (`run_post_tool_use` / `run_session_start`), not in
   `orchestrate_phase_entry`.** This mirrors the existing marker-I/O placement exactly: both are
   phase-entry bookkeeping *writes* the callers own, keeping `orchestrate_phase_entry` pure (so the 5-action
   unit tests don't acquire a filesystem side effect on the project root).

4. **`wb_claudemd` soft-imported in the spine, hard-imported in bootstrap.** In `wb_orchestrate.py` the
   CLAUDE.md refresh is peripheral to the spine's injection, so a present-but-broken/absent module must
   never break the spine import — guarded `try/except` → degrades to a no-op (mirrors the Wave-2
   import-guard doctrine). In `wb-bootstrap.py` it is a direct dependency (the whole point of that step),
   imported normally; the call itself is `try/except`-wrapped so a CLAUDE.md failure never fails bootstrap.

5. **Gap #6 was a robustness delta, not a from-scratch wiring.** The SKILL.md already named
   `wb_postlaunch.py`, but with a bare `python` invocation. Per the mission's explicit instruction, the
   delta was to adopt the `python3 || python || py` fallback the hooks use (`hooks/hooks.json`) so it is
   robust across machines — and to add a structural contract test so the wiring can't silently regress.

6. **New leaf module `scripts/wb_claudemd.py` rather than duplicating logic.** Per
   `modular-build-convention.md` — both `wb-bootstrap.py` (a hyphenated, non-importable filename) and
   `wb_orchestrate.py` need the managed-block logic; a shared leaf module is the SSOT-clean way to share it.

## Sub-agents used

None. Executed directly (per Captain doctrine: execute, do not re-dispatch).

## Follow-ups filed

- **`wb maintain postlaunch` CLI verb** (pre-existing, not introduced here): the SKILL.md still invokes
  `wb_postlaunch.py` directly because the `wb` verb surface is locked (`scripts/README.md`). A future
  Captain INST could add `wb maintain postlaunch` to wrap the runner. Out of scope for this packet.
- **`session_start.py` could surface the project CLAUDE.md presence** in its context block (a one-line
  "project CLAUDE.md: present/managed" note) — minor polish, not required by the DoD. Flagged for the
  General's consideration; not built here to keep the change minimal.

## Ship Verification

Designed-and-merged ≠ shipped (dispatch-flow Stage 6). Verbatim call-site evidence that the wiring is live:

**Gap #2 — bootstrap CREATE call-site:**
- `scripts/wb-bootstrap.py:66` — `import wb_claudemd` (after `sys.path.insert(0, PLUGIN_ROOT/"scripts")`).
- `scripts/wb-bootstrap.py:689` — `claudemd_result = wb_claudemd.write_project_claudemd(project_root, proj)`
  inside `bootstrap()`, immediately after `extend_gitignore(...)` (Step 7.5). **Smoke-confirmed**: greenfield
  bootstrap writes a real `CLAUDE.md` at the project root (DoD #1 paste).

**Gap #2 — spine REFRESH call-sites:**
- `scripts/wb_orchestrate.py:99` — soft-`import wb_claudemd` (guarded).
- `scripts/wb_orchestrate.py:486` — `def _refresh_project_claudemd(project_root)` (calls
  `wb_claudemd.refresh_project_claudemd`).
- `scripts/wb_orchestrate.py:773` — invoked in `run_post_tool_use` (after `_write_marker`).
- `scripts/wb_orchestrate.py:789` — invoked in `run_session_start` (after `_write_marker`).
  **Behavior-confirmed**: advancing `current_phase` 0→11 rewrote the CLAUDE.md phase line via the live
  `run_post_tool_use` path (DoD #2 paste); the existing PostToolUse handler subprocess tests
  (`TestHandlerSubprocess`) stay green, so the JSON `additionalContext` stdout is uncorrupted (the refresh
  writes no stdout).

**Gap #6 — deploy-skill invocation:**
- `skills/wb-deploy/SKILL.md:92-94` — the `python3 || python || py` fallback invoking
  `${CLAUDE_PLUGIN_ROOT}/scripts/wb_postlaunch.py --answers "$ANSWERS_JSON"`, inside the
  `## The post-launch maintainer wizard (phase 29)` section. **Contract-tested** by
  `TestDeploySkillWiring` (4 tests: invocation present, all-three-interpreter fallback, in-phase-29-section,
  runner-file-exists) and **smoke-confirmed** by a real `wb_postlaunch.py` run materializing
  `.website-builder/post-launch/` (DoD #3 paste).

If the system silently dropped any of these, the next agent would see: a greenfield project with no
project-root `CLAUDE.md`; a stale phase line after an advance; or a phase-29 deploy that never materializes
the post-launch maintainer. All three are now wired and verified.

## Retro notes

- The only build hiccup was 6 self-inflicted test-string mismatches (asserting `Current phase: 11` vs the
  actual markdown-bold `**Current phase:** 11`); the production code was correct first time. Cheap fix.
- The managed-block design generalizes cleanly: any future "standing surface the plugin keeps fresh"
  (e.g. a project-root `AGENTS.md`) can reuse `wb_claudemd`'s render/upsert primitives.

## Branch + commit

- Branch: `wiring-1` (off `dev` @ `4da14c6`).
- Final commit sha: _recorded in the standup / final message_ (this RPT is committed on `wiring-1`).
- **Not merged** — the General reviews + merges to `dev`.
