---
name: wb-deploy
description: This skill should be used when the website-builder user reaches the deployment group — when they say "deploy my site", "put it live", "connect my domain", "set up DNS", "get a domain", "configure SSL", "make the site public", "publish to Vercel/Cloudflare/Netlify/Framer", "push it to production", "set up Google Analytics on the live site", "confirm analytics is firing on the live site", "analytics not tracking", "test analytics after deploy", "submit my sitemap", "add my site to Google Search Console / Bing", or when `project.yaml.current_phase` is 28, 29, or 30. Drives phases 28 (domain + DNS + SSL), 29 (hosting deployment + post-launch maintainer materialization), and 30 (analytics verification + search-console submission). Enforces real-domain-before-deploy, no-error live verification, local↔production secret parity, and proven-not-assumed analytics.
version: 0.1.0
---

# wb-deploy — Deployment Group (phases 28-30)

> The skill that ends the temp-URL era and makes the site genuinely live. Phase 28 gets the real domain pointing at real hosting with a real certificate. Phase 29 ships the site, pushes production secrets correctly, verifies every page renders, and materializes the post-launch maintainer. Phase 30 proves analytics fires on the live site and submits the sitemap to Google + Bing.
>
> This skill implements three phase contracts. **Read the contract for the active phase before acting** — the contracts are the substantive source of truth, this skill is the procedural spine:
> - `phase-contracts/28-domain-dns-ssl.md`
> - `phase-contracts/29-hosting-deployment.md`
> - `phase-contracts/30-analytics-search-submission.md`
>
> Design context: `DESIGN-deploy-providers.md` (the decision-50 provider rankings + cost reality), `DESIGN-secrets-and-keys.md` (registrar/DNS/host tokens — user-supplied at use, never persisted), `DESIGN-post-launch-template.md` (the phase-29 wizard + materialization), `DESIGN-architecture.md` § Skills (how phase-group skills layer on the freelancer agent).

## What this skill does

Carries the agent through the three-phase deployment group in strict order — 28 → 29 → 30 — each gated on its predecessor's audit artifact. The deployment group's defining discipline: **verified, not assumed.** DNS is done when `dig` observes it resolving, not when the API returned 200. SSL is done when a valid certificate is observed, not because "the host does it automatically." A deploy is done when every page is walked live and renders, not because the build succeeded. Analytics works when a real test pageview is observed arriving, not because the snippet is on the page.

The host is **not a free choice** — it is ranked by stack per locked decision 50 (see `references/deploy-provider-matrix.md`). The skill applies the ranking and surfaces realistic cost, but **never locks the user in**: an off-ranking choice is always available as an explicit, logged decision with the trade-off surfaced.

## When invoked

Trigger when the user enters the deployment group:

- `project.yaml.current_phase` is `28`, `29`, or `30` (the SessionStart hook surfaces this).
- The user asks to deploy, go live, connect a domain, get/configure a domain, set up DNS or SSL, publish to a host, push to production, set up live analytics, or submit a sitemap / add the site to a search console.
- A prior deployment-group phase completed and the pipeline advances to the next.

This skill **layers** on the always-loaded freelancer agent profile (per `DESIGN-architecture.md` § Skills) — it does not replace it. The anti-skip and tool-discipline rules in the agent profile still apply; this skill adds the deployment-specific procedure and gates.

## Phase routing

Determine the active phase from `project.yaml.current_phase`, read that phase's contract, then follow the matching procedure below.

### Phase 28 — Domain + DNS + SSL

**Read first:** `phase-contracts/28-domain-dns-ssl.md` (full), then `references/dns-ssl-verification.md` for the verification command patterns.

Entry gate: phase 27 complete, `audit/QA-REPORT.md` green. A broken site does not get a real address — verify the QA report is green before proceeding.

