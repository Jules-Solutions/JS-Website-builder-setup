# Runbook — weekly monitor review

> Process for the recurring uptime + error + deploy-log review on a live site. Backs `wb-maintain-monitoring`. Customized per project at deploy: the providers below come from `config.yaml`.

## Scope

The recurring "is the site healthy" check — uptime, error tracking, recent deploys. Typically weekly (per `config.yaml.iteration_cadence`).

## Preconditions

- Read `config.yaml`: `uptime.provider`, `error_tracking.provider`, `deploy_provider`, and the secret env-var names (resolved at runtime via the project's secrets backend — `.env` or 1Password; values never in state files).

## Steps

1. **Uptime.** Pull from `config.yaml.uptime.provider`:
   - **UptimeRobot** — API via `Bash` + `curl` (`getMonitors`). NOTE: UptimeRobot's free tier monitor count has been in flux (reports of 50→10 in 2026) — if monitor coverage looks reduced, surface it and recommend re-checking the plan or moving to Better Stack's free tier.
   - **Better Stack** — API; also surfaces incidents.
   - **Cloudflare Health Checks** — Cloudflare MCP (canonical-tool path; integrated with the project's DNS).
   - **Pingdom** — API.
   Report: current status, downtime in the period, response-time trend.
2. **Errors.** Pull from `config.yaml.error_tracking.provider` (Sentry / LogRocket / Raygun). Surface new error types, error-rate spikes, top offenders. If error tracking is `considered-and-declined` (static no-JS site), this is a deliberate no-op — say so.
3. **Deploy logs.** Recent build/deploy history from `deploy_provider`. Flag failed or slow deploys.
4. **Triage + file.** For each anomaly: assess severity, surface it plainly, file a follow-up (in-chat task or `decisions/` note). A site-down or revenue-affecting issue → `runbooks/incident-response.md`. A fix bigger than maintenance → `wb-maintain-escalate`.
5. **Summarize.** A short health summary to the user: status, anything actionable, anything filed.

## Alert-path sanity

Periodically confirm the monitor's alert actually reaches a channel the user watches (the wizard verified this at phase 34; re-verify if the user changed contact details). A monitor whose alert goes nowhere is no monitor.

## Failure modes

- **"All good" without pulling data** — review by observation, not assumption.
- **Alert path silently broken** — the monitor polls but nobody is notified. Re-verify the alert channel.
- **Absorbing an anomaly** — every anomaly gets surfaced + filed, never silently dropped.
