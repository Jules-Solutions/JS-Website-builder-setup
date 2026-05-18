---
phase: "24b"
name: Payment provider wiring
group: pre-launch
pipeline_section: pre-launch
skill: wb-prelaunch
prev_phase: "24a"
next_phase: "24c"
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/commerce/DESIGN-payment-providers.md
  - Workstreams/website-builder/commerce/DESIGN-commerce-stripe-checkout.md
  - Workstreams/website-builder/commerce/DESIGN-booking-calcom.md
  - Workstreams/website-builder/cross-cutting/DESIGN-secrets-and-keys.md
---

# Phase 24b — Payment provider wiring *(only if transactional)*

> Wire the actual payment rails under the commerce platform phase 24a stood up. For the MVP this is Stripe as the canonical processor, with TWINT-via-Stripe enabled by default whenever the audience is Switzerland (locked decision 26). The phase where the right card methods, the right regional methods, the webhooks, and the jurisdiction-correct SCA/3DS settings get configured and test-transacted. The agent refuses a non-test deploy if SCA is not configured for EU users, or if a Swiss-audience site is missing TWINT. Four other providers (Mollie, PayPal, Square, Klarna) are real expansion options named here in a brief block; the MVP combination is Stripe + TWINT-via-Stripe.

## Mission

Phase 24a stood up the commerce platform (Stripe Checkout for payments, Cal.com for bookings). Phase 24b wires the payment provider *underneath* it: which payment methods are enabled, which regional methods are turned on for which audience, how webhooks are configured so the site only confirms an order/booking after the provider confirms the money moved, and how Strong Customer Authentication / 3D Secure is set for the user's jurisdiction. The site can take money in the abstract after 24a; after 24b it can take money *correctly* — with the right methods for the right region, the right fraud/authentication posture, and a verified webhook so a held order never silently confirms unpaid.

The MVP scope is locked by **decision 54** (Stripe is the canonical payment provider) and sharpened by **decision 26** (a Swiss audience implies TWINT-via-Stripe enabled by default). For the MVP the agent wires **Stripe** — the global workhorse, best documentation, broadest method coverage, deepest stack integration, the right answer for ~80% of website-builder users — and, when `project.yaml` indicates a Swiss audience, **TWINT through Stripe** (TWINT has no separate account or aggregator; it is a Stripe payment method type for CHF transactions). The other four providers in the design surface (Mollie, PayPal, Square, Klarna) are real and fully designed but are expansion options for the MVP — named here in a brief block, wired only on explicit user request with a logged decision.

For a **Cal.com booking** site, 24b is light when the booking is free (no payment rails to wire — the agent confirms the no-payment path and advances) and runs in full when the booking is paid (Cal.com bridges to Stripe; TWINT for Swiss paid bookings works only via Stripe, never PayPal). For a **Stripe Checkout** site, 24b is the main event: enabling cards + wallets + regional methods, verifying domain for Apple Pay / Google Pay, configuring the webhook endpoint, and confirming SCA fires for EU customers in a test rehearsal.

The two hard gates: **a Swiss-audience site without TWINT is not done** (per decision 26 — the agent flags and enables, or fires the pause-and-report if the platform cannot do TWINT), and **an EU-customer flow without SCA configured is not deployable** (PSD2 in the EEA, equivalent in the UK and effectively Switzerland-via-Stripe — the agent verifies the 3DS challenge fires in a test transaction before it will let the build proceed to live).

## Entry conditions

- Phase 24a (commerce platform setup) complete. `.website-builder/commerce-config.yaml` exists with the chosen platform (Stripe Checkout or Cal.com), the products/event-types, and the phase-24a test-rehearsal evidence.
- `.website-builder/project.yaml.transactional` = `true`; `.transactional_kind` set. If a Cal.com booking site is free (`transactional_kind: bookings` with no price on the event types), 24b runs light.
- `.website-builder/project.yaml` audience signal is readable — `languages` containing `de`/`fr`/`it`/`rm` and/or an explicit Swiss-audience statement drives the TWINT decision; the audience region drives the SCA requirement and the regional-method set (iDeal for NL, SEPA for EU recurring, etc.).
- `.website-builder/keys.yaml` has the Stripe key references from 24a (`STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`). TWINT needs no additional keys (it uses Stripe credentials). Any expansion-provider keys (Mollie/PayPal/etc.) are registered here only if that provider is added by explicit decision.

