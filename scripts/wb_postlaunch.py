#!/usr/bin/env python3
"""
scripts/wb_postlaunch.py — the phase-29 post-launch maintainer MATERIALIZER.

This script materializes the website-builder plugin's post-launch maintainer
template (the plugin's `post-launch/` tree) into the user's project at
`.website-builder/post-launch/`, customized via the 7-section deploy wizard.

It is the test-harness + automation sibling of the in-CC interactive wizard:
the `wb-deploy` skill (phase-29 section) walks a live agent through the wizard
with `AskUserQuestion`; this runner replays the same materialization
non-interactively, taking wizard answers via flags / a JSON answers file /
sensible defaults, and produces the identical `.website-builder/post-launch/`
result. Mirrors the shape of `scripts/wb-bootstrap.py` (Captain D's bootstrap
runner) — the same launcher→runner→idempotent-materialize pattern.

WHAT IT DOES (per DESIGN-post-launch-template.md § Materialized location at
deploy + § Wizard config output + § Skill installation):
  1. Read the project's state (project.yaml) for identity placeholders
     (project / stack / deploy_provider / languages).
  2. Read the wizard answers (flags / --answers JSON / defaults) for the 7
     sections (analytics / uptime / error-tracking / cms / backup / iteration
     cadence / translation preference).
  3. Write `.website-builder/post-launch/config.yaml` — the template's
     `config-template.yaml` with every placeholder resolved.
  4. Materialize the chosen skill subset + the customized
     `website-maintainer.md` (placeholders resolved) + the runbooks + README
     into `.website-builder/post-launch/`.

WHY A STANDALONE RUNNER, NOT A `wb` VERB:
  The `wb` CLI verb surface is locked (scripts/wb.py lines 72-77; adding a verb
  is a General-review change). This runner ships standalone — invoked by the
  wb-deploy skill at phase 29 + re-runnable directly — exactly as wb-bootstrap.py
  is the runner behind the wb-bootstrap skill. Wiring a `wb maintain postlaunch`
  CLI verb is a clean follow-up once the dispatcher surface is open for edits
  (see RPT-phase-6-captain-s.md § Follow-ups).

CONTRACT: invoked with cwd = the user's project directory (or --project-dir),
reads/writes `.website-builder/`. Pure-stdlib (argparse); PyYAML when available,
hand-rolled YAML emit/parse fallback otherwise (mirrors wb-bootstrap.py).

Idempotent: re-run re-materializes config.yaml + the skill subset cleanly. It
NEVER touches user-authored content (content/ media/ decisions/) — it owns only
the post-launch/ subtree.

Per locked decisions in Workstreams/website-builder/website-builder.md:
  28 — post-launch maintainer template (the killer template)
  37 — phases 31-34 once vs maintainer ongoing
  40 — translation preference default = 1 (auto-translate inline)
  45 — wizard-driven customization at phase 29
  49 — 8-skill split materialized via the phase-29 wizard
  75 — provider specifics re-verified at deploy (the wizard re-confirms)

See also:
  - post-launch/README.md (the template this materializes)
  - post-launch/config-template.yaml (the config schema this resolves)
  - skills/wb-deploy/SKILL.md § Phase 29 (the interactive wizard this mirrors)
  - phase-contracts/29-hosting-deployment.md (the contract)
  - scripts/wb-bootstrap.py (the sibling runner this mirrors)
  - tests/post-launch/test_wb_postlaunch.py (materialization tests)
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------- Plugin-root resolution (mirrors wb-bootstrap.py lines 54-56) ----------

PLUGIN_ROOT_ENV = os.environ.get("CLAUDE_PLUGIN_ROOT")
SCRIPT_PATH = Path(__file__).resolve()
PLUGIN_ROOT = (
    Path(PLUGIN_ROOT_ENV).resolve() if PLUGIN_ROOT_ENV else SCRIPT_PATH.parent.parent
)

# ---------- Constants ----------

SCRIPT_NAME = "wb_postlaunch.py"
SCRIPT_VERSION = "0.1.0"
PLUGIN_VERSION = "0.1.0"  # matches .claude-plugin/plugin.json

# The plugin's template source tree (what we materialize FROM).
TEMPLATE_DIR = PLUGIN_ROOT / "post-launch"

# The 8 maintainer skills (locked per decision 49). The wizard may install a
# subset; the default is all 8.
ALL_MAINTAINER_SKILLS = (
    "wb-maintain-content",
    "wb-maintain-monitoring",
    "wb-maintain-deps",
    "wb-maintain-content-add",
    "wb-maintain-section-add",
    "wb-maintain-page-add",
    "wb-maintain-iterate",
    "wb-maintain-escalate",
)

# The 5 runbooks (always materialized — small footprint, all skills reference them).
RUNBOOKS = (
    "content-update.md",
    "dep-update.md",
    "monitor-review.md",
    "analytics-review.md",
    "incident-response.md",
)

# Provider option allow-lists (grounds wizard answers; re-verified 2026-06-14 per
# decision 75 — the live wizard re-confirms current free-tiers/pricing).
ANALYTICS_PROVIDERS = ("plausible", "ga4", "cloudflare-web-analytics", "fathom", "none", "custom")
UPTIME_PROVIDERS = ("uptimerobot", "better-stack", "cloudflare-health-checks", "pingdom", "none")
ERROR_TRACKING_PROVIDERS = ("sentry", "logrocket", "raygun", "none")
TRANSLATION_PREFERENCES = ("1", "2", "3")


# ---------- Logging helpers (mirror wb-bootstrap.py) ----------

def _color_supported() -> bool:
    return sys.stdout.isatty()


_USE_COLOR = _color_supported()


def _c(code: str, msg: str) -> str:
    if not _USE_COLOR:
        return msg
    return f"\x1b[{code}m{msg}\x1b[0m"


def log_info(msg: str) -> None:
    print(f"{_c('36', '[wb-postlaunch]')} {msg}", flush=True)


def log_ok(msg: str) -> None:
    print(f"{_c('32', '[wb-postlaunch]')} {msg}", flush=True)


def log_warn(msg: str) -> None:
    print(f"{_c('33', '[wb-postlaunch]')} {msg}", file=sys.stderr, flush=True)


def log_err(msg: str) -> None:
    print(f"{_c('31', '[wb-postlaunch]')} {msg}", file=sys.stderr, flush=True)


# ---------- YAML emit / parse (PyYAML with hand-rolled fallback) ----------
# Mirrors wb-bootstrap.py: PyYAML is a tests/ runtime dep (run-tests.sh uses
# `uv run --with pyyaml`); fall back to a minimal emitter/parser when absent.

try:
    import yaml  # type: ignore
    HAS_PYYAML = True
except ImportError:  # pragma: no cover — exercised outside the test harness
    HAS_PYYAML = False


def _hand_emit_scalar(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, str):
        specials = (":", "#", "{", "}", "[", "]", ",", "&", "*", "!", "|", ">",
                    "'", '"', "%", "@", "`", "\n", "\t")
        needs_quote = (
            v == ""
            or v.lower() in ("yes", "no", "true", "false", "null", "~")
            or any(c in v for c in specials)
            or (v[0].isdigit() if v else False)
        )
        if needs_quote:
            escaped = v.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        return v
    return json.dumps(v)


def _hand_emit_yaml(data: dict[str, Any]) -> str:
    out: list[str] = []

    def emit(node: Any, indent: int) -> None:
        pad = " " * indent
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(v, dict):
                    if not v:
                        out.append(f"{pad}{k}: {{}}")
                    else:
                        out.append(f"{pad}{k}:")
                        emit(v, indent + 2)
                elif isinstance(v, list):
                    if not v:
                        out.append(f"{pad}{k}: []")
                    else:
                        scalars_only = all(not isinstance(x, (dict, list)) for x in v)
                        if scalars_only:
                            out.append(f"{pad}{k}:")
                            for item in v:
                                out.append(f"{pad}  - {_hand_emit_scalar(item)}")
                        else:
                            out.append(f"{pad}{k}:")
                            for item in v:
                                out.append(f"{pad}  - {_hand_emit_scalar(item)}")
                else:
                    out.append(f"{pad}{k}: {_hand_emit_scalar(v)}")

    emit(data, 0)
    return "\n".join(out) + "\n"


def emit_yaml(data: dict[str, Any]) -> str:
    if HAS_PYYAML:
        return yaml.safe_dump(  # type: ignore[no-any-return]
            data, sort_keys=False, default_flow_style=False, allow_unicode=True
        )
    return _hand_emit_yaml(data)


def parse_yaml(text: str) -> dict[str, Any]:
    if HAS_PYYAML:
        result = yaml.safe_load(text)
        return result if isinstance(result, dict) else {}
    # Minimal fallback — flat scalar k:v lines only (sufficient to read
    # project.yaml identity fields when PyYAML is absent).
    parsed: dict[str, Any] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        if line.startswith((" ", "\t")):
            continue
        key, _, raw = stripped.partition(":")
        key, raw = key.strip(), raw.strip()
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


# ---------- Helpers ----------

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # LF + binary write → byte-identical across OSes (mirrors wb-bootstrap.py).
    path.write_bytes(content.encode("utf-8"))


def _read_project_identity(state_dir: Path) -> dict[str, Any]:
    """Read project / stack / deploy_provider / languages from project.yaml."""
    proj_path = state_dir / "project.yaml"
    if not proj_path.is_file():
        return {}
    proj = parse_yaml(proj_path.read_text(encoding="utf-8"))
    return {
        "project": proj.get("slug") or proj.get("name") or "",
        "stack": proj.get("stack"),
        "deploy_provider": proj.get("deploy_provider") or proj.get("provider"),
        "languages": proj.get("languages"),
    }


def _languages_to_str(languages: Any) -> str:
    """Render a languages value as the config string form (e.g. '[en, de]')."""
    if isinstance(languages, (list, tuple)):
        return "[" + ", ".join(str(x) for x in languages) + "]"
    if languages in (None, ""):
        return "[en]"
    return str(languages)


# ---------- Wizard answers ----------

def default_answers() -> dict[str, Any]:
    """
    Sensible non-interactive defaults for the 7 wizard sections.

    These mirror the muggle-default recommendations in
    DESIGN-post-launch-template.md. The live wizard surfaces choices + re-verifies
    current provider free-tiers (decision 75); the runner's defaults are the
    safe baseline for automation/tests, NOT a substitute for the live wizard's
    fresh provider verification.
    """
    return {
        "analytics_provider": "none",
        "analytics_config_url": None,
        "analytics_api_key_env": None,
        "uptime_provider": "none",
        "uptime_monitor_id": None,
        "uptime_alert_channel": None,
        "error_tracking_provider": "none",
        "error_tracking_dsn_env": None,
        "error_tracking_declined_reason": None,
        "cms_provider": "none",
        "cms_notification_cadence": "off",
        "cms_stale_months": None,
        "backup_code": "git (origin/main) + host deploy history",
        "backup_content": "git (Layer-4 markdown)",
        "backup_cms": "n/a",
        "backup_media": "git",
        "backup_database": "n/a",
        "iteration_frequency": "monthly",
        "iteration_next_review": None,
        "translation_preference": "1",  # decision 40 default
        "maintainer_skills_installed": list(ALL_MAINTAINER_SKILLS),
    }


def load_answers(answers_path: Path | None) -> dict[str, Any]:
    """Merge an optional --answers JSON file over the defaults."""
    answers = default_answers()
    if answers_path is not None:
        if not answers_path.is_file():
            raise FileNotFoundError(f"--answers file not found: {answers_path}")
        data = json.loads(answers_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("--answers JSON must be an object/dict.")
        answers.update(data)
    return answers


def validate_answers(answers: dict[str, Any]) -> list[str]:
    """Return a list of validation errors (empty = valid)."""
    errors: list[str] = []
    if answers.get("analytics_provider") not in ANALYTICS_PROVIDERS:
        errors.append(
            f"analytics_provider must be one of {ANALYTICS_PROVIDERS}; "
            f"got {answers.get('analytics_provider')!r}"
        )
    if answers.get("uptime_provider") not in UPTIME_PROVIDERS:
        errors.append(
            f"uptime_provider must be one of {UPTIME_PROVIDERS}; "
            f"got {answers.get('uptime_provider')!r}"
        )
    if answers.get("error_tracking_provider") not in ERROR_TRACKING_PROVIDERS:
        errors.append(
            f"error_tracking_provider must be one of {ERROR_TRACKING_PROVIDERS}; "
            f"got {answers.get('error_tracking_provider')!r}"
        )
    if str(answers.get("translation_preference")) not in TRANSLATION_PREFERENCES:
        errors.append(
            f"translation_preference must be one of {TRANSLATION_PREFERENCES}; "
            f"got {answers.get('translation_preference')!r}"
        )
    skills = answers.get("maintainer_skills_installed")
    if not isinstance(skills, list) or not skills:
        errors.append("maintainer_skills_installed must be a non-empty list.")
    else:
        unknown = [s for s in skills if s not in ALL_MAINTAINER_SKILLS]
        if unknown:
            errors.append(
                f"maintainer_skills_installed has unknown skills: {unknown}; "
                f"valid: {ALL_MAINTAINER_SKILLS}"
            )
    return errors


# ---------- config.yaml composition ----------

def build_config(identity: dict[str, Any], answers: dict[str, Any]) -> dict[str, Any]:
    """Assemble the resolved post-launch config.yaml dict (placeholders filled)."""
    return {
        "version": 1,
        "project": identity.get("project", ""),
        "stack": identity.get("stack"),
        "deploy_provider": identity.get("deploy_provider"),
        "languages": identity.get("languages") or ["en"],
        "analytics": {
            "provider": answers["analytics_provider"],
            "config_url": answers["analytics_config_url"],
            "api_key_env": answers["analytics_api_key_env"],
        },
        "uptime": {
            "provider": answers["uptime_provider"],
            "monitor_id": answers["uptime_monitor_id"],
            "alert_channel": answers["uptime_alert_channel"],
        },
        "error_tracking": {
            "provider": answers["error_tracking_provider"],
            "dsn_env": answers["error_tracking_dsn_env"],
            "declined_reason": answers["error_tracking_declined_reason"],
        },
        "cms": {
            "provider": answers["cms_provider"],
            "notification_cadence": answers["cms_notification_cadence"],
            "stale_content_months": answers["cms_stale_months"],
        },
        "backup": {
            "code": answers["backup_code"],
            "content_layer_4": answers["backup_content"],
            "cms": answers["backup_cms"],
            "media": answers["backup_media"],
            "database": answers["backup_database"],
        },
        "iteration_cadence": {
            "frequency": answers["iteration_frequency"],
            "next_review": answers["iteration_next_review"],
        },
        "translation_preference": str(answers["translation_preference"]),
        "maintainer_skills_installed": list(answers["maintainer_skills_installed"]),
        "materialized_at": _now_iso(),
        "plugin_version": PLUGIN_VERSION,
    }


# ---------- Placeholder resolution for the maintainer profile ----------

def resolve_placeholders(text: str, identity: dict[str, Any]) -> str:
    """Replace {project_name}/{chosen_stack}/{chosen_provider}/{languages}."""
    mapping = {
        "{project_name}": str(identity.get("project") or ""),
        "{chosen_stack}": str(identity.get("stack") or ""),
        "{chosen_provider}": str(identity.get("deploy_provider") or ""),
        "{languages}": _languages_to_str(identity.get("languages")),
    }
    for placeholder, value in mapping.items():
        text = text.replace(placeholder, value)
    return text


# ---------- Materialization ----------

def materialize(
    project_root: Path,
    *,
    answers: dict[str, Any],
    force: bool,
) -> int:
    """
    Materialize the post-launch template into .website-builder/post-launch/.

    Steps (per DESIGN-post-launch-template.md § Materialized location at deploy):
      1. Validate the plugin template source exists.
      2. Read project identity for placeholder resolution.
      3. Write config.yaml (resolved).
      4. Copy README.md + the customized website-maintainer.md (placeholders
         resolved) + the chosen skill subset + the runbooks.
    """
    state_dir = project_root / ".website-builder"
    dest = state_dir / "post-launch"

    # ----- 1. Template source must exist -----
    if not TEMPLATE_DIR.is_dir():
        log_err(f"Plugin template source missing: {TEMPLATE_DIR}")
        log_err("  The post-launch/ template ships with the plugin (Phase 6). "
                "Check plugin install integrity.")
        return 4

    # ----- 2. Project identity -----
    if not state_dir.is_dir():
        log_err(f"No .website-builder/ at {project_root}. Run bootstrap first.")
        return 2
    identity = _read_project_identity(state_dir)

    # ----- 0. Validate answers -----
    errors = validate_answers(answers)
    if errors:
        for e in errors:
            log_err(f"answers: {e}")
        return 2

    # ----- Idempotency: an existing config.yaml is fine to overwrite on a
    # re-materialize; warn unless --force suppresses the notice. We never touch
    # user content/ or media/ — we own only post-launch/.
    config_path = dest / "config.yaml"
    if config_path.is_file() and not force:
        log_info("Existing post-launch/config.yaml found; re-materializing "
                 "(post-launch/ is plugin-owned; content/ + media/ untouched).")

    dest.mkdir(parents=True, exist_ok=True)

    # ----- 3. config.yaml -----
    config = build_config(identity, answers)
    write_text(config_path, emit_yaml(config))
    log_ok(f"Wrote {config_path.relative_to(project_root)}")

    # ----- 4a. README.md (verbatim copy) -----
    src_readme = TEMPLATE_DIR / "README.md"
    if src_readme.is_file():
        write_text(dest / "README.md", src_readme.read_text(encoding="utf-8"))
        log_info("Materialized README.md")

    # ----- 4b. website-maintainer.md (placeholders resolved) -----
    src_profile = TEMPLATE_DIR / "agents" / "website-maintainer.md"
    if not src_profile.is_file():
        log_err(f"Maintainer profile missing in template: {src_profile}")
        return 4
    resolved = resolve_placeholders(src_profile.read_text(encoding="utf-8"), identity)
    write_text(dest / "agents" / "website-maintainer.md", resolved)
    log_ok("Materialized agents/website-maintainer.md (placeholders resolved)")

    # ----- 4c. chosen skill subset -----
    chosen = answers["maintainer_skills_installed"]
    installed = 0
    for skill in chosen:
        src_skill = TEMPLATE_DIR / "skills" / skill / "SKILL.md"
        if not src_skill.is_file():
            log_warn(f"Skill {skill} requested but not in template; skipping.")
            continue
        write_text(dest / "skills" / skill / "SKILL.md",
                   src_skill.read_text(encoding="utf-8"))
        installed += 1
    log_ok(f"Materialized {installed} maintainer skill(s): {', '.join(chosen)}")

    # ----- 4d. runbooks (all; small footprint, skills reference them) -----
    for rb in RUNBOOKS:
        src_rb = TEMPLATE_DIR / "runbooks" / rb
        if src_rb.is_file():
            write_text(dest / "runbooks" / rb, src_rb.read_text(encoding="utf-8"))
    log_info(f"Materialized {len(RUNBOOKS)} runbook(s)")

    log_ok(
        f"Post-launch maintainer materialized at "
        f"{dest.relative_to(project_root)} for project "
        f"{identity.get('project') or '(unnamed)'}."
    )
    return 0


# ---------- CLI entry point ----------

def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        description=(
            "Materialize the post-launch maintainer template into "
            ".website-builder/post-launch/, customized via the phase-29 wizard. "
            "Non-interactive sibling of the in-CC wizard in skills/wb-deploy."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Default behavior (no flags) — materialize with safe defaults:
              - cwd = the project directory (set via subprocess cwd= or --project-dir)
              - all 8 maintainer skills installed
              - all providers 'none', translation_preference 1 (decision 40 default)

            Live CC sessions: the wb-deploy skill runs the wizard interactively
            (AskUserQuestion) then invokes this runner with the answers. This
            runner is the non-interactive sibling for automation + tests.

            Override via --answers <file.json> (keys per default_answers()).
        """),
    )
    p.add_argument(
        "--project-dir", type=Path, default=None,
        help="Project directory to materialize into. Default: cwd.",
    )
    p.add_argument(
        "--answers", type=Path, default=None,
        help="JSON file of wizard answers; merged over defaults.",
    )
    p.add_argument(
        "--force", action="store_true",
        help="Suppress the existing-config notice on re-materialize.",
    )
    p.add_argument(
        "--version", action="version",
        version=f"{SCRIPT_NAME} {SCRIPT_VERSION} (plugin {PLUGIN_VERSION})",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    project_dir: Path = (args.project_dir or Path.cwd()).resolve()

    if not project_dir.is_dir():
        log_err(f"Project dir does not exist or is not a directory: {project_dir}")
        return 2

    # Don't materialize into the plugin install dir itself (mirrors wb-bootstrap).
    if PLUGIN_ROOT_ENV:
        try:
            if project_dir == Path(PLUGIN_ROOT_ENV).resolve():
                log_warn(
                    f"Refusing to materialize into the plugin install dir itself "
                    f"({project_dir}). Open a real user-project directory."
                )
                return 0
        except (OSError, ValueError):
            pass

    try:
        answers = load_answers(args.answers)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        log_err(f"Could not load --answers: {exc}")
        return 2

    log_info(f"{SCRIPT_NAME} v{SCRIPT_VERSION} — materializing into {project_dir}")
    return materialize(project_dir, answers=answers, force=args.force)


if __name__ == "__main__":
    sys.exit(main())
