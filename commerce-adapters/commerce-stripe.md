# Commerce adapter — Stripe Checkout + Stripe payment-provider

> The canonical commerce adapter for payment-only sites: a "Buy this course" button, a single-product landing page, a one-time consulting fee on a contact form. Stripe Checkout is **payment-only** — the cheapest, simplest way to take money on the web when the user doesn't need product browsing infrastructure. For catalog-style stores, route to Shopify / Lemon Squeezy / Snipcart / Saleor (Phase 10+ adapters).
>
> This file combines two concerns the Captain 0 prep packet kept together (BOARD line 39 single-file decision): the Stripe Checkout / Payment Links commerce-platform surface AND Stripe as a payment provider. They share the same auth, the same MCP, the same dashboard, and the same TWINT integration — splitting them would force every reader to chase a cross-link instead of reading one self-contained adapter.

## Mental model

### Identity

- **Platform name:** Stripe (Stripe Checkout / Payment Links / Elements + Payment Intents)
- **Version surface:** Stripe API uses date-versioned snapshots (e.g., `2025-04-30`); SDKs surface `apiVersion` parameter. Stripe Checkout itself is a hosted page — versionless from the user's perspective.
- **Canonical context7 IDs:**
  - `/websites/stripe_js` — Stripe.js + Checkout primary reference (benchmark 71.4, 5,937 code snippets; verified 2026-05-20)
  - `/stripe/stripe-node` — Server-side Node SDK (benchmark 73.97; verified 2026-05-20)
  - `/stripe/stripe-python` — Server-side Python SDK (benchmark 68.4; verified 2026-05-20)
- **Freshness-check requirement:** agent invokes `resolve-library-id` for `/websites/stripe_js` at phase 24a entry; if cached docs in `.website-builder/library/docs/stripe-*.md` are >30 days old or the current Stripe API version surface has shifted (check `https://docs.stripe.com/upgrades` for the latest version pin), re-fetch before generating the checkout code.

> **Naming note:** the source design doc (`DESIGN-commerce-stripe-checkout.md` line 95 + `DESIGN-payment-providers.md` line 110) refers to context7 ID `/stripe/stripe-docs`. As of 2026-05-20 re-verification, that ID is no longer indexed — the canonical Stripe references on context7 are now the IDs above. The shift is library-side recomposition, not an API change; agent updates the cache and proceeds.

Stripe Checkout is a **hosted payment page** — Stripe hosts the actual checkout form (card, Apple Pay, Google Pay, regional methods like TWINT/iDeal/Bancontact/SEPA) and the user's site redirects to it for payment. Payment Links are a no-code variant: a URL Stripe generates which embeds Checkout — the user shares the link via email / social / button on their site, and customers pay through it.

Three modes the website-builder picks from at phase 24a:

1. **Stripe Payment Links** — no API code needed. User creates a link in Stripe Dashboard; agent embeds the link as a button on the user's site. Simplest path for one-time payments / single-product sales. Default for muggles.
2. **Stripe Checkout (server-side session)** — agent creates a `Checkout Session` via API (one Session per checkout instance), redirects user to it, handles success/cancel callbacks. More flexible: dynamic pricing, per-customer customization, line items, discounts, metadata, subscriptions.
3. **Stripe Elements + Payment Intents** — fully custom checkout in user's site. Most flexible, most complex. Out of scope for this adapter; if the user needs this, route to a custom integration design.

For the website-builder, Modes 1 and 2 are the primary paths. Mode 1 for muggles, Mode 2 for users with custom logic. Mode 3 is escape hatch.

## Auth model

Stripe auth is canonical and stable. All secrets via `secrets-conventions.md` — env-var indirection only; no literal secrets in committed files; 1Password is the SSOT.

| Auth method | Used for | Key shape | Env var | 1Password reference |
|---|---|---|---|---|
| **Secret key** | Server-side API calls | `sk_live_xxx` / `sk_test_xxx` | `STRIPE_SECRET_KEY` (live), `STRIPE_TEST_SECRET_KEY` (test) | `op://shared/stripe/secret-key` |
| **Publishable key** | Frontend (Stripe.js, redirects) | `pk_live_xxx` / `pk_test_xxx` | `STRIPE_PUBLISHABLE_KEY` (live), `STRIPE_TEST_PUBLISHABLE_KEY` (test) | `op://shared/stripe/publishable-key` |
| **Webhook signing secret** | Verifying webhook authenticity | `whsec_xxx` | `STRIPE_WEBHOOK_SECRET` | `op://shared/stripe/webhook-secret` |
| **Restricted keys (RAK)** | Scoped server-side calls (optional production hardening) | `rk_live_xxx` / `rk_test_xxx` | per-purpose env var | `op://shared/stripe/rak-<purpose>` |

**Test vs live discipline:** agent uses `sk_test_*` / `pk_test_*` for ALL rehearsal at phase 24a. Live keys (`sk_live_*` / `pk_live_*`) flip only after explicit user confirmation at deploy time + key-pattern check (per `DESIGN-commerce-stripe-checkout.md` line 248). Test-mode keys deployed to production is one of the canonical failure modes — agent never makes this flip silently.

> Canonical `payment-config.yaml` schema — including the test_mode + test_keys_env fields — see [commerce-adapters/payment-config-schema.md](payment-config-schema.md).

## CRUD vocabulary

Stripe's API is REST-y JSON (legacy form-encoded support remains). Minimal request samples:

