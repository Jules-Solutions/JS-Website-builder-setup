#!/usr/bin/env bash
# scripts/wb-bootstrap.sh — cross-OS shell launcher for wb-bootstrap.py.
#
# Thin wrapper that resolves a Python interpreter and invokes the runner.
# All bootstrap logic lives in wb-bootstrap.py; this file is just the entry
# point for callers that prefer bash invocation (test harnesses on POSIX,
# `wb maintain reconfig` CLI later, manual user invocation).
#
# Invoked by the wb-bootstrap skill (skills/wb-bootstrap/SKILL.md) at first-run.
# Re-invokeable via `wb maintain reconfig` per locked decision 48.
#
# Idempotent: re-running on an already-bootstrapped project is a clean no-op
# unless --force is given. Idempotency check is in the Python runner.
#
# Mirrors the cross-platform style of install-skills.sh (sibling script).
#
# See:
#   - Workstreams/website-builder/foundation/DESIGN-architecture.md
#   - Workstreams/website-builder/foundation/DESIGN-project-scaffold.md
#   - skills/wb-bootstrap/SKILL.md (the invoking skill)
#   - scripts/wb-bootstrap.py (the actual runner)

set -euo pipefail

SCRIPT_NAME="wb-bootstrap.sh"
SCRIPT_VERSION="0.1.0"

# ---------- Plugin root resolution ----------
# Resolve plugin root from this script's location (one level up from scripts/).
# Honors CLAUDE_PLUGIN_ROOT env var if set (CC plugin spec contract).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-${DEFAULT_PLUGIN_ROOT}}"

# ---------- Output helpers ----------
if [[ -t 1 ]] && command -v tput >/dev/null 2>&1; then
  COLOR_CYAN="$(tput setaf 6 2>/dev/null || true)"
  COLOR_GREEN="$(tput setaf 2 2>/dev/null || true)"
  COLOR_YELLOW="$(tput setaf 3 2>/dev/null || true)"
  COLOR_RED="$(tput setaf 1 2>/dev/null || true)"
  COLOR_RESET="$(tput sgr0 2>/dev/null || true)"
else
  COLOR_CYAN=""
  COLOR_GREEN=""
  COLOR_YELLOW=""
  COLOR_RED=""
  COLOR_RESET=""
fi

log_info() { printf "%s[%s]%s %s\n" "$COLOR_CYAN"  "$SCRIPT_NAME" "$COLOR_RESET" "$*" ; }
log_ok()   { printf "%s[%s]%s %s\n" "$COLOR_GREEN" "$SCRIPT_NAME" "$COLOR_RESET" "$*" ; }
log_warn() { printf "%s[%s]%s %s\n" "$COLOR_YELLOW" "$SCRIPT_NAME" "$COLOR_RESET" "$*" >&2 ; }
log_err()  { printf "%s[%s]%s %s\n" "$COLOR_RED"   "$SCRIPT_NAME" "$COLOR_RESET" "$*" >&2 ; }

# ---------- Python interpreter resolution ----------
# Cross-OS fallback order:
#   1. WB_BOOTSTRAP_PYTHON env var (explicit override)
#   2. python3 (POSIX-standard name)
#   3. python (some distros only ship `python`)
#   4. py (Windows Python Launcher; ships with python.org installer)
#
# This mirrors install-skills.sh's invocation pattern and works under Git Bash
# / WSL / MSYS2 on Windows + native bash on macOS / Linux.

resolve_python() {
  if [[ -n "${WB_BOOTSTRAP_PYTHON:-}" ]]; then
    if command -v "${WB_BOOTSTRAP_PYTHON}" >/dev/null 2>&1; then
      echo "${WB_BOOTSTRAP_PYTHON}"
      return 0
    fi
    log_warn "WB_BOOTSTRAP_PYTHON=${WB_BOOTSTRAP_PYTHON} not found on PATH; falling through."
  fi
  for candidate in python3 python py; do
    if command -v "$candidate" >/dev/null 2>&1; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

# ---------- Banner ----------
log_info "${SCRIPT_NAME} v${SCRIPT_VERSION} — invoking wb-bootstrap.py for the website-builder plugin."
log_info "Plugin root: ${PLUGIN_ROOT}"
log_info "Working dir: $(pwd)"

# ---------- Locate the Python runner ----------
RUNNER="${PLUGIN_ROOT}/scripts/wb-bootstrap.py"
if [[ ! -f "$RUNNER" ]]; then
  log_err "wb-bootstrap.py runner not found at ${RUNNER}"
  log_err "  (expected sibling of this script — check plugin install integrity)"
  exit 3
fi

# ---------- Resolve Python ----------
if ! PYTHON_BIN="$(resolve_python)"; then
  log_err "No Python interpreter found on PATH."
  log_err "  Tried: python3, python, py"
  log_err "  On Windows, install Python from https://python.org and ensure it's on PATH."
  log_err "  On macOS, install via brew (brew install python) or python.org."
  log_err "  On Linux, install via your distro's package manager (apt install python3 / etc.)."
  log_err "  Or set WB_BOOTSTRAP_PYTHON to your interpreter's path."
  exit 4
fi

log_info "Python interpreter: ${PYTHON_BIN}"

# ---------- Invoke ----------
# Pass through all argv to the Python runner. Export CLAUDE_PLUGIN_ROOT so the
# runner can resolve the plugin's tests/detector.py via its env-var fallback.
export CLAUDE_PLUGIN_ROOT="${PLUGIN_ROOT}"

exec "$PYTHON_BIN" "$RUNNER" "$@"
