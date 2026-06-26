---
name: wb-prelaunch
description: This skill should be used when the website-builder agent reaches the pre-launch phase group (phases 24-27) of a website project — specifically when the user says "wire up my integrations", "add analytics / a mailing list / a CRM", "I need to take payments / sell something / set up Stripe", "add a booking / Cal.com / paid consultation", "set up the commerce side", "I need a privacy policy / imprint / cookie banner / refund policy / terms of sale", "make my site show up on Google / add SEO / structured data / sitemap", "do a final QA pass / cross-browser check / Safari testing", or when `.website-builder/project.yaml.current_phase` is 24, 24a, 24b, 24c, 25, 26, or 27. Drives the integrations fork, the conditional commerce branch (active only when `transactional: true`), the legal surface, SEO/structured-data, and the cross-browser/cross-device dress rehearsal before deployment.
version: 0.1.0
---

# wb-prelaunch — Pre-launch phase group (24-27 + commerce branch 24a/b/c)

> The pre-launch group: the phases that turn a built site into a launchable one. Integrations get wired (24), commerce stands up if the site is transactional (24a→24b→24c), the legal surface goes live (25), the site becomes discoverable (26), and the whole thing gets a real cross-browser dress rehearsal (27). After this group, the deployment group (phase 28+) takes over.
>
> **Design-doc primacy.** This skill is a procedural router. The substantive contracts live in the phase-contract MDs and the design docs cited below — read those verbatim at the phase the user is in. Do not paraphrase them from this skill; point the agent at them.
>
> Skill anatomy + how this skill integrates with the freelancer agent profile + hooks: `Workstreams/website-builder/foundation/DESIGN-architecture.md` § Skills ("one per phase group"; skills layer, do not override; the phase contract MD is the instruction body). Key handling for every keyed integration in this group (analytics/CRM/mailing keys at 24, commerce secrets at 24a/24b, DNS/deploy tokens forward): `Workstreams/website-builder/cross-cutting/DESIGN-secrets-and-keys.md` — `keys.yaml` holds *references* only, secrets live in `.env`/1Password, code reads `process.env.{KEY}`, never inline a secret (the publishable Stripe key is *not* a secret but still flows through the env mechanism for uniformity).

## What this skill drives

The agent invokes the right phase contract per the user's `current_phase` and executes it. The seven phases:

| Phase | Name | Contract | Always runs? |
|---|---|---|---|
| 24 | Integrations (non-commerce) + the transactional fork | `phase-contracts/24-integrations.md` | Yes |
| 24a | Commerce platform setup | `phase-contracts/24a-commerce-platform.md` | Only if `transactional: true` |
| 24b | Payment provider wiring | `phase-contracts/24b-payment-provider.md` | Only if `transactional: true` |
| 24c | Commerce-specific legal | `phase-contracts/24c-commerce-legal.md` | Only if `transactional: true` |
| 25 | Legal pages (privacy, imprint, cookie consent, T&Cs) | `phase-contracts/25-legal-pages.md` | Yes |
| 26 | SEO + structured data + metadata | `phase-contracts/26-seo-structured-data.md` | Yes |
| 27 | Polish + cross-browser/cross-device QA | `phase-contracts/27-polish-cross-browser.md` | Yes |

Each contract spells out its own Mission / Entry conditions / What Claude must establish / Gating rules / Tools / Output artifacts / Common failure modes. **Read the contract for the phase the user is in before doing the work.** This skill is the connective tissue across the seven, not a substitute for any of them.

## The conditional fork — the load-bearing routing rule

Phase 24 is the pipeline fork. Phase 11 locked `.website-builder/project.yaml.transactional` to `true` or `false`. At phase 24's close the agent computes `next_phase` **strictly from that flag — never from the site's vibe**:

- `transactional: true` → `next_phase` is `24a`. The linear chain `24a → 24b → 24c → 25` runs.
- `transactional: false` → `next_phase` is `25`. The commerce branch is skipped entirely.

Surface the computed branch to the user explicitly at phase-24 close ("your project is flagged transactional, so we're setting up commerce next" / "non-transactional, so we go straight to legal pages") so a wrong phase-11 decision gets caught before the pipeline commits. If the flag is somehow unset (should be impossible — phase 11 is not skippable), **do not guess** — route back to phase 11's transactional decision. If a non-transactional user realizes mid-phase-24 that they need to sell something, route through the decision-34 transactional-flag-change path (forces restart of phases 12, 22, 24a/b/c) — never silently bolt commerce onto a non-commerce build.

