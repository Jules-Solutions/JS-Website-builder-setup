#!/usr/bin/env python3
"""
website-builder — PostToolUse hook handler.

The orchestration spine's phase-advance trigger (DESIGN-orchestration-spine.md
§ 3). Fires after every Write|Edit|MultiEdit (matcher in hooks/hooks.json — Bash is
deliberately excluded, § 3.1). It detects whether the agent just advanced the
project's phase (by comparing `.website-builder/project.yaml.current_phase` against
the `.website-builder/.orchestrator-state` marker) and, on a change, injects the
phase-entry orchestration block.

Injection channel — LOCKED (§ 2): unlike SessionStart (whose plain stdout enters
context), a PostToolUse hook's plain stdout is DROPPED — only JSON
`hookSpecificOutput.additionalContext` enters the model's context. So on a fire
this handler writes:

    {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                            "additionalContext": <block>}}

to stdout and exits 0. On no-change (or pre-bootstrap) it exits 0 SILENTLY (no
output → nothing enters context).

CRASH-PROOF (§ 3.3): this runs after EVERY Write/Edit/MultiEdit — a crash here
would block the user's edits. Any exception → exit 0 with no output. A broken spine
must never block an edit.

Exit code is always 0 (success). Output (when present) is a single JSON object.

Per BUILD-strategy.md + foundation/DESIGN-orchestration-spine.md § 3 + decision 59
(handlers in Python at ${CLAUDE_PLUGIN_ROOT}/hooks-handlers/).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _scripts_dir() -> Path:
    """The plugin's scripts/ dir (sibling of hooks-handlers/), where wb_orchestrate
    lives. Resolved relative to this file so it works regardless of cwd (cwd at hook
    time is the USER's project, not the plugin)."""
    return Path(__file__).resolve().parent.parent / "scripts"


def _read_payload() -> dict:
    """Read the CC PostToolUse payload from stdin. Returns {} on any problem (no
    stdin, malformed JSON) — the marker compare is authoritative, the payload is
    only used for the project dir + (optional) fast-path file check."""
    try:
        raw = sys.stdin.read()
    except Exception:  # noqa: BLE001 — defensive: stdin may be closed/unreadable
        return {}
    if not raw or not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return {}
    return data if isinstance(data, dict) else {}


def _project_root(payload: dict) -> Path:
    """The user-project working directory. Prefer the payload's `cwd` (the dir CC
    ran the tool in); fall back to os.getcwd() (mirrors session_start's
    project_dir())."""
    cwd = payload.get("cwd")
    if isinstance(cwd, str) and cwd.strip():
        try:
            return Path(cwd)
        except (OSError, ValueError):
            pass
    return Path(os.getcwd())


def main() -> int:
    """Run the PostToolUse handler. Always returns 0; emits JSON only on a phase
    advance. Wrapped so no exception escapes (crash-proof contract)."""
    try:
        payload = _read_payload()
        root = _project_root(payload)

        # Ultra-cheap reject: no project.yaml ⇒ greenfield / pre-bootstrap ⇒ nothing
        # to orchestrate. (The marker compare would also no-op, but this skips the
        # scripts/ import entirely on the common no-project edit.)
        if not (root / ".website-builder" / "project.yaml").is_file():
            return 0

        scripts = _scripts_dir()
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        try:
            import wb_orchestrate  # type: ignore
        except Exception:  # noqa: BLE001 — a broken/absent module must not break the hook
            return 0

        result = wb_orchestrate.run_post_tool_use(root)
        if result is None or result.is_empty():
            # Phase unchanged (or nothing to inject) → silent no-op.
            return 0

        block = result.render()
        _emit_json(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": block,
                }
            }
        )
        return 0
    except Exception:  # noqa: BLE001 — crash-proof: never block the user's Edit/Write
        return 0


def _emit_json(obj: dict) -> None:
    """Write a single JSON object to stdout, encoding-safe (Windows consoles may be
    cp1252; the block can contain em-dashes/arrows). Mirrors session_start._emit's
    buffer-first approach."""
    text = json.dumps(obj)
    out = sys.stdout
    buffer = getattr(out, "buffer", None)
    if buffer is not None:
        try:
            buffer.write((text + "\n").encode("utf-8"))
            buffer.flush()
            return
        except Exception:  # noqa: BLE001 — fall through to the str path
            pass
    try:
        print(text, flush=True)
    except UnicodeEncodeError:
        enc = getattr(out, "encoding", None) or "ascii"
        print(text.encode(enc, errors="replace").decode(enc), flush=True)


if __name__ == "__main__":
    sys.exit(main())
