---
phase: 29
name: Hosting deployment
group: deployment
pipeline_section: deployment
skill: wb-deploy
prev_phase: 28
next_phase: 30
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/cross-cutting/DESIGN-deploy-providers.md
  - Workstreams/website-builder/cross-cutting/DESIGN-secrets-and-keys.md
  - Workstreams/website-builder/cross-cutting/DESIGN-post-launch-template.md
---

# Phase 29 — Hosting deployment

> Ship the site. Deploy to the right host for the stack (Vercel for Next.js, Cloudflare Pages for static, Netlify fallback, Framer Publish for Framer, the WordPress host for WordPress), push production secrets correctly, and verify every page renders live with no 4xx/5xx. Also where the post-launch maintainer template is materialized via the deploy wizard. The site goes live here. The agent refuses to call it deployed if any page errors or a section does not render, and enforces local↔production parity rather than discovering env-var drift after launch.

## Mission

By phase 29 the site is built, verified across browsers, and has a real domain with DNS + SSL (phase 28). Phase 29 makes it *live*: the deploy to the chosen host, the production secrets pushed correctly (different from local — `sk_live_*` not `sk_test_*`), the build succeeding, and every page verified rendering at the real domain with HTTPS and no errors. This is the moment the site exists for the public. It is also where the **post-launch maintainer template is materialized** (per decision 49 + the deploy wizard) — phase 29 is the seam between "the website-builder built it" and "the maintainer keeps it running."

The host is not a free choice — it is ranked by stack per **locked decision 50**:

- **Vercel** — for the **Next.js** stack (canonical; native ISR/Server-Actions/Edge, zero-config preview deploys).
- **Cloudflare Pages** — for **static / Astro / Hugo / SvelteKit** stacks (generous free tier, unlimited bandwidth, global edge, integrated with Cloudflare DNS from phase 28).
- **Netlify** — the **fallback** when Vercel/Cloudflare Pages are not the right fit (good general-purpose host, mature adapters).
- **Framer Publish** — for the **Framer** stack (built-in; the only fully-supported Framer host).
- **WordPress host** — for the **WordPress** stack, per the user's choice (Kinsta / WP Engine / SiteGround / Cloudways / managed-WP).

The agent applies this ranking per `project.yaml.stack` and does not free-style the host. The full provider matrix + cost projections are in `DESIGN-deploy-providers.md`; the agent surfaces realistic costs (Vercel Hobby is non-commercial — a commercial site needs Pro at ~$20/mo; Cloudflare Pages free tier is genuinely viable for static; Framer/Webflow/WP-host carry their own monthly cost) so the muggle is not surprised by a bill.

