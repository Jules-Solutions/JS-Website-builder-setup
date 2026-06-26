"""
tests/claudemd/test_wb_claudemd.py — Wave 3a (Captain wiring-1) tests for the
project-root CLAUDE.md orientation surface (gap #2 — DESIGN-orchestration-spine.md
§7 row #2 + §9, Commander CONFIRMED).

Covers:
  TestManagedBlock — pure-function unit tests of scripts/wb_claudemd.py (render,
    upsert, identity extraction, idempotency / determinism).
  TestBootstrapWritesClaudemd — scripts/wb-bootstrap.py (subprocess) writes a
    project-root CLAUDE.md carrying the expected orientation sections, idempotently,
    without clobbering a user-authored CLAUDE.md.
  TestSpineRefreshesPhaseLine — advancing the phase refreshes the managed block's
    phase line via wb_orchestrate.run_post_tool_use / run_session_start.
  TestSpineDefensive — the spine never CREATES the file, never touches a CLAUDE.md
    with no managed block, and never crashes.

All Tier 1 — no network, no real CC dir. Every test writes only into a tmp project
dir; nothing touches the plugin repo's own CLAUDE.md.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import wb_claudemd as wc  # noqa: E402  (sys.path mutation must precede)
import wb_orchestrate as wo  # noqa: E402


# --- helpers ----------------------------------------------------------------


def _make_project(root: Path, **fields) -> Path:
    """Write a flat .website-builder/project.yaml under `root`. Returns `root`."""
    defaults = {
        "name": "acme-co",
        "slug": "acme-co",
        "current_phase": 11,
        "stack": "nextjs",
        "cms": "none",
    }
    defaults.update(fields)
    sd = root / ".website-builder"
    sd.mkdir(parents=True, exist_ok=True)
    lines = [f"{k}: {v}" for k, v in defaults.items()]
    (sd / "project.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return root


def _run_bootstrap(args: list[str], *, cwd: Path) -> tuple[int, str, str]:
    """Invoke scripts/wb-bootstrap.py via this interpreter (mirrors the post-launch
    + smoke-test subprocess pattern)."""
    runner = SCRIPTS_DIR / "wb-bootstrap.py"
    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(PLUGIN_ROOT)}
    proc = subprocess.run(
        [sys.executable, str(runner), *args],
        capture_output=True, text=True, cwd=str(cwd), env=env, timeout=120,
    )
    return proc.returncode, proc.stdout, proc.stderr


# --- TestManagedBlock (pure unit) -------------------------------------------


class TestManagedBlock:
    def test_render_contains_markers_and_identity(self):
        block = wc.render_managed_block(
            project_name="acme-co", current_phase="11", stack="nextjs", cms="none"
        )
        assert wc.MANAGED_BEGIN in block
        assert wc.MANAGED_END in block
        assert "acme-co" in block
        assert "**Current phase:** 11" in block
        assert "**Stack:** nextjs" in block
        assert "**CMS:** none" in block
        assert "## How to resume" in block
        assert ".website-builder/" in block

    def test_render_is_deterministic(self):
        kw = dict(project_name="x", current_phase="2", stack="astro", cms="decap")
        assert wc.render_managed_block(**kw) == wc.render_managed_block(**kw)

    def test_upsert_absent_returns_block_alone(self):
        block = wc.render_managed_block(
            project_name="x", current_phase="0", stack="(not yet chosen)", cms="(not yet chosen)"
        )
        out = wc.upsert_managed_block(None, block)
        assert out.strip().startswith(wc.MANAGED_BEGIN)
        assert out.endswith("\n")
        assert out.count(wc.MANAGED_BEGIN) == 1

    def test_upsert_replaces_in_place_preserving_user_content(self):
        block_v1 = wc.render_managed_block(
            project_name="x", current_phase="0", stack="a", cms="none"
        )
        existing = (
            "# My own notes\n\nKeep this above.\n\n"
            + block_v1
            + "\n## Below\n\nKeep this below too.\n"
        )
        block_v2 = wc.render_managed_block(
            project_name="x", current_phase="11", stack="a", cms="none"
        )
        out = wc.upsert_managed_block(existing, block_v2)
        # User content (above + below) preserved.
        assert "Keep this above." in out
        assert "Keep this below too." in out
        # Exactly one managed block; the phase line was updated.
        assert out.count(wc.MANAGED_BEGIN) == 1
        assert out.count(wc.MANAGED_END) == 1
        assert "**Current phase:** 11" in out
        assert "**Current phase:** 0" not in out

    def test_upsert_appends_when_no_block(self):
        existing = "# User CLAUDE.md\n\nMy project rules.\n"
        block = wc.render_managed_block(
            project_name="x", current_phase="3", stack="a", cms="b"
        )
        out = wc.upsert_managed_block(existing, block)
        assert "My project rules." in out  # user content preserved
        assert out.count(wc.MANAGED_BEGIN) == 1  # block appended once
        assert "**Current phase:** 3" in out

    def test_upsert_idempotent_on_repeat(self):
        block = wc.render_managed_block(
            project_name="x", current_phase="3", stack="a", cms="b"
        )
        once = wc.upsert_managed_block(None, block)
        twice = wc.upsert_managed_block(once, block)
        assert once == twice  # re-applying the same block is a no-op

    def test_identity_fallbacks(self):
        ident = wc._identity_from_project(
            {"name": "", "slug": "", "current_phase": 0, "stack": None, "cms": None}
        )
        assert ident["project_name"] == "(project name set at phase 1)"
        assert ident["current_phase"] == "0"
        assert ident["stack"] == "(not yet chosen)"
        assert ident["cms"] == "(not yet chosen)"

    def test_identity_prefers_name_then_slug(self):
        assert wc._identity_from_project({"name": "Real Name", "slug": "s"})["project_name"] == "Real Name"
        assert wc._identity_from_project({"name": "", "slug": "the-slug"})["project_name"] == "the-slug"

    def test_fmt_choice_shows_cms_none_verbatim(self):
        # 'none' is a legitimate CMS choice (no CMS) — shown verbatim, not as unchosen.
        assert wc._fmt_choice("none") == "none"
        assert wc._fmt_choice(None) == "(not yet chosen)"
        assert wc._fmt_choice("null") == "(not yet chosen)"


# --- TestBootstrapWritesClaudemd (subprocess) -------------------------------


class TestBootstrapWritesClaudemd:
    @pytest.fixture
    def greenfield(self):
        d = Path(tempfile.mkdtemp(prefix="wb-claudemd-bootstrap-"))
        try:
            yield d
        finally:
            import shutil
            shutil.rmtree(d, ignore_errors=True)

    def test_bootstrap_writes_project_claudemd(self, greenfield):
        rc, out, err = _run_bootstrap([], cwd=greenfield)
        assert rc == 0, f"bootstrap exited {rc}\n{out}\n{err}"
        # The .website-builder scaffold AND the project-root CLAUDE.md both exist.
        assert (greenfield / ".website-builder" / "project.yaml").is_file()
        claudemd = greenfield / "CLAUDE.md"
        assert claudemd.is_file(), "bootstrap must write a project-root CLAUDE.md"
        text = claudemd.read_text(encoding="utf-8")
        assert wc.MANAGED_BEGIN in text and wc.MANAGED_END in text
        assert "## How to resume" in text
        assert "Current phase:" in text
        assert "Stack:" in text
        assert "CMS:" in text
        assert ".website-builder/" in text

    def test_bootstrap_claudemd_idempotent_rerun(self, greenfield):
        rc1, _, _ = _run_bootstrap([], cwd=greenfield)
        assert rc1 == 0
        first = (greenfield / "CLAUDE.md").read_text(encoding="utf-8")
        rc2, out2, err2 = _run_bootstrap(["--force"], cwd=greenfield)
        assert rc2 == 0, f"re-run exited {rc2}\n{err2}"
        second = (greenfield / "CLAUDE.md").read_text(encoding="utf-8")
        # Exactly one managed block survives a re-run (no duplication).
        assert second.count(wc.MANAGED_BEGIN) == 1
        # Deterministic block → identical bytes on an unchanged-identity re-run.
        assert first == second

    def test_bootstrap_preserves_user_authored_claudemd(self, greenfield):
        user = greenfield / "CLAUDE.md"
        user.write_text("# My project\n\nMy own rules the agent must follow.\n", encoding="utf-8")
        rc, out, err = _run_bootstrap([], cwd=greenfield)
        assert rc == 0, f"bootstrap exited {rc}\n{err}"
        text = user.read_text(encoding="utf-8")
        # User content preserved; managed block appended.
        assert "My own rules the agent must follow." in text
        assert wc.MANAGED_BEGIN in text
        assert text.count(wc.MANAGED_BEGIN) == 1


# --- TestSpineRefreshesPhaseLine (wb_orchestrate integration) ---------------


class TestSpineRefreshesPhaseLine:
    def _seed_claudemd_at_phase(self, root: Path, phase: int) -> str:
        """Seed a project-root CLAUDE.md managed block at a given phase (simulates the
        bootstrap-time state before the spine advances it). Returns the seeded text."""
        wc.write_project_claudemd(root, {
            "name": "acme-co", "slug": "acme-co",
            "current_phase": phase, "stack": "nextjs", "cms": "none",
        })
        return (root / "CLAUDE.md").read_text(encoding="utf-8")

    def test_post_tool_use_refreshes_phase_line(self, tmp_path: Path):
        root = _make_project(tmp_path, current_phase=11)
        before = self._seed_claudemd_at_phase(root, 0)
        assert "**Current phase:** 0" in before

        result = wo.run_post_tool_use(root)  # project.yaml says phase 11 → fires
        assert result is not None and result.phase == 11

        after = (root / "CLAUDE.md").read_text(encoding="utf-8")
        assert "**Current phase:** 11" in after
        assert "**Current phase:** 0" not in after
        # Still exactly one managed block.
        assert after.count(wc.MANAGED_BEGIN) == 1

    def test_session_start_refreshes_phase_line(self, tmp_path: Path):
        root = _make_project(tmp_path, current_phase=17)
        self._seed_claudemd_at_phase(root, 0)
        resumed = wo.run_session_start(root)
        assert resumed is not None and resumed.phase == 17
        after = (root / "CLAUDE.md").read_text(encoding="utf-8")
        assert "**Current phase:** 17" in after

    def test_refresh_picks_up_stack_choice(self, tmp_path: Path):
        # Seed at phase 0 with no stack; advance to a phase where stack is picked.
        root = _make_project(tmp_path, current_phase=11, stack="astro", cms="none")
        wc.write_project_claudemd(root, {
            "name": "acme-co", "slug": "acme-co",
            "current_phase": 0, "stack": None, "cms": None,
        })
        before = (root / "CLAUDE.md").read_text(encoding="utf-8")
        assert "**Stack:** (not yet chosen)" in before
        wo.run_post_tool_use(root)
        after = (root / "CLAUDE.md").read_text(encoding="utf-8")
        assert "**Stack:** astro" in after

    def test_refresh_unchanged_when_identity_matches(self, tmp_path: Path):
        root = _make_project(tmp_path, current_phase=11)
        self._seed_claudemd_at_phase(root, 11)  # already at phase 11
        before = (root / "CLAUDE.md").read_text(encoding="utf-8")
        wo.run_session_start(root)  # fires, but identity already matches
        after = (root / "CLAUDE.md").read_text(encoding="utf-8")
        assert before == after  # deterministic block → no churn


# --- TestSpineDefensive -----------------------------------------------------


class TestSpineDefensive:
    def test_spine_never_creates_claudemd(self, tmp_path: Path):
        root = _make_project(tmp_path, current_phase=11)
        # No CLAUDE.md present.
        result = wo.run_post_tool_use(root)
        assert result is not None  # the spine still fires its injection
        assert not (root / "CLAUDE.md").exists(), \
            "the spine must NOT create CLAUDE.md (only bootstrap creates it)"

    def test_spine_leaves_unmanaged_claudemd_untouched(self, tmp_path: Path):
        root = _make_project(tmp_path, current_phase=11)
        user = root / "CLAUDE.md"
        original = "# Hand-written\n\nNo managed block here.\n"
        user.write_text(original, encoding="utf-8")
        wo.run_post_tool_use(root)
        assert user.read_text(encoding="utf-8") == original, \
            "the spine must not inject a block into a user-authored CLAUDE.md"

    def test_refresh_with_none_project_is_noop(self, tmp_path: Path):
        assert wc.refresh_project_claudemd(tmp_path, None) is None

    def test_refresh_absent_file_is_noop(self, tmp_path: Path):
        assert wc.refresh_project_claudemd(tmp_path, {"current_phase": 5}) is None
