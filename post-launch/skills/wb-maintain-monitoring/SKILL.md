---
name: wb-maintain-monitoring
description: This skill should be used by the website-maintainer for the recurring health review of a live site — when the user says "review my monitoring", "do the weekly check", "is the site up", "check uptime", "any errors", "review the analytics", "how's the site doing", "did anything break this week", or when a configured cadence is due. Pulls uptime status, error-tracking events, and recent deploy logs; surfaces anomalies; files follow-ups. Reads providers from the project's post-launch config. NOT for setting up monitoring (that was the phase-29 wizard + phase 34) — this reviews already-configured monitors.
version: 0.1.0
---

# wb-maintain-monitoring — health + analytics review

> The recurring "is the site healthy" review. Uptime + error tracking + analytics + deploy logs, on the cadence the wizard set. Surfaces anomalies and files actionable follow-ups; it does not silently absorb a problem.

## When invoked

On the configured cadence (`config.yaml.iteration_cadence.frequency`, typically weekly for the operational check) or on demand. The providers were chosen at the phase-29 wizard and live in `config.yaml` (`analytics`, `uptime`, `error_tracking`). This skill *reads* them — it does not reconfigure them (re-config is `wb maintain reconfig`).

## Behavior

1. **Read the config.** `config.yaml` tells you which providers are wired and the secret env-var names (resolved at runtime via the project's secrets backend — `.env` or 1Password; values never stored in state files).
2. **Pull uptime.** From the configured monitor (`config.yaml.uptime.provider` — e.g. UptimeRobot / Better Stack / Cloudflare Health Checks / Pingdom). Use the provider API via `Bash` + `curl`, or the Cloudflare MCP when the monitor is Cloudflare Health Checks. Report current status + any downtime in the period + response-time trend.
3. **Pull error tracking.** From `config.yaml.error_tracking.provider` (e.g. Sentry / LogRocket / Raygun). Surface new error types, error-rate spikes, and the top offenders. If error tracking is recorded as `considered-and-declined` (a static no-JS site), note that this step is a deliberate no-op.
4. **Pull deploy logs.** Recent build/deploy history from the hosting provider (`deploy_provider`). Flag failed or slow deploys.
5. **Review analytics** (per the monthly cadence, or when asked). Pull from `config.yaml.analytics.provider` (Plausible / GA4 / Cloudflare Web Analytics / Fathom). Surface traffic trend, top pages, top sources. Restate the measurement caveats honestly so the user reads numbers as a floor, not a census: privacy-friendly tools rotate visitor hashes daily; GA4 under-counts Safari/iOS via ITP; consent-rejecters are lawfully uncounted. A flat or low number is not necessarily a dead site.
6. **Surface + file follow-ups.** For anything actionable (uptime drops, error spikes, slow deploys, a broken integration), surface it plainly and file a maintenance follow-up (in-chat task, or `.website-builder/decisions/` note). If a fix is bigger than maintenance, route to `wb-maintain-escalate`.

## Cadence

User-set in `config.yaml.iteration_cadence` — typically weekly for uptime/errors, monthly for analytics. Runs on demand any time.

## Runbooks

Weekly process: `runbooks/monitor-review.md`. Monthly analytics process: `runbooks/analytics-review.md`. When something is actually down: `runbooks/incident-response.md`.

## Anti-patterns

- Reporting "all good" without actually pulling the data (review is by observation, not assumption).
- Reading a lawful analytics under-count as a dead site.
- Absorbing an anomaly silently instead of surfacing + filing it.
