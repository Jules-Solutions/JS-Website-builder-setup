# hooks-handlers/

> Python handlers invoked by `hooks/hooks.json` for the website-builder plugin.
> Per Anthropic CC plugin spec + decision 59, hooks are configured in
> `hooks/hooks.json` and reference handlers via `${CLAUDE_PLUGIN_ROOT}/hooks-handlers/...`.

## Files

| Handler | Hook event | Matcher | Purpose |
|---|---|---|---|
| `session_start.py` | `SessionStart` | (none — fires every session) | Detects entry mode (5 modes per locked decision 15) on a fresh project, or surfaces current phase + project state on a mid-flight project. Output is injected into the agent's session context. |
| `pre_tool_use.py` | `PreToolUse` | `Edit\|Write\|MultiEdit\|Bash` | Anti-skip gating against the current phase's exit criteria. v0.1 minimal — permissive when phase contracts (Phase 2 deliverable) are absent. |

## Invocation

The handlers are invoked by Claude Code at the registered hook events. The
`hooks/hooks.json` file uses `python3` as the interpreter and resolves the
script via `${CLAUDE_PLUGIN_ROOT}/hooks-handlers/<name>.py`.

`${CLAUDE_PLUGIN_ROOT}` resolves to the plugin's installed directory at runtime.
`python3` must be available on the user's PATH. The handlers are pure-stdlib
Python — no third-party dependencies.

## Hook contract

Per the CC plugin spec:

- **SessionStart** — no stdin payload at session start. The handler reads cwd
  to determine the user's project directory. stdout is injected into the
  session as additional context. Exit 0 = success.
- **PreToolUse** — stdin contains a JSON payload describing the tool invocation
  (tool name, parameters, cwd, etc.). The handler reads and evaluates against
  the current phase's gating rules.
  - Exit 0 + empty stdout = allow silently
  - Exit 0 + stdout = allow with advisory
  - Exit non-zero + stdout = block with reason

## Why Python

- **Portable across user OSes.** Muggles run on Windows, macOS, and Linux. A
  Bash handler would not run on stock Windows; PowerShell would not run on
  stock macOS.
- **Pure stdlib.** No PyYAML, no pydantic — the handlers ship with only what
  Python 3.10+ provides. Tolerant YAML reading is implemented inline.
- **Vault discipline.** `.claude/rules/conventions.md` mandates `uv` for vault
  Python; CC plugin handlers are user-installed and run in the user's Python
  env, not the vault's. The handlers are stdlib-only so they don't depend on
  the user having `uv` installed.

## Testing

The plugin's `tests/walkthroughs/` (Captain E's deliverable) carries 5
entry-mode fixtures that exercise `session_start.py`. To smoke-test directly
during development:

```bash
# From a fresh project dir
cd /tmp && mkdir test-greenfield && cd test-greenfield
CLAUDE_PLUGIN_ROOT="$HOME/.claude/plugins/website-builder" \
  python3 "$CLAUDE_PLUGIN_ROOT/hooks-handlers/session_start.py"
```

Expected output for an empty dir: a markdown context block reporting
`Detected entry mode: greenfield`.

## Design references

- Architecture: `DESIGN-architecture.md`
  lines 233-238 (hooks spec), 240-249 (entry modes spec)
- Project scaffold: `DESIGN-project-scaffold.md`
  (`.website-builder/` layout, `project.yaml` shape)
- Ingestion + extraction: `DESIGN-ingestion-and-extraction.md`
  (phase 6.5 re-runnable ingestion logic — surfaced by the SessionStart hook
  for entry modes 2-5)
- Locked decisions: 15 (entry modes), 36 (phase 6.5 conflict default = halt +
  force user decision), 59 (manifest format + hook config)
- Anthropic CC plugin spec: `.claude/temp/ctx7-docs/claude-code-plugin-spec.md`
