# Maintenance & Monitoring — Reference (phases 33 + 34)

> Loaded on demand when executing phases 33-34. Per-stack maintenance-routine matrix, 2026 uptime-provider comparison, GDPR-compliant Sentry recipe, stack-correct backup matrix, and the phase-34 gate verification checklist. Authoritative behavior specs are `phase-contracts/33-maintenance-cadence.md` and `phase-contracts/34-monitoring-backup.md`; this file is the working reference for *producing* the artifacts.

## The non-negotiable: document + verify the wizard, do not re-decide it

`.website-builder/post-launch/config.yaml` was written by the **phase-29 deploy wizard** (decision 45). It already holds the chosen iteration/notification cadence, the uptime provider, the error-tracking choice, the backup strategy per stack, and `maintainer_skills_installed`. Phases 33 + 34 **document + verify** this — they do not re-run the wizard or impose a different cadence/provider than the user already chose. A `maintenance.md` that contradicts `config.yaml` (and therefore the materialized maintainer's configured behavior) is a defect.

---

## Phase 33 — Per-stack maintenance-routine matrix

`maintenance.md` has four standard sections. Their *content and weight* are stack-specific. Each item names its cadence (from the verified wizard config) **and the maintainer skill that executes it** so the document is an executable contract, not a guilt-list.

| Section | Static (Astro/Eleventy/Hugo) | Next.js / SvelteKit / Payload | WordPress | Framer / Webflow / Wix |
|---|---|---|---|---|
| **Content freshness** | Dated copy, footer year, "current" claims, the roadmap reference. Cadence per wizard. → `wb-maintain-content` | Same + any CMS-driven content drift. → `wb-maintain-content` | Same + WP-post staleness; CMS-notification per wizard. → `wb-maintain-content` | Same; platform-hosted content, lighter. → `wb-maintain-content` |
| **Dependency updates** | `pnpm/npm outdated` — categorize security / minor / major. → `wb-maintain-deps` | Same + framework majors (read release notes; escalate if it touches the design system or core flows) + Payload migration discipline. → `wb-maintain-deps` | **Core + plugin + theme updates** — this is where WP sites get compromised; the heaviest dep surface. → `wb-maintain-deps` | Platform-managed — minimal/no dep surface; note this explicitly so the user knows it is lighter, not skipped. → `wb-maintain-deps` |
| **Security patches** | Advisory-driven `pnpm audit` + redeploy. Apply security ASAP. → `wb-maintain-deps` | Same + dependabot-style review + redeploy. → `wb-maintain-deps` | **Heaviest**: core+plugin+theme security advisories applied fast; WP is the most-attacked surface. → `wb-maintain-deps` | Platform-managed; document that the platform owns this and what the user is still responsible for (their content, their integrations). → `wb-maintain-deps` |
| **Broken-link checks** | Internal + outbound link verification at the wizard cadence. → `wb-maintain-monitoring` / `-content` | Same. → `wb-maintain-monitoring` / `-content` | Same + plugin-driven link breakage. → `wb-maintain-monitoring` / `-content` | Same; platform-hosted assets less likely to 404 but outbound links still rot. → `wb-maintain-monitoring` / `-content` |

**Dependency categorization (all stacks):** *security* → apply ASAP on advisory; *minor* → apply with a regression check; *major* → read release notes, escalate to the full pipeline if breaking changes touch the design system or core flows.

**Skip-cost language for phase 33 (blunt, not softened — no gate but the bluntness is the discipline):** "Without this, the site rots in 6 months. Not *might* rot — *will*. Dependencies accrue vulnerabilities; content goes stale; links break. The decay is the default outcome this plan exists to prevent, not a risk you are accepting." *Mitigant the agent also surfaces:* if the phase-29 wizard already installed the `deps`/`content`/`monitoring` maintainer skills, much of the routine is **already wired to run** — skipping phase 33's *documentation* does not un-install the maintainer; it just leaves the user without the human-readable spec of what it does and when. Log `.website-builder/decisions/skip-phase-33.md` with the certain cost surfaced.

---

## Phase 34 — Uptime provider comparison (2026)

The wizard already chose a provider; phase 34 verifies + activates it. This table is for confirming the choice still makes sense and for explaining the trade-off to the user — not for re-deciding.

| Provider | Free tier (2026) | Strengths | When the wizard picks it |
|---|---|---|---|
| **UptimeRobot** | **50 monitors @ 5-min** — the most generous free plan in 2026; Solo ~$7-8/mo (1-min checks), Team ~$15/mo | Most accessible; large free tier; straightforward scaling | The strong default for muggle sites — free, generous, simple |
| **Better Stack** | Free ~10 monitors @ 3-min + incident management / status pages / log integration | Goes beyond detection into on-call routing + investigation; nicer UI | User wants status pages / incident workflow, not just up/down |
| **Cloudflare Health Checks** | Included with Cloudflare paid plans (not a standalone free tier) | Integrated with Cloudflare DNS (phase 28); canonical-tool path via the **Cloudflare MCP** | The site is already on Cloudflare DNS + the user is on a paid Cloudflare plan |
| **Pingdom** | **No meaningful free tier** in 2026; starts ~$12-15/mo for ~10 monitors | RUM + synthetic testing; performance-focused | The user explicitly wants performance/RUM and will pay; rarely the muggle default |

Default reasoning to give the user: *UptimeRobot's free tier is the most competitive in 2026 for a solo operator / small site; Better Stack if you want incident workflow + a status page; Cloudflare Health Checks only if you are already on Cloudflare paid (it integrates with your phase-28 DNS via the Cloudflare MCP).* Verify the active monitor via the provider API/CLI (`Bash`) or the Cloudflare MCP, confirm it is polling, and **trigger a test alert to confirm the notification reaches a channel the user actually watches** — a monitor alerting to an unread inbox is no monitor.

## Phase 34 — GDPR-compliant Sentry configuration (error tracking)

Only wire error tracking where the stack warrants it (non-trivial JS: Next.js/SvelteKit/interactive). For a static no-JS brochure site, record a *considered decline with reason* in `monitoring.md` — never a silent omission, never reflexive install. When wiring it, configure it GDPR-correctly from the start (DACH/EU audiences make this load-bearing):

- **`send_default_pii: false`** in the SDK config — do not send IP addresses, cookies, user identifiers by default.
- **Server-side data scrubbing** — in Sentry project settings, add sensitive fields to the data scrubber: `email`, `password`, `token`, `ssn`, `credit_card`, `authorization`. Server-side scrubbing applies immediately without a redeploy.
- **SDK `before_send` hook** — filter PII from events client-side before they leave the user's browser (belt-and-suspenders with server-side scrubbing).
- **EU data residency** — for strict GDPR posture, use Sentry's EU region storage, or **Sentry Relay** (a free standalone middle-layer that scrubs PII inside the user's own infrastructure before anything reaches Sentry), or self-host (open-source; GlitchTip is a lighter open-source alternative). Self-host minimum: ~4 CPU / 16GB RAM / 20GB disk — usually over-investment for a muggle site; the SaaS free tier + Relay or EU region + scrubbing is the pragmatic default.
- **Verify receipt** — trigger a test error via the **Playwright MCP** against the live site and confirm it lands in the Sentry dashboard (the "verify active, not just configured" discipline applied to error tracking).