## What Claude must establish

The payment provider wired, the right methods enabled for the audience, webhooks verified, SCA/3DS jurisdiction-correct, test transactions completed. The work product:

1. **Payment methods enabled per audience.** Cards auto-enabled (Visa/MC/Amex/etc.). Apple Pay / Google Pay auto-enabled *after the agent walks the user through DNS-based domain verification*. Regional methods turned on per the `DESIGN-payment-providers.md` decision tree: **TWINT** for a Swiss audience (CHF-only, native via Stripe), iDeal for a Dutch audience (EUR), SEPA Direct Debit for EU recurring, etc. Klarna/Afterpay only if BNPL is wanted and AOV justifies it (an expansion-provider decision).
2. **Webhook endpoint configured + verified.** The Stripe webhook points at the site's production-bound handler; the handler verifies the `stripe-signature` header against `STRIPE_WEBHOOK_SECRET` via `stripe.webhooks.constructEvent` before trusting `checkout.session.completed`. For a paid Cal.com booking, the payment-confirmation webhook is configured so the booking confirms only after payment success.
3. **SCA / 3DS configured for the jurisdiction** (see the dedicated sub-section below). For EU/EEA + UK + Swiss-via-Stripe customers, Strong Customer Authentication must be active; Stripe Checkout handles it automatically, but the agent *verifies the challenge actually fires* in a test transaction rather than trusting "it's automatic."
4. **Test transactions completed per enabled method.** Stripe test card `4242 4242 4242 4242` for the happy path; a 3DS-required regulatory test card to confirm the SCA challenge fires for EU; a CHF + TWINT test selection for a Swiss site; a paid-Cal.com-booking test confirming the booking only after payment.
5. **`.website-builder/payment-config.yaml`** recording: primary provider, enabled methods, currencies, regional overrides (e.g., `CH: { primary: stripe }` to force the TWINT-enabled flow), webhook config, SCA verification evidence, test-transaction evidence.

The agent updates `.website-builder/project.yaml.current_phase` to `24c` (commerce-specific legal) upon completion. The chain is linear — 24b always advances to 24c.

## Primary MVP combination (full prose — locked decisions 54 + 26)

### Stripe as the canonical payment provider

