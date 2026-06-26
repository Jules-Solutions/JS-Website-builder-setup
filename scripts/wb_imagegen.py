#!/usr/bin/env python3
"""
scripts/wb_imagegen.py — the website-builder plugin's image-gen consumer resolver.

Wave-2 module (orchestration-spine remediation). Lights up the spine's
import-guarded **action 5** (DESIGN-orchestration-spine.md § 4.3, fired at phase 8)
and is surfaced as a session-start summary (hooks-handlers/session_start.py). The
consumer contract lives in
`Workstreams/website-builder/cross-cutting/DESIGN-image-gen-consumer.md`.

Public surface (the resolver-as-entry-point pattern — mirrors wb_keys.resolve_keys):

    resolve_imagegen_path(project_root) -> ImagegenPath
        Resolve the project's image-gen execution path from
        `.website-builder/keys.yaml` (the `image_gen` config block) + a SECRET-SAFE
        presence probe of the provider's key env var. Per **locked decision 56**,
        v1 uses the CONSUMER-FALLBACK path (the user supplies their own provider
        key); the Jules-Solutions platform image-gen path is a deferred follow-up
        (DESIGN-image-gen-consumer.md "When the platform image-gen feature is
        missing"). Called by wb_orchestrate._action_imagegen (action 5) + the
        SessionStart hook. project_root is passed in explicitly (no os.getcwd()).

    run(argv, *, project_root) -> int
        Debug/`wb`-style dispatch: resolve + print the (secret-safe) path. `--json`
        emits the structured fields. NOT a user-facing `wb` verb.

    main() -> int
        Standalone entry for isolated debugging. project_root = cwd.

SECRET DISCIPLINE (`.claude/rules/secrets-conventions.md` + DESIGN-secrets-and-keys.md):
  - This module NEVER reads, returns, or logs a secret VALUE. It surfaces only the
    provider name, the key's env-var NAME, and a boolean "present / MISSING". The
    presence probe checks `.env` + the process env for a non-empty value and throws
    the value away immediately.

Interface rules (mirrors the locked wb_keys.py module contract):
  - IMPORT-SAFE: importing this module has NO side effects (no network, no file
    writes, no subprocess at import time). All work happens inside the entry points.
  - `project_root` is passed in explicitly — never os.getcwd() inside the logic.
  - Depends only on the leaf util wb_markdown (parse_yaml) + stdlib. Does NOT import
    the dispatcher, wb_keys, wb_library, or wb_orchestrate (no cycle — wb_orchestrate
    soft-imports THIS module, never the reverse). Sister module: wb_videogen.py.

See also:
  - Workstreams/website-builder/cross-cutting/DESIGN-image-gen-consumer.md
  - Workstreams/website-builder/foundation/DESIGN-orchestration-spine.md § 4.3 (action 5)
  - scripts/wb_keys.py (the locked module template + the .env / keys.yaml read model)
  - scripts/wb_videogen.py (sister consumer — same shape, video + audio modalities)
  - scripts/wb_orchestrate.py (_action_imagegen — the action-5 call-site)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ---------- Sibling import (wb_markdown lives in this scripts/ dir) ----------
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import wb_markdown  # noqa: E402  (sys.path nudge must precede)


# ---------- Constants ----------

MODULE_NAME = "wb imagegen"
STATE_DIR_NAME = ".website-builder"
KEYS_YAML_NAME = "keys.yaml"
CONFIG_KEY = "image_gen"

# Per locked decision 56: v1 is consumer-fallback only (user-provides-key); the
# Jules-Solutions platform image-gen path is a deferred follow-up. We name the path
# kinds for forward-room — `platform` is never returned in v1.
PATH_PLATFORM = "platform"
PATH_CONSUMER = "consumer-fallback"
PATH_GAP = "gap"

IMAGEGEN_DESIGN_DOC = (
    "Workstreams/website-builder/cross-cutting/DESIGN-image-gen-consumer.md"
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
    print(f"{_c('36', '[wb imagegen]')} {msg}", flush=True)


def log_warn(msg: str) -> None:
    print(f"{_c('33', '[wb imagegen]')} {msg}", file=sys.stderr, flush=True)


# ---------- Typed result (mirror the wb_keys.py slot-object pattern) ----------

@dataclass
class ImagegenPath:
    """The resolved image-gen execution path. SECRET-SAFE: `key_present` is a
    boolean — the secret value is never stored. `__str__` is the human one-liner
    the orchestrator + session-start summary render."""

    path_kind: str               # PATH_CONSUMER | PATH_GAP  (PATH_PLATFORM = forward-room)
    provider: str | None
    api_key_env: str | None
    key_present: bool
    detail: str

    def to_summary(self) -> dict[str, Any]:
        """Secret-safe dict (env-var NAME + presence boolean — never the value)."""
        return {
            "path_kind": self.path_kind,
            "provider": self.provider,
            "api_key_env": self.api_key_env,
            "key_present": self.key_present,
            "detail": self.detail,
        }

    def __str__(self) -> str:
        return self.detail


# ---------- keys.yaml + .env reading (self-contained; mirrors wb_keys.py) ----------

def _state_dir(project_root: Path) -> Path:
    return project_root / STATE_DIR_NAME


def _keys_yaml_path(project_root: Path) -> Path:
    return _state_dir(project_root) / KEYS_YAML_NAME


def _load_keys_doc(project_root: Path) -> dict[str, Any] | None:
    """Parse `.website-builder/keys.yaml`. None if absent / unreadable / unparsable
    (the resolver treats any of these as 'not configured', never a crash)."""
    path = _keys_yaml_path(project_root)
    if not path.is_file():
        return None
    try:
        return wb_markdown.parse_yaml(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — a broken keys.yaml degrades to "not configured"
        return None


def _find_dotenv(project_root: Path) -> Path | None:
    """Locate the .env file (project root wins; `.website-builder/.env` is the
    documented fallback — mirrors wb_keys._find_dotenv)."""
    for c in (project_root / ".env", _state_dir(project_root) / ".env"):
        if c.is_file():
            return c
    return None


def _parse_dotenv(text: str) -> dict[str, str]:
    """Minimal dotenv subset (KEY=VALUE, `#` comments, optional `export `, single/
    double quote stripping). Mirrors wb_keys.parse_dotenv. No ${VAR} interpolation."""
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
    """SECRET-SAFE presence probe: True if `name` resolves to a NON-EMPTY value in
    the project .env or the process env. The value itself is read for the
    emptiness test and immediately discarded — never returned or logged."""
    if not name:
        return False
    value = dotenv.get(name)
    if value is None:
        value = os.environ.get(name)
    return bool(value and value.strip())


def _extract_provider_key(block: Any) -> tuple[str | None, str | None]:
    """Pull (provider, api_key_env) out of an image_gen config block. Tolerant of
    the shapes in DESIGN-image-gen-consumer.md:
      - flat:    {provider: gemini, api_key_env: GEMINI_API_KEY}
      - suffix:  {primary_provider: gemini, primary_api_key_env: GEMINI_API_KEY}
      - nested:  {primary: {provider: gemini, api_key_env: GEMINI_API_KEY}}
      - keys.yaml entry style: {provider: ..., api_key: {env_var: GEMINI_API_KEY}}
    """
    if not isinstance(block, dict):
        return None, None
    provider = block.get("provider") or block.get("primary_provider")
    api_key_env = block.get("api_key_env") or block.get("primary_api_key_env")
    # nested `primary:` dict
    nested = block.get("primary")
    if isinstance(nested, dict):
        provider = provider or nested.get("provider")
        api_key_env = api_key_env or nested.get("api_key_env")
    # keys.yaml entry style nested `api_key: {env_var: ...}`
    if not api_key_env:
        api_key = block.get("api_key")
        if isinstance(api_key, dict):
            ev = api_key.get("env_var")
            if isinstance(ev, str):
                api_key_env = ev
    provider = str(provider) if isinstance(provider, (str, int)) else None
    api_key_env = str(api_key_env) if isinstance(api_key_env, (str, int)) else None
    return provider, api_key_env


# ---------- resolve_imagegen_path (the resolver entry point) ----------

def resolve_imagegen_path(project_root: Path) -> ImagegenPath:
    """Resolve the image-gen execution path (consumer-fallback per decision 56).

    Returns an ImagegenPath. SECRET-SAFE — only the provider name, key env-var
    NAME, and a presence boolean are surfaced; the secret value is never read into
    the result. project_root is passed in explicitly (no os.getcwd())."""
    keys_doc = _load_keys_doc(project_root)
    if not keys_doc:
        return ImagegenPath(
            path_kind=PATH_GAP, provider=None, api_key_env=None, key_present=False,
            detail=(
                "gap — no keys.yaml / image-gen not configured yet. Run `/wb-bootstrap` "
                "or set image strategy at phase 8 to choose a provider (you supply the "
                "key — consumer-fallback, decision 56)."
            ),
        )

    block = keys_doc.get(CONFIG_KEY)
    provider, api_key_env = _extract_provider_key(block)
    if not provider:
        return ImagegenPath(
            path_kind=PATH_GAP, provider=None, api_key_env=None, key_present=False,
            detail=(
                "gap — no image-gen provider configured in keys.yaml (`image_gen.provider`). "
                "Phase 8 sets it; you supply the key (consumer-fallback, decision 56)."
            ),
        )

    dotenv = _load_dotenv(project_root)
    key_present = _env_present(api_key_env, dotenv)

    if api_key_env is None:
        detail = (
            f"consumer-fallback → {provider}, but no `api_key_env` is named in "
            f"keys.yaml.image_gen. Add `api_key_env: <PROVIDER_KEY>` so the key can be "
            f"resolved ({IMAGEGEN_DESIGN_DOC})."
        )
    elif key_present:
        detail = f"consumer-fallback → {provider} (env {api_key_env}: set)"
    else:
        detail = (
            f"consumer-fallback → {provider} (env {api_key_env}: MISSING — set it in "
            f".env or your shell before generating images)"
        )

    return ImagegenPath(
        path_kind=PATH_CONSUMER,
        provider=provider,
        api_key_env=api_key_env,
        key_present=key_present,
        detail=detail,
    )


# ---------- run (debug dispatch — NOT a user-facing wb verb) ----------

def run(argv: list[str], *, project_root: Path) -> int:
    """Debug dispatch: resolve + print the (secret-safe) image-gen path. `--json`
    emits the structured fields. Returns 0 always. Mirrors wb_keys: the resolver is
    an entry point, not a user-facing `wb` verb."""
    parser = argparse.ArgumentParser(
        prog="wb_imagegen",
        description="Resolve the image-gen execution path (consumer-fallback, decision 56).",
    )
    parser.add_argument("--json", action="store_true",
                        help="Emit the resolved path as JSON (secret-safe fields).")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code or 0)

    resolved = resolve_imagegen_path(project_root)
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
