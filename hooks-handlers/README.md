# hooks-handlers/

> Python handlers invoked by `hooks/hooks.json` for the website-builder plugin.
> Per Anthropic CC plugin spec + decision 59, hooks are configured in
> `hooks/hooks.json` and reference handlers via `${CLAUDE_PLUGIN_ROOT}/hooks-handlers/...`.

## Files

| Handler | Hook event | Matcher | Purpose |
|---|---|---|---|
| `session_start.py` | `SessionStart` | (none — fires every session) | Detects entry mode (5 modes per locked decision 15) on a fresh project, or surfaces current phase + project state on a mid-flight project. Output is injected into the agent's session context. |
| `pre_tool_use.py` | `PreToolUse` | `Edit\|Write\|MultiEdit\|Bash` | Anti-skip gating against the current phase's exit criteria. v0.1 minimal — permissive when phase contracts (Phase 2 deliverable) are absent. |

## What the PreToolUse gate does and does not gate

The gate refuses a forward-skip into building or deploying the SITE. It does not touch the files people
and agents use to collaborate and to keep the project's records:

- **Writes** (Write / Edit / MultiEdit) to `comms/`, `docs/`, `CLAUDE.md`, `README.md` and `.claude/`, plus
  any entry in `project.yaml.gate_exempt_paths`, are class `meta-write`: allowed at every phase, silently.
  `gate_exempt_defaults: false` drops the built-in entries. Schema: `state/README.md` § `project.yaml`.
  Paths are resolved (absolute or relative, either slash, `..` collapsed) before they are matched, so
  `comms/../src/app/page.tsx` is a code write.
- **`git`** commands (`git add`, `git commit`, `git push`, ...) are never build-deploy, whatever their
  arguments say (a commit message may mention "vercel"). A deploy chained after git still is one:
  `git commit -m x && vercel --prod` is blocked. The gate that keeps site code out of a push is code-write
  (the editor tools cannot create site files before phase 18); the hook is a discipline aid, not a sandbox,
  and does not inspect what a `git push` carries.

## Invocation

The handlers are invoked by Claude Code at the registered hook events, through
the launcher `run.sh`. Each command in `hooks/hooks.json` is

```
sh "${CLAUDE_PLUGIN_ROOT}/hooks-handlers/run.sh" "${CLAUDE_PLUGIN_ROOT}/hooks-handlers/<name>.py"
```

`${CLAUDE_PLUGIN_ROOT}` resolves to the plugin's installed directory at runtime
(forward-slash form on Windows, where Claude Code runs shell-form hooks through
Git Bash). The handlers are pure-stdlib Python — no third-party dependencies.

### Why a launcher (and not `python3 X || python X || py X`)

A hook reads its payload from stdin exactly once, and a non-zero exit is how a
PreToolUse handler says BLOCK (exit 2). With an `||` chain, that exit 2 made the
shell start the next interpreter on the already-consumed stdin; it read an empty
payload, allowed the call and exited 0, so the block never reached Claude Code.
`run.sh` instead chooses ONE interpreter first (the first of `python3`, `python`,
`py -3` whose `-V` prints `Python 3.x`, which also skips a Windows Store alias stub
and a Python 2 `python`), then `exec`s it. The handler runs exactly once; its
stdin, stdout, stderr and exit code are the hook's. With no usable interpreter
it exits 1 (a non-blocking hook error: the tool still runs), never 2.

Do not put a `||` fallback back into `hooks.json`; `tests/test_pre_tool_use.py`
(`TestConfiguredHookLauncher`) fails if you do.

### What the PreToolUse handler returns

BLOCK: stdout JSON `{"hookSpecificOutput": {"hookEventName": "PreToolUse",
"permissionDecision": "deny", "permissionDecisionReason": "..."}, "systemMessage":
"..."}`, the same reason on stderr, exit 2. Claude Code 2.1.295 ignored the deny
JSON when `hookEventName` and `permissionDecisionReason` were missing. ALLOW:
silent, or `{"systemMessage": "<advisory>"}`; never a `permissionDecision`,
because `allow` auto-approves the call past the user's permission prompt.

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
