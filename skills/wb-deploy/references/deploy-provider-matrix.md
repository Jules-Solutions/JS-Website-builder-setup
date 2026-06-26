# Deploy Provider Matrix — decision 50, per-stack hosts, deploy mechanisms, secret parity, DNS records

> Reference for phases 28 + 29. The substantive source of truth is `Workstreams/website-builder/cross-cutting/DESIGN-deploy-providers.md` (read it in full for phase 29) and locked decision 50 in `Workstreams/website-builder/website-builder.md`. This file is the procedural condensation the skill loads on demand.
>
> External CLI surface confirmed fresh 2026-05-18 via context7 `/vercel/vercel` and `/cloudflare/wrangler-action`, and WebSearch on Framer Publish custom-domain DNS. Host CLIs evolve — re-validate at session start when phase 29 is active.

## Decision-50 host ranking (the host is not a free choice)

Per locked decision 50: defaults per stack, surfaced but never locking the user in — an explicit override is always available via a logged decision doc.

| Stack | Host (decision 50) | Why | Cost reality the agent surfaces |
|---|---|---|---|
| **Next.js** | **Vercel** (canonical) | Native ISR / Server Actions / Edge with zero config; per-branch preview deploys | Hobby is **non-commercial**; a commercial site needs Pro **~$20/mo per seat**; Image Optimization billed per source image; Edge Functions billed per request × duration |
| **static / Astro / Hugo / SvelteKit** | **Cloudflare Pages** | Generous free tier (unlimited bandwidth, egress free); global edge; same dashboard as phase-28 Cloudflare DNS | Free tier genuinely viable for static/SSG; SvelteKit SSR needs Workers Paid **~$5/mo**; Image Resizing is paid; build minutes billed beyond free quota |
| *(when Vercel / CF Pages are not the right fit)* | **Netlify** (fallback) | Good general-purpose host; mature adapters; drag-and-drop muggle UX | Starter free viable; Pro **~$19/mo per seat**; build minutes + Functions usage-billed |
| **Framer** | **Framer Publish** | Built-in; the only fully-supported Framer host | Included in the paid Framer plan **~$5-25/mo** |
| **WordPress** | **the chosen WP host** | Per the user's pick (Kinsta / WP Engine / SiteGround / Cloudways / managed-WP) | Managed-WP **~$25-50/mo**; the operational footprint is the user's |

Apply the row for `project.yaml.stack`. Do not deploy a Next.js site to Cloudflare-Pages-without-the-adapter, or a static site to a Node host it does not need. An off-ranking choice requires an explicit logged `.website-builder/decisions/off-ranking-host.md` with the cost/limitation surfaced and accepted. "I always use Netlify" for a Next.js site is the canonical off-ranking-by-habit failure — surface the lost native ISR/Server-Actions and require the explicit decision.

## Deploy mechanism per host (current 2026-05-18)

Git-integration auto-deploy on push to the production branch is the standard path; the host CLI is the direct path. Never a manual file copy. Use the host MCP first (Vercel MCP / Cloudflare MCP) per the canonical-tool-first discipline, fall back to the CLI.

### Vercel (Next.js)

Confirmed via context7 `/vercel/vercel` 2026-05-18 (Vercel CLI 53.x):

```bash
npm i -g vercel          # install
vercel login
vercel link              # link the local project to a Vercel project (vercel link --repo for monorepo)
vercel deploy            # preview deployment (default)
vercel --prod            # production deployment
vercel deploy --prebuilt # deploy a locally-built project (vercel build first)
vercel deploy --yes --token $VERCEL_TOKEN   # CI / non-interactive
```

`vercel deploy` auto-detects the framework and reads `vercel.json`. The standard muggle path is **git-integration**: connect the repo in the Vercel dashboard (or `vercel git connect`), and a push to the production branch builds + deploys automatically — `vercel --prod` from the CLI is the direct alternative. Custom domain attach: `vercel domains add example.com` (or the dashboard), then point DNS per the DNS-records section below.

### Cloudflare Pages (static / Astro / Hugo / SvelteKit)

Confirmed via context7 `/cloudflare/wrangler-action` 2026-05-18 (Wrangler 3.81+ / v4):

```bash
npm i -g wrangler
wrangler login
wrangler pages project list
wrangler pages deploy ./dist --project-name=my-site            # direct deploy of a built dir
wrangler pages deploy ./dist --project-name=my-site --branch=main
```

The standard muggle path is **git-integration**: in the Cloudflare dashboard, connect the repo to a Pages project with the build command + output dir set — push to the production branch auto-deploys; non-production branches deploy as previews. C3 (`npm create cloudflare`) scaffolds a new project with the deploy wired. `wrangler pages deploy` is the direct CLI path for CI or non-git deploys.

### Netlify (fallback)

```bash
npm i -g netlify-cli
netlify login
netlify deploy            # draft/preview deploy
netlify deploy --prod     # production deploy
```

Git-integration via the Netlify dashboard (connect repo, set build command + publish dir) is the standard path; `netlify deploy --prod` is the direct CLI path. No official MCP; the CLI is the canonical surface.

### Framer Publish (Framer)

Built-in publish from the Framer editor — there is no CLI. Confirmed via WebSearch 2026-05-18 (Framer Help, current improved hosting): publish from the editor, then attach the custom domain in the project's domain settings, then point DNS at Framer (records in the DNS-records section). Framer auto-provisions + renews SSL once DNS resolves. The agent confirms the current publish + custom-domain flow via WebFetch of framer.com publish docs at session start (mandatory per the phase-29 contract).

### WordPress host (WordPress)

