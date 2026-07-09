"""
Tier-1 tests for the fresh-path subproject scan in hooks-handlers/session_start.py.

Entry-routing change: when the cwd has NO `.website-builder/` state, the hook now
scans BELOW the cwd (bounded: depth + result count) for existing website-builder
projects, so the agent routes the user to an existing project ("which project is
today's focus?") instead of proposing a fresh bootstrap next to existing ones.

Covered here:
  - find_subprojects(): finds projects at several depths, reads name/slug/phase
    from their project.yaml, skips heavy/dot dirs, respects the depth bound, and
    does not descend INTO a found project.
  - render_context(): fresh path renders the `## Website-builder projects found
    below this directory` section (single- vs multi-project wording) and carries
    `subprojects` in the machine-readable JSON; mid-project path carries null and
    renders no such section; fresh-with-none carries [] and instructs the agent
    to ASK before bootstrapping.
  - End-to-end subprocess (isolated HOME, mirrors test_session_start_wiring.py):
    hook exits 0 on an umbrella dir with two projects below and emits the section
    + JSON.

Like test_session_start_wiring.py, all state is built synthetically in tmp_path —
the repo .gitignore ignores `.website-builder/` dirs, so a committed fixture
would be silently swallowed.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Make hooks-handlers/session_start.py importable regardless of pytest's cwd
# (mirrors test_session_start_wiring.py).
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
HOOKS_HANDLERS = PLUGIN_ROOT / "hooks-handlers"
sys.path.insert(0, str(HOOKS_HANDLERS))

import session_start as ss  # noqa: E402  (sys.path mutation must precede)


# --- Synthetic-tree helpers --------------------------------------------------


def _make_project(root: Path, rel: str, *, name: str, phase: str = "17") -> Path:
    """Create <root>/<rel>/.website-builder/project.yaml with minimal scalars."""
    proj = root / rel
    sd = proj / ".website-builder"
    sd.mkdir(parents=True)
    (sd / "project.yaml").write_text(
        f'version: 1\nname: "{name}"\nslug: "{name.lower()}"\n'
        f"entry_mode: greenfield\ncurrent_phase: {phase}\n",
        encoding="utf-8",
    )
    return proj


SECTION_HEADING = "## Website-builder projects found below this directory"


# --- find_subprojects() unit tests -------------------------------------------


class TestFindSubprojects:
    def test_finds_projects_at_multiple_depths_with_state_fields(self, tmp_path):
        _make_project(tmp_path, "alpha", name="Alpha", phase="30")
        _make_project(tmp_path, "clients/beta", name="Beta", phase="9")

        found = ss.find_subprojects(tmp_path)

        assert [(p["name"], p["current_phase"]) for p in found] == [
            ("Alpha", "30"),
            ("Beta", "9"),
        ]
        assert found[0]["path"] == "alpha"
        assert found[0]["slug"] == "alpha"
        assert found[1]["path"] == str(Path("clients") / "beta")

    def test_empty_tree_returns_empty_list(self, tmp_path):
        (tmp_path / "docs").mkdir()
        assert ss.find_subprojects(tmp_path) == []

    def test_skips_heavy_and_dot_dirs(self, tmp_path):
        _make_project(tmp_path, "node_modules/sneaky", name="Sneaky")
        _make_project(tmp_path, ".hidden/nested", name="Hidden")
        _make_project(tmp_path, "real", name="Real")

        found = ss.find_subprojects(tmp_path)
        assert [p["name"] for p in found] == ["Real"]

    def test_respects_depth_bound(self, tmp_path):
        # Depth 4 = a/b/c/deep is reachable; a/b/c/d/toodeep is not.
        _make_project(tmp_path, "a/b/c/deep", name="Deep")
        _make_project(tmp_path, "a/b/c/d/toodeep", name="TooDeep")

        names = {p["name"] for p in ss.find_subprojects(tmp_path)}
        assert names == {"Deep"}

    def test_does_not_descend_into_a_found_project(self, tmp_path):
        outer = _make_project(tmp_path, "outer", name="Outer")
        _make_project(outer, "inner", name="Inner")  # nested inside a project

        names = {p["name"] for p in ss.find_subprojects(tmp_path)}
        assert names == {"Outer"}

    def test_result_count_is_bounded(self, tmp_path):
        for i in range(ss.SUBPROJECT_SCAN_MAX_RESULTS + 5):
            _make_project(tmp_path, f"p{i:02d}", name=f"P{i:02d}")

        found = ss.find_subprojects(tmp_path)
        assert len(found) == ss.SUBPROJECT_SCAN_MAX_RESULTS

    def test_unreadable_project_yaml_falls_back_to_dirname(self, tmp_path):
        proj = tmp_path / "broken"
        (proj / ".website-builder").mkdir(parents=True)
        (proj / ".website-builder" / "project.yaml").write_bytes(b"\xff\xfe\x00broken")

        found = ss.find_subprojects(tmp_path)
        assert len(found) == 1
        assert found[0]["name"] == "broken"
        assert found[0]["current_phase"] == "?"


# --- render_context() tests ---------------------------------------------------


def _fresh_entry() -> dict:
    return {"mode": "ambiguous", "signal": "test"}


def _payload(context: str) -> dict:
    m = re.search(r"```json\s*\n(\{[\s\S]*?\})\s*\n```", context)
    assert m, "machine-readable JSON block missing"
    return json.loads(m.group(1))


class TestRenderContextSubprojects:
    def test_multi_project_section_and_json(self, tmp_path):
        subs = [
            {"path": "alpha", "name": "Alpha", "slug": "alpha", "current_phase": "30"},
            {"path": "beta", "name": "Beta", "slug": "beta", "current_phase": "9"},
        ]
        context = ss.render_context(
            root=tmp_path,
            state_present=False,
            entry=_fresh_entry(),
            project=None,
            subprojects=subs,
        )
        assert SECTION_HEADING in context
        assert "**Alpha**" in context and "(current phase: 30)" in context
        assert "which project is today's focus" in context
        assert "Do NOT bootstrap" in context
        assert _payload(context)["subprojects"] == subs

    def test_single_project_wording(self, tmp_path):
        subs = [{"path": "alpha", "name": "Alpha", "slug": "alpha", "current_phase": "30"}]
        context = ss.render_context(
            root=tmp_path,
            state_present=False,
            entry=_fresh_entry(),
            project=None,
            subprojects=subs,
        )
        assert SECTION_HEADING in context
        assert "one project exists below it" in context
        assert "Do NOT bootstrap" in context

    def test_fresh_with_no_subprojects_instructs_ask_before_bootstrap(self, tmp_path):
        context = ss.render_context(
            root=tmp_path,
            state_present=False,
            entry={"mode": "greenfield", "signal": "empty"},
            project=None,
            subprojects=[],
        )
        assert SECTION_HEADING not in context
        assert "ASK whether a new project" in context
        assert _payload(context)["subprojects"] == []

    def test_mid_project_carries_null_and_no_section(self, tmp_path):
        context = ss.render_context(
            root=tmp_path,
            state_present=True,
            entry={"mode": "mid-project", "signal": "state"},
            project={"current_phase": "17"},
            subprojects=None,
        )
        assert SECTION_HEADING not in context
        assert _payload(context)["subprojects"] is None


# --- End-to-end subprocess test (isolated HOME) --------------------------------


def _isolated_env(tmp_path: Path) -> dict[str, str]:
    """Isolated HOME so no real ~/.op / 1Password session is reachable (mirrors
    test_session_start_wiring.py). The fresh path never runs the keys module,
    but belt-and-suspenders costs nothing."""
    env = {**os.environ}
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    env["HOME"] = str(home)
    env["USERPROFILE"] = str(home)
    env["WB_OP_BIN"] = "wb-nonexistent-op-binary"
    return env


class TestHookSubprocessSubprojects:
    def test_umbrella_dir_with_two_projects(self, tmp_path):
        umbrella = tmp_path / "umbrella"
        umbrella.mkdir()
        _make_project(umbrella, "alpha", name="Alpha", phase="30")
        _make_project(umbrella, "clients/beta", name="Beta", phase="9")

        hook = HOOKS_HANDLERS / "session_start.py"
        result = subprocess.run(
            [sys.executable, str(hook)],
            capture_output=True,
            text=True,
            cwd=str(umbrella),  # CC sets cwd to the user project at SessionStart
            env=_isolated_env(tmp_path),
            timeout=30,
        )

        assert result.returncode == 0, result.stderr
        assert SECTION_HEADING in result.stdout
        payload = _payload(result.stdout)
        assert payload["state_present"] is False
        assert [p["name"] for p in payload["subprojects"]] == ["Alpha", "Beta"]
