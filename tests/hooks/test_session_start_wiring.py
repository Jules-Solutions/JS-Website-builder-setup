"""
Tier-1 tests for the Phase-6 SessionStart hook wiring (hooks-handlers/session_start.py).

Phase 5 shipped two callable-but-unwired runtime modules:
  - scripts/wb_library.py :: autoclone_for_state  (Captain P — resource auto-clone)
  - scripts/wb_keys.py    :: resolve_keys         (Captain Q — secrets resolution)

Phase 6 wires both into the SessionStart hook. These tests prove the interlock:
  - Both fire on the MID-PROJECT path (a `.website-builder/` state dir exists).
  - Both are SKIPPED on the FRESH path (no state dir) — they'd have no
    project.yaml / keys.yaml to read.
  - Every failure mode is non-fatal: the hook always exits 0 + emits context, and
    no exception escapes into the CC session (this hook runs on EVERY website-
    builder session — a crash breaks every user session).
  - SECRET-SAFE: a resolved key's VALUE never appears in the hook output — only
    its env-var NAME + counts + value-free fix-path messages.

Tier 1 (always runs): NO network, NO real `op` CLI, NO real secrets. The two
Phase-5 functions are monkeypatched on the hook module so the wiring is asserted
deterministically; the end-to-end subprocess tests use an ISOLATED HOME +
placeholder-only secrets over a synthetic `.website-builder/` built in tmp_path
(no committed fixture dir — so no `.gitignore` whitelist edit is needed, keeping
this strictly inside the Lieutenant write zone).

`TestHookIntegration` in smoke_test.py (the Phase-1 entry-mode hook tests) must
remain 5/5 — these tests are additive and never touch that surface.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

# Make hooks-handlers/session_start.py importable regardless of pytest's cwd
# (mirrors smoke_test.py's sys.path.insert for detector.py and the keys/library
# tests' sys.path.insert for the scripts/ modules).
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
HOOKS_HANDLERS = PLUGIN_ROOT / "hooks-handlers"
sys.path.insert(0, str(HOOKS_HANDLERS))

import session_start as ss  # noqa: E402  (sys.path mutation must precede)


# --- Synthetic-state helpers ----------------------------------------------
#
# Built programmatically in tmp_path (NOT a committed fixture dir). The repo
# .gitignore ignores `.website-builder/` and only whitelists the per-Captain
# fixture subdirs (tests/cli|library|keys|...); there is no tests/hooks/
# whitelist, so committing a fixture would be silently gitignored. Building the
# state in tmp_path sidesteps that cleanly and keeps the write zone to this file.

_PROJECT_YAML = """\
version: 1
name: "wiring-fixture"
slug: "wiring-fixture"
entry_mode: "greenfield"
current_phase: 17
stack: "astro"
cms: "decap"
transactional: true
payment_provider: "stripe"
component_library: "shadcn"
"""

_KEYS_YAML_ENV = """\
version: 1
image_gen:
  api_key:
    source: env
    env_var: WB_WIRING_GEMINI
analytics:
  plausible:
    api_key:
      source: env
      env_var: WB_WIRING_OPTIONAL
      required: false
