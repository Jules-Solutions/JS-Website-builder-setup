"""
Wave-5 test-gap closure (Captain verify-1). The five gaps the Wave-5 survey flagged
on top of the Wave-1 isolated 16->17 fire:

  1. Full 5-action integrated path — autoclone + adapter sections + skill directives
     + content-layer validation + image-gen path exercised together, asserting the
     rendered block (phase 17 w/ a seeded invalid layer drives actions 1-4; phase 8
     drives action 5; phase 12 w/ cms=payload drives the CMS adapter binding).
  2. PostToolUse JSON-schema validation — the post_tool_use.py subprocess output is
     STRICTLY validated against the locked envelope shape (§2).
  3. session_start resume subprocess — session_start.py invoked as a subprocess exits
     0 and its PLAIN stdout carries the current-phase orchestration block (the §2
     SessionStart-stdout-enters-context asymmetry).
  4. Multi-phase idempotency — 16->17->18 advance in sequence, each fires once;
     re-firing the same phase is a no-op (marker correctness).

Run:
  cd tests && uv run --with pyyaml --with pytest pytest orchestration/test_e2e_gaps.py -v
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
HANDLERS_DIR = PLUGIN_ROOT / "hooks-handlers"
sys.path.insert(0, str(SCRIPTS_DIR))

import wb_orchestrate as wo  # noqa: E402

GREENFIELD = {
    "stack": "nextjs",
    "cms": "none",
    "component_library": "shadcn",
    "entry_mode": "greenfield",
    "languages": "en",
    "transactional": "false",
}


def _write_project(root: Path, phase: int, **overrides) -> Path:
    fields = dict(GREENFIELD)
    fields.update(overrides)
    fields["current_phase"] = phase
    sd = root / ".website-builder"
    sd.mkdir(parents=True, exist_ok=True)
    body = "\n".join(f"{k}: {v}" for k, v in fields.items()) + "\n"
    (sd / "project.yaml").write_text(body, encoding="utf-8")
    return root


def _seed_invalid_layer(root: Path) -> None:
    """Author a Layer-4 page WITHOUT the required `slug:` frontmatter — Check 2 of
    wb_validate_layers fires a `[error] ... missing the required slug:` finding."""
    pages = root / ".website-builder" / "content" / "pages"
    pages.mkdir(parents=True, exist_ok=True)
    (pages / "home.md").write_text(
        "---\ntitle: Home\n---\n\n# Home\n", encoding="utf-8"
    )


def _child_env() -> dict:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    # Don't let an inherited CLAUDE_PLUGIN_ROOT short-circuit session_start's
    # detection (it only triggers when cwd == CLAUDE_PLUGIN_ROOT, but be explicit).
    env.pop("CLAUDE_PLUGIN_ROOT", None)
    return env


# --- Gap 1: the full 5-action integrated path -------------------------------


class TestFullFiveActionPath:
    def test_phase17_drives_actions_1_through_4(self, tmp_path: Path):
        root = _write_project(tmp_path, 17)
        _seed_invalid_layer(root)
        result = wo.orchestrate_phase_entry(root, 17)

        # action 1 — autoclone
        assert result.autoclone, "action 1 (autoclone) produced nothing"
        # action 2 — adapter sections
        assert result.adapter_sections, "action 2 (adapter sections) produced nothing"
        # action 3 — skill directives
        assert result.skill_directives is not None, "action 3 (skill directives) absent"
        # action 4 — content-layer validation (seeded missing-slug page)
        assert result.validation_errors, "action 4 (validation) produced no finding"
        assert any("slug" in e for e in result.validation_errors)

        block = result.render()
        assert "## Phase-entry resource clones" in block
        assert "## Phase skill" in block
        assert "## Active-adapter sections" in block
        assert "## Content-layer validation" in block

    def test_phase8_drives_action_5_imagegen(self, tmp_path: Path):
        root = _write_project(tmp_path, 8)
        result = wo.orchestrate_phase_entry(root, 8)
        assert result.imagegen is not None, "action 5 (image-gen) produced nothing"
        assert "## Image generation" in result.render()

    def test_phase12_cms_binding_injects_stack_and_cms(self, tmp_path: Path):
        # CMS binding (the General's "add 12 for CMS binding"): cms=payload → both the
        # stack CMS-pairing section AND the cms-payload adapter sections inject.
        root = _write_project(tmp_path, 12, cms="payload")
        result = wo.orchestrate_phase_entry(root, 12)
        kinds = {s.adapter_kind for s in result.adapter_sections}
        assert "stack" in kinds
        assert "cms" in kinds
        assert any(s.adapter == "cms-payload" for s in result.adapter_sections)

    def test_render_composes_all_five_action_sections(self):
        """Deterministic guard: an OrchestrationResult carrying output from all five
        actions renders all five section headers (the render is the integration point
        for the additionalContext payload)."""
        result = wo.OrchestrationResult(
            phase=17,
            autoclone=[SimpleNamespace(
                resource="awesome-design-md", status="fetch-deferred",
                target="awesome-design-md", reason="design corpus",
            )],
            adapter_sections=[wo.InjectedSection(
                adapter="stack-nextjs", adapter_kind="stack",
                heading="Content layer mapping", body="| Layer | x |\n",
                source_path="adapters/stack-nextjs.md", full_len=12,
            )],
            skill_directives=wo.SkillDirectives(
                skill="wb-design-system", description="refuses non-OKLCH color",
                discipline="grounded option-generation",
            ),
            validation_errors=["[error] content/pages/home.md — missing slug:"],
            imagegen=wo.ImagegenStatus(available=True, detail="provider: gemini"),
        )
        block = result.render()
        for header in (
            "## Phase-entry resource clones",
            "## Phase skill",
            "## Active-adapter sections",
            "## Content-layer validation",
            "## Image generation",
        ):
            assert header in block, f"render missing {header}"


# --- Gap 2: PostToolUse JSON-schema validation (strict) ----------------------


class TestPostToolUseJsonSchema:
    def _run_handler(self, root: Path) -> subprocess.CompletedProcess:
        payload = {
            "tool_name": "Edit",
            "tool_input": {"file_path": str(root / ".website-builder" / "project.yaml")},
            "cwd": str(root),
        }
        return subprocess.run(
            [sys.executable, str(HANDLERS_DIR / "post_tool_use.py")],
            input=json.dumps(payload),
            cwd=str(root),
            capture_output=True,
            text=True,
            env=_child_env(),
        )

    def test_emitted_payload_matches_locked_schema_exactly(self, tmp_path: Path):
        root = _write_project(tmp_path, 17)  # no marker → first observation fires
        proc = self._run_handler(root)
        assert proc.returncode == 0, proc.stderr

        # stdout is exactly one JSON object (the handler emits a single line).
        data = json.loads(proc.stdout)
        assert isinstance(data, dict)
        # exact top-level key set — no leakage of stray keys.
        assert set(data.keys()) == {"hookSpecificOutput"}
        hso = data["hookSpecificOutput"]
        assert set(hso.keys()) == {"hookEventName", "additionalContext"}
        # exact literal + types per § 2 (the locked PostToolUse channel).
        assert hso["hookEventName"] == "PostToolUse"
        assert isinstance(hso["additionalContext"], str)
        assert hso["additionalContext"].strip(), "additionalContext is empty"
        assert "phase 17 entry" in hso["additionalContext"]

    def test_no_output_when_phase_unchanged(self, tmp_path: Path):
        root = _write_project(tmp_path, 17)
        first = self._run_handler(root)            # fires (writes marker)
        assert first.returncode == 0 and first.stdout.strip()
        second = self._run_handler(root)           # marker == phase → silent
        assert second.returncode == 0
        assert second.stdout.strip() == ""


# --- Gap 3: session_start resume subprocess ----------------------------------


class TestSessionStartResumeSubprocess:
    def test_resume_emits_phase_block_on_plain_stdout(self, tmp_path: Path):
        root = _write_project(tmp_path, 17)
        proc = subprocess.run(
            [sys.executable, str(HANDLERS_DIR / "session_start.py")],
            input="",
            cwd=str(root),
            capture_output=True,
            encoding="utf-8",  # session_start emits UTF-8 bytes (em-dashes); decode faithfully
            errors="replace",
            env=_child_env(),
        )
        assert proc.returncode == 0, proc.stderr
        out = proc.stdout
        # SessionStart's plain stdout enters context (§2) — the orchestration block is
        # appended verbatim, NOT JSON-wrapped (unlike PostToolUse).
        assert "# website-builder — session context" in out
        assert "# website-builder — phase 17 entry (orchestration spine)" in out
        # the resume re-injects the design-system skill + adapter sections too.
        assert "wb-design-system" in out
        assert "## Component library pairing" in out

    def test_resume_reconciles_marker(self, tmp_path: Path):
        root = _write_project(tmp_path, 17)
        subprocess.run(
            [sys.executable, str(HANDLERS_DIR / "session_start.py")],
            input="", cwd=str(root), capture_output=True,
            encoding="utf-8", errors="replace", env=_child_env(),
        )
        # session_start.run_session_start writes last_phase = current_phase.
        assert wo._read_marker(root)["last_phase"] == 17


# --- Gap 4: multi-phase idempotency 16 -> 17 -> 18 ---------------------------


class TestMultiPhaseIdempotency:
    def test_sequence_fires_once_each_no_refire(self, tmp_path: Path):
        root = tmp_path
        for phase in (16, 17, 18):
            _write_project(root, phase)
            fired = wo.run_post_tool_use(root)
            assert fired is not None and fired.phase == phase, f"phase {phase} didn't fire"
            # re-firing the SAME phase is a no-op (the marker is authoritative).
            assert wo.run_post_tool_use(root) is None, f"phase {phase} re-fired"
            assert wo._read_marker(root)["last_phase"] == phase

    def test_session_start_refires_at_settled_phase(self, tmp_path: Path):
        # Contrast with post-tool-use: session-start re-injects unconditionally even
        # when the marker already equals current_phase (resume lost its context window).
        root = _write_project(tmp_path, 18)
        assert wo.run_post_tool_use(root) is not None       # first advance fires
        assert wo.run_post_tool_use(root) is None           # post-tool no-ops
        resumed = wo.run_session_start(root)                # session-start does NOT
        assert resumed is not None and resumed.phase == 18
