# Runbook — incident response

> Process for when something breaks on a live site — an outage, a broken deploy, or a leaked secret. Backs `wb-maintain-monitoring` (when a review surfaces a live problem) and the secret-compromise path from `DESIGN-secrets-and-keys.md`. Customized per project at deploy: provider + backup details come from `config.yaml`.

## Scope

- Site down / pages erroring in production.
- A deploy that broke the live site.
- A leaked or compromised API key/secret.

## Triage first

1. **Confirm the symptom by observation.** Walk the live site (Playwright at the real domain). Is it a full outage (all pages 5xx), a partial break (one route, one section), or a degraded integration (form/analytics dead)?
2. **Check the monitors.** Uptime status + recent error spike + last deploy time (`config.yaml` providers). A break right after a deploy points at the deploy.

## Outage / broken page

1. **If a recent deploy caused it** — the fastest fix is revert. Use the provider's rollback (Vercel: redeploy a previous deployment; Cloudflare Pages: roll back to a prior deployment; Netlify: publish a prior deploy; WP host: restore). Confirm the rollback restored the site live before declaring resolved — don't assert an untested escape hatch.
2. **If env-var drift caused it** (works local, dead in prod — the canonical post-launch incident) — a secret/env-var is missing or wrong-class in the host's production env. Push the correct production value (live key, not test) via the provider, redeploy, verify live.
3. **If a dependency/runtime caused it** — identify the change, fix or pin, verify, deploy. If the fix is bigger than maintenance, escalate.
4. **Verify recovery live.** Walk every affected page at the real domain. Resolved = verified-rendering, not "the deploy command succeeded."
5. **File the post-incident note** in `decisions/` — what broke, root cause, fix, prevention.

## Secret compromise (per DESIGN-secrets-and-keys.md)

If a key is exposed (committed by mistake, leaked, etc.):

1. **Alert immediately** — surface loudly; do not continue other work.
2. **Revoke** the exposed key at the provider.
3. **Generate** a new key.
4. **Update** `.env` (or the 1Password item) with the new key — per the project's secrets backend. Never paste the secret into chat, a commit message, a log, or any committed file.
5. **Push the new prod value** to the host's production env (provider CLI/API) and redeploy.
6. **Verify** the rotated key works in production; **verify** the old key is revoked.
7. **Audit git history.** If the exposed key is in git, recommend `git filter-repo` / BFG Repo-Cleaner with an explicit warning about history rewrite + force-push implications.

## Backup recovery (per config.yaml.backup)

Know what git does NOT cover before you need it: code → git + the host's deploy history; Layer-4 content → git; **a WordPress database + uploads, or a Payload Postgres DB, are NOT in the repo**. Recover the database from the CMS/DB-specific backup path recorded in `config.yaml.backup` — and verify the recovery path actually works rather than asserting an untested one.

## Failure modes

- **Asserting an untested rollback/backup** — always verify the recovery path live.
- **"Resolved" on a build-success, not a live walk** — resolved = verified-rendering.
- **Leaking the secret again during rotation** — never echo it; runtime injection only.
- **Assuming git is a database backup** — it isn't; CMS/DB has its own backup path.
