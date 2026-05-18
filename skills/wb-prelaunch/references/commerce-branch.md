# Reference — Commerce branch (phases 24a / 24b / 24c)

> Loaded when `transactional: true` and the agent is in phase 24a, 24b, or 24c. The substantive recipes live in the design docs and phase contracts cited per section — read those **in full** before standing commerce up. This file is the cross-phase map: which recipe applies, the non-negotiables, the schemas.

The chain is linear: `24 → 24a → 24b → 24c → 25`. The agent never advances with a sub-phase half-stood-up.

**Commerce secrets handling (read before 24a/24b):** `Workstreams/website-builder/cross-cutting/DESIGN-secrets-and-keys.md` § The hybrid mechanism + § Provider key configuration UX. `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` / `CALCOM_API_KEY` are registered in `.website-builder/keys.yaml` as **references only** (`source: env` → `.env`; `source: onepassword` → `op://` ref); the actual secret lives in `.env` (gitignored, muggle default) or 1Password (opt-in), never committed. `STRIPE_PUBLISHABLE_KEY` is *not* a secret (designed for client code) but still flows through the env mechanism for uniformity. Code reads `process.env.{KEY}` — uniform regardless of source. Test keys (`sk_test_*`/`pk_test_*`) local; live keys (`sk_live_*`/`pk_live_*`) flipped only at phase 29 with explicit confirmation and environment-specific separation. Never log a secret, never inline one, never the same key both environments.

---

## Phase 24a — Commerce platform setup

**Read in full first:** `Workstreams/website-builder/commerce/DESIGN-commerce-stripe-checkout.md` (payments path) and/or `Workstreams/website-builder/commerce/DESIGN-booking-calcom.md` (bookings path), plus the contract `phase-contracts/24a-commerce-platform.md`.

### Pick the MVP platform from `project.yaml.transactional_kind`

| `transactional_kind` | Platform | Why |
|---|---|---|
| `payments` | **Stripe Checkout** | Payment-only: a hosted page / Payment Link. The cheapest way to take money when the site needs no browse/search/filter storefront. |
| `bookings` | **Cal.com** | Scheduling-as-a-platform: event types, availability, calendar/video integrations, optional payment-at-booking via Stripe. |
| `both` | Both | Stripe Checkout for products, Cal.com for bookings; each gets its own test rehearsal. |

MVP scope is locked by **decision 54**: only these two are first-class. The nine expansion platforms (Shopify, Lemon Squeezy, Snipcart, Paddle, Gumroad, Sellfy, Saleor, WooCommerce, Shopify Hydrogen) are named-as-expansion-paths only — one or two sentences each, steer the MVP user to Stripe Checkout / Cal.com. If the user insists on one of the nine for v1: write `.website-builder/decisions/commerce-platform-expansion-{platform}.md`, surface the "design exists, MVP runtime adapter not yet shipped" support level, and proceed only with explicit acceptance of degraded support OR route to Stripe Checkout / Cal.com with an intent-to-migrate note. Never pretend MVP support exists when it does not.

### Stripe Checkout — the three modes

1. **Stripe Payment Links** — no API code. Agent creates a link (Dashboard or `payment_links` API) and embeds it as an `<a href>` button. The muggle default; simplest for one-time / single-product.
2. **Stripe Checkout (server-side Session)** — agent generates a stack-appropriate endpoint creating a `Checkout Session` per checkout (`mode: 'payment'` one-time, `mode: 'subscription'` recurring) with `success_url` (carry `{CHECKOUT_SESSION_ID}`) + `cancel_url`, plus a signature-verifying webhook handler. The flexible path: dynamic pricing, line items, discounts, metadata.
3. **Stripe Elements + Payment Intents** — fully custom in-site checkout. Out of MVP scope; if a user genuinely needs it, log the decision and treat as a custom integration beyond the recipe.

Stack-pairing default: Framer / WordPress / static-HTML lean Payment Links; Next.js leans the server-side Session endpoint. Auth: `sk_test_*` for all rehearsal, `pk_test_*` client, `whsec_*` webhook; flip to `sk_live_*`/`pk_live_*` only at phase 29 with explicit user confirmation and environment-specific separation — never the same key both places. Costs (surface transparently — muggles care): processor-only, no monthly fee; ~2.9% + 30¢ US, ~1.5% + €0.25 EU cards, +1% cross-currency, $15/dispute; tax is the user's burden unless Stripe Tax (+0.5%) or an MoR expansion platform. The full auth table / CRUD vocabulary / 10-step phase-24a setup sequence is in `DESIGN-commerce-stripe-checkout.md`.