```bash
# Create a product
POST https://api.stripe.com/v1/products
  -d name="My Course"
  -d description="Six-week cohort on..."

# Create a price for that product (CHF in minor units — 4900 = CHF 49.00)
POST https://api.stripe.com/v1/prices
  -d product=PROD_ID
  -d unit_amount=4900
  -d currency=chf

# Create a Checkout Session (mode = payment, one-time, CHF + TWINT)
POST https://api.stripe.com/v1/checkout/sessions
  -d currency=chf
  -d "payment_method_types[]"=card
  -d "payment_method_types[]"=twint
  -d "line_items[0][price]"=PRICE_ID
  -d "line_items[0][quantity]"=1
  -d mode=payment
  -d success_url="https://example.com/success?sid={CHECKOUT_SESSION_ID}"
  -d cancel_url="https://example.com/cancel"

# Create a subscription Checkout Session
POST https://api.stripe.com/v1/checkout/sessions
  -d "line_items[0][price]"=PRICE_ID
  -d mode=subscription
  -d success_url="..."
  -d cancel_url="..."

# Create a Payment Link (no-code-friendly variant of Checkout)
POST https://api.stripe.com/v1/payment_links
  -d "line_items[0][price]"=PRICE_ID
  -d "line_items[0][quantity]"=1

# Retrieve a Session for success-page rendering
GET https://api.stripe.com/v1/checkout/sessions/SESSION_ID

# Issue a refund for a paid Session's payment_intent
POST https://api.stripe.com/v1/refunds
  -d payment_intent=PI_ID
  -d amount=4900    # optional; omit for full refund

# Construct + verify a webhook event (server-side handler — Stripe SDK)
event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
# raises SignatureVerificationError if invalid — refuse to ship handler that catches this
```

For Payment Links specifically, the user can also create them in the Stripe Dashboard UI without any API call — agent guides the user through that flow when no programmatic logic is needed.

> **Modern note (verified context7 2026-05-20):** Stripe's Custom Checkout (server-side Session + client-side confirm) supports an embedded confirm flow with `actions.confirm({...})` carrying return URL, payment method, address fields, and express-checkout event objects. Useful for users who want a server-managed Session with client-side fine-grained confirm semantics (e.g., embedded confirm on a Next.js Route Handler-backed page).

## API + MCP availability

| Surface | Type | Use | Captain L verification |
|---|---|---|---|
| **REST API v1** | JSON / form-encoded | Server-side ops (products, prices, sessions, refunds) | verified 2026-05-20 |
| **Webhooks** | HTTP callbacks | Payment events (`checkout.session.completed`, `payment_intent.succeeded`, `invoice.paid`, etc.) | verified 2026-05-20 |
| **Stripe.js** | Browser SDK | Redirect to Checkout, embed Elements, Express Checkout buttons | verified context7 `/websites/stripe_js` 2026-05-20 |
| **Server SDKs** | Node, Python, Ruby, PHP, Go, Java, .NET | Typed clients; agent generates code from these | verified context7 `/stripe/stripe-node` + `/stripe/stripe-python` 2026-05-20 |
| **Stripe CLI** | CLI | Webhook tunneling in dev (`stripe listen --forward-to localhost:3000/api/webhook`), log inspection, fixture replay | verified 2026-05-20 |
| **Stripe MCP** (`@stripe/mcp` / hosted) | MCP server | Stripe-published MCP for agent integrations | **verified — Anthropic plugin catalog (see below)** |
| **Stripe Workbench / Sigma** | Dashboard | SQL access to user's data; analytical queries | verified 2026-05-20 |

### Stripe MCP — official, blessed by Anthropic (confirmed Phase 3 finding)

The Stripe MCP is the agent's primary integration path at phase 24a/b/c. Re-verified 2026-05-20:

- **Anthropic plugin catalog entry:** `https://claude.com/plugins/stripe` — 27,078 installations as of 2026-05-20 (per `claude.com/plugins` catalog scan). Install command: `claude plugin install stripe@anthropic`. The plugin wraps `@stripe/mcp` and ships a `stripe-mcp` subagent that CC automatically delegates to for checkout / subscription / webhook patterns.
- **Direct MCP (without plugin wrapper):**
  - Local stdio via npx: `{"mcpServers": {"stripe": {"command": "npx", "args": ["-y", "@stripe/mcp@latest"], "env": {"STRIPE_SECRET_KEY": "<test-key>"}}}}`
  - Remote HTTP: `{"servers": {"stripe": {"type": "http", "url": "https://mcp.stripe.com"}}}` — OAuth-based; preferred for OAuth-managed teams.
- **Used by agent at:** phase **24a** (Checkout Session creation pattern + Payment Link generation + product/price creation + Stripe-recommended best practices), phase **24b** (payment-method enablement per audience incl. TWINT for CHF, webhook configuration, 3DS/SCA verification), phase **24c** (Stripe Tax wiring + receipt customization + subscription Customer Portal), post-launch (refund flows, subscription state changes, dispute response).
- **Fallback per `tool-dependency-discipline.md` Tier 2:** if Stripe MCP is not installed or fails, agent uses Stripe Node SDK + `docs.stripe.com` REST reference. Functional — loses the canonical-pattern surface (e.g., "create a TWINT-enabled subscription Checkout Session with metadata in one turn"); agent must compose from API reference manually.

### Other MCP ecosystem checks (negative/positive findings, 2026-05-20)

