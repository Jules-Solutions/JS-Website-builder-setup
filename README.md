# website-builder

> A Claude Code plugin that turns Claude Code into a freelancer-shaped collaborator for building websites. Disciplined process, not a generator. Stack-agnostic.

## What this is

A Claude Code plugin that turns CC into a disciplined collaborator for building serious websites. The agent enforces multi-phase decomposition (brand → content → design system → components → pages → polish → deploy) and writes code in **your chosen stack**.

It is **not** a component library, template kit, or one-shot generator. It is a process — the discipline a senior freelancer brings to a project, encoded as Claude Code skills, hooks, and adapters.

## What it does

- **Picks you up wherever you are.** Greenfield, has-existing-site, has-AI-output, has-Framer-attempt, has-Figma-file — five entry modes covered.
- **Enforces phase order.** No jumping to components before the design system is locked. No writing code before the content is structured.
- **Re-runnable artifact ingestion.** Generated a new section in ChatGPT mid-project? Phase 6.5 ingests it back without restarting.
- **Stack-agnostic.** Pick your stack at phase 11 (Framer / Next.js / WordPress and more in v1; expansion to Webflow / Astro / Hugo / SvelteKit / static-html post-v1).
- **Writes real code** — once the design system is locked, the agent generates production-quality code in your chosen stack.
- **Hands off cleanly** — JSON handoff protocol lets you take a structured brief to ChatGPT, Claude.ai, v0, Cursor, or a human freelancer, and ingest the result back via phase 6.5.

## Status

**v0.1 (current — invite-only).** Plugin scaffold + agent profile + bootstrap skill landing in Phases 1-2 of the build. Sister's "Still Humans" Framer cosplay test in Phase 7; Ralph muggle test in Phase 8. Public release at Phase 9 (target: 6-14 weeks post-Phase-0).

**v1 ships with:** 3 stacks (Framer + Next.js + WordPress), 3 CMS options (none / Decap / Payload), Stripe Checkout commerce + Cal.com booking, UI/UX Pro Max design-skill flavor, Stitch extraction. The 8-stack / 9-CMS / 14-commerce / 6-skill / 4-extraction full surface ships in expansion phase 10 post-v1.

## Install

See `INSTALL.md` — git-clone + `claude --plugin-dir` for the v0.1 invite-only release; CC marketplace publish at Phase 9.

## Why this exists

Every existing AI website tool optimizes for the first 30 minutes. The first 30 minutes feel magical. Then iteration begins, and the codebase collapses into spaghetti the user can't read or fix.

This isn't a tooling problem — it's a **discipline problem**. Real freelancers build sites in phases. AI tools don't enforce that decomposition; they let muggles skip to the website. Three iteration cycles in, the project is dead.

The website-builder enforces the discipline a senior freelancer brings to a project. It refuses to skip steps. The output is durable code the user can read, modify, and extend — because the user participated in designing every primitive that went into it.

## Where the design lives

This repo is the codebase — the runtime plugin surface. Its authoring design SSOT (strategic positioning + the full design surface: 66 docs, 50+ architectural decisions, 10-phase build plan) lives vault-side in the `website-builder` workstream of the Jules.Life vault (not part of this distribution): VISION (positioning + anti-vision), STATE (daily log + decisions ledger), BUILD-strategy (10-phase plan), and the full `DESIGN-*` set (architecture, phase contracts, per-stack/CMS/commerce, skills, extraction, components, cross-cutting).

Inside this repo, the runtime realization of that design lives in `phase-contracts/`, `adapters/`, `cms-adapters/`, `commerce-adapters/`, `skills/`, `skills-bundle/`, `extraction/`, `component-libraries/`, and the curated `reference-corpus/ECOSYSTEM-CATALOG.md`.

## License

UNLICENSED — invite-only Phase 1-8 release. License will be set at Phase 9 public release.

## Contact

Jules.Solutions — https://jules.solutions
