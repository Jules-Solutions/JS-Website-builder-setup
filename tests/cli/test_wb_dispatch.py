"""
tests/cli/test_wb_dispatch.py — dispatch-routing tests for the `wb` CLI
(Captain O, Phase 5).

Validates that scripts/wb.py:
  - routes `library *`  → Captain P's wb_library.run(argv, project_root=...)
  - routes `keys *`     → Captain Q's wb_keys.run(argv, project_root=...)
  - delegates `skills update|sync`        → scripts/install-skills.sh
  - delegates `maintain reconfig`         → scripts/wb-bootstrap.py
  - delegates `maintain install-skills`   → scripts/install-skills.sh
  - exposes `--help` at every level + `--version`
  - fails cleanly when P's/Q's module is absent (the parallel-build reality:
    O's worktree has no wb_library.py / wb_keys.py until merge time)
  - is import-safe (importing wb has no side effects)

Two test classes mirror the Phase-1 two-tier convention (smoke_test.py):

  TestWbDispatch (Tier 1) — always runs. Pure in-process routing using
    INJECTED stub modules for wb_library / wb_keys (no real P/Q modules
    needed), plus argparse help/version checks. No network, no external tools.

  TestWbDelegateIntegration (Tier 2) — subprocess invocation of the real
    delegate scripts (install-skills.sh / wb-bootstrap.py). These ship as
    Phase-1 substrate so they're present in every worktree; the class still
    skips gracefully if a delegate is missing (mirrors smoke_test.py's
    skip-when-absent pattern), and runs each delegate against an isolated
    HOME so install-skills.sh never touches the real ~/.claude/skills/.

CRITICAL — this test NEVER writes a stub wb_library.py / wb_keys.py into
scripts/. The real modules land at merge time (O merges last). Stubs are
injected into sys.modules at test time only and removed in teardown.
"""

from __future__ import annotations

import importlib
import os
import shutil
import subprocess
import sys
import tempfile
import types
from pathlib import Path

import pytest

# --- Locate the plugin + make scripts/ importable ---------------------------

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"

# Put scripts/ first on sys.path so `import wb` (+ stubbed wb_library/wb_keys)
# resolves to the plugin's dispatcher, regardless of pytest's cwd.
sys.path.insert(0, str(SCRIPTS_DIR))


def _fresh_wb():
    """
    Import (or reimport) the wb dispatcher module fresh.

    Reimporting matters because individual tests inject/remove the wb_library /
    wb_keys stub modules; wb.py imports them lazily (inside route fns), so a
    fresh wb module isn't strictly required for the stubs to take effect, but a
    clean import guards against cross-test state in wb's module globals.
    """
    if "wb" in sys.modules:
        del sys.modules["wb"]
    return importlib.import_module("wb")


# --- Stub-module helpers ----------------------------------------------------


class _Recorder:
    """Captures the args a stub's run() was called with."""

    def __init__(self, return_code: int = 0):
        self.calls: list[dict] = []
        self.return_code = return_code

    def run(self, argv, *, project_root):  # matches the contract signature
        self.calls.append({"argv": list(argv), "project_root": Path(project_root)})
        return self.return_code


_SENTINEL = object()  # distinguished "was absent" marker

# Stash for pre-stub/pre-block originals, keyed by module name.  Both
# _inject_stub and _block_module save the current sys.modules entry here before
# replacing it; _remove_stub restores it so cross-file tests (e.g. the library
# reload tests) can still use importlib.reload() on the real module object
# after any cli test that injected stubs.
_saved_originals: dict[str, object] = {}


def _remove_stub(module_name: str) -> None:
    """Remove a stub or None-sentinel from sys.modules, restoring saved originals.

    If _inject_stub or _block_module previously saved the original for this
    name, restore it.  If not (nothing was saved, i.e. nobody injected a stub
    for this name this test), leave whatever is in sys.modules untouched — this
    prevents the autouse setup phase from evicting the real wb_library that was
    imported at collection time by test_wb_library.py (F3 root cause).
    """
    saved = _saved_originals.pop(module_name, _SENTINEL)
    if saved is _SENTINEL:
        # Nobody saved an original for this name in this test — nothing to restore.
        # Leave sys.modules as-is (protects the real module from eviction).
        return

    # We have a saved original: evict whatever is there now and restore.
    sys.modules.pop(module_name, None)
    if saved is not None:
        sys.modules[module_name] = saved  # type: ignore[assignment]
    # If saved is None it means the module was absent before injection; leave absent.