Current Stripe Checkout Session API surface (confirmed against Stripe docs 2026-05-18; the phase contracts also cite a verbatim context7 `/stripe/stripe-node` v19.1.0 fetch from 2026-05-18 — re-fetch if cached `.website-builder/library/docs/stripe.md` is >30 days old):

```
POST https://api.stripe.com/v1/checkout/sessions
  mode = payment | subscription          # subscription also for mixed recurring+one-time carts
  line_items[n][price] / [quantity]
  success_url (carry {CHECKOUT_SESSION_ID})  /  cancel_url
  payment_method_types[] = card, twint, ...  # or leave to Dashboard config
  metadata[...]
  # embedded variant: ui_mode=embedded_page + return_url (replaces success_url)
# Session expires in 24h by default (expires_at: 30 min–24 h)
# Webhook: checkout.session.completed (fulfillment) + checkout.session.expired (abandonment)
```

### Cal.com — bookings

Two deployment paths, surface both honestly with costs: **Cal.com Cloud** (Cal-hosted at `cal.com/{username}`; Free tier is generous — single-user, unlimited bookings, all core features $0/mo; Teams $15-19/user/mo) or **self-hosted** (open-source $0 + ~$5-50/mo hosting + real DevOps burden + AGPLv3 only matters if the user modifies-and-serves the source). Auth: `CALCOM_API_KEY` (`cal_live_xxx`) from Dashboard → Settings → Developer → API Keys. No official MCP — use REST API v2 at `https://api.cal.com/v2/` via `Bash`+`curl` (Bearer auth, rate limit 120/min):

```
GET    /v2/event-types                          # list
POST   /v2/event-types                          # create: title, slug, lengthInMinutes,
                                                 #   locations[{type}], price, currency, buffer
GET    /v2/bookings  /  DELETE /v2/bookings/{id}
GET    /v2/slots/available?startTime=&endTime=&eventTypeId=
# Webhooks: booking created/rescheduled/canceled + payment confirmation
# Embed: inline widget | popup | floating button | Cal.com Atoms (React, white-label, Next.js)
```

Create event types matching `project.yaml.services` (title, duration, location, price+currency, buffer, booking window), connect the user's calendar for availability + a video integration per event type, then embed. A **free** booking with no payment is still a phase-24a setup here (committing time on the site is transactional per the phase-11 decision-tree edge case) but phase 24b is light when no payment is involved. Paid bookings bridge to Stripe (default) or PayPal; **TWINT for Swiss paid bookings works only via Stripe, never PayPal** — ensure Stripe is the Cal.com payment app for Swiss booking sites. Enforce the payment-confirmation webhook so an unpaid hold never confirms as a booking. Full recipe in `DESIGN-booking-calcom.md`.

### Phase 24a non-overridable gates