The commerce branch (24a/b/c) is **inside this skill** — there is no separate commerce skill (Decision 64). The same `wb-prelaunch` skill carries the whole pre-launch group including commerce.

## How to use this skill, phase by phase

For every phase: read the phase contract, run the work it specifies, produce its required `.website-builder/audit/*-REPORT.md` artifact, and respect its gating rules (most are **not overridable** — they are the failures the phase exists to prevent). Then advance `project.yaml.current_phase`.

### Phase 24 — Integrations + the fork

Re-read `project.yaml.requirements` (phase 3) and wire every non-commerce integration it named (analytics, mailing list, CRM, chat, search, free scheduling). The discipline is **parity**: an integration is done only when a real event fired against the *production-bound* configuration and was confirmed received — not "it works on the preview deploy". For any cookie-setting integration (GA4, some chat/CRM trackers), write the hard dependency that phase 25 must gate it behind consent into `INTEGRATIONS-REPORT.md` so phase 25 cannot miss it. Surface cookieless analytics (Plausible/Fathom/Cloudflare) as the choice that sidesteps the phase-25 consent burden entirely. Compute and surface the transactional fork at close.

### Phases 24a / 24b / 24c — the commerce branch (only if transactional)

This is the heaviest part of the group and the part with mandatory external research. Load `references/commerce-branch.md` for the full Stripe Checkout / Cal.com / TWINT / SCA recipe map, and read the per-phase design docs **in full** before standing commerce up:

- 24a — `Workstreams/website-builder/commerce/DESIGN-commerce-stripe-checkout.md` and/or `commerce/DESIGN-booking-calcom.md`
- 24b — `Workstreams/website-builder/commerce/DESIGN-payment-providers.md`
- 24c — jurisdiction legal: load `references/jurisdiction-legal.md`

MVP scope is locked (decision 54): **Stripe Checkout** (payments) + **Cal.com** (bookings) are the only first-class platforms; the nine expansion platforms (Shopify, Lemon Squeezy, Snipcart, Paddle, Gumroad, Sellfy, Saleor, WooCommerce, Shopify Hydrogen) are named-as-expansion-paths only, picked only with an explicit logged decision and degraded-support acceptance. **TWINT-via-Stripe is the default for any Swiss-audience site** (decision 26) — CHF-only, native via Stripe, no separate account. The three non-overridable commerce gates: (1) no commerce-ready claim without a **rehearsed test purchase/booking** observed succeeding in test mode; (2) any webhook handler that acts on `checkout.session.completed` (or the Cal.com payment confirmation) **without verifying the signature** against the raw body is refused; (3) an EU/EEA/UK/Swiss card flow where the **3DS/SCA challenge does not fire** in a regulatory-test-card transaction is not deployable.

### Phase 25 — Legal pages