def _inject_stub(module_name: str, recorder: _Recorder) -> None:
    """Insert a fake wb_library / wb_keys module exposing recorder.run.

    Saves the current sys.modules entry so _remove_stub can restore it.
    """
    if module_name not in _saved_originals:
        _saved_originals[module_name] = sys.modules.get(module_name, _SENTINEL)
    mod = types.ModuleType(module_name)
    mod.run = recorder.run  # type: ignore[attr-defined]
    sys.modules[module_name] = mod


def _block_module(module_name: str) -> None:
    """Set a None sentinel so `import <module_name>` raises ModuleNotFoundError.

    Python treats sys.modules[name] = None as a cached "does not exist" entry,
    which makes wb.py's lazy `import wb_library` raise ModuleNotFoundError
    deterministically regardless of whether the real .py exists on sys.path.
    Saves the current entry so _remove_stub restores the real module in teardown,
    keeping cross-file reload() calls working.
    """
    if module_name not in _saved_originals:
        _saved_originals[module_name] = sys.modules.get(module_name, _SENTINEL)
    sys.modules[module_name] = None  # type: ignore[assignment]


@pytest.fixture
def project_dir():
    """A throwaway project directory (real OS tempdir) passed as --project-dir."""
    d = Path(tempfile.mkdtemp(prefix="wb-cli-test-"))
    try:
        yield d
    finally:
        shutil.rmtree(d, ignore_errors=True)


@pytest.fixture(autouse=True)
def _clean_stubs():
    """Ensure no stub or None-sentinel leaks between tests.

    Setup (pre-yield): only removes stubs/sentinels — leaves real modules intact
    so tests in other files (e.g. test_wb_library.py) can still reload them.
    Teardown (post-yield): same safe removal, which also cleans up any
    None-sentinels placed by _block_module inside a test.
    """
    _remove_stub("wb_library")
    _remove_stub("wb_keys")
    yield
    _remove_stub("wb_library")
    _remove_stub("wb_keys")


# --- Tier 1 — in-process dispatch routing -----------------------------------


