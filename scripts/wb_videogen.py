#!/usr/bin/env python3
"""
scripts/wb_videogen.py — the website-builder plugin's video + audio gen consumer resolver.

Wave-2 module (orchestration-spine remediation). Sister of `wb_imagegen.py` — same
shape, extended to the video + audio modalities. Surfaced as a session-start summary
(hooks-handlers/session_start.py). The consumer contract lives in
`Workstreams/website-builder/cross-cutting/DESIGN-video-audio-consumer.md`.

Public surface (the resolver-as-entry-point pattern — mirrors wb_keys.resolve_keys):

    resolve_videogen_path(project_root) -> VideogenPath
        Resolve the project's video + audio gen execution paths from
        `.website-builder/keys.yaml` (the `video_gen` + `audio_gen` config blocks) +
        a SECRET-SAFE presence probe of each provider's key env var. Per **locked
        decision 56**, v1 uses the CONSUMER-FALLBACK path (the user supplies their
        own provider keys); the platform video/audio-gen path is a deferred
        follow-up. project_root is passed in explicitly (no os.getcwd()).

    run(argv, *, project_root) -> int
        Debug/`wb`-style dispatch: resolve + print the (secret-safe) paths. `--json`
        emits the structured fields. NOT a user-facing `wb` verb.

    main() -> int
        Standalone entry for isolated debugging. project_root = cwd.

SECRET DISCIPLINE: identical to wb_imagegen — this module NEVER reads, returns, or
logs a secret VALUE. It surfaces only provider names, key env-var NAMES, and
present/MISSING booleans.

Interface rules (mirrors the locked wb_keys.py module contract):
  - IMPORT-SAFE: no side effects at import time.
  - `project_root` passed in explicitly — never os.getcwd() inside the logic.
  - Depends only on the leaf util wb_markdown (parse_yaml) + stdlib. Does NOT import
    wb_keys / wb_library / wb_orchestrate / wb_imagegen (sister module; no cycle).

Modalities (DESIGN-video-audio-consumer.md § "Multi-provider configuration"):
  - video           — `video_gen` block (flat or nested `primary:`/`fallback:`)
  - audio.voice     — `audio_gen.voice`
  - audio.music     — `audio_gen.music`
  - audio.sfx       — `audio_gen.sfx`
  - audio           — a flat `audio_gen` block (provider/api_key_env at top level)

See also:
  - Workstreams/website-builder/cross-cutting/DESIGN-video-audio-consumer.md
  - scripts/wb_imagegen.py (sister consumer — image modality)
  - scripts/wb_keys.py (the locked module template + the .env / keys.yaml read model)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------- Sibling import (wb_markdown lives in this scripts/ dir) ----------
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import wb_markdown  # noqa: E402  (sys.path nudge must precede)


# ---------- Constants ----------

MODULE_NAME = "wb videogen"
STATE_DIR_NAME = ".website-builder"
KEYS_YAML_NAME = "keys.yaml"
VIDEO_KEY = "video_gen"
AUDIO_KEY = "audio_gen"
AUDIO_SUBMODALITIES = ("voice", "music", "sfx")

PATH_PLATFORM = "platform"      # forward-room; never returned in v1 (decision 56)
PATH_CONSUMER = "consumer-fallback"
PATH_GAP = "gap"

VIDEO_DESIGN_DOC = (
    "Workstreams/website-builder/cross-cutting/DESIGN-video-audio-consumer.md"
)


# ---------- Logging helpers (mirror wb_keys.py) ----------

def _color_supported() -> bool:
    return bool(getattr(sys.stdout, "isatty", lambda: False)())


_USE_COLOR = _color_supported()


def _c(code: str, msg: str) -> str:
    if not _USE_COLOR:
        return msg
    return f"\x1b[{code}m{msg}\x1b[0m"


def log_info(msg: str) -> None:
    print(f"{_c('36', '[wb videogen]')} {msg}", flush=True)


def log_warn(msg: str) -> None:
    print(f"{_c('33', '[wb videogen]')} {msg}", file=sys.stderr, flush=True)


# ---------- Typed result (mirror the wb_keys.py slot-object pattern) ----------

@dataclass
class ModalityPath:
    """One resolved modality (video / audio.voice / ...). SECRET-SAFE."""

    modality: str
    path_kind: str               # PATH_CONSUMER | PATH_GAP
    provider: str | None
    api_key_env: str | None
    key_present: bool

    def to_summary(self) -> dict[str, Any]:
        return {
            "modality": self.modality,
            "path_kind": self.path_kind,
            "provider": self.provider,
            "api_key_env": self.api_key_env,
            "key_present": self.key_present,
        }

    def __str__(self) -> str:
        if self.path_kind == PATH_GAP or not self.provider:
            return f"{self.modality}→gap"
        present = "set" if self.key_present else "MISSING"
        if not self.api_key_env:
            return f"{self.modality}→{self.provider} (no api_key_env named)"
        return f"{self.modality}→{self.provider} ({self.api_key_env}: {present})"


@dataclass
class VideogenPath:
    """The resolved video + audio gen paths. `modalities` is empty when nothing is
    configured. `__str__` is the human one-liner the session-start summary renders."""

    modalities: list[ModalityPath] = field(default_factory=list)
    detail: str = ""

    def configured(self) -> bool:
        return any(m.path_kind == PATH_CONSUMER for m in self.modalities)

    def to_summary(self) -> dict[str, Any]:
        return {
            "configured": self.configured(),
            "modalities": [m.to_summary() for m in self.modalities],
            "detail": self.detail,
        }

    def __str__(self) -> str:
        return self.detail


# ---------- keys.yaml + .env reading (self-contained; mirrors wb_keys.py / wb_imagegen.py) ----------

def _state_dir(project_root: Path) -> Path:
    return project_root / STATE_DIR_NAME


def _keys_yaml_path(project_root: Path) -> Path:
    return _state_dir(project_root) / KEYS_YAML_NAME


def _load_keys_doc(project_root: Path) -> dict[str, Any] | None:
    path = _keys_yaml_path(project_root)
    if not path.is_file():
        return None
    try:
        return wb_markdown.parse_yaml(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — a broken keys.yaml degrades to "not configured"
        return None


def _find_dotenv(project_root: Path) -> Path | None:
    for c in (project_root / ".env", _state_dir(project_root) / ".env"):
        if c.is_file():
            return c
    return None


def _parse_dotenv(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        if "=" not in line:
            continue
        name, _, value = line.partition("=")
        name = name.strip()
        if not name:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        out[name] = value
    return out


def _load_dotenv(project_root: Path) -> dict[str, str]:
    path = _find_dotenv(project_root)
    if path is None:
        return {}
    try:
        return _parse_dotenv(path.read_text(encoding="utf-8"))
    except OSError:
        return {}


def _env_present(name: str | None, dotenv: dict[str, str]) -> bool:
    """SECRET-SAFE presence probe (value read for emptiness test, then discarded)."""
    if not name:
        return False
    value = dotenv.get(name)
    if value is None:
        value = os.environ.get(name)
    return bool(value and value.strip())


def _extract_provider_key(block: Any) -> tuple[str | None, str | None]:
    """Pull (provider, api_key_env) out of a config block. Tolerant of the shapes in
    DESIGN-video-audio-consumer.md:
      - flat:    {provider: runway-gen3, api_key_env: RUNWAY_API_KEY}
      - nested:  {primary: {provider: ..., api_key_env: ...}, fallback: {...}}
      - suffix:  {primary_provider: ..., primary_api_key_env: ...}
    Picks `primary` over `fallback` when both nested keys are present.
    """
    if not isinstance(block, dict):
        return None, None
    provider = block.get("provider") or block.get("primary_provider")
    api_key_env = block.get("api_key_env") or block.get("primary_api_key_env")
    for nested_key in ("primary", "fallback"):
        nested = block.get(nested_key)
        if isinstance(nested, dict):
            provider = provider or nested.get("provider")
            api_key_env = api_key_env or nested.get("api_key_env")
    provider = str(provider) if isinstance(provider, (str, int)) else None
    api_key_env = str(api_key_env) if isinstance(api_key_env, (str, int)) else None
    return provider, api_key_env


def _resolve_modality(
    modality: str, block: Any, dotenv: dict[str, str]
) -> ModalityPath | None:
    """Resolve one modality config block to a ModalityPath. None when the block
    carries no provider (nothing configured for this modality)."""
    provider, api_key_env = _extract_provider_key(block)
    if not provider:
        return None
    return ModalityPath(
        modality=modality,
        path_kind=PATH_CONSUMER,
        provider=provider,
        api_key_env=api_key_env,
        key_present=_env_present(api_key_env, dotenv),
    )


# ---------- resolve_videogen_path (the resolver entry point) ----------

def resolve_videogen_path(project_root: Path) -> VideogenPath:
    """Resolve the video + audio gen execution paths (consumer-fallback per
    decision 56). SECRET-SAFE. project_root passed in explicitly (no os.getcwd())."""
    keys_doc = _load_keys_doc(project_root)
    if not keys_doc:
        return VideogenPath(
            modalities=[],
            detail=(
                "gap — no keys.yaml / video+audio gen not configured yet. Set media "
                "strategy at phase 8 to choose providers (you supply the keys — "
                "consumer-fallback, decision 56)."
            ),
        )

    dotenv = _load_dotenv(project_root)
    modalities: list[ModalityPath] = []

    # Video (flat or nested primary/fallback).
    video_block = keys_doc.get(VIDEO_KEY)
    if video_block is not None:
        mp = _resolve_modality("video", video_block, dotenv)
        if mp is not None:
            modalities.append(mp)

    # Audio: either flat (provider at top level) or split by voice/music/sfx.
    audio_block = keys_doc.get(AUDIO_KEY)
    if isinstance(audio_block, dict):
        had_sub = False
        for sub in AUDIO_SUBMODALITIES:
            if sub in audio_block:
                had_sub = True
                mp = _resolve_modality(f"audio.{sub}", audio_block[sub], dotenv)
                if mp is not None:
                    modalities.append(mp)
        if not had_sub:
            mp = _resolve_modality("audio", audio_block, dotenv)
            if mp is not None:
                modalities.append(mp)

    if not modalities:
        return VideogenPath(
            modalities=[],
            detail=(
                "gap — no video/audio gen provider configured in keys.yaml "
                "(`video_gen` / `audio_gen`). Phase 8 sets it; you supply the keys "
                "(consumer-fallback, decision 56)."
            ),
        )

    detail = "consumer-fallback → " + "; ".join(str(m) for m in modalities)
    return VideogenPath(modalities=modalities, detail=detail)


# ---------- run (debug dispatch — NOT a user-facing wb verb) ----------

def run(argv: list[str], *, project_root: Path) -> int:
    """Debug dispatch: resolve + print the (secret-safe) video/audio paths. `--json`
    emits the structured fields. Returns 0 always."""
    parser = argparse.ArgumentParser(
        prog="wb_videogen",
        description="Resolve video + audio gen execution paths (consumer-fallback, decision 56).",
    )
    parser.add_argument("--json", action="store_true",
                        help="Emit the resolved paths as JSON (secret-safe fields).")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code or 0)

    resolved = resolve_videogen_path(project_root)
    if args.json:
        print(json.dumps(resolved.to_summary(), indent=2))
    else:
        log_info(str(resolved))
    return 0


def main(argv: list[str] | None = None) -> int:
    """Standalone entry for isolated debugging. project_root = cwd."""
    args = list(argv if argv is not None else sys.argv[1:])
    return run(args, project_root=Path.cwd())


if __name__ == "__main__":
    sys.exit(main())
