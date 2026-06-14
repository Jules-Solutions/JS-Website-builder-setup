---
name: wb-maintain-deps
description: This skill should be used by the website-maintainer for dependency-update work on a live site — when the user says "update dependencies", "are my packages out of date", "apply security updates", "patch this vulnerability", "bump the deps", "npm audit", "is anything vulnerable", "update to the latest version of X", or when a configured update cadence is due or a security advisory lands. Categorizes outdated deps into security / minor / major, applies safely with regression checks, and escalates major breaking changes. Reads the stack from project state. NOT for adding new dependencies for new features (that is feature work — content-add / section-add / iterate).
version: 0.1.0
---

# wb-maintain-deps — dependency updates

> Keep the site's dependencies current without breaking it. The discipline is categorize-by-risk: security updates ship fast (after a verify run); minor updates ship with a regression check; major updates get read-the-release-notes and may escalate.

## When invoked

On the configured update cadence (typically monthly per `config.yaml.iteration_cadence`), immediately on a security advisory, or on demand. Read `config.yaml`/`project.yaml` for the stack — the tooling differs (npm/pnpm for Node stacks, pip/uv for Python, WordPress core+plugin+theme updates for WP, platform-managed for Framer/Webflow).

## Behavior

1. **List what's outdated.** Per stack: `npm outdated` / `pnpm outdated` (Node), `pip list --outdated` / `uv` (Python), WordPress update screen (WP). For Framer/Webflow, dependency updates are platform-managed — note that and focus on integration SDK versions if any.
2. **Categorize each outdated dep** into three buckets:
   - **Security** — a CVE / advisory applies. Apply ASAP.
   - **Minor** — patch/minor bump, low risk. Apply with a regression check.
   - **Major** — major-version bump, potential breaking changes. Requires attention.
3. **Security updates.** Surface the advisory, apply the fix, run the project's verify suite (build + tests + a Playwright smoke of the key flows), then deploy on user confirmation. Use `context7` to confirm the patched version's current API if the bump changes anything.
4. **Minor updates.** Surface them, recommend applying, walk the regression check (build + smoke). Deploy on confirmation.
5. **Major updates.** Surface them, recommend reading the release notes (`WebFetch` the changelog; `context7` for the new major's docs). If the breaking changes touch the design system or a core flow, **escalate** via `wb-maintain-escalate` — a framework major that rewrites component APIs is pipeline-scale work, not a maintenance bump.
6. **Always user-confirmed deploy.** Even a one-line security bump deploys only on explicit "yes". Never autonomous.

## Cadence

User-set in `config.yaml.iteration_cadence` — typically monthly. Security updates trigger immediately on advisory regardless of cadence.

## Runbook

Full process: `runbooks/dep-update.md`.

## Anti-patterns

- Bulk-bumping every dep at once (a failed build then has N suspects, not one).
- Applying a major version without reading the release notes.
- Treating a framework-major that rewrites component APIs as a maintenance task instead of escalating.
- Deploying a "harmless" bump without a regression check.