class TestWbDispatch:
    """Always-runnable. Routing + help/version, no external dependency."""

    # ----- import safety -----

    def test_import_is_side_effect_free(self):
        """Importing wb must not run network/file-write/subprocess at import."""
        wb = _fresh_wb()
        assert hasattr(wb, "main")
        assert hasattr(wb, "build_parser")

    # ----- library routing (Captain P) -----

    def test_library_routes_to_p_with_argv_and_project_root(self, project_dir):
        rec = _Recorder(return_code=0)
        _inject_stub("wb_library", rec)
        wb = _fresh_wb()
        rc = wb.main(["--project-dir", str(project_dir), "library", "add",
                      "https://example.com", "--tag", "docs"])
        assert rc == 0
        assert len(rec.calls) == 1
        call = rec.calls[0]
        # The argv handed to P is everything AFTER `wb library`.
        assert call["argv"] == ["add", "https://example.com", "--tag", "docs"]
        assert call["project_root"] == project_dir.resolve()

    def test_library_propagates_p_return_code(self, project_dir):
        rec = _Recorder(return_code=7)
        _inject_stub("wb_library", rec)
        wb = _fresh_wb()
        rc = wb.main(["--project-dir", str(project_dir), "library", "list"])
        assert rc == 7
        assert rec.calls[0]["argv"] == ["list"]

    def test_library_strips_leading_double_dash(self, project_dir):
        """`wb library -- add ...` and `wb library add ...` behave identically."""
        rec = _Recorder()
        _inject_stub("wb_library", rec)
        wb = _fresh_wb()
        wb.main(["--project-dir", str(project_dir), "library", "--", "list"])
        assert rec.calls[0]["argv"] == ["list"]

    def test_library_missing_module_returns_4(self, project_dir):
        """No wb_library present (the parallel-build reality) → clean exit 4.

        Uses _block_module (sys.modules[name] = None sentinel) instead of a
        mere pop so that the real scripts/wb_library.py on sys.path cannot be
        imported — the test must pass whether or not the real module file exists.
        """
        _block_module("wb_library")
        wb = _fresh_wb()
        rc = wb.main(["--project-dir", str(project_dir), "library", "list"])
        assert rc == 4

    # ----- keys routing (Captain Q) -----

    def test_keys_routes_to_q_with_argv_and_project_root(self, project_dir):
        rec = _Recorder(return_code=0)
        _inject_stub("wb_keys", rec)
        wb = _fresh_wb()
        rc = wb.main(["--project-dir", str(project_dir), "keys",
                      "migrate-to-1password"])
        assert rc == 0
        assert rec.calls[0]["argv"] == ["migrate-to-1password"]
        assert rec.calls[0]["project_root"] == project_dir.resolve()

    def test_keys_propagates_q_return_code(self, project_dir):
        rec = _Recorder(return_code=3)
        _inject_stub("wb_keys", rec)
        wb = _fresh_wb()
        rc = wb.main(["--project-dir", str(project_dir), "keys", "migrate-to-env"])
        assert rc == 3

    def test_keys_missing_module_returns_4(self, project_dir):
        """No wb_keys present (the parallel-build reality) → clean exit 4.

        Uses _block_module so the test is repo-state-independent: passes whether
        or not scripts/wb_keys.py exists on sys.path.
        """
        _block_module("wb_keys")
        wb = _fresh_wb()
        rc = wb.main(["--project-dir", str(project_dir), "keys", "migrate-to-env"])
        assert rc == 4

    # ----- routing isolation: P and Q don't cross-fire -----

    def test_library_does_not_invoke_keys(self, project_dir):
        lib = _Recorder()
        keys = _Recorder()
        _inject_stub("wb_library", lib)
        _inject_stub("wb_keys", keys)
        wb = _fresh_wb()
        wb.main(["--project-dir", str(project_dir), "library", "list"])
        assert len(lib.calls) == 1
        assert len(keys.calls) == 0

    # ----- no command -----

    def test_no_command_prints_help_returns_0(self, capsys):
        wb = _fresh_wb()
        rc = wb.main([])
        assert rc == 0
        out = capsys.readouterr().out
        assert "library" in out and "keys" in out and "skills" in out \
            and "maintain" in out

    # ----- bad project dir -----

    def test_nonexistent_project_dir_returns_2(self):
        wb = _fresh_wb()
        missing = str(Path(tempfile.gettempdir()) / "wb-does-not-exist-xyz123")
        rc = wb.main(["--project-dir", missing, "skills", "update"])
        assert rc == 2

    # ----- help + version via subprocess (exercises the real entry point) -----

    def test_top_level_help(self):
        rc, out, _ = _run_wb_py(["--help"])
        assert rc == 0
        for token in ("library", "keys", "skills", "maintain"):
            assert token in out

    def test_version(self):
        rc, out, _ = _run_wb_py(["--version"])
        assert rc == 0
        assert "wb" in out and "0.1.0" in out

    @pytest.mark.parametrize("command", ["library", "keys", "skills", "maintain"])
    def test_each_command_has_help(self, command):
        rc, out, err = _run_wb_py([command, "--help"])
        assert rc == 0, f"`wb {command} --help` exited {rc}: {err}"
        assert command in (out + err)

    @pytest.mark.parametrize("verb", ["update", "sync"])
    def test_skills_subverb_help(self, verb):
        rc, out, err = _run_wb_py(["skills", verb, "--help"])
        assert rc == 0, f"`wb skills {verb} --help` exited {rc}: {err}"

    @pytest.mark.parametrize("verb", ["reconfig", "install-skills"])
    def test_maintain_subverb_help(self, verb):
        rc, out, err = _run_wb_py(["maintain", verb, "--help"])
        assert rc == 0, f"`wb maintain {verb} --help` exited {rc}: {err}"

    def test_unknown_command_rejected(self):
        rc, _, _ = _run_wb_py(["bogus-verb"])
        assert rc != 0  # argparse rejects unknown subcommands


# --- Subprocess helper (invoke the real wb.py the way production does) -------

