# Installation

> v0.1 (invite-only): git-clone + `--plugin-dir` install per locked decision 59 of the website-builder workstream.
> v1.0 (public release at Phase 9): CC marketplace install via `/plugin install website-builder@<marketplace>`.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/claude-code) installed and configured
- `git` available on your machine
- A directory you want to use as a website project (greenfield) OR an existing project directory (has-existing-site / has-AI-output / has-Framer-attempt / has-Figma-file)

## Phase 1-8 install (current — invite-only)

### Step 1 — Clone the plugin repo

```bash
git clone https://github.com/Jules-Solutions/JS-Website-builder-setup.git ~/website-builder
```

You can clone to anywhere. The path you choose becomes the value you pass to `--plugin-dir`.

### Step 2 — Launch Claude Code with the plugin loaded

In your website project directory:

```bash
cd /path/to/your/website-project
claude --plugin-dir ~/website-builder
```

Claude Code starts with the website-builder plugin active. The SessionStart hook detects your entry mode (greenfield / has-existing-site / etc.) and routes you into the appropriate phase.

### Step 3 — Confirm install

After Claude Code starts, check that the plugin loaded:

```
/plugin list
```

You should see `website-builder` in the active plugins list.

### Step 4 — Run the bootstrap skill

```
/wb-bootstrap
```

(Or simply ask Claude *"help me build a website"* — the agent profile triggers automatically.)

The bootstrap skill scans your project directory, prompts you to confirm the entry mode it detected, fetches any upstream skills the plugin needs (`scripts/install-skills.sh`), creates `.website-builder/` state directory, and seeds `project.yaml` defaults.

## Phase 9 install (public release — coming soon)

Once the plugin is published to a Claude Code marketplace, install becomes:

```
/plugin install website-builder@claude-code-marketplace
```

No git-clone required. The plugin auto-updates via the marketplace mechanism.

## Updating during the invite-only phase

The plugin updates frequently during Phases 1-8. To pull updates:

```bash
cd ~/website-builder
git pull origin master
```

Restart Claude Code in your project directory; the new plugin version is picked up at next launch.

## Troubleshooting

**"plugin not found" after `--plugin-dir`** — the path must point at the directory containing `.claude-plugin/plugin.json`. The default clone target above (`~/website-builder`) puts it at `~/website-builder/.claude-plugin/plugin.json`. Verify with:

```bash
ls -la ~/website-builder/.claude-plugin/plugin.json
```

**"hook scripts not executing"** — the plugin's hooks are **Python** (`hooks-handlers/session_start.py` + `pre_tool_use.py`), wired via `hooks/hooks.json` and run through your Python interpreter. There are no shell scripts to mark executable (`chmod` is not needed). If a hook isn't firing, confirm Python is on your PATH (`python --version`) and that the plugin loaded (`/plugin list` shows `website-builder`).

**Anything else** — open an issue on the repo or contact Jules.Solutions directly. (During invite-only Phase, support is via direct contact rather than public issue tracker.)

## Uninstall

Remove the plugin clone:

```bash
rm -rf ~/website-builder
```

Your `.website-builder/` state directory inside the website project is independent of the plugin install — keep it (you can re-attach a future plugin install) or delete it (full reset).

## See also

- `README.md` — what the plugin is and isn't
- The website-builder workstream in the Jules.Life vault — `Workstreams/website-builder/` — has full design + architecture docs.