- **Stripe Workbench/Sigma MCP** — no separate MCP; Sigma access is through the Stripe Dashboard SQL UI or via direct API call to Workbench endpoints. Not yet exposed as MCP. Negative finding.
- **Stripe Tax MCP** — bundled into the main Stripe MCP (Tax operations are exposed alongside Checkout/Payment Intent operations); no separate Tax-specific MCP. Confirmed.
- **Stripe Issuing / Connect MCP** — same: bundled into main Stripe MCP for accounts with Issuing/Connect features enabled. Out of scope for v1 commerce adapter; documented for completeness.
- **Stripe webhook tunneling MCP** — none; the Stripe CLI's `stripe listen` covers this. Agent uses the CLI directly when running local rehearsal.

## Costs

Stripe pricing is processor-only — no monthly fee, no commerce-platform overhead. Captain L's pricing table is the phase-24a dialogue's most-read section; values verified at `https://stripe.com/pricing` 2026-05-20.

| Region | Card payments (online) | Apple Pay / Google Pay | Bank debits / regional methods |
|---|---|---|---|
| **US** | 2.9% + 30¢ | Same as cards | ACH 0.8% (capped at $5) |
| **EU (€)** | 1.5% + €0.25 for EEA cards; 2.5% + €0.25 for international | Same as cards | SEPA 0.8%; iDeal €0.29; Bancontact €0.39 |
| **UK (£)** | 1.5% + 20p UK; 2.5% + 20p international | Same as cards | Bacs 1.0% (capped) |
| **CH (CHF)** | 2.9% + 30¢ for international cards; lower for Swiss-issued | TWINT bundled into Stripe's CHF processing rate | — |
| **CA / AU / SG / JP** | 2.9% + 30¢ (local currency) | Same | Pre-authorized debits (CA), BPAY (AU) |

**Critical disclosures:**

1. **Currency conversion:** +1% on cross-currency transactions (charged in one currency, settled in another).
2. **Disputed charges (chargebacks):** $15 per dispute (refunded if you win the dispute).
3. **Disputes are processor-handled but user-responsible** — Stripe doesn't act as Merchant of Record (MoR); the **user is on the hook for chargebacks**. Contrast: Lemon Squeezy and Paddle ARE the MoR — they handle chargebacks on the user's behalf.
4. **Tax handling is the user's responsibility** unless they pay for **Stripe Tax** (additional 0.5% per transaction). Stripe Tax automates tax calculation + remittance in supported jurisdictions but does NOT transfer compliance liability the way an MoR does — the user is still legally the merchant.
5. **No monthly fee, ever.** Major upside vs Shopify ($29-299/mo) or other recurring-fee platforms.
6. **TWINT — no surcharge:** TWINT transactions in CHF settle at Stripe's standard CHF processing rate (2.9% + 30¢ for international cards / lower for Swiss-issued cards); no separate TWINT-specific fee on top.

**MoR disclosure summary (commerce):** Stripe = **user is MoR**. If the user is selling internationally and finds tax compliance burdensome, agent surfaces three alternatives at phase 24a/c:
- Add Stripe Tax (+0.5%) — automates calc + remit, user remains MoR
- Route to Lemon Squeezy (Phase 10+ adapter) — MoR absorbs compliance for digital products globally
- Route to Paddle (Phase 10+ adapter) — MoR absorbs compliance for B2B SaaS

## Stack pairings

Per locked decision 18 (full coverage). Verdicts match what Phase 3 stack adapters say about pairing with Stripe — cross-references `adapters/stack-framer.md` § "Commerce integration", `adapters/stack-nextjs.md` § "Commerce integration", `adapters/stack-wordpress.md` § "Commerce integration".

