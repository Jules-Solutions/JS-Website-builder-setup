# Skill-bundle composition manifests — canonical schema

> Every design-skill composition manifest at `skills-bundle/<name>.md` MUST follow the frontmatter schema + body-section outline below. The `wb-bootstrap` skill (flavor pick + install) and the `wb skills update/sync` CLI verbs read these manifests by field name at runtime — schema divergence is silent skill-orchestration failure.
>
> This README is the **Phase 5 Captain-0 prep contract** for the skill bundle. It is the sibling of `scripts/README.md` (the `wb` CLI + module-boundary contract). Genre reference: `cms-adapters/README.md` (Phase 4 Captain-0 prep — schema contract + per-section guidance + write zones).
>
> **v0.1 ships ONE manifest: `ui-ux-pro-max.md` (Captain M).** Per locked decision 55, only the UI/UX Pro Max flavor ships in v0.1; the other five flavors (Impeccable / Emil Kowalski / Taste / Framer Motion / 21st.dev Magic) are Phase 10 expansion and follow this same schema when authored.
>
> **Anchors:** `Workstreams/website-builder/cross-cutting/DESIGN-skill-distribution.md` (the canonical manifest-schema authority — § "Composition manifest schema" lines 96-154), `Workstreams/website-builder/skills/DESIGN-skill-uiuxpromax.md` (Captain M's per-skill source), `Workstreams/website-builder/foundation/DESIGN-architecture.md` § "Skill bundle" (line 283), `Workstreams/website-builder/BUILD-strategy.md` Phase 5 (lines 209-230), STATE doc decisions 32 / 33 / 55 / 59 / 65 / 77 / 78.

---

## What a composition manifest IS (and is NOT)

Per locked decision 32 (hybrid skill distribution): the plugin ships **lightweight composition manifests**, NOT the skills themselves. Each manifest is the plugin's wiring layer telling the agent how to *use* an upstream skill once installed; the upstream author ships the actual skill content from their canonical source, fetched at first-run by `scripts/install-skills.sh`.

A manifest **IS**:
- The orchestration contract: which phases load this skill, at what priority, how it composes with sibling flavors.
- The install recipe pointer: where the upstream lives, how it installs, where it lands per-OS, attribution.
- The conflict-resolution rules: which flavors are mutually-exclusive primaries, which layer as complementary.

A manifest is **NOT**:
- A vendored copy of the skill (licensing + version-drift + attribution reasons per `DESIGN-skill-distribution.md` § "Why we don't redistribute").
- A skill itself (manifests live in `skills-bundle/`, not `skills/`; CC does NOT auto-discover them as skills — they're read by `wb-bootstrap` + the `wb skills` verbs).

## Why exact field names matter

Two load-bearing reasons (mirrors the `cms-adapters/README.md` § "Why exact section names matter" rationale):

1. **Runtime field lookups.** `wb-bootstrap` (flavor pick + install) reads `default_loaded`, `install_method`, `install_target_path`, `required_for_phases`, and `optional_complementary_with` by exact key to drive the pick dialogue + the install-skills.sh invocation. `wb skills update`/`sync` (Captain O's verbs delegating to `install-skills.sh`) read `skill_name`, `upstream_id`/`upstream_url`, and `install_method` to fetch + replace + verify. A renamed or missing field = the orchestration reads stale/absent data; the user can't easily diagnose.
2. **Cross-flavor composition.** When Phase 10 adds the other five flavors, `wb-bootstrap` enforces "only one primary at a time" + "complementary skills layer" by reading `load_order` + `optional_complementary_with` across all loaded manifests. The fields must be identical across manifests for the composition engine to compare them side-by-side.

---

## Canonical frontmatter schema (per `DESIGN-skill-distribution.md` lines 100-117)

Every `skills-bundle/<name>.md` MUST carry all of these frontmatter fields. Field names + value shapes are the contract; Captain M (and Phase 10 flavor Captains) fill in per-skill values.

```yaml
---
type: SKILL_MANIFEST                      # literal — lets wb-bootstrap / wb skills identify manifest files
skill_name: ui-ux-pro-max                 # canonical short id (kebab-case); matches the install dir basename
upstream_id: ui-ux-pro-max:ui-ux-pro-max  # registry/marketplace id when install_method is skill-registry; else "" 
upstream_url: https://...                 # canonical upstream source (registry URL, GitHub repo, or website)
upstream_license: MIT                     # the upstream's license (MIT / Apache-2.0 / proprietary-free / etc.)
upstream_attribution: "UI/UX Pro Max by {Author}"   # human attribution string surfaced at install + in body
install_method: skill-registry            # one of: skill-registry | git-clone | curl | platform-specific
install_target_path:                      # per-OS install destination (user-level CC skills dir)
  windows: "%USERPROFILE%/.claude/skills/{skill-id}"
  macos: "$HOME/.claude/skills/{skill-id}"
  linux: "$HOME/.claude/skills/{skill-id}"
install_size_estimate_mb: 5               # integer/float — surfaced before install so the user knows the cost
required_for_phases: [17, 18]             # phase numbers where this skill load-bears (UI/UX Pro Max: 14, 17, 18, 22)
optional_complementary_with: [emil-kowalski, taste, framer-motion]   # flavors that layer (NOT conflict) with this one
load_order: primary                       # one of: primary | secondary  (primary = drives; secondary = layers/refs)
default_loaded: false                     # bool — only loaded when the user PICKS this flavor (keeps context budget lean)
---
```

### Field semantics + value-shape rules

| Field | Type | Rule |
|---|---|---|
| `type` | literal | Always `SKILL_MANIFEST`. Lets lint + `wb-bootstrap` distinguish manifests from skill `SKILL.md` files. |
| `skill_name` | string (kebab-case) | Canonical short id. MUST equal the manifest filename basename (`ui-ux-pro-max.md` → `ui-ux-pro-max`) AND the install dir basename. |
| `upstream_id` | string | Registry/marketplace id (`ui-ux-pro-max:ui-ux-pro-max`) when `install_method: skill-registry`. Empty string `""` for non-registry installs. |
| `upstream_url` | URL | The canonical upstream source. Re-verify at author time (do not copy a stale URL — same freshness discipline as Decision 75 for context7 IDs). |
| `upstream_license` | string | The upstream's actual license. If unknown/ambiguous, write `unverified` and flag in body — do NOT guess (licensing is why we don't redistribute). |
| `upstream_attribution` | string | Human-readable credit, surfaced at install + in the body's `## Upstream attribution` section. |
| `install_method` | enum | `skill-registry` (CC marketplace path) / `git-clone` / `curl` / `platform-specific` (per-skill recipe in body). |
| `install_target_path` | map (3 OS keys) | All three of `windows` / `macos` / `linux`. Default = user-level CC skills dir (`~/.claude/skills/{skill-id}`) so the flavor is shared across the user's projects (per `DESIGN-skill-distribution.md` § "Per-OS install paths"). |
| `install_size_estimate_mb` | number | Best-known estimate; surfaced before install so muggles know what they're fetching. |
| `required_for_phases` | list[int] | Phase numbers where this skill is load-bearing. Drives auto-mention in `wb-bootstrap` + context-budget decisions. |
| `optional_complementary_with` | list[string] | Other `skill_name`s that LAYER with this one. Mutually-exclusive primaries are NOT listed here (they're documented in the body's `## Composition rules`). |
| `load_order` | enum | `primary` (drives the design decisions when picked) / `secondary` (layers on / reference lookup). |
| `default_loaded` | bool | `false` for all design flavors — they load ONLY when the user picks them (context-budget; per `DESIGN-skill-distribution.md` § "Pickability vs auto-load"). |

> **Schema-discrepancy note for Captain M (read this).** `DESIGN-skill-uiuxpromax.md` (lines 44-62) sketches an *older, lighter* manifest frontmatter (`skill_id`, `upstream_source`, `local_install_path`, `load_when`, `load_priority`, `required`, `composes_with`). The **canonical schema is the one above**, from `DESIGN-skill-distribution.md` (the doc whose entire purpose is the manifest schema). Where the two docs disagree, follow `DESIGN-skill-distribution.md`. The older fields map onto the canonical ones as: `skill_id`→`skill_name`, `upstream_source`→`upstream_id`/`upstream_url`, `local_install_path`→`install_target_path`, `load_when`→`required_for_phases`, `load_priority`→`load_order`, `required`→(drop; `default_loaded: false` covers pickability), `composes_with`→`optional_complementary_with`. Captain M authors the canonical schema; the per-skill *content* (capabilities, phase-load semantics, conflict rules) comes from `DESIGN-skill-uiuxpromax.md`.

---

## Body-section outline (per `DESIGN-skill-distribution.md` lines 119-154)

After the frontmatter, the manifest body MUST contain these H2 sections, in this order. Section names are the contract (the same runtime-lookup rationale as `cms-adapters/README.md`). Captain M fills each per UI/UX Pro Max; Phase 10 flavor Captains follow the same outline.

| # | Section | Purpose |
|---|---|---|
| 1 | `## What it provides` | Brief capability description — what the skill brings (UI/UX Pro Max: 50+ styles, 161 palettes, 57 font pairings, 161 product types, 99 UX guidelines, 25 chart types). Source: `DESIGN-skill-uiuxpromax.md` § "What it provides". |
| 2 | `## How the website-builder uses it` | Per-phase usage — which phases load it as primary vs secondary + what it drives in each. UI/UX Pro Max: phase 17 (primary, palette/type/spacing), phase 18 (secondary, component patterns), phase 14 (product-type lookup), phase 22 (chart-perf patterns). |
| 3 | `## Composition rules` | The mutually-exclusive-primary rules + complementary-layering rules + conflict-resolution default (more-specialized skill wins on its axis). UI/UX Pro Max is the broad-coverage default; others narrow/specialize. Source: `DESIGN-skill-uiuxpromax.md` § "Composition with other bundle members". |
| 4 | `## Install` | The per-platform install command(s) matching `install_method` + `install_target_path`. For UI/UX Pro Max (`skill-registry`): the registry install invocation that `scripts/install-skills.sh` runs. Must be consistent with the install-skills.sh block. |
| 5 | `## Verification` | How to confirm the install worked — skill loads in a fresh CC session, or a static path check at `install_target_path`. |
| 6 | `## Uninstall` | How to remove cleanly (delete the install dir; deregister from `.website-builder/skills-installed.yaml`). |
| 7 | `## Upstream attribution` | The full attribution + license + "we orchestrate; they author; please support upstream" note. Source field: `upstream_attribution`. |

Adding flavor-specific H3 subsections within any H2 is allowed. Adding new trailing H2 sections (8, 9, …) for flavor-specific concerns is allowed (the schema is the floor, not the ceiling — same convention as `cms-adapters/README.md`).

### Per-section guidance

**`## What it provides`** — concrete, not marketing. Enumerate the actual surface the agent draws from (counts + categories). The agent reads this at the bootstrap pick dialogue to explain the flavor to the user.

**`## How the website-builder uses it`** — map `required_for_phases` to concrete behavior per phase. This is what `wb-bootstrap` surfaces when it explains "you'll work with this most at phase 17." Distinguish primary-load phases from secondary-reference phases.

**`## Composition rules`** — the load-bearing section for the future multi-flavor composition engine. MUST state: (a) is this a primary or can it be complementary; (b) which flavors it CANNOT co-primary with; (c) which it layers with; (d) the conflict-resolution default when two loaded skills disagree on the same axis. For UI/UX Pro Max: "broad-coverage default; only-one-primary; the more-specialized loaded skill wins on its axis; UI/UX Pro Max keeps authority over product-type/archetype recs."

**`## Install`** — the command(s) `scripts/install-skills.sh` executes for this skill, consistent with `install_method`. For `skill-registry`: the registry install path. For `git-clone`: the `git clone <upstream_url> <install_target_path>` form. Keep it copy-paste-runnable and cross-OS (the install-skills.sh handles OS-path resolution; the manifest documents the per-method command).

**`## Verification`** — a concrete check, not "it should work." Static path check (`test -d "$install_target_path"`) or fresh-session skill-load probe.

**`## Uninstall`** — symmetric to install. Delete the install dir + remove the `skills-installed.yaml` entry.

**`## Upstream attribution`** — author + source URL + license + the support-upstream note. This is the licensing-compliance surface (we orchestrate; they author).

---

## Skill installation provenance — `.website-builder/skills-installed.yaml`

Not part of THIS manifest schema, but the manifest's downstream consumer. After `scripts/install-skills.sh` installs a picked flavor, it records the install in the user project's `.website-builder/skills-installed.yaml` (schema in `DESIGN-skill-distribution.md` lines 326-349: `name`, `role`, `upstream_id`/`upstream_url`, `version`, `install_path`, `install_method`, `fetched_from`, `fetched_at`). `wb skills sync` (Captain O verb) reads this on a fresh machine to re-create the install set. Captain M does NOT author `skills-installed.yaml` (it's runtime output, written by `install-skills.sh`); M's manifest is the *input* that drives what gets recorded.

---

## Per-Captain write zone — Phase 5 skill-bundle work

| Captain | Concern | Exclusive write paths |
|---|---|---|
| **M** | UI/UX Pro Max composition manifest | `skills-bundle/ui-ux-pro-max.md` (the manifest — per this schema + `DESIGN-skill-uiuxpromax.md` content) + `tests/skills-bundle/ui-ux-pro-max/` (manifest-validation fixture, if M adds one per `tests/README.md` § Phase 5). **Per decision 55, ONLY the UI/UX Pro Max manifest ships in v0.1** — M does NOT author the other five flavor manifests (Impeccable / Emil Kowalski / Taste / Framer Motion / 21st.dev — Phase 10). |

### READ-ONLY for Captain M (and all Phase 5 Captains)

Per the shared-substrate discipline (same as `scripts/README.md` § "READ-ONLY for ALL Phase 5 Captains" — the authoritative list lives there):

- `skills-bundle/README.md` (this file — the manifest-schema contract)
- `scripts/README.md` (the `wb` CLI + module-boundary contract — sibling Captain-0 prep)
- `scripts/install-skills.sh` (Phase-1 substrate, 16 KB — M's manifest's `## Install` section must be *consistent with* it; M does NOT rewrite install-skills.sh. If M's manifest implies an install-skills.sh change, M surfaces it to the General — does not edit the script.)
- `skills/wb-bootstrap/SKILL.md` + all `skills/wb-*/` (Phase 1-2 substrate — the bootstrap reads M's manifest; M does not edit the bootstrap)
- `.gitignore` (Captain-0 reviews/extends as part of this prep per Decision 77; Phase 5 Captains do NOT edit it)
- `.claude-plugin/plugin.json` (manifest — `skills-bundle/` is NOT a CC auto-discovery dir, so no plugin.json change needed; manifests are read by wb-bootstrap, not CC's skill loader)

M's manifest may *reference* (cross-link to) any read-only anchor; it may not edit it.

> **install-skills.sh consistency interlock (behavioral, not a write collision):** M's `ui-ux-pro-max.md` `## Install` section documents the install command for UI/UX Pro Max; `scripts/install-skills.sh` (Phase-1) is the script that runs it. These must agree on the registry id + install path. In Phase 5, M ships the manifest; if the existing `install-skills.sh` doesn't already handle the UI/UX Pro Max install correctly, that's a behavioral interlock the General sequences (likely folded into integration, or a small follow-up) — M does NOT race-edit `install-skills.sh`. M surfaces the gap to the General.

### Worktree discipline (Decision 65 + 77 forward-doctrine)

Per decisions 65 (worktree isolation) + 77 (validated multi-Captain wave pattern): each Phase 5 Captain works in a per-callsign git worktree under `Projects/Jules.Solutions/Subprojects/website-builder.captain-{m,n,o,p,q}/`. Worktree pattern per `.claude/rules/git-and-deploy.md`. **No-push-from-Captain rule** — Captains commit on their per-callsign branch (`phase-5-captain-{m,n,o,p,q}`) inside their worktree; the General does sequential merges + a single push at end of the wave. **Merge order M → N → P → Q → O** (per Decision 78d; O merges last as the integration point). This Captain-0 prep packet (`phase-5-captain-0-prep`) merges before any of M-Q.

---

## See also

- `Workstreams/website-builder/cross-cutting/DESIGN-skill-distribution.md` — the canonical manifest-schema authority (frontmatter + body + install-skills.sh)
- `Workstreams/website-builder/skills/DESIGN-skill-uiuxpromax.md` — Captain M's per-skill content source
- `Workstreams/website-builder/foundation/DESIGN-architecture.md` § "Skill bundle" (line 283) — bundle's place in the plugin
- `Workstreams/website-builder/foundation/DESIGN-ecosystem-catalog.md` § "Design-skill flavor bundle" — the 6-flavor catalogue
- `scripts/README.md` — sibling Captain-0 contract (`wb` CLI + module boundary; the authoritative READ-ONLY list)
- `tests/README.md` § Phase 5 — where the `tests/skills-bundle/` manifest-validation fixture lands
- `scripts/install-skills.sh` — the Phase-1 cross-OS install script M's `## Install` section must stay consistent with
- `.claude/rules/modular-build-convention.md` — single-responsibility discipline
- STATE doc decisions 32 / 33 / 55 / 59 / 65 / 77 / 78 — `Workstreams/website-builder/website-builder.md`
- Phase 10 (later) — the other five flavor manifests (Impeccable / Emil Kowalski / Taste / Framer Motion / 21st.dev Magic) follow this same schema

## Provenance

Authored 2026-06-12 by Captain `wb-phase5-captain-0-prep-1` per the Phase 5 Captain-0 prep INST (BUILD-strategy Phase 5). Canonical manifest schema sourced from `DESIGN-skill-distribution.md` (authoritative over the older sketch in `DESIGN-skill-uiuxpromax.md` — discrepancy documented above for Captain M). v0.1 ships UI/UX Pro Max only per decision 55. Sibling of `scripts/README.md` (the `wb` CLI Captain-0 prep contract).
