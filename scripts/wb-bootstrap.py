#!/usr/bin/env python3
"""
scripts/wb-bootstrap.py — non-interactive runner for the website-builder plugin's
first-run bootstrap.

This script DRIVES the `wb-bootstrap` skill (`skills/wb-bootstrap/SKILL.md`)
programmatically against a project directory. It's the test-harness sibling of
the in-CC interactive flow — the SKILL.md guides a live agent through 9 steps
with `AskUserQuestion` prompts; this runner replays the same 9 steps without
prompts, supplying answers via flags / env vars / sensible defaults driven by
the project's detected entry mode.

Contract: invoked with cwd = the user's project directory, NO argv args by
default (matching `tests/smoke_test.py::TestBootstrapSkill`'s invocation
pattern: `[sys.executable, str(self.runner)]` + `cwd=tempdir`). Reads
`Path.cwd()` to find the project. Flags below permit override for CLI usage.

Per locked decisions in `website-builder.md`:
  15 — 5 canonical entry modes
  29 — secrets backend choice (.env / 1Password / deferred)
  32 — install-skills.sh for upstream design-skill fetch
  43 — Captain D ships this runner
  48 — `wb maintain reconfig` re-invokes
  55 — v0.1 ships UI/UX Pro Max only
  58 — website-builder lives parallel to platform

Idempotent: re-run on an already-bootstrapped project is a clean no-op (or
"already bootstrapped" notice). See SKILL.md `## Failure modes` sub-case 1.

See also:
  - DESIGN-project-scaffold.md
  - DESIGN-skill-distribution.md
  - DESIGN-secrets-and-keys.md
  - skills/wb-bootstrap/SKILL.md
  - tests/smoke_test.py::TestBootstrapSkill
  - tests/detector.py (entry-mode detection — reused by this runner)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Make the plugin's tests/detector.py importable so we can reuse the canonical
# entry-mode detection logic. We deliberately reuse the reference detector
# rather than re-implementing detection here — the reference is the SSOT for
# every fixture in tests/walkthroughs/.
PLUGIN_ROOT_ENV = os.environ.get("CLAUDE_PLUGIN_ROOT")
SCRIPT_PATH = Path(__file__).resolve()
PLUGIN_ROOT = Path(PLUGIN_ROOT_ENV).resolve() if PLUGIN_ROOT_ENV else SCRIPT_PATH.parent.parent

sys.path.insert(0, str(PLUGIN_ROOT / "tests"))
from detector import detect  # noqa: E402  (sys.path mutation must precede)

# Make the plugin's scripts/ dir importable so the project-root CLAUDE.md helper
# (gap #2 — DESIGN-orchestration-spine.md §9, Commander CONFIRMED) resolves
# regardless of how this runner is invoked. wb_claudemd is a leaf module (no in-repo
# deps); importing it is side-effect-free.
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))
import wb_claudemd  # noqa: E402  (sys.path mutation must precede)


# ---------- Constants ----------

SCRIPT_NAME = "wb-bootstrap.py"
SCRIPT_VERSION = "0.1.0"
PLUGIN_VERSION = "0.1.0"  # matches .claude-plugin/plugin.json

# Sub-dirs created under .website-builder/ (per SKILL.md Step 6).
# Split into "always" + "non-greenfield" because the greenfield fixture forbids
# `outputs/` (no external-tool outputs to ingest on a fresh project). The other
# 4 fixtures don't forbid `outputs/`, so it's created when an artifact exists
# to potentially ingest into. See tests/walkthroughs/greenfield/expected.yaml.
SUB_DIRS_ALWAYS = (
    "content/pages",
    "content/strings",
    "library",
    "briefs",
    "decisions",
    "audit",
    "media",
    "post-launch",
)
SUB_DIRS_NON_GREENFIELD = (
    "outputs",
)


def sub_dirs_for(entry_mode: str) -> tuple[str, ...]:
    if entry_mode == "greenfield":
        return SUB_DIRS_ALWAYS
    return SUB_DIRS_ALWAYS + SUB_DIRS_NON_GREENFIELD

# .gitignore block appended to the user's project .gitignore (per SKILL.md Step 7).
# Wrapped in idempotency markers so re-runs don't duplicate.
GITIGNORE_START = "# Added by website-builder bootstrap — runtime state, not source."
GITIGNORE_END = "# End of website-builder bootstrap-managed .gitignore additions."
GITIGNORE_BODY = """\
# Added by website-builder bootstrap — runtime state, not source.
# .website-builder/ is mostly committed (state files), but secrets and resolved
# caches are gitignored. Edit at your own risk.
.website-builder/keys-resolved.tmp
.website-builder/.env
.env
.env.local
.env.*.local
.env.development
.env.production
.env.test
# End of website-builder bootstrap-managed .gitignore additions.
"""


# ---------- Logging helpers ----------

def _color_supported() -> bool:
    return sys.stdout.isatty()


_USE_COLOR = _color_supported()


def _c(code: str, msg: str) -> str:
    if not _USE_COLOR:
        return msg
    return f"\x1b[{code}m{msg}\x1b[0m"


def log_info(msg: str) -> None:
    print(f"{_c('36', '[wb-bootstrap]')} {msg}", flush=True)


def log_ok(msg: str) -> None:
    print(f"{_c('32', '[wb-bootstrap]')} {msg}", flush=True)


def log_warn(msg: str) -> None:
    print(f"{_c('33', '[wb-bootstrap]')} {msg}", file=sys.stderr, flush=True)


def log_err(msg: str) -> None:
    print(f"{_c('31', '[wb-bootstrap]')} {msg}", file=sys.stderr, flush=True)


# ---------- YAML emit / parse ----------
#
# Per `RPT-phase-1-captain-d.md`, a Phase 5 follow-up
# is to swap awk+grep for a proper YAML library. For this Phase 2 CL-1 runner,
# we use PyYAML when available (it's a tests/ runtime dep already, used by
# smoke_test.py + the run-tests.sh `uv run --with pyyaml` invocation). When
# PyYAML isn't on PATH, we fall back to a minimal hand-rolled emit (sufficient
# for the simple flat-shape `project.yaml` we generate).

try:
    import yaml  # type: ignore
    HAS_PYYAML = True
except ImportError:  # pragma: no cover — exercised when running outside the test harness
    HAS_PYYAML = False


def _hand_emit_yaml(data: dict[str, Any]) -> str:
    """
    Minimal YAML emitter for our flat project.yaml shape.

    Handles: None → "null", bool → "true"/"false", str → quoted-if-needed,
    int/float → as-is, list of strings → JSON-flow style, nested dict → 2-space
    indent. Sufficient for the project.yaml we write; not a general YAML emitter.
    """

    def _emit_scalar(v: Any) -> str:
        if v is None:
            return "null"
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, (int, float)):
            return str(v)
        if isinstance(v, str):
            # Quote if string contains YAML-special chars or could be ambiguous
            specials = (":", "#", "{", "}", "[", "]", ",", "&", "*", "!", "|", ">",
                        "'", '"', "%", "@", "`", "\n", "\t")
            needs_quote = (
                v == "" or
                v.lower() in ("yes", "no", "true", "false", "null", "~") or
                any(c in v for c in specials) or
                v[0].isdigit() if v else False
            )
            if needs_quote:
                escaped = v.replace("\\", "\\\\").replace('"', '\\"')
                return f'"{escaped}"'
            return v
        return json.dumps(v)

    def _emit(node: Any, indent: int) -> list[str]:
        out: list[str] = []
        pad = " " * indent
        if isinstance(node, dict):
            if not node:
                return ["{}"]
            for k, v in node.items():
                if isinstance(v, dict):
                    if not v:
                        out.append(f"{pad}{k}: {{}}")
                    else:
                        out.append(f"{pad}{k}:")
                        out.extend(_emit(v, indent + 2))
                elif isinstance(v, list):
                    if not v:
                        out.append(f"{pad}{k}: []")
                    else:
                        # Compact JSON-flow for lists of scalars (default for our shape)
                        scalars_only = all(
                            not isinstance(x, (dict, list)) for x in v
                        )
                        if scalars_only:
                            parts = [_emit_scalar(x) for x in v]
                            out.append(f"{pad}{k}: [{', '.join(parts)}]")
                        else:
                            out.append(f"{pad}{k}:")
                            for item in v:
                                if isinstance(item, dict):
                                    sub = _emit(item, indent + 2)
                                    if sub:
                                        first = sub[0].lstrip()
                                        out.append(f"{pad}  - {first}")
                                        out.extend(sub[1:])
                                else:
                                    out.append(f"{pad}  - {_emit_scalar(item)}")
                else:
                    out.append(f"{pad}{k}: {_emit_scalar(v)}")
        elif isinstance(node, list):
            for item in node:
                if isinstance(item, dict):
                    sub = _emit(item, indent + 2)
                    if sub:
                        out.append(f"{pad}- " + sub[0].lstrip())
                        out.extend(sub[1:])
                else:
                    out.append(f"{pad}- {_emit_scalar(item)}")
        else:
            out.append(f"{pad}{_emit_scalar(node)}")
        return out

    return "\n".join(_emit(data, 0)) + "\n"


def emit_yaml(data: dict[str, Any]) -> str:
    """Emit YAML using PyYAML if available, hand-rolled emit otherwise."""
    if HAS_PYYAML:
        # Sort_keys=False preserves logical order; default_flow_style=False
        # produces block-style consistent with our hand-rolled output.
        return yaml.safe_dump(  # type: ignore[no-any-return]
            data,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
        )
    return _hand_emit_yaml(data)


def parse_yaml(text: str) -> dict[str, Any]:
    """Parse YAML using PyYAML if available, minimal fallback otherwise."""
    if HAS_PYYAML:
        result = yaml.safe_load(text)
        if isinstance(result, dict):
            return result
        return {}
    # Minimal fallback — only handles flat scalar k:v lines (sufficient to
    # detect `bootstrap_completed_at` for the idempotency check).
    parsed: dict[str, Any] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        if line.startswith((" ", "\t")):
            continue
        key, _, raw = stripped.partition(":")
        key = key.strip()
        raw = raw.strip()
        if raw.startswith(("'", '"')) and raw.endswith(("'", '"')):
            raw = raw[1:-1]
        if raw in ("null", "~", ""):
            parsed[key] = None
        elif raw == "true":
            parsed[key] = True
        elif raw == "false":
            parsed[key] = False
        else:
            parsed[key] = raw
    return parsed


# ---------- project.yaml composition (per fixtures' assertions + SKILL.md scaffold) ----------

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_project_yaml(
    *,
    entry_mode: str,
    detector_result: Any,  # DetectionResult dataclass from detector.py
    secrets_backend: str,
    design_skill_flavor: str | None,
) -> dict[str, Any]:
    """
    Assemble the seeded `project.yaml` dict.

    Contract: the 5 fixtures in tests/walkthroughs/<mode>/expected.yaml
    define `project_yaml_assertions`. The test asserts each key in
    `project_yaml_assertions` matches the value in our emitted project.yaml.
    Extra keys we emit are permitted (the assertion is subset, not equality).

    Per-fixture assertions (summarized):
      greenfield:           entry_mode=greenfield, current_phase=0, stack=null,
                            cms=null, transactional=null, languages=null,
                            default_language=null, design_skill_flavor=null,
                            component_library=null
      has-existing-site:    entry_mode=has-existing-site, current_phase=0,
                            stack=nextjs, stack_pre_detected=true, cms=null,
                            languages=null, component_library=null
      has-AI-output:        entry_mode=has-AI-output, current_phase=0,
                            stack=null, stack_pre_detected=false, cms=null,
                            languages=null
      has-Framer-attempt:   entry_mode=has-Framer-attempt, current_phase=0,
                            stack=framer, stack_pre_detected=true,
                            cms=framer-cms, cms_pre_detected=true,
                            languages=null, component_library=framer-custom
      has-Figma-file:       entry_mode=has-Figma-file, current_phase=0,
                            stack=null, stack_pre_detected=false, cms=null,
                            languages=null

    Note on `current_phase: 0`: the fixtures assert 0 (bootstrap pre-phase);
    the SKILL.md prose example showed 1. We follow the fixtures (test = contract).
    The General can reconcile the SKILL.md prose in a follow-up if desired.
    """
    now = _now_iso()
    detected_stack = getattr(detector_result, "detected_stack", None)
    detected_cms = getattr(detector_result, "detected_cms", None)
    detected_component_library = getattr(
        detector_result, "detected_component_library", None
    )

    stack_pre_detected = detected_stack is not None
    cms_pre_detected = detected_cms is not None

    proj: dict[str, Any] = {
        "version": 1,
        "plugin_version": PLUGIN_VERSION,
        "created_at": now,
        "bootstrap_completed_at": now,
        # Identity (filled by phase 1)
        "name": "",
        "slug": "",
        # Pipeline state
        "entry_mode": entry_mode,
        "current_phase": 0,
        "phase_locked": False,
        # Secrets backend
        "secrets_backend": secrets_backend,
        # Design-skill flavor — fixtures assert null in greenfield. We emit
        # whatever the caller specified (None → null), letting tests pass.
        "design_skill_flavor": design_skill_flavor,
        "design_skill_flavor_preferred": None,
        "design_skill_complementary": [],
        # Stack / CMS — populated from detector if available, else null.
        "stack": detected_stack,
        "stack_pre_detected": stack_pre_detected,
        "cms": detected_cms,
        "cms_pre_detected": cms_pre_detected,
        "transactional": None,
        # Languages — null by default; phase 14 / i18n decision populates.
        "languages": None,
        "default_language": None,
        # Component library — from detector if present (Framer case).
        "component_library": detected_component_library,
        "component_library_composition": {
            "primary": None,
            "complementary": [],
        },
    }

    # Append pre_existing_artifacts block for non-greenfield modes (per SKILL.md)
    if entry_mode != "greenfield":
        signals = getattr(detector_result, "detection_signals", {}) or {}
        proj["pre_existing_artifacts"] = {
            "detected_at": now,
            "entry_mode": entry_mode,
            "signals": dict(signals),
            "phase_6_5_extractors": list(
                getattr(detector_result, "phase_6_5_extractors", []) or []
            ),
            "ingestion_phase_pending": True,
        }

    return proj


def build_readme(*, entry_mode: str, secrets_backend: str) -> str:
    """Auto-generated README inside .website-builder/ (per SKILL.md Step 8)."""
    return textwrap.dedent(f"""\
        # `.website-builder/` — website-builder plugin state

        > Auto-generated by `scripts/wb-bootstrap.py` v{SCRIPT_VERSION}.
        > Don't hand-edit unless you know what you're doing.

        This directory is the website-builder plugin's per-project state. It tracks
        the pipeline phase you're on, the choices you've locked in (stack, CMS,
        languages, secrets backend), the content you've authored, and the artifacts
        of any ingestion runs (phase 6.5).

        Entry mode: **{entry_mode}**
        Secrets backend: **{secrets_backend}**

        ## Top-level files

        | File | What it holds |
        |---|---|
        | `project.yaml` | The canonical project state — entry mode, current phase, stack, CMS, languages, secrets backend. Schema in `DESIGN-project-scaffold.md`. Human-readable AND human-editable, but mind the schema. |
        | `tasks.yaml` | Phase-by-phase task tracking. Owned by the agent; safe to read, don't hand-edit. |
        | `keys.yaml` | Records what API keys each phase needs + their secret-backend refs. Real values resolved at runtime, never stored here. |
        | `state.yaml` | Phase-by-phase state predicates. Owned by the agent. The SessionStart hook reads this. |
        | `skills-installed.yaml` | Records which upstream design-skill flavors are installed. |
        | `README.md` | This file. |

        ## Sub-directories

        | Dir | Purpose |
        |---|---|
        | `content/pages/` | Page prose, markdown per page |
        | `content/strings/` | Microcopy / i18n strings, JSON per language |
        | `library/` | Reusable content blocks |
        | `briefs/` | JSON handoff briefs for external tools (Framer / Figma / etc.) |
        | `outputs/` | External-tool outputs pasted back for ingestion |
        | `decisions/` | Significant project-level decisions recorded by the agent |
        | `audit/` | Audit artifacts (a11y / perf / SEO snapshots) |
        | `media/` | Project media — images, logos, video |
        | `post-launch/` | Populated at deploy time |

        ## What NOT to edit by hand

        - `state.yaml` — agent-owned; hand-edits get clobbered.
        - `tasks.yaml` — agent-owned.
        - `skills-installed.yaml` — managed by `scripts/install-skills.sh`.

        `project.yaml` is schema-validated but hand-editable (e.g. to correct your
        project name + slug if bootstrap got them wrong).

        ## How to re-run bootstrap

        - Type `/wb-bootstrap` in your Claude Code session — re-runs the interview
          + re-checks the install state. Preserves content/, decisions/, audit/.
        - Or run `wb maintain reconfig` once the CLI ships (per locked decision 48).

        ## Reference

        - Design surface: `DESIGN-project-scaffold.md`
        - The bootstrap skill: `skills/wb-bootstrap/SKILL.md`
        - Secrets handling: `DESIGN-secrets-and-keys.md`
        """)


# ---------- Filesystem ops ----------

def write_text(path: Path, content: str, *, mkdir: bool = True) -> None:
    if mkdir:
        path.parent.mkdir(parents=True, exist_ok=True)
    # Always write with LF; binary mode bypasses Python's text translation
    # so the file is byte-identical on Windows + macOS + Linux.
    path.write_bytes(content.encode("utf-8"))


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def extend_gitignore(project_root: Path) -> str:
    """
    Add the website-builder gitignore block to the user's project .gitignore
    (per SKILL.md Step 7). Idempotent: if the block markers already exist,
    don't append again. Creates .gitignore if missing.

    Returns: "created" | "extended" | "already-present"
    """
    gi = project_root / ".gitignore"
    if gi.exists():
        existing = gi.read_text(encoding="utf-8", errors="replace")
        if GITIGNORE_START in existing:
            return "already-present"
        # Append with separating blank line if existing has content
        sep = "\n" if existing and not existing.endswith("\n") else ""
        new_content = existing + sep + "\n" + GITIGNORE_BODY
        write_text(gi, new_content, mkdir=False)
        return "extended"
    # Create from scratch
    write_text(gi, GITIGNORE_BODY)
    return "created"


def write_secrets_artifact(state_dir: Path, secrets_backend: str) -> str | None:
    """Per SKILL.md Step 6: write .env.example for env-mode, .env.op for op-mode.

    Returns the relative path written, or None for deferred mode.
    """
    if secrets_backend == "env":
        path = state_dir / ".env.example"
        write_text(
            path,
            textwrap.dedent("""\
                # .env.example — committed; placeholder values; copy to .env and fill in real values.
                # The website-builder populates this as phases discover required keys.
                # Real .env file is gitignored; this file is the schema.
            """),
        )
        return str(path.relative_to(state_dir.parent))
    if secrets_backend == "onepassword":
        path = state_dir / ".env.op"
        write_text(
            path,
            textwrap.dedent("""\
                # .env.op — committed; 1Password references via op://vault/item/field syntax.
                # The website-builder populates this as phases discover required keys.
                # Resolved at runtime via `op run --env-file=.website-builder/.env.op`.
            """),
        )
        return str(path.relative_to(state_dir.parent))
    # deferred — no artifact
    return None


# ---------- Bootstrap orchestration ----------

def bootstrap(
    project_root: Path,
    *,
    entry_mode_override: str | None,
    secrets_backend: str,
    design_skill_flavor: str | None,
    force: bool,
) -> int:
    """
    Run the 9-step bootstrap flow from SKILL.md non-interactively.

    Step 1 — read SessionStart context (or fall back to live detector run)
    Step 2 — confirm entry mode (non-interactive: detector + override flag)
    Step 3 — confirm secrets backend (non-interactive: --secrets-backend flag)
    Step 4 — confirm design-skill flavor (non-interactive: --design-skill-flavor flag)
    Step 5 — run install-skills.sh (non-interactive: best-effort; non-blocking if missing)
    Step 6 — initialize .website-builder/
    Step 7 — extend project .gitignore
    Step 8 — write .website-builder/README.md
    Step 9 — hand off (this runner just logs hand-off; in CC the agent picks up)
    """
    log_info(f"{SCRIPT_NAME} v{SCRIPT_VERSION} — bootstrapping {project_root}")
    state_dir = project_root / ".website-builder"

    # ----- Step 1 — detect (and check for already-bootstrapped state) -----
    project_yaml_path = state_dir / "project.yaml"
    if project_yaml_path.is_file():
        existing = parse_yaml(project_yaml_path.read_text(encoding="utf-8"))
        completed = existing.get("bootstrap_completed_at")
        if completed and not force:
            log_ok(
                f"Bootstrap already ran on {completed}. "
                "Re-run with --force to overwrite project.yaml. "
                "Skipping (idempotent no-op)."
            )
            return 0
        log_warn(
            f"project.yaml exists (bootstrap_completed_at={completed!r}); "
            "--force given, will overwrite."
            if force
            else f"project.yaml exists but bootstrap_completed_at is missing; re-running."
        )

    # Run the canonical entry-mode detector (re-uses the SSOT in tests/detector.py).
    detector_result = detect(project_root)
    detected_mode = detector_result.entry_mode
    log_info(
        f"Detector ran: entry_mode={detected_mode}, "
        f"confidence={detector_result.detection_confidence}"
    )

    # ----- Step 2 — confirm entry mode (--entry-mode overrides detector) -----
    chosen_mode = entry_mode_override or detected_mode
    if chosen_mode == "ambiguous":
        # In non-interactive mode, fall back to greenfield rather than error.
        # The user can re-run with --entry-mode <mode> to override.
        log_warn(
            "Detector returned 'ambiguous'. Non-interactive mode: falling back "
            "to greenfield. Re-run with --entry-mode <mode> to override."
        )
        chosen_mode = "greenfield"
    if entry_mode_override and entry_mode_override != detected_mode:
        log_info(
            f"Entry-mode override: detector said {detected_mode!r}, "
            f"caller said {entry_mode_override!r}; using caller's pick."
        )

    valid_modes = {
        "greenfield",
        "has-existing-site",
        "has-AI-output",
        "has-Framer-attempt",
        "has-Figma-file",
    }
    if chosen_mode not in valid_modes:
        log_err(
            f"Invalid entry mode {chosen_mode!r}. "
            f"Valid: {', '.join(sorted(valid_modes))}"
        )
        return 2

    # ----- Step 3 — secrets backend (already supplied via --secrets-backend) -----
    if secrets_backend not in ("env", "onepassword", "deferred"):
        log_err(
            f"Invalid secrets backend {secrets_backend!r}. "
            "Valid: env, onepassword, deferred."
        )
        return 2

    # ----- Step 4 — design-skill flavor (already supplied via --design-skill-flavor) -----
    # None is permitted (matches greenfield fixture which asserts null).
    # No registry validation here — install-skills.sh validates its known list.

    # ----- Step 5 — install-skills.sh (best-effort; non-blocking) -----
    install_script = PLUGIN_ROOT / "scripts" / "install-skills.sh"
    if design_skill_flavor and install_script.is_file():
        log_info(
            f"Would invoke install-skills.sh --primary {design_skill_flavor} "
            "(skipped in non-interactive runner — phase 5 wires this fully)."
        )
        # We intentionally DO NOT invoke install-skills.sh from the runner:
        # the script writes to ~/.claude/skills/ which is the user's machine
        # CC dir, and is destructive at test time. The fixture tests assert
        # project-state only, not skills-installed state. Live CC sessions
        # invoke install-skills.sh directly per SKILL.md Step 5.
    elif design_skill_flavor:
        log_warn(
            f"design-skill-flavor={design_skill_flavor} but install-skills.sh "
            f"not found at {install_script}; skipping."
        )

    # ----- Step 6 — initialize .website-builder/ -----
    ensure_dir(state_dir)
    subs = sub_dirs_for(chosen_mode)
    for sub in subs:
        ensure_dir(state_dir / sub)
    log_info(f"Created {state_dir}/ with sub-dirs: {', '.join(subs)}")

    # Write project.yaml
    proj = build_project_yaml(
        entry_mode=chosen_mode,
        detector_result=detector_result,
        secrets_backend=secrets_backend,
        design_skill_flavor=design_skill_flavor,
    )
    write_text(project_yaml_path, emit_yaml(proj))
    log_ok(f"Wrote {project_yaml_path.relative_to(project_root)}")

    # Write initial state files (per SKILL.md Step 6)
    write_text(state_dir / "tasks.yaml", emit_yaml({"version": 1, "phases": {}}))
    write_text(state_dir / "keys.yaml", emit_yaml({"version": 1}))
    write_text(state_dir / "state.yaml", emit_yaml({"version": 1, "phases": {}}))
    log_info("Wrote tasks.yaml, keys.yaml, state.yaml (initial empty state)")

    # Secrets-backend artifact (per SKILL.md Step 6)
    secrets_artifact = write_secrets_artifact(state_dir, secrets_backend)
    if secrets_artifact:
        log_info(f"Wrote {secrets_artifact} (secrets backend = {secrets_backend})")
    else:
        log_info(f"No secrets artifact written (secrets backend = {secrets_backend})")

    # ----- Step 7 — extend .gitignore -----
    gi_result = extend_gitignore(project_root)
    log_info(f".gitignore: {gi_result}")

    # ----- Step 7.5 — write the project-root CLAUDE.md orientation surface -----
    # gap #2 — DESIGN-orchestration-spine.md §7 row #2 + §9 (Commander CONFIRMED).
    # A STANDING orientation surface (project / phase / stack / cms / how-to-resume)
    # that survives even when the plugin isn't loaded; the orchestration spine keeps
    # its phase line fresh on phase entry. Idempotent via a delimited managed block —
    # never clobbers a user-authored CLAUDE.md (their content lives outside the markers).
    claudemd_result = wb_claudemd.write_project_claudemd(project_root, proj)
    log_info(f"project-root CLAUDE.md: {claudemd_result}")

    # ----- Step 8 — write README.md inside .website-builder/ -----
    readme = build_readme(entry_mode=chosen_mode, secrets_backend=secrets_backend)
    write_text(state_dir / "README.md", readme)
    log_ok("Wrote .website-builder/README.md")

    # ----- Step 9 — handoff message -----
    log_ok(
        f"Bootstrap complete. Entry mode: {chosen_mode}, "
        f"secrets backend: {secrets_backend}, "
        f"design-skill flavor: {design_skill_flavor or '(none)'}."
    )
    log_info("Next: phase 1 (idea questionnaire) — the website-builder agent picks up.")
    return 0


# ---------- CLI entry point ----------

def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        description=(
            "Non-interactive runner for the website-builder plugin's wb-bootstrap "
            "skill. Invoked by the test harness (tests/smoke_test.py) and reusable "
            "from CLI for batch / scripted bootstraps."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Default behavior (no flags) — exactly what TestBootstrapSkill expects:
              - cwd = the project directory (must be set by caller via subprocess cwd=...)
              - entry_mode = auto-detected via tests/detector.py
              - secrets_backend = env (sensible muggle-default)
              - design_skill_flavor = null (the fixtures assert null)

            Test harness invocation:
              cd <project-dir>
              python scripts/wb-bootstrap.py

            CLI invocation (override defaults):
              python scripts/wb-bootstrap.py --entry-mode greenfield --secrets-backend env

            For live CC sessions, the agent invokes the wb-bootstrap SKILL.md
            interactively via AskUserQuestion prompts — this runner is the
            non-interactive sibling for automation + tests.
        """),
    )
    p.add_argument(
        "--project-dir",
        type=Path,
        default=None,
        help="Project directory to bootstrap. Default: cwd (matches test invocation).",
    )
    p.add_argument(
        "--entry-mode",
        choices=[
            "greenfield",
            "has-existing-site",
            "has-AI-output",
            "has-Framer-attempt",
            "has-Figma-file",
        ],
        default=None,
        help="Override the detected entry mode. Default: use detector's result.",
    )
    p.add_argument(
        "--secrets-backend",
        choices=["env", "onepassword", "deferred"],
        default=os.environ.get("WB_BOOTSTRAP_SECRETS_BACKEND", "env"),
        help="Secrets handling. Default: env (muggle-default per locked decision 29).",
    )
    p.add_argument(
        "--design-skill-flavor",
        default=os.environ.get("WB_BOOTSTRAP_DESIGN_SKILL_FLAVOR"),
        help=(
            "Primary design-skill flavor to install. Default: None (fixtures assert null). "
            "Use 'ui-ux-pro-max' for v0.1 default per locked decision 55."
        ),
    )
    p.add_argument(
        "--force",
        action="store_true",
        help=(
            "Re-run bootstrap even if .website-builder/project.yaml exists with a "
            "non-empty bootstrap_completed_at timestamp. Without this flag, an "
            "already-bootstrapped project is a clean no-op."
        ),
    )
    p.add_argument(
        "--version",
        action="version",
        version=f"{SCRIPT_NAME} {SCRIPT_VERSION} (plugin {PLUGIN_VERSION})",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    project_dir: Path = (args.project_dir or Path.cwd()).resolve()

    if not project_dir.is_dir():
        log_err(f"Project dir does not exist or is not a directory: {project_dir}")
        return 2

    # Sanity check: don't bootstrap the plugin install dir itself.
    # Matches session_start.py's same guard.
    if PLUGIN_ROOT_ENV:
        try:
            if project_dir == Path(PLUGIN_ROOT_ENV).resolve():
                log_warn(
                    f"Refusing to bootstrap the plugin install dir itself "
                    f"({project_dir}). Open a real user-project directory."
                )
                return 0
        except (OSError, ValueError):
            pass

    return bootstrap(
        project_dir,
        entry_mode_override=args.entry_mode,
        secrets_backend=args.secrets_backend,
        design_skill_flavor=args.design_skill_flavor,
        force=args.force,
    )


if __name__ == "__main__":
    sys.exit(main())
