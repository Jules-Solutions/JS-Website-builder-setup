---
name: wb-bootstrap
description: Use when the user invokes the website-builder agent in a fresh or unrecognized project, when no `.website-builder/` state directory exists yet, when the directory is invalid/incomplete, or when the user explicitly runs `/wb-bootstrap` or `wb maintain reconfig`. Runs first-run setup — entry-mode confirmation, secrets-backend choice, upstream skill installation via `scripts/install-skills.sh`, and `.website-builder/` state-dir initialization. Hands off to the website-builder agent for phase 1 (idea questionnaire) when complete.
version: 0.1.0
---

# wb-bootstrap — Website-builder First-Run Setup

> The plugin's entry point. Picks the user up wherever they are, sets up the project's state directory, fetches the upstream design skills they need, and hands off to the website-builder agent for the first phase of the pipeline.
>
> See `Workstreams/website-builder/foundation/DESIGN-architecture.md` (lines 38, 182-191), `foundation/DESIGN-project-scaffold.md`, `cross-cutting/DESIGN-skill-distribution.md`, and `cross-cutting/DESIGN-secrets-and-keys.md` for the design context this skill implements.

## What this skill does

Runs the website-builder plugin's first-run setup in the user's project directory. Five concerns:

1. **Entry-mode detection + confirmation** — five canonical entry modes per locked decision 15 (greenfield / has-existing-site / has-AI-output / has-Framer-attempt / has-Figma-file). The plugin's SessionStart hook (per `hooks-handlers/session_start.py`) scans for signals and emits a context block to STDOUT, which CC injects into the agent's session context. This skill consumes that injected context and confirms with the user via `AskUserQuestion`.
2. **Secrets-backend choice** — `.env` (muggle default, single-machine simple) vs 1Password CLI (opt-in for multi-machine / power-user setups). Per locked decision 29.
3. **Upstream skill install** — runs `scripts/install-skills.sh` to fetch the user-picked design-skill flavor (v0.1 ships UI/UX Pro Max only per decision 55; full 6-flavor surface in expansion phase 10) into the user's `~/.claude/skills/` directory. Per locked decision 32.
4. **`.website-builder/` state-dir initialization** — creates the canonical layout per `foundation/DESIGN-project-scaffold.md` with sensible `project.yaml` defaults seeded from the entry mode + secrets-backend choices.
5. **Hand-off to the website-builder agent** — once setup is complete, the agent's phase 1 (idea questionnaire) runs.

## When invoked

This skill is the **first-run** entry point. Trigger conditions:

- The user invokes the website-builder agent in a directory where no `.website-builder/` exists.
- A `.website-builder/` directory exists but its `project.yaml` is invalid, missing required fields, or fails schema validation (the SessionStart hook surfaces this; the user is offered re-bootstrap).
- The user explicitly types `/wb-bootstrap` to re-run setup.
- The user runs `wb maintain reconfig` (per locked decision 48; the CLI command re-invokes this skill).

The skill is **re-runnable**. If invoked when partial state exists (e.g., a previous bootstrap was cancelled mid-flight), it must detect the partial state and resume gracefully — not start over and not silently overwrite user choices. See `## Re-runnability` below.

## Step-by-step instructions for the agent

### Step 1 — Read the SessionStart hook's detection signal from the agent's session context

