---
phase: 28
name: Domain + DNS + SSL
group: deployment
pipeline_section: deployment
skill: wb-deploy
prev_phase: 27
next_phase: 29
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/cross-cutting/DESIGN-deploy-providers.md
  - Workstreams/website-builder/cross-cutting/DESIGN-secrets-and-keys.md
---

# Phase 28 — Domain + DNS + SSL

> Get the real domain pointing at the real hosting with a real certificate. Acquire the domain if the user does not own it, configure DNS, verify SSL, confirm both `www` and apex resolve. The phase that ends the temp-URL era. First phase of the deployment group. The agent refuses to fake-deploy on a throwaway `*.vercel.app` URL when the user has a real domain in mind, and surfaces propagation wait-time honestly rather than cutting corners around it.

## Mission

By phase 28 the site is built, polished, and verified across the browser matrix. It has no home. Phase 28 gives it one: the user's real domain, owned by the user, with DNS pointing at the hosting the site will deploy to (phase 29), SSL active, and both the apex (`example.com`) and `www` (`www.example.com`) resolving correctly with the chosen canonical redirect. This is the first phase of the deployment group — 28 (domain/DNS/SSL) → 29 (hosting) → 30 (analytics + search submission) — and it deliberately precedes the actual deploy so that when phase 29 ships, it ships *to the real domain*, not to a temp URL the user then has to migrate off.

The defining discipline: **the real domain, owned by the user, configured before deploy.** The failure this prevents is the "I'll just deploy to the `*.vercel.app` URL for now and sort the domain later" path — which produces a launched site on a URL nobody will type, indexed by Google under the wrong hostname, with social shares pointing at the throwaway address, and a painful later migration. If the user has a real domain in mind, phase 28 makes it real *before* phase 29 deploys. If the user genuinely has no domain yet, phase 28 is where they acquire one (the agent walks the registrar choice) — it is not skipped into a temp-URL launch.

The second discipline: **honesty about propagation.** DNS changes are not instant — nameserver delegation and record propagation take minutes to (occasionally) tens of hours. The agent surfaces the realistic wait, verifies propagation with real tooling (`dig`, DNS-over-HTTPS resolver checks, SSL inspection) rather than assuming, and does not declare DNS done until it has *observed* the records resolving and the certificate valid — propagation is waited-for and verified, not hoped-through.

A constraint that recurs: registrar/DNS API tokens are secrets and are never stored — they are user-supplied at the moment of use, used, and not persisted (per `DESIGN-secrets-and-keys.md`).

## Entry conditions

- Phase 27 (cross-browser QA) complete. `audit/QA-REPORT.md` is green — the site is verified-good before it gets a real address (deploying a broken site to a real domain is worse than to a temp URL).
- `.website-builder/project.yaml.stack` (phase 11) and the intended hosting target known — DNS configuration depends on where the site will deploy (Vercel-managed nameservers vs Cloudflare DNS pointing at Cloudflare Pages vs a WordPress host's nameservers vs Framer's). The hosting *target* is decided at phase 11 / refined here; phase 29 actualizes the deploy.
- `.website-builder/keys.yaml` registers the DNS/registrar token *reference* (per `DESIGN-secrets-and-keys.md`) — the token itself is user-supplied at use and not persisted. If the user keeps DNS at an existing registrar, the agent reads the reference and prompts for the token at the moment of the DNS write.
- The user's domain intent is known: a domain they already own (at which registrar), or no domain yet (phase 28 includes acquisition).

## What Claude must establish

A user-owned domain, DNS pointing at the hosting target, SSL active, apex + www both resolving with a canonical redirect — all *verified*, not assumed. The work product:

