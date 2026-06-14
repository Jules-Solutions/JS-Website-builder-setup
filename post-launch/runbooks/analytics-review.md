# Runbook — monthly analytics review

> Process for the recurring analytics review on a live site. Backs `wb-maintain-monitoring` (analytics half). Customized per project at deploy: the provider comes from `config.yaml.analytics`.

## Scope

The recurring traffic + engagement review — typically monthly (per `config.yaml.iteration_cadence`). Surfaces trends; frames numbers honestly.

## Preconditions

- Read `config.yaml.analytics.provider` + `config.yaml.analytics.config_url` + the API-key env-var name (resolved at runtime via the secrets backend; never stored in state).

## Steps

1. **Pull the data** from `config.yaml.analytics.provider`:
   - **Plausible** — Stats API (privacy-friendly; EU-hosted; no cookie banner needed).
   - **GA4** — Data API / dashboard (free; richer; under-counts Safari/iOS via ITP; needs consent banner in EU).
   - **Cloudflare Web Analytics** — Cloudflare dashboard / API (free, cookie-free; basic pageviews/visitors only — a sanity-check supplement, no conversion goals).
   - **Fathom** — API (privacy-friendly; flat-rate; 3-year retention).
   - **None** — recorded no-op; this review is skipped.
2. **Report the trend.** Traffic over the period vs prior; top pages; top sources/referrers; the conversion signal tied to the site's phase-3 conversion outcome (the *one* thing the site is for).
3. **Frame numbers honestly — floor, not census.** Restate the measurement caveats so a lawful under-count isn't misread as a dead site:
   - Privacy-friendly tools (Plausible / Fathom) rotate visitor hashes daily — a returning next-day visitor counts as new.
   - GA4 (cookie-based) under-measures Safari/iOS via Intelligent Tracking Prevention.
   - Consent-rejecters are lawfully not counted.
   - Small-site GA4 reports can be threshold-filtered/sampled.
4. **Tie to the roadmap.** Connect signal to the v1.1 roadmap (`roadmap.md`) — a page with traffic but no conversion is an `iterate` candidate; a high-intent source is a content-add candidate. File follow-ups; route bigger moves to the relevant maintainer skill.

## Failure modes

- **Reading a lawful under-count as failure** — always restate the floor-not-census framing.
- **Reporting raw numbers with no trend / no tie to conversion** — the number alone isn't a finding.
- **Treating Cloudflare Web Analytics as a full analytics tool** — it's a basic sanity check; no conversion goals.