Two defining disciplines. **No-error definition of deployed:** the site is not "deployed" if any page returns 4xx/5xx or a section silently fails to render — the agent walks every page live and confirms it before declaring deploy done. **Local↔production parity:** the env-var drift failure (the integration/commerce/analytics that worked locally because the secret was in local `.env` but was never set in the host's production env) is caught *here*, by an explicit parity check, not discovered by a user reporting "payments don't work in production." Phases 24/24b explicitly deferred the live-secret cutover to this phase; phase 29 closes it loudly and explicitly.

## Entry conditions

- Phase 28 (domain + DNS + SSL) complete. `audit/DOMAIN-REPORT.md` confirms the real domain is owned, DNS points at *this* host, SSL is valid for apex+www. Phase 29 deploys *to that domain*, not a temp URL.
- `.website-builder/project.yaml.stack` (phase 11) — drives the host per decision 50.
- `.website-builder/keys.yaml` — the secret registry. Every `source: env`/`source: onepassword` entry must end up set in the *host's production environment*, with production values (live keys), distinct from local `.env` test values (per `DESIGN-secrets-and-keys.md`). This is the parity input.
- All prior audits green: `audit/QA-REPORT.md` (27), `audit/INTEGRATIONS-REPORT.md` (24), `audit/LEGAL-REPORT.md` (25), `audit/SEO-REPORT.md` (26), and (if transactional) `commerce-config.yaml` + `payment-config.yaml` + `COMMERCE-LEGAL-REPORT.md` (24a/b/c) — including the deferred-to-phase-29 items those phases flagged (Stripe account activation for live mode; live-key cutover).
- The post-launch template source exists in the plugin's `post-launch/` directory (per `DESIGN-post-launch-template.md`) — phase 29 materializes it into `.website-builder/post-launch/`.

## What Claude must establish

The site live at the real domain, secret-parity-correct, every page verified, with the post-launch maintainer materialized. The work product:

1. **Deployed to the decision-50 host for the stack.** Next.js → Vercel; static/Astro/Hugo/SvelteKit → Cloudflare Pages; fallback → Netlify; Framer → Framer Publish; WordPress → the chosen WP host. Deploy via the host's canonical surface: git-integration auto-deploy on push to the production branch (the standard path — connect the repo, the host builds + deploys on push) or the host's CLI for a direct deploy where git-integration is not used. For Next.js on Vercel: `vercel` git-integration (or `vercel --prod` CLI), correct build command, the framework auto-detected. For Cloudflare Pages: git-integration via the dashboard, or `wrangler pages deploy` / C3, build config set. The agent uses the host's real mechanism, not a manual file copy.
2. **Production secrets pushed correctly.** Every `keys.yaml` secret set in the *host's* production env (Vercel: `vercel env add {KEY} production` / dashboard; Cloudflare: Pages env vars; Netlify: `netlify env:set`; WP host: `wp-config.php`/host env). Production values, not local test values — the agent surfaces each secret's state ("`STRIPE_SECRET_KEY` not set in Vercel; this must be the *live* key, different from your local test key — push from 1Password ref / paste once / you set it manually?") loudly and explicitly. The publishable key (not a secret) is pushed; live secret keys require explicit user confirmation per `DESIGN-secrets-and-keys.md`.
3. **Build succeeds + migrations run (where applicable).** The production build completes; for stacks with a build-time data step (e.g., a Payload-CMS Next.js site: `payload migrate && next build` in the build command — flagged at phase 12, enforced here), the migration runs as part of deploy so the schema is not drifted.
4. **Every page verified live.** The agent walks every page in `sitemap.yaml` at the real `https://` domain via Playwright: 200 (no 4xx/5xx), every section renders (no silently-failed component), HTTPS works, the consent banner gates cookies *in production* (the phase-25 network-level proof re-run against the live site), the integrations fire against production config (the phase-24 parity check, now truly against production), the structured data is in the live server HTML (phase 26).
5. **Local↔production parity check.** An explicit pass: for every integration/commerce/analytics path, the same behavior local and live. Any divergence (a key set locally but absent in prod env) is surfaced and fixed *before* deploy is declared done — not discovered post-launch.
6. **Post-launch maintainer materialized.** The deploy wizard (decision 49 / `DESIGN-post-launch-template.md`) runs: it asks the analytics / uptime / error-tracking / CMS-notification / backup / iteration-cadence / translation-preference questions, writes `.website-builder/post-launch/config.yaml`, copies the chosen maintainer skills + the customized `website-maintainer.md` + the per-project runbooks into `.website-builder/post-launch/`. The site now has its long-term maintainer installed, configured to *this* site's stack + provider + integrations.
7. **`.website-builder/audit/DEPLOY-REPORT.md`** — the deploy URL (real domain), the host (+ why, per decision 50), the build result, the per-page live-verification grid, the production-secret-parity result (each key: set-in-prod? value-class correct?), the migration result (if applicable), and the post-launch-template materialization confirmation.

The agent updates `.website-builder/project.yaml.current_phase` to `30` upon completion.

## Decision-50 host ranking (the host is not a free choice)

| Stack | Host (decision 50) | Deploy mechanism | Cost reality the agent surfaces |
|---|---|---|---|
| **Next.js** | **Vercel** (canonical) | git-integration (push → build → deploy) or `vercel --prod`; framework auto-detected; `vercel env add {KEY} production` for secrets | Hobby is non-commercial; a commercial site needs Pro ~$20/mo; Image Optimization + Edge Functions are usage-billed |
| **static / Astro / Hugo / SvelteKit** | **Cloudflare Pages** | git-integration (dashboard) or `wrangler pages deploy` / C3; build config set; same Cloudflare dashboard as phase-28 DNS | Free tier genuinely viable (unlimited bandwidth); SSR features (SvelteKit) need Workers Paid ~$5/mo |
| *(when Vercel/CF Pages are not the right fit)* | **Netlify** (fallback) | git-integration or `netlify deploy --prod`; mature adapters | Free Starter viable; Pro ~$19/mo; build-minutes + functions usage-billed |
| **Framer** | **Framer Publish** | Built-in publish (the only fully-supported Framer host — DNS pointed at Framer per phase 28) | Included in the paid Framer plan (~$5-25/mo) |
| **WordPress** | **the chosen WP host** | Per host (Kinsta/WP Engine/SiteGround/Cloudways) — git or host-native deploy; `wp-config.php` for secrets | Managed-WP ~$25-50/mo; the operational footprint is the user's |

The agent applies the row for `project.yaml.stack`. It does not deploy a Next.js site to Cloudflare Pages-without-the-adapter, or a static site to a Node host it does not need — the matrix from `DESIGN-deploy-providers.md` is the source of truth, and an off-ranking choice requires an explicit logged decision with the cost/limitation surfaced.

## Gating rules

The agent refuses to call the site deployed when:

- **Any page returns 4xx/5xx or a section does not render.** The defining gate. The agent walks every page live; a 404 on a real route, a 500 on a server-rendered page, a silently-empty section (a component that failed to render) means the site is *not deployed* — it is broken-and-online. **Not overridable** — a launched site with a dead page is the failure phase 29 exists to prevent.
- **Local↔production parity failure.** An integration/commerce/analytics path that works locally and not in production because a secret/env-var is set locally but absent (or wrong class — test key in prod) in the host's production env. The agent's explicit parity check catches this *before* declaring deploy done. **Not overridable** — env-var drift discovered by a user is the canonical post-launch incident this gate prevents.
- **Production secret missing or wrong class.** A required `keys.yaml` secret not set in the host's production env, or a `sk_test_*` where prod needs `sk_live_*`. The agent surfaces each secret's state explicitly and loudly; live-key cutover requires explicit user confirmation. Deploy is not done with a missing/test-class production secret.
- **Build failed or migration skipped.** The production build errored, or a Payload-class build-time migration did not run (schema drift). The agent does not declare a failed build deployed; it surfaces the error and fixes the cause.
- **Off-ranking host without explicit acceptance.** Deploying a stack to a host other than its decision-50 ranking (a Next.js site to Cloudflare Pages without the adapter, etc.) without a logged decision and the limitation surfaced. Overridable only with the explicit decision doc.
- **Post-launch template not materialized.** Phase 29 owns the maintainer-template install per decision 49. Declaring deploy done without running the wizard and materializing `.website-builder/post-launch/` leaves the site with no long-term maintainer — the agent does not skip the wizard.

Override is available only on the off-ranking-host case via an explicit logged decision. The no-error, parity, secret-class, build-success, and template-materialization gates are not overridable.

## Tools and skills used

- **Vercel MCP / Cloudflare MCP** (canonical-tool-first per the stack's host) — deploy, env-var push, domain attach, deployment inspection. Falls back to the host CLI.
- **`Bash`** — the host CLI (`vercel`, `wrangler`, `netlify`, WP-host CLI), the production-env-var push, the build invocation, the migration command where applicable.
- **`mcp__context7__resolve-library-id` + `mcp__context7__query-docs`** — **mandatory at this phase**: `/vercel/vercel` (current Vercel CLI deploy + git-integration + `vercel env add` surface) and `/cloudflare/wrangler` (current Cloudflare Pages deploy + git-integration + env-var surface). Cached to `.website-builder/library/docs/{vercel,cloudflare}.md`; cited.
- **`WebFetch`** — **mandatory at this phase**: framer.com publish docs for the Framer-stack deploy path (Framer Publish is built-in, not CLI — the agent confirms the current publish + custom-domain flow). Cited.
- **`Playwright` MCP** — the live-verification workhorse: walk every page at the real `https://` domain, confirm 200 + full render, re-run the phase-25 consent network-proof and phase-24 integration parity *against production*, confirm structured data in the live server HTML.
- **`AskUserQuestion`** — the production-secret cutover (live-key confirmation — explicit, never silent, per `DESIGN-secrets-and-keys.md`), the off-ranking-host acceptance if applicable, and the post-launch wizard questions (analytics/uptime/error-tracking/CMS/backup/cadence/translation).
- **`Read` / `Write`** — `keys.yaml` + every prior audit (the deploy preconditions), `project.yaml.stack` (the host ranking), `DESIGN-post-launch-template.md` (the wizard + materialization spec); writes the wizard answers to `.website-builder/post-launch/config.yaml` and copies the maintainer template in.

No subagent spawn. The `wb-deploy` phase-group skill carries phases 28-30; phase 29's live site is what phase 30 submits to the search consoles and what the materialized post-launch maintainer takes over.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/audit/DEPLOY-REPORT.md` | Deploy URL (real domain), host + decision-50 rationale, build result, per-page live-verification grid (200 + render + HTTPS), production-secret-parity table (per key: set-in-prod / value-class), migration result, post-launch-template materialization confirmation | The audit trail proving the site is genuinely live, error-free, parity-correct, and has its maintainer; read by phase 30 + the post-launch maintainer |
| The live site | At the real domain, HTTPS, every page 200 | The deployed product |
| `.website-builder/post-launch/` (materialized) | `config.yaml` (wizard answers) + chosen maintainer skills + customized `website-maintainer.md` + per-project runbooks | The long-term maintainer, configured to this site |
| Production env vars set at the host | Host-native | Live secrets in the host's production environment (values never in any committed file) |
| `.website-builder/decisions/off-ranking-host.md` *(when applicable)* | Standard decision-doc frontmatter + body | Created only when the user deployed to a non-decision-50 host with the limitation surfaced and accepted |

The `DEPLOY-REPORT.md` with the per-page live grid + the production-parity table is the required artifact.

## Common failure modes

**Env-var misconfiguration: works local, dead in production.** The single canonical post-launch incident. Stripe/analytics/the mailing list works in dev because the key is in local `.env`; production was never given the key (or got the test key) and the feature is silently dead live. Phases 24/24b deferred the live cutover here precisely so phase 29's explicit parity check catches it *before* the user does. The agent surfaces every secret's production state loudly and verifies the behavior live, not just that the build succeeded.

**"It deployed" = the build succeeded, nobody walked the pages.** The deploy command returned a URL and the agent called it done — but a route 404s, a server component 500s, or a section is silently empty because a data fetch failed in production. The agent's no-error gate is a *live walk of every page*, not the deploy command's exit code; deployed means verified-rendering, not build-succeeded.

**Deployed to a temp URL despite phase 28 configuring the real domain.** Phase 28 set up `example.com`; phase 29 deploys to `project.vercel.app` because the domain attach was skipped. The agent deploys to the *phase-28 domain* (the `DOMAIN-REPORT.md` domain) and verifies the live walk is against `https://example.com`, not the platform subdomain.

**Off-ranking host chosen by habit.** "I always use Netlify" for a Next.js site that decision 50 ranks to Vercel, losing native ISR/Server-Actions. The agent applies the decision-50 row for the stack and surfaces the trade-off; an off-ranking choice is the user's explicit logged decision with the limitation surfaced, not a silent habit.

**Payload migration not in the build command.** A Next.js + Payload site deploys with `next build` but no `payload migrate` — the schema drifts and the admin/API breaks in production. Flagged at phase 12, *enforced here*: the build command runs the migration; the agent does not declare deploy done with a skipped migration.

**Live secret keys pushed silently.** The agent flips `sk_test_*` to `sk_live_*` and pushes without explicit user confirmation. Per `DESIGN-secrets-and-keys.md`, live-key cutover is always an explicit, loud, user-confirmed step — never silent, never the same key both environments.

**Post-launch template skipped.** The deploy works and the agent moves on, never running the wizard — the site launches with no maintainer, and the user has no configured path for ongoing content/monitoring/deps. Phase 29 owns the materialization (decision 49); the agent runs the wizard and confirms `.website-builder/post-launch/` exists before declaring the phase done.

**Cookie consent / integrations verified only on the preview, not production.** Phase 24/25's parity checks were against a preview deploy; the *production* env differs and the live site drops cookies pre-consent or the integration is dead. Phase 29 re-runs the phase-25 consent network-proof and the phase-24 integration parity *against the live production site* — earlier verification on a preview is not verification of production.

## Reference materials

- **Design doc — deploy provider matrix + cost projections + decision-50 ranking (read in full):** `Workstreams/website-builder/cross-cutting/DESIGN-deploy-providers.md` § Per-stack provider pairings + § Provider deep dives + § Cost comparison summary + § Multi-environment deploys + § Phase contracts that invoke this concern (phase 29 = "deploy via chosen provider's CLI/API/MCP")
- **Design doc — secrets to production (the parity input):** `Workstreams/website-builder/cross-cutting/DESIGN-secrets-and-keys.md` § What lives in production env vs `.env` + § Phase contracts (phase 29 = "hosting provider deploy tokens; sync of secrets to production env")
- **Design doc — post-launch maintainer template + the phase-29 wizard (read for materialization):** `Workstreams/website-builder/cross-cutting/DESIGN-post-launch-template.md` § Wizard-driven customization (decision 45) + § Materialized location at deploy + § Phase 31-34 vs maintainer template (decision 37)
- **Design doc — phase pipeline source:** `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 29 (seed) + the MVP-scope decision-50 guardrail
- **Phase 28 (the domain phase 29 deploys onto):** `phase-contracts/28-domain-dns-ssl.md` § Output artifacts (the `DOMAIN-REPORT.md` domain)
- **Phase 24 / 24b / 25 / 26 (the deferred-to-29 items + the production re-verification):** `phase-contracts/24-integrations.md` (production parity), `phase-contracts/24b-payment-provider.md` (live-key cutover deferred here), `phase-contracts/25-legal-pages.md` (consent network-proof re-run on prod), `phase-contracts/26-seo-structured-data.md` (structured data in live server HTML)
- **External research (loaded fresh 2026-05-18 for this contract):**
  - context7 `/vercel/vercel` (1649 snippets, High reputation, benchmark 76.29) — `vercel deploy` / `vercel --prod`, git-integration, `vercel env add {KEY} production` (and `echo value | vercel env add`), framework auto-detection, `now-build`/build-command config; cached `.website-builder/library/docs/vercel.md`. Confirmed 2026-05-18.
  - Cloudflare Pages — https://developers.cloudflare.com/pages/get-started/ — C3 CLI, Direct Upload, Git integration (connect repo → auto-deploy on push); + `/cloudflare/wrangler` context7 for `wrangler pages deploy` + env vars. Confirmed 2026-05-18.
  - Framer Publish — framer.com publish docs (built-in publish, custom-domain attach) — confirmed current 2026-05-18.
- **Locked decision 50** (deploy ranking) + **decision 49** (post-launch 8-skill split, materialized via the phase-29 wizard) — STATE doc: `Workstreams/website-builder/website-builder.md`

Freshness date for this contract: **2026-05-18**. Host CLIs + git-integration surfaces evolve; the agent re-validates the Vercel/Cloudflare/Framer deploy surface via context7/WebFetch at session start when phase 29 is active and verifies the deploy by a *live walk of every page at the real domain*, never by the deploy command's exit code alone.