The legal surface every site needs whether it sells or not: privacy policy (generated from the *real* `INTEGRATIONS-REPORT.md` + `FORMS-REPORT.md`, never a template that lies about the data practice), terms of use where warranted, **imprint** (non-negotiable for any commercial site whose owner is in or targets DACH — Switzerland/Germany/Austria), and **cookie consent** that genuinely gates the phase-24-flagged non-essential cookies (the gate is the network-level proof — Playwright confirms the cookie does *not* set pre-consent — not the banner's mere presence). Load `references/jurisdiction-legal.md` for the DACH-imprint and EU-cookie-consent specifics, the 2026 enforcement landscape, and the not-a-lawyer discipline.

### Phase 26 — SEO + structured data + metadata

Per-page-specific title / meta description / OG+Twitter / schema.org JSON-LD of the type the page actually is, plus build-wired sitemap.xml and a correct robots.txt. Two non-negotiables: **no two pages share a title or description** (the single-template-everywhere failure), and **structured data mirrors visible content, never invents it** (invented `AggregateRating`/`Offer` markup risks a Google manual action). Load `references/seo-structured-data.md` for the schema.org type-per-page catalog and the validation workflow. In 2026 LLMs are a primary brand interpreter — the page's metadata + `Organization`/`Person` data must read coherently to a model, not just a crawler.

### Phase 27 — Polish + cross-browser/cross-device QA

The last cross-cutting look before deploy. A Playwright walk-through of every page across **Chromium + Firefox + WebKit** at **mobile + tablet + desktop** profiles, a deliberate **Safari-specific bug pass**, final visual polish, and **re-verification on the matrix** that 24-26's deliverables hold (consent still gates cookies on Safari; structured data renders server-side in every engine; integrations fire or their ITP caveat is true). The absolute gate: **the agent refuses to deploy with a known visual bug** — it is fixed here, or explicitly accepted by the user with the cost logged. "Tested" means the matrix, not desktop-Chrome-only. Load `references/cross-browser-qa.md` for the Safari checklist and the matrix grid schema.

## 3rd-party composables to surface (recommend — do NOT vendor)

These are skills the user MAY invoke via the `Skill` tool. Recommend them at the right phase; do not bundle or embed them:

- **Phase 26 (sitemap):** recommend `documentation-generation:openapi-spec-generation` as a loose composable when the user wants a more structured/validated sitemap XML or an API-surface sitemap for an app-shaped site. Phase 26's sitemap is build-wired regardless; this is an optional enhancement, not a dependency.

(The pre-launch group is otherwise tool-heavy rather than composable-heavy — the Stripe MCP, Playwright MCP, `WebFetch`/`WebSearch`, and the phase contracts carry the load. The agent uses the provider's MCP where one exists per the canonical-tool-first principle, falling back to REST via `Bash`+`curl`.)

## Mandatory external research (run at the phase that needs it; cite in the audit report)

The phase contracts carry a fresh 2026-05-18 research baseline cited verbatim in their `## Reference materials`. The agent re-validates at session start when the relevant phase is active and re-fetches if cached docs are >30 days old. Required surfaces:

- **24a/24b — context7 `/stripe/stripe-node`** (Checkout Session API, `webhooks.constructEvent` signature verification against the raw body, TWINT `payment_method_types`, SCA `off_session`/`setup_future_usage` flags) — cache to `.website-builder/library/docs/stripe.md`. **24b — Stripe TWINT docs** (`https://docs.stripe.com/payments/twint` — CHF-only, merchant prerequisites) and **Stripe SCA docs** (`https://docs.stripe.com/strong-customer-authentication`).
- **24a — Cal.com developer docs** (`https://cal.com/docs/api-reference` — API v2 at `https://api.cal.com/v2/`, event-types/bookings/slots, Atoms React components; no official MCP — REST via `Bash`+`curl`).
- **24c — EU consumer-rights** (European Commission consumer-contract-law canonical) + **Swiss VAT** (admin.ch / Swiss FTA). **Includes the EU Withdrawal-Button obligation — Directive (EU) 2023/2673, mandatory "withdraw/cancel" function for sites selling to EU consumers, effective 19 June 2026** (see `references/jurisdiction-legal.md`).
- **25 — Swiss imprint** (UWG Art. 3(1)(s) + revFADP) + **EU GDPR/ePrivacy cookie consent** (EDPB / Your Europe; the 2026 enforcement landscape — CNIL fined Google €325M and Shein €150M in Sept 2025 for cookie violations).
- **26 — schema.org** (`https://schema.org/`) + **Google structured-data guidance** (`https://developers.google.com/search/docs/appearance/structured-data`).
- **27 — none mandated** (cross-browser behavior is a runtime concern verified by running the site via Playwright, not by fetched docs).

Treat a 404 on a canonical legal source as a Tier-2 fall-back: WebSearch reputable *current* sources, cite with the fetch date — never silently substitute training-data law (it changes; stale legal knowledge is a liability).

## Reference files

- **`references/commerce-branch.md`** — phases 24a/24b/24c recipe map: Stripe Checkout three modes + stack pairings, Cal.com cloud-vs-self-hosted, TWINT-via-Stripe constraints, SCA/3DS jurisdiction table, the webhook-signature-verification non-negotiable, the expansion-platform list, `commerce-config.yaml`/`payment-config.yaml` schemas, the per-phase setup sequences.
- **`references/jurisdiction-legal.md`** — phases 24c + 25 legal regimes: EU Consumer Rights Directive (14-day withdrawal + digital-supply-consent waiver + the 2023/2673 withdrawal-button), Swiss VAT (8.1%, CHF 100k threshold, fiscal representative) + Swiss imprint (UWG Art. 3(1)(s)) + revFADP, US sales-tax nexus, UK consumer law, the EU cookie-consent valid-consent requirements + 2026 enforcement, the not-a-lawyer discipline.
- **`references/seo-structured-data.md`** — phase 26: the schema.org type-per-page catalog with core properties, the per-page metadata checklist, the JSON-LD validation workflow, the LLM-discoverability check, the sitemap/robots build-wiring.
- **`references/cross-browser-qa.md`** — phase 27: the full Safari-specific bug checklist with fixes, the browser × device matrix grid schema, the pre-launch-layer re-verification list, the known-bug gate procedure.
