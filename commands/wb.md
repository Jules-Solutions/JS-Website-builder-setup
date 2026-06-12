---
name: wb
description: Run the website-builder CLI (library, keys, skills, maintain).
argument-hint: <command> [args...]  e.g. library list | keys migrate-to-env | skills update | maintain reconfig
allowed-tools: Bash(bash:*)
---

# `/wb` — website-builder CLI

Run the `wb` CLI for the website-builder plugin. The CLI manages the current
project's resource library, secret keys, installed design skills, and setup.

Invoke the launcher, passing the user's arguments through verbatim, from the
user's current project directory (the launcher reads `.website-builder/` state
relative to the working directory):

!`bash "${CLAUDE_PLUGIN_ROOT}/scripts/wb.sh" $ARGUMENTS`

Then relay the CLI's output to the user. If the command needs arguments and the
user gave none, show the available commands (the output of running it with no
arguments already lists them) and ask which they want.

## What the verbs do

The `wb` CLI exposes four command families (run `/wb <command> --help` for the
full flag surface of any one):

- **`library <verb>`** — manage cloned resources in `.website-builder/library/`.
  Verbs: `list`, `add <url>`, `remove <name>`, `refresh <name>`, `refresh-all`,
  `prune`, `inspect <name>`.
- **`keys <verb>`** — migrate API keys between backends. Verbs:
  `migrate-to-1password`, `migrate-to-env`.
- **`skills <verb>`** — manage installed design-skill flavors (v0.1: UI/UX Pro
  Max). Verbs: `update`, `sync`.
- **`maintain <verb>`** — re-run setup. Verbs: `reconfig` (re-confirm
  entry-mode / secrets-backend / flavor without destroying content),
  `install-skills` (re-run the skill installer).

## Notes for interpreting output

- `keys migrate-*` and `maintain reconfig` are interactive flows — if the CLI
  prompts, surface the prompt to the user and pass their answer back on the next
  invocation. These are not no-ops; treat a confirmation prompt as a real
  decision point, not noise.
- A "module not installed" error from `library` or `keys` means the plugin
  install is incomplete — advise reinstalling the plugin, do not try to work
  around it.
- On Windows, `wb` requires a bash environment (Git for Windows or WSL). If the
  launcher reports no bash / no Python, point the user at installing Git for
  Windows; do not attempt to translate the command into PowerShell.
