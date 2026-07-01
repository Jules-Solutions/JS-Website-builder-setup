# `post-launch/` — the maintainer template (plugin source)

> The "killer template" the website-builder installs into the user's project at deploy (phase 29). Per locked decisions 28 / 37 / 45 / 49 and `DESIGN-post-launch-template.md`.

This directory is **plugin source** — it ships with the website-builder plugin and is **not** itself the running maintainer. At phase 29 (deploy), the `wb-deploy` skill runs the 7-section customization wizard, then materializes a customized copy of this tree into the user's project at `.website-builder/post-launch/`. From then on, that materialized copy is the user's long-term site maintainer.

## What the template is

Once a site is live, the work changes shape. The discovery → build pipeline (phases 1-34) is a heavy one-shot. Ongoing maintenance — small content edits, monitoring review, dependency updates, the occasional new essay or section — is a different agent shape. This template is that shape: a **maintainer** that knows *this specific site* (its stack, brand, content layers, integrations, deploy provider), carries the design system forward as a constraint, makes small changes without re-running discovery, and **escalates back to the full website-builder pipeline** when scope grows beyond maintenance.

The clean separation (decision 37):

- **Phases 31-34** run **once** at launch (announce / roadmap / cadence / monitoring) — owned by the `wb-postlaunch` skill.
- **This maintainer template** takes over for **ongoing** maintenance — materialized at phase 29, lives with the project forever.

## Three-part structure

1. **Maintainer agent profile** — `agents/website-maintainer.md`. A template with deploy-time placeholders (`{project_name}` / `{chosen_stack}` / `{chosen_provider}` / `{languages}`) filled in by the wizard. Identity + behavior + authority + anti-authority.
2. **Maintenance skill bundle** — `skills/wb-maintain-*/` (8 skills, decision 49), one per maintenance concern. Each carries use + behavior + time-box.
3. **Runbooks + config** — `runbooks/*.md` (5 process docs) + `config-template.yaml` (customized at deploy into `config.yaml`).

## Layout

```
post-launch/
├── README.md                      # this file
├── agents/
│   └── website-maintainer.md      # the maintainer profile TEMPLATE (placeholders filled at deploy)
├── skills/
│   ├── wb-maintain-content/       # small content edits
│   ├── wb-maintain-monitoring/    # uptime / error / analytics review
│   ├── wb-maintain-deps/          # dependency updates (security / minor / major)
│   ├── wb-maintain-content-add/   # add new content (essay / post / case study)
│   ├── wb-maintain-section-add/   # add a section to an existing page
│   ├── wb-maintain-page-add/      # add a whole new page
│   ├── wb-maintain-iterate/       # medium iteration (design-system tweak)
│   └── wb-maintain-escalate/      # escalate to the full pipeline when scope grows
├── runbooks/
│   ├── content-update.md          # content-only update process
│   ├── dep-update.md              # how to evaluate + apply dep updates
│   ├── monitor-review.md          # weekly monitoring review
│   ├── analytics-review.md        # monthly analytics review
│   └── incident-response.md       # what to do when something breaks (incl. secret-compromise)
└── config-template.yaml           # the template config customized at deploy → config.yaml
```

## How it gets materialized (phase 29)

The `wb-deploy` skill (phase 29 section) drives this:

1. Run the 7-section wizard (analytics / uptime / error-tracking / CMS-notification / backup / iteration-cadence / maintenance-language) via `AskUserQuestion`.
2. Write `.website-builder/post-launch/config.yaml` from the wizard answers (schema = this dir's `config-template.yaml`, placeholders resolved).
3. Materialize the chosen skill subset + the customized `website-maintainer.md` + the per-project runbooks into `.website-builder/post-launch/`.

The materialization mechanism is the runner `scripts/wb_postlaunch.py` (the non-interactive sibling of the in-CC wizard, mirroring `scripts/wb-bootstrap.py`). The live agent runs the wizard interactively; the runner replays the same steps non-interactively for automation + tests.

## What this template does NOT do

- **Not autonomous deploys** — every deploy goes through user confirmation, even dep updates.
- **Not auto-content-creation** — the maintainer never generates content unprompted.
- **Not a replacement for the full builder** — anything beyond maintenance scope escalates (`wb-maintain-escalate`).
- **Not a multi-site manager** — one maintainer per site (one per `.website-builder/` dir).
- **Never installed if the site never deploys** — the template is gated behind a verified phase-29 deploy. No deploy = nothing to maintain = no maintainer. (Correct by design.)

## References

- Design: `DESIGN-post-launch-template.md`
- Phase 29 contract: `phase-contracts/29-hosting-deployment.md`
- Phases 31-34 (launch-once): `skills/wb-postlaunch/SKILL.md`
- Deploy providers (wizard provider input): `DESIGN-deploy-providers.md`
- Secrets + keys (provider keys for monitoring / analytics): `DESIGN-secrets-and-keys.md`
- i18n (translation-preference wizard section, decision 40): `DESIGN-i18n.md`
- Locked decisions 28 / 37 / 45 / 49 — STATE doc: `website-builder.md`
