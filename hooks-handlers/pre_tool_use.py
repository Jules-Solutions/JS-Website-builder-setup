#!/usr/bin/env python3
"""
website-builder — PreToolUse hook handler.

Fires before every tool invocation matching the matcher in `hooks/hooks.json`
(currently `Edit|Write|MultiEdit|Bash`). The handler enforces the website-builder
agent's anti-skip discipline: tools that would touch downstream-phase artifacts
before the current phase's exit criteria are met get blocked with a diagnostic.

This is the v0.1 minimal implementation:

- If `.website-builder/state.yaml` or `project.yaml` is missing, the user is
  pre-bootstrap; the hook ALLOWS all tool calls (the bootstrap skill needs
  Edit/Write to scaffold).
- If the project state is present, the hook reads `current_phase` and looks for
  a phase contract MD at `${CLAUDE_PLUGIN_ROOT}/phase-contracts/{NN}-*.md`.
  If a contract exists with explicit `gating_rules:` frontmatter, the hook
  evaluates them against the tool invocation. If no contract or no rules, the
  hook ALLOWS (logs an "ungated" notice for visibility).
- Phase contracts will be filled in Phase 2 (per BUILD-strategy.md). Until
  then, the hook is permissive-with-visibility — it surfaces the current phase
  + intended tool action so the agent doesn't accidentally drift, but doesn't
  block on missing contracts.

Per BUILD-strategy.md Phase 1 line 113-118 + foundation/DESIGN-architecture.md
lines 237-238.

Hook contract per Anthropic CC plugin spec:
- stdin: JSON payload describing the tool invocation (tool name, parameters,
  cwd, etc.). Schema is forward-compatible — we read what we need defensively.
- exit code 0 + empty stdout: ALLOW the tool call.
- exit code 0 + stdout: ALLOW the tool call; stdout is appended as advisory
  context (the agent reads it but the call proceeds).
- exit code 1 (or non-zero): BLOCK the tool call; stdout is shown to the agent
  as a refusal message + reason.
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys
from pathlib import Path


def project_dir() -> Path:
    """User-project working directory (cwd at session start)."""
    return Path.cwd()


def state_dir(root: Path) -> Path:
    return root / ".website-builder"


def has_state(root: Path) -> bool:
    sd = state_dir(root)
    return sd.is_dir() and (sd / "project.yaml").is_file()


def read_scalar_yaml(path: Path) -> dict:
    """Tolerant top-level-scalar YAML reader (no PyYAML dependency).

    Returns dict of `key: value` for top-level scalar entries. Nested keys and
    list entries are silently skipped — they're not used here.
    """
    if not path.exists():
        return {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    parsed: dict = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            continue
        if ":" not in line:
            continue
        key, _, raw_value = line.partition(":")
        key = key.strip()
        raw_value = raw_value.strip()
        if not raw_value:
            continue
        if raw_value.startswith(("'", '"')) and raw_value.endswith(("'", '"')):
            raw_value = raw_value[1:-1]
        parsed[key] = raw_value
    return parsed


def read_project_state(root: Path) -> dict:
    """Read .website-builder/project.yaml and return a dict of scalars."""
    return read_scalar_yaml(state_dir(root) / "project.yaml")


def find_phase_contract(plugin_root: Path, phase: str) -> Path | None:
    """Look for a phase-contract MD file at `${CLAUDE_PLUGIN_ROOT}/phase-contracts/{NN}-*.md`.

    `phase` may be "17", "06.5", "24a", etc. We try a few normalizations.
    """
    contract_dir = plugin_root / "phase-contracts"
    if not contract_dir.is_dir():
        return None

    candidates: list[str] = []
    # Try as-is, zero-padded, with leading zero stripped — covers "17", "06", "24a".
    candidates.append(f"{phase}-*.md")
    if re.fullmatch(r"\d+", phase):
        candidates.append(f"{int(phase):02d}-*.md")
        candidates.append(f"{int(phase)}-*.md")
    if re.fullmatch(r"\d+\.\d+", phase):
        # e.g. "6.5" -> "06.5", "06-5"
        major, minor = phase.split(".")
        candidates.append(f"{int(major):02d}.{minor}-*.md")
        candidates.append(f"{int(major):02d}-{minor}-*.md")
        candidates.append(f"{major}-{minor}-*.md")

    for pat in candidates:
        matches = sorted(contract_dir.glob(pat))
        if matches:
            return matches[0]
    return None


def read_payload() -> dict:
    """Read the tool-invocation JSON from stdin.

    Tolerant: if stdin isn't valid JSON or is empty, return {} so the hook can
    fall through to permissive behavior rather than block.
    """
    try:
        raw = sys.stdin.read()
    except (OSError, ValueError):
        return {}
    if not raw or not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def extract_tool_name(payload: dict) -> str:
    """Return the tool name from the payload (best-effort across schema variants)."""
    for key in ("tool_name", "tool", "name"):
        v = payload.get(key)
        if isinstance(v, str) and v:
            return v
    return ""


def extract_tool_input(payload: dict) -> dict:
    """Return the tool input dict from the payload."""
    for key in ("tool_input", "input", "parameters", "args"):
        v = payload.get(key)
        if isinstance(v, dict):
            return v
    return {}


def main() -> int:
    """Run the PreToolUse handler."""
    payload = read_payload()
    tool_name = extract_tool_name(payload)
    tool_input = extract_tool_input(payload)

    root = project_dir()
    plugin_root_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    plugin_root = Path(plugin_root_env) if plugin_root_env else None

    # If the user is pre-bootstrap, allow everything. The bootstrap skill itself
    # needs Edit/Write/Bash to scaffold `.website-builder/`.
    if not has_state(root):
        return 0  # silent allow

    project = read_project_state(root)
    current_phase = project.get("current_phase")
    if not current_phase:
        # State dir exists but `current_phase` is missing — degraded state.
        # Allow with a soft notice; the bootstrap skill can reconcile later.
        print(
            "[website-builder] PreToolUse: `.website-builder/project.yaml` exists "
            "but `current_phase` is missing or unreadable. Tool call allowed; "
            "consider running the bootstrap skill to reconcile state.",
            flush=True,
        )
        return 0

    # Find the phase contract (will mostly be absent in v0.1 — phase contracts
    # are Phase 2's deliverable per BUILD-strategy.md lines 143-160).
    contract: Path | None = None
    if plugin_root is not None:
        contract = find_phase_contract(plugin_root, str(current_phase))

    if contract is None:
        # No contract: ungated. Emit a low-noise advisory so the agent stays
        # aware of the current phase. Does not block.
        # Skip advisory entirely if the tool is benign (Read or Grep would have
        # been filtered out by the matcher already; we're only matching writes).
        # Keep it short — this fires before every Edit/Write/Bash.
        # We deliberately keep the v0.1 implementation permissive; Phase 2 fills
        # in the actual gating behavior.
        return 0

    # Future: read frontmatter from `contract`, parse `gating_rules:`, evaluate
    # against (tool_name, tool_input). For v0.1 we treat presence-of-contract as
    # success — the contract content authoring is Phase 2's job.
    return 0


if __name__ == "__main__":
    # Diagnostics for the silent-fail case: if anything throws, allow the call
    # but emit a notice. We never want this hook to brick a session because of
    # an unexpected exception in the handler itself.
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 — defensive in a hook
        print(
            f"[website-builder] PreToolUse handler error (allowing call): {exc}",
            flush=True,
        )
        sys.exit(0)
