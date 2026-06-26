---
name: wb-maintain-content
description: This skill should be used by the website-maintainer when the user asks for a small content edit on an already-live site — "fix this typo", "update that stat", "this number is wrong", "refresh this link", "change the wording here", "update the copy on the about page", "the price changed", "swap this date". For edits to existing content (Layer 4 page MD or Layer 3 CDJSON strings) that do not add new pages/sections or touch the design system. NOT for adding new content (use wb-maintain-content-add), new sections (wb-maintain-section-add), or design changes (wb-maintain-iterate).
version: 0.1.0
---

# wb-maintain-content — small content edits

> The maintainer's most common task: a small edit to existing live content. Typically under 10 minutes. The discipline is light validation + brand-voice consistency + user-confirmed deploy — fast, but never careless.

## When invoked

The user wants to change words, numbers, or links in content that already exists. The change does NOT add a page or section, and does NOT touch design tokens or component code. If it does, route to the right skill: new content → `wb-maintain-content-add`; new section → `wb-maintain-section-add`; design tweak → `wb-maintain-iterate`.

## Behavior

1. **Locate the content.** Read the relevant `.website-builder/content/pages/{slug}.md` (Layer 4 prose) or `.website-builder/content/strings/{lang}.json` (Layer 3 CDJSON microcopy). Use `Grep` to find the exact string the user means; confirm with the user if more than one match.
2. **Make the edit** in place via `Edit`. For multi-language sites (`languages` in `config.yaml`), apply the edit across all language files per the project's translation preference (`config.yaml.translation_preference`): preference `1` = translate the edit inline; `2` = emit a translation brief for the changed string; `3` = ask each time. Never leave one language stale after an edit to another.
3. **Check against brand voice.** The phase-5 voice doc (`brand.yaml.voice`) still applies. A "small edit" that drifts into off-voice phrasing is not a small edit — surface it.
4. **Light validation.** Confirm: string references still resolve (no dangling CDJSON keys), frontmatter still parses, links are reachable (`WebFetch` a changed URL if external). Run the project's content-lint if one exists.
5. **Show the diff + ask to deploy.** Present the before/after to the user. Deploy only on explicit confirmation, via the project's provider (`deploy_provider` in `config.yaml`). Never autonomous.

## Time-box

Typically **under 10 minutes** for a single edit. If a "small edit" balloons (touches many files, implies a structural change), stop and re-scope — it's probably a different skill.

## Runbook

Full process: `runbooks/content-update.md`.

## Anti-patterns

- Editing one language file and leaving the others stale (multi-language drift).
- Deploying without showing the diff and getting confirmation.
- Letting a "typo fix" smuggle in a voice or design change — that's not this skill.
