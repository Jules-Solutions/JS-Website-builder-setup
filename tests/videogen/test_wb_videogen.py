"""
Unit tests for the video+audio gen consumer resolver (`scripts/wb_videogen.py`).
Wave 2 / Captain modules-1 scope (DESIGN-video-audio-consumer.md + decision 56).

Fixtures built inline in tmp_path. Env isolated via monkeypatch.

Run:
  cd tests && uv run --with pyyaml --with pytest pytest videogen/ -v
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

import wb_videogen as vg  # noqa: E402  (sys.path mutation must precede)


def _state(tmp_path: Path) -> Path:
    sd = tmp_path / ".website-builder"
    sd.mkdir(parents=True, exist_ok=True)
    return sd


def _keys(tmp_path: Path, body: str) -> None:
    (_state(tmp_path) / "keys.yaml").write_text(textwrap.dedent(body), encoding="utf-8")


def _modal(result, name):
    for m in result.modalities:
        if m.modality == name:
            return m
    return None


class TestImportSafety:
    def test_public_surface(self):
        for name in ("resolve_videogen_path", "run", "main", "VideogenPath", "ModalityPath"):
            assert hasattr(vg, name), name

    def test_signature(self):
        assert list(inspect.signature(vg.resolve_videogen_path).parameters) == ["project_root"]


class TestGap:
    def test_no_keys_is_gap(self, tmp_path: Path):
        _state(tmp_path)
        r = vg.resolve_videogen_path(tmp_path)
        assert r.modalities == [] and r.configured() is False
        assert "gap" in str(r)

    def test_no_media_blocks_is_gap(self, tmp_path: Path):
        _keys(tmp_path, "image_gen:\n  provider: gemini\n  api_key_env: GEMINI_API_KEY\n")
        r = vg.resolve_videogen_path(tmp_path)
        assert r.configured() is False


class TestVideo:
    def test_flat_video(self, tmp_path: Path, monkeypatch):
        _keys(tmp_path, "video_gen:\n  provider: runway-gen3\n  api_key_env: RUNWAY_API_KEY\n")
        monkeypatch.setenv("RUNWAY_API_KEY", "v")
        r = vg.resolve_videogen_path(tmp_path)
        m = _modal(r, "video")
        assert m is not None and m.provider == "runway-gen3" and m.key_present is True

    def test_nested_primary_fallback(self, tmp_path: Path, monkeypatch):
        _keys(tmp_path, textwrap.dedent("""
            video_gen:
              primary:
                provider: runway-gen3
                api_key_env: RUNWAY_API_KEY
              fallback:
                provider: replicate-svd
                api_key_env: REPLICATE_API_TOKEN
        """))
        monkeypatch.delenv("RUNWAY_API_KEY", raising=False)
        r = vg.resolve_videogen_path(tmp_path)
        m = _modal(r, "video")
        # picks primary
        assert m is not None and m.provider == "runway-gen3"
        assert m.key_present is False


class TestAudio:
    def test_audio_submodalities(self, tmp_path: Path, monkeypatch):
        _keys(tmp_path, textwrap.dedent("""
            audio_gen:
              voice:
                provider: elevenlabs
                api_key_env: ELEVENLABS_API_KEY
              music:
                provider: mubert
                api_key_env: MUBERT_API_KEY
              sfx:
                provider: replicate-bark
                api_key_env: REPLICATE_API_TOKEN
        """))
        monkeypatch.setenv("ELEVENLABS_API_KEY", "v")
        monkeypatch.delenv("MUBERT_API_KEY", raising=False)
        r = vg.resolve_videogen_path(tmp_path)
        names = {m.modality for m in r.modalities}
        assert {"audio.voice", "audio.music", "audio.sfx"} <= names
        assert _modal(r, "audio.voice").key_present is True
        assert _modal(r, "audio.music").key_present is False

    def test_flat_audio_block(self, tmp_path: Path, monkeypatch):
        _keys(tmp_path, "audio_gen:\n  provider: openai\n  api_key_env: OPENAI_API_KEY\n")
        monkeypatch.setenv("OPENAI_API_KEY", "v")
        r = vg.resolve_videogen_path(tmp_path)
        m = _modal(r, "audio")
        assert m is not None and m.provider == "openai"


class TestSecretSafety:
    def test_secret_value_never_leaks(self, tmp_path: Path, monkeypatch):
        _keys(tmp_path, "video_gen:\n  provider: runway-gen3\n  api_key_env: RUNWAY_API_KEY\n")
        monkeypatch.setenv("RUNWAY_API_KEY", "super-secret-DO-NOT-LEAK")
        r = vg.resolve_videogen_path(tmp_path)
        blob = str(r) + json.dumps(r.to_summary())
        assert "super-secret-DO-NOT-LEAK" not in blob
        assert "RUNWAY_API_KEY" in blob


class TestRun:
    def test_run_default(self, tmp_path: Path, capsys):
        _state(tmp_path)
        assert vg.run([], project_root=tmp_path) == 0
        assert "gap" in capsys.readouterr().out

    def test_run_json(self, tmp_path: Path, monkeypatch, capsys):
        _keys(tmp_path, "video_gen:\n  provider: runway-gen3\n  api_key_env: RUNWAY_API_KEY\n")
        monkeypatch.setenv("RUNWAY_API_KEY", "v")
        rc = vg.run(["--json"], project_root=tmp_path)
        assert rc == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["configured"] is True
        assert any(m["provider"] == "runway-gen3" for m in payload["modalities"])
