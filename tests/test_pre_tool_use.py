"""
Phase 2.C — PreToolUse anti-skip gating tests.

Auto-discovered by pytest (per tests/pyproject.toml
`python_files = ["smoke_test.py", "test_*.py"]`). Does NOT touch the shared
TestHookIntegration harness in smoke_test.py — that exercises the SessionStart
hook and must stay 5/5 green; this file is a separate module exercising the
PreToolUse hook only.

Each test invokes `hooks-handlers/pre_tool_use.py` as a subprocess with:
  * a synthesized PreToolUse JSON payload on stdin,
  * `CLAUDE_PLUGIN_ROOT` set to the real plugin root (so the hook can read the
    38 phase contracts for the block rationale + locate skip-decision files),
  * cwd = a tempdir holding a synthetic `.website-builder/` project state,
matching the exact invocation contract the SessionStart harness uses
(cwd-not-argv; the hook reads Path.cwd() and CLAUDE_PLUGIN_ROOT per the CC
spec) and matching how Claude Code actually fires the hook.

The CC contract verified via context7 /anthropics/claude-code (2026-05-19):
ALLOW = exit 0 (+ optional JSON permissionDecision=allow on stdout);
BLOCK = JSON permissionDecision=deny on stdout AND exit 2 with the reason on
stderr (dual-emit for compatibility). Tests assert on both surfaces.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parent.parent.resolve()
HOOK = PLUGIN_ROOT / "hooks-handlers" / "pre_tool_use.py"


# --- helpers --------------------------------------------------------------- #


def _make_project(
    *,
    state: bool = True,
    current_phase: str | None = "1",
    skip_files: list[str] | None = None,
) -> Path:
    """Build a tempdir holding a synthetic user project.

    state=False        → no `.website-builder/` at all (pre-bootstrap).
    current_phase=None  → `.website-builder/project.yaml` exists but has no
                          `current_phase:` line (degraded state).
    skip_files          → names to create under `.website-builder/decisions/`
                          (e.g. ["skip-phase-21.md"]).
    """
    tmp = Path(tempfile.mkdtemp(prefix="wb-ptu-test-"))
    if state:
        sd = tmp / ".website-builder"
        sd.mkdir()
        lines = ["name: Test Site", "slug: test-site", "entry_mode: greenfield"]
        if current_phase is not None:
            lines.append(f"current_phase: {current_phase}")
        (sd / "project.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")
        if skip_files:
            ddir = sd / "decisions"
            ddir.mkdir()
            for name in skip_files:
                (ddir / name).write_text(
                    "---\ntype: decision\nchosen: skip\n---\nuser authorized.\n",
                    encoding="utf-8",
                )
    return tmp


def _run(project: Path, payload: dict) -> subprocess.CompletedProcess:
    """Invoke the PreToolUse hook the way CC does: payload on stdin,
    CLAUDE_PLUGIN_ROOT in env, cwd = the project dir."""
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={**os.environ, "CLAUDE_PLUGIN_ROOT": str(PLUGIN_ROOT)},
        cwd=str(project),
        timeout=30,
    )


def _decision(proc: subprocess.CompletedProcess) -> str | None:
    """Pull hookSpecificOutput.permissionDecision out of stdout if present."""
    out = (proc.stdout or "").strip()
    if not out:
        return None
    # stdout may carry the JSON object; tolerate trailing newline / single obj
    try:
        obj = json.loads(out)
    except json.JSONDecodeError:
        # last non-empty line might be the JSON (defensive)
        for line in reversed(out.splitlines()):
            line = line.strip()
            if line.startswith("{"):
                try:
                    obj = json.loads(line)
                    break
                except json.JSONDecodeError:
                    continue
        else:
            return None
    hso = obj.get("hookSpecificOutput") if isinstance(obj, dict) else None
    if isinstance(hso, dict):
        return hso.get("permissionDecision")
    return None


def _assert_allow(proc: subprocess.CompletedProcess) -> None:
    assert proc.returncode == 0, (
        f"expected ALLOW (exit 0); got {proc.returncode}\n"
        f"stdout={proc.stdout!r}\nstderr={proc.stderr!r}"
    )
    dec = _decision(proc)
    # ALLOW is either a silent exit-0 (no stdout) or an explicit allow JSON.
    assert dec in (None, "allow"), f"expected allow/silent; got decision={dec!r}"


def _assert_block(proc: subprocess.CompletedProcess) -> None:
    # Dual-emit contract: exit 2 + reason on stderr + deny JSON on stdout.
    assert proc.returncode == 2, (
        f"expected BLOCK (exit 2); got {proc.returncode}\n"
        f"stdout={proc.stdout!r}\nstderr={proc.stderr!r}"
    )
    assert _decision(proc) == "deny", (
        f"expected permissionDecision=deny on stdout; stdout={proc.stdout!r}"
    )
    assert proc.stderr.strip(), "expected a block reason on stderr"


# --- payload factories ----------------------------------------------------- #


def _edit(path: str) -> dict:
    return {"tool_name": "Edit", "tool_input": {"file_path": path}}


def _write(path: str) -> dict:
    return {"tool_name": "Write", "tool_input": {"file_path": path}}


def _bash(cmd: str) -> dict:
    return {"tool_name": "Bash", "tool_input": {"command": cmd}}


def _ask() -> dict:
    return {"tool_name": "AskUserQuestion", "tool_input": {"questions": []}}


# --------------------------------------------------------------------------- #
# Case 1 — pre-bootstrap (no .website-builder/) → ALLOW
# --------------------------------------------------------------------------- #


class TestPreToolUseGating:
    """The 7 cases the INST mandates, plus the 1→3 walk demonstration."""

    def test_case1_pre_bootstrap_allows(self):
        proj = _make_project(state=False)
        try:
            proc = _run(proj, _write("src/app/page.tsx"))
            _assert_allow(proc)
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    # ---- Case 2 — degraded state (project.yaml, no current_phase) → ALLOW -- #

    def test_case2_degraded_state_soft_allows(self):
        proj = _make_project(current_phase=None)
        try:
            proc = _run(proj, _edit("src/components/Hero.tsx"))
            _assert_allow(proc)
            # soft-allow must surface an advisory systemMessage
            obj = json.loads(proc.stdout.strip())
            assert "current_phase" in obj.get("systemMessage", "")
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    # ---- Case 3 — tool authorized at current phase → ALLOW ---------------- #

    def test_case3a_phase1_askuserquestion_allows(self):
        proj = _make_project(current_phase="1")
        try:
            _assert_allow(_run(proj, _ask()))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    def test_case3b_phase1_write_project_yaml_allows(self):
        proj = _make_project(current_phase="1")
        try:
            # Write to .website-builder/project.yaml is state-write — allowed
            # at phase 1 (the contract's own output artifact).
            _assert_allow(_run(proj, _write(".website-builder/project.yaml")))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    # ---- Case 4 — downstream tool at upstream phase → BLOCK --------------- #

    def test_case4a_phase5_edit_tsx_blocked_code_gated_to_18(self):
        proj = _make_project(current_phase="5")
        try:
            proc = _run(proj, _edit("src/components/foo.tsx"))
            _assert_block(proc)
            assert "phase 18" in proc.stderr or "phase 18" in proc.stdout
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    def test_case4b_phase1_write_codefile_blocked(self):
        proj = _make_project(current_phase="1")
        try:
            # Writing a real source file at phase 1 (a phase-18 artifact) is the
            # canonical forward-skip the hook exists to refuse.
            proc = _run(proj, _write("app/page.tsx"))
            _assert_block(proc)
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    def test_case4c_phase14_build_command_blocked(self):
        proj = _make_project(current_phase="14")
        try:
            # `npm run build` is build-deploy — gated until phase 19.
            proc = _run(proj, _bash("npm run build"))
            _assert_block(proc)
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    # ---- Case 5 — phase 6.5 side-channel → ALLOW even for its tools ------- #

    def test_case5a_phase_6_5_is_current_never_blocks(self):
        proj = _make_project(current_phase="6.5")
        try:
            # Even a state-write at 6.5 (its ingestion target) is allowed; the
            # side-channel never blocks the agent from advancing.
            _assert_allow(_run(proj, _write(".website-builder/brand.yaml")))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    def test_case5b_phase_6_5_playwright_allowed(self):
        proj = _make_project(current_phase="6.5")
        try:
            payload = {
                "tool_name": "mcp__playwright__browser_navigate",
                "tool_input": {"url": "https://example.com"},
            }
            _assert_allow(_run(proj, payload))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    # ---- Case 6 — skip-decision override → ALLOW with notice ------------- #

    def test_case6_skip_decision_file_overrides_block(self):
        proj = _make_project(
            current_phase="21", skip_files=["skip-phase-21.md"]
        )
        try:
            # At phase 21, code-write would normally be authorized (21 is in
            # build-integration). To prove the override path we attempt a
            # build-deploy at a phase that authorizes it AND a true upstream
            # skip: use phase 14 + skip-phase-14.md instead.
            proj2 = _make_project(
                current_phase="14", skip_files=["skip-phase-14.md"]
            )
            try:
                proc = _run(proj2, _edit("src/components/Hero.tsx"))
                _assert_allow(proc)
                obj = json.loads(proc.stdout.strip())
                assert "skip-phase-14.md" in obj.get("systemMessage", "")
            finally:
                shutil.rmtree(proj2, ignore_errors=True)
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    # ---- Case 7 — authorized-at-current for a mid-pipeline phase → ALLOW -- #

    def test_case7_phase18_edit_tsx_allows(self):
        proj = _make_project(current_phase="18")
        try:
            # Phase 18 is THE codegen gate — code-write is authorized here.
            _assert_allow(_run(proj, _edit("src/components/Hero.tsx")))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    def test_case7b_phase19_build_allows(self):
        proj = _make_project(current_phase="19")
        try:
            _assert_allow(_run(proj, _bash("pnpm run build")))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    # ---- DoD demonstration: walk current_phase 1 → 2 → 3 ----------------- #

    def test_dod_walk_1_to_3_allows_in_phase_blocks_forward_skip(self):
        """With current_phase walking 1→2→3: the hook ALLOWs in-phase tools
        (AskUserQuestion, state-write) and BLOCKs every forward-skip attempt
        (code-write / build) at each of the three phases."""
        for phase in ("1", "2", "3"):
            proj = _make_project(current_phase=phase)
            try:
                # in-phase tools allowed
                _assert_allow(_run(proj, _ask()))
                _assert_allow(
                    _run(proj, _write(".website-builder/project.yaml"))
                )
                # forward-skip attempts blocked
                _assert_block(_run(proj, _write("src/app/page.tsx")))
                _assert_block(_run(proj, _bash("next build")))
            finally:
                shutil.rmtree(proj, ignore_errors=True)

    # ---- robustness: malformed payload must not brick (fails open) ------- #

    def test_malformed_payload_fails_open(self):
        proj = _make_project(current_phase="1")
        try:
            proc = subprocess.run(
                [sys.executable, str(HOOK)],
                input="not json at all",
                capture_output=True,
                text=True,
                env={**os.environ, "CLAUDE_PLUGIN_ROOT": str(PLUGIN_ROOT)},
                cwd=str(proj),
                timeout=30,
            )
            # empty/invalid payload → empty tool_name → unknown class → ALLOW;
            # the hook must never brick the session.
            assert proc.returncode == 0
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    def test_unknown_tool_allows(self):
        proj = _make_project(current_phase="1")
        try:
            payload = {"tool_name": "SomeFutureTool", "tool_input": {}}
            _assert_allow(_run(proj, payload))
        finally:
            shutil.rmtree(proj, ignore_errors=True)
