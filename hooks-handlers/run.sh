#!/bin/sh
# run.sh -- launch a website-builder hook handler with ONE Python 3 interpreter.
#
# Usage (hooks/hooks.json):  sh "${CLAUDE_PLUGIN_ROOT}/hooks-handlers/run.sh" "<handler>.py"
# stdin is the hook payload; the handler's stdout, stderr and exit code are ours.
#
# Why this exists. hooks.json used to say `python3 X || python X || py X`. A hook
# reads its payload from stdin exactly once. When the handler exits non-zero --
# the PreToolUse BLOCK is exit 2 -- the shell ran the NEXT interpreter, which
# found stdin already consumed, saw an empty payload, allowed the call and
# exited 0. The block never reached Claude Code. This launcher decides WHICH
# interpreter to use before running anything, then `exec`s it: the handler runs
# exactly once and nothing is retried on a non-zero exit.
#
# Picking. The first of `python3`, `python`, `py -3` whose `-V` prints
# "Python 3.x". That skips a missing command, a Windows Store alias stub
# (python3.exe that only opens the Store and exits non-zero) and a Python 2
# `python`. `-V` does not read stdin, so the payload is untouched.
#
# Shell. POSIX sh only. Claude Code runs shell-form hooks through Git Bash on
# Windows and /bin/sh elsewhere. Invoked as `sh run.sh`, so no exec bit is needed.

if [ "$#" -lt 1 ]; then
  echo "website-builder: run.sh needs the handler script path as its first argument" >&2
  exit 1
fi

for candidate in "python3" "python" "py -3"; do
  # $candidate is deliberately unquoted: "py -3" must split into program + flag.
  version=$($candidate -V 2>&1) || continue
  case $version in
    "Python 3."*) exec $candidate "$@" ;;
  esac
done

# No usable interpreter: exit 1 is a non-blocking hook error (the tool still
# runs), never the exit 2 that would block it.
echo "website-builder: no Python 3 interpreter found (tried python3, python, py -3); hook not run" >&2
exit 1
