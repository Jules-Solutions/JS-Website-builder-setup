#!/usr/bin/env bash
# scripts/wb.sh — cross-OS shell launcher for the wb CLI (wb.py).
#
# Thin wrapper that resolves a Python interpreter and invokes the dispatcher.
# All routing/argparse logic lives in wb.py; this file is just the entry point
# for callers that prefer bash invocation — primarily the commands/wb.md slash
# wrapper, which shells out to "${CLAUDE_PLUGIN_ROOT}/scripts/wb.sh", plus
# manual user invocation on macOS / Linux / Windows-with-bash.
#
# Mirrors the cross-platform style of wb-bootstrap.sh + install-skills.sh
# (sibling scripts). The launcher→runner layering is the established repo
# pattern (see scripts/README.md § OQ-1 + § Cross-platform invocation): the
# slash command is the trigger surface; this .sh resolves an interpreter; wb.py
# is the implementation.
#
# See:
#   - scripts/README.md (the CLI + module-boundary contract)
#   - scripts/wb.py (the actual dispatcher this launcher execs)
#   - commands/wb.md (the slash-command wrapper that shells to this launcher)
#   - scripts/wb-bootstrap.sh (the sibling launcher this copies)

set -euo pipefail

SCRIPT_NAME="wb.sh"
SCRIPT_VERSION="0.1.0"

# ---------- Plugin root resolution ----------
# Resolve plugin root from this script's location (one level up from scripts/).
# Honors CLAUDE_PLUGIN_ROOT env var if set (CC plugin spec contract).
# (Pattern copied verbatim from wb-bootstrap.sh lines 31-33.)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-${DEFAULT_PLUGIN_ROOT}}"

# ---------- Output helpers ----------
if [[ -t 1 ]] && command -v tput >/dev/null 2>&1; then
  COLOR_CYAN="$(tput setaf 6 2>/dev/null || true)"
  COLOR_RED="$(tput setaf 1 2>/dev/null || true)"
  COLOR_RESET="$(tput sgr0 2>/dev/null || true)"
else
  COLOR_CYAN=""
  COLOR_RED=""
  COLOR_RESET=""
fi

log_info() { printf "%s[%s]%s %s\n" "$COLOR_CYAN" "$SCRIPT_NAME" "$COLOR_RESET" "$*" ; }
log_err()  { printf "%s[%s]%s %s\n" "$COLOR_RED"  "$SCRIPT_NAME" "$COLOR_RESET" "$*" >&2 ; }

# ---------- Python interpreter resolution ----------
# Cross-OS fallback order (copied from wb-bootstrap.sh lines 65-80):
#   1. WB_WB_PYTHON env var (explicit override for the wb CLI)
#   2. WB_BOOTSTRAP_PYTHON env var (shared website-builder override — honored so
#      a user who set one interpreter for the whole plugin gets it here too)
#   3. python3 (POSIX-standard name)
#   4. python (some distros only ship `python`)
#   5. py (Windows Python Launcher; ships with python.org installer)

resolve_python() {
  for override in "${WB_WB_PYTHON:-}" "${WB_BOOTSTRAP_PYTHON:-}"; do
    if [[ -n "$override" ]]; then
      if command -v "$override" >/dev/null 2>&1; then
        echo "$override"
        return 0
      fi
      log_err "Python override '${override}' not found on PATH; falling through."
    fi
  done
  for candidate in python3 python py; do
    if command -v "$candidate" >/dev/null 2>&1; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

# ---------- Locate the Python runner ----------
RUNNER="${PLUGIN_ROOT}/scripts/wb.py"
if [[ ! -f "$RUNNER" ]]; then
  log_err "wb.py runner not found at ${RUNNER}"
  log_err "  (expected sibling of this script — check plugin install integrity)"
  exit 3
fi

# ---------- Resolve Python ----------
if ! PYTHON_BIN="$(resolve_python)"; then
  log_err "No Python interpreter found on PATH."
  log_err "  Tried: python3, python, py"
  log_err "  On Windows, install Python from https://python.org and ensure it's on PATH,"
  log_err "  or use Git for Windows (ships Git Bash) / WSL."
  log_err "  On macOS: brew install python (or python.org). On Linux: your distro's package manager."
  log_err "  Or set WB_WB_PYTHON to your interpreter's path."
  exit 4
fi

# ---------- Invoke ----------
# Pass through all argv to the Python runner. Export CLAUDE_PLUGIN_ROOT so the
# runner can resolve sibling modules (wb_library / wb_keys) + delegate scripts
# (install-skills.sh / wb-bootstrap.py).
export CLAUDE_PLUGIN_ROOT="${PLUGIN_ROOT}"

exec "$PYTHON_BIN" "$RUNNER" "$@"
