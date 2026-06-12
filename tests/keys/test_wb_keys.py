"""
Tests for Captain Q's keys module (scripts/wb_keys.py) — Phase 5.

Covers the locked public surface (scripts/README.md § Module boundary):
  - resolve_keys(project_root)  — .env source + 1Password source (op MOCKED)
  - run(argv, *, project_root)  — migrate-to-1password + migrate-to-env (op MOCKED)
  - the unresolved-required-key error path (typed error + fix-path message)
  - import-safety (importing wb_keys has no side effects)

Tier 1 (always runs): NO real `op` CLI, NO real 1Password account, NO network, NO
real secrets. The `op` subprocess is monkeypatched at the single `_run_op` seam so
the 1Password code paths are exercised deterministically. Fixture values are
obvious placeholders (per .claude/rules/secrets-conventions.md + tests/README.md
Phase 5 "placeholder values ONLY") — the asserts check the MECHANISM, not real keys.

project_root is passed in explicitly (per the interface contract); each test copies
the committed fixture into a pytest tmp_path so the module never touches cwd and
migrate verbs never mutate the committed fixture.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

# Make scripts/wb_keys.py importable regardless of pytest cwd (mirrors
# smoke_test.py's sys.path.insert pattern for detector.py).
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

import wb_keys  # noqa: E402

FIXTURE_DIR = Path(__file__).parent / "fixture"


# --- Fixture helpers -------------------------------------------------------

def _copy_fixture(tmp_path: Path) -> Path:
    """Copy the committed fixture project into tmp_path; return the project root."""
    dst = tmp_path / "project"
    shutil.copytree(FIXTURE_DIR, dst)
    return dst


def _dotenv_path(project_root: Path) -> Path:
    """
    The fixture's .env lives at .website-builder/.env (the documented fallback
    location), not project-root .env — because the repo .gitignore ignores root
    .env files but whitelists tests/<captain>/fixture/.website-builder/**. The
    resolver checks project-root .env first then .website-builder/.env, so this
    path exercises the same env-source mechanism. Tests use this helper for any
    read/write of the fixture .env.
    """
    return project_root / ".website-builder" / ".env"


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    return _copy_fixture(tmp_path)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch):
    """
    Ensure the fixture's env-var names aren't already set in the real process env
    (so the .env file — not a stray ambient var — is what the resolver reads).
    """
    for name in (
        "WB_TEST_GEMINI_API_KEY",
        "WB_TEST_STRIPE_PUBLISHABLE_KEY",
        "WB_TEST_STRIPE_SECRET_KEY",
        "WB_TEST_VERCEL_TOKEN",
        "WB_TEST_PLAUSIBLE_KEY",
    ):
        monkeypatch.delenv(name, raising=False)


# A canned op:// reference -> value map for the mocked op CLI. Placeholder values.
_OP_VALUES = {
    "op://TestVault/Vercel/api_token": "placeholder-vercel-token-from-1password",
    "op://TestVault/Stripe/secret_key": "placeholder-stripe-secret-from-1password",
}


def _install_op_mock(monkeypatch: pytest.MonkeyPatch, *, available: bool = True,
                     signed_in: bool = True, read_values: dict[str, str] | None = None,
                     create_ok: bool = True):
    """
    Monkeypatch the `op` CLI seams so 1Password paths run without a real `op`.

    Patches:
      - _op_available()  -> `available`
      - _run_op(args)    -> a fake CompletedProcess for read/whoami/item-create
    """
    values = read_values if read_values is not None else _OP_VALUES

    monkeypatch.setattr(wb_keys, "_op_available", lambda: available)

    class _FakeProc:
        def __init__(self, returncode: int, stdout: str = "", stderr: str = ""):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    def fake_run_op(args, *, input_text=None):
        # args is the op argv WITHOUT the binary name.
        if not args:
            return _FakeProc(2, stderr="no args")
        cmd = args[0]
        if cmd == "whoami":
            return _FakeProc(0 if signed_in else 1,
                             stdout="test-account" if signed_in else "",
                             stderr="" if signed_in else "not signed in")
        if cmd == "read":
            ref = args[1]
            if ref in values:
                # _op_read passes -n (no trailing newline) — mimic op's -n output.
                return _FakeProc(0, stdout=values[ref])
            return _FakeProc(1, stderr=f"could not read {ref}: item not found")
        if cmd == "item" and len(args) > 1 and args[1] == "create":
            return _FakeProc(0 if create_ok else 1,
                             stdout='{"id":"fake","title":"created"}' if create_ok else "",
                             stderr="" if create_ok else "create failed")
        return _FakeProc(2, stderr=f"unexpected op call: {args}")

    monkeypatch.setattr(wb_keys, "_run_op", fake_run_op)


# --- Import safety ---------------------------------------------------------

class TestWbKeysImportSafety:
    """The interface contract requires the module to be import-safe."""

    def test_import_has_no_side_effects(self):
        # Re-import is a no-op; the import at module top already succeeded with no
        # network / file-write / op call. Assert the public surface exists.
        import importlib
        mod = importlib.import_module("wb_keys")
        assert callable(mod.run)
        assert callable(mod.resolve_keys)

    def test_op_not_invoked_at_import(self, monkeypatch: pytest.MonkeyPatch):
        # If importing triggered an op call, this sentinel would have been hit. We
        # can't retroactively check the original import, but we assert that simply
        # touching the module's constants/helpers needs no op binary.
        called = {"n": 0}
        monkeypatch.setattr(wb_keys, "_run_op",
                            lambda *a, **k: called.__setitem__("n", called["n"] + 1))
        # Reading constants + parsing YAML must not call op.
        _ = wb_keys.OP_BIN
        _ = wb_keys.collect_key_entries({"version": 1})
        assert called["n"] == 0


# --- resolve_keys: env source ----------------------------------------------

class TestResolveKeysEnvSource:

    def test_env_keys_resolve_from_dotenv(self, project_root, monkeypatch):
        # op is needed for the onepassword entries in the fixture; mock it so the
        # whole resolve succeeds. The assertion here is on the env-sourced values.
        _install_op_mock(monkeypatch)
        resolved = wb_keys.resolve_keys(project_root)
        assert resolved["WB_TEST_GEMINI_API_KEY"] == "placeholder-gemini-not-a-real-key"
        assert resolved["WB_TEST_STRIPE_PUBLISHABLE_KEY"] == "pk_test_placeholder_publishable"

    def test_env_key_falls_back_to_process_env(self, project_root, monkeypatch):
        # Remove the .env line for GEMINI by rewriting .env without it, then set a
        # process env var — resolver must fall back to process env (the design's
        # ".env <-> system env vars" path).
        _install_op_mock(monkeypatch)
        env_file = _dotenv_path(project_root)
        env_file.write_text(
            "WB_TEST_STRIPE_PUBLISHABLE_KEY=pk_test_placeholder_publishable\n",
            encoding="utf-8",
        )
        monkeypatch.setenv("WB_TEST_GEMINI_API_KEY", "from-process-env-placeholder")
        resolved = wb_keys.resolve_keys(project_root)
        assert resolved["WB_TEST_GEMINI_API_KEY"] == "from-process-env-placeholder"

    def test_optional_key_absence_is_not_an_error(self, project_root, monkeypatch):
        # WB_TEST_PLAUSIBLE_KEY is required: false and absent from .env — must not
        # raise, and must simply be omitted from the resolved dict.
        _install_op_mock(monkeypatch)
        resolved = wb_keys.resolve_keys(project_root)
        assert "WB_TEST_PLAUSIBLE_KEY" not in resolved


# --- resolve_keys: onepassword source (op MOCKED) --------------------------

class TestResolveKeysOnePasswordSource:

    def test_op_keys_resolve_via_mocked_op(self, project_root, monkeypatch):
        _install_op_mock(monkeypatch)
        resolved = wb_keys.resolve_keys(project_root)
        assert resolved["WB_TEST_VERCEL_TOKEN"] == "placeholder-vercel-token-from-1password"
        assert resolved["WB_TEST_STRIPE_SECRET_KEY"] == "placeholder-stripe-secret-from-1password"

    def test_op_read_uses_no_newline_flag(self, project_root, monkeypatch):
        # Verify the resolver calls `op read <ref> -n` (verified-2026-06-12 syntax).
        seen_args: list[list[str]] = []

        class _FakeProc:
            def __init__(self, rc, out="", err=""):
                self.returncode, self.stdout, self.stderr = rc, out, err

        def fake_run_op(args, *, input_text=None):
            seen_args.append(args)
            if args[0] == "whoami":
                return _FakeProc(0, "acct")
            if args[0] == "read":
                return _FakeProc(0, _OP_VALUES.get(args[1], ""))
            return _FakeProc(2)

        monkeypatch.setattr(wb_keys, "_op_available", lambda: True)
        monkeypatch.setattr(wb_keys, "_run_op", fake_run_op)
        wb_keys.resolve_keys(project_root)
        read_calls = [a for a in seen_args if a and a[0] == "read"]
        assert read_calls, "expected at least one `op read` call"
        for call in read_calls:
            assert call[0] == "read"
            assert call[1].startswith("op://")
            assert "-n" in call, f"op read must pass -n (--no-newline); got {call}"


# --- resolve_keys: unresolved-required-key error path ----------------------

class TestResolveKeysErrorPath:

    def test_missing_required_env_key_raises_with_fix_path(self, project_root, monkeypatch):
        _install_op_mock(monkeypatch)
        # Blank out .env so the required GEMINI + publishable keys are missing.
        _dotenv_path(project_root).write_text("# empty\n", encoding="utf-8")
        with pytest.raises(wb_keys.KeyResolutionError) as exc_info:
            wb_keys.resolve_keys(project_root)
        msg = str(exc_info.value)
        # Names the missing keys + a concrete fix path; never leaks a value.
        assert "WB_TEST_GEMINI_API_KEY" in msg
        assert ".env" in msg
        assert "your-value-here" in msg
        # The optional key must NOT appear in the error.
        assert "WB_TEST_PLAUSIBLE_KEY" not in msg

    def test_op_unavailable_for_required_op_key_raises(self, project_root, monkeypatch):
        # op not installed; the source: onepassword keys are required -> error with
        # an install hint as the fix path.
        _install_op_mock(monkeypatch, available=False)
        with pytest.raises(wb_keys.KeyResolutionError) as exc_info:
            wb_keys.resolve_keys(project_root)
        msg = str(exc_info.value)
        assert "WB_TEST_VERCEL_TOKEN" in msg
        assert "1Password CLI" in msg or "op" in msg

    def test_error_collects_all_unresolved_at_once(self, project_root, monkeypatch):
        # Both env keys missing AND op unavailable -> all reported together.
        _install_op_mock(monkeypatch, available=False)
        _dotenv_path(project_root).write_text("# empty\n", encoding="utf-8")
        with pytest.raises(wb_keys.KeyResolutionError) as exc_info:
            wb_keys.resolve_keys(project_root)
        unresolved_vars = {u.env_var for u in exc_info.value.unresolved}
        assert "WB_TEST_GEMINI_API_KEY" in unresolved_vars
        assert "WB_TEST_STRIPE_PUBLISHABLE_KEY" in unresolved_vars
        assert "WB_TEST_VERCEL_TOKEN" in unresolved_vars
        assert "WB_TEST_STRIPE_SECRET_KEY" in unresolved_vars
        # optional one stays out
        assert "WB_TEST_PLAUSIBLE_KEY" not in unresolved_vars


# --- run: migrate-to-1password (op MOCKED) ---------------------------------

class TestMigrateTo1Password:

    def test_migrate_env_keys_to_1password(self, project_root, monkeypatch):
        _install_op_mock(monkeypatch)
        rc = wb_keys.run(
            ["migrate-to-1password", "--vault", "TestVault", "--yes"],
            project_root=project_root,
        )
        assert rc == 0
        # keys.yaml entries that were source: env should now be source: onepassword
        # with an op:// ref. The publishable + gemini env keys had values in .env.
        doc = wb_keys.parse_yaml((project_root / ".website-builder" / "keys.yaml").read_text("utf-8"))
        entries = {e.env_var: e for e in wb_keys.collect_key_entries(doc)}
        assert entries["WB_TEST_GEMINI_API_KEY"].source == "onepassword"
        assert entries["WB_TEST_GEMINI_API_KEY"].ref == "op://TestVault/WB_TEST_GEMINI_API_KEY/credential"
        assert entries["WB_TEST_STRIPE_PUBLISHABLE_KEY"].source == "onepassword"

    def test_migrate_calls_op_item_create(self, project_root, monkeypatch):
        seen: list[list[str]] = []

        class _FakeProc:
            def __init__(self, rc, out="", err=""):
                self.returncode, self.stdout, self.stderr = rc, out, err

        def fake_run_op(args, *, input_text=None):
            seen.append(args)
            if args[0] == "whoami":
                return _FakeProc(0, "acct")
            if args[0] == "read":
                return _FakeProc(0, "placeholder-resolved")
            if args[0] == "item" and args[1] == "create":
                return _FakeProc(0, '{"id":"x"}')
            return _FakeProc(2)

        monkeypatch.setattr(wb_keys, "_op_available", lambda: True)
        monkeypatch.setattr(wb_keys, "_run_op", fake_run_op)
        wb_keys.run(["migrate-to-1password", "--vault", "TestVault", "--yes"],
                    project_root=project_root)
        create_calls = [a for a in seen if len(a) >= 2 and a[0] == "item" and a[1] == "create"]
        assert create_calls, "expected `op item create` calls"
        # Verified-2026-06-12 syntax: --category / --title / --vault + assignment stmt.
        for call in create_calls:
            assert "--category" in call
            assert "--title" in call
            assert "--vault" in call
            assert any("=" in tok and not tok.startswith("--") for tok in call), \
                "expected a field=value assignment statement"

    def test_migrate_to_1password_op_missing_returns_error(self, project_root, monkeypatch):
        _install_op_mock(monkeypatch, available=False)
        rc = wb_keys.run(["migrate-to-1password", "--vault", "TestVault", "--yes"],
                         project_root=project_root)
        assert rc != 0


# --- run: migrate-to-env (op MOCKED) ---------------------------------------

class TestMigrateToEnv:

    def test_migrate_op_keys_to_env(self, project_root, monkeypatch):
        _install_op_mock(monkeypatch)
        rc = wb_keys.run(["migrate-to-env"], project_root=project_root)
        assert rc == 0
        # The two source: onepassword keys should now be source: env in keys.yaml.
        doc = wb_keys.parse_yaml((project_root / ".website-builder" / "keys.yaml").read_text("utf-8"))
        entries = {e.env_var: e for e in wb_keys.collect_key_entries(doc)}
        assert entries["WB_TEST_VERCEL_TOKEN"].source == "env"
        assert entries["WB_TEST_VERCEL_TOKEN"].ref is None
        assert entries["WB_TEST_STRIPE_SECRET_KEY"].source == "env"
        # Their resolved values should be written into .env (the fallback path,
        # which is where the fixture's .env lives + where _find_dotenv resolves).
        dotenv = wb_keys.parse_dotenv(_dotenv_path(project_root).read_text("utf-8"))
        assert dotenv["WB_TEST_VERCEL_TOKEN"] == "placeholder-vercel-token-from-1password"
        assert dotenv["WB_TEST_STRIPE_SECRET_KEY"] == "placeholder-stripe-secret-from-1password"
        # Pre-existing env lines preserved.
        assert dotenv["WB_TEST_GEMINI_API_KEY"] == "placeholder-gemini-not-a-real-key"

    def test_migrate_to_env_aborts_if_ref_unresolvable(self, project_root, monkeypatch):
        # op available + signed in, but a ref doesn't resolve -> no .env changes.
        _install_op_mock(monkeypatch, read_values={})  # empty value map -> read fails
        before = _dotenv_path(project_root).read_text("utf-8")
        rc = wb_keys.run(["migrate-to-env"], project_root=project_root)
        assert rc != 0
        after = _dotenv_path(project_root).read_text("utf-8")
        assert before == after, "migrate-to-env must not mutate .env when a ref fails"
        # keys.yaml unchanged too (still onepassword).
        doc = wb_keys.parse_yaml((project_root / ".website-builder" / "keys.yaml").read_text("utf-8"))
        entries = {e.env_var: e for e in wb_keys.collect_key_entries(doc)}
        assert entries["WB_TEST_VERCEL_TOKEN"].source == "onepassword"


# --- run: dispatch errors --------------------------------------------------

class TestRunDispatch:

    def test_no_verb_returns_usage_error(self, project_root):
        assert wb_keys.run([], project_root=project_root) == 2

    def test_unknown_verb_returns_error(self, project_root):
        assert wb_keys.run(["list"], project_root=project_root) == 2  # `list` not in locked surface

    def test_missing_keys_yaml_is_handled(self, tmp_path, monkeypatch):
        # A project with no keys.yaml -> migrate verbs surface a KeysError -> rc 1.
        empty = tmp_path / "empty"
        (empty / ".website-builder").mkdir(parents=True)
        _install_op_mock(monkeypatch)
        rc = wb_keys.run(["migrate-to-env"], project_root=empty)
        assert rc == 1
