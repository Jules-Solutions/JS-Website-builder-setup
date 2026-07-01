---
phase: "24a"
name: Commerce platform setup
group: pre-launch
pipeline_section: pre-launch
skill: wb-prelaunch
prev_phase: 24
next_phase: "24b"
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - DESIGN-phase-contracts.md
  - DESIGN-architecture.md
  - DESIGN-commerce-stripe-checkout.md
  - DESIGN-booking-calcom.md
  - DESIGN-payment-providers.md
  - DESIGN-secrets-and-keys.md
---

# Phase 24a — Commerce platform setup *(only if `project.yaml.transactional` = true)*

> Stand up the thing that takes money or books time. For the MVP this is Stripe Checkout (general commerce — sell a course, a consult, a digital download, a one-time fee) or Cal.com (paid bookings — a consultation, a coaching slot, a workshop). The phase where a non-commerce site becomes a business. The agent refuses to claim the site is commerce-ready without a real test purchase rehearsed end-to-end in test mode. Nine other commerce platforms exist in the full design surface and are named here as expansion paths, but per locked decision 54 the MVP is Stripe Checkout + Cal.com — full prose for those two, a brief expansion block for the rest.

## Mission

This phase only runs when phase 11 set `project.yaml.transactional = true`. Phase 24 forked here. The site is built, integrated, and now it has to actually take money (or commit time that needs payment rails). Phase 24a sets up the commerce *platform* — the account, the products/SKUs/services, the catalogue, the integration into the site's chosen stack. Phase 24b (next) wires the *payment provider* underneath it; phase 24c handles the *commerce-specific legal*. The three sub-phases are a linear chain — 24 → 24a → 24b → 24c → 25 — and the agent refuses to let the user advance with the platform half-stood-up.

The MVP scope is locked by **decision 54**: two primary commerce platforms get full first-class support — **Stripe Checkout** for general payment (the "sell a thing without a storefront" path) and **Cal.com** for bookings (the "commit time, possibly paid" path). These are the two the agent stands up with real recipes, real test rehearsals, real config. The other nine platforms in the design surface (Shopify, Lemon Squeezy, Snipcart, Paddle, Gumroad, Sellfy, Saleor, WooCommerce, Shopify Hydrogen) are real, fully designed, and accessible to users who already know them — but they ship in expansion phase 10 of the platform roadmap. The agent names them as expansion paths (one or two sentences each) and steers the MVP user toward Stripe Checkout or Cal.com, logging an explicit expansion-platform decision if the user insists on one of the nine.

The agent picks the right MVP platform from the *kind* of transaction `project.yaml.transactional_kind` records:

- **`payments`** (sell a product/course/download/one-time fee, no calendar) → **Stripe Checkout**. Stripe Checkout is payment-only: a hosted payment page or Payment Link, the cheapest and simplest way to take money when the site does not need a browse/search/filter storefront.
- **`bookings`** (a consultation/coaching/workshop slot, possibly paid) → **Cal.com**. Cal.com is scheduling-as-a-platform: event types, availability, calendar + video integrations, optional payment collection at booking time via Stripe.
- **`both`** → both platforms stood up, Stripe Checkout for the products, Cal.com for the bookings, each with its own test rehearsal.

The hard gate of this phase: **no commerce-ready claim without a rehearsed test purchase.** Test mode where the provider offers it (Stripe test cards; Cal.com test bookings). A site that "should be able to take payment" has not been verified; it has been hoped. The agent runs the checkout (or booking) flow end-to-end, in test mode, and watches the success state arrive before it writes `commerce-config.yaml` as complete.

## Entry conditions

