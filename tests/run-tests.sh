#!/usr/bin/env bash
# run-tests.sh — entry point for the website-builder plugin test suite.
#
# Usage:
#   ./tests/run-tests.sh                  # run all tests (Tier 1 + Tier 2)
#   ./tests/run-tests.sh --tier1          # run only Tier 1 (reference-detector + fixture meta)
#   ./tests/run-tests.sh --verbose        # extra-verbose output
#   ./tests/run-tests.sh --no-uv          # use system pytest instead of uv
#
# Phase 1 / Captain E scope: entry-mode detection + bootstrap initialization
# smoke tests. End-to-end tests (real CC against a fixture) are Phase 7-8 scope.
#
# Tier 1 tests (reference detector + fixture completeness) ALWAYS pass when
# fixtures + spec are aligned. Tier 2 tests (Captain C's hook + Captain D's
# skill integration) are SKIPPED until those Captains' branches merge to dev.
# A Tier 2 skip is not a failure — it's the expected state pre-merge.

set -e

# Resolve plugin root from this script's location (one level up from tests/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TESTS_DIR="$SCRIPT_DIR"

# Default flags
TIER="all"
VERBOSE=""
USE_UV=1

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --tier1)
      TIER="tier1"
      shift
      ;;
    --verbose|-v)
      VERBOSE="-vv"
      shift
      ;;
    --no-uv)
      USE_UV=0
      shift
      ;;
    --help|-h)
      sed -n '2,15p' "${BASH_SOURCE[0]}" | sed 's/^# //;s/^#//'
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Run with --help for usage." >&2
      exit 2
      ;;
  esac
done

cd "$TESTS_DIR"

# Build pytest invocation
PYTEST_ARGS=()
if [[ -n "$VERBOSE" ]]; then
  PYTEST_ARGS+=("$VERBOSE")
fi

# Tier filtering via pytest -k expressions
case "$TIER" in
  tier1)
    PYTEST_ARGS+=("-k" "TestReferenceDetector or TestFixtureCompleteness")
    ;;
  all)
    : # no filter
    ;;
esac

echo "==> website-builder test suite"
echo "    plugin root: $PLUGIN_ROOT"
echo "    tier:        $TIER"
echo "    runner:      $([[ $USE_UV -eq 1 ]] && echo 'uv run pytest' || echo 'system pytest')"
echo

if [[ $USE_UV -eq 1 ]]; then
  if ! command -v uv >/dev/null 2>&1; then
    echo "ERROR: 'uv' not found on PATH. Install uv (https://github.com/astral-sh/uv)" >&2
    echo "       or re-run with --no-uv to use system pytest." >&2
    exit 3
  fi
  exec uv run --with pyyaml --with pytest pytest "${PYTEST_ARGS[@]}"
else
  if ! command -v pytest >/dev/null 2>&1; then
    echo "ERROR: 'pytest' not found on PATH. Install pytest + pyyaml" >&2
    echo "       or re-run with uv installed." >&2
    exit 3
  fi
  exec pytest "${PYTEST_ARGS[@]}"
fi
