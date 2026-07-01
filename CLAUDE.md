# website-builder — Subproject

> The Claude Code plugin codebase. Clone target for the `JS-Website-builder-setup` repo (private; on Jules-Solutions GitHub org).
> Status as of 2026-05-10: **repo exists empty on GitHub; not yet cloned here**. Phase 1 of `BUILD-strategy.md` clones the empty repo into this dir, scaffolds plugin layout, then pushes initial commit.
> Per locked decision 58 of the website-builder workstream: this subproject runs **parallel to platform**, NOT inside `platform/`.

## Identity

| | |
|---|---|
| **Type** | CC plugin (standalone — not a platform service) |
| **Purpose** | Turn Claude Code into a freelancer-shaped collaborator for muggles building websites — disciplined, refuses to skip steps, writes code in user's chosen stack |
| **Repo** | `Jules-Solutions/JS-Website-builder-setup` (private, empty) — clone here once Phase 1 begins |
| **Authoring home** | The `website-builder` workstream in the Jules.Life vault (authoring SSOT; not part of this distribution) — full design surface (66 docs) + STATE doc + BUILD strategy + daily log + decisions ledger |
| **Coverage** | `general-website-builder` — General-rank persistent owner, reports to Commander directly |
| **Distribution** | Invite-only via Jules's network until v1 functional milestone; public release after Phase 9 |

## Quick navigation (in-plugin homes)

The runtime plugin surface lives in this repo. Its authoring design SSOT lives vault-side in the `website-builder` workstream (Jules.Life vault; not part of this distribution). For work on the plugin itself, navigate the in-repo homes:

| Need | Where (in this repo) |
|---|---|
| The plugin's agent profile | `agents/website-builder.md` |
| Phase pipeline (contracts) | `phase-contracts/NN-name.md` |
| Per-stack adapters (MVP) | `adapters/stack-{framer,nextjs,wordpress}.md` |
| Per-CMS adapters (MVP) | `cms-adapters/cms-{none,decap,payload}.md` |
| Commerce + payment + booking | `commerce-adapters/` |
| Design-skill bundle manifests | `skills-bundle/` |
| Extraction tools | `extraction/` |
| Component libraries | `component-libraries/` |
| Ecosystem catalogue (the shipped menu) | `reference-corpus/ECOSYSTEM-CATALOG.md` |
| Bundled reference corpora | `reference-corpus/` |
| CLI + scripts | `scripts/` (see `scripts/README.md`) |
| `.website-builder/` user-side state layout | `state/README.md` |

Strategic positioning (VISION), the master build plan (BUILD-strategy), the decisions ledger, and the full `DESIGN-*` design surface remain vault-side in the `website-builder` workstream — they are the authoring SSOT, not shipped with the plugin.

## Why this isn't in `platform/`

The website-builder is a CC plugin distributed to end users — NOT a Jules.Solutions platform service. Per locked decision 58, this subproject lives parallel to platform to keep the missions cleanly separated:

- **Platform** = the 6-service backbone (jules-api, jules-auth, jules-dash, jules-local, jules-ops, jules-sandbox) consumed by Jules.Solutions clients + agents
- **Website-builder** = a CC plugin consumed by users in Jules's network → eventually public

The plugin DOES consume platform features when present (image-gen / video-audio gen / ask-jules-protocol). But per locked decision 56, v1 uses the consumer-fallback path (user provides their own keys) so the plugin can ship **before** the corresponding platform features are built. When platform-General eventually ships those features, wiring the plugin to consume platform endpoints is a small follow-up INST — NOT a v1 blocker.

## Repo workflow

When cloned (Phase 1), standard branch workflow per `.claude/rules/git-and-deploy.md`:

- `master` = production (no direct push; PRs only)
- `dev` = agent work (default branch for ongoing builds)
- PRs: `dev` → `master`

This dir is gitignored at the vault level (`.gitignore` rule `Projects/*/`) — the subproject has its own git history that's independent of the vault's. Vault tracks design + coordination (the `website-builder` workstream); the repo tracks plugin code (here).

## Coordination

| Surface | Who maintains |
|---|---|
| Workstream STATE doc | `general-website-builder` (post-spawn); operator-daily-driver-3 (pre-spawn) |
| BUILD-strategy.md | Operator authored; General reads at orient |
| Captain dispatches | General → Captains per phase per `BUILD-strategy.md` |
| This subproject's code | Captains during Phase 1+ build (write here, commit to JS-Website-builder-setup repo, push) |
| Cross-workstream coordination | General coordinates with platform-General via inbox when consumer-fallback paths need eventual wiring |

## Status as of 2026-05-10

- **Design phase**: ✓ Complete (vault-side, the `website-builder` workstream). 50 architectural decisions locked. 66 design docs across 8 organized subdirs.
- **Build strategy**: ✓ Complete. `BUILD-strategy.md` authored with full 10-phase sequence + DoD per phase.
- **Phase 0 (pre-flight)**: in progress. General profile + subproject dir created. CC plugin spec recon + manifest format decision + repo clone pending.
- **Phase 1+ (codebase build)**: not yet started. Begins when the General is spawned and dispatches Captain A (Plugin manifest + repo bootstrap) per `BUILD-strategy.md`.
- **Files in this dir as of now**: just this `CLAUDE.md` (orientation note). The actual repo clone happens in Phase 1.
