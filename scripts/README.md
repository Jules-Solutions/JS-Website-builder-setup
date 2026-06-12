# `wb` CLI — namespace + module-boundary contract

> This README is the **Phase 5 Captain-0 prep contract**. It locks the `wb` CLI's command surface, the module ownership boundary between Captains O / P / Q (per locked decision 78), and the per-Captain write-zones for the whole Phase 5 wave (M / N / O / P / Q). All five Captains build against the boundaries fixed here without needing to talk to each other.
>
> Genre sibling: `cms-adapters/README.md` (Phase 4 Captain-0 prep) + `adapters/README.md` (Phase 3). This is the lighter Phase 5 analog — no new top-level adapter dir, one shared CLI surface + one shared skill-bundle manifest schema.
>
> **Placement note (General Option-B decision, 2026-06-12):** this contract lives at `scripts/README.md` — NOT `commands/README.md` — because the CC plugin spec auto-registers **every** `commands/*.md` as a slash command (a `commands/README.md` would ship a junk `/README` command). The repo's genre rule holds: *the contract doc is the README of the directory where the contracted code lands* — and the contracted code (O's dispatcher + P's library module + Q's keys module) lands in `scripts/`. **`commands/` is CC-reserved: NO `.md` may be placed there except real slash-command wrappers** (Captain O's `commands/wb.md` is the only Phase 5 entry).
>
> **Anchors:** `Workstreams/website-builder/foundation/DESIGN-architecture.md` (CLI exposure + plugin layout), `Workstreams/website-builder/cross-cutting/DESIGN-resource-curation.md` (library verbs), `Workstreams/website-builder/cross-cutting/DESIGN-secrets-and-keys.md` (keys verbs), `Workstreams/website-builder/cross-cutting/DESIGN-skill-distribution.md` (skills verbs + install-skills.sh), `Workstreams/website-builder/BUILD-strategy.md` Phase 5 (lines 209-230), STATE doc decisions 29 / 32 / 42 / 48 / 55 / 59 / 65 / 75 / 77 / 78.

---

## OQ-1 resolution — how the `wb` surface maps onto CC plugin primitives

**Question:** In a CC plugin, `commands/` holds slash-command markdown files. Is the `wb` surface (a) slash commands wrapping Python scripts, (b) a Python CLI under `scripts/` with `commands/` carrying thin slash-command wrappers, or (c) something else?

**Resolution: option (b).** The `wb` CLI is implemented as **Python modules + a dispatcher under `scripts/`**; the `commands/` directory carries **thin slash-command markdown wrappers** that invoke those scripts via `${CLAUDE_PLUGIN_ROOT}`.

**Why (b), with evidence:**

1. **CC plugin spec (authoritative, via `plugin-dev:plugin-structure` skill, 2026-06-12):**
   - `commands/` → "Slash commands (`.md` files)"; auto-discovered; each `.md` file becomes a native `/command-name`. Format = YAML frontmatter (`name`, `description`) + instruction body.
   - `scripts/` → "Helper scripts and utilities" — where executable logic lives.
   - Slash commands and skills reference scripts via `${CLAUDE_PLUGIN_ROOT}/scripts/...` (the portable-path contract; never hardcode, never `~`, never CWD-relative).
   - The plugin manifest (`.claude-plugin/plugin.json`) has **no `commands` custom-path override**, so `commands/*.md` auto-discovers.

2. **Established repo precedent (do not diverge from it):** the existing `wb-bootstrap` surface is exactly this shape — `skills/wb-bootstrap/SKILL.md` invokes `${CLAUDE_PLUGIN_ROOT}/scripts/install-skills.sh`; `scripts/wb-bootstrap.sh` is a thin cross-OS bash launcher that resolves a Python interpreter and `exec`s `scripts/wb-bootstrap.py` (the real runner). The `wb` CLI follows the same launcher→runner→modules layering.

3. **Decision 78 requires it:** "O's CLI imports and calls P/Q modules." Importable modules = Python under `scripts/`, not slash-command markdown. A slash-command `.md` can't `import` another `.md`.

4. **Design docs are consistent, not contradictory:** `DESIGN-architecture.md` says the CLI is "exposed via the plugin's slash-command surface" (= `commands/`, the user-facing trigger) AND `DESIGN-resource-curation.md` line 197 / `DESIGN-skill-distribution.md` say it's "implemented as part of the plugin's bootstrap skill" / `scripts/`. Those are the two halves of option (b): the slash-command is the *trigger surface*; the script is the *implementation*. **No pause-and-report was required** — spec and design docs agree.

**Concrete consequence for the wave:**
- Captain O authors the `scripts/` dispatcher + module-glue + the `commands/*.md` slash-command wrappers.
- Captains P and Q author their **runtime modules under `scripts/`** (importable by O's dispatcher) — they do NOT author slash-command markdown.
- The user types `/wb` (or a sub-verb slash command) → the slash-command body shells out to `${CLAUDE_PLUGIN_ROOT}/scripts/<dispatcher>` → dispatcher imports/calls P's library module + Q's keys module + O's own maintain/skills logic.

> **Implementation latitude left to Captain O (not locked here):** the exact dispatcher filename (e.g. `scripts/wb.py` + `scripts/wb.sh` launcher mirroring the `wb-bootstrap` pair), the exact number of `commands/*.md` files (one umbrella `/wb` vs one per top verb), and the internal arg-parsing library. What IS locked: dispatcher + modules live under `scripts/`; wrappers live under `commands/`; module import boundary per § "Module boundary" below; portable-path discipline.

---

## Verb surface (locked — anchored in design docs + decision 48, NOT invented)

Canonical decision-48 surface (STATE doc line 115), reconciled with the per-concern design docs. The verb set is the contract; Captains MUST implement exactly these verbs (adding `--flags` within a verb is fine; adding/renaming top-level verbs is an architectural change requiring General review).

### `wb library <verb>` — owned by Captain P (`DESIGN-resource-curation.md` § CLI sketch, lines 166-195)

| Verb | Behavior | Source |
|---|---|---|
| `wb library list` | List all cloned resources in `.website-builder/library/` — name, source URL, clone date, last-used phase. | DESIGN-resource-curation lines 162-164, 171-172 |
| `wb library add <url>` | Add a resource. Auto-detect type (web page / GitHub repo / Figma file). Flags: `--as <subdir>`, `--tag <tag>`. | lines 140-157, 174-178 |
| `wb library remove <name>` | Remove a resource + update `library/README.md`. Flag: `--keep-files`. | lines 158-160, 180-182 |
| `wb library refresh <name>` | Re-fetch a resource that may have changed; update local copy + clone date. | lines 184-185 |
| `wb library prune` | Remove entries not referenced by current project state (interactive; confirm before delete). | lines 191-192 |
| `wb library inspect <name>` | Show details: source, type, size, consumers (which phase contracts reference it). | lines 193-194 |

> **`refresh-all` note:** `DESIGN-resource-curation.md` line 187 sketches `wb library refresh-all` and decision 48 (STATE line 115) lists it. The INST headline verb-set names only the six above. **Locked:** ship `refresh-all` as documented in decision 48 — it is in scope for Captain P (refresh every `clone-into-project` entry; warn on local edits that would be overwritten). It is a sibling of `refresh`, not a separate concern.

### `wb keys <verb>` — owned by Captain Q (`DESIGN-secrets-and-keys.md` § Migration paths, lines 443-472)

| Verb | Behavior | Source |
|---|---|---|
| `wb keys migrate-to-1password` | Read `.env`; per key, prompt for `op://` destination; create item via `op item create`; flip `keys.yaml` entries to `source: onepassword`; optionally remove from `.env`; verify resolution. | DESIGN-secrets-and-keys lines 445-455 |
| `wb keys migrate-to-env` | Resolve all `op://` refs to values; write to `.env`; flip `keys.yaml` to `source: env`; verify; remind about `.gitignore`. | lines 457-468 |

> **Keys verb scope (locked):** decision 48 names exactly the two `migrate-*` verbs under `wb keys`. The session-start **resolver** (`keys.yaml` → env vars, `.env` + `op` layers, the validation block in `DESIGN-secrets-and-keys.md` lines 173-185 + 474-488) is Captain Q's module too, but it is invoked by the SessionStart hook / resolver entry point — NOT a `wb keys` sub-verb. Captain Q ships both the `migrate-*` CLI verbs AND the importable resolver module. A `wb keys list` / `wb keys status` convenience verb is **NOT** in the decision-48 surface — do not add it without General review.

### `wb skills <verb>` — owned by Captain O (dispatcher), backed by `scripts/install-skills.sh` (`DESIGN-skill-distribution.md` lines 252-266, 354-371)

| Verb | Behavior | Source |
|---|---|---|
| `wb skills update` | Check installed design skills for newer upstream versions; prompt per skill; fetch + replace + verify load. v0.1: UI/UX Pro Max only (decision 55). | DESIGN-skill-distribution lines 252-264 |
| `wb skills sync` | On a fresh machine, read `.website-builder/skills-installed.yaml`; install configured-but-missing skills. | lines 354-371 |

> Both `wb skills` verbs delegate to the existing `scripts/install-skills.sh` (Phase 1, 16 KB). Captain O wires the dispatcher → `install-skills.sh` invocation; O does **not** rewrite `install-skills.sh` (it's read-only Phase-1 substrate — see write-zone table).

### `wb maintain <verb>` — owned by Captain O (`wb-bootstrap` re-invocation; decision 48)

| Verb | Behavior | Source |
|---|---|---|
| `wb maintain reconfig` | Re-invoke the `wb-bootstrap` skill / `scripts/wb-bootstrap.py` runner to re-confirm entry-mode / secrets-backend / flavor choices without destroying content. | STATE line 115; `skills/wb-bootstrap/SKILL.md` § Re-runnability (lines 391-399) |
| `wb maintain install-skills` | Re-run `scripts/install-skills.sh` directly (decision 48 lists `maintain {reconfig\|install-skills}`). | STATE line 115; `scripts/install-skills.sh` |

> `wb maintain` delegates to existing Phase-1 scripts (`wb-bootstrap.py` / `wb-bootstrap.sh` / `install-skills.sh`) — all read-only for Captain O. O wires the dispatch; O does not rewrite the runners.

---

## Module boundary (locked per Decision 78)

Decision 78 (STATE doc line 163) resolves the BUILD-strategy ambiguity between decision 48 (all sub-verbs worded under O) and decisions 42/29 (library/keys runtime under P/Q). The boundary, per `modular-build-convention.md` (each module = one job, clean interface, importable in isolation):

```
              ┌─────────────────────────────────────────────┐
   user types │  /wb ...   (commands/*.md slash wrappers)    │   ← Captain O authors
   a slash    └───────────────────────┬─────────────────────┘
   command                            │ shells out via ${CLAUDE_PLUGIN_ROOT}
                                       ▼
              ┌─────────────────────────────────────────────┐
              │  scripts/<wb dispatcher>  (entry + argparse)  │   ← Captain O authors
              │  - routes `library *`  → P's module           │
              │  - routes `keys *`     → Q's module           │
              │  - handles `skills *`  → calls install-skills.sh
              │  - handles `maintain *`→ calls wb-bootstrap.*  │
              └───────┬───────────────────────────┬───────────┘
        import/call   │                           │   import/call
                      ▼                           ▼
       ┌──────────────────────────┐   ┌──────────────────────────┐
       │ scripts/<library module> │   │ scripts/<keys module>     │
       │   Captain P              │   │   Captain Q               │
       │ - library list/add/...   │   │ - resolver (env/1Password)│
       │ - auto-clone runtime     │   │ - migrate-to-1password    │
       │   (session-start +       │   │ - migrate-to-env          │
       │    phase-trigger)        │   │ - keys.yaml read/validate │
       └──────────────────────────┘   └──────────────────────────┘
```

### The import/call interface (concrete enough to build against without cross-Captain talk)

The dispatcher (O) calls P's and Q's modules through a **stable function contract**. Captain O depends on these signatures; Captains P and Q provide them. **This is the locked interface — its shape is fixed; the exact module filenames are P's and Q's choice (suggested names given), but the public entry-point functions MUST match this contract.**

**Captain P — library module** (suggested file: `scripts/wb_library.py`). Public entry point:

```python
def run(argv: list[str], *, project_root: Path) -> int:
    """Dispatch a `library` sub-verb.
    argv: the args AFTER `wb library` (e.g. ["add", "https://...", "--tag", "docs"]).
    project_root: the user's project dir (cwd of the `wb` invocation; contains .website-builder/).
    Returns a process exit code (0 = success).
    Verbs handled: list | add | remove | refresh | refresh-all | prune | inspect.
    """
```

Plus the **auto-clone runtime** (called by the SessionStart hook + phase-entry logic, NOT via the `wb` CLI). Public entry point:

```python
def autoclone_for_state(project_root: Path, *, trigger: str, phase: int | None = None) -> list[CloneResult]:
    """Run auto-clones for the project's current state.
    trigger: "session-start" | "phase-entry".
    phase: the phase number when trigger == "phase-entry"; None for session-start.
    Reads project.yaml (stack/cms/component_library/commerce/flavors) + the phase contract's
    `library_clones_at_entry` field (see § library_clones_at_entry schema). Idempotent:
    skips resources already present unless freshness is in question.
    Absent/empty `library_clones_at_entry` → returns [] (no clones). Defensive-read: never throw on a
    contract that omits the field.
    """
```

**Captain Q — keys module** (suggested file: `scripts/wb_keys.py`). Public entry points:

```python
def run(argv: list[str], *, project_root: Path) -> int:
    """Dispatch a `keys` sub-verb.
    argv: args after `wb keys` (e.g. ["migrate-to-1password"]).
    Verbs handled: migrate-to-1password | migrate-to-env.
    Returns a process exit code.
    """

def resolve_keys(project_root: Path) -> dict[str, str]:
    """Resolve keys.yaml → env-var dict. Reads .env (source: env) + op:// refs (source: onepassword).
    Called by the SessionStart hook / resolver entry point — NOT a `wb keys` sub-verb.
    Returns {env_var_name: value}. Raises a typed error with a fix-path message on unresolved required keys.
    """
```

**Captain O — dispatcher** (suggested files: `scripts/wb.py` runner + `scripts/wb.sh` launcher mirroring the `wb-bootstrap` pair; `commands/wb.md` slash wrapper). O imports P's and Q's modules:

```python
# inside scripts/wb.py (illustrative — O owns the real impl)
from wb_library import run as library_run     # Captain P
from wb_keys import run as keys_run           # Captain Q
# `skills` + `maintain` delegate to existing scripts via subprocess:
#   skills update/sync  -> scripts/install-skills.sh
#   maintain reconfig   -> scripts/wb-bootstrap.{sh,py}
#   maintain install-skills -> scripts/install-skills.sh
```

**Interface rules (locked):**
- Modules are **import-safe**: importing `wb_library` / `wb_keys` must have **no side effects** (no network, no file writes, no `op` calls at import time). All work happens inside the entry-point functions.
- Modules **do not import the dispatcher** (no circular dependency). O depends on P/Q; P/Q do not depend on O.
- P and Q **do not import each other**. If a verb needs both (none in the locked surface do), it routes through O.
- `project_root` is passed in explicitly — modules do not read `os.getcwd()` themselves (testability; mirrors `wb-bootstrap.py`'s `Path.cwd()`-via-contract pattern).
- Each module is independently testable with a synthetic `.website-builder/` fixture (see Phase 5 test conventions in `tests/README.md`).

---

## Cross-platform invocation (match existing `scripts/` precedent)

The `wb` CLI must work the same way `wb-bootstrap` + `install-skills.sh` already do:

- **macOS / Linux / Windows-with-bash (Git Bash, WSL, MSYS2):** the bash launcher (`scripts/wb.sh` — Captain O) resolves a Python interpreter in the order `WB_*_PYTHON` env override → `python3` → `python` → `py` (Windows Python Launcher), then `exec`s the Python runner. This is the exact pattern in `scripts/wb-bootstrap.sh` lines 65-80 — **copy it, don't reinvent it.**
- **Windows without any bash:** per the precedent in `skills/wb-bootstrap/SKILL.md` Step 5 (lines 158-160) — surface a friendly message pointing the user at Git for Windows (ships Git Bash) or WSL. **Do NOT translate the CLI into PowerShell on the fly.** If first-class PowerShell support becomes a priority, that is a future Captain's INST, not Phase 5 scope.
- **`${CLAUDE_PLUGIN_ROOT}` discipline:** the slash-command wrappers (`commands/*.md`) and any script-to-script reference use `${CLAUDE_PLUGIN_ROOT}/scripts/...`. The bash launcher resolves `PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-<one-level-up-from-scripts>}"` (precedent: `wb-bootstrap.sh` lines 31-33) and exports it before invoking the Python runner so the runner can resolve sibling modules + `tests/detector.py`.
- **Python invocation in the runner:** prefer the repo's `uv`-based convention where the runner needs third-party deps (mirrors `tests/run-tests.sh` `uv run --with ...`). Pure-stdlib modules can run under the resolved interpreter directly. If a module needs a dep (e.g. `pyyaml` for `keys.yaml`/`project.yaml`), declare it the same way the test runner does — do not silently rely on system site-packages.

---

## `library_clones_at_entry` schema (locked — Deliverable 3)

Phase contracts declare their auto-clone triggers in a **frontmatter field** named `library_clones_at_entry`. This is the read-side contract for Captain P's `autoclone_for_state(..., trigger="phase-entry", phase=N)`.

**Decision: frontmatter field, not a body section.** Rationale:
- The phase-contract frontmatter is already the machine-readable header (`phase`, `group`, `skill`, `prev_phase`, `next_phase`, `re_runnable`, `relates_to` — see `phase-contracts/11-stack-decision.md` lines 1-23). Auto-clone triggers are machine-read by the hook/runtime, so they belong in frontmatter alongside the other machine-read fields, not in human-prose body.
- A body section would force P's runtime to parse markdown prose; a frontmatter list is a clean YAML read (consistent with how `session_start.py` / the runtime already parse `project.yaml`).

**Schema:**

```yaml
# phase-contracts/NN-*.md frontmatter (NEW optional field)
library_clones_at_entry:
  - resource: <catalogue-key-or-url>      # required: what to clone
    when: <condition>                       # optional: a project.yaml predicate gating the clone
    as: <subdir>                            # optional: target subdir under .website-builder/library/
    note: <human reason>                    # optional: why this phase needs it
```

- `library_clones_at_entry` is a **list** (zero or more entries). **Absent or empty list = no auto-clones at this phase** — this is the default for the vast majority of the 38 contracts.
- `resource` — required per entry. Either a catalogue key (resolved against `DESIGN-ecosystem-catalog.md`) or a literal URL (same input space as `wb library add <url>`).
- `when` — optional predicate over `project.yaml` (e.g. `stack == "astro"`, `transactional == true`, `component_library == "shadcn"`). Absent `when` = always clone at this phase entry. Predicate grammar is **Captain P's choice** (suggested: simple `key op value` strings P evaluates against the loaded `project.yaml`) — not locked here beyond "must read from `project.yaml`".
- `as` / `note` — optional, mirror the `wb library add --as` flag + the `library/README.md` provenance note.

**Example (phase 17 design-system entry, per `DESIGN-resource-curation.md` lines 234-242):**

```yaml
library_clones_at_entry:
  - resource: awesome-design-md-corpus
    as: awesome-design-md
    note: "10-20 most-relevant exemplars based on chosen aesthetic (phase 17)"
  - resource: shadcn-components
    when: component_library == "shadcn"
    as: docs
    note: "component-library reference for phase 18 build"
```

**CRITICAL — do NOT mass-edit the 38 phase contracts.** This Captain-0 prep packet locks the *schema* only. Captain P wires the **read side defensively**: a contract with no `library_clones_at_entry` field yields `[]` (no clones, no error). Back-filling the field into the contracts that need it (17 / 18 / 24a / 24b / 28 / 29 + session-start stack/cms triggers per `DESIGN-resource-curation.md` lines 231-242) is a **future follow-up INST**, NOT Phase 5 work. Phase 5's DoD ("`.website-builder/library/` populates via auto-clone + manual-add") is met by: P's `autoclone_for_state` runtime + the manual `wb library add` path + at least one demonstration (P may add the field to ONE contract — phase 17 — as a working example/test fixture, but MUST NOT sweep all 38).

> Placement note: this schema lives here in `scripts/README.md` § library (the closest design-doc-consistent home — the library runtime + its CLI are documented together). It is cross-referenced from `tests/README.md` Phase 5 conventions. No `phase-contracts/README.md` exists, so this is the canonical home for the field's definition.

---

## Per-Captain write zones — the collision-prevention table (locked)

Recon verdict (General orient-time, decision 78b): **no inherent file-path collisions across M / N / O / P / Q — behavioral interlocks only.** This table makes that explicit. Each Captain writes ONLY inside its zone; everything else is READ-ONLY. Worktree discipline per § below.

| Captain | Concern | Exclusive write paths |
|---|---|---|
| **M** | UI/UX Pro Max design-skill bundle | `skills-bundle/ui-ux-pro-max.md` (the composition manifest) + `tests/skills-bundle/ui-ux-pro-max/` (manifest-validation fixture, if M adds one per `tests/README.md` Phase 5 conventions). Per decision 55, ONLY the UI/UX Pro Max manifest ships in v0.1 — M does NOT author the other 5 flavor manifests. |
| **N** | Stitch extraction | `extraction/stitch.md` (the extraction recipe — **already exists** as Phase-3-prep substrate, committed in `a5960c4`; N **extends it in place** with the Phase-5 runtime-wiring it needs, not creates it from scratch) + `tests/extraction/stitch/` (the end-to-end extraction fixture per BUILD-strategy DoD line 225 "Stitch extraction runs from a URL → DESIGN.md import works end-to-end" — N's primary Phase-5 deliverable). N does NOT touch the other 4 extractors (`divmagic.md` / `figma-design-to-json.md` / `ai-output.md` / `playwright-walk.md` — all also already exist as Phase-3-prep substrate; their Phase-5+ runtime is out of scope per decision 55, Phase 10). |
| **O** | `wb` CLI dispatcher + slash wrappers + maintain/skills verbs | `scripts/wb.py` + `scripts/wb.sh` (dispatcher + launcher) + `commands/wb.md` (and any further `commands/*.md` slash wrappers O chooses) + `tests/cli/` (CLI dispatch tests per Phase 5 conventions). O imports P/Q modules + shells to `install-skills.sh` / `wb-bootstrap.*` — reads them, does not edit them. |
| **P** | Resource-curation library module + auto-clone runtime | `scripts/wb_library.py` (library module — `list/add/remove/refresh/refresh-all/prune/inspect` + `autoclone_for_state`) + `tests/library/` (library-runtime tests). P MAY add `library_clones_at_entry` to **phase 17 only** as a working example; P MUST NOT sweep all 38 contracts. |
| **Q** | Secrets resolver module + keys migrate verbs | `scripts/wb_keys.py` (keys module — resolver + `migrate-to-1password` + `migrate-to-env`) + `tests/keys/` (secrets-flow tests). Q reads `DESIGN-secrets-and-keys.md` keys.yaml/.env/.env.op schemas; Q does NOT edit `wb-bootstrap`'s gitignore/`.env.example` logic (that's shipped Phase-1 substrate). |

### READ-ONLY for ALL Phase 5 Captains

Shared substrate authored in this Captain-0 prep + earlier phases. **Do NOT modify** during Phase 5 Captain work — modifications surface as architectural concerns requiring General review:

- `scripts/README.md` (this file — the CLI + module-boundary contract)
- `skills-bundle/README.md` (the manifest-schema contract — Captain M authors `ui-ux-pro-max.md` per it)
- `scripts/install-skills.sh`, `scripts/wb-bootstrap.py`, `scripts/wb-bootstrap.sh` (Phase 1 substrate — O delegates to them; nobody rewrites them in Phase 5)
- `skills/wb-bootstrap/SKILL.md` + all other `skills/wb-*/` (Phase 1-2 substrate)
- `hooks/hooks.json` + `hooks-handlers/*.py` (Captain C Phase 1 + later; P's `autoclone_for_state` is *called by* `session_start.py` but P does not edit the hook — the hook→module wiring is documented here as the contract; the actual hook edit, if needed, is flagged as a follow-up, NOT Phase 5 Captain work — see note below)
- `phase-contracts/*.md` (38 contracts — except P's single phase-17 example per its write zone)
- All Phase 3 / Phase 4 substrate: `adapters/*`, `cms-adapters/*`, `commerce-adapters/*`, `i18n/*`, `handoff-spec/*`, their `tests/*/README.md` contracts
- `.gitignore` (Captain-0 reviews + extends it as part of this prep — see Deliverable 5; Phase 5 Captains do NOT edit it)
- `.claude-plugin/plugin.json` (manifest — `commands/` auto-discovers without a custom path; no manifest edit needed for Phase 5)

> **Hook-wiring interlock (behavioral, not a write collision):** P's `autoclone_for_state` is designed to be called by the SessionStart hook (`hooks-handlers/session_start.py`) and by phase-entry logic. In Phase 5, P ships the **callable module**; the actual edit to `session_start.py` to call it is a behavioral interlock that the General sequences (likely a small follow-up after O's integration merge, or folded into O's integration work if the General directs). Phase 5 Captains do NOT race-edit `session_start.py`. If P believes the hook edit is in-scope, P surfaces it to the General rather than editing the hook unilaterally.

### Worktree discipline (Decision 65 + 77 forward-doctrine)

Per decisions 65 (worktree isolation) + 77 (validated multi-Captain wave pattern): each Phase 5 Captain works in a per-callsign git worktree under `Projects/Jules.Solutions/Subprojects/website-builder.captain-{m,n,o,p,q}/` to avoid filesystem collisions on the read-only shared substrate. Worktree pattern per `.claude/rules/git-and-deploy.md`. **No-push-from-Captain rule** — Captains commit on their per-callsign branch (`phase-5-captain-{m,n,o,p,q}`) inside their worktree; the General does sequential merges + a single push at end of the Phase 5 wave.

**Merge order (locked per Decision 78d): M → N → P → Q → O.** O merges LAST because it is the integration point (its dispatcher imports P's and Q's modules — those must land first). This Captain-0 prep packet (`phase-5-captain-0-prep`) merges before any of M-Q.

---

## See also

- `Workstreams/website-builder/BUILD-strategy.md` Phase 5 (lines 209-230) — wave DoD + dispatch model
- `Workstreams/website-builder/foundation/DESIGN-architecture.md` — plugin layout (`commands/` per line 58-ish; CLI exposure)
- `Workstreams/website-builder/cross-cutting/DESIGN-resource-curation.md` — `wb library` CLI sketch + auto-clone triggers (Captain P)
- `Workstreams/website-builder/cross-cutting/DESIGN-secrets-and-keys.md` — keys.yaml/.env/.env.op + migrate flows (Captain Q)
- `Workstreams/website-builder/cross-cutting/DESIGN-skill-distribution.md` — install-skills.sh + `wb skills update/sync` (Captain O)
- `Workstreams/website-builder/extraction/DESIGN-extraction-stitch.md` — Stitch recipe (Captain N)
- `Workstreams/website-builder/skills/DESIGN-skill-uiuxpromax.md` — UI/UX Pro Max manifest source (Captain M)
- `skills-bundle/README.md` — sibling Captain-0 contract (manifest schema)
- `tests/README.md` § Phase 5 — where CLI / library / keys / skill-bundle / extraction tests land
- `scripts/wb-bootstrap.sh` + `scripts/install-skills.sh` — the cross-OS launcher + Python-resolution precedent the `wb` CLI follows
- `.claude/rules/modular-build-convention.md` — the atomic-unit discipline behind the O/P/Q module split
- STATE doc decisions 29 / 32 / 42 / 48 / 55 / 59 / 65 / 75 / 77 / 78 — `Workstreams/website-builder/website-builder.md`

## Provenance

Authored 2026-06-12 by Captain `wb-phase5-captain-0-prep-1` per the Phase 5 Captain-0 prep INST (BUILD-strategy Phase 5). Locks decision 78's O/P/Q ownership boundary + the M/N/O/P/Q write zones. OQ-1 resolved from the CC plugin spec (`plugin-dev:plugin-structure` skill) — option (b), no design-doc contradiction. Genre sibling of `cms-adapters/README.md` (Phase 4 Captain-0 prep).
