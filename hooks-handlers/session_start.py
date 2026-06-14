#!/usr/bin/env python3
"""
website-builder — SessionStart hook handler.

Fires on Claude Code session start (per Anthropic CC plugin hook spec). The handler:

1. Inspects the current working directory (which is the user's project — NOT the
   plugin install dir; ${CLAUDE_PLUGIN_ROOT} points at the plugin, but cwd at
   session start is the user's project).
2. Detects whether the user is mid-project (`.website-builder/` state dir exists)
   or fresh (one of 5 entry modes per locked decision 15).
3. If mid-project: reads `state.yaml` + `project.yaml` + surfaces current phase,
   languages, stack, completion progress.
4. If fresh: detects which entry mode applies by scanning for stack-specific
   markers (Framer / Next.js / Astro / WordPress / Hugo / SvelteKit / etc.) and
   AI-output / Figma indicators.
5. Emits a context block to stdout. CC injects the stdout of SessionStart hooks
   into the session as additional context the agent reads at startup.

The handler **does not** initialize `.website-builder/` — that is the
`wb-bootstrap` skill's job (Captain D, locked decision 43). The hook only
reports.

Per BUILD-strategy.md Phase 1 line 113-118 + foundation/DESIGN-architecture.md
lines 233-238 + lines 240-249 + DESIGN-project-scaffold.md.

Exit code 0 = success (output is appended to session context).
Exit code != 0 = error (output goes to user-visible error log; session
proceeds without the context block).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


# Stack-specific markers used for entry-mode detection. Order matters slightly:
# more specific markers come first within their group so we report the strongest
# signal. See foundation/DESIGN-architecture.md lines 240-249 for spec.
EXISTING_SITE_MARKERS: list[tuple[str, str]] = [
    # (filename or dirname, human-readable stack label)
    (".framer", "Framer (project metadata dir)"),
    ("framer.config.json", "Framer (config)"),
    ("wp-config.php", "WordPress"),
    ("wp-content", "WordPress (theme/plugin dir)"),
    ("next.config.js", "Next.js"),
    ("next.config.mjs", "Next.js"),
    ("next.config.ts", "Next.js"),
    ("astro.config.mjs", "Astro"),
    ("astro.config.ts", "Astro"),
    ("astro.config.js", "Astro"),
    ("hugo.toml", "Hugo"),
    ("hugo.yaml", "Hugo"),
    ("config.toml", "Hugo (legacy config)"),
    ("svelte.config.js", "SvelteKit"),
    ("svelte.config.ts", "SvelteKit"),
    ("nuxt.config.js", "Nuxt"),
    ("nuxt.config.ts", "Nuxt"),
    ("gatsby-config.js", "Gatsby"),
    ("gatsby-config.ts", "Gatsby"),
    ("vite.config.js", "Vite"),
    ("vite.config.ts", "Vite"),
    # Webflow exports often look like static-html with a specific structure;
    # a top-level webflow marker file is rare but possible:
    ("webflow.json", "Webflow"),
]

# Regex / suffix-based markers handled separately
FRAMER_ATTEMPT_MARKERS: list[str] = [".framer"]
FIGMA_FILE_SUFFIX = ".fig"

# AI-output detection: a single .html file at root + size hint + filename hint.
# We keep this conservative — false positives here mean the user gets nudged
# toward phase 6.5 unnecessarily. The user-prompt confirmation in wb-bootstrap
# resolves any disagreement.
AI_OUTPUT_FILENAME_HINTS: tuple[str, ...] = (
    "claude",
    "chatgpt",
    "gpt",
    "v0",
    "lovable",
    "bolt",
    "cursor",
    "ai-output",
    "generated",
)


def project_dir() -> Path:
    """Return the user-project working directory."""
    return Path.cwd()


def state_dir(root: Path) -> Path:
    """Return the .website-builder/ state directory (may not exist yet)."""
    return root / ".website-builder"


def has_state_dir(root: Path) -> bool:
    """Has the user already bootstrapped this project with website-builder?"""
    sd = state_dir(root)
    return sd.is_dir()


def list_top_level(root: Path) -> set[str]:
    """Return set of top-level filenames + dirnames in root.

    Excludes `.git`, `node_modules`, and other heavy dirs to keep this fast.
    """
    skip = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache"}
    try:
        return {p.name for p in root.iterdir() if p.name not in skip}
    except (OSError, PermissionError):
        return set()


def find_stack_markers(root: Path) -> list[tuple[str, str]]:
    """Return list of (marker, label) for any stack markers found at root."""
    top = list_top_level(root)
    found: list[tuple[str, str]] = []
    for marker, label in EXISTING_SITE_MARKERS:
        if marker in top:
            found.append((marker, label))
    return found


def find_figma_files(root: Path) -> list[str]:
    """Return list of .fig filenames at root (Figma files)."""
    try:
        return sorted(p.name for p in root.iterdir() if p.suffix == FIGMA_FILE_SUFFIX)
    except (OSError, PermissionError):
        return []


def find_root_html(root: Path) -> list[Path]:
    """Return list of .html files at root (used for AI-output detection)."""
    try:
        return sorted(p for p in root.iterdir() if p.suffix.lower() == ".html" and p.is_file())
    except (OSError, PermissionError):
        return []


def looks_like_ai_output(html_files: list[Path]) -> bool:
    """Heuristic: a single .html file at root, name hints at AI tool output, OR
    the file is large enough to plausibly be a one-shot generated landing page.

    Conservative — we'd rather miss a true positive (and let bootstrap ask the
    user) than false-positive on a normal static site.
    """
    if len(html_files) != 1:
        return False
    name = html_files[0].name.lower()
    if any(hint in name for hint in AI_OUTPUT_FILENAME_HINTS):
        return True
    # Size hint: AI-generated landing pages tend to be 30-200 KB single files.
    # We don't enforce this — name-hint is the strong signal. Size alone is
    # too noisy.
    return False


def is_effectively_empty(root: Path) -> bool:
    """Greenfield: dir is empty or contains only .git/ + a few trivial files."""
    top = list_top_level(root)
    trivial = {"README.md", "LICENSE", ".gitignore", ".gitattributes"}
    return all(name in trivial for name in top)


def detect_entry_mode(root: Path) -> dict:
    """Detect the entry mode per locked decision 15.

    Returns a dict with at least `mode` (one of greenfield / has-existing-site
    / has-AI-output / has-Framer-attempt / has-Figma-file) and any
    mode-specific signals.

    The 5 modes are defined in foundation/DESIGN-architecture.md lines 240-249.
    Signals can overlap; we apply the spec's implicit precedence:
    has-Framer-attempt > has-existing-site (Framer is the strongest signal because
    of the cosplay test target), then has-Figma-file > has-AI-output > greenfield.
    """
    figma_files = find_figma_files(root)
    if figma_files:
        return {
            "mode": "has-Figma-file",
            "figma_files": figma_files,
            "signal": (
                f"Found {len(figma_files)} Figma file(s) at project root: "
                + ", ".join(figma_files)
            ),
        }

    stack_markers = find_stack_markers(root)
    framer_markers = [m for m, _ in stack_markers if m in FRAMER_ATTEMPT_MARKERS]
    if framer_markers:
        return {
            "mode": "has-Framer-attempt",
            "markers": [{"marker": m, "label": label} for m, label in stack_markers],
            "signal": (
                "Found Framer project metadata; treating as has-Framer-attempt "
                "(may be incomplete — phase 6.5 walks the artifact)."
            ),
        }

    if stack_markers:
        return {
            "mode": "has-existing-site",
            "markers": [{"marker": m, "label": label} for m, label in stack_markers],
            "signal": (
                "Detected existing-site stack markers: "
                + ", ".join(label for _, label in stack_markers)
            ),
        }

    html_files = find_root_html(root)
    if looks_like_ai_output(html_files):
        return {
            "mode": "has-AI-output",
            "ai_output_file": html_files[0].name,
            "signal": (
                f"Single .html file at root ({html_files[0].name}) — looks like "
                "one-shot AI-output."
            ),
        }

    if is_effectively_empty(root):
        return {
            "mode": "greenfield",
            "signal": "Project directory is empty (or contains only trivial files).",
        }

    # Anything else: ambiguous. Default to has-existing-site without specific
    # markers — the bootstrap skill will ask the user for clarification.
    return {
        "mode": "ambiguous",
        "top_level": sorted(list_top_level(root)),
        "signal": (
            "No definitive entry-mode markers found, but directory is non-empty. "
            "The wb-bootstrap skill will ask the user for clarification."
        ),
    }


def read_state_yaml(state_path: Path) -> dict | None:
    """Best-effort read of .website-builder/state.yaml or project.yaml.

    PyYAML is not in the plugin's runtime dependencies (the plugin ships as a
    directory of markdown + handlers; we do not own the user's Python env).
    Use a tolerant minimal parser: we only need a handful of top-level scalar
    keys, so a regex-style read is sufficient.

    Returns None if the file is absent or unreadable.
    """
    if not state_path.exists():
        return None
    try:
        text = state_path.read_text(encoding="utf-8")
    except OSError:
        return None

    parsed: dict = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            continue
        # Skip nested keys (only top-level scalars are read here)
        if line.startswith((" ", "\t")):
            continue
        key, _, raw_value = stripped.partition(":")
        key = key.strip()
        raw_value = raw_value.strip()
        if not raw_value:
            continue
        # Strip simple quoting
        if raw_value.startswith(("'", '"')) and raw_value.endswith(("'", '"')):
            raw_value = raw_value[1:-1]
        parsed[key] = raw_value
    return parsed


def read_project_state(root: Path) -> dict | None:
    """Read .website-builder/project.yaml if present.

    Returns dict with whatever scalar fields are extractable, or None if absent.
    """
    sd = state_dir(root)
    if not sd.is_dir():
        return None
    project_yaml = sd / "project.yaml"
    return read_state_yaml(project_yaml)


# ---------------------------------------------------------------------------
# Phase-5 runtime interlocks (wired here at Phase 6 per RPT-phase-5-stage-
# completion.md follow-up #1 + RPT-phase-5-captain-q.md follow-up #1).
#
# Two Phase-5 modules ship callable-but-unwired: scripts/wb_library.py's
# `autoclone_for_state` (project.yaml-derived resource auto-clone, Captain P) and
# scripts/wb_keys.py's `resolve_keys` (secrets resolution, Captain Q). This hook
# is where they become live. Both run ONLY on the mid-project path (a
# `.website-builder/` state dir exists) — a fresh project has no project.yaml /
# keys.yaml for them to read.
#
# DEFENSIVE CONTRACT (this file runs on EVERY website-builder CC session — a
# crash here breaks every user session):
#   - imports are guarded (the modules live in scripts/, may be absent in a
#     partially-installed plugin) — matching the `try: import yaml` idiom the
#     sibling modules already use;
#   - every call is wrapped so no exception escapes into main();
#   - resolve_keys NEVER has its resolved VALUES logged — only counts + names +
#     the (value-free) fix-path message on KeyResolutionError (per
#     .claude/rules/secrets-conventions.md + the hook-development skill's
#     "DON'T log sensitive information" rule);
#   - autoclone_for_state records clone INTENT at session-start (the module
#     defers the actual network fetch — DESIGN-resource-curation line 138), so
#     this stays fast + offline-safe inside the 30s SessionStart timeout.
# ---------------------------------------------------------------------------


def _scripts_dir() -> Path:
    """The plugin's scripts/ dir (sibling of hooks-handlers/), where the Phase-5
    runtime modules live. Resolved relative to this file so it works regardless
    of cwd (cwd at session-start is the USER's project, not the plugin)."""
    return Path(__file__).resolve().parent.parent / "scripts"


def run_autoclone(root: Path) -> dict | None:
    """Invoke scripts/wb_library.autoclone_for_state for the session-start trigger.

    Import-safe + non-fatal: a missing module, an unreadable project.yaml, or any
    runtime error yields a structured note (never an exception). Returns a dict
    summary for the context block, or None if the module is unavailable.
    """
    scripts = _scripts_dir()
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    try:
        import wb_library  # type: ignore
    except Exception as exc:  # noqa: BLE001 — defensive: a broken/absent module must not break the hook
        return {"available": False, "error": f"wb_library import failed: {exc}"}

    log_lines: list[str] = []
    try:
        results = wb_library.autoclone_for_state(
            root, trigger="session-start", log=log_lines.append
        )
    except Exception as exc:  # noqa: BLE001 — defensive: autoclone must never crash session-start
        return {"available": True, "error": f"autoclone_for_state raised: {exc}"}

    # CloneResult is a dataclass; summarize without assuming attribute presence.
    summary: list[dict] = []
    for r in results:
        summary.append(
            {
                "resource": getattr(r, "resource", "?"),
                "status": getattr(r, "status", "?"),
                "target": getattr(r, "target", None),
                "reason": getattr(r, "reason", ""),
            }
        )
    return {
        "available": True,
        "count": len(summary),
        "results": summary,
        "log": log_lines,
    }


def run_resolve_keys(root: Path) -> dict | None:
    """Invoke scripts/wb_keys.resolve_keys for the project.

    Import-safe + non-fatal + SECRET-SAFE: never returns or logs a resolved
    value. Surfaces only:
      - the count of resolved keys + their env-var NAMES (not values), OR
      - the value-free fix-path message when required keys can't be resolved
        (KeyResolutionError), OR
      - a "no keys.yaml yet" note (KeysError — the project hasn't run bootstrap's
        secrets step), OR
      - a generic defensive note on any other error.
    Returns a dict summary for the context block, or None if the module is
    unavailable.
    """
    scripts = _scripts_dir()
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    try:
        import wb_keys  # type: ignore
    except Exception as exc:  # noqa: BLE001 — defensive: a broken/absent module must not break the hook
        return {"available": False, "error": f"wb_keys import failed: {exc}"}

    try:
        resolved = wb_keys.resolve_keys(root)
    except wb_keys.KeyResolutionError as exc:
        # The fix-path message is value-free by contract (names keys + sources +
        # fix paths, never secret values). Safe to surface verbatim.
        return {
            "available": True,
            "status": "unresolved",
            "unresolved_count": len(getattr(exc, "unresolved", []) or []),
            "fix_message": str(exc),
        }
    except wb_keys.KeysError as exc:
        # No keys.yaml yet (or another typed keys error) — the secrets registry
        # hasn't been initialized. Not an error condition for the hook.
        return {"available": True, "status": "no-registry", "note": str(exc)}
    except Exception as exc:  # noqa: BLE001 — defensive: resolve_keys must never crash session-start
        return {"available": True, "status": "error", "error": f"resolve_keys raised: {exc}"}

    # SECRET-SAFE: surface only the NAMES of resolved keys, never the values.
    return {
        "available": True,
        "status": "resolved",
        "count": len(resolved),
        "env_vars": sorted(resolved.keys()),
    }


def render_context(
    *,
    root: Path,
    state_present: bool,
    entry: dict,
    project: dict | None,
    autoclone: dict | None = None,
    keys: dict | None = None,
) -> str:
    """Render the context block injected into the session.

    The agent reads this at session start. Format is markdown for readability;
    structured JSON is appended for any downstream programmatic consumer.

    `autoclone` / `keys` are the (optional) Phase-5 runtime-interlock summaries
    from run_autoclone() / run_resolve_keys() — present on the mid-project path,
    None otherwise. Both are already secret-safe (run_resolve_keys never returns
    a resolved value).
    """
    lines: list[str] = []
    lines.append("# website-builder — session context")
    lines.append("")
    lines.append(f"Project root: `{root}`")
    lines.append("")

    if state_present:
        lines.append("## Mid-project (`.website-builder/` exists)")
        lines.append("")
        if project:
            current_phase = project.get("current_phase", "?")
            stack = project.get("stack", "(not yet picked)")
            cms = project.get("cms", "(not yet picked)")
            entry_mode = project.get("entry_mode", "(not recorded)")
            languages = project.get("languages", "(not recorded)")
            transactional = project.get("transactional", "(not recorded)")
            lines.append(f"- Current phase: **{current_phase}**")
            lines.append(f"- Entry mode: {entry_mode}")
            lines.append(f"- Stack: {stack}")
            lines.append(f"- CMS: {cms}")
            lines.append(f"- Languages: {languages}")
            lines.append(f"- Transactional: {transactional}")
            lines.append("")
            lines.append(
                "The website-builder agent should resume at the current phase. "
                "Phase 6.5 (artifact ingestion) remains available at any time — "
                "if the user describes a new artifact (URL, Figma file, AI-output, "
                "freelancer delivery), invoke phase 6.5 to integrate it."
            )
        else:
            lines.append(
                "- `.website-builder/` directory exists but `project.yaml` is "
                "missing or unreadable. Suggest running `wb-bootstrap` to "
                "reconcile state."
            )
        lines.append("")
        _render_autoclone_section(lines, autoclone)
        _render_keys_section(lines, keys)
    else:
        lines.append("## Fresh project (no `.website-builder/` state yet)")
        lines.append("")
        lines.append(f"- Detected entry mode: **{entry['mode']}**")
        lines.append(f"- Signal: {entry.get('signal', '(no signal)')}")
        if "markers" in entry:
            lines.append("- Markers found:")
            for m in entry["markers"]:
                lines.append(f"  - `{m['marker']}` — {m['label']}")
        if "figma_files" in entry:
            lines.append(f"- Figma files: {', '.join(entry['figma_files'])}")
        if "ai_output_file" in entry:
            lines.append(f"- AI-output file: `{entry['ai_output_file']}`")
        if "top_level" in entry:
            lines.append(f"- Top-level entries: {', '.join(entry['top_level'][:20])}")
        lines.append("")
        lines.append(
            "The user has not yet run the bootstrap skill. When they ask for "
            "help building or improving a website, invoke the `wb-bootstrap` "
            "skill — it confirms the entry mode, initializes `.website-builder/`, "
            "fetches upstream skills, and routes into phase 1 (greenfield) or "
            "phase 6.5 (any other entry mode)."
        )
        if entry["mode"] in ("has-existing-site", "has-Framer-attempt", "has-AI-output", "has-Figma-file"):
            lines.append("")
            lines.append(
                "Phase 6.5 (artifact ingestion) is the right entry point for this "
                "mode — it walks the existing artifact, extracts design tokens + "
                "content + structure, and integrates into project state without "
                "losing the user's prior work."
            )

    lines.append("")
    lines.append("## Machine-readable summary")
    lines.append("")
    lines.append("```json")
    payload = {
        "plugin": "website-builder",
        "project_root": str(root),
        "state_present": state_present,
        "entry_mode": entry["mode"] if not state_present else None,
        "entry_signals": {k: v for k, v in entry.items() if k != "mode"} if not state_present else None,
        "project_state": project,
        # Phase-5 runtime interlocks (mid-project path only; None on fresh
        # projects). `keys` is secret-safe — it carries env-var NAMES + counts +
        # value-free fix messages, never resolved secret values.
        "autoclone": autoclone,
        "keys": keys,
    }
    lines.append(json.dumps(payload, indent=2, default=str))
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def _render_autoclone_section(lines: list[str], autoclone: dict | None) -> None:
    """Append the resource auto-clone summary (from run_autoclone) to `lines`."""
    if not autoclone:
        return
    lines.append("## Resource library (auto-clone)")
    lines.append("")
    if not autoclone.get("available"):
        lines.append(
            f"- Resource auto-clone unavailable: {autoclone.get('error', 'unknown')}"
        )
        lines.append("")
        return
    if "error" in autoclone:
        lines.append(f"- Resource auto-clone error (non-fatal): {autoclone['error']}")
        lines.append("")
        return
    results = autoclone.get("results", [])
    if not results:
        lines.append(
            "- No resource auto-clones for the current project state "
            "(nothing picked yet, or all referenced resources already present)."
        )
        lines.append("")
        return
    lines.append(
        f"- {autoclone.get('count', len(results))} resource(s) considered for "
        "the project-local library (`.website-builder/library/`):"
    )
    for r in results:
        target = r.get("target")
        target_str = f" -> library/{target}" if target else ""
        reason = r.get("reason", "")
        reason_str = f" ({reason})" if reason else ""
        lines.append(f"  - `{r.get('resource')}` [{r.get('status')}]{target_str}{reason_str}")
    lines.append("")
    lines.append(
        "Network fetches are deferred — the agent (or `wb library add`/`refresh`) "
        "performs the actual clone on demand. Session-start records intent only."
    )
    lines.append("")


def _render_keys_section(lines: list[str], keys: dict | None) -> None:
    """Append the secrets-resolution summary (from run_resolve_keys) to `lines`.

    SECRET-SAFE: only counts, env-var names, and value-free fix messages are
    rendered — never a resolved secret value.
    """
    if not keys:
        return
    lines.append("## Secrets / keys")
    lines.append("")
    if not keys.get("available"):
        lines.append(f"- Secrets resolution unavailable: {keys.get('error', 'unknown')}")
        lines.append("")
        return
    status = keys.get("status")
    if status == "resolved":
        count = keys.get("count", 0)
        env_vars = keys.get("env_vars", [])
        lines.append(f"- {count} key(s) resolved for this project (env vars set for child processes):")
        if env_vars:
            lines.append(f"  - {', '.join(env_vars)}")
        lines.append("")
    elif status == "no-registry":
        lines.append(
            "- No `keys.yaml` secrets registry yet — the project hasn't run the "
            "bootstrap secrets step. (Run `wb-bootstrap` / `wb maintain reconfig` "
            "if this project needs API keys.)"
        )
        lines.append("")
    elif status == "unresolved":
        lines.append(
            f"- {keys.get('unresolved_count', 0)} required key(s) could not be "
            "resolved. Fix path (no secret values shown):"
        )
        for fixline in str(keys.get("fix_message", "")).splitlines():
            lines.append(f"  > {fixline}" if fixline.strip() else "  >")
        lines.append("")
    else:  # "error" or unexpected
        lines.append(f"- Secrets resolution error (non-fatal): {keys.get('error', 'unknown')}")
        lines.append("")


def _emit(text: str) -> None:
    """Write the context block to stdout, never crashing on console encoding.

    SessionStart hooks run under whatever console encoding the user's terminal
    has. On Windows that's often cp1252 / cp437, which can't encode every
    character (e.g. an arrow or em-dash). A bare print() raising
    UnicodeEncodeError would non-zero-exit the hook on every such session — a
    high-blast-radius failure for a hook that runs on EVERY website-builder
    session. We write to the underlying buffer as UTF-8 when we can, and fall
    back to an ASCII-safe replacement encoding otherwise. Either way the hook
    keeps exit 0 + emits readable context.
    """
    out = sys.stdout
    buffer = getattr(out, "buffer", None)
    if buffer is not None:
        try:
            buffer.write((text + "\n").encode("utf-8"))
            buffer.flush()
            return
        except Exception:  # noqa: BLE001 — defensive: fall through to the str path below
            pass
    try:
        print(text, flush=True)
    except UnicodeEncodeError:
        enc = getattr(out, "encoding", None) or "ascii"
        print(text.encode(enc, errors="replace").decode(enc), flush=True)


def main() -> int:
    """Run the SessionStart handler.

    The hook does NOT consume any payload from CC for SessionStart — there is no
    tool invocation context at session start. We simply emit a context block.
    """
    root = project_dir()

    # If the cwd is the plugin's own dir (developer testing), don't try to
    # detect entry mode against the plugin's own scaffold — that's noise.
    plugin_root_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root_env:
        try:
            if root.resolve() == Path(plugin_root_env).resolve():
                # Developer is in the plugin repo itself, not a user project.
                # Emit a brief diagnostic and return.
                _emit(
                    "# website-builder — session context\n\n"
                    f"cwd is the plugin install dir (`{root}`); skipping entry-mode "
                    "detection. Open a user-project directory to activate the plugin's "
                    "session-start logic."
                )
                return 0
        except (OSError, ValueError):
            # If resolve fails, fall through to normal detection.
            pass

    state_present = has_state_dir(root)
    autoclone: dict | None = None
    keys: dict | None = None
    if state_present:
        entry: dict = {"mode": "mid-project", "signal": "`.website-builder/` exists"}
        project = read_project_state(root)
        # Phase-5 runtime interlocks — only meaningful once the project has state
        # (autoclone reads project.yaml; resolve_keys reads keys.yaml). Both are
        # internally defensive (they never raise out), but main() must stay
        # crash-proof regardless, so belt-and-suspenders try/except here too.
        try:
            autoclone = run_autoclone(root)
        except Exception as exc:  # noqa: BLE001 — last-resort guard: session-start must never crash
            autoclone = {"available": True, "error": f"run_autoclone wrapper raised: {exc}"}
        try:
            keys = run_resolve_keys(root)
        except Exception as exc:  # noqa: BLE001 — last-resort guard: session-start must never crash
            keys = {"available": True, "status": "error", "error": f"run_resolve_keys wrapper raised: {exc}"}
    else:
        entry = detect_entry_mode(root)
        project = None

    _emit(
        render_context(
            root=root,
            state_present=state_present,
            entry=entry,
            project=project,
            autoclone=autoclone,
            keys=keys,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