"""

# Placeholder value ONLY — never a real secret (per secrets-conventions.md +
# tests/README.md Phase-5 "placeholder values ONLY"). The test asserts the
# NAME is surfaced and the VALUE is not.
_DOTENV = "WB_WIRING_GEMINI=placeholder-not-a-real-key\n"
_GEMINI_PLACEHOLDER = "placeholder-not-a-real-key"


def _make_mid_project(tmp_path: Path, *, with_keys: bool = True) -> Path:
    """Build a synthetic mid-project `.website-builder/` under tmp_path."""
    root = tmp_path / "project"
    state = root / ".website-builder"
    state.mkdir(parents=True)
    (state / "project.yaml").write_text(_PROJECT_YAML, encoding="utf-8")
    if with_keys:
        (state / "keys.yaml").write_text(_KEYS_YAML_ENV, encoding="utf-8")
        (state / ".env").write_text(_DOTENV, encoding="utf-8")
    return root


def _make_fresh_project(tmp_path: Path) -> Path:
    """Build a fresh (greenfield, no state dir) project under tmp_path."""
    root = tmp_path / "fresh"
    root.mkdir(parents=True)
    return root


# --- In-process wiring tests (monkeypatch the Phase-5 functions) -----------


class TestWiringInvocation:
    """main() invokes BOTH Phase-5 functions on the mid-project path, and NEITHER
    on the fresh path. Proven by spying on the run_* wrappers + the underlying
    module functions."""

    def test_both_fire_on_mid_project(self, tmp_path, monkeypatch, capsys):
        root = _make_mid_project(tmp_path)
        monkeypatch.chdir(root)

        calls = {"autoclone": 0, "resolve": 0}
        real_autoclone = ss.run_autoclone
        real_keys = ss.run_resolve_keys

        def spy_autoclone(r):
            calls["autoclone"] += 1
            return real_autoclone(r)

        def spy_keys(r):
            calls["resolve"] += 1
            return real_keys(r)

        monkeypatch.setattr(ss, "run_autoclone", spy_autoclone)
        monkeypatch.setattr(ss, "run_resolve_keys", spy_keys)

        rc = ss.main()
        assert rc == 0
        assert calls["autoclone"] == 1, "autoclone_for_state must fire once on mid-project"
        assert calls["resolve"] == 1, "resolve_keys must fire once on mid-project"

    def test_neither_fires_on_fresh_project(self, tmp_path, monkeypatch):
        root = _make_fresh_project(tmp_path)
        monkeypatch.chdir(root)

        calls = {"autoclone": 0, "resolve": 0}
        monkeypatch.setattr(ss, "run_autoclone", lambda r: calls.__setitem__("autoclone", calls["autoclone"] + 1))
        monkeypatch.setattr(ss, "run_resolve_keys", lambda r: calls.__setitem__("resolve", calls["resolve"] + 1))

        rc = ss.main()
        assert rc == 0
        assert calls["autoclone"] == 0, "autoclone must NOT fire on a fresh project (no project.yaml)"
        assert calls["resolve"] == 0, "resolve_keys must NOT fire on a fresh project (no keys.yaml)"

    def test_underlying_modules_invoked_with_session_start_trigger(self, tmp_path, monkeypatch):
        """run_autoclone calls wb_library.autoclone_for_state with trigger=session-start;
        run_resolve_keys calls wb_keys.resolve_keys with the project root."""
        root = _make_mid_project(tmp_path)

        # Import the real modules the hook imports, then spy on their functions.
        sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))
        import wb_library  # noqa: E402
        import wb_keys  # noqa: E402

        seen = {}

        def spy_autoclone(project_root, *, trigger, phase=None, log=None):
            seen["autoclone_trigger"] = trigger
            seen["autoclone_root"] = project_root
            return []

        def spy_resolve(project_root):
            seen["resolve_root"] = project_root
            return {"WB_WIRING_GEMINI": _GEMINI_PLACEHOLDER}

        monkeypatch.setattr(wb_library, "autoclone_for_state", spy_autoclone)
        monkeypatch.setattr(wb_keys, "resolve_keys", spy_resolve)

        ac = ss.run_autoclone(root)
        keys = ss.run_resolve_keys(root)

        assert seen["autoclone_trigger"] == "session-start"
        assert seen["autoclone_root"] == root
        assert seen["resolve_root"] == root
        assert ac is not None and ac["available"] is True
        assert keys is not None and keys["status"] == "resolved"


# --- run_autoclone behavior ------------------------------------------------


class TestRunAutoclone:
    def test_derives_candidates_from_project_yaml(self, tmp_path):
        root = _make_mid_project(tmp_path)
        ac = ss.run_autoclone(root)
        assert ac is not None and ac["available"] is True
        resources = {r["resource"] for r in ac["results"]}
        # astro + shadcn + decap + (transactional + stripe) all map to candidates.
        assert "astro-content-collections" in resources
        assert "shadcn-components" in resources
        assert "stripe-checkout" in resources
        # Session-start records intent only — no network fetch inline.
        assert all(r["status"] in ("fetch-deferred", "skipped") for r in ac["results"])

    def test_empty_project_yaml_yields_no_candidates(self, tmp_path):
        root = tmp_path / "p"
        (root / ".website-builder").mkdir(parents=True)
        (root / ".website-builder" / "project.yaml").write_text("version: 1\n", encoding="utf-8")
        ac = ss.run_autoclone(root)
        assert ac is not None and ac["available"] is True
        assert ac["count"] == 0

    def test_no_state_dir_is_non_fatal(self, tmp_path):
        # run_autoclone over a dir with no .website-builder/ → empty, never raises.
        ac = ss.run_autoclone(tmp_path)
        assert ac is not None and ac["available"] is True
        assert ac["count"] == 0

    def test_import_failure_is_non_fatal(self, tmp_path, monkeypatch):
        # Simulate the wb_library module being unimportable (partially-installed
        # plugin). run_autoclone must report unavailable, never raise.
        root = _make_mid_project(tmp_path)
        monkeypatch.setitem(sys.modules, "wb_library", None)  # forces ImportError
        ac = ss.run_autoclone(root)
        assert ac is not None
        assert ac["available"] is False
        assert "import failed" in ac["error"]

    def test_runtime_error_is_non_fatal(self, tmp_path, monkeypatch):
        root = _make_mid_project(tmp_path)
        sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))
        import wb_library  # noqa: E402

        def boom(*a, **k):
            raise RuntimeError("synthetic autoclone failure")

        monkeypatch.setattr(wb_library, "autoclone_for_state", boom)
        ac = ss.run_autoclone(root)
        assert ac is not None and ac["available"] is True
        assert "raised" in ac["error"]


# --- run_resolve_keys behavior + secret safety -----------------------------


class TestRunResolveKeys:
    def test_resolves_env_keys_names_only(self, tmp_path):
        root = _make_mid_project(tmp_path)
        keys = ss.run_resolve_keys(root)
        assert keys is not None and keys["status"] == "resolved"
        assert keys["count"] == 1
        assert keys["env_vars"] == ["WB_WIRING_GEMINI"]

    def test_secret_value_never_in_summary(self, tmp_path):
        # The placeholder VALUE must NOT appear anywhere in the returned summary.
        root = _make_mid_project(tmp_path)
        keys = ss.run_resolve_keys(root)
        assert _GEMINI_PLACEHOLDER not in json.dumps(keys)

    def test_no_keys_yaml_is_no_registry(self, tmp_path):
        root = _make_mid_project(tmp_path, with_keys=False)
        keys = ss.run_resolve_keys(root)
        assert keys is not None and keys["status"] == "no-registry"

    def test_missing_required_key_surfaces_fix_path(self, tmp_path):
        # keys.yaml declares a required env key, but no .env / process env supplies
        # it → KeyResolutionError → surfaced as a value-free fix message.
        root = tmp_path / "p"
        state = root / ".website-builder"
        state.mkdir(parents=True)
        state.joinpath("project.yaml").write_text("version: 1\n", encoding="utf-8")
        state.joinpath("keys.yaml").write_text(
            "version: 1\nx:\n  k:\n    source: env\n    env_var: WB_WIRING_REQUIRED\n",
            encoding="utf-8",
        )
        # Ensure the env var isn't ambiently set.
        keys = ss.run_resolve_keys(root)
        assert keys is not None and keys["status"] == "unresolved"
        assert keys["unresolved_count"] == 1
        assert "WB_WIRING_REQUIRED" in keys["fix_message"]
        # Fix message is value-free (it names keys + sources + paths, not secrets).

    def test_import_failure_is_non_fatal(self, tmp_path, monkeypatch):
        root = _make_mid_project(tmp_path)
        monkeypatch.setitem(sys.modules, "wb_keys", None)  # forces ImportError
        keys = ss.run_resolve_keys(root)
        assert keys is not None
        assert keys["available"] is False
        assert "import failed" in keys["error"]

    def test_unexpected_error_is_non_fatal(self, tmp_path, monkeypatch):
        root = _make_mid_project(tmp_path)
        sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))
        import wb_keys  # noqa: E402

        def boom(_root):
            raise RuntimeError("synthetic resolve failure")

        monkeypatch.setattr(wb_keys, "resolve_keys", boom)
        keys = ss.run_resolve_keys(root)
        assert keys is not None and keys["available"] is True
        assert keys["status"] == "error"
        assert "raised" in keys["error"]


# --- End-to-end subprocess tests (isolated HOME, placeholder secrets) -------
#
# Mirrors smoke_test.py's TestHookIntegration: invoke the hook as a real
# subprocess with cwd = the synthetic project (CC sets cwd to the user's project
# at SessionStart; the hook reads Path.cwd()). Asserts exit 0 + parses the
# machine-readable JSON block out of the stdout context (same parser strategy as
# smoke_test._parse_hook_output).

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*\n(\{[\s\S]*?\})\s*\n```", re.MULTILINE)


def _parse_machine_block(stdout: str) -> dict | None:
    for m in _JSON_FENCE_RE.finditer(stdout.strip()):
        try:
            obj = json.loads(m.group(1))
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            continue
    return None


def _isolated_env(tmp_path: Path) -> dict[str, str]:
    """Env with an isolated HOME (so no real ~/.op, no real 1Password session is
    reachable) + a bogus `op` bin name (so the keys module's _op_available()
    returns False instead of finding a real op). Belt-and-suspenders: our fixture
    uses source: env only, so op is never invoked anyway."""
    env = {**os.environ}
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    env["HOME"] = str(home)
    env["USERPROFILE"] = str(home)
    env["WB_OP_BIN"] = "wb-nonexistent-op-binary"  # keys module: op never found
    # Clear any ambient copies of the fixture key names.
    for name in ("WB_WIRING_GEMINI", "WB_WIRING_OPTIONAL", "WB_WIRING_REQUIRED"):
        env.pop(name, None)
    return env


def _run_hook(project_root: Path, tmp_path: Path) -> subprocess.CompletedProcess:
    hook = HOOKS_HANDLERS / "session_start.py"
    return subprocess.run(
        [sys.executable, str(hook)],
        capture_output=True,
        text=True,
        cwd=str(project_root),  # CC sets cwd to the user project at SessionStart
        env=_isolated_env(tmp_path),
        timeout=30,
    )


class TestHookSubprocessWiring:
    def test_mid_project_subprocess_fires_both(self, tmp_path):
        root = _make_mid_project(tmp_path)
        proc = _run_hook(root, tmp_path)
        assert proc.returncode == 0, f"hook non-zero exit\nstdout:{proc.stdout}\nstderr:{proc.stderr}"
        block = _parse_machine_block(proc.stdout)
        assert block is not None, f"no machine block parsed\nstdout:{proc.stdout}"
        # autoclone fired + recorded candidates
        assert block["autoclone"] is not None
        assert block["autoclone"]["available"] is True
        assert block["autoclone"]["count"] >= 1
        # resolve_keys fired + resolved the env key (NAME surfaced)
        assert block["keys"] is not None
        assert block["keys"]["status"] == "resolved"
        assert "WB_WIRING_GEMINI" in block["keys"]["env_vars"]
        # The human-readable section is present too.
        assert "## Resource library (auto-clone)" in proc.stdout
        assert "## Secrets / keys" in proc.stdout

    def test_mid_project_subprocess_never_leaks_secret_value(self, tmp_path):
        root = _make_mid_project(tmp_path)
        proc = _run_hook(root, tmp_path)
        assert proc.returncode == 0
        assert _GEMINI_PLACEHOLDER not in proc.stdout, "secret VALUE leaked into hook stdout"
        assert _GEMINI_PLACEHOLDER not in proc.stderr, "secret VALUE leaked into hook stderr"

    def test_fresh_project_subprocess_skips_both(self, tmp_path):
        root = _make_fresh_project(tmp_path)
        proc = _run_hook(root, tmp_path)
        assert proc.returncode == 0
        block = _parse_machine_block(proc.stdout)
        assert block is not None
        assert block["autoclone"] is None, "autoclone must be absent on fresh project"
        assert block["keys"] is None, "keys must be absent on fresh project"
        assert "## Resource library (auto-clone)" not in proc.stdout
        assert "## Secrets / keys" not in proc.stdout

    def test_mid_project_no_keys_yaml_subprocess_is_clean(self, tmp_path):
        root = _make_mid_project(tmp_path, with_keys=False)
        proc = _run_hook(root, tmp_path)
        assert proc.returncode == 0
        block = _parse_machine_block(proc.stdout)
        assert block is not None
        assert block["keys"]["status"] == "no-registry"