The SessionStart hook (Captain C's territory; `hooks-handlers/session_start.py`) emits a context block to STDOUT at CC startup. Per the canonical CC SessionStart hook spec, CC injects that STDOUT directly into the agent's session context — there is **no signal file on disk**. By the time this skill is invoked, that context is already in the agent's session and the agent reads it directly.

Look for the context block in the existing session context. It begins with the literal heading `# website-builder — session context` and contains either:

- A `## Fresh project (no `.website-builder/` state yet)` section (when the user is starting fresh) with bulleted lines:
  - `- Detected entry mode: **<mode>**` — one of `greenfield`, `has-existing-site`, `has-Framer-attempt`, `has-AI-output`, `has-Figma-file`
  - `- Signal: <signal description>` — short prose describing what the hook saw
  - `- Markers found:` — list of marker files / dirs that drove the detection (e.g., `framer.json`, `*.fig`, `package.json`)
  - Optional fields: `- Figma files:`, `- AI-output file:`, `- Top-level entries:`

- A `## Mid-project (`.website-builder/` exists)` section (when re-entering an existing project) with bulleted lines:
  - `- Current phase: **<n>**`
  - `- Entry mode: <mode>` — the mode from `project.yaml`
  - `- Stack`, `- CMS`, `- Languages`, `- Transactional` — the locked-in choices

Both sections are followed by a `## Machine-readable summary` section containing a fenced ` ```json ` block. The JSON shape:

```json
{
  "plugin": "website-builder",
  "project_root": "/path/to/user/project",
  "state_present": false,
  "entry_mode": "has-Framer-attempt",
  "entry_signals": {
    "signal": "Framer project detected",
    "markers": [{"marker": "framer.json", "label": "Framer project file"}]
  },
  "project_state": null
}
```

When `state_present` is `true`, `entry_mode` and `entry_signals` are `null` and `project_state` is the parsed `project.yaml` from disk. When `state_present` is `false`, `project_state` is `null` and the entry-mode fields are populated.

**How to consume**: prefer the JSON record (it's machine-readable and unambiguous). Fall back to the markdown bullets if the JSON block is malformed or missing — the markdown is the same data in human-readable form.

**Special case — developer in plugin dir**: if the cwd is the plugin install directory itself (the hook detects this via `CLAUDE_PLUGIN_ROOT`), the context block is a brief diagnostic only ("cwd is the plugin install dir; skipping entry-mode detection") with no entry-mode fields. Surface this to the user verbatim and stand down — they need to open a real user-project directory before bootstrap is meaningful.

**If the SessionStart context is absent** (the hook didn't fire, the skill is invoked outside a CC session, or the context block was elided), fall through to greenfield-default. Mention this to the user as a small caveat: *"I didn't get a signal from the entry-mode detector — defaulting to greenfield. If that's wrong, pick the right mode below."*

### Step 2 — Confirm entry mode with the user

Use `AskUserQuestion` to confirm. Offer the 5 canonical modes plus an "other / unsure" option:

```
Question: "What's the starting state of your website project?"
Options (single-select):
  1. greenfield — fresh project; nothing yet
  2. has-existing-site — a deployed website (any platform) you want to evolve
  3. has-AI-output — a one-shot landing page from ChatGPT / Claude.ai / v0 / Lovable / Bolt.new
  4. has-Framer-attempt — a partial Framer / Webflow / Wix / WordPress project
  5. has-Figma-file — a Figma file (often delivered by a designer)
  6. other / unsure — I'll help you figure it out
```

Pre-select the detected mode from Step 1 if confidence was `high`. If the user picks "other / unsure", run a short clarifying dialogue — ask what they have, route them to the closest of the 5 modes. Do not invent a 6th canonical mode; the design surface only supports 5.

Record the chosen mode for `project.yaml.entry_mode`.

### Step 3 — Confirm secrets-backend choice

Use `AskUserQuestion` to ask the user how they want to handle API keys:

```
Question: "Where do you want to keep API keys for this project?"
Context: "Most muggles use a .env file (simple, single-machine). Power users with
1Password use the 1Password CLI for cross-machine sync and rotation. You can
switch later via 'wb keys migrate-to-1password' or 'wb keys migrate-to-env'."

Options (single-select):
  1. .env file (recommended for muggles; simple; single-machine)
  2. 1Password CLI (recommended for multi-machine / multi-user)
  3. Skip for now — I'll set this up later when a phase needs a key
```

If the user picks 1Password:

- Verify the `op` CLI is available (`bash -lc 'op --version'`). If missing, surface the install path per the user's platform per `cross-cutting/DESIGN-secrets-and-keys.md` `## Cross-platform 1Password CLI installation`. Offer to fall back to `.env` if the user can't / won't install `op`.
- Verify the user can sign in (`op signin`). If not, walk them through it. Persist sign-in for the rest of the bootstrap.

If the user picks `.env`:

- Surface the multi-machine limitation per locked decision 44 (verbatim copy from `cross-cutting/DESIGN-secrets-and-keys.md` `## Multi-machine sync limitation`):

  > Heads up — using .env across multiple machines means you'll need to keep your .env files in sync manually. For each new machine you work on this project from, you'll re-fill in the keys. Two paths to fix this if it becomes painful: (1) Use 1Password (we'll integrate; one source of truth across machines); (2) Use a different secrets manager (you handle it; we don't reinvent the wheel). For now, .env is fine. We'll surface this again if you set up a second machine.

If the user picks "Skip for now":

- Set `secrets_backend: deferred` in `project.yaml`. The first phase that needs a key (typically phase 8 image strategy) will re-trigger the secrets-backend choice.

Record the chosen backend for `project.yaml.secrets_backend`.

### Step 4 — Confirm design-skill flavor pick

For v0.1, only one flavor ships (UI/UX Pro Max per locked decision 55). For forward-compat, still ask — if the user picks anything else, surface that the chosen flavor lands in expansion phase 10 and offer UI/UX Pro Max as the v0.1 default.

```
Question: "Which design-skill flavor do you want as your primary?"
Context: "v0.1 ships with UI/UX Pro Max. Other flavors (Impeccable, Emil Kowalski,
Taste, Framer Motion, 21st.dev) land in expansion phase 10. Pick UI/UX Pro Max
unless you have a strong reason to wait."

Options (single-select):
  1. UI/UX Pro Max — comprehensive default; available now (v0.1)
  2. Impeccable — brand vs product split (v0.2+; deferred)
  3. Emil Kowalski — animation + design engineering (v0.2+; deferred)
  4. Taste — pick a flavor (taste / soft / minimalist / brutalist) (v0.2+; deferred)
  5. Framer Motion — animation companion (v0.2+; deferred)
  6. 21st.dev Magic — agent-UX patterns (v0.2+; deferred)
```

Record the chosen primary flavor for `project.yaml.design_skill_flavor`. If the user picks anything beyond #1, write `design_skill_flavor: ui-ux-pro-max` (the v0.1 default) and `design_skill_flavor_preferred: <user-pick>` so a future bootstrap re-run after expansion phase 10 ships can install the user's actual preference.

Complementary skills are also v0.2+ — defer the question. `project.yaml.design_skill_complementary: []` for v0.1.

### Step 5 — Run `scripts/install-skills.sh`

Invoke the install script. It lives at `${CLAUDE_PLUGIN_ROOT}/scripts/install-skills.sh` (use the env var; do not hardcode the plugin path).

Cross-platform invocation:

- **macOS / Linux** — direct: `bash "${CLAUDE_PLUGIN_ROOT}/scripts/install-skills.sh" --primary ui-ux-pro-max`
- **Windows (Git Bash / WSL)** — direct, same as macOS / Linux.
- **Windows (no Bash available)** — surface a friendly message: *"This step needs Bash. On Windows, install Git for Windows (https://git-scm.com/download/win) which ships with Git Bash; then re-run `/wb-bootstrap`. Or, if you have WSL, run from a WSL shell."* Do NOT attempt to translate the script into PowerShell on the fly — that's a future Captain's territory if cross-shell support becomes a priority.

Stream the script's output to the user. The script is idempotent (per its design); a re-run after a partial install only fetches what's missing.

If the script fails:

- Network failure (can't reach upstream registry) — Tier 2 per `.claude/rules/tool-dependency-discipline.md`. Surface the failure, retry once, fall back to manual-install instructions if the second attempt fails. Do NOT silently substitute a different skill.
- Disk-space / permission failure — surface, ask user to fix, offer retry.
- Upstream URL 404 — surface; the manifest may be stale; flag a follow-up INST for the General to update the manifest.

### Step 6 — Initialize `.website-builder/` directory

Create the canonical layout per `foundation/DESIGN-project-scaffold.md`. Minimum scaffold:

```
.website-builder/
├── project.yaml              # seeded with entry-mode, secrets-backend, plugin version, current_phase: 0 (bootstrap pre-phase; phase 1 = idea questionnaire is the next step the agent enters AFTER bootstrap)
├── content/                  # empty subdirs ready to be filled by downstream phases
│   ├── pages/
│   └── strings/
├── library/                  # empty; populated by phase triggers + manual `wb library add`
├── briefs/                   # empty; populated when JSON handoff protocol fires
├── outputs/                  # empty; populated when external-tool outputs are pasted back
├── decisions/                # empty; populated by the agent when significant decisions are made
├── audit/                    # empty; populated at audit-relevant phases
├── media/                    # empty; populated as media is added
├── post-launch/              # empty placeholder; populated at deploy time per decision 45
└── README.md                 # auto-generated explainer (what's in this dir + don't edit by hand)
```

Plus the initial state files:

- `project.yaml` — seeded values, see `## Initial project.yaml` below.
- `tasks.yaml` — empty initial state: `{phases: {}}`.
- `keys.yaml` — empty initial state: `{version: 1}` (entries added when phases need keys).
- `state.yaml` — empty initial state: `{phases: {}}` for phase-by-phase state predicates (used by the SessionStart hook to know the project's current phase).

If the user picked `.env`:
- Create `.website-builder/.env.example` (committed; placeholder values; auto-populated when phases discover required keys). Initial content:

  ```
  # .env.example — committed; placeholder values; copy to .env and fill in real values
  # The website-builder will populate this as phases discover required keys.
  # Real .env file is gitignored; this file is the schema.
  ```

If the user picked 1Password:
- Create `.website-builder/.env.op` (commit-eligible; references-only; per `cross-cutting/DESIGN-secrets-and-keys.md` `## Layer 3 — 1Password CLI resolution`). Initial content:

  ```
  # .env.op — committed; 1Password references via op://vault/item/field syntax.
  # The website-builder populates this as phases discover required keys.
  # Resolved at runtime via `op run --env-file=.website-builder/.env.op`.
  ```

If the user picked "Skip for now":
- Skip both `.env.example` and `.env.op`. The first phase that needs a key will re-trigger Step 3.

### Step 7 — Extend the user-project's `.gitignore`

Append `.website-builder/` rules to the user's project `.gitignore` (create the file if it doesn't exist). Use the following block, with a clear comment header so the user knows what's plugin-managed:

```
# Added by website-builder bootstrap — runtime state, not source.
# .website-builder/ is mostly committed (state files), but secrets and resolved
# caches are gitignored. Edit at your own risk.
.website-builder/keys-resolved.tmp
.website-builder/.env
.env
.env.local
.env.*.local
.env.development
.env.production
.env.test
```

If the user picked 1Password (no `.env` files), still add the `.env*` lines defensively — users sometimes adopt `.env` later and we want to be safe-by-default. Skip if those lines already exist (idempotent extension).

The plugin's own `.gitignore` (at the plugin repo root) already gitignores `.website-builder/` for the **plugin repo** (so test fixtures don't pollute it) — that's separate from the user-project `.gitignore` we're touching here. Don't conflate the two.

### Step 8 — Generate the `.website-builder/README.md`

Write an auto-generated README explaining what's in `.website-builder/` and how the user can read it (but not edit it by hand). Include:

- One-paragraph overview of the dir's purpose
- Schema of each top-level file (project.yaml / tasks.yaml / keys.yaml / state.yaml)
- Pointer to the design surface in the Jules.Life vault: `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md`
- "What NOT to edit" — don't hand-edit `state.yaml`; the agent owns it. `project.yaml` is human-readable and editable but mind the schema.
- "How to re-run bootstrap" — the user can run `/wb-bootstrap` to re-confirm choices, or `wb maintain reconfig` once the CLI ships.

### Step 9 — Hand off to the website-builder agent for phase 1

Bootstrap is complete. The website-builder agent (Captain B's profile at `agents/website-builder.md`) takes over for phase 1 (idea questionnaire). Surface the handoff to the user:

```
Setup complete. We're ready to start designing your website.

Entry mode: <mode>
Secrets backend: <backend>
Design-skill flavor: <flavor>

Next: phase 1 (idea questionnaire). I'll ask you about the project — what
you're building, why, who it's for, and what success looks like. Take your
time — this is the foundation of everything we'll build.

Ready to start?
```

Wait for confirmation, then transition control to the website-builder agent's phase 1 behavior.

## Initial `project.yaml`

The seeded `project.yaml` after a successful bootstrap (greenfield + .env path; other entry modes adjust accordingly):

```yaml
# project.yaml — generated by wb-bootstrap
# See Workstreams/website-builder/foundation/DESIGN-project-scaffold.md for schema details.
version: 1
plugin_version: "0.1.0"        # matches .claude-plugin/plugin.json
created_at: "<ISO 8601 timestamp at bootstrap>"
bootstrap_completed_at: "<ISO 8601 timestamp at bootstrap>"

# Identity (filled by phase 1)
name: ""
slug: ""

# Pipeline state
entry_mode: "greenfield"        # set by Step 2
current_phase: 0                # 0 = bootstrap pre-phase complete, agent has NOT yet entered phase 1; phase 1 (idea questionnaire) is the next step the agent enters after bootstrap. Matches the 5 entry-mode fixtures + scripts/wb-bootstrap runner.
phase_locked: false             # true once a phase is locked, prevents accidental rollback

# Secrets backend (set by Step 3)
secrets_backend: "env"          # env | onepassword | deferred

# Design-skill flavor (set by Step 4)
design_skill_flavor: "ui-ux-pro-max"
design_skill_flavor_preferred: null  # populated if user picked a v0.2+ flavor; we use v0.1 default for now
design_skill_complementary: []       # populated in v0.2+ (currently empty for v0.1)

# Stack / CMS (filled by phase 11+)
stack: null
cms: null
transactional: null
languages: ["en"]
default_language: "en"
component_library: null

# Component-library composition (per locked decision 46)
# Set at phase 18 (component build) — primary library + 1-2 complementary max.
component_library_composition:
  primary: null
  complementary: []
```

For non-greenfield entry modes, append a `pre_existing_artifacts` block populated by the SessionStart hook's signal (Step 1 detection):

```yaml
pre_existing_artifacts:
  detected_at: "<ISO 8601>"
  signals:
    - { type: "framer_project", path: "framer.json" }
    - { type: "ai_output_html", path: "landing.html" }
    # ... etc per the hook's signal
  ingestion_phase_pending: true  # phase 6.5 (artifact ingestion) will run on these
```

The phase-6.5 logic (Captain B / future phase-skill Captain's territory) consumes `pre_existing_artifacts` to drive the ingestion flow.

## Output artifacts

Files created in the user's project directory after a successful bootstrap:

| Path | Content |
|---|---|
| `.website-builder/project.yaml` | Seeded with bootstrap choices (see above). |
| `.website-builder/tasks.yaml` | `{phases: {}}` initial state. |
| `.website-builder/keys.yaml` | `{version: 1}` initial state. |
| `.website-builder/state.yaml` | `{phases: {}}` initial state. |
| `.website-builder/README.md` | Auto-generated explainer. |
| `.website-builder/content/pages/` | Empty dir. |
| `.website-builder/content/strings/` | Empty dir. |
| `.website-builder/library/` | Empty dir. |
| `.website-builder/briefs/` | Empty dir. |
| `.website-builder/outputs/` | Empty dir. |
| `.website-builder/decisions/` | Empty dir. |
| `.website-builder/audit/` | Empty dir. |
| `.website-builder/media/` | Empty dir. |
| `.website-builder/post-launch/` | Empty dir. |
| `.website-builder/.env.example` | If `.env` path picked. |
| `.website-builder/.env.op` | If 1Password path picked. |
| `<project-root>/.gitignore` | Extended with the website-builder gitignore block (Step 7). |

User-level files (outside the project dir):

| Path | Content |
|---|---|
| `~/.claude/skills/ui-ux-pro-max/` | The UI/UX Pro Max skill, fetched by `scripts/install-skills.sh`. |
| `.website-builder/skills-installed.yaml` | Records what was installed + version + fetched timestamp (for `wb skills sync`). |

## Failure modes

### `op` CLI not installed but user picked 1Password

Surface: *"You picked 1Password but the `op` CLI isn't installed. Want me to walk you through installing it (per your platform), or fall back to `.env` for now?"*

Walk through install per `cross-cutting/DESIGN-secrets-and-keys.md` `## Cross-platform 1Password CLI installation`. If user can't / won't install, fall back to `.env` and update `project.yaml.secrets_backend: env`.

### `.website-builder/` partially exists from a prior abandoned bootstrap

Detect by checking for `project.yaml` and validating its schema. Three sub-cases:

1. **`project.yaml` exists + valid + `bootstrap_completed_at` set** — bootstrap already ran successfully. Don't overwrite. Ask user: *"Bootstrap already ran on `<bootstrap_completed_at>`. Want to (a) skip and continue from current_phase, (b) re-run bootstrap (will reset entry-mode + secrets choices but preserve content/), or (c) full reset (delete `.website-builder/` and start over)?"*
2. **`project.yaml` exists + invalid** — schema violation. Surface the diagnostic. Offer: *"Your project.yaml has a problem (`<diagnostic>`). Want me to (a) try to fix it automatically, or (b) re-run bootstrap fresh?"*
3. **Some files exist but `project.yaml` doesn't** — partial state. Detect what's there, then resume from the appropriate step. Don't re-create dirs that exist; don't re-write README if it's already there. The skill is **additive** in this case, not destructive.

### User cancels mid-bootstrap

Per `AskUserQuestion` semantics, the user can interrupt. If they do, leave `.website-builder/` in whatever partial state it's in, and write a `.website-builder/.bootstrap-cancelled` marker file with the timestamp + the step we were on. Next bootstrap run reads the marker and offers to resume.

### `scripts/install-skills.sh` fails after upstream skill fetch but before recording in `skills-installed.yaml`

This is a partial install. The installed skill is on disk; the record isn't. The script's idempotence (per its design) handles this — re-run picks up where we left off.

### User picks an entry mode that conflicts with detected signals

E.g., the SessionStart hook detected `has-Framer-attempt` (high confidence — found `framer.json`) but the user picks `greenfield`. Don't blindly accept; ask the user to confirm: *"You picked greenfield but I see Framer files in this directory. Are you sure? If so, I'll move them aside; if not, want to switch to has-Framer-attempt?"*

### Network unavailable during `install-skills.sh`

Tier 2 per `.claude/rules/tool-dependency-discipline.md`. Surface, retry, fall back to "you can complete bootstrap without the skill installed; the skill installs the next time you have network and run `wb skills update` or re-run /wb-bootstrap". Mark `skills-installed.yaml` with `installation_pending: true` so the deferred install is auditable.

## Re-runnability

Per locked decision 48, `wb maintain reconfig` re-runs this skill. Re-runs MUST handle existing state gracefully:

- Detect `.website-builder/project.yaml` and read existing values
- Re-prompt only the values the user wants to change (the user can confirm "keep current" for any of the 4 choices in steps 2-5)
- Never destructively overwrite content/, media/, or decisions/ on re-run — those are user-authored and re-bootstrap is about config, not content reset
- The `.bootstrap-cancelled` marker is cleared on successful completion of a re-run

## Cross-references

- Architecture: `Workstreams/website-builder/foundation/DESIGN-architecture.md` (skill load order, `wb-bootstrap` slot)
- Project scaffold: `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` (canonical `.website-builder/` layout this skill creates)
- Skill distribution: `Workstreams/website-builder/cross-cutting/DESIGN-skill-distribution.md` (the `scripts/install-skills.sh` design + composition manifests)
- Secrets and keys: `Workstreams/website-builder/cross-cutting/DESIGN-secrets-and-keys.md` (`.env` vs 1Password hybrid + multi-machine limitation)
- Locked decisions 15, 29, 32, 33, 43, 44, 48, 55: STATE doc at `Workstreams/website-builder/website-builder.md`
- CC plugin spec: `.claude/temp/ctx7-docs/claude-code-plugin-spec.md` (skill format, frontmatter schema)
- Tool / dep discipline: `.claude/rules/tool-dependency-discipline.md` (Tier 2 third-party-failure handling for upstream-skill fetches)
