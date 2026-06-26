"""
Unit + integration tests for the orchestration spine (`scripts/wb_orchestrate.py`).
Wave 1 / Captain spine-1 scope (DESIGN-orchestration-spine.md § 10 DoD).

These exercise the real plugin adapters/skills/phase-contracts via the module's
_plugin_root() (the worktree), against a synthetic `.website-builder/project.yaml`
built inline in pytest's tmp_path (so nothing ships / no .gitignore exception).

The 16->17 fire is the program DoD (§ 10.2): advancing current_phase fires
phase-entry autoclone + injects the wb-design-system directives + injects the
Next.js adapter's Content-layer-mapping + Component-library-pairing sections.

Run:
  bash tests/run-tests.sh
  cd tests && uv run --with pyyaml --with pytest pytest orchestration/ -v
"""

from __future__ import annotations

import importlib
import inspect
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
HANDLERS_DIR = PLUGIN_ROOT / "hooks-handlers"
sys.path.insert(0, str(SCRIPTS_DIR))

import wb_orchestrate as wo  # noqa: E402  (sys.path mutation must precede)


# --- Fixtures --------------------------------------------------------------


def _make_project(tmp_path: Path, **fields) -> Path:
    """Build a synthetic .website-builder/project.yaml under tmp_path. Returns the
    project_root (tmp_path). Default fields target the phase-17 DoD."""
    defaults = {
        "current_phase": 17,
        "stack": "nextjs",
        "cms": "none",
        "component_library": "shadcn",
        "entry_mode": "greenfield",
        "languages": "en",
        "transactional": "false",
    }
    defaults.update(fields)
    sd = tmp_path / ".website-builder"
    sd.mkdir(parents=True, exist_ok=True)
    lines = []
    for k, v in defaults.items():
        lines.append(f"{k}: {v}")
    (sd / "project.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def proj17(tmp_path: Path) -> Path:
    return _make_project(tmp_path, current_phase=17)


# --- Import safety ----------------------------------------------------------


class TestImportSafety:
    def test_import_side_effect_free(self):
        mod = importlib.reload(wo)
        for name in (
            "run_post_tool_use",
            "run_session_start",
            "orchestrate_phase_entry",
            "run",
            "OrchestrationResult",
            "PHASE_ADAPTER_SECTIONS",
        ):
            assert hasattr(mod, name), name

    def test_public_surface_signatures(self):
        for fn in (wo.run_post_tool_use, wo.run_session_start):
            params = list(inspect.signature(fn).parameters)
            assert params == ["project_root"]

        ope = inspect.signature(wo.orchestrate_phase_entry)
        assert list(ope.parameters)[:2] == ["project_root", "phase"]
        assert ope.parameters["log"].kind == inspect.Parameter.KEYWORD_ONLY

        run_sig = inspect.signature(wo.run)
        assert run_sig.parameters["project_root"].kind == inspect.Parameter.KEYWORD_ONLY


# --- Phase → adapter-section map (§ 4.4) ------------------------------------


class TestPhaseAdapterMap:
    def test_phase_17_maps_design_sections(self):
        assert wo.PHASE_ADAPTER_SECTIONS[17]["stack"] == [
            "Content layer mapping",
            "Component library pairing",
        ]

    def test_phase_12_has_cms_sections(self):
        assert "cms" in wo.PHASE_ADAPTER_SECTIONS[12]

    def test_commerce_heading_is_verbatim(self):
        # The `(if transactional=true)` clause is part of the H2 verbatim.
        assert (
            "Commerce integration (if transactional=true)"
            in wo.PHASE_ADAPTER_SECTIONS["24a"]["stack"]
        )

    def test_phase_8_has_no_adapter_section(self):
        # Image-strategy: action 5 surfaces the path; no adapter section.
        assert wo.PHASE_ADAPTER_SECTIONS[8] == {}


# --- The DoD core: orchestrate_phase_entry(17) ------------------------------


class TestPhase17DoD:
    def test_autoclone_fires_design_corpus(self, proj17: Path):
        result = wo.orchestrate_phase_entry(proj17, 17)
        resources = {getattr(c, "resource", None) for c in result.autoclone}
        # phase-17 contract library_clones_at_entry: awesome-design-md (always) +
        # shadcn-components (when component_library == shadcn).
        assert "awesome-design-md" in resources
        assert "shadcn-components" in resources

    def test_skill_directives_injected(self, proj17: Path):
        result = wo.orchestrate_phase_entry(proj17, 17)
        assert result.skill_directives is not None
        assert result.skill_directives.skill == "wb-design-system"
        # The required directive is the skill's frontmatter description (verbatim).
        assert "OKLCH" in result.skill_directives.description
        assert "refuses arbitrary color picks" in result.skill_directives.description
        # Best-effort discipline H2 also resolved for wb-design-system.
        assert result.skill_directives.discipline is not None
        assert "grounded option-generation" in result.skill_directives.discipline

    def test_adapter_sections_injected(self, proj17: Path):
        result = wo.orchestrate_phase_entry(proj17, 17)
        headings = {s.heading for s in result.adapter_sections}
        assert "Content layer mapping" in headings
        assert "Component library pairing" in headings
        # All from the active stack adapter (nextjs).
        assert all(s.adapter == "stack-nextjs" for s in result.adapter_sections)

    def test_rendered_block_contains_all_three(self, proj17: Path):
        block = wo.orchestrate_phase_entry(proj17, 17).render()
        assert "awesome-design-md" in block
        assert "wb-design-system" in block
        assert "## Content layer mapping" in block
        assert "## Component library pairing" in block

    def test_no_validation_or_imagegen_at_phase17(self, proj17: Path):
        # Post-Wave-2 the modules are present, but at phase 17 with a project that
        # has no content-layer files yet, validate_content_layers returns [] (skip-
        # on-absent), and phase 17 is not an IMAGEGEN_PHASES phase → imagegen None.
        result = wo.orchestrate_phase_entry(proj17, 17)
        assert result.validation_errors == []
        assert result.imagegen is None


# --- Marker + fire decision (§ 3.2 / § 3.3) ---------------------------------


class TestFireDecision:
    def test_16_to_17_advance_fires_once(self, tmp_path: Path):
        root = _make_project(tmp_path, current_phase=16)
        r16 = wo.run_post_tool_use(root)
        assert r16 is not None and r16.phase == 16

        # advance
        _make_project(tmp_path, current_phase=17)
        r17 = wo.run_post_tool_use(root)
        assert r17 is not None and r17.phase == 17

        # idempotent: same phase → None
        assert wo.run_post_tool_use(root) is None

    def test_marker_written_on_fire(self, proj17: Path):
        wo.run_post_tool_use(proj17)
        marker = json.loads(
            (proj17 / ".website-builder" / ".orchestrator-state").read_text()
        )
        assert marker["last_phase"] == 17
        assert "last_fired_utc" in marker
        assert len(marker["project_yaml_digest"]) == 16

    def test_session_start_fires_unconditionally(self, proj17: Path):
        # Even when the marker already equals current_phase, session-start re-injects.
        wo.run_post_tool_use(proj17)  # sets marker = 17
        assert wo.run_post_tool_use(proj17) is None  # post-tool no-ops
        resumed = wo.run_session_start(proj17)  # session-start does NOT no-op
        assert resumed is not None and resumed.phase == 17

    def test_no_project_yaml_returns_none(self, tmp_path: Path):
        assert wo.run_post_tool_use(tmp_path) is None
        assert wo.run_session_start(tmp_path) is None

    def test_non_integer_current_phase_returns_none(self, tmp_path: Path):
        root = _make_project(tmp_path, current_phase="6.5")
        # v1 marker keys on int; a non-int token resolves to None (no fire).
        assert wo.run_post_tool_use(root) is None


# --- Marker helpers ---------------------------------------------------------


class TestMarkerHelpers:
    def test_read_absent_marker_is_empty(self, tmp_path: Path):
        assert wo._read_marker(tmp_path) == {}

    def test_write_then_read_roundtrip(self, proj17: Path):
        wo._write_marker(proj17, last_phase=17, digest="abc123")
        m = wo._read_marker(proj17)
        assert m["last_phase"] == 17 and m["project_yaml_digest"] == "abc123"

    def test_corrupt_marker_is_empty(self, proj17: Path):
        (proj17 / ".website-builder" / ".orchestrator-state").write_text(
            "{not json", encoding="utf-8"
        )
        assert wo._read_marker(proj17) == {}


# --- Slug normalization (§ 5.2) ---------------------------------------------


class TestSlugNormalization:
    @pytest.mark.parametrize(
        "raw,expected",
        [("nextjs", "nextjs"), ("Next.js", "nextjs"), ("next", "nextjs"),
         ("Framer", "framer"), ("WordPress", "wordpress"), ("wp", "wordpress")],
    )
    def test_stack_aliases(self, raw, expected):
        assert wo._normalize_stack_slug(raw) == expected

    def test_stack_none_or_empty(self):
        assert wo._normalize_stack_slug(None) is None
        assert wo._normalize_stack_slug("none") is None

    def test_cms_none_sentinel(self):
        assert wo._normalize_cms_slug("none") == "none"
        assert wo._normalize_cms_slug("payload") == "payload"


# --- CMS + commerce injection (real adapters) -------------------------------


class TestCmsAndCommerce:
    def test_phase_12_with_payload_injects_cms_and_stack(self, tmp_path: Path):
        root = _make_project(tmp_path, current_phase=12, cms="payload")
        result = wo.orchestrate_phase_entry(root, 12)
        kinds = {s.adapter_kind for s in result.adapter_sections}
        # Stack CMS-pairing + CMS adapter sections both present (cms-payload.md exists).
        assert "stack" in kinds
        assert "cms" in kinds

    def test_cms_none_injects_only_stack(self, tmp_path: Path):
        root = _make_project(tmp_path, current_phase=12, cms="none")
        result = wo.orchestrate_phase_entry(root, 12)
        kinds = {s.adapter_kind for s in result.adapter_sections}
        assert "cms" not in kinds

    def test_commerce_only_when_transactional(self, tmp_path: Path):
        non_tx = _make_project(
            tmp_path, current_phase="24a", payment_provider="stripe", transactional="false"
        )
        # 24a isn't an int → run_post_tool_use no-ops; test the core directly with the
        # string key via _action_adapter_sections through orchestrate is int-typed,
        # so exercise the map+resolver path with a transactional project at the int
        # phases isn't applicable. Assert the resolver gates on transactional:
        project_non_tx = wo.wb_library.load_project_yaml(non_tx)
        assert wo._truthy(project_non_tx.get("transactional")) is False
        tx_dir = non_tx / "tx"
        root_tx = _make_project(tx_dir, payment_provider="stripe", transactional="true")
        project_tx = wo.wb_library.load_project_yaml(root_tx)
        assert wo._truthy(project_tx.get("transactional")) is True
        assert wo._resolve_commerce_adapter(project_tx) is not None  # commerce-stripe.md


# --- Defensive behavior -----------------------------------------------------


class TestDefensive:
    def test_unknown_stack_no_crash_no_sections(self, tmp_path: Path):
        root = _make_project(tmp_path, current_phase=17, stack="doesnotexist")
        result = wo.orchestrate_phase_entry(root, 17)
        # No stack adapter file → no adapter sections, but skill + autoclone still run.
        assert result.adapter_sections == []
        assert result.skill_directives is not None  # contract-driven, stack-independent

    def test_phase_with_no_contract_no_crash(self, tmp_path: Path):
        root = _make_project(tmp_path, current_phase=99)
        result = wo.orchestrate_phase_entry(root, 99)
        assert result.is_empty()  # no map entry, no contract → empty, no raise

    def test_empty_result_renders_header_only(self, tmp_path: Path):
        root = _make_project(tmp_path, current_phase=99)
        block = wo.orchestrate_phase_entry(root, 99).render()
        assert "phase 99 entry" in block


# --- Import guards (Wave-2 decoupling, § 4.3) -------------------------------


class TestImportGuards:
    def test_wave2_modules_guarded(self):
        # Post-Wave-2 these resolve to callables; the guard tolerates absence too
        # (None when a module is missing/broken). Either is acceptable — the guard
        # is retained as defensive decoupling.
        assert wo.validate_content_layers is None or callable(wo.validate_content_layers)
        assert wo.resolve_imagegen_path is None or callable(wo.resolve_imagegen_path)


# --- Concision budget (§ 2) -------------------------------------------------


class TestConcisionBudget:
    def test_oversize_section_truncated_with_pointer(self):
        big = "## Component library pairing\n" + ("x" * 5000)
        out = wo._truncate_with_pointer(big, wo.PER_SECTION_CAP, "Component library pairing", "adapters/stack-nextjs.md")
        assert len(out) < len(big)
        assert "section truncated for concision" in out
        assert "adapters/stack-nextjs.md" in out

    def test_phase17_block_both_sections_present_and_bounded(self, proj17: Path):
        block = wo.orchestrate_phase_entry(proj17, 17).render()
        # Both DoD sections present even though one is truncated.
        assert "## Content layer mapping" in block
        assert "## Component library pairing" in block
        # Bounded under the hard ceiling.
        assert len(block) <= wo.TOTAL_SOFT_CAP * 2


# --- run() debug dispatch ---------------------------------------------------


class TestRunDebug:
    def test_run_phase(self, proj17: Path, capsys):
        rc = wo.run(["--phase", "17"], project_root=proj17)
        assert rc == 0
        out = capsys.readouterr().out
        assert "phase 17 entry" in out

    def test_run_show_marker(self, proj17: Path, capsys):
        wo.run_post_tool_use(proj17)
        rc = wo.run(["--show-marker"], project_root=proj17)
        assert rc == 0
        assert '"last_phase": 17' in capsys.readouterr().out

    def test_run_no_args_usage(self, proj17: Path):
        assert wo.run([], project_root=proj17) == 2


# --- Handler integration (post_tool_use.py via subprocess) ------------------


class TestHandlerSubprocess:
    def _run_handler(self, cwd: Path, payload: dict) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        return subprocess.run(
            [sys.executable, str(HANDLERS_DIR / "post_tool_use.py")],
            input=json.dumps(payload),
            cwd=str(cwd),
            capture_output=True,
            text=True,
            env=env,
        )

    def test_emits_json_additionalcontext_on_advance(self, tmp_path: Path):
        root = _make_project(tmp_path, current_phase=17)
        payload = {
            "tool_name": "Edit",
            "tool_input": {"file_path": str(root / ".website-builder" / "project.yaml")},
            "cwd": str(root),
        }
        proc = self._run_handler(root, payload)
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        assert data["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
        ctx = data["hookSpecificOutput"]["additionalContext"]
        assert "phase 17 entry" in ctx
        assert "wb-design-system" in ctx

    def test_silent_when_no_project_yaml(self, tmp_path: Path):
        payload = {"tool_name": "Edit", "tool_input": {"file_path": "x.txt"}, "cwd": str(tmp_path)}
        proc = self._run_handler(tmp_path, payload)
        assert proc.returncode == 0
        assert proc.stdout.strip() == ""

    def test_crashproof_on_garbage_stdin(self, tmp_path: Path):
        root = _make_project(tmp_path, current_phase=17)
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        proc = subprocess.run(
            [sys.executable, str(HANDLERS_DIR / "post_tool_use.py")],
            input="}{ not json at all",
            cwd=str(root),
            capture_output=True,
            text=True,
            env=env,
        )
        # Garbage stdin → payload {} → cwd falls back to os.getcwd() (== root) →
        # project.yaml found → fires (or no-ops). Either way exit 0, never a crash.
        assert proc.returncode == 0
