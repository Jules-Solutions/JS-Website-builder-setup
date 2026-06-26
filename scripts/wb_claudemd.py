#!/usr/bin/env python3
"""
scripts/wb_claudemd.py — the project-root CLAUDE.md orientation surface.

Gap #2 of the orchestration-spine remediation program
(`Workstreams/website-builder/foundation/DESIGN-orchestration-spine.md` §7 row #2
+ §9 — Commander CONFIRMED). The plugin writes a STANDING project-root `CLAUDE.md`:
durable, always-loaded orientation that survives even when the plugin isn't loaded
(the user opens the project in plain Claude Code, or on a machine without the
plugin). It COMPLEMENTS the live hooks/skills (which only fire when the plugin is
active) — it does not replace them; the orchestration spine keeps its phase line
fresh on phase entry.

Idempotency — the load-bearing design decision (§9): a DELIMITED MANAGED BLOCK,
NOT write-once. Write-once-whole-file is *incompatible* with "the spine keeps the
phase line fresh" — you cannot refresh a line you never touch after creation. The
managed-block design is the only one that satisfies BOTH stated requirements:
  - never clobber user edits — the user's own content lives OUTSIDE the markers and
    is never touched;
  - keep the phase line fresh — the spine rewrites the managed block (phase + stack
    + cms) from the current `project.yaml`.

Mirrors the `.gitignore` managed-block pattern already proven in
`scripts/wb-bootstrap.py` (`GITIGNORE_START` / `GITIGNORE_END` markers).

Two roles, two entry points:
  - bootstrap CREATES — `write_project_claudemd(project_root, project)`: called by
    `scripts/wb-bootstrap.py` after the `.gitignore` write. Creates the file if
    absent, appends the managed block if the file exists without one, replaces the
    block in place if present. Never raises out.
  - the spine REFRESHES — `refresh_project_claudemd(project_root, project)`: called
    by `scripts/wb_orchestrate.py` on phase entry. DEFENSIVE — no-op if the file is
    absent or has no managed block (the spine only refreshes; it never CREATES, that
    is bootstrap's job). Never raises.

Interface rules (mirror the locked wb_keys.py / wb_markdown.py module contract,
`scripts/README.md` § Interface rules + DESIGN-orchestration-spine.md § 4):
  - IMPORT-SAFE: importing this module has NO side effects (no network, no file
    writes, no subprocess at import time). Pure-function utility + two thin file ops.
  - `project_root` is passed in explicitly — this module never reads `os.getcwd()`.
  - Leaf module: depends on nothing in-repo (consumed by wb-bootstrap.py +
    wb_orchestrate.py; depends on nobody). No `print()` to stdout — the spine's
    PostToolUse handler emits JSON on stdout, so a stray print here would corrupt it.
  - File emit is LF-normalized UTF-8 byte-write (mirrors wb-bootstrap.py write_text)
    so the managed block is byte-identical across OSes and re-rendering an unchanged
    identity produces identical bytes (no git churn).

See also:
  - Workstreams/website-builder/foundation/DESIGN-orchestration-spine.md §7 #2 + §9
  - scripts/wb-bootstrap.py (the .gitignore managed-block pattern this mirrors; the
    bootstrap caller that CREATES the file)
  - scripts/wb_orchestrate.py (the spine caller that REFRESHES the phase line)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# ---------- Managed-block markers (HTML comments — invisible when rendered) ----------
# Wrapped in idempotency markers so the block can be located + replaced in place
# without ever touching the user's own content above/below it.

MANAGED_BEGIN = (
    "<!-- BEGIN website-builder (managed orientation — auto-updated on phase "
    "change; add your own notes OUTSIDE these markers) -->"
)
MANAGED_END = "<!-- END website-builder (managed orientation) -->"

CLAUDEMD_NAME = "CLAUDE.md"


# ---------- Identity extraction ----------

def _fmt_phase(raw: Any) -> str:
    """Render current_phase for the orientation block. Absent/blank → '(not started)'."""
    if raw is None:
        return "(not started)"
    s = str(raw).strip()
    if not s or s.lower() in ("null", "~"):
        return "(not started)"
    return s


def _fmt_choice(raw: Any) -> str:
    """Render a stack/cms choice. None/blank/null → '(not yet chosen)'. A real value
    (including the legitimate cms sentinel 'none') is shown verbatim."""
    if raw is None:
        return "(not yet chosen)"
    s = str(raw).strip()
    if not s or s.lower() in ("null", "~"):
        return "(not yet chosen)"
    return s


def _identity_from_project(project: dict[str, Any]) -> dict[str, str]:
    """Extract the display identity (project name / phase / stack / cms) from a
    loaded project.yaml dict. Name falls back slug → a 'set at phase 1' placeholder
    (bootstrap writes name='' until phase 1 fills it)."""
    name = project.get("name") or project.get("slug") or ""
    name = str(name).strip()
    return {
        "project_name": name or "(project name set at phase 1)",
        "current_phase": _fmt_phase(project.get("current_phase")),
        "stack": _fmt_choice(project.get("stack")),
        "cms": _fmt_choice(project.get("cms")),
    }


# ---------- Managed-block render ----------

def render_managed_block(
    *,
    project_name: str,
    current_phase: str,
    stack: str,
    cms: str,
) -> str:
    """Render the managed orientation block (markers inclusive). DETERMINISTIC — no
    timestamp — so re-rendering an unchanged identity yields identical bytes (no git
    churn). Ends with a trailing newline."""
    lines = [
        MANAGED_BEGIN,
        f"# {project_name}",
        "",
        "> Built with the **website-builder** Claude Code plugin. The plugin keeps "
        "this block",
        "> current as your project advances — edits *inside* the markers are "
        "overwritten on",
        "> phase change. Put your own project notes **outside** the markers; those "
        "are never touched.",
        "",
        f"- **Project:** {project_name}",
        f"- **Current phase:** {current_phase}",
        f"- **Stack:** {stack}",
        f"- **CMS:** {cms}",
        "- **State:** `.website-builder/` — `project.yaml` is the canonical project "
        "state.",
        "",
        "## How to resume",
        "",
        "Open this project in Claude Code with the website-builder plugin installed. "
        "Its",
        "SessionStart hook reads `.website-builder/project.yaml` and resumes at the "
        "current",
        "phase; the orchestration spine re-injects that phase's resources, skill "
        "discipline,",
        "and stack/CMS adapter guidance. Tell the agent what you want to do next — it "
        "knows",
        "where you are in the build.",
        "",
        "If the plugin isn't loaded, `.website-builder/project.yaml` still records "
        "your phase,",
        "stack, CMS, and locked choices so any agent can orient from it.",
        MANAGED_END,
    ]
    return "\n".join(lines) + "\n"


# ---------- Managed-block upsert (pure text in → text out) ----------

def upsert_managed_block(existing: str | None, block: str) -> str:
    """Insert/replace the managed block into a CLAUDE.md document.

    - existing is None / blank → return the block alone (fresh file).
    - existing carries both markers → replace the marker region IN PLACE, preserving
      the user's content before/after (blank-line separated).
    - existing has no markers → append the block after the user's content.

    `block` must start with MANAGED_BEGIN and end with MANAGED_END (+ newline).
    Always returns LF-joined content ending in exactly one newline.
    """
    block_clean = block.strip("\n")

    if existing is None or not existing.strip():
        return block_clean + "\n"

    begin = existing.find(MANAGED_BEGIN)
    end = existing.find(MANAGED_END)
    if begin != -1 and end != -1 and end > begin:
        before = existing[:begin]
        after = existing[end + len(MANAGED_END):]
        return _join_around(before, block_clean, after)

    # No managed block present → append after the user's content.
    return _join_around(existing, block_clean, "")


def _join_around(before: str, block_clean: str, after: str) -> str:
    """Join user-content-before + managed-block + user-content-after with a single
    blank-line separator on each side that has content. Returns LF content ending in
    one newline."""
    parts: list[str] = []
    if before.strip():
        parts.append(before.rstrip("\n"))
        parts.append("")
    parts.append(block_clean)
    if after.strip():
        parts.append("")
        parts.append(after.strip("\n"))
    return "\n".join(parts) + "\n"


# ---------- File ops ----------

def _write_text(path: Path, content: str) -> None:
    """LF + binary write → byte-identical across OSes (mirrors wb-bootstrap.py)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))