| Stack | Integration mode | Notes |
|---|---|---|
| **Framer** | Embed Payment Link as button via Framer Code Component **OR** redirect to Checkout via Code Component using `@stripe/stripe-js` loaded lazily | Payment Links easiest. Per `adapters/stack-framer.md` line 358: "Second default. Embedded via Code Component using `@stripe/stripe-js` loaded at runtime." |
| **Next.js + shadcn** *(strongest pairing)* | `app/api/checkout/route.ts` creates Stripe Checkout Sessions; client `<Link>` redirects to Stripe-hosted page; webhook handler at `app/api/stripe-webhook/route.ts` updates order state | The classic SaaS-marketing-site path. Per `adapters/stack-nextjs.md` line 539: "primary default; most muggle-friendly; minimal code; no PCI complications." Phase 4 fixture exercises this pairing. |
| **WordPress + WooCommerce** | Via the **Stripe for WooCommerce** plugin (supports SCA / 3DS / Apple Pay / Google Pay / TWINT enable in plugin settings) — OR direct Payment Link buttons via Gutenberg block | WordPress without WooCommerce: agent generates a Gutenberg Buy Button block wrapping a Payment Link. Per `adapters/stack-wordpress.md` line 674: "Stripe for WooCommerce — primary recommendation." |
| **Astro** | API endpoint (`src/pages/api/checkout.ts`) creates Session **OR** Payment Link buttons in static HTML | Same pattern as Next.js |
| **Hugo** | Payment Links as `<a href>` buttons (static-friendly) **OR** client-side fetch to a Functions endpoint (Cloudflare Workers / Netlify Functions / Vercel Functions) | Static-first; agent recommends Payment Links unless dynamic pricing needed |
| **SvelteKit** | `+server.ts` endpoint creates Session; client-side `goto()` redirect | Same pattern as Next |
| **Webflow** | Webflow Ecommerce uses Stripe natively (Webflow's hosted Stripe integration) — OR Payment Link buttons via Webflow Embed element for non-Ecommerce sites | Webflow Ecommerce: Stripe is built in. Non-Ecommerce: Payment Links. |
| **Plain static HTML** | Payment Links as `<a href>` buttons; success/cancel pages are static HTML files | The simplest entry point; agent recommends this when user is muggle + has 1-5 products + wants zero backend |

## Content layer mapping

Same 5-row contract as `adapters/README.md` §4 + `cms-adapters/README.md` §6 — IDENTICAL row labels in exact order. For commerce, most rows resolve to "n/a / handled via stack adapter" because Stripe Checkout is a hosted payment page that doesn't carry the website's design system; the L4 row carries checkout-success / cancel page content + receipt-customization tokens.

| Layer | Stripe Checkout native concept |
|---|---|
| **L1 brand.yaml.tokens** | n/a for Checkout itself (Stripe-hosted page is Stripe-styled). Limited Dashboard branding: logo upload + primary brand color (single hue) — Stripe applies these to the hosted page. For full white-label, route to Stripe Elements (out of scope for this adapter). |
| **L2 sitemap.yaml + sections.yaml** | n/a / handled via stack adapter — the stack adapter owns `/checkout`, `/success`, `/cancel` page registrations in `sitemap.yaml`. Stripe adds two off-site Stripe URLs: the Checkout Session URL (Stripe-hosted, transient per Session) and the Payment Link URL (Stripe-hosted, persistent). |
| **L3 strings/{lang}.json** | n/a / handled via stack adapter for the marketing-site's checkout-button labels + success/cancel page copy. Stripe Checkout's own UI strings auto-translate per browser locale (~25 languages) — see § "i18n + currency". |
| **L4 content/pages/*.md** | Carries checkout-success + cancel + receipt-customization content authored on the website-builder side: `content/pages/success.md` (post-payment confirmation + onboarding next steps), `content/pages/cancel.md` (recovery copy + retry CTA). Receipt email customization happens in Stripe Dashboard → Settings → Email; agent provides receipt-template copy via `content/transactional/receipt.md` for muggle-grade defaults. |
| **L5 briefs/{component}.json** | n/a / handled via stack adapter — buy-button / checkout-button / pricing-card components are generated by the stack adapter at phase 18; the brief targets the stack-native component shape, not Stripe's hosted page. The Stripe Checkout redirect is a *destination* the buy-button component points to, not a component itself. |

The mandatory table preserves cross-adapter consistency for the phase-12-cum-phase-24a verification anchor — `commerce-stripe.md` and (future) `commerce-shopify.md` / `commerce-lemonsqueezy.md` etc. share row labels so the General can sanity-check coverage row-by-row across commerce adapters AND against stack adapters.

## i18n + currency

Stripe Checkout has strong native i18n; the website-builder's i18n design (per `DESIGN-i18n.md`) lives at the marketing-site layer, NOT at Stripe's hosted Checkout layer.

- **Checkout UI languages:** Stripe Checkout auto-translates to ~25 languages based on browser locale (DE / FR / IT / EN / ES / PT / NL / PL / RU / JA / ZH / etc.). No agent work — Stripe handles it. The `locale` parameter on Session creation can force a specific locale; default is `auto`.
- **Currencies:** configured per Session / Payment Link; Stripe auto-detects user country to surface relevant regional methods (TWINT for CH-origin CHF transactions, iDeal for NL-origin EUR, Bancontact for BE, etc.).
- **Tax:** with Stripe Tax (+0.5%), automatic per-jurisdiction calculation + remittance in supported jurisdictions. Without Stripe Tax, the agent surfaces VAT registration / sales-tax-nexus implications at phase 24c per `DESIGN-commerce-stripe-checkout.md` lines 207-211.
- **Receipts:** localized in customer's language; agent can customize the email template via Dashboard → Settings → Email.

For the website-builder's i18n integration:

- **Marketing site i18n** → handled by the stack adapter's i18n integration (next-intl on Next.js, Framer's per-page locales, WordPress Polylang/WPML, etc.); agent generates `content/strings/{lang}.json` for the site itself.
- **Checkout i18n** → handled by Stripe's `locale: 'auto'` (default) — no extra agent work.
- **Currency display on marketing site** → agent uses `Intl.NumberFormat(locale, { style: 'currency', currency: 'CHF' })` per locale, NOT hardcoded format strings.
- **Currency at Stripe checkout** → matches the Session creation `currency` parameter; agent generates per-currency Session creation code when the user serves multiple currencies (e.g., one Session for EUR-region customers, one for CHF-region customers).

## TWINT-for-Switzerland callout

**TWINT is the non-negotiable Swiss-market payment method.** Per `commerce-adapters/README.md` § "TWINT-for-Switzerland — non-negotiable rule" + `Workstreams/website-builder/website-builder.md` decision 26 (Switzerland home market) + decision 47 (TWINT priority).

This adapter's TWINT support classification: **Native via Stripe** — Stripe is the canonical TWINT integration. No separate TWINT account, no second aggregator. Stripe handles the TWINT-backend integration as a first-class `payment_method_type`.

### How TWINT works on Stripe

- **Customer-facing:** TWINT is Switzerland's dominant mobile payment app (~3.5M+ active users on ~8.5M Swiss population; ~35%+ of Swiss e-commerce share — `DESIGN-payment-providers.md` lines 222-274). Users link a bank account or credit card to the TWINT app; pay by QR-code scan or push-notification approval.
- **Behind the scenes:** Stripe routes the payment-method-type=`twint` selection through the TWINT network for CHF-denominated Checkout Sessions; payment confirmation returns through the standard Checkout webhook (`checkout.session.completed`).

### CHF-only constraint + transaction limits (verified 2026-05-20)

Verified directly against `docs.stripe.com/payments/twint`:

- **Currency:** TWINT is **CHF-only** — protocol constraint, not config. A Session with `currency=eur` cannot include `twint` in `payment_method_types`; Stripe will reject the request.
- **Maximum transaction:** **5,000.00 CHF per transaction** — Stripe-enforced. Agent surfaces this at phase 24b when the user's product/service price exceeds CHF 5,000; for higher-value transactions, the user falls back to card / bank transfer.
- **Eligible merchant countries:** Stripe accounts in 35 European countries can accept TWINT (full list: AT, BE, BG, CH, CY, CZ, DE, DK, EE, ES, FI, FR, GB, GI, GR, HR, HU, IE, IS, IT, LI, LT, LU, LV, MC, MT, NL, NO, PL, PT, RO, SE, SI, SK, SM). The customer must be in Switzerland; the merchant's Stripe account can be in any of the 35.
- **No additional surcharge:** TWINT settles at Stripe's standard CHF processing rate.

### Configuration in Stripe Checkout (canonical agent pattern)

```bash
POST https://api.stripe.com/v1/checkout/sessions
  -d currency=chf
  -d "payment_method_types[]"=card
  -d "payment_method_types[]"=twint
  -d "line_items[0][price]"=PRICE_ID_IN_CHF
  -d mode=payment
  -d success_url="..."
  -d cancel_url="..."
```

**Modern alternative (verified context7 2026-05-20):** Stripe Checkout also supports `payment_method_types: 'auto'` (Dashboard-driven enablement). When TWINT is enabled in Dashboard → Settings → Payment methods, Stripe Checkout auto-surfaces TWINT for CHF Sessions without the explicit `payment_method_types[]=twint` parameter. Agent uses the explicit-list pattern for fixture validation (deterministic) and the Dashboard-driven pattern for production when the user prefers Dashboard control.

### Per-currency rendering rule

If a Swiss user is selling internationally (CH + EU customers), agent creates **per-currency** Checkout flows:
- CHF Session: `payment_method_types[]=card, twint` — Swiss customers see card + TWINT
- EUR Session: `payment_method_types[]=card, sepa, ideal, klarna` (per audience) — TWINT NOT included; protocol-rejected
- USD Session: `payment_method_types[]=card, link, klarna` (per audience)

The agent's per-currency payment-method picker enforces this rule — never offering TWINT outside CHF.

### Pause-and-report rule (TWINT compatibility)

For Swiss-audience projects on commerce adapters that don't reach TWINT (Paddle, Gumroad, Sellfy, Snipcart direct, Lemon Squeezy direct — per `DESIGN-payment-providers.md` lines 249-262), the phase-24a/b skill MUST surface a critical decision per `commerce-adapters/README.md` § "TWINT-for-Switzerland — non-negotiable rule" point 4:

- **(a)** Switch commerce platform to a TWINT-compatible one — Stripe direct (this adapter), WooCommerce + Stripe Gateway, Shopify if Shopify Payments available in CH, Saleor via Stripe payment app
- **(b)** Accept losing TWINT — requires **explicit user confirmation** of the ~35%+ Swiss revenue impact

### Cross-link to canonical contracts

- Canonical `payment-config.yaml` schema + TWINT contract (5-condition rule): [commerce-adapters/payment-config-schema.md § TWINT contract](payment-config-schema.md#twint-contract--non-negotiable-for-ch-audience-projects)
- Test fixture embodying the contract: [tests/commerce-adapters/stripe/fixture/](../tests/commerce-adapters/stripe/fixture/) (Phase 4 Captain L deliverable)
- Phase 4 DoD anchor: `Workstreams/website-builder/BUILD-strategy.md` line 202 — *"TWINT path validates on Stripe Checkout (CH-region simulation)"*

## Phase 24a/24b/24c integration

> Canonical `payment-config.yaml` schema for all phase-24b output: see [commerce-adapters/payment-config-schema.md](payment-config-schema.md). Adapter file does not duplicate the schema — only documents the Stripe-specific cells of the schema (per Captain 0 spec, S8).

### Phase 24a — Commerce platform setup

For Stripe Checkout, "platform setup" is minimal because Stripe IS the payment-only provider (vs Shopify, where 24a involves storefront + product catalog setup before 24b touches payments):

1. Agent confirms Stripe Checkout is the right choice (single product / 1-5 products / no catalog browsing; no inventory tracking; no shipping calculator). Decision tree from `DESIGN-commerce-stripe-checkout.md` lines 16, 234-242 — if the user has >5 products with browse/filter/search, route to Shopify (Phase 10+ adapter) or Lemon Squeezy (Phase 10+ adapter).
2. Agent walks the user through Stripe Dashboard signup at https://dashboard.stripe.com/register.
3. Agent helps activate the Stripe account: business info, bank account, identity verification — REQUIRED for live mode (test mode works without activation).
4. Agent generates a restricted API key (RAK) for setup phase; user copies to `.env`; 1Password stores the live secret key separately.
5. Agent uses Stripe MCP (or REST/SDK fallback per Tier 2 discipline) to create Stripe Products + Prices matching the user's product list (1-5 products typical for this commerce mode).
6. Agent picks Mode 1 (Payment Links) or Mode 2 (Checkout Sessions) per user's flexibility needs:
   - **Mode 1 (muggle default):** agent generates Payment Links via API or guides the user to create them in Dashboard; user gets URLs; agent embeds as `<a href>` buttons or stack-specific button components (per § "Stack pairings").
   - **Mode 2 (custom logic):** agent generates server-side endpoint code per stack (e.g., `app/api/checkout/route.ts` for Next.js) that creates Checkout Sessions on demand; agent generates client-side button code that hits that endpoint.
7. Agent runs **checkout-flow rehearsal** in test mode using Stripe test cards: `4242 4242 4242 4242` (always succeeds), `4000 0000 0000 9995` (insufficient funds decline), `4000 0027 6000 3184` (3DS required). For TWINT rehearsal, agent uses Stripe's TWINT test simulator (Dashboard → Test mode → Payment method simulators) — Phase 4 Captain L's fixture-level verification covers config-shape validity; runtime TWINT rehearsal is Phase 5+ test-runner scope.
8. Agent updates `.website-builder/commerce-config.yaml` with Stripe config + key env-var names + selected Mode (1 or 2) + product/price IDs.

### Phase 24b — Payment provider wiring

Stripe IS the payment provider in this commerce mode. The `.website-builder/payment-config.yaml` is the primary output (schema per `payment-config-schema.md`). Configuration per region/audience:

- **Cards:** auto-enabled in Stripe Dashboard (Visa, MC, Amex, Discover, JCB, Diners, UnionPay)
- **Apple Pay / Google Pay:** auto-enabled when domain verified — agent enforces domain verification at phase 24a as part of setup checklist (per § "Common failure modes")
- **TWINT (CHF, Swiss audience):** activated per § "TWINT-for-Switzerland callout" above. **MANDATORY** if `project.yaml.audience_regions` includes `CH`.
- **iDeal (EUR, NL audience):** activated for EUR transactions if Dutch audience
- **SEPA Direct Debit (EU recurring):** activated for recurring EUR transactions (subscription mode)
- **Bancontact (BE):** activated for Belgian audience
- **Klarna / Afterpay:** activated for BNPL where applicable (AOV > $100 / €100; per `DESIGN-payment-providers.md` lines 324-381)
- **3DS / SCA:** automatic for EU customers; agent verifies in test rehearsal that 3DS challenge fires for EU test cards
- **Webhook configuration:** agent configures webhook endpoint in Stripe Dashboard pointing to user's site (`/api/stripe-webhook` per stack); webhook signing secret to 1Password; webhook handler code MUST verify the signature (`stripe.Webhook.construct_event(payload, sig, secret)`) — agent refuses to ship handler without signature verification per `DESIGN-commerce-stripe-checkout.md` lines 251-252

For multi-provider configurations (Stripe + PayPal for legacy-trust audiences, Stripe + Klarna for high-AOV BNPL, Stripe + Mollie for EU optimization), agent adds the secondary provider entries to `payment-config.yaml` per the canonical schema. Routing per audience uses `regional_overrides` (e.g., `CH: primary: stripe, secondary: paypal`).

### Phase 24c — Commerce-specific legal

Stripe is **NOT** the Merchant of Record (user is). Legal pages required:

1. **Refund policy** — required; agent generates from user's actual policy via interview
2. **Tax handling disclosure** — user is MoR; agent surfaces VAT-registration implications (EU sales) and sales-tax-nexus implications (US sales). Three paths:
   - User remains MoR + handles tax manually (acceptable for small turnover but compliance-fragile)
   - Stripe Tax (+0.5%) — automates calc + remit in supported jurisdictions; user remains MoR
   - Route to Lemon Squeezy / Paddle (Phase 10+ MoR adapters) — MoR absorbs compliance; user pays adapter's higher commission
3. **T&Cs of sale** — required (separate from general T&Cs at phase 25)
4. **Imprint (DACH)** — required for Germany / Austria / Switzerland audiences (separate from general Imprint)
5. **Subscription disclosures** — required if Mode 2 with subscription pricing — agent generates standard disclosures (renewal frequency, cancellation procedure, refund-on-cancel policy, price-change notice period)
6. **Receipt / invoice format** — Stripe handles by default; agent can customize the receipt email template via Dashboard → Settings → Email → Customize the receipt sent to customers

### Customer Portal (for subscription mode)

If the user runs subscriptions (Mode 2 + `mode=subscription` Sessions), agent wires Stripe's Customer Portal at phase 24a:

```bash
POST https://api.stripe.com/v1/billing_portal/sessions
  -d customer=cus_xxx
  -d return_url="https://example.com/account"
```

The Customer Portal lets the user's customers manage their own subscriptions (upgrade, downgrade, cancel, update payment method) without the user building those flows manually. Agent generates a "Manage subscription" button on the user's account page that fires the portal-session creation + redirect.

## Mid-project transactional change handling

Per Decision 34 (transactional flag changes mid-project):

| Scenario | Re-runs |
|---|---|
| User adds Stripe Checkout mid-project (was non-transactional) | Phase 12 (CMS) generally compatible — no special CMS coupling. Phase 22 (forms) existing forms continue, agent adds checkout buttons or links. **Phase 24a / 24b / 24c run from scratch** (light for Stripe Checkout vs heavier for full commerce). Phase 25 (legal) — user is MoR, legal burden meaningful, agent surfaces this clearly. |
| User switches from Stripe Checkout → Shopify (later, Phase 10+ scope) | Phase 24a full restart on Shopify adapter; subscription customer migration (saved payment methods, subscription state) surfaced as a migration cost. |
| User adds a new payment provider alongside Stripe (e.g., Stripe + PayPal for legacy-trust) | Partial phase 24b: agent adds the new provider entry to `payment-config.yaml`, updates checkout flows to surface the second method, runs new test transactions, deploys. No full 24a restart. |
| User switches from test mode to live mode | Agent enforces explicit user confirmation + key-pattern check (`pk_live_*` / `sk_live_*` etc.) + domain verification check (Apple Pay / Google Pay) before live keys flip. |

Decision logged in `.website-builder/decisions/transactional-change-{ts}.md` (commerce-side change) or `.website-builder/decisions/payment-provider-change-{ts}.md` (provider-side change).

## Phase 6.5 ingestion (existing setup)

When `entry_mode = has-existing-site` AND the existing site uses Stripe Checkout / Payment Links:

1. Agent connects via Stripe API using user-supplied secret key (or a Restricted Key the user generates for read-only inspection)
2. Lists existing Products + Prices → seeds `.website-builder/commerce-config.yaml.products[]`
3. Lists existing Payment Links → catalogs current buy-buttons (per Payment Link → URL → target product mapping)
4. Reads enabled payment methods from Stripe Dashboard (or API where exposed) → seeds `.website-builder/payment-config.yaml.providers[].payment_methods[]`
5. Lists configured webhooks → identifies live webhook endpoint URLs + verifies signing secrets in 1Password
6. **TWINT presence check:** if the user has CH audience (per `project.yaml.audience_regions` or interview), agent verifies TWINT appears in the ingested `payment_methods[]` list. If absent, agent flags a critical gap and recommends enabling TWINT immediately (CHF + TWINT activation in Dashboard).
7. Logs ingestion in `.website-builder/decisions/ingest-{ts}.md` with: products found, payment methods found, TWINT-presence verdict, gaps flagged.

> Test fixture cross-link: [tests/commerce-adapters/stripe/fixture/](../tests/commerce-adapters/stripe/fixture/) — the Phase 4 fixture demonstrates the canonical post-ingestion shape (Stripe + TWINT + CHF + CH audience).

## Limitations

- **No catalog / browse / search.** Stripe Checkout is payment-only; for storefront UX with browse/filter/search, route to Shopify / Lemon Squeezy / Snipcart / Saleor (Phase 10+ adapters).
- **No inventory tracking.** Stripe doesn't manage stock levels; user manages inventory externally (or upgrades to Shopify).
- **No shipping calculator.** For physical products with shipping, route to Shopify / Sellfy / WooCommerce.
- **User is Merchant of Record.** Sales tax / VAT compliance is the user's burden (or use Stripe Tax / route to Lemon Squeezy / Paddle).
- **Limited UI customization on Checkout.** Hosted Checkout is Stripe-styled — brand customization limited to logo + a single primary brand color via Dashboard. For full white-label, use Stripe Elements (out of scope for this adapter; Phase 10+ scope if demand surfaces).
- **No subscription management UI for customers.** User must wire the Customer Portal (Stripe provides one — see § "Phase 24a/24b/24c integration → Customer Portal"); agent automates this at phase 24a when subscription mode is selected.
- **TWINT only works on CHF transactions.** A user trying to accept TWINT for EUR / USD will get rejected; agent's per-currency payment-method picker enforces this (per § "TWINT-for-Switzerland callout").
- **TWINT capped at 5,000 CHF per transaction.** For higher-value sales, user falls back to card / bank transfer (verified `docs.stripe.com/payments/twint` 2026-05-20).
- **TWINT only for Swiss customers.** The merchant's Stripe account can be in 35 European countries; the customer must be in Switzerland.

## Common failure modes

- **User picks Stripe Checkout when they actually need a catalog.** Agent's phase 24a decision tree screens for "do you have >5 products with browse/filter?" — if yes, route to Shopify or Lemon Squeezy.
- **User forgets to verify domain for Apple Pay / Google Pay.** Agent enforces domain verification at phase 24a as part of setup checklist; refuses to mark Apple Pay / Google Pay "enabled" without it.
- **User leaves test mode keys in production.** Agent enforces explicit user confirmation before flipping to live keys + key-pattern check (`sk_live_*` / `pk_live_*`); uses environment-specific config (`STRIPE_TEST_*` vs `STRIPE_*` env vars per `payment-config-schema.md`).
- **User assumes Stripe handles their VAT.** Agent surfaces this clearly: Stripe is processor only; tax is user's burden unless using Stripe Tax (+0.5%) or routing to MoR alternative.
- **TWINT not enabled for Swiss audience.** Agent flags at phase 24b for any project with `audience_regions: [CH]` (or `languages` including de-CH / fr-CH / it-CH / rm); fixture-level validation per [tests/commerce-adapters/stripe/expected.yaml](../tests/commerce-adapters/stripe/expected.yaml) asserts `phase_24b_payment.twint_enabled: true`.
- **Webhook signature not verified.** Agent enforces webhook signature verification in generated handler code; refuses to accept webhooks without `stripe.Webhook.construct_event(payload, sig, secret)` (or SDK equivalent). Per `DESIGN-commerce-stripe-checkout.md` lines 251-252.
- **Stripe Tax enabled but Tax Settings not configured.** If user enables Stripe Tax (+0.5%) but doesn't configure tax registrations per jurisdiction in Dashboard → Tax → Settings, Stripe Tax silently falls back to no calculation. Agent verifies Tax Settings show ≥1 active registration after Stripe Tax enablement.
- **Subscription mode without Customer Portal.** Agent enforces Customer Portal wire-up at phase 24a when subscription mode is selected; refuses to mark phase 24a complete without it.
- **Currency mismatch in TWINT Session.** Agent's per-currency payment-method picker prevents this at code-gen time; runtime Stripe API rejection is a secondary safety net.
- **Payment Link reused across products (Payment Link confusion).** Agent reminds the user at phase 24a that each Payment Link targets one product/price; for multi-product carts, agent recommends Mode 2 (Checkout Sessions) instead.

## References

### Foundation cross-references

- `Workstreams/website-builder/foundation/DESIGN-architecture.md` — plugin directory layout (`commerce-adapters/` per line 100)
- `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` — phase 22 (forms / transactional) + phase 24a (commerce platform) + 24b (payment provider) + 24c (commerce legal)
- `Workstreams/website-builder/foundation/DESIGN-content-layers.md` — the 5 content layers the § "Content layer mapping" table maps
- `Workstreams/website-builder/foundation/DESIGN-i18n.md` — i18n model + currency
- `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` — `.website-builder/` directory layout
- `Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md` — phase 6.5 mechanism

### Source design docs

- `Workstreams/website-builder/commerce/DESIGN-commerce-stripe-checkout.md` — Stripe Checkout source design doc (lines 17-266)
- `Workstreams/website-builder/commerce/DESIGN-payment-providers.md` — payment-provider matrix + decision tree + TWINT-critical section + canonical `payment-config.yaml` schema source

### Captain 0 prep packet (sibling Phase 4 files)

- [commerce-adapters/README.md](README.md) — commerce + booking adapter schema contract (read-only)
- [commerce-adapters/payment-config-schema.md](payment-config-schema.md) — canonical `payment-config.yaml` schema (read-only; this adapter references but does not duplicate)
- [commerce-adapters/booking-calcom.md](booking-calcom.md) — sibling booking adapter (Cal.com); cross-link for paid-booking TWINT-via-Stripe-bridge (S7)
- [tests/commerce-adapters/README.md](../tests/commerce-adapters/README.md) — fixture convention + TWINT-required fixture rule
- [tests/commerce-adapters/stripe/fixture/](../tests/commerce-adapters/stripe/fixture/) — Phase 4 Captain L deliverable: TWINT-required CH-region fixture
- [tests/commerce-adapters/stripe/expected.yaml](../tests/commerce-adapters/stripe/expected.yaml) — Phase 4 Captain L deliverable: expected phase-24a/b/c output

### Stack pairing cross-references

- `adapters/stack-framer.md` § "Commerce integration (if transactional=true)" — Stripe via Code Component + Payment Links
- `adapters/stack-nextjs.md` § "Commerce integration (if transactional=true)" — Stripe via Route Handler + webhook + shadcn buy-button pattern
- `adapters/stack-wordpress.md` § "Commerce integration (if transactional=true)" — Stripe via WooCommerce plugin OR Gutenberg buy-button block

### External (verified 2026-05-20)

- Stripe homepage: https://stripe.com
- Stripe Checkout product page: https://stripe.com/payments/checkout
- Payment Links product page: https://stripe.com/payments/payment-links
- Stripe API reference: https://docs.stripe.com/api
- TWINT integration guide: https://docs.stripe.com/payments/twint (CHF-only, max 5,000 CHF, 35 eligible merchant countries)
- Stripe Tax: https://stripe.com/tax (+0.5% per transaction)
- Stripe Customer Portal: https://docs.stripe.com/customer-management
- Stripe MCP plugin: https://claude.com/plugins/stripe (Anthropic blessed; 27,078 installs as of 2026-05-20)
- Stripe MCP direct: https://docs.stripe.com/mcp (`@stripe/mcp` npx + remote HTTP at `https://mcp.stripe.com`)
- context7 library IDs: `/websites/stripe_js`, `/stripe/stripe-node`, `/stripe/stripe-python`

### Phase 4 / Phase 10+ commerce adapter siblings

- (future, Phase 10) `commerce-shopify.md` — when user needs full storefront with browse/cart/inventory
- (future, Phase 10) `commerce-lemonsqueezy.md` — MoR alternative for digital products; tax-compliance-absorbed
- (future, Phase 10) `commerce-paddle.md` — MoR for B2B SaaS subscriptions
- (future, Phase 10) `commerce-snipcart.md` — cart on static site (Snipcart drop-in)
- (future, Phase 10) `commerce-saleor.md` — open-source GraphQL commerce backend

### Decision anchors

- `Workstreams/website-builder/website-builder.md` decision 18 (full stack coverage), decision 26 (Switzerland home market), decision 34 (transactional flag mid-flip), decision 47 (TWINT priority), decision 54 (Cal.com booking default — sibling), decision 58 (parallel-to-platform subproject location), decision 65 (per-callsign worktree)
- `Workstreams/website-builder/BUILD-strategy.md` Phase 4 DoD lines 187-209 (TWINT path validates on Stripe Checkout — CH-region simulation; line 202)