- Phase 24 (non-commerce integrations) complete. `.website-builder/audit/INTEGRATIONS-REPORT.md` is green; the non-commerce connective tissue is wired before commerce stacks on top.
- `.website-builder/project.yaml.transactional` = `true` (phase 11). If it is `false`, this contract does not fire — the pipeline went 24 → 25.
- `.website-builder/project.yaml.transactional_kind` is set (`payments` | `bookings` | `both`) — phase 11's follow-up captured this; it drives which MVP platform stands up.
- `.website-builder/project.yaml.stack` (phase 11) is known — the integration mode depends on it (Stripe Payment Link button vs server-side Checkout Session endpoint; Cal.com embed vs Cal.com Atoms React components).
- `.website-builder/keys.yaml` exists; commerce secrets (`STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `CALCOM_API_KEY`) are registered as references per `DESIGN-secrets-and-keys.md` (secrets in `.env`/1Password, never committed). The publishable key (`STRIPE_PUBLISHABLE_KEY`) is *not* a secret — it is designed for client code — but still flows through the env mechanism for uniformity.

## What Claude must establish

A live commerce platform, configured for the user's actual products/services, integrated into the site's stack, with a rehearsed test purchase or booking. The work product:

1. **Platform account + catalogue.** The Stripe account exists and is activated (business info, bank account, identity verification — required before live mode); or the Cal.com account exists (Cloud free/Teams tier or self-hosted). The user's actual products/prices (Stripe Products + Prices, in the right currency) or event types (Cal.com event types with duration, location, price, buffer) are created — typically 1-5 for the MVP-shaped sites this serves.
2. **Stack integration.** The commerce surface is wired into the site per the chosen stack: a Stripe Payment Link as an `<a href>` button (Mode 1, muggle-simplest), or a server-side Checkout Session endpoint + client redirect (Mode 2, dynamic pricing/metadata), or a Cal.com inline/popup/floating embed, or Cal.com Atoms React components for a white-label booking flow on Next.js.
3. **Rehearsed test purchase/booking.** End-to-end, in test mode: Stripe test card `4242 4242 4242 4242` through a real Checkout Session to the success URL; or a Cal.com test booking landing on a dedicated test calendar (never the user's real calendar). The agent watched the success state arrive.
4. **`.website-builder/commerce-config.yaml`** recording: chosen platform, mode, product/event-type list, key env-var names (references, not values), webhook configuration, the test-rehearsal evidence.

The agent updates `.website-builder/project.yaml.current_phase` to `24b` (payment provider wiring) upon completion. The chain is linear here — 24a always advances to 24b.

## MVP commerce platforms (full prose — locked decision 54)

### Stripe Checkout (general payment)

Stripe Checkout is a **hosted payment page**. Stripe hosts the actual checkout form — card, Apple Pay, Google Pay, TWINT, regional methods — and the user's site either redirects to it (server-side Checkout Session) or links to it (Payment Link). It is **payment-only**: the cheapest, simplest way to take money on the web when the site does not need product browsing, search, filtering, or inventory infrastructure. The right answer for "Buy this course" on a landing page, "Order this service" on a portfolio, a one-time consulting fee from a contact form, a paid digital download. The wrong answer for a catalogue store with browse/search/filter — that routes to an expansion platform (Shopify / Snipcart / Saleor).

Three modes the agent picks from at this phase:

1. **Stripe Payment Links** — no API code. The user (guided by the agent) creates a link in the Stripe Dashboard or the agent creates it via the `payment_links` API; the agent embeds it as a button. Simplest path for one-time / single-product sales. The muggle default.
2. **Stripe Checkout (server-side Session)** — the agent generates a stack-appropriate server endpoint that creates a `Checkout Session` per checkout (`mode: 'payment'` for one-time, `mode: 'subscription'` for recurring), with `success_url` (carrying `{CHECKOUT_SESSION_ID}` for confirmation) and `cancel_url`, plus a webhook handler that verifies the `stripe-signature` header against `STRIPE_WEBHOOK_SECRET` before trusting `checkout.session.completed`. The flexible path: dynamic pricing, line items, discounts, metadata, customer email.
3. **Stripe Elements + Payment Intents** — fully custom in-site checkout. Most flexible, most complex; out of MVP scope for this phase — if a user genuinely needs it, the agent logs the decision and treats it as a custom integration beyond the recipe.

Modes 1 and 2 are the MVP paths — Mode 1 for muggles, Mode 2 for users with custom logic. The agent's stack-pairing recipe: Framer/WordPress/static-HTML lean Payment Links; Next.js leans the server-side Session endpoint (the classic SaaS-marketing-site path). Auth model: `sk_test_*` for all rehearsal, `pk_test_*` for the client, `whsec_*` for webhook verification — the agent flips to `sk_live_*`/`pk_live_*` only after explicit user confirmation at deploy (phase 29). Costs are surfaced transparently (muggles care intensely): processor-only, no monthly fee ever — ~2.9% + 30¢ US, ~1.5% + €0.25 EU cards, +1% cross-currency, $15/dispute, tax is the user's burden unless Stripe Tax (+0.5%) is enabled or the build routes to a Merchant-of-Record expansion platform. Full recipe — auth table, CRUD vocabulary, stack pairings, i18n, TWINT, the phase-24a 10-step setup sequence — in `commerce/DESIGN-commerce-stripe-checkout.md`. The agent reads it in full before standing Stripe up. context7 `/stripe/stripe-node` confirms the current Checkout Session API surface (the agent invokes it at this phase per the mandatory-tool list; current as of the 2026-05-18 fetch: `stripe.checkout.sessions.create({ mode, success_url, cancel_url, line_items, payment_method_types, metadata })` + `stripe.webhooks.constructEvent(body, sig, secret)` for verification).

### Cal.com (bookings)

Cal.com is **scheduling as a platform** — the open-source, self-hostable Calendly alternative (AGPLv3). Event types (a bookable service: 30-min consult, 1-hour coaching, 2-hour workshop) with availability rules, calendar integrations (Google / Microsoft 365 / Apple / CalDAV — read availability, write events), video integrations (Zoom / Google Meet / Teams / Daily — auto-generated links), payment integrations (Stripe default, PayPal alternative — collect payment when the booking is created), and embed options (inline widget, popup, floating button, or Cal.com Atoms React components for white-label). Cal.com fits when the user runs a service/consulting/coaching business with bookable appointments, values open-source/data-ownership, wants embedded booking (not just a link out), and may need payment at booking time.

Two deployment paths the agent helps pick: **Cal.com Cloud** (Cal-hosted at `cal.com/{username}`; Free tier is generous — single-user, unlimited bookings, all core features at $0/mo; Teams at $15-19/user/mo for round-robin/collective) or **self-hosted** (open-source, $0 software + variable hosting ~$5-50/mo Postgres+Node, real DevOps burden, AGPLv3 compliance only matters if the user modifies-and-serves the source). The agent surfaces both honestly with costs (muggles care). Auth: `CALCOM_API_KEY` (`cal_live_xxx`) from Dashboard → Settings → Developer → API Keys, registered per `DESIGN-secrets-and-keys.md`. The agent uses the REST API v2 (`https://api.cal.com/v2/`) to create event types matching `project.yaml.services` — title, duration, location, price+currency, buffer, booking window — connects the user's calendar for availability and a video integration per event type, then embeds Cal.com on the site (inline event-type page, popup "Book a call" button, floating CTA, or Cal.com Atoms on Next.js). Crucial line: a *free* booking with no payment is still a phase-24a setup here (per the phase-11 decision-tree edge case — committing time on the site is transactional even with no money), but phase 24b is light when no payment is involved. Paid bookings bridge to Stripe (default) or PayPal; Cal.com does not process payment itself — it triggers the payment flow at booking creation and confirms the booking only after payment success (the agent enforces the payment-confirmation webhook so an unpaid hold never confirms). TWINT for Swiss paid bookings works only via Stripe (not PayPal) — flagged at 24b. Full recipe — auth, CRUD vocabulary, the phase-24a booking-branch setup sequence, calendar/video/payment wiring — in `commerce/DESIGN-booking-calcom.md`. The agent reads it in full before standing Cal.com up; context7 `/calcom/cal.com` confirms the current API + embed shape.

## Expansion commerce platforms (post-MVP, expansion phase 10 — brief mention)

Fully designed in the website-builder workstream (vault-side; not shipped as MVP adapters), accessible to users who already know them, **not first-class in the MVP** (per decision 54). The agent names these only when the user asks or when Stripe Checkout / Cal.com is clearly the wrong fit, and logs an explicit expansion decision before proceeding with degraded (design-exists-runtime-adapter-later) support:

- **Shopify** — full storefront: catalogue, browse, search, inventory, shipping. The answer when the user needs a real store, not a buy-button. MVP substitute: none (Stripe Checkout is payment-only).
- **Lemon Squeezy** — Merchant-of-Record for digital products; offloads sales-tax/VAT compliance. MVP substitute: Stripe Checkout + Stripe Tax (compliance stays the user's burden).
- **Snipcart** — drop-in cart for static sites; HTML-attribute-driven. MVP substitute: Stripe Checkout (no cart UX).
- **Paddle** — Merchant-of-Record for SaaS/digital; subscription-heavy. No TWINT. MVP substitute: Stripe Checkout subscription mode.
- **Gumroad** — creator-first single-product sales with built-in audience. No TWINT. MVP substitute: Stripe Payment Links.
- **Sellfy** — creator storefront for digital + print-on-demand. No TWINT. MVP substitute: Stripe Checkout.
- **Saleor** — headless GraphQL commerce for engineering-heavy builds. MVP substitute: Stripe Checkout for simple cases.
- **WooCommerce** — WordPress-native full store via the WooCommerce plugin (TWINT via the Stripe Gateway plugin). The natural commerce path *only* when the stack is already WordPress. MVP substitute: Stripe Checkout embedded.
- **Shopify Hydrogen** — Shopify's React/Remix headless storefront framework. MVP substitute: Shopify (expansion) or Stripe Checkout for non-catalogue.

If the user insists on one of the nine for v1, the agent writes `.website-builder/decisions/commerce-platform-expansion-{platform}.md`, surfaces the "design exists, MVP runtime adapter not yet shipped" support level, and either proceeds with the user's explicit acceptance of degraded support or routes to Stripe Checkout / Cal.com with an intent-to-migrate note. The agent does not pretend MVP support exists when it does not.

## Gating rules

The agent refuses to advance when:

- **No rehearsed test purchase / test booking.** The defining gate. Stripe: a real Checkout Session driven with test card `4242 4242 4242 4242` to the success URL, the success state observed. Cal.com: a test booking landing on a dedicated test calendar (free) or a test-mode Stripe payment confirming a paid booking. "It should work" is not a pass; the observed success state is. **Not overridable** — a launched commerce site that has never had a successful test transaction is the exact failure this phase exists to prevent.
- **Currency / region mismatch.** Products priced in USD for a Swiss-audience site that should be CHF (and will need TWINT, which is CHF-only — flagged here, wired in 24b). The agent enforces a checkout-flow rehearsal in the audience's actual currency and surfaces the mismatch before it advances.
- **Expansion platform chosen without explicit acceptance.** If the user picks one of the nine expansion platforms for v1, the agent refuses to silently proceed — it writes the expansion decision doc, surfaces the degraded-support level, and requires explicit user confirmation.
- **Stripe account not activated for live (when launch is imminent).** Test mode works without activation; live mode requires business info + bank + identity verification. The agent does not block phase 24a for this (rehearsal is test-mode), but it records the activation requirement as a phase-29 deploy dependency and surfaces it so live launch does not fail at the last step.
- **Cal.com test booking would hit the user's real calendar.** The agent refuses to rehearse against the production calendar — it uses Cal.com test mode + a dedicated test calendar so the rehearsal does not pollute the user's real schedule. Not overridable; calendar pollution is a real, embarrassing failure.
- **Webhook handler without signature verification.** Any generated Stripe webhook handler that trusts `checkout.session.completed` without verifying the `stripe-signature` header is refused — the agent will not ship a handler that accepts unverified webhooks (a forged-event vulnerability). The same applies to the Cal.com payment-confirmation webhook.

Override is available on the expansion-platform and currency-mismatch gates via explicit user confirmation with the cost logged. The test-purchase, real-calendar-pollution, and webhook-verification gates are not overridable.

## Tools and skills used

- **Stripe MCP** (official, the canonical-tool-first path) — for Stripe account/product/price/Checkout-Session/Payment-Link configuration and the test-mode rehearsal. Falls back to direct REST API (`https://api.stripe.com/v1/`) via `Bash` + `curl` when the MCP cannot do a specific operation.
- **`mcp__context7__resolve-library-id` + `mcp__context7__query-docs`** — **mandatory at this phase** for `/stripe/stripe-node` (current Checkout Session + webhook-verification API surface; Stripe's API evolves). The agent caches the result to `.website-builder/library/docs/stripe.md` and cites it in `## Reference materials`.
- **`WebFetch`** — **mandatory at this phase** for the current Cal.com developer docs (`https://cal.com/docs/api-reference` or current canonical) — Cal.com's API v2 + embed surface, confirmed fresh. Cited in `## Reference materials`.
- **Cal.com REST API v2** via `Bash` + `curl` (no official Cal.com MCP) — event-type creation, availability/calendar/video wiring, test booking.
- **`Edit` / `Write`** — to write the commerce client code into the user's project (Payment Link button, server-side Session endpoint + webhook handler, Cal.com embed/Atoms) per the chosen stack's convention. Secrets referenced via env vars, never inlined.
- **`Playwright` MCP** — the test-rehearsal workhorse: drive the real checkout/booking flow, observe the success state, confirm the redirect/confirmation.
- **`AskUserQuestion`** — for the steps only the user can do (Stripe Dashboard signup + activation, Cal.com signup, calendar connection, the products/services the user actually sells). The agent walks them through it per `DESIGN-secrets-and-keys.md`'s provider-key UX.
- **`Read`** — `commerce/DESIGN-commerce-stripe-checkout.md` and `commerce/DESIGN-booking-calcom.md` **in full** (the recipes), `project.yaml.transactional_kind` + `.stack` + `.services`, `keys.yaml`.

No subagent spawn. The `wb-prelaunch` phase-group skill carries the commerce branch (per Decision 64, commerce folds into `wb-prelaunch` — there is no separate commerce skill); the cross-phase contract is that 24a's platform, 24b's payment provider, and 24c's commerce-legal compose into one working transactional flow.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/commerce-config.yaml` | Chosen platform, mode, product/event-type list, key env-var names (references), webhook config, test-rehearsal evidence | The commerce platform's configuration record; read by phase 24b (payment provider), 24c (commerce legal), 29 (deploy), and the post-launch maintainer |
| Commerce client code in the user's project | Per stack convention | The actual Payment Link button / Checkout Session endpoint + webhook handler / Cal.com embed or Atoms — live code |
| `.website-builder/keys.yaml` (updated) | References only, per `DESIGN-secrets-and-keys.md` | `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` / `CALCOM_API_KEY` registered; `STRIPE_PUBLISHABLE_KEY` registered (not secret, but uniform) |
| `.website-builder/library/docs/stripe.md` | Cached context7 output | Stripe API surface frozen at this phase; re-fetched if >30 days stale at a later phase |
| `.website-builder/decisions/commerce-platform-expansion-{platform}.md` *(when applicable)* | Standard decision-doc frontmatter + body | Created only when the user chose one of the nine expansion platforms for v1 with explicit acceptance of degraded support |

The `commerce-config.yaml` with embedded test-rehearsal evidence is the required artifact.

## Common failure modes

**The user picks Stripe Checkout when they actually need a catalogue.** Five products, browse, filter, inventory — that is a storefront, and Stripe Checkout is payment-only. The agent's decision screen ("more than ~5 products with browse/filter?") catches this and routes to an expansion platform (Shopify/Snipcart/Saleor) with the expansion-decision logged, rather than bolting a buy-button onto what should be a store.

**"It's set up, it should take payment."** Set-up ≠ verified. The agent has, in this exact session, seen "the Stripe code is written" treated as "commerce works" — the test-purchase gate exists because writing the integration and successfully running a test transaction through it are different facts. The agent runs the Stripe test card to the success URL (or the Cal.com test booking to a confirmed slot) and observes the success state before `commerce-config.yaml` is marked complete.

**Test bookings land on the user's real calendar.** The agent rehearses Cal.com against the production Google/Microsoft calendar and now there are three fake "test consultation" events on the user's actual schedule. The agent uses Cal.com test mode + a dedicated test calendar; real-calendar pollution is a non-overridable gate.

**The user forgets to verify the domain for Apple Pay / Google Pay.** Stripe wallet methods need DNS-based domain verification. The agent makes domain verification part of the phase-24a Stripe setup checklist so the wallet options actually appear at checkout, not just "should appear."

**Test-mode keys ship to production.** The agent flips to live keys only at phase 29 with explicit user confirmation and environment-specific separation (`sk_test_*` local, `sk_live_*` prod-only) — never silently, never the same key both places.

**The user assumes Stripe handles their VAT.** Stripe is a processor, not a Merchant of Record — sales tax / VAT compliance is the user's burden unless Stripe Tax (+0.5%) is enabled or the build uses an MoR expansion platform (Lemon Squeezy / Paddle). The agent surfaces this clearly at 24a and hands the detailed jurisdiction work to phase 24c (commerce legal) — it is flagged here, fully addressed there.

**TWINT not enabled for a Swiss audience.** Per decision 26, a Swiss-audience site needs TWINT (~35%+ of Swiss e-commerce). The agent flags the TWINT requirement at 24a (currency must be CHF; TWINT is CHF-only) and wires it at 24b. If the chosen platform cannot do TWINT (the expansion platforms Paddle/Gumroad/Sellfy/Snipcart cannot), the agent fires the pause-and-report from `DESIGN-payment-providers.md`: switch to a Stripe-direct-compatible platform or accept the Swiss-revenue loss with explicit confirmation.

**Cal.com booking confirms before payment.** A paid booking is held but the payment never completed, yet the slot shows confirmed. The agent enforces the payment-confirmation webhook so a Cal.com booking is only confirmed *after* Stripe reports payment success — an unpaid hold never becomes a confirmed appointment.

**The agent stands up commerce on a non-transactional site.** This contract only fires when `transactional: true`. If the agent reaches here on a `false`-flag project, the pipeline routing is broken — the agent stops and surfaces the routing error rather than building commerce nobody asked for.

## Reference materials

- **Design doc — Stripe Checkout (full recipe, read in full before standing up):** `DESIGN-commerce-stripe-checkout.md` — mental model, auth table, CRUD vocabulary, costs, stack pairings, i18n, TWINT section, the phase-24a 10-step setup sequence, limitations, failure modes
- **Design doc — Cal.com booking (full recipe, read in full before standing up):** `DESIGN-booking-calcom.md` — mental model, Cloud-vs-self-hosted, auth, CRUD vocabulary, costs, the phase-24a booking-branch sequence, TWINT-via-Stripe-only caveat, failure modes
- **Design doc — payment-provider matrix (24b's source, TWINT-by-platform table):** `DESIGN-payment-providers.md` — the decision tree, the commerce-platform-TWINT-support table, the Swiss pause-and-report rule
- **Design doc — phase pipeline source:** `DESIGN-phase-contracts.md` § 24a (seed) + the 24→24a→24b→24c chain
- **Design doc — key handling:** `DESIGN-secrets-and-keys.md` § Provider key configuration UX + § Phase contracts (24a listed)
- **Phase 11 transactional decision (why this phase fired):** `phase-contracts/11-stack-decision.md` § Transactional decision + the donations/free-booking/paid-membership edge cases + decision-34 mid-project-change cost
- **External research (loaded fresh 2026-05-18 for this contract):**
  - context7 `/stripe/stripe-node` v19.1.0 (High reputation, benchmark 74.21) — `stripe.checkout.sessions.create({ mode: 'payment'|'subscription', success_url, cancel_url, line_items, payment_method_types, metadata })`; webhook verification via `stripe.webhooks.constructEvent(rawBody, stripe-signature, whsec)`; cached to `.website-builder/library/docs/stripe.md`
  - Cal.com developer docs — https://cal.com/docs/api-reference (API v2 at `https://api.cal.com/v2/`; event-types, bookings, slots/available, webhooks; Cal.com Atoms React components for white-label) — confirmed current 2026-05-18
  - Stripe Checkout: https://docs.stripe.com/payments/checkout · Payment Links: https://docs.stripe.com/payments/payment-links · API: https://docs.stripe.com/api
  - Cal.com: https://cal.com · self-hosting: https://cal.com/docs/self-hosting · GitHub: https://github.com/calcom/cal.com
- **Locked decision 54** (MVP commerce = Stripe Checkout + Cal.com) — STATE doc: `website-builder.md`

Freshness date for this contract: **2026-05-18**. The agent re-validates the Stripe + Cal.com API surface via context7/WebFetch at session start when phase 24a is active and re-fetches if the cached docs are >30 days old.