## Phase 34 — Stack-correct backup matrix

State explicitly what git does **and does not** cover. "I assumed git was a backup" is itself a named failure mode for stacks where it is false.

| Asset | Static (Astro/etc.) | Next.js / Payload | WordPress |
|---|---|---|---|
| **Code** | git (repo + host deploy/rollback history — confirm rollback works) | Same | Theme/plugin code in git if custom; **core is not** |
| **Content (Layer-4 MD)** | git | git | n/a (content is in the DB) |
| **CMS / DB content** | n/a (file-based) | **Payload Postgres DB → real DB backup; git does NOT cover this** | **WP database (every post, setting) → explicit DB backup; git does NOT cover this** |
| **Media / uploads** | git or git-LFS | git-LFS or documented store | **WP uploads directory → explicit backup; git does NOT cover this** |
| **Recovery path** | Host rollback — **verify it actually works for this project**, do not assert | Host rollback + DB restore — verify both | Host/plugin backup mechanism + DB restore — verify |

The recovery path must be **verified**, not asserted. "You can roll back on Vercel" is a defect if the agent never confirmed the rollback works for this project. The backup strategy must at minimum be *documented* even when it is trivially "code in git + host deploy history" — the documentation is the deliverable, because the assumption is the failure mode.

## Phase 34 — Gate verification checklist (the pipeline's last gate)

