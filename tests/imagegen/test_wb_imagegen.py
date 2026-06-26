"""
Unit tests for the image-gen consumer resolver (`scripts/wb_imagegen.py`).
Wave 2 / Captain modules-1 scope (DESIGN-image-gen-consumer.md + decision 56 +
DESIGN-orchestration-spine.md § 4.3 action 5).

Fixtures built inline in tmp_path (mirrors tests/orchestration/). Env is isolated
via pytest's monkeypatch so a real GEMINI_API_KEY in the dev shell never leaks in.

Run:
  cd tests && uv run --with pyyaml --with pytest pytest imagegen/ -v
"""

from __future__ import annotations

import inspect
import json
import sys
import textwrap
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import wb_imagegen as ig  # noqa: E402  (sys.path mutation must precede)


# --- Fixture helpers --------------------------------------------------------


def _state(tmp_path: Path) -> Path:
    sd = tmp_path / ".website-builder"
    sd.mkdir(parents=True, exist_ok=True)
    return sd


def _keys(tmp_path: Path, body: str) -> None:
    (_state(tmp_path) / "keys.yaml").write_text(textwrap.dedent(body), encoding="utf-8")


def _clear_env(monkeypatch, *names: str) -> None:
    for n in names:
        monkeypatch.delenv(n, raising=False)


# --- Import safety ----------------------------------------------------------


class TestImportSafety:
    def test_public_surface(self):
        for name in ("resolve_imagegen_path", "run", "main", "ImagegenPath"):
            assert hasattr(ig, name), name

    def test_signature(self):
        params = list(inspect.signature(ig.resolve_imagegen_path).parameters)
        assert params == ["project_root"]


# --- Gap cases --------------------------------------------------------------


class TestGap:
    def test_no_keys_yaml_is_gap(self, tmp_path: Path):
        _state(tmp_path)
        r = ig.resolve_imagegen_path(tmp_path)
        assert r.path_kind == "gap"
        assert r.provider is None and r.key_present is False

    def test_no_image_gen_block_is_gap(self, tmp_path: Path):
        _keys(tmp_path, "hosting:\n  vercel:\n    deploy_token:\n      env_var: VERCEL_TOKEN\n")
        r = ig.resolve_imagegen_path(tmp_path)
        assert r.path_kind == "gap"


# --- Consumer-fallback (decision 56) ----------------------------------------


class TestConsumerFallback:
    def test_provider_and_key_present(self, tmp_path: Path, monkeypatch):
        _keys(tmp_path, "image_gen:\n  provider: gemini\n  api_key_env: GEMINI_API_KEY\n")
        monkeypatch.setenv("GEMINI_API_KEY", "sk-secret-value")
        r = ig.resolve_imagegen_path(tmp_path)
        assert r.path_kind == "consumer-fallback"
        assert r.provider == "gemini"
        assert r.api_key_env == "GEMINI_API_KEY"
        assert r.key_present is True
        assert "set" in str(r)

    def test_provider_key_missing(self, tmp_path: Path, monkeypatch):
        _keys(tmp_path, "image_gen:\n  provider: gemini\n  api_key_env: GEMINI_API_KEY\n")
        _clear_env(monkeypatch, "GEMINI_API_KEY")
        r = ig.resolve_imagegen_path(tmp_path)
        assert r.path_kind == "consumer-fallback"
        assert r.key_present is False
        assert "MISSING" in str(r)

    def test_key_present_via_dotenv(self, tmp_path: Path, monkeypatch):
        _keys(tmp_path, "image_gen:\n  provider: gemini\n  api_key_env: GEMINI_API_KEY\n")
        _clear_env(monkeypatch, "GEMINI_API_KEY")
        (tmp_path / ".env").write_text("GEMINI_API_KEY=from-dotenv\n", encoding="utf-8")
        r = ig.resolve_imagegen_path(tmp_path)
        assert r.key_present is True

    def test_suffix_shape(self, tmp_path: Path, monkeypatch):
        _keys(tmp_path, textwrap.dedent("""
            image_gen:
              primary_provider: gemini
              primary_api_key_env: GEMINI_API_KEY
              fallback_provider: openai
              fallback_api_key_env: OPENAI_API_KEY
        """))
        monkeypatch.setenv("GEMINI_API_KEY", "v")
        r = ig.resolve_imagegen_path(tmp_path)
        assert r.provider == "gemini" and r.api_key_env == "GEMINI_API_KEY"
        assert r.key_present is True

    def test_provider_without_api_key_env(self, tmp_path: Path):
        _keys(tmp_path, "image_gen:\n  provider: gemini\n")
        r = ig.resolve_imagegen_path(tmp_path)
        assert r.path_kind == "consumer-fallback"
        assert r.api_key_env is None
        assert "api_key_env" in str(r)


# --- Secret discipline ------------------------------------------------------


class TestSecretSafety:
    def test_secret_value_never_leaks(self, tmp_path: Path, monkeypatch):
        _keys(tmp_path, "image_gen:\n  provider: gemini\n  api_key_env: GEMINI_API_KEY\n")
        monkeypatch.setenv("GEMINI_API_KEY", "super-secret-DO-NOT-LEAK")
        r = ig.resolve_imagegen_path(tmp_path)
        blob = str(r) + json.dumps(r.to_summary())
        assert "super-secret-DO-NOT-LEAK" not in blob
        # but the NON-secret env-var name + presence boolean are surfaced
        assert "GEMINI_API_KEY" in blob and r.key_present is True


# --- run() debug dispatch ---------------------------------------------------


class TestRun:
    def test_run_default(self, tmp_path: Path, capsys):
        _state(tmp_path)
        assert ig.run([], project_root=tmp_path) == 0
        assert "gap" in capsys.readouterr().out

    def test_run_json(self, tmp_path: Path, monkeypatch, capsys):
        _keys(tmp_path, "image_gen:\n  provider: gemini\n  api_key_env: GEMINI_API_KEY\n")
        monkeypatch.setenv("GEMINI_API_KEY", "v")
        rc = ig.run(["--json"], project_root=tmp_path)
        assert rc == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["provider"] == "gemini"
        assert payload["key_present"] is True
        assert "v" not in json.dumps(payload) or payload["api_key_env"] == "GEMINI_API_KEY"