- **No rehearsed test purchase/booking** → not done. Stripe: real Checkout Session driven with test card `4242 4242 4242 4242` to the success URL, success state observed. Cal.com: test booking on a *dedicated test calendar* (never the user's real calendar) or a test-mode Stripe payment confirming a paid booking.
- **Cal.com test booking would hit the user's real calendar** → refused (calendar pollution is real and embarrassing).
- **Webhook handler without signature verification** → refused (forged-event vulnerability).

Overridable (with logged cost): currency/region mismatch, expansion-platform choice. Phase-24a output: `.website-builder/commerce-config.yaml` (platform, mode, product/event-type list, key env-var *references*, webhook config, test-rehearsal evidence).

---

## Phase 24b — Payment provider wiring

**Read in full first:** `Workstreams/website-builder/commerce/DESIGN-payment-providers.md` (the per-audience decision tree, the comparison matrix, the TWINT-by-platform table, the Swiss pause-and-report rule) + contract `phase-contracts/24b-payment-provider.md`.

MVP provider is **Stripe** (decision 54). The four expansion providers (Mollie — EU/cheaper iDeal, no TWINT; PayPal — brand-trust, high in DE ~70%, no TWINT; Square — US/UK/AU/CA POS, no TWINT; Klarna — BNPL >$100 AOV, via Stripe) are named-only, added alongside Stripe only with a logged decision and their own test transactions.

### TWINT-via-Stripe — default for Switzerland (decision 26)

A Swiss-audience site (languages including `de`/`fr`/`it`/`rm`, or an explicit Swiss-audience statement) gets TWINT enabled by default — Switzerland's dominant mobile method (~3.5M+ users, ~35%+ of Swiss e-commerce). **Native via Stripe — no separate account, no aggregator, no extra keys.** Enable in Stripe Dashboard (Settings → Payment Methods → TWINT) or include `twint` in `payment_method_types` with `currency: chf`. Hard constraints (confirmed against Stripe TWINT docs 2026-05-18):

- **CHF-only.** Cannot process EUR/USD/any other currency. A Swiss-international site needs separate flows (CHF+TWINT for Swiss, cards-only for others). Enforce CHF-only TWINT in Session creation.
- **Maximum transaction amount 5,000.00 CHF.**
- **Non-recurring only** — TWINT does not support delayed/recurring payments.
- **Merchant-onboarding prerequisites Stripe enforces:** an operational, publicly accessible website (no password protection, no "coming soon"), displaying the legal business name + owner (full first+last for sole proprietors), complete business address, contact info; for physical goods, Switzerland a shipping destination and CHF pricing at checkout. The merchant must also obtain + verify the customer's mobile phone number and share it with Stripe on request. **These prerequisites are the same identity surface phase 25 (imprint) and phase 24c (Swiss VAT) produce — connect them so the user does not discover at launch that TWINT was blocked for a missing imprint.**

**Pause-and-report rule:** if the site has a Swiss audience but the chosen platform cannot do TWINT (expansion platforms Paddle/Gumroad/Sellfy/Snipcart, or a PayPal-only Cal.com), surface a critical decision point: switch to a Stripe-direct-compatible platform, OR accept the Swiss-revenue loss with explicit confirmation. Never silently launch a Swiss site without TWINT.

### SCA / 3DS — jurisdiction map (confirmed against Stripe SCA docs 2026-05-18)

SCA is a regulatory requirement, not a feature toggle. PSD2 has required it in the EEA since 2019-09-14; UK since 2021-09-14. Stripe Checkout / Billing / Payment Intents are SCA-ready and apply the 3DS challenge automatically when required — but **"automatic" is verified, not trusted**: run a 3DS-required regulatory test card against an EU-configured flow and confirm the challenge fires and the `requires_action` → completed path works.

| Customer region | SCA |
|---|---|
| EU / EEA | Mandatory (PSD2). Configure for SCA; do not rely on risk-based exemptions. |
| UK | Mandatory (equivalent enforcement; grandfathered cards pre-2021-09-14). Treat like EEA. |
| Swiss | Effectively required via Stripe (EU/EEA-acquired cards). Configure like EEA. TWINT is push-approval (own strong-auth property). |
| US | Not required (no PSD2 equivalent). Do not impose 3DS friction; keep Radar/dynamic-3DS for fraud-flagged. |

Off-session/subscription billing: set `setup_future_usage: 'off_session'` / `off_session: true` (or Setup Intents `usage: 'off_session'`); the **merchant-initiated-transaction consent** (explicit authorization, expected frequency, amount basis) is legally required for it — 24b wires the technical flag, **24c owns the disclosure copy**. Never generate legacy Charges-API code for an EU-audience site (no SCA support, high decline rates).

### Webhook signature verification — non-negotiable

Any handler that acts on `checkout.session.completed` (or the Cal.com payment confirmation) must verify the `stripe-signature` header against `STRIPE_WEBHOOK_SECRET` via `stripe.webhooks.constructEvent(rawBody, sig, whsec)` — against the **raw body** (`express.raw({ type: 'application/json' })`), never the parsed JSON — inside a try/catch, returning 400 on failure, acting only after verification passes. An order/booking marked fulfilled on an unverified webhook is a forged-event vulnerability the agent refuses to ship.

### Phase 24b non-overridable gates

- Swiss audience, no TWINT (when the platform *can* do TWINT) → refused (per decision 26; only the explicit-acceptance branch of the pause-and-report overrides).
- EU/EEA/UK/Swiss flow without the 3DS challenge verified firing → not deployable.
- Webhook handler without signature verification → refused.
- Test transactions not run per enabled method → "it should work" is not a pass.

Overridable (logged): regional-method gap, currency/method mismatch, dropping wallet methods instead of DNS-verifying the domain for Apple Pay / Google Pay. Output: `.website-builder/payment-config.yaml` (primary provider, enabled methods, currencies, regional overrides e.g. `CH: { primary: stripe }`, webhook config, SCA verification evidence, per-method test evidence).

---

## Phase 24c — Commerce-specific legal

Owns the legal surface that exists *only because money changes hands* (refund/returns/shipping, sale T&Cs, SCA disclosure, consumer-rights + tax). Phase 25 owns the surface every site needs regardless. The split is deliberate; state it to the user. Full jurisdiction detail (EU Consumer Rights Directive incl. the **2023/2673 withdrawal-button effective 19 June 2026**, the digital-supply-consent waiver, Swiss VAT, US nexus, UK consumer law) is in `references/jurisdiction-legal.md` — load it for this phase.

The discipline: **jurisdiction-correctness + truthfulness**. Extract the user's *actual* refund/returns/cancellation practice by conversation (`AskUserQuestion` is the core tool here) and refuse a copy-pasted policy that is a promise the user will break. Produce only the jurisdiction sections the user's actual regime requires (audience region + seller establishment — they can differ, both matter). Always record the not-a-lawyer disclaimer and recommend professional review for consequential commerce — while still producing the pages (a paid site with no policy is the worse failure).

### Phase 24c non-overridable gates

- Commerce flow without commerce-legal pages **in place + linked from checkout** ("by completing this purchase you agree to [Terms of Sale] / [Refund Policy]" at the point of payment, not just a footer link) → not deployable.
- Copy-pasted policy contradicting the user's actual practice → refused (an inaccurate policy is a liability, not a placeholder).
- SCA disclosure missing for an EU/Swiss off-session/subscription flow → not deployable.

Overridable only with an explicit decision doc recording the user taking professional responsibility. Output: commerce-legal pages live + checkout-linked, and `.website-builder/audit/COMMERCE-LEGAL-REPORT.md` which **explicitly lists the phase-25 dependencies** (general T&Cs / privacy / imprint / cookie-consent the commerce flow also leans on) so phase 25 inherits them.

---

## Mid-project transactional change (decision 34)

If a non-transactional user adds commerce at phase N (post-11): treated as a structural pivot, not additive. Re-run phases 12 (CMS may need to change), 22 (forms now need payment), 24a/b/c from scratch. Log in `.website-builder/decisions/transactional-change-{ts}.md`. For Stripe Checkout this is light; for full commerce, heavier. If an already-transactional user only adds a provider (e.g., TWINT after launching Stripe-only): partial 24b — add to `payment-config.yaml`, update flows, new test transactions, no full restart. Switching providers (Stripe → Mollie): full 24b restart incl. customer migration, surfaced cost, cutover-with-rollback.

## Phase 6.5 ingestion (existing commerce)

When `entry_mode = has-existing-site` and the site already uses Stripe Checkout / Cal.com: connect via the user-supplied key (Restricted Key for read-only where possible), list existing Products+Prices / Payment Links / event types → seed `commerce-config.yaml`, identify enabled payment methods → seed `payment-config.yaml`, flag obvious gaps (e.g., a Swiss site without TWINT), log in `decisions/ingest-{ts}.md`.

## External research surfaces for the commerce branch (cite in the audit reports)

- context7 `/stripe/stripe-node` — Checkout Session API, `webhooks.constructEvent` (raw-body signature verification), `payment_method_types` incl. `twint`, SCA `off_session`/`setup_future_usage`. Cache `.website-builder/library/docs/stripe.md`; re-fetch if >30 days.
- `https://docs.stripe.com/payments/twint` — TWINT CHF-only, 5,000 CHF max, non-recurring, merchant prerequisites.
- `https://docs.stripe.com/strong-customer-authentication` — SCA/3DS2, EEA/UK regions, automatic Checkout handling, off-session flags.
- `https://cal.com/docs/api-reference` — Cal.com API v2, event-types/bookings/slots, Atoms React components.
- 24c jurisdiction sources — see `references/jurisdiction-legal.md`.