Per the chosen host (Kinsta / WP Engine / SiteGround / Cloudways) — git deploy or host-native deploy; secrets in `wp-config.php` / the host's env. The operational story is the user's; the agent follows the host's documented deploy path.

## Secret parity per host (the phase-29 parity input)

Every `keys.yaml` secret with `source: env` / `source: onepassword` must be set in the **host's production environment**, with the production value (live keys, not test keys). Surface each secret's state loudly via `AskUserQuestion`; live-key cutover is always explicit + user-confirmed (per `DESIGN-secrets-and-keys.md`). Per-host push:

| Host | Push a production env var |
|---|---|
| **Vercel** | `vercel env add KEY production` (or `echo "$value" \| vercel env add KEY production`), or the dashboard. Confirmed via context7 `/vercel/vercel` 2026-05-18. |
| **Cloudflare Pages** | Pages project → Settings → Environment variables (Production), or `wrangler pages secret put KEY --project-name=my-site` for secrets. |
| **Netlify** | `netlify env:set KEY "$value"` or the dashboard (scope to production). |
| **Framer** | Framer does not run user server secrets the way a Node host does; client-only keys (e.g. a publishable analytics ID) are set in the Framer site settings. Server-side secrets are not a Framer pattern. |
| **WordPress host** | `wp-config.php` or the host's env-var mechanism per the host. |

The parity check (step 3 of phase 29): for every integration/commerce/analytics path, the same behavior local and live. A key set locally in `.env` but absent (or test-class) in the host's production env is the **single canonical post-launch incident** — caught here by the explicit parity pass + the live page walk, not discovered by the user.

## DNS records per host (the phase-28 record shape)

The records phase 28 sets depend on where phase 29 will deploy. Confirmed via WebSearch 2026-05-18 (Cloudflare SSL/TLS DCV docs, Vercel domains troubleshooting, Framer Help).

| Host | Apex (`example.com`) | `www` | Notes |
|---|---|---|---|
| **Vercel** | `A` → `76.76.21.21` | `CNAME` → `cname.vercel-dns.com` | Or use Vercel-managed nameservers (required for wildcard, which forces DNS-01). Add `CAA 0 issue "letsencrypt.org"` if other CAA records exist (Vercel uses Let's Encrypt). |
| **Cloudflare Pages** | `CNAME`/flattened → the Pages project domain, in **Cloudflare DNS** (same dashboard as the DNS-provider work) | `CNAME` → the Pages project domain | Full setup (Cloudflare runs the authoritative nameservers) → Cloudflare handles SSL DCV automatically via a TXT record. |
| **Netlify** | `A`/`ALIAS` per Netlify's current apex guidance | `CNAME` → the Netlify subdomain | Netlify DNS or external; Netlify auto-provisions Let's Encrypt. |
| **Framer** | two `A` records → `31.43.160.6` and `31.43.161.6` | `CNAME` → `sites.framer.app` | **No `AAAA` records** (they block Framer's SSL issuance). If DNS is on Cloudflare, set proxy to **DNS-only (gray cloud)** — Framer provides its own SSL+CDN; proxied creates a redirect loop. Framer auto-provisions + renews SSL once DNS resolves. |
| **WordPress host** | `A` → the host's IP | `CNAME` → the host's domain | Per the host; many provide managed nameservers instead. |

Plus any host-required verification `TXT` record. Always confirm by observation (`dig`) that the records resolve to the right target before marking DNS done — see `dns-ssl-verification.md`.

## Registrar selection logic (phase 28)

From `DESIGN-deploy-providers.md` § Domain registrar selection logic:

```
IF the user already owns the domain at a registrar
  → use the existing registrar; read the API-token reference from keys.yaml
ELSE IF the user wants Cloudflare hosting + Cloudflare DNS already set up
  → recommend Cloudflare Registrar (at-cost, no markup, free WHOIS privacy, integrated)
ELSE IF the user needs a .ch or other strict ccTLD
  → recommend a registrar that supports it (Gandi often; switch.ch for .ch)
ELSE
  → recommend Cloudflare Registrar (default) or Namecheap (alternative)
```

The domain ends up **owned by the user, in the user's own registrar account** — never under the agent's or a third party's control. Non-overridable. Registrar API surface: Cloudflare (full API + official MCP), Namecheap (REST, IP-whitelist), Porkbun (REST), Gandi (LiveDNS REST), GoDaddy (REST). Tokens are user-supplied at the moment of use and never persisted.

## Cost reality summary (surface at phase 28/29 so the muggle is not surprised)

For a typical muggle site (5-15 pages, low-medium traffic, no heavy backend):

| Provider | Free tier viable? | First-year monthly | Note |
|---|---|---|---|
| Cloudflare Pages | YES | $0 | Most cost-effective for static/SSG |
| GitHub Pages | YES | $0 | Free for public repos; static-only; no official commercial use |
| Vercel Hobby | YES (non-commercial) | $0 | Commercial → Pro $20/mo |
| Netlify Starter | YES | $0 | Build-minute + bandwidth soft limits |
| Vercel Pro | NO | $20/mo | Most common muggle commercial choice |
| Netlify Pro | NO | $19/mo | Alternative |
| Framer Hosting | NO | $5-25/mo | When chosen for Framer |
| WordPress.com Business | NO | $25/mo | When chosen for WP |
| WP Engine / Kinsta | NO | $25-50/mo | Premium managed WP |

Plus the domain: ~$10-15/yr at Cloudflare Registrar / Namecheap / Porkbun (at-cost) vs marked-up elsewhere (GoDaddy can be high after year one — the agent surfaces transfer-out if the user is overpaying).
