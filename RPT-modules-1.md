---
type: RPT
workstream: website-builder
title: "Wave 2 (modules-1) — content-layer validation + image/video consumer modules + session-start wiring + pyright hygiene"
status: complete
author: modules-1 (Captain)
created: 2026-06-26
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-orchestration-spine.md
  - Workstreams/website-builder/foundation/DESIGN-content-layers.md
  - Workstreams/website-builder/cross-cutting/DESIGN-image-gen-consumer.md
  - Workstreams/website-builder/cross-cutting/DESIGN-video-audio-consumer.md
---

# RPT — Wave 2 (modules-1)

> Branch `modules-1` off `dev` (plugin repo `JS-Website-builder-setup`). Do NOT touch master (held through Wave 5). The General reviews + merges to `dev`.

## Summary

Built the three Wave-2 modules that light up the orchestration spine's import-guarded actions 4 (content-layer validation) + 5 (image-gen path), wired the consumer resolvers + a content-layer-validation summary into `session_start.py`, refreshed the spine's stale Wave-2 comments (guards retained per INST locked decision), and added a repo-root `pyrightconfig.json` that resolves the runtime-only sibling imports under static analysis. Closes gap #1 (image/video consumer = zero impl) + gap #7 (content-layer validation absent). Full `tests/` suite green at **413** (was 365); pyright **0 errors / 0 warnings** across `scripts/` + `hooks-handlers/`.

## What was done

**New modules (`scripts/`)** — each mirrors the locked `wb_keys.py` shape (import-safe, `project_root` explicit, typed result, logging helpers, resolver entry point, `run(argv, *, project_root)`, `main()`); each depends only on the leaf util `wb_markdown` + stdlib, imports no sibling resolver (no cycle):

- `scripts/wb_validate_layers.py` — `validate_content_layers(project_root) -> list[str]` per `DESIGN-content-layers.md` §351-362 (the 7 cross-layer checks). **Skip-on-absent contract**: the 5 layers are authored progressively across phases, so each check is a no-op when its source files don't exist — a greenfield project returns `[]`. Each finding carries a concrete fix-path. **Decision 41**: a key present in the default language but missing from another language is a `[warning]` (runtime falls back to the default value), not a hard `[error]`. `$`-prefixed JSON-schema meta keys (`$language`/`$schema`) are excluded from parity.
- `scripts/wb_imagegen.py` — `resolve_imagegen_path(project_root) -> ImagegenPath`. **Consumer-fallback per decision 56** (user-provides-key; platform path is forward-room, never returned in v1). Reads the `image_gen` block from `.website-builder/keys.yaml`; **secret-safe** — surfaces only provider name, key env-var NAME, and a present/MISSING boolean (the value is read for the emptiness test and immediately discarded, never stored/returned/logged).
- `scripts/wb_videogen.py` — `resolve_videogen_path(project_root) -> VideogenPath`. Sister of imagegen; resolves video + audio modalities (`video_gen`, `audio_gen.{voice,music,sfx}`, tolerant of flat / nested `primary`/`fallback` / suffix shapes). Same secret discipline.

**Wiring:**

- `hooks-handlers/session_start.py` — added `run_resolve_media()` (calls both consumer resolvers) + `run_validate_layers()` (calls the validator) + two render helpers (`_render_media_section`, `_render_validation_section`); wired into the `state_present` branch after `run_resolve_keys`, rendered into the context block + the machine-readable JSON payload. Defensive (belt-and-suspenders guards; internally non-fatal) and secret-safe.
- `scripts/wb_orchestrate.py` — **kept the import-guards** (per INST locked decision — see Decisions); refreshed the stale "Wave 1 ships before Wave 2" comments to describe the now-present-but-defensively-guarded reality. Actions 4 + 5 now resolve the real modules and fire (verified, §Ship Verification). No change to the injection field / matcher / skill-directive approach.

**Static-analysis hygiene:**

