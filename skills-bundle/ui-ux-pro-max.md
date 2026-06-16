---
type: SKILL_MANIFEST
skill_name: ui-ux-pro-max
upstream_id: ui-ux-pro-max@ui-ux-pro-max-skill
upstream_url: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
upstream_license: MIT
upstream_attribution: "UI/UX Pro Max by nextlevelbuilder (https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)"
install_method: skill-registry
install_target_path:
  windows: "%USERPROFILE%/.claude/skills/ui-ux-pro-max"
  macos: "$HOME/.claude/skills/ui-ux-pro-max"
  linux: "$HOME/.claude/skills/ui-ux-pro-max"
install_size_estimate_mb: 5
required_for_phases: [14, 17, 18, 22]
optional_complementary_with: [impeccable, emil-kowalski, taste, framer-motion, twenty-first-dev]
load_order: primary
default_loaded: false
---

# Skill — UI/UX Pro Max

> The default design-skill flavor in the website-builder bundle. Broad-coverage UI/UX design intelligence — 50+ styles, 161 color palettes, 57 font pairings, 161 product types, 99 UX guidelines, 25 chart types across 10 stacks. The plugin ships this composition manifest (the wiring layer), NOT a vendored copy of the skill; `scripts/install-skills.sh` fetches the real upstream from its canonical source at first-run per locked decision 32.
>
> Upstream state verified 2026-06-12: repo `nextlevelbuilder/ui-ux-pro-max-skill`, license MIT, latest release v2.5.0 (2026-03-10). Per the freshness discipline (decision 75), these values reflect the verified-at-author-time upstream — re-verify before any future manifest edit. The `install_size_estimate_mb: 5` frontmatter value is a best-known pre-install estimate (surfaced to the user before fetch), not a measured-against-v2.5.0 figure — refine it if a measured size becomes available.

## What it provides

A comprehensive design vocabulary the freelancer agent draws from at design-time:

- **50+ aesthetic styles** — glassmorphism, claymorphism, minimalism, brutalism, neumorphism, bento grid, dark mode, skeuomorphism, flat design, and responsive variants. Each carries token defaults (typography weighting, spacing, surface treatment, motion conventions).
- **161 color palettes** — pre-curated harmonies across hue families, saturation levels, and contrast tiers, each with semantic role mappings (primary / secondary / accent / surface / on-surface / muted / danger / warning / success).
- **57 font pairings** — display + body combinations vetted for legibility, character, and OS coverage; web-font sources noted, system-stack fallbacks specified.
- **161 product types** — site/app archetypes with canonical layouts and component patterns (SaaS landing, e-commerce storefront, dashboard, admin panel, blog, portfolio, agency, mobile app, marketing site, single-product launch, etc.). Each names typical sections, hierarchy patterns, and conversion-design cues.
- **99 UX guidelines** — accessibility (4.5:1 contrast, focus states, keyboard nav), touch/interaction (44×44px targets), performance (WebP/AVIF, lazy-loading, CLS < 0.1, virtualization), layout/responsive, typography/color rhythm, animation timing (150–300ms, reduced-motion), forms/feedback, navigation, charts/data.
- **25 chart types across 10 stacks** — bar, line, area, pie, radar, scatter, treemap, sankey, and the rest of the 25, for React, Next.js, Vue, Svelte, SwiftUI, React Native, Flutter, Tailwind, shadcn/ui, and HTML/CSS.
- **Action vocabulary** — plan, build, create, design, implement, review, fix, improve, optimize, enhance, refactor, check — verbs that map to design-phase work.
- **Component element library** — button, modal, navbar, sidebar, card, table, form, chart, with style-aware variants.
- **shadcn/ui MCP integration** — component search + live examples when the chosen stack uses shadcn primitives.

The agent reads this section at the `wb-bootstrap` flavor-pick dialogue to explain the flavor to the user.

## How the website-builder uses it

UI/UX Pro Max load-bears at four phases (the `required_for_phases` field: `[14, 17, 18, 22]`):

- **Phase 14 (wireframe per page) — secondary / reference.** Product-type lookup: the agent uses the 161 product types to surface canonical layout patterns matching the user's site (e.g., "this is a SaaS landing — typical layout is hero / proof / features / social-proof / pricing / footer").
- **Phase 17 (design system creation) — primary.** The load-bearing phase. When the user has picked UI/UX Pro Max as primary, this skill drives palette generation (3–5 options grounded in phase-2 vision + phase-5 voice), font-pair selection, spacing scale, motion tokens, and dark-mode strategy. The 161 palettes + 57 font pairings + 50+ styles surface as agent-curated options (narrowed to 3–5 — never the raw full set).
- **Phase 18 (component build) — secondary.** The agent consults the component element library (button / modal / navbar / sidebar / card / table / form / chart) with style-aware variants matched to the aesthetic chosen at phase 17.
- **Phase 22 (performance audit) — secondary / reference.** Consulted for chart-specific performance patterns (table virtualization, lazy-loading for chart libraries, font-loading strategy alignment).