Stripe is the MVP payment provider. Why default: best documentation, most mature API, widest payment-method coverage, deepest stack integration across all eight stacks, the right answer for the large majority of website-builder users. Auth is the trio registered at 24a: `STRIPE_SECRET_KEY` (server-side, `sk_test_*` for all rehearsal, `sk_live_*` only at phase-29 deploy with explicit confirmation), `STRIPE_PUBLISHABLE_KEY` (client-side, not a secret), `STRIPE_WEBHOOK_SECRET` (`whsec_*`, used to verify every webhook). Costs are surfaced transparently: ~2.9% + 30¢ US, ~1.5% + €0.25 EEA cards, ~2.5% + €0.25 international, +1% cross-currency, $15/dispute (refunded if won; the user is on the hook — Stripe is not a Merchant of Record), Stripe Tax optional at +0.5% (automates calculation but does not transfer compliance liability — that is phase 24c's concern). Payment methods by region: global cards + Apple Pay + Google Pay; EU SEPA/iDeal/Bancontact/Sofort/giropay/P24; CH TWINT (CHF only); UK BACS; US/CA/AU ACH; BNPL Klarna/Afterpay. The agent enables exactly the methods the audience needs per the `DESIGN-payment-providers.md` decision tree — not every method (a US-only site does not get iDeal), and never *fewer* than the audience requires (a Dutch site without iDeal loses conversion).

The webhook is non-negotiable infrastructure. The agent generates (or verified, from 24a) a handler that calls `stripe.webhooks.constructEvent(rawBody, req.headers['stripe-signature'], STRIPE_WEBHOOK_SECRET)` inside a try/catch, returns 400 on signature-verification failure, and only acts on `checkout.session.completed` (or the relevant event) after verification passes. An order/booking that is marked fulfilled on an *unverified* webhook is a forged-event vulnerability the agent refuses to ship (a non-overridable gate). context7 `/stripe/stripe-node` confirms the current verification API (current as of the 2026-05-18 fetch: synchronous `stripe.webhooks.constructEvent` against `express.raw({ type: 'application/json' })` body — the raw body, never the parsed JSON).

### TWINT-via-Stripe — enabled by default for Switzerland (decision 26)

TWINT is Switzerland's dominant mobile payment method — ~3.5M+ active users out of ~8.5M population, ~35%+ of Swiss e-commerce. A Swiss-audience site without TWINT loses substantial revenue, so **decision 26 makes TWINT-via-Stripe the default for any site whose `project.yaml` indicates a Swiss audience** (languages including `de`/`fr`/`it`/`rm`, or an explicit Swiss-audience statement at the 24b interview). TWINT is **native via Stripe** — no separate TWINT account, no aggregator, no extra keys. The agent enables it in the Stripe Dashboard (Settings → Payment Methods → TWINT) which makes it appear automatically in Checkout, Payment Links, and Elements; or, for server-side Sessions, by including `twint` in `payment_method_types` alongside `card` with `currency: chf`.

The hard constraints, confirmed fresh from Stripe's TWINT docs (2026-05-18 fetch): **TWINT is CHF-only** — it cannot process EUR/USD/any other currency; a Swiss-international site needs separate flows (CHF+TWINT for Swiss customers, cards-only default for others), and the agent enforces CHF-only TWINT in Session creation. **Maximum transaction amount 5,000.00 CHF.** **Merchant-onboarding prerequisites Stripe enforces before granting TWINT access:** an operational, publicly accessible website (no password protection, no "coming soon"), displaying the legal business name + owner (for sole proprietors), complete business address, and contact info — for physical goods, Switzerland must be a shipping destination and prices shown in CHF at checkout. The agent surfaces these prerequisites at 24b because they are also exactly what phase 25 (imprint) and phase 24c (commerce legal) produce — TWINT access and DACH legal compliance are the same checklist viewed from two angles, and the agent connects them so the user does not discover at launch that TWINT was blocked for a missing imprint. Refunds: full/partial, up to 180 days, minutes to process. Disputes: supported, rare (25-50 per 1,000,000). For a paid **Cal.com** booking, TWINT works only when Cal.com's payment processor is Stripe (not PayPal) — the agent flags this at 24b for any Swiss booking site and ensures Stripe is the Cal.com payment app.

**Pause-and-report rule (from `DESIGN-payment-providers.md`):** if the site has a Swiss audience but the commerce platform chosen at 24a cannot do TWINT (the expansion platforms Paddle / Gumroad / Sellfy / Snipcart, or a PayPal-only Cal.com), the agent MUST surface this as a critical decision point and recommend either (a) switch to a Stripe-direct-compatible platform, or (b) accept losing TWINT with the user's explicit confirmation of the Swiss-revenue impact. The agent does not silently launch a Swiss site without TWINT.

## SCA / 3DS — jurisdiction sub-section

Strong Customer Authentication is a regulatory requirement, not a feature toggle, and the right setting depends entirely on where the customer is:

- **EU / EEA customers — SCA mandatory.** PSD2 has required SCA since 14 September 2019. Two-factor authentication (typically a 3D Secure challenge) on card payments unless a risk-based exemption applies (low-value, low-risk — and the bank can still demand full authentication even when an exemption is claimed). The agent does not rely on exemptions; it configures for SCA and verifies the 3DS challenge fires.
- **UK customers — SCA mandatory.** Equivalent UK enforcement (with a grandfathering date of 14 September 2021 for cards saved before then). Treated the same as EEA for configuration purposes.
- **Swiss customers — SCA via Stripe, effectively required.** Swiss customers paying EU-issued or EEA-acquired cards fall under the SCA regime through Stripe's handling; the agent configures Swiss flows for SCA the same as EEA. TWINT itself is a push-approval method (the user approves in the TWINT app), which carries its own strong-authentication property.
- **US customers — SCA not required.** No PSD2 equivalent. The agent does not impose 3DS friction on a US-only audience (it would needlessly lower conversion), but it does keep Stripe Radar / dynamic 3DS rules available for fraud-flagged transactions.

How the agent handles it: **Stripe Checkout handles SCA automatically** — the hosted page applies the 3DS challenge when required, with no extra merchant configuration, and the same applies to saved-card/off-session flows via `setup_future_usage: 'off_session'` / `off_session: true` (or Setup Intents `usage: 'off_session'`) and to subscriptions via Stripe Billing. But "automatic" is a claim the agent verifies, not trusts: the agent runs a test transaction with a 3DS-required regulatory test card against an EU-configured flow and confirms the challenge actually appears and the `requires_action` → completed path works. Liability shift: 3DS-authenticated payments shift fraud liability to the card issuer — a real benefit the agent surfaces to the user. Merchant-initiated transactions (subscriptions billed off-session) require recorded customer consent (explicit authorization, expected frequency, amount-determination basis) — the agent ensures the consent language exists (phase 24c owns the disclosure copy; 24b ensures the technical `off_session` flag and the consent capture are wired). Legacy Charges API does not support SCA and faces high EU decline rates — the agent never generates Charges-API code for an EU-audience site; it uses Checkout / Payment Intents.

**Gate:** an EU/EEA/UK/Swiss-audience flow where the 3DS challenge does not fire in the SCA test transaction is not deployable. Not overridable.

## Expansion payment providers (post-MVP — brief mention block)

Fully designed in `Workstreams/website-builder/commerce/DESIGN-payment-providers.md`, real, but expansion options for the MVP. The agent names these only on explicit user request or clear audience need, and logs a decision before adding one alongside Stripe:

- **Mollie** — EU-focused; cheaper iDeal (0.29% + €0.25) / Bancontact / SEPA than Stripe. The pick when NL/BE/Nordic audience >40%. No TWINT.
- **PayPal** — brand-trust legacy; high in Germany (~70% e-commerce share) and older/consumer audiences. Higher fees (3.49% + $0.49 US; severe cross-border ~4.4%). Rarely sole provider — offered *alongside* Stripe. No TWINT.
- **Square** — US/UK/AU/CA/JP merchants running online + in-person POS with unified inventory. No TWINT.
- **Klarna** — BNPL (Pay-in-3/4, Pay-in-30, Financing) for higher AOV (>$100 — fashion/furniture/electronics/courses). Enabled *via Stripe* (`klarna` payment_method_type) or Mollie or direct. Higher fees offset by conversion + AOV lift.

A common real configuration is **Stripe (with TWINT) + PayPal** for a Swiss + general audience, or **Stripe + Klarna** for higher-AOV. Multi-provider is supported but each added provider is an explicit decision with its own test transactions; the MVP default stays Stripe (+ TWINT for Switzerland) alone.

## Gating rules

The agent refuses to advance when:

- **Swiss audience, no TWINT.** Per decision 26. If `project.yaml` indicates a Swiss audience and TWINT is not enabled (and the platform *can* do TWINT), the agent refuses and enables it. If the platform *cannot* do TWINT, the agent fires the pause-and-report (switch platform or explicitly accept the Swiss-revenue loss). **Not overridable** except via the explicit-acceptance branch of the pause-and-report.
- **EU/EEA/UK/Swiss flow without SCA verified.** The agent runs a 3DS-required test transaction; if the challenge does not fire for an EU-configured flow, the build is not deployable. **Not overridable** — shipping an EU card flow that silently bypasses SCA is a regulatory and decline-rate failure.
- **Webhook handler without signature verification.** Any handler that acts on `checkout.session.completed` (or the Cal.com payment confirmation) without verifying the signature is refused. **Not overridable.**
- **Regional payment method missing for the named audience.** Dutch audience without iDeal, EU-recurring without SEPA — the agent's per-audience decision tree flags the gap and enables the method (overridable only with an explicit logged decision that the conversion cost is accepted).
- **Currency / method mismatch.** TWINT enabled for a EUR-priced flow (TWINT is CHF-only) — the agent's per-currency method map prevents this and surfaces the contradiction.
- **Domain not verified for Apple Pay / Google Pay.** The wallet methods will silently not appear without DNS domain verification; the agent makes verification part of the 24b checklist (overridable only by explicitly dropping the wallet methods).
- **Test transactions not run per enabled method.** "It should work" is not a pass; each enabled method has an observed test transaction. Not overridable.

## Tools and skills used

- **Stripe MCP** (canonical-tool-first) — method enablement, webhook configuration, domain verification, test transactions. Falls back to Stripe REST API via `Bash` + `curl`.
- **`mcp__context7__resolve-library-id` + `mcp__context7__query-docs`** — **mandatory at this phase** for `/stripe/stripe-node`, this time the TWINT-enablement + SCA-configuration + off-session surface (same library, different surface than 24a). Cached/extended in `.website-builder/library/docs/stripe.md`; cited.
- **`WebFetch`** — **mandatory at this phase**: `https://docs.stripe.com/payments/twint` (TWINT-via-Stripe MVP combo, CHF-only, 5,000 CHF cap, merchant prerequisites — confirmed 2026-05-18) and `https://docs.stripe.com/strong-customer-authentication` (current SCA/3DS guidance, EEA/UK regions, automatic Checkout handling, off-session flags — confirmed 2026-05-18). Cited in `## Reference materials`.
- **`Playwright` MCP** — the test-transaction workhorse: drive the checkout with the happy-path test card, the 3DS-required regulatory card (verify the challenge fires), the CHF+TWINT selection, the paid-booking flow.
- **`Edit` / `Write`** — webhook-handler code (with signature verification, non-negotiable), regional-method config, the `payment-config.yaml`.
- **`AskUserQuestion`** — the target-market question (drives the decision tree), Stripe Dashboard steps only the user can do (method enablement toggles, domain verification DNS records the user adds at their registrar).
- **`Read`** — `commerce/DESIGN-payment-providers.md` **in full** (the decision tree, the TWINT-by-platform table, the pause-and-report rule), `commerce-config.yaml` (24a's output), `project.yaml` audience signals, `keys.yaml`.

No subagent spawn. `wb-prelaunch` phase-group skill carries the commerce branch (Decision 64 — no separate commerce skill).

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/payment-config.yaml` | Primary provider, enabled methods, currencies, regional overrides, webhook config, SCA verification evidence, per-method test-transaction evidence | The payment-rails configuration record; read by phase 24c (commerce legal — SCA disclosures), 29 (deploy — live-key cutover), and the post-launch maintainer (rotation) |
| Webhook handler code in the user's project | Per stack convention, signature-verifying | The verified handler — live code that refuses unverified events |
| `.website-builder/keys.yaml` (updated) | References only | Any expansion-provider keys (only if added by decision); TWINT needs none |
| `.website-builder/decisions/payment-provider-added-{provider}.md` *(when applicable)* | Standard decision-doc frontmatter + body | Created only when an expansion provider (Mollie/PayPal/Square/Klarna) was added alongside Stripe with explicit acceptance |

The `payment-config.yaml` with embedded SCA + per-method test evidence is the required artifact.

## Common failure modes

**TWINT not enabled for a Swiss audience.** The single most important failure for this product's home market. The agent flags TWINT at 24a (CHF currency) and enables it at 24b for any Swiss-audience project; if the platform cannot do TWINT, the pause-and-report fires rather than a silent Swiss launch without ~35% of the local payment market.

**SCA "is automatic" so nobody verified it.** Stripe Checkout does handle SCA automatically — but "handles automatically" and "verified the 3DS challenge actually fires for an EU card" are different facts. The agent runs the regulatory 3DS test card against an EU-configured flow and confirms the `requires_action` path before it will let the build go live.

**Webhook signature not verified.** The handler trusts `checkout.session.completed` because "Stripe sent it" — but anyone can POST that JSON. The agent generates handlers that verify the signature against the raw body before acting; an order fulfilled on a forged event is the failure this gate prevents.

**Test-mode keys deployed to production.** `sk_test_*` ships and no real payment can clear. The agent flips to `sk_live_*` only at phase 29 with explicit confirmation and environment-specific separation — never the same key both places.

**Domain not verified, wallets silently absent.** Apple Pay / Google Pay need DNS domain verification or they just do not appear; the user thinks they offered wallets and did not. The agent makes verification a 24b checklist item, confirmed by Playwright actually seeing the wallet option at checkout.

**Regional method missing.** A Dutch site without iDeal, an EU subscription without SEPA — conversion quietly suffers. The agent's per-audience decision tree (from `DESIGN-payment-providers.md`) enumerates the required methods per the audience and flags any gap.

**TWINT enabled for the wrong currency.** TWINT is CHF-only; enabling it on a EUR flow produces rejected transactions. The agent's per-currency method map prevents the mismatch and surfaces it if the config is contradictory.

**A free Cal.com booking site gets full payment wiring it does not need.** If the booking is genuinely free (no price on the event types), 24b is light — the agent confirms the no-payment path and advances rather than wiring Stripe rails for a transaction that never takes money.

**Cal.com paid booking on PayPal in Switzerland.** TWINT works only via Stripe. A Swiss paid-booking site configured with Cal.com → PayPal cannot offer TWINT; the agent flags this and ensures Stripe is the Cal.com payment app for Swiss booking sites.

## Reference materials

- **Design doc — payment-provider matrix (read in full):** `Workstreams/website-builder/commerce/DESIGN-payment-providers.md` — the per-audience decision tree, the comparison matrix, the TWINT-CRITICAL section, the commerce-platform-TWINT-support table, the Swiss pause-and-report rule, the multi-provider patterns, `payment-config.yaml` schema, cross-provider failure modes
- **Design doc — Stripe Checkout (TWINT + phase-24b sub-section):** `Workstreams/website-builder/commerce/DESIGN-commerce-stripe-checkout.md` § TWINT for Switzerland + § Phase 24b — payment provider wiring
- **Design doc — Cal.com (paid-booking payment bridge):** `Workstreams/website-builder/commerce/DESIGN-booking-calcom.md` § Phase 24b — payment provider wiring (for paid bookings) + the TWINT-via-Stripe-only caveat
- **Design doc — phase pipeline source:** `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 24b (seed)
- **Design doc — key handling:** `Workstreams/website-builder/cross-cutting/DESIGN-secrets-and-keys.md` § Phase contracts (24b listed) + § Anti-patterns
- **Phase 24a (the platform 24b wires under):** `phase-contracts/24a-commerce-platform.md` § What Claude must establish
- **Phase 11 transactional decision (decision 26 Swiss-audience source):** `phase-contracts/11-stack-decision.md` § Transactional decision
- **External research (loaded fresh 2026-05-18 for this contract):**
  - context7 `/stripe/stripe-node` v19.1.0 — webhook verification (`stripe.webhooks.constructEvent(rawBody, sig, whsec)` against `express.raw`), Checkout Session `payment_method_types` including `twint`, off-session/SCA flags (`setup_future_usage: 'off_session'`, `off_session: true`); cached `.website-builder/library/docs/stripe.md`
  - Stripe TWINT — https://docs.stripe.com/payments/twint — CHF-only, 5,000.00 CHF max, merchant-onboarding prerequisites (operational public site, legal name/address/contact, CH shipping for physical goods, CHF pricing), refunds to 180 days, disputes 25-50/1M, payment_method_type `twint`, supported in Checkout/Payment Links/Elements/Subscriptions/Invoicing (NOT Express Checkout Element). Confirmed 2026-05-18.
  - Stripe SCA — https://docs.stripe.com/strong-customer-authentication — EEA mandatory since 2019-09-14, UK since 2021-09-14, Checkout handles SCA automatically, off-session/Setup-Intent flags, grandfathered cards (EU pre-2020-12-31, UK pre-2021-09-14), liability shift to issuer, legacy Charges API unsupported. Confirmed 2026-05-18.
- **Locked decisions 54 + 26** (MVP = Stripe; Swiss audience → TWINT-via-Stripe default) — STATE doc: `Workstreams/website-builder/website-builder.md`

Freshness date for this contract: **2026-05-18**. The agent re-validates the Stripe TWINT + SCA surface via WebFetch/context7 at session start when phase 24b is active.