1. **Domain ownership.** Either the user's existing domain (the agent confirms ownership and reads the registrar) or a newly acquired one. Registrar selection logic (from `DESIGN-deploy-providers.md`): if the user already has the domain, use that registrar; if they want Cloudflare hosting + DNS, recommend Cloudflare Registrar (at-cost, no markup, integrated, free WHOIS privacy); for a `.ch` or other strict ccTLD, recommend a registrar that supports it (Gandi often; switch.ch for `.ch`); otherwise Cloudflare Registrar (default) or Namecheap (alternative). The domain ends up *owned by the user*, in the user's account — never registered under the agent's or a third party's control.
2. **DNS configured.** The records that point the domain at the phase-29 hosting target: A/AAAA or CNAME/ALIAS per the host's requirement (Vercel: A `76.76.21.21` + CNAME, or Vercel-managed nameservers; Cloudflare Pages: CNAME via Cloudflare DNS, same dashboard; Framer/Webflow/WordPress.com: the platform's managed nameservers; a WordPress host: A record at the host's IP), plus any verification TXT the host needs. DNS managed at the registrar (more flexible) or at the hosting platform (simpler) — the agent surfaces the trade-off and the user chooses.
3. **SSL active.** Auto-provisioned (Let's Encrypt or platform-managed) by every recommended host. The agent **verifies** the certificate is issued, valid, covers both apex and www (SAN), and HTTPS is enforced — it does not assume "the host does SSL automatically" without observing a valid cert.
4. **Apex + www both resolve, with a canonical redirect.** `example.com` and `www.example.com` both work; one canonically redirects to the other (the user's choice, consistently applied — this also matters for the phase-26 canonical URL and the phase-30 Search Console property).
5. **`.website-builder/audit/DOMAIN-REPORT.md`** — domain + registrar, DNS records set (type/name/value), the host they point at, the propagation verification (`dig`/DoH output showing resolution, timestamp), the SSL verification (issuer, validity, SAN coverage, HTTPS-enforced), the canonical-redirect direction.

The agent updates `.website-builder/project.yaml.current_phase` to `29` upon completion.

## Gating rules

The agent refuses to advance when:

- **Fake-deploy on a temp URL when the user has a real domain in mind.** The defining gate. If the user intends `example.com`, the agent does not let phase 29 ship to `project-abc.vercel.app` "for now" — the real domain is configured *before* the deploy. **Not overridable** as a silent default; a deliberate temp-URL launch (genuinely no domain yet and the user wants to launch on the platform subdomain meanwhile) is an explicit, logged user decision with the migration cost surfaced.
- **Domain not actually owned by the user.** A domain registered under the agent's account, a placeholder, or a domain the user does not control. The agent confirms the domain is in the user's own registrar account; the user owns their domain, full stop.
- **DNS declared done without observed propagation.** The agent ran the registrar API and assumed it worked. The agent verifies with `dig`/DoH that the records actually resolve to the right target before marking DNS done — assumed propagation is not propagation.
- **SSL assumed, not verified.** "The host auto-provisions SSL" is not "SSL is active." The agent observes a valid certificate (correct issuer, not expired, covers apex + www, HTTPS enforced) before marking SSL done. A site that serves an invalid/incomplete cert at launch is the failure this catches.
- **Apex or www does not resolve, or no canonical redirect.** Only `www` works and the apex 404s (or vice versa), or both resolve but neither redirects to the other (duplicate-content + ambiguous-canonical problem that undercuts phase 26). Both must resolve and the canonical direction must be set.
- **A registrar/DNS token would be persisted.** Any path that writes the registrar API token into a committed file or a non-`.env`/non-1Password store. Tokens are user-supplied at use, used, not persisted (per `DESIGN-secrets-and-keys.md`). Not overridable.

Override is available only on the deliberate-temp-URL-launch case via an explicit logged decision with the migration cost surfaced. Ownership, observed-propagation, verified-SSL, and token-non-persistence are not overridable.

## Tools and skills used

- **Cloudflare MCP** (the canonical-tool path for DNS when Cloudflare is the DNS provider — the recommended default per `DESIGN-deploy-providers.md`) — DNS record provisioning, SSL/TLS settings, redirect rules. Falls back to the registrar's API via `Bash` + `curl` for Namecheap/Gandi/GoDaddy-managed DNS.
- **`Bash`** — the verification workhorse: `whois` (registration/ownership), `dig` (record resolution + propagation from multiple resolvers), DNS-over-HTTPS resolver checks, `openssl s_client` / curl `-vI` (SSL certificate inspection: issuer, validity, SAN, HTTPS-enforced), apex-vs-www resolution + redirect chain.
- **`mcp__context7__resolve-library-id` + `mcp__context7__query-docs`** — for `/cloudflare/wrangler` when the Cloudflare DNS/Pages workflow is heavy in the user's configuration (current Cloudflare DNS + cert + redirect-rule surface). Cited.
- **`WebSearch`** — **mandatory at this phase**: current DNS-verification patterns 2026 (`dig` + `whois` + DoH check patterns, the DNSSEC-validation change CAs adopted, current SSL-verification methods). Cited in `## Reference materials`. Also the Tier-2 fall-back if a canonical DNS/registrar doc is unreachable.
- **`WebFetch`** — Cloudflare DNS docs (or the relevant registrar's API doc) when context7 lacks fresh coverage of the specific provider's record requirements.
- **`AskUserQuestion`** — the registrar credentials (user-supplied at the moment of use, never stored), the domain choice if acquiring, the canonical-redirect direction (apex→www or www→apex), DNS-at-registrar vs DNS-at-host preference.
- **`Read`** — `project.yaml.stack` + the hosting target (drives the DNS record shape), `keys.yaml` (the token reference), `audit/QA-REPORT.md` (the site is verified-good before it gets a real address).

No subagent spawn. The `wb-deploy` phase-group skill (loaded at the deployment-group transition, per Lock M5 — phases 28/29/30) carries the cross-phase contract: phase 28's domain + DNS + SSL is what phase 29 deploys onto and phase 30 submits to the search consoles.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/audit/DOMAIN-REPORT.md` | Domain + registrar (ownership confirmed), DNS records (type/name/value/target host), propagation verification (`dig`/DoH output + timestamp), SSL verification (issuer/validity/SAN/HTTPS-enforced), canonical-redirect direction | The audit trail proving the real domain is owned, configured, propagated, and TLS-valid; read by phase 29 (deploy to this domain), phase 30 (Search Console property = this domain), and the post-launch maintainer |
| DNS records at the registrar/DNS provider | Provider-native | The live records pointing the domain at the hosting target |
| `.website-builder/decisions/temp-url-launch.md` *(when applicable)* | Standard decision-doc frontmatter + body | Created only when the user deliberately chose to launch on a platform subdomain with no custom domain yet, with the migration cost surfaced and accepted |

The `DOMAIN-REPORT.md` with observed propagation + SSL evidence is the required artifact.

## Common failure modes

**"Just deploy to the vercel.app URL, I'll add the domain later."** The temp-URL trap. The site launches on a subdomain nobody types, Google indexes it under that hostname, social shares point at it, and the eventual domain migration costs more than configuring it now would have. The agent's defining gate: if the user has a real domain in mind, it is configured *before* phase 29 deploys — "later" is an explicit logged decision, not a silent default.

**DNS "configured" but never verified to propagate.** The agent set the records via API, got a 200, and called it done — but the records have not propagated, or were set on the wrong zone, and the domain still 404s an hour later. The agent verifies with `dig`/DoH from real resolvers that the domain *actually resolves to the target* before marking DNS done; the API 200 is not the proof, the resolution is.

**SSL assumed because "the host does it automatically."** The host *does* auto-provision — but provisioning can fail (a CAA record blocking the CA, DNS not yet pointing right, a delegation error) and the site serves an invalid cert at launch. The agent observes a valid certificate (issuer, validity, SAN covers apex+www, HTTPS enforced) — "automatic" is verified, not trusted.

**Only www works; the apex 404s.** A CNAME on www but no apex A/ALIAS, so `example.com` is dead while `www.example.com` works (or vice-versa). Both must resolve, and one must canonically redirect to the other — otherwise phase 26's canonical URL and phase 30's Search Console property are pointing at a hostname half the visitors will not reach.

**Propagation wait-time cut instead of waited.** The agent declares DNS done before propagation completes because waiting is inconvenient, and the user "launches" to a domain that intermittently resolves. The agent surfaces the realistic propagation window honestly and waits-and-verifies rather than cutting the corner — DNS that "should be propagated by now" is not propagated until observed.

**Domain registered under the wrong account.** The agent (or a quick-fix path) registers the domain under something other than the user's own registrar account, and the user does not actually control their own domain. The domain is always in the user's account, owned by the user — this is non-negotiable.

**Registrar token persisted.** The DNS API token gets written into a config file or committed for "convenience." Tokens are secrets — user-supplied at the moment of use, used, not stored (per `DESIGN-secrets-and-keys.md`). The agent never persists a registrar/DNS credential.

**A CAA record silently blocks SSL issuance.** An existing CAA record permits only a different CA, so Let's Encrypt/the platform CA cannot issue and SSL silently never provisions. On the agent's SSL-verification checklist — if the cert does not issue, the agent diagnoses the CAA/DNS cause and walks the fix rather than shipping an HTTP-only site.

## Reference materials

- **Design doc — deploy + DNS + registrar catalog (read for the registrar-selection logic + DNS-automation section):** `Workstreams/website-builder/cross-cutting/DESIGN-deploy-providers.md` § Domain registrars + § Domain registrar selection logic + § DNS automation + § Automatic SSL + § Phase contracts that invoke this concern (phase 28 = "registrar choice + DNS automation per adapters")
- **Design doc — secrets handling (registrar/DNS tokens are user-supplied at use, never stored):** `Workstreams/website-builder/cross-cutting/DESIGN-secrets-and-keys.md` § Phase contracts (phase 28 = "DNS provider tokens") + § Anti-patterns
- **Design doc — phase pipeline source:** `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 28 (seed)
- **Phase 29 (the hosting phase 28's DNS points at):** `phase-contracts/29-hosting-deployment.md` § What Claude must establish
- **Phase 26 (the canonical URL phase 28's apex/www redirect must match):** `phase-contracts/26-seo-structured-data.md`
- **External research (loaded fresh 2026-05-18 for this contract):**
  - DNS verification patterns 2026 (WebSearch) — `dig`/`whois`/DoH check patterns; CA challenge methods (HTTP-01/DNS-01/TLS-ALPN-01); DNSSEC-validation adoption by CAs during domain-control + CAA checks; SSL cert-chain inspection; propagation-check tooling (DNSToolbx-class). Confirmed 2026-05-18.
  - `/cloudflare/wrangler` (context7) — current Cloudflare DNS / cert / redirect-rule surface when the Cloudflare workflow is heavy.
  - Cloudflare Registrar: https://www.cloudflare.com/products/registrar/ · Namecheap: https://www.namecheap.com · Gandi: https://www.gandi.net
- **Phase 27 QA gate (verified-good before a real address):** `phase-contracts/27-polish-cross-browser.md`

Freshness date for this contract: **2026-05-18**. DNS/SSL verification practice + CA policies evolve; the agent re-checks current patterns at session start when phase 28 is active and verifies propagation + certificate state by *observation* (`dig`/`openssl`), never by assumption.