`wb-bootstrap` surfaces the primary-load phase ("you'll work with this most at phase 17") when it explains the pick. The freelancer agent loads this skill at session-start when it is the picked default; phase-group skills layer on top as the user progresses.

## Composition rules

UI/UX Pro Max is the **broad-coverage default**. Composition follows the bundle's only-one-primary rule plus complementary layering:

- **(a) Primary vs complementary.** UI/UX Pro Max is a `primary` flavor (`load_order: primary`). It can be the active primary, or — when the user picks a different primary — it remains available as a broad reference; in practice v0.1 ships it as the sole flavor, so it is always the primary.
- **(b) Cannot co-primary with.** Only ONE primary design-skill is active at a time. UI/UX Pro Max MUST NOT be co-primary with **Impeccable** (their rule sets conflict — Impeccable's brand-vs-product split is a different primary stance). **Taste** is both-capable: it can be picked as primary *or* loaded as a complementary layer. It cannot be *co-primary* with UI/UX Pro Max (the user picks exactly one primary), but it can layer as complementary — see (c) and (d).
- **(c) Layers with (complementary).** The flavors in `optional_complementary_with` layer on top without conflict:
  - **+ Impeccable** — when loaded as a *complementary* lens (not co-primary), its brand-vs-product rule split layers on; UI/UX Pro Max provides the palette/font/style surface.
  - **+ Emil Kowalski** — animation + design-engineering lens layers on; UI/UX Pro Max provides static visual options, Emil provides motion taste + code patterns (used at phase 17 motion tokens + phase 18 animation-heavy components).
  - **+ Taste** — when complementary, Taste's flavor variants (taste / soft / minimalist / brutalist) override palette/font defaults on those axes; UI/UX Pro Max still provides style breadth + product types.
  - **+ Framer Motion** — animation-API companion on React stacks; UI/UX Pro Max provides the component element library, Framer Motion provides the animation patterns when coding those components.
  - **+ 21st.dev Magic** — agent-UX specialty (chat interfaces, prompt boxes, agent dashboards); composes with UI/UX Pro Max's general-purpose components when the user's site includes agent-driven features.
- **(d) Conflict-resolution default.** When two loaded skills disagree on the same axis, **the more-specialized loaded skill wins on its axis.** Example: with both UI/UX Pro Max and Taste loaded, Taste-soft wins palette decisions. UI/UX Pro Max retains authority over product-type / archetype recommendations, because the specialized flavors do not cover that axis.

> **Default-aesthetic note.** Because UI/UX Pro Max is the broad default, a site built with it as the *sole* skill can feel generic. The agent surfaces this at `wb-bootstrap` and recommends complementary flavor choices (available in expansion phase 10).

## Install

`install_method: skill-registry` — the Claude Code plugin-marketplace path. `scripts/install-skills.sh` reserves the install slot at `install_target_path` and the upstream skill content is fetched via Claude Code's plugin-install flow. The marketplace install (verified 2026-06-12) is two commands inside a Claude Code session:

```
/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
/plugin install ui-ux-pro-max@ui-ux-pro-max-skill
```

This installs the skill into the user-level CC skills directory so it is shared across the user's projects:

| OS | Install target |
|---|---|
| Windows | `%USERPROFILE%/.claude/skills/ui-ux-pro-max` |
| macOS | `$HOME/.claude/skills/ui-ux-pro-max` |
| Linux | `$HOME/.claude/skills/ui-ux-pro-max` |

`scripts/install-skills.sh` is the plugin's automation around this: invoked by `wb-bootstrap` (Step 5) as `bash "${CLAUDE_PLUGIN_ROOT}/scripts/install-skills.sh" --primary ui-ux-pro-max`, it detects the OS, resolves the target path above, and records the install in `.website-builder/skills-installed.yaml`. The script's `KNOWN_SKILLS` registry row for this flavor carries upstream method `registry` (the script's spelling of this manifest's `install_method: skill-registry`), the install ref `ui-ux-pro-max@ui-ux-pro-max-skill` (matching this manifest's `upstream_id`), and the marketplace source `nextlevelbuilder/ui-ux-pro-max-skill` — so the stub it writes emits the correct `/plugin marketplace add` + `/plugin install` pair (reconciled 2026-06-16, Decision 90). The `@` form is the **install** id; the `Skill`-tool **invoke** id is the `plugin:skill` form `ui-ux-pro-max:ui-ux-pro-max`.

> **Windows prerequisite.** `scripts/install-skills.sh` runs under bash. On Windows it needs Git Bash (ships with [Git for Windows](https://git-scm.com/download/win)) or WSL — there is no native PowerShell/cmd path in v0.1 (per the cross-platform precedent in `wb-bootstrap` Step 5). The two `/plugin` commands above run inside a Claude Code session and are OS-agnostic.

## Verification

Confirm the install one of two ways:

- **Static path check (no session restart needed):**

  ```bash
  test -f "$HOME/.claude/skills/ui-ux-pro-max/SKILL.md" && echo "installed" || echo "missing"
  ```

  On Windows under Git Bash, `$HOME` resolves to the user profile, so the same command works; if it doesn't, substitute `"$(cygpath "$USERPROFILE")/.claude/skills/ui-ux-pro-max/SKILL.md"`.

- **Fresh-session skill-load probe:** start a new Claude Code session in the user's project and confirm the `ui-ux-pro-max` skill appears in the available-skills list. If `install-skills.sh` reserved a stub (`version: 0.0.0-pending` in the stub SKILL.md), the upstream content has not yet been fetched — complete the `/plugin install` step above, then re-run `scripts/install-skills.sh` to replace the stub.

A successful install also writes a `ui-ux-pro-max` entry under `skills:` in `.website-builder/skills-installed.yaml` (`role`, `upstream_ref`, `install_path`, `install_method`, `fetched_at`) — `wb skills sync` reads this to re-create the install on a fresh machine.

## Uninstall

Symmetric to install — remove the install dir and deregister:

1. Delete the install dir:

   ```bash
   rm -rf "$HOME/.claude/skills/ui-ux-pro-max"
   ```

   (Windows Git Bash: `$HOME` resolves to the user profile, so the same command works; if not, `rm -rf "$(cygpath "$USERPROFILE")/.claude/skills/ui-ux-pro-max"`.)

2. Remove the `ui-ux-pro-max` entry from the `skills:` list in `.website-builder/skills-installed.yaml` so `wb skills sync` does not re-install it.

If the skill was installed via the CC plugin marketplace, it can also be removed with `/plugin uninstall ui-ux-pro-max@ui-ux-pro-max-skill` inside a CC session. Removing the skill only affects the user-level CC skills dir; the user's project content under `.website-builder/` is untouched.

## Upstream attribution

This skill is authored by **nextlevelbuilder**. Source: <https://github.com/nextlevelbuilder/ui-ux-pro-max-skill>. License: **MIT**. Latest release at cataloguing: **v2.5.0** (2026-03-10).

The website-builder plugin **orchestrates; nextlevelbuilder authors.** Per locked decision 32 (hybrid distribution), the plugin ships this composition manifest — the wiring layer describing how the skill composes with the website-builder pipeline — and never a vendored copy of the skill content. The user installs the real upstream skill from nextlevelbuilder's own distribution (the CC plugin marketplace), which preserves the author's attribution, gives the user the latest version, and avoids any redistribution-licensing concern. Please support the upstream project.

<!-- BUILD-TIME NOTE (not end-user-facing) — registry-id reconciliation: RESOLVED 2026-06-16 (Decision 90).
Ground truth re-verified against the upstream repo manifests + the canonical CC plugin docs (code.claude.com):
  - marketplace.json `name`/`id` = `ui-ux-pro-max-skill`; plugin.json `name` = `ui-ux-pro-max`, declared skill dir
    `./.claude/skills/ui-ux-pro-max` (skill name `ui-ux-pro-max`).
  - INSTALL id (for `/plugin install`) = `<plugin>@<marketplace>` = `ui-ux-pro-max@ui-ux-pro-max-skill`,
    preceded by `/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill`.
  - INVOKE id (for the `Skill` tool) = `<plugin>:<skill>` = `ui-ux-pro-max:ui-ux-pro-max`.
These are two DIFFERENT ids by design; an earlier pass (the build-audit F2 + decision 80) treated the `:` form as a
stale duplicate of the `@` form — they are not duplicates. Reconciled both surfaces:
  - install-skills.sh KNOWN_SKILLS now carries the `@` INSTALL id + a `marketplace_source` field
    (`nextlevelbuilder/ui-ux-pro-max-skill`) and emits the correct `/plugin marketplace add` + `/plugin install` pair.
  - the user-facing `Skill`-tool recommendation lines (wb-component-build, wb-design-system) use the `:` INVOKE id.
Remaining: DESIGN-skill-distribution.md still references the older `:` form in an install context — back-propagate
under INST-B (design-doc sync); non-gating. -->