def write_project_claudemd(project_root: Path, project: dict[str, Any]) -> str:
    """Bootstrap entry — create/update the project-root CLAUDE.md managed block.

    Returns "created" | "updated" | "unchanged". Best-effort: never raises out (a
    CLAUDE.md failure must not fail bootstrap)."""
    try:
        path = project_root / CLAUDEMD_NAME
        block = render_managed_block(**_identity_from_project(project))
        existing: str | None
        try:
            existing = path.read_text(encoding="utf-8") if path.is_file() else None
        except OSError:
            existing = None
        new_content = upsert_managed_block(existing, block)
        if existing is not None and new_content == existing:
            return "unchanged"
        _write_text(path, new_content)
        return "updated" if existing is not None else "created"
    except Exception:  # noqa: BLE001 — a CLAUDE.md write must never break bootstrap
        return "error"


def refresh_project_claudemd(
    project_root: Path, project: dict[str, Any] | None
) -> str | None:
    """Spine entry — refresh the managed orientation block (phase line + stack/cms)
    from the current project.yaml.

    DEFENSIVE — never raises:
      - file absent → None (the spine never CREATES the file; bootstrap does)
      - `project` is None → None (caller owns the project.yaml read; keeps this a leaf)
      - file present WITHOUT the managed block → None (the spine only refreshes,
        never injects a block into a user-authored CLAUDE.md)
      - file present WITH the block → rewrite the block; returns "refreshed" |
        "unchanged".
    """
    try:
        if project is None:
            return None
        path = project_root / CLAUDEMD_NAME
        if not path.is_file():
            return None
        existing = path.read_text(encoding="utf-8")
        if MANAGED_BEGIN not in existing or MANAGED_END not in existing:
            return None
        block = render_managed_block(**_identity_from_project(project))
        new_content = upsert_managed_block(existing, block)
        if new_content == existing:
            return "unchanged"
        _write_text(path, new_content)
        return "refreshed"
    except Exception:  # noqa: BLE001 — the CLAUDE.md refresh must never break the spine
        return None