1. **Establish domain ownership.** Ask (via `AskUserQuestion`) whether the user already owns a domain (at which registrar) or needs one. Apply the registrar-selection logic from `references/deploy-provider-matrix.md` § Registrar selection. The domain must end up **in the user's own registrar account** — never registered under the agent's or a third party's control. This is non-overridable.
2. **Decide DNS-at-registrar vs DNS-at-host.** Surface the trade-off (registrar = more flexible; host = simpler). Cloudflare DNS is the recommended default when the user has no strong preference (native API, free, integrates with Cloudflare Pages from phase 29).
3. **Configure the DNS records** for the phase-29 hosting target. The record shape depends on the host — see `references/deploy-provider-matrix.md` § DNS records per host (Vercel A `76.76.21.21` + CNAME; Cloudflare Pages CNAME via Cloudflare DNS; Framer two A records `31.43.160.6` / `31.43.161.6` + `www` CNAME to `sites.framer.app`; WordPress host's A record; plus any host verification TXT). Use **Cloudflare MCP** when Cloudflare is the DNS provider (canonical-tool path); fall back to the registrar's API via `Bash` + `curl`. The registrar/DNS token is user-supplied at the moment of use via `AskUserQuestion` and **never persisted** (non-overridable, per `DESIGN-secrets-and-keys.md`).
4. **Verify propagation by observation.** Run the `dig` / DNS-over-HTTPS checks from `references/dns-ssl-verification.md` from multiple resolvers. Do **not** mark DNS done on an API 200 — mark it done when records *resolve to the right target*. Surface the realistic propagation window honestly (records minutes-to-hours; nameserver delegation up to 24-48h) and wait-and-verify rather than cutting the corner.
5. **Verify SSL by observation.** After DNS resolves, confirm a valid certificate via `openssl s_client` / `curl -vI` (correct issuer, not expired, SAN covers both apex and www, HTTPS enforced). If the cert does not issue, diagnose the cause (commonly a CAA record permitting only a different CA, or DNS not yet pointing right) and walk the fix — see `references/dns-ssl-verification.md` § CAA + DCV troubleshooting. Never ship an HTTP-only site.
6. **Confirm apex + www both resolve with a canonical redirect.** Both `example.com` and `www.example.com` must work, and one canonically redirects to the other (the user's choice, applied consistently — this must match the phase-26 canonical URL and the phase-30 Search Console property).
7. **Write `.website-builder/audit/DOMAIN-REPORT.md`** per the contract's schema (domain + registrar with ownership confirmed, DNS records, propagation evidence with timestamp, SSL evidence, canonical-redirect direction). Update `project.yaml.current_phase` to `29`.

Gating (refuse to advance): fake-deploy on a temp URL when the user has a real domain in mind (overridable only via an explicit logged `decisions/temp-url-launch.md` with migration cost surfaced); domain not owned by the user; DNS declared done without observed propagation; SSL assumed not verified; apex-or-www broken or no canonical redirect; registrar token persisted. Only the deliberate-temp-URL-launch case is overridable.

### Phase 29 — Hosting deployment

**Read first:** `phase-contracts/29-hosting-deployment.md` (full), then `references/deploy-provider-matrix.md` for the per-stack deploy mechanism and `references/dns-ssl-verification.md` is not needed here.

Entry gate: phase 28 complete, `audit/DOMAIN-REPORT.md` confirms the real domain is owned, DNS points at *this* host, SSL valid for apex+www. All prior audits green (QA/integrations/legal/SEO and, if transactional, the commerce audits). Deploy is **to the phase-28 domain**, never a temp URL.

1. **Pick the host by decision 50, not by habit.** Read `project.yaml.stack`; apply the ranking from `references/deploy-provider-matrix.md` § Decision-50 host ranking (Next.js → Vercel; static/Astro/Hugo/SvelteKit → Cloudflare Pages; fallback → Netlify; Framer → Framer Publish; WordPress → the chosen WP host). Surface the realistic cost so the muggle is not surprised (Vercel Hobby is non-commercial — a commercial site needs Pro ~$20/mo, etc.). An off-ranking host requires an explicit logged `decisions/off-ranking-host.md` with the limitation surfaced.
2. **Deploy via the host's real mechanism.** Git-integration auto-deploy on push to the production branch is the standard path; the host CLI (`vercel --prod`, `wrangler pages deploy`, `netlify deploy --prod`) is the direct path. Never a manual file copy. Use **Vercel MCP / Cloudflare MCP** first (canonical-tool path), fall back to the host CLI. Per-host commands + the current CLI surface are in `references/deploy-provider-matrix.md` § Deploy mechanism per host.
3. **Push production secrets correctly + run the parity check.** For every `keys.yaml` secret, set it in the *host's production env* with the production value (`sk_live_*`, not `sk_test_*`). Surface each secret's state loudly and explicitly via `AskUserQuestion` — live-key cutover is **always** an explicit, user-confirmed step, never silent (per `DESIGN-secrets-and-keys.md`). Then run the explicit local↔production parity pass: for every integration/commerce/analytics path, confirm the same behavior local and live. Any divergence is fixed *before* deploy is declared done — see `references/deploy-provider-matrix.md` § Secret parity per host for the per-host env-var push commands.
4. **Confirm build + migrations.** The production build must complete; for build-time data steps (e.g., a Payload-CMS Next.js site: `payload migrate && next build`), the migration runs as part of deploy so the schema is not drifted.
5. **Walk every page live.** Via `Playwright` MCP at the real `https://` domain: every page in `sitemap.yaml` returns 200 (no 4xx/5xx), every section renders (no silently-failed component), HTTPS works, the phase-25 consent banner gates cookies *in production*, the phase-24 integrations fire against production config, the phase-26 structured data is in the live server HTML. "Deployed" = verified-rendering, not build-succeeded.
6. **Materialize the post-launch maintainer.** Run the 7-section deploy wizard, then materialize the template — at this post-deploy-verify step (after step 5's live page-walk confirms the site renders). This is non-overridable — see `## The post-launch maintainer wizard (phase 29)` below for the full procedure. In short: ask the 7 wizard questions via `AskUserQuestion`, then invoke the materializer `${CLAUDE_PLUGIN_ROOT}/scripts/wb_postlaunch.py` (the non-interactive sibling of the wizard, via the `python3 || python || py` fallback — see Step B) with the answers — it writes `.website-builder/post-launch/config.yaml` and copies the chosen maintainer skills + the customized `website-maintainer.md` + the per-project runbooks into `.website-builder/post-launch/`. Do not skip the wizard.
7. **Write `.website-builder/audit/DEPLOY-REPORT.md`** per the contract schema (deploy URL, host + decision-50 rationale, build result, per-page live grid, production-secret-parity table, migration result, post-launch materialization confirmation). Update `project.yaml.current_phase` to `30`.

Gating (refuse to call deployed): any page 4xx/5xx or non-rendering section (non-overridable); local↔production parity failure (non-overridable); production secret missing or wrong class; build failed or migration skipped; off-ranking host without the explicit decision doc (only this is overridable); post-launch template not materialized.

#### The post-launch maintainer wizard (phase 29)

> The "killer template" install. Per locked decisions 28 / 37 / 45 / 49 + `DESIGN-post-launch-template.md`. Run this as part of phase 29 step 6 — declaring deploy done without it is a non-overridable gate violation ("post-launch template not materialized"). The wizard customizes the maintainer to *this* site; the materializer copies it into `.website-builder/post-launch/`.

**Read first:** `DESIGN-post-launch-template.md` § Wizard-driven customization + § Wizard config output. The provider option lists below are grounded but **drift** — re-verify current free-tiers/pricing via WebSearch at deploy time (decision 75) before surfacing them; never present stale pricing as fact.

**Step A — run the 7-section wizard via `AskUserQuestion`** (one section at a time; surface options, let the user pick or skip):

1. **Analytics** — `plausible` (privacy-friendly; flat-rate) / `ga4` (free; rich; needs consent banner + under-counts Safari via ITP) / `cloudflare-web-analytics` (free; cookie-free; basic only) / `fathom` (privacy-friendly; flat-rate) / `none` / `custom`. Captures provider + config URL + the API-key env-var name.
2. **Uptime monitoring** — `uptimerobot` (most generous free tier historically — *re-verify, the free monitor count has been in flux in 2026*) / `better-stack` (free tier + incident mgmt) / `cloudflare-health-checks` (with Cloudflare paid; integrates with the site's DNS) / `pingdom` (paid) / `none`. Captures provider + monitor id + the alert channel the user actually watches.
3. **Error tracking** — `sentry` (free tier ~5-7.5k events/mo; widely used) / `logrocket` (session replay) / `raygun` / `none` (the default for static no-JS sites; record it as a *considered decline with reason*, never a silent omission). Captures provider + DSN env-var name.
4. **CMS notification** (only if the site has a CMS) — watch for stale content, track CMS health, optionally pull CMS changes into git for backup. Captures cadence + stale-content threshold.
5. **Backup strategy** — per-component, stack-specific. Record what git covers (code, Layer-4 content) and — critically — what it does NOT (a WordPress database + uploads, a Payload Postgres DB are not in the repo). Captures code / content / cms / media / database backup paths.
6. **Iteration cadence** — `weekly` / `monthly` / `quarterly` / `adhoc`. Locks the maintainer's review cadence + next-review date.
7. **Maintenance language preference** (multi-language sites) — `1` auto-translate inline (default per decision 40) / `2` always emit a translation brief / `3` ask each time.

Also confirm the **skill subset** to install (default: all 8 — `wb-maintain-{content,monitoring,deps,content-add,section-add,page-add,iterate,escalate}`).

**Step B — materialize via the runner.** Collect the wizard answers into a JSON object (keys per `scripts/wb_postlaunch.py` `default_answers()` — `analytics_provider`, `uptime_provider`, `error_tracking_provider`, `cms_provider`, `backup_*`, `iteration_frequency`, `translation_preference`, `maintainer_skills_installed`, etc.), write it to a throwaway temp file (`$ANSWERS_JSON`), and invoke the materializer with the `python3 || python || py` interpreter fallback the plugin's hooks use (so it works on machines where only one interpreter name is on PATH):

```bash
# cwd = the user's project dir; $ANSWERS_JSON = path to the temp wizard-answers file.
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/wb_postlaunch.py" --answers "$ANSWERS_JSON" \
  || python "${CLAUDE_PLUGIN_ROOT}/scripts/wb_postlaunch.py" --answers "$ANSWERS_JSON" \
  || py "${CLAUDE_PLUGIN_ROOT}/scripts/wb_postlaunch.py" --answers "$ANSWERS_JSON"
# reads .website-builder/project.yaml for identity; writes .website-builder/post-launch/.
# Delete $ANSWERS_JSON afterwards — it is a throwaway, not project state.
```

The runner reads project identity (project / stack / deploy_provider / languages) from `project.yaml`, writes `.website-builder/post-launch/config.yaml` (placeholders resolved), and materializes the customized `website-maintainer.md` + the chosen skill subset + the runbooks + README into `.website-builder/post-launch/`. It is idempotent (re-runnable) and never touches user `content/` or `media/`.

**Step C — confirm + surface.** Verify `.website-builder/post-launch/config.yaml` + `.website-builder/post-launch/agents/website-maintainer.md` exist (no unresolved `{...}` placeholders). Surface the handoff to the user:

> *Your site is live, and I've installed your post-launch maintainer at `.website-builder/post-launch/`. When you want a small change — update content, add an essay, review analytics, check the site's health — invoke `/wb-maintain` (or run `wb maintain`). It knows your stack, brand, and integrations, and escalates back to me for anything bigger than maintenance.*

**Re-running the wizard later:** the user can re-run `scripts/wb_postlaunch.py` directly to re-materialize (e.g. after changing a provider). A future `wb maintain postlaunch` CLI verb would wrap this — currently the runner is invoked directly (the `wb` verb surface is locked; see the plugin's `scripts/README.md`).

### Phase 30 — Analytics + search-engine submission

**Read first:** `phase-contracts/30-analytics-search-submission.md` (full), then `references/analytics-and-search-console.md`.

Entry gate: phase 29 complete, `audit/DEPLOY-REPORT.md` confirms the site is live. **Phase 30 has no refusal gate** — it is operational confirmation, not a quality checkpoint. The site is already live. But "no gate" is not "no rigor."

1. **Read the analytics + consent context.** `audit/INTEGRATIONS-REPORT.md` (provider + snippet location; if "no analytics for now," the analytics half is a recorded no-op), `audit/LEGAL-REPORT.md` (consent-gated cookie-based vs cookieless — drives the test sequence).
2. **Prove analytics fires — do not assume.** Via `Playwright` MCP: load the live site; for cookie-based analytics, confirm it does *not* fire pre-consent, accept consent, fire a test pageview (a real navigation), then confirm the visit appears in the provider's real-time view (GA4 Realtime / Plausible live / Fathom live / Cloudflare Web Analytics). For cookieless analytics, the pageview registers regardless of consent. Procedure + provider real-time-view notes in `references/analytics-and-search-console.md` § Proving the pageview.
3. **Submit the sitemap to Google Search Console.** Verify the live domain as a GSC property (DNS TXT is the cleanest path — it ties to the phase-28 DNS the agent already controls). `curl` the live `sitemap.xml` first to confirm it is reachable + well-formed. Submit the **live canonical** sitemap URL (matching phase 28's apex/www decision — GSC does not follow redirects) and confirm status "Success" (or surface "Has errors"/"Couldn't fetch" with the diagnosis). Steps in `references/analytics-and-search-console.md` § GSC submission.
4. **Submit the sitemap to Bing Webmaster Tools.** The cheapest path is **Import from Google Search Console** (Settings → Import from Google Search Console — Bing auto-imports ownership verification *and* existing sitemaps within minutes). Otherwise verify via XML-file / meta-tag / CNAME and submit in the Sitemaps section. Confirm received. Steps in `references/analytics-and-search-console.md` § Bing submission.
5. **Record the honest measurement caveats.** GA4 (and cookie-based analytics generally) under-measures Safari/iOS because of Intelligent Tracking Prevention; consent-rejecters are lawfully not counted; cookieless tools (Plausible/Fathom) rotate visitor hashes daily so a returning visitor next day counts as new. Frame the numbers as a *floor, not a census* so the user does not later misread lawful under-counting as a dead site. Detail in `references/analytics-and-search-console.md` § Measurement caveats.
6. **Write `.website-builder/audit/POST-DEPLOY-REPORT.md`** per the contract schema. Update `project.yaml.current_phase` to `31` (phase 31 begins the post-launch group under `wb-postlaunch`).

Operational standards (not pipeline gates, but enforced): analytics is proven not assumed; the submitted sitemap is the live canonical one; if phase 30's test reveals cookie-based analytics firing pre-consent on production, surface it loudly as a phase-25 *statutory* regression and escalate (a live cookie-consent violation is serious) even though phase 30 itself does not gate.

## Recommended 3rd-party composables (surface, do not vendor)

These are composables the user MAY invoke via the `Skill` tool — recommend them at the relevant phase; do not bundle or embed them:

- **`cicd-automation:deployment-pipeline-design`** (loose composable) — recommend at phase 29 when the user wants a more elaborate multi-environment / staging-gate deploy pipeline than the host's default git-integration provides. The website-builder default is the host's native preview/production branch model (per `DESIGN-deploy-providers.md` § Multi-environment deploys); this composable is for users who want approval gates or a richer CD topology.
- **Cloudflare MCP / Vercel MCP** — if the user has these MCP servers configured locally, prefer them over the CLI for DNS (phase 28) and deploy + env-var push (phase 29) per the canonical-tool-first discipline. Surface this at phase 28: "If you have the Cloudflare MCP set up locally, the DNS work goes through it directly — otherwise the skill uses the Cloudflare API via curl." These are not bundled; the skill detects and uses them if present, else falls back.

## Additional resources

### Reference files

Load these as needed for the active phase:

- **`references/deploy-provider-matrix.md`** — the decision-50 host ranking, per-stack provider pairings, per-host deploy mechanism + CLI surface (current 2026-05-18 via context7), per-host secret-parity env-var push commands, DNS records per host, registrar selection logic, cost reality table.
- **`references/dns-ssl-verification.md`** — the phase-28 verification workhorse: `dig` / `whois` / DNS-over-HTTPS propagation patterns, `openssl s_client` / `curl -vI` SSL inspection, CAA + Domain-Control-Validation troubleshooting, the apex-vs-www + redirect-chain check, propagation-window honesty.
- **`references/analytics-and-search-console.md`** — phase-30: proving the test pageview (per provider real-time view, consent-sequencing), GSC property verification + sitemap submission, Bing import-from-GSC path + direct submission, the Safari/ITP + consent-rejection + hash-rotation measurement caveats with the floor-not-census framing.

External research backing these references was loaded fresh 2026-05-18 (context7 `/vercel/vercel` + `/cloudflare/wrangler-action`; WebSearch on DNS/SSL DCV patterns, GA4/Plausible/PostHog + Safari ITP, GSC/Bing sitemap submission, Framer Publish custom-domain DNS). Re-validate the host CLI + console UX at session start when a deployment phase is active — these surfaces evolve — and always verify by observation (`dig`/`openssl`/live page walk/observed pageview), never by assumption.