The agent refuses to mark the project complete unless ALL hold (or the explicit logged informed-refusal path is taken):

- [ ] Uptime monitor is **active and polling** (not configured-but-paused).
- [ ] Monitor alert path **verified reaching a channel the user actually watches** (test notification sent + confirmed).
- [ ] Backup strategy **documented and stack-correct** (says what git does NOT cover for this stack).
- [ ] Recovery path **verified** (rollback / DB-restore actually tested for this project, not asserted).
- [ ] Error tracking either **active with test-error confirmed** OR **considered-and-declined with a logged reason** (silent omission on a JS-heavy site = gate failure).
- [ ] `.website-builder/monitoring.md` written with all of the above + the maintainer `wb-maintain-monitoring` / `-escalate` skill mapping.

**The only override** is `.website-builder/decisions/no-monitoring.md`: the user's explicit acknowledgement that the project is being declared complete *without* the safety net, the specific risks restated, and the agent's contrary recommendation recorded. Loud and logged — never a silent close on an un-monitored site. Even then, surface the maintainer's `wb-maintain-monitoring` skill as the cheap path to add it later.

## Hand-off (after phase 34 closes)

The launch sequence is done; the maintainer template (materialized at phase 29 at `.website-builder/post-launch/`) takes over ongoing. This skill points at it and ends — it does not author or invoke the maintainer or its 8 skills (`wb-maintain-content` / `-monitoring` / `-deps` / `-content-add` / `-section-add` / `-page-add` / `-iterate` / `-escalate`). Maintainer invoked via `/wb-maintain` or `wb maintain`. Reference: `DESIGN-post-launch-template.md` §§ Maintenance skill bundle + Wizard-driven customization (decisions 45/49).

## Sources (external research, loaded fresh 2026-05-18)

- Uptime provider 2026 comparison (UptimeRobot 50-monitor free tier strongest; Pingdom no meaningful free tier; Better Stack free + incident workflow): [11 Best Uptime Monitoring Tools 2026 — UptimeRobot Knowledge Hub](https://uptimerobot.com/knowledge-hub/monitoring/11-best-uptime-monitoring-tools-compared/), [Best Pingdom Alternatives 2026](https://uptimerobot.com/knowledge-hub/comparisons-and-alternatives/best-pingdom-alternatives/), [Pingdom vs UptimeRobot vs Hyperping](https://hyperping.com/blog/pingdom-vs-uptimerobot-vs-hyperping)
- Sentry GDPR config (`send_default_pii: false`, server-side scrubbing, `before_send`, Relay, EU residency, self-host minimums): [Best Practices for GDPR Compliance with Sentry — Sentry](https://sentry.io/trust/privacy/gdpr-best-practices/), [Sentry GDPR error tracking + EU storage guide — FlowConsent](https://www.flowconsent.com/en/services/other/sentry), [Self-Host Sentry or GlitchTip 2026 — DanubeData](https://danubedata.ro/blog/self-host-sentry-glitchtip-error-tracking-2026), [Removing PII from Sentry in JavaScript](https://advena.hashnode.dev/removing-personal-information-pii-from-sentry-error-monitoring-in-javascript)