- `pyrightconfig.json` (NEW, repo root) — `extraPaths: ["scripts", "hooks-handlers", "tests"]` so the runtime-only sibling imports (`import wb_markdown` / `wb_library` / `wb_orchestrate`, and `wb-bootstrap.py`'s `from detector import detect` reuse of `tests/detector.py`) resolve under static pyright.

**Tests (built inline in `tmp_path` — no shipped fixtures, no `.gitignore` exception):**

- `tests/validate-layers/test_wb_validate_layers.py` (25), `tests/imagegen/test_wb_imagegen.py` (12), `tests/videogen/test_wb_videogen.py` (11) → **48 new tests**.
- `tests/orchestration/test_wb_orchestrate.py` — refreshed two now-stale comments (assertions unchanged; still green).

## DoD evidence

**1. Each module's `run()` + resolver unit-tested.** 48 tests across the three modules, all green:

```
validate-layers\test_wb_validate_layers.py .........................     [ 52%]
imagegen\test_wb_imagegen.py ............                                [ 77%]
videogen\test_wb_videogen.py ...........                                 [100%]
============================= 48 passed in 0.32s ==============================
```

Includes resolver tests (gap / consumer-fallback / key-present / key-missing / dotenv / suffix+nested shapes / secret-never-leaks) and `run()`/`run --json` tests for each module.

**2. `session_start` fires the resolvers + validation (rendered summary, secret-safe).** Running `hooks-handlers/session_start.py` against a mid-project fixture (phase 8, `default_language: en`, `languages: [en, de]`, `de.json` missing `cta.subscribe`, keys.yaml with image/video/audio providers, `GEMINI_API_KEY=sk-SECRET-NEVER-PRINT` in env) renders:

```
## Media generation

- Image-gen: consumer-fallback → gemini (env GEMINI_API_KEY: set)
- Video/audio-gen: consumer-fallback → video→runway-gen3 (RUNWAY_API_KEY: MISSING); audio.voice→elevenlabs (ELEVENLABS_API_KEY: MISSING)

## Content-layer validation

- 1 content-layer finding(s) (each carries a fix path):
  - [warning] i18n: content/strings/de.json is missing key `cta.subscribe` (present in en.json). It falls back to the en value at runtime (decision 41). To localize it, add `cta.subscribe` to content/strings/de.json.
```

Secret-leak check (`grep -c "sk-SECRET-NEVER-PRINT"` over the full rendered context): **0** — the resolved secret value never appears.

**3. `validate_content_layers` catches a seeded invalid state with a fix-path.** Seeded: `en.json` has `cta.subscribe`; `de.json` omits it. Output:

```
[warning] i18n: content/strings/de.json is missing key `cta.subscribe` (present in en.json). It falls back to the en value at runtime (decision 41). To localize it, add `cta.subscribe` to content/strings/de.json.
```

Greenfield (only `project.yaml`) returns `[]` (skip-on-absent), so the existing spine test (`proj17` → `validation_errors == []`) stays green.

**4. Spine actions 4+5 fire on phase entry.** `wb_orchestrate.orchestrate_phase_entry(root, 8)` block (the additionalContext payload), with the same seeded fixture, shows both actions firing in one block:

```
# website-builder — phase 8 entry (orchestration spine)
...
## Content-layer validation

- [warning] i18n: content/strings/de.json is missing key `cta.subscribe` (present in en.json). It falls back to the en value at runtime (decision 41). To localize it, add `cta.subscribe` to content/strings/de.json.

## Image generation

- image-gen provider/path: consumer-fallback → gemini (env GEMINI_API_KEY: set)
```

(Action 4 = Content-layer validation; action 5 = Image generation, phase-gated to `IMAGEGEN_PHASES = (8,)`.)

**5. Full `tests/` suite green.** `bash tests/run-tests.sh` (uv + pyyaml + pytest):

```
============================ 413 passed in 12.53s =============================
```

413 = 365 (Wave 1 + corpus) + 48 new.

**6. `npx pyright@latest` — sibling imports now resolve.** Before this INST there was no `pyrightconfig.json`, so static pyright could not resolve the `sys.path.insert`-only sibling imports. With the new config:

```
=== FULL pyright (repo root) ===
0 errors, 0 warnings, 0 informations

=== Targeted: spine + new modules ===
0 errors, 0 warnings, 0 informations
```

0 `reportMissingImports` on the spine (`wb_orchestrate`, `wb_markdown`, `session_start`, `post_tool_use`) + the new modules — and the whole `scripts/` + `hooks-handlers/` gate is clean (including the previously-unresolved `wb-bootstrap.py` `detector` import, fixed by adding `tests` to `extraPaths`).

**7. Ship Verification subsection** — see below.

## Decisions made

- **Import-guards retained (INST locked decision overrides design §8 Wave-2 row).** The design's §8 Wave-2 row says "remove the spine's import-guards once present", but the INST's "Locked decisions — honor" + "Code anchors" both say **KEEP the guards (defensive)**. The INST is the direct contract and the more defensive choice — `except Exception` guards mean a present-but-broken Wave-2 module can never break the spine import. Guards kept; the soft-import comments refreshed to document the retention rationale. (No PAUSE: the INST itself resolves the conflict.)
- **`resolve_imagegen_path` returns a typed `ImagegenPath` with a secret-safe `__str__`** (rather than a bare dict/string). The orchestrator's action 5 does `f"...: {resolved}"`, so `__str__` yields a clean one-liner; the session-start summary uses the structured `to_summary()` fields. Mirrors the wb_keys "resolver returns typed data" pattern while staying f-string-friendly.
- **New modules import `wb_markdown` (the consolidated leaf) for `parse_yaml`** rather than copying the parser a fourth time. `wb_markdown` is the designated parse_yaml home (its docstring says "consolidated here so the fallback parser lives in ONE place"); `wb_orchestrate` already established that new spine modules consume it. `wb_keys`'s own private parse_yaml predates `wb_markdown` and is the "optional Wave-5 dedup" target noted in the spine design. The dotenv reader + keys.yaml path logic are kept self-contained per the "mirror wb_keys (self-contained module)" convention.
- **Skip-on-absent for the validator.** Validating cross-layer references only among files that EXIST is what keeps action 4 quiet on early-phase projects and keeps the existing `proj17` spine test green. An absent source file makes its dependent check a no-op, never an error.
- **Tests build fixtures inline in `tmp_path`** (mirroring `tests/orchestration/`) rather than shipping fixture dirs — zero `.gitignore` churn, zero committed `.website-builder/` fixtures.
- **`tests` added to pyright `extraPaths`** (not `include`) to resolve `wb-bootstrap.py`'s pre-existing `from detector import detect` (reuse of `tests/detector.py`) — drives the whole gate to 0 without type-checking the test files themselves.

## Sub-agents used

None. Executed the packet directly (the wiring step depends on all three modules, and the modules are small + interdependent enough that parallel Lieutenants would add coordination overhead without payoff).

## Follow-ups filed

- **FU-1 (dedup, low priority):** `wb_imagegen.py` + `wb_videogen.py` share ~30 lines of keys.yaml/.env reading + `_extract_provider_key` + `_env_present`. A shared consumer-base helper (or migrating to a common util) is a candidate dedup — consistent with the spine design's "optional Wave-5 dedup" note. Not built now (avoids speculative-pattern-building; the duplication mirrors the established self-contained-module convention).
- **FU-2 (platform path, deferred per decision 56):** the `platform` execution path (Jules-Solutions image/video/audio-gen API) is forward-room only (`PATH_PLATFORM` constant, never returned in v1). Wiring the plugin to consume platform endpoints when those features ship is the deferred follow-up named in the consumer design docs.
- **FU-3 (validator depth):** checks 4/5/6 (sections/components/tokens cross-refs) use tolerant heuristics against the loosely-specified `sections.yaml`/`components.yaml` shapes. If those layer schemas get firmed up (e.g. a SPEC doc), the lookups can be tightened. Check 7 (i18n parity, the DoD case) is precise.

## Ship Verification

Per `dispatch-flow.md` Stage 6 — verbatim evidence that the code is actually wired and running, not merely merged.

**Call-sites (where the new code is invoked):**

- Action 4 → validator: `scripts/wb_orchestrate.py` `_action_validate_layers` calls `validate_content_layers(project_root)`; soft-import at `scripts/wb_orchestrate.py` top (`from wb_validate_layers import validate_content_layers`). Fired by `orchestrate_phase_entry` (every phase) → `run_post_tool_use` / `run_session_start`.
- Action 5 → imagegen: `scripts/wb_orchestrate.py` `_action_imagegen` calls `resolve_imagegen_path(project_root)` (phase-gated to `IMAGEGEN_PHASES = (8,)`); soft-import `from wb_imagegen import resolve_imagegen_path`.
- Session-start summary: `hooks-handlers/session_start.py` `main()` (state_present branch) calls `run_resolve_media(root)` (→ `wb_imagegen.resolve_imagegen_path` + `wb_videogen.resolve_videogen_path`) + `run_validate_layers(root)` (→ `wb_validate_layers.validate_content_layers`); rendered via `render_context(..., media=media, validation=validation)`.
- pyright path: `pyrightconfig.json` at repo root; `extraPaths` includes `scripts`, `hooks-handlers`, `tests`.

**Operational probes (real invocations, pasted above):**

- Phase-8 `orchestrate_phase_entry` block shows `## Content-layer validation` + `## Image generation` populated (DoD evidence #4) — action 4 + action 5 fire on phase entry.
- `session_start.py` subprocess renders `## Media generation` + `## Content-layer validation` (DoD evidence #2) — session-start wiring live, secret-leak count = 0.
- `validate_content_layers` surfaces the seeded `de.json` warning (DoD evidence #3); greenfield → `[]`.
- `bash tests/run-tests.sh` → 413 passed (DoD evidence #5).
- `npx pyright@latest` → 0 errors / 0 warnings (DoD evidence #6).

**Import-guard confirmation:** the guards are present-but-resolving — `wo.validate_content_layers` and `wo.resolve_imagegen_path` are now callables (not `None`), confirmed by `tests/orchestration/test_wb_orchestrate.py::TestImportGuards::test_wave2_modules_guarded` (green within the 413).

## Retro notes

- Caught one real wiring bug via evidence-capture before declaring done: I updated `render_context`'s signature/body but initially missed its **call site** in `main()`, so `media`/`validation` came through as `null`. Re-running the session_start subprocess surfaced it immediately. Lesson reinforced: paste the real rendered output, don't trust "the function exists therefore it's wired."
- The pyright gate surfaced a pre-existing `detector` import error the moment the config included `scripts/` (the file-granularity-ratchet effect from captain memory). Fixed properly via `extraPaths` rather than excluding the file — the whole gate is now genuinely 0, not 0-by-scoping.

## Branch + commit

- Branch: `modules-1` (off `dev`).
- Final commit sha: recorded in my completion message to the General (the commit that includes this RPT).
- Do NOT merge to dev/master — the General reviews + merges to `dev`; master is held through Wave 5.