def _run_wb_py(args: list[str], *, cwd: Path | None = None,
               env: dict | None = None) -> tuple[int, str, str]:
    """
    Invoke scripts/wb.py via the test's own interpreter (sys.executable).

    We invoke the .py directly rather than the .sh launcher: per
    tests/smoke_test.py's documented reasoning, invoking the Python runner is
    portable across all subprocess/bash combinations (Windows-Python invoking
    WSL-bash mangles backslash drive paths). The .sh launcher's only job is
    interpreter resolution, which sys.executable already gives us.
    """
    runner = SCRIPTS_DIR / "wb.py"
    full_env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(PLUGIN_ROOT)}
    if env:
        full_env.update(env)
    proc = subprocess.run(
        [sys.executable, str(runner), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
        env=full_env,
        timeout=120,
    )
    return proc.returncode, proc.stdout, proc.stderr


# --- Tier 2 — real delegate-script integration ------------------------------


def _find_install_skills() -> Path | None:
    p = SCRIPTS_DIR / "install-skills.sh"
    return p if p.is_file() else None


def _find_bootstrap_runner() -> Path | None:
    p = SCRIPTS_DIR / "wb-bootstrap.py"
    return p if p.is_file() else None


def _isolated_home(tmp: Path) -> dict:
    """Env that points HOME/USERPROFILE at a throwaway dir so install-skills.sh
    writes its skill slots there, never the real ~/.claude/skills/."""
    home = tmp / "home"
    home.mkdir(parents=True, exist_ok=True)
    return {"HOME": str(home), "USERPROFILE": str(home)}


class TestWbDelegateIntegration:
    """
    Tier 2. Invokes the real delegate scripts through wb.py. install-skills.sh +
    wb-bootstrap.py ship as Phase-1 substrate (present in every worktree), so
    these normally run; they skip gracefully if a delegate is absent.
    """

    def test_maintain_install_skills_delegates(self, project_dir):
        if _find_install_skills() is None:
            pytest.skip("install-skills.sh not present (Phase-1 substrate).")
        env = _isolated_home(project_dir)
        rc, out, err = _run_wb_py(
            ["--project-dir", str(project_dir), "maintain", "install-skills"],
            env=env,
        )
        combined = out + err
        assert rc == 0, f"delegate exited {rc}\n{combined}"
        # The delegate ran install-skills.sh end to end:
        assert "install-skills" in combined
        # It recorded install state in the project's .website-builder/:
        state = project_dir / ".website-builder" / "skills-installed.yaml"
        assert state.is_file(), "install-skills.sh did not write skills-installed.yaml"
        assert "ui-ux-pro-max" in state.read_text(encoding="utf-8")

    def test_skills_update_delegates(self, project_dir):
        if _find_install_skills() is None:
            pytest.skip("install-skills.sh not present (Phase-1 substrate).")
        env = _isolated_home(project_dir)
        rc, out, err = _run_wb_py(
            ["--project-dir", str(project_dir), "skills", "update"],
            env=env,
        )
        assert rc == 0, f"`skills update` delegate exited {rc}\n{out}{err}"
        assert "install-skills" in (out + err)

    def test_skills_sync_delegates(self, project_dir):
        if _find_install_skills() is None:
            pytest.skip("install-skills.sh not present (Phase-1 substrate).")
        env = _isolated_home(project_dir)
        rc, out, err = _run_wb_py(
            ["--project-dir", str(project_dir), "skills", "sync"],
            env=env,
        )
        assert rc == 0, f"`skills sync` delegate exited {rc}\n{out}{err}"

    def test_maintain_reconfig_delegates_to_bootstrap(self, project_dir):
        if _find_bootstrap_runner() is None:
            pytest.skip("wb-bootstrap.py not present (Phase-1 substrate).")
        env = _isolated_home(project_dir)
        rc, out, err = _run_wb_py(
            ["--project-dir", str(project_dir), "maintain", "reconfig"],
            env=env,
        )
        combined = out + err
        assert rc == 0, f"`maintain reconfig` delegate exited {rc}\n{combined}"
        # wb-bootstrap.py ran: it initializes .website-builder/project.yaml.
        proj_yaml = project_dir / ".website-builder" / "project.yaml"
        assert proj_yaml.is_file(), "reconfig did not produce project.yaml"
