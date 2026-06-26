#!/usr/bin/env python3
"""
scripts/wb.py — the `wb` CLI dispatcher for the website-builder plugin.

This is the entry + argparse router that the `commands/wb.md` slash wrapper
shells out to (via `scripts/wb.sh`). It owns the top-level verb surface and
routes each verb-family to its implementation:

    wb library <verb> ...   → Captain P's module (scripts/wb_library.py)
    wb keys <verb> ...      → Captain Q's module (scripts/wb_keys.py)
    wb skills <verb> ...    → scripts/install-skills.sh (subprocess)
    wb maintain <verb> ...  → scripts/wb-bootstrap.{sh,py} / install-skills.sh

Module boundary (locked per Decision 78 — see scripts/README.md § Module boundary):
  - `library` + `keys` are IMPORTABLE Python modules under scripts/ that this
    dispatcher imports and calls through a stable function contract
    (`run(argv, *, project_root) -> int`). The imports are LAZY (inside the
    route functions) so this dispatcher is import-safe and unit-testable
    WITHOUT P's/Q's modules present (they are built in parallel worktrees and
    land at merge time — O merges last).
  - `skills` + `maintain` delegate to the existing Phase-1 bash/python scripts
    via subprocess. This dispatcher does NOT reimplement install-skills.sh or
    wb-bootstrap.* — it wires the dispatch.

Cross-platform: invoked by scripts/wb.sh (the bash launcher mirroring
scripts/wb-bootstrap.sh). The launcher resolves a Python interpreter +
CLAUDE_PLUGIN_ROOT and execs this runner. This file is pure-stdlib (argparse)
so it runs under any resolved interpreter without third-party deps.

Per locked decisions in `Workstreams/website-builder/website-builder.md`:
  42 — library runtime owned by Captain P
  29 — keys/secrets runtime owned by Captain Q
  48 — the `wb {library|keys|skills|maintain} <verb>` surface
  55 — v0.1 ships UI/UX Pro Max only (skills surface scoped accordingly)
  78 — O's dispatcher imports + calls P/Q modules; P/Q do not import O

See also:
  - scripts/README.md (the CLI + module-boundary contract — the bible)
  - scripts/wb.sh (the cross-OS launcher that execs this runner)
  - commands/wb.md (the slash-command wrapper that shells to wb.sh)
  - scripts/install-skills.sh (skills/maintain delegate target)
  - scripts/wb-bootstrap.{sh,py} (maintain reconfig delegate target)
  - tests/cli/test_wb_dispatch.py (the dispatch routing tests)
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from shutil import which

# ---------- Constants ----------

SCRIPT_NAME = "wb"
SCRIPT_VERSION = "0.1.0"
PLUGIN_VERSION = "0.1.0"  # matches .claude-plugin/plugin.json

# Plugin root resolution: honor CLAUDE_PLUGIN_ROOT (set + exported by wb.sh per
# the CC plugin spec contract), else fall back to one level up from scripts/.
# This mirrors wb-bootstrap.py lines 54-56.
_PLUGIN_ROOT_ENV = os.environ.get("CLAUDE_PLUGIN_ROOT")
_SCRIPT_PATH = Path(__file__).resolve()
PLUGIN_ROOT = (
    Path(_PLUGIN_ROOT_ENV).resolve() if _PLUGIN_ROOT_ENV else _SCRIPT_PATH.parent.parent
)
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"

# The locked verb surface per scripts/README.md § Verb surface + decision 48.
# Adding/renaming a top-level verb-family or a sub-verb is an architectural
# change requiring General review (NOT a Captain-level edit).
LIBRARY_VERBS = ("list", "add", "remove", "refresh", "refresh-all", "prune", "inspect")
KEYS_VERBS = ("migrate-to-1password", "migrate-to-env")
SKILLS_VERBS = ("update", "sync")
MAINTAIN_VERBS = ("reconfig", "install-skills")


# ---------- Logging helpers ----------
# Mirror the wb-bootstrap.py convention: cyan/green/yellow/red tags, color only
# on a TTY, stderr for warn/err.

def _use_color() -> bool:
    return sys.stdout.isatty()


def _c(code: str, msg: str) -> str:
    if not _use_color():
        return msg
    return f"\x1b[{code}m{msg}\x1b[0m"


def log_info(msg: str) -> None:
    print(f"{_c('36', '[wb]')} {msg}", flush=True)


def log_ok(msg: str) -> None:
    print(f"{_c('32', '[wb]')} {msg}", flush=True)


def log_warn(msg: str) -> None:
    print(f"{_c('33', '[wb]')} {msg}", file=sys.stderr, flush=True)


def log_err(msg: str) -> None:
    print(f"{_c('31', '[wb]')} {msg}", file=sys.stderr, flush=True)


# ---------- Module-not-installed error path ----------

def _module_missing(family: str, module_file: str, exc: ModuleNotFoundError) -> int:
    """
    Clean error when a routed module (P's library / Q's keys) isn't present.

    During the parallel Phase-5 build, P's and Q's modules live in separate
    worktrees and aren't in O's worktree — so a bare-import dispatcher must fail
    gracefully here rather than crash. Post-merge (O merges last) the modules
    are present and this path is never hit in production.
    """
    # Only swallow the *expected* missing-sibling-module error. If the module
    # imported but raised ModuleNotFoundError for one of ITS OWN deps, re-raise
    # so the real cause surfaces (don't mask a pyyaml-missing-in-wb_library bug
    # as "wb_library not installed").
    missing = getattr(exc, "name", "") or ""
    expected_module = module_file.removesuffix(".py")
    if missing not in (expected_module, ""):
        raise exc
    log_err(
        f"`wb {family}` is unavailable: the {family} module "
        f"({SCRIPTS_DIR / module_file}) is not installed."
    )
    log_err(
        "  This usually means the plugin install is incomplete. The "
        f"{family} module ships as part of the website-builder plugin "
        "(Phase 5). Reinstall the plugin or check install integrity."
    )
    return 4


# ---------- Route: library (Captain P) ----------

def route_library(argv: list[str], *, project_root: Path) -> int:
    """
    Route `library` sub-verbs to Captain P's module.

    Lazy import (inside the function) so this dispatcher is import-safe and
    testable without wb_library present. Tests monkeypatch wb_library.run.
    """
    try:
        import wb_library  # type: ignore  # Captain P — scripts/wb_library.py
    except ModuleNotFoundError as exc:
        return _module_missing("library", "wb_library.py", exc)
    return wb_library.run(argv, project_root=project_root)


# ---------- Route: keys (Captain Q) ----------

def route_keys(argv: list[str], *, project_root: Path) -> int:
    """
    Route `keys` sub-verbs to Captain Q's module.

    Lazy import for the same import-safety reason as library. Tests monkeypatch
    wb_keys.run. Note: the session-start *resolver* (wb_keys.resolve_keys) is
    NOT a `wb keys` sub-verb — it's invoked by the SessionStart hook directly,
    per scripts/README.md § Keys verb scope.
    """
    try:
        import wb_keys  # type: ignore  # Captain Q — scripts/wb_keys.py
    except ModuleNotFoundError as exc:
        return _module_missing("keys", "wb_keys.py", exc)
    return wb_keys.run(argv, project_root=project_root)


# ---------- Subprocess delegation helper ----------

def _run_subprocess(cmd: list[str], *, project_root: Path) -> int:
    """
    Run a delegate script (install-skills.sh / wb-bootstrap.*) as a subprocess.

    cwd is set to the user's project_root because install-skills.sh writes to
    `.website-builder/skills-installed.yaml` relative to cwd (see
    install-skills.sh line 111) and wb-bootstrap.py reads Path.cwd() for the
    project dir (see wb-bootstrap.py line 773). CLAUDE_PLUGIN_ROOT is exported
    so delegate scripts resolve sibling modules. Returns the child's exit code.
    """
    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(PLUGIN_ROOT)}
    try:
        proc = subprocess.run(cmd, cwd=str(project_root), env=env)
    except FileNotFoundError as exc:
        # The interpreter/launcher itself (bash / python) wasn't found — a
        # Tier-2 environment failure, not a bug in our wiring. Surface clearly.
        log_err(f"Could not launch delegate: {exc}")
        log_err(f"  Command was: {' '.join(cmd)}")
        return 127
    return proc.returncode


def _bash_path(path: Path) -> str:
    """
    Render a filesystem path so `bash` can resolve it on every platform.

    On Windows, `str(Path("C:\\a\\b.sh"))` yields backslashes; when that string
    is passed as an argv element to `bash`, bash treats backslashes as escape
    chars and mangles the path. Git Bash resolves forward-slash drive paths
    (`C:/a/b.sh`) correctly, and forward slashes are already native on POSIX —
    so normalizing to forward slashes is safe everywhere. (Pairs with
    `_resolve_bash`, which pins the *correct* bash; see that docstring for why
    the path form alone is insufficient on Windows.)
    """
    return str(path).replace("\\", "/")


def _resolve_bash() -> str:
    """
    Resolve an absolute path to a usable `bash`, not the bare string "bash".

    On Windows this matters: `subprocess.run(["bash", ...])` lets the OS pick
    the first `bash` on PATH, which is frequently `C:\\Windows\\System32\\bash.exe`
    — the WSL launcher stub. That stub runs a Linux bash that cannot see the
    Windows filesystem at `C:/...` or `/c/...` (it mounts its own rootfs), so
    EVERY script-path form fails with `/bin/bash: <path>: No such file or
    directory`. The Git-for-Windows bash (`shutil.which("bash")` →
    `C:\\Program Files\\Git\\usr\\bin\\bash.exe`) resolves `C:/...` forward-slash
    paths fine. Passing that absolute path to subprocess pins the right bash and
    sidesteps the WSL-stub trap. This mirrors wb-bootstrap.sh's discipline of
    resolving its interpreter explicitly rather than trusting bare PATH lookup.

    Resolution order:
      1. WB_BASH env override (explicit escape hatch).
      2. shutil.which("bash") (Git Bash registers here ahead of the WSL stub in
         a normal Git-for-Windows install; on POSIX this is just /bin/bash etc.).
      3. Known Git-for-Windows locations derived from MINGW_PREFIX or the
         standard install path (Windows fallback when PATH is unusual).
      4. Bare "bash" as a last resort (POSIX-only; subprocess surfaces a clear
         error if even this is absent).
    """
    override = os.environ.get("WB_BASH")
    if override and (which(override) or Path(override).is_file()):
        return override

    found = which("bash")
    # On Windows, reject the WSL System32 stub — it can't see the Windows FS.
    if found and "system32" in found.lower():
        found = None
    if found:
        return found

    # Windows fallback: probe Git-for-Windows install locations.
    candidates: list[str] = []
    mingw = os.environ.get("MINGW_PREFIX")  # e.g. C:/Program Files/Git/mingw64
    if mingw:
        git_root = Path(mingw).parent
        candidates.append(str(git_root / "usr" / "bin" / "bash.exe"))
        candidates.append(str(git_root / "bin" / "bash.exe"))
    candidates += [
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files\Git\usr\bin\bash.exe",
    ]
    for cand in candidates:
        if Path(cand).is_file():
            return cand

    return "bash"  # last resort (POSIX); subprocess error is clear if missing


def _resolve_python() -> str:
    """
    Resolve a Python interpreter for delegating to wb-bootstrap.py.

    Prefer the interpreter running THIS process (sys.executable) — it's the one
    wb.sh already resolved + handed us, so it's known-good and avoids a second
    PATH-resolution round. Falls back to the wb-bootstrap.sh order only if
    sys.executable is somehow unavailable.
    """
    if sys.executable:
        return sys.executable
    for candidate in ("python3", "python", "py"):
        if which(candidate):
            return candidate
    return "python3"  # last resort; subprocess will surface a clear error


# ---------- Route: skills (Captain O — delegates to install-skills.sh) ----------

def route_skills(args: argparse.Namespace, *, project_root: Path) -> int:
    """
    Route `skills update|sync` to scripts/install-skills.sh.

    Both verbs delegate to the existing Phase-1 install-skills.sh per
    scripts/README.md § wb skills. O wires the dispatch; O does not rewrite the
    script. v0.1 scope: UI/UX Pro Max only (decision 55) — install-skills.sh
    enforces that.

    - `skills update` — check installed design skills for newer upstream and
      fetch+replace. install-skills.sh is idempotent: it detects existing
      installs and only fetches what's missing/stale.
    - `skills sync` — on a fresh machine, install configured-but-missing skills
      from .website-builder/skills-installed.yaml. install-skills.sh's
      idempotency + state-yaml read covers this; passthrough of --primary lets
      a caller pin the flavor.
    """
    install_script = SCRIPTS_DIR / "install-skills.sh"
    if not install_script.is_file():
        log_err(f"install-skills.sh not found at {install_script}.")
        log_err("  Check plugin install integrity (it's Phase-1 substrate).")
        return 4

    cmd: list[str] = [_resolve_bash(), _bash_path(install_script)]
    # Pass --primary through if the caller specified a flavor (default flavor is
    # decided by install-skills.sh itself: ui-ux-pro-max per decision 55).
    if getattr(args, "primary", None):
        cmd += ["--primary", args.primary]
    for comp in getattr(args, "complementary", None) or []:
        cmd += ["--complementary", comp]

    if args.verb == "update":
        log_info("skills update - checking installed design skills for updates "
                 "(delegating to install-skills.sh; idempotent re-fetch).")
    else:  # sync
        log_info("skills sync - installing configured-but-missing skills from "
                 ".website-builder/skills-installed.yaml (delegating to "
                 "install-skills.sh).")

    return _run_subprocess(cmd, project_root=project_root)


# ---------- Route: maintain (Captain O — delegates to wb-bootstrap.* / install-skills.sh) ----------

def route_maintain(args: argparse.Namespace, *, project_root: Path) -> int:
    """
    Route `maintain reconfig|install-skills` to the existing Phase-1 runners.

    - `maintain reconfig` — re-invoke wb-bootstrap to re-confirm entry-mode /
      secrets-backend / flavor choices without destroying content. Delegates to
      scripts/wb-bootstrap.py (the runner; the .sh is a launcher around it — we
      call the .py directly via the resolved interpreter for cross-platform
      robustness, the same reasoning tests/smoke_test.py documents for invoking
      the .py runner over the .sh launcher).
    - `maintain install-skills` — re-run install-skills.sh directly (decision 48
      lists `maintain {reconfig|install-skills}`).
    """
    if args.verb == "reconfig":
        runner = SCRIPTS_DIR / "wb-bootstrap.py"
        if not runner.is_file():
            log_err(f"wb-bootstrap.py not found at {runner}.")
            log_err("  Check plugin install integrity (it's Phase-1 substrate).")
            return 4
        python_bin = _resolve_python()
        # wb-bootstrap.py reads Path.cwd() for the project dir (line 773); cwd
        # is set to project_root by _run_subprocess. Pass --force through so a
        # deliberate reconfig can overwrite an already-bootstrapped project.yaml.
        cmd: list[str] = [python_bin, str(runner)]
        if getattr(args, "force", False):
            cmd.append("--force")
        log_info("maintain reconfig - re-invoking wb-bootstrap.py to re-confirm "
                 "entry-mode / secrets-backend / flavor (content preserved).")
        return _run_subprocess(cmd, project_root=project_root)

    # install-skills
    install_script = SCRIPTS_DIR / "install-skills.sh"
    if not install_script.is_file():
        log_err(f"install-skills.sh not found at {install_script}.")
        log_err("  Check plugin install integrity (it's Phase-1 substrate).")
        return 4
    log_info("maintain install-skills - re-running install-skills.sh directly.")
    cmd = [_resolve_bash(), _bash_path(install_script)]
    if getattr(args, "primary", None):
        cmd += ["--primary", args.primary]
    return _run_subprocess(cmd, project_root=project_root)


# ---------- argparse construction ----------

def build_parser() -> argparse.ArgumentParser:
    """
    Build the top-level argparse parser + the 4 verb-family sub-parsers.

    For `library` + `keys`, we capture the sub-verb + the remaining args as an
    opaque argv list (REMAINDER) and hand the whole tail to P's / Q's module —
    the modules own their own sub-verb parsing per the contract. For `skills` +
    `maintain` (O's own verbs), we parse the sub-verb explicitly since O owns
    their semantics + flag surface.
    """
    p = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        description=(
            "wb - the website-builder plugin CLI. Manage the project's resource "
            "library, secret keys, installed design skills, and re-run setup."
        ),
        epilog=(
            "Run `wb <command> --help` for command-specific help. "
            "The CLI operates on the .website-builder/ state in the current "
            "project directory."
        ),
    )
    p.add_argument(
        "--version",
        action="version",
        version=f"{SCRIPT_NAME} {SCRIPT_VERSION} (plugin {PLUGIN_VERSION})",
    )
    p.add_argument(
        "--project-dir",
        type=Path,
        default=None,
        help="Project directory to operate on. Default: current directory.",
    )

    sub = p.add_subparsers(dest="command", metavar="<command>")

    # --- library (routes to Captain P) ---
    lib = sub.add_parser(
        "library",
        help="Manage the project's cloned resource library (.website-builder/library/).",
        description=(
            "Manage cloned resources (web pages / GitHub repos / Figma files) in "
            ".website-builder/library/. Verbs: " + " | ".join(LIBRARY_VERBS) + "."
        ),
    )
    # Opaque tail: the sub-verb + its args go straight to wb_library.run().
    lib.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="library sub-verb + its arguments (e.g. `add <url> --tag docs`).",
    )

    # --- keys (routes to Captain Q) ---
    keys = sub.add_parser(
        "keys",
        help="Migrate API keys between .env and 1Password backends.",
        description=(
            "Migrate secret keys between backends. Verbs: "
            + " | ".join(KEYS_VERBS) + ". (The session-start resolver is invoked "
            "by the SessionStart hook, not as a `wb keys` verb.)"
        ),
    )
    keys.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="keys sub-verb + its arguments (e.g. `migrate-to-1password`).",
    )

    # --- skills (O's own; delegates to install-skills.sh) ---
    skills = sub.add_parser(
        "skills",
        help="Update or sync installed design-skill flavors.",
        description=(
            "Manage installed design skills (v0.1: UI/UX Pro Max only, per "
            "decision 55). Delegates to scripts/install-skills.sh."
        ),
    )
    skills_sub = skills.add_subparsers(dest="verb", metavar="<verb>", required=True)
    skills_update = skills_sub.add_parser(
        "update",
        help="Check installed design skills for newer upstream versions and fetch.",
    )
    skills_sync = skills_sub.add_parser(
        "sync",
        help="On a fresh machine, install configured-but-missing skills.",
    )
    for sp in (skills_update, skills_sync):
        sp.add_argument(
            "--primary",
            default=None,
            help="Primary design-skill flavor (default: install-skills.sh's "
                 "default, ui-ux-pro-max).",
        )
        sp.add_argument(
            "--complementary",
            action="append",
            default=None,
            help="Complementary skill id (repeatable; empty in v0.1).",
        )

    # --- maintain (O's own; delegates to wb-bootstrap.* / install-skills.sh) ---
    maintain = sub.add_parser(
        "maintain",
        help="Re-run setup: reconfigure choices or reinstall skills.",
        description=(
            "Re-run plugin setup. Verbs: " + " | ".join(MAINTAIN_VERBS) + ". "
            "Delegates to scripts/wb-bootstrap.py / scripts/install-skills.sh."
        ),
    )
    maintain_sub = maintain.add_subparsers(dest="verb", metavar="<verb>", required=True)
    maintain_reconfig = maintain_sub.add_parser(
        "reconfig",
        help="Re-confirm entry-mode / secrets-backend / flavor (preserves content).",
    )
    maintain_reconfig.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an already-bootstrapped project.yaml during reconfig.",
    )
    maintain_install = maintain_sub.add_parser(
        "install-skills",
        help="Re-run install-skills.sh directly.",
    )
    maintain_install.add_argument(
        "--primary",
        default=None,
        help="Primary design-skill flavor (default: ui-ux-pro-max).",
    )

    return p


# ---------- main ----------

def main(argv: list[str] | None = None) -> int:
    raw_argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(raw_argv)

    if not args.command:
        parser.print_help()
        return 0

    project_root: Path = (args.project_dir or Path.cwd()).resolve()
    if not project_root.is_dir():
        log_err(f"Project dir does not exist or is not a directory: {project_root}")
        return 2

    if args.command == "library":
        # argparse.REMAINDER keeps a leading "--" if the user typed one; strip a
        # single leading "--" so `wb library -- add ...` and `wb library add ...`
        # behave identically when handed to P's module.
        lib_argv = list(args.args)
        if lib_argv and lib_argv[0] == "--":
            lib_argv = lib_argv[1:]
        return route_library(lib_argv, project_root=project_root)

    if args.command == "keys":
        keys_argv = list(args.args)
        if keys_argv and keys_argv[0] == "--":
            keys_argv = keys_argv[1:]
        return route_keys(keys_argv, project_root=project_root)

    if args.command == "skills":
        return route_skills(args, project_root=project_root)

    if args.command == "maintain":
        return route_maintain(args, project_root=project_root)

    # Unreachable: argparse rejects unknown commands before here.
    log_err(f"Unknown command: {args.command!r}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
