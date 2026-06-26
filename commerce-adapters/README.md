# Commerce adapters — canonical section schemas

> Every commerce adapter at `commerce-adapters/commerce-<name>.md` MUST follow the **commerce schema** below. Every booking adapter at `commerce-adapters/booking-<name>.md` MUST follow the **booking schema** below. The skills (`wb-architecture` phase 24a, phase 24b payment-provider wiring, phase 24c commerce-specific legal, phase 22 transactional mid-flip per Decision 34, phase 6.5 re-runnable ingestion) look up sections by exact name at runtime — schema divergence is silent skill failure across the pipeline.
>
> This README is the contract Phase 4 Captain L (`commerce-stripe.md` + `booking-calcom.md`) builds against. Subsequent commerce adapters (Shopify / Lemon Squeezy / Paddle / Snipcart / Saleor — Phase 10 expansion) follow the commerce schema; subsequent booking adapters (Calendly / SimplyBook / etc.) follow the booking schema.

## Two distinct schemas, one README

Commerce adapters and booking adapters are **structurally different**:

- **Commerce adapters** (Stripe, Shopify, Lemon Squeezy, Paddle, Snipcart, Saleor) handle product / payment / cart / checkout primitives. The user is selling a thing (a course, a service fee, a physical product, a digital download, a subscription). Phase 24a sets up the platform; phase 24b wires the payment provider(s); phase 24c addresses commerce-specific legal.
- **Booking adapters** (Cal.com, Calendly, SimplyBook) handle event-types / availability / scheduling primitives. The user is selling time (consults, coaching, workshops, appointments). Phase 24a sets up the booking platform; phase 24b wires payment IF the bookings are paid (some bookings are free); phase 24c addresses booking-specific legal (cancellation, no-show, service contract).

Both schemas share many H2 names (Mental model / Auth model / CRUD vocabulary / API + MCP availability / Costs / Stack pairings / Content layer mapping / i18n + currency / TWINT callout / Limitations / Common failure modes / References) — but their internal content + phase-24 integration sections differ. Captain L authors ONE file per adapter type (one commerce file + one booking file), each following its respective schema.

**Why not collapse into one schema?** The phase-24 contracts differ. A commerce adapter's phase 24a is "platform setup → products + prices → checkout flow"; a booking adapter's phase 24a is "platform setup → event types + availability → embed widget on site." Forcing one schema would either make commerce sections empty for booking (or vice versa) or smear the per-phase contract checks. Keeping them distinct keeps the phase-24 skill's per-section lookups unambiguous.

---

## Commerce adapter schema — 15 required H2 sections, exact order

Every `commerce-adapters/commerce-<name>.md` MUST contain all 15 sections below as H2 headings, in this exact order. Renaming or reordering is prohibited. Adding adapter-specific subsections (H3 / H4) within a section is allowed. Adding entirely new H2 sections at the end (16, 17, ...) is allowed for adapter-specific concerns the schema doesn't cover.

| # | Section | Purpose |
|---|---|---|
| 1 | `## Mental model` | What the commerce platform IS — the user's mental shape. **First paragraph or `### Identity` H3 encodes platform name + version + canonical context7 ID + freshness-check requirement.** Anchor for the user's intuition + the agent's phase-24a explanation. |
| 2 | `## Auth model` | Credential surface — secret keys, publishable keys, webhook signing secrets, restricted access keys. Table form: auth method / used for / key shape / where it lives (env var + 1Password path). All secrets via `secrets-conventions.md`. |
| 3 | `## CRUD vocabulary` | Native API verbs translated for the website-builder's vocabulary — create product, create price, create session, create payment link, refund, void, dispute. REST endpoints + minimal request samples. |
| 4 | `## API + MCP availability` | What integration surfaces exist: REST API, webhooks, browser SDK, server SDKs, CLI, official MCP, dashboard. Per-surface use + fallback discipline (per `tool-dependency-discipline.md` Tier 2). |
| 5 | `## Costs` | **REQUIRED muggle-transparent pricing table.** Per-region card fees + per-method fees + currency conversion overhead + chargeback fees + tax-handling responsibility + MoR-or-not disclosure. The phase-24a dialogue reads this verbatim to give the user the honest cost picture before lock-in. |
| 6 | `## Stack pairings` | Per phase-11 stack choice (Framer / Next.js / WordPress / Astro / Hugo / SvelteKit / Webflow / Plain static HTML): integration mode + notes. Per locked decision 18 (full stack coverage). |
| 7 | `## Content layer mapping` | **REQUIRED table** — same 5-row contract as `adapters/README.md` §4 + `cms-adapters/README.md` §6. For commerce, most rows resolve to "n/a for commerce / handled via stack adapter" but the table is still mandatory for cross-adapter consistency verification. The L4 row may carry "checkout flow / success page / cancel page content" if the platform owns those surfaces. |
| 8 | `## i18n + currency` | Locale support in checkout UI + currency / receipt / regional-tax handling + which currencies / regional payment methods are supported. Cross-references the website-builder's marketing-site i18n (which IS separate from checkout i18n — checkout i18n is usually free via the platform). |
| 9 | `## TWINT-for-Switzerland callout` | **REQUIRED for every commerce adapter.** Document this adapter's TWINT support — native via Stripe / via-Stripe-bridge from another platform / unsupported. The CHF-only constraint. Where in checkout the TWINT option surfaces. If unsupported: an explicit pause-and-report rule for Swiss-audience projects (per `DESIGN-payment-providers.md` line 273). |
| 10 | `## Phase 24a/24b/24c integration` | Per-sub-phase recipe for THIS adapter. 24a (platform setup) → product/price creation + checkout flow + rehearsal. 24b (payment provider wiring) → method enablement per audience + webhook + 3DS/SCA + TWINT for CHF + iDeal for NL + etc. 24c (commerce-specific legal) → refund / shipping / T&Cs of sale / Imprint / subscription disclosures / receipt format. |
| 11 | `## Mid-project transactional change handling` | Per Decision 34 (transactional flag changes mid-project) — what re-runs when user adds this commerce adapter mid-project, OR when user changes commerce platform, OR adds a new provider alongside existing. Phase 12 / phase 22 / phase 24a-c / phase 25 re-run scope per scenario. Decision logged in `.website-builder/decisions/transactional-change-{ts}.md`. |
| 12 | `## Phase 6.5 ingestion (existing setup)` | When `entry_mode = has-existing-site` AND existing site already uses this commerce platform: read existing config via API / dashboard inspection; seed `commerce-config.yaml` + `payment-config.yaml`; identify enabled methods; log ingestion in `decisions/ingest-{ts}.md`. |
| 13 | `## Limitations` | What this adapter CAN'T do — bullets. (e.g., Stripe Checkout: no catalog / browse / search; no inventory tracking; no shipping calculator; user is MoR. Shopify: monthly fee; Shopify-locked checkout.) |
| 14 | `## Common failure modes` | Specific failure-path enumeration — test-mode keys deployed to prod, webhooks not verified, domain not verified for Apple Pay, TWINT not enabled for CHF audience, currency mismatch, missing legal pages. Per-failure: agent's prevention mechanism. |
| 15 | `## References` | Foundation design-doc paths (vault-root-relative per `vault-workstreams.md` link standard) + per-adapter external references (official docs, API reference, source design doc, sibling commerce + payment-provider docs). |

---

## Booking adapter schema — 15 required H2 sections, exact order

Every `commerce-adapters/booking-<name>.md` MUST contain all 15 sections below as H2 headings, in this exact order. Same renaming / reordering / extension rules as the commerce schema.

| # | Section | Purpose |
|---|---|---|
| 1 | `## Mental model` | What the booking platform IS — the user's mental shape. **First paragraph or `### Identity` H3 encodes platform name + version + canonical context7 ID + freshness-check requirement + Cloud-vs-self-hosted-vs-other deployment-mode summary.** |
| 2 | `## Auth model` | API key + embed token surfaces. Same table form as commerce. Self-hosted vs cloud auth differences if applicable. |
| 3 | `## CRUD vocabulary` | Native API verbs — create event type, list bookings, cancel booking, get availability, set buffer time, sync calendar. REST endpoints + minimal request samples. |
| 4 | `## API + MCP availability` | What integration surfaces exist: REST API, webhooks, embed scripts (inline / popup / floating button), React component library (e.g., Cal.com Atoms), dashboard, official MCP if any. |
| 5 | `## Costs` | **REQUIRED muggle-transparent pricing table.** SaaS pricing tiers (per-user / per-month) + self-hosted option (if any) + per-booking fees (usually $0; payment processor fee applies for paid bookings). License callout (AGPLv3 for Cal.com — only matters if user modifies + offers as service). |
| 6 | `## Stack pairings` | Per phase-11 stack choice: integration mode (embed script / iframe / React Atoms / shortcode / plugin) + notes. Per locked decision 18 (full stack coverage). |
| 7 | `## Content layer mapping` | **REQUIRED table** — same 5-row contract. For booking adapters, most rows are "n/a for booking / handled via stack adapter" — but L4 may carry the event-type description / booking-success-page content / cancellation-policy content; L1 sometimes carries embedded-widget styling tokens. The table is still mandatory. |
| 8 | `## i18n + currency` | Locale support in booking UI + time-zone handling (booking adapters are TZ-aware in a way commerce adapters aren't — customer-TZ + provider-TZ are distinct) + currencies for paid bookings. |
| 9 | `## TWINT-for-Switzerland callout` | **REQUIRED for every booking adapter.** For booking, TWINT only applies to paid bookings AND only when the booking platform's payment processor is Stripe (Cal.com → Stripe → TWINT works; Cal.com → PayPal → TWINT does NOT work). Document the bridge chain explicitly. |
| 10 | `## Phase 24a/24b/24c integration (booking branch)` | Per-sub-phase recipe FOR BOOKING. 24a (platform setup) → event-types + availability + calendar integration + video integration + embed on site + rehearsal. 24b (payment provider wiring, IF paid bookings) → connect Stripe in platform dashboard + enable TWINT for CH + paid-booking rehearsal. 24c (commerce-specific legal, IF paid bookings) → cancellation policy + no-show policy + T&Cs of service + Imprint + GDPR/privacy disclosure of booking processor. **The `(booking branch)` qualifier is part of the H2 heading verbatim per design-doc convention.** |
| 11 | `## Mid-project transactional change handling` | Per Decision 34 — what re-runs when user adds booking mid-project (light-touch: phase 22 forms unchanged, phase 24a from scratch, phase 24b only if paid). User changes from "free booking" → "paid booking" mid-project: phase 24b only. Decision logged in `.website-builder/decisions/transactional-change-{ts}.md`. |
| 12 | `## Phase 6.5 ingestion (existing setup)` | When `entry_mode = has-existing-site` AND existing user already has this booking platform: list event types + recent bookings + enabled integrations (calendar / video / payment) via API; seed `commerce-config.yaml.bookings`; log ingestion. |
| 13 | `## Limitations` | What this adapter CAN'T do — bullets. (e.g., Cal.com: booking-only — no products/catalog/cart; self-hosted operational burden; AGPLv3 restrictions; embed customization moderate; payment processor required for paid bookings; multi-staff requires Teams plan; TWINT only via Stripe.) |
| 14 | `## Common failure modes` | Specific failure-path enumeration — calendar not connected before launch, time-zone confusion, test bookings polluting real calendar, TWINT not enabled for CH, buffer time not configured (back-to-back bookings), payment-confirmation webhook missing. |
| 15 | `## References` | Foundation paths + adapter-specific (official site, API docs, self-hosting guide, GitHub if open-source, source design doc, sibling commerce + payment-provider docs, peer booking-adapter docs). |

---

## TWINT-for-Switzerland — non-negotiable rule

Per Commander direction + `Workstreams/website-builder/website-builder.md` decision 26 (Switzerland is Jules's home market) + decision 54 (Cal.com is the Phase 4 booking default) + `DESIGN-payment-providers.md` lines 222-274 (TWINT critical, ~3.5M+ Swiss users, ~35%+ of Swiss e-commerce share, CHF-only):

**TWINT is the non-negotiable Swiss-market payment method. Every commerce + booking adapter MUST:**

1. **Document TWINT support for the adapter's payment path.** One of:
   - **Native via Stripe** — adapter sits on Stripe directly; TWINT is enabled as a Stripe payment method for CHF transactions; example: `commerce-stripe.md`
   - **Via Stripe bridge from another platform** — adapter uses Stripe as its payment processor; TWINT flows through that bridge; example: `booking-calcom.md` (Cal.com → Stripe → TWINT for CHF paid bookings)
   - **Via Stripe Gateway plugin** — example: WooCommerce-on-WordPress + Stripe Gateway → TWINT
   - **Unsupported** — adapter cannot reach TWINT (e.g., Paddle, Gumroad, Sellfy, Snipcart, Lemon Squeezy direct). For Swiss-audience projects, this MUST trigger the **pause-and-report rule** below.

2. **Document the CHF-only constraint.** TWINT does NOT process non-CHF transactions; a user trying to accept TWINT for EUR will get rejected. Adapter's payment-method picker per-currency map must enforce this (i.e., only show TWINT in checkout when transaction currency is CHF).

3. **Include CH-region simulation in the test fixture.** The `tests/commerce-adapters/<name>/fixture/project.yaml` MUST include `audience_regions: [CH]` (or similar CH marker per the fixture convention in `tests/commerce-adapters/README.md`) AND the corresponding `payment-config.yaml` MUST include CHF + TWINT in the providers/payment_methods config. This is the BUILD-strategy.md Phase 4 DoD line 202 (*"TWINT path validates on Stripe Checkout (CH-region simulation)"*) requirement made concrete.

4. **Pause-and-report rule for TWINT-unsupported adapters.** If `project.yaml.audience_regions` includes CH AND the chosen adapter is in the unsupported list (Paddle / Gumroad / Sellfy / Snipcart / Lemon Squeezy direct / etc.), the phase-24a/b skill MUST surface this as a critical decision point and recommend either:
   - **(a)** Switch commerce platform to a TWINT-compatible one (Stripe-direct, WooCommerce + Stripe Gateway, Shopify if Shopify Payments available in CH, Saleor via Stripe payment app)
   - **(b)** Accept losing TWINT — requires **explicit user confirmation** of the Swiss revenue impact (the phase-24b dialogue surfaces ~35%+ of Swiss e-commerce share as the loss estimate)

This rule applies even to free-tier / muggle-scale projects. TWINT is load-bearing for Swiss market viability; silent omission would degrade Swiss-audience projects.

---

## Per-section content guidance — commerce adapter highlights

What the load-bearing sections require beyond their headlines. Captains author per their adapter's specifics; this establishes the floor for commerce adapters specifically (booking-specific guidance follows in the next sub-section).

### `## Costs` (commerce)

The phase-24a dialogue's most-read section. Required content:

- **Per-region card fee table** — US / EU / UK / CH / CA / AU / SG / JP (or subset relevant to this adapter)
- **Per-method fee variants** — Apple/Google Pay typically same as cards; ACH / SEPA / iDeal / Bancontact often cheaper; TWINT-via-Stripe matches Stripe's CHF rate
- **Currency conversion overhead** — Stripe ~+1%; Mollie + PayPal vary
- **Chargeback fees** — Stripe $15; PayPal $20; refunded if won
- **MoR-or-not disclosure** — is the adapter the merchant of record (Lemon Squeezy, Paddle, Shopify with Shopify Tax) or is the USER the MoR (Stripe, Mollie, PayPal direct)? Tax compliance lives with the MoR.
- **Tax handling responsibility** — auto-calc + remit (Stripe Tax +0.5%) vs user's burden vs MoR-absorbs (Lemon Squeezy / Paddle)
- **No monthly fee callout** if applicable (Stripe / Mollie / PayPal / Square direct = $0/mo; Shopify = $29-299/mo)

Source anchor: `DESIGN-commerce-stripe-checkout.md` § "Costs (TRANSPARENT to muggles — they care intensely)" lines 97-117 for the template shape.

### `## Phase 24a/24b/24c integration` (commerce)

The phase-24 skill consumes this. Required content per sub-phase:

**Phase 24a — Commerce platform setup:**
- Pre-conditions check (does the adapter fit the user's commerce shape? — for Stripe Checkout: single product / no catalog browsing; for Shopify: full storefront; etc.)
- Dashboard signup + account activation (business info, bank account, identity verification — required for live mode)
- API key generation flow (in dashboard) + 1Password storage + restricted-key recommendation for setup vs live keys
- Product + Price creation via API (per `project.yaml.products` or via interview)
- Checkout flow generation per stack pairing (server endpoint code for Mode 2 / Payment Link generation for Mode 1)
- Test-mode rehearsal with test cards (`4242 4242 4242 4242` for Stripe; equivalent for other platforms)
- `.website-builder/commerce-config.yaml` schema update with platform config + env-var names

**Phase 24b — Payment provider wiring:**
- Method enablement per audience (decision tree from `DESIGN-payment-providers.md` lines 22-52)
- Cards + Apple/Google Pay activation (domain verification required for Apple/Google Pay)
- **Regional methods** — TWINT for CHF (mandatory if CH audience), iDeal for NL (mandatory if NL audience), SEPA for EU recurring, Klarna for BNPL > $100 AOV, Bancontact for BE, Sofort for DACH
- Webhook endpoint configuration + webhook signing secret to 1P
- 3DS / SCA verification in test rehearsal (mandatory for EU)
- Live-mode flip explicit user confirmation (test-key → live-key cutover)

**Phase 24c — Commerce-specific legal:**
- Refund policy (required; generated from user's actual policy via interview)
- Shipping policy (required for physical products only)
- T&Cs of sale (separate from general T&Cs of phase 25)
- Imprint (DACH legal requirement) — separate from general Imprint
- Subscription disclosures (renewal frequency, cancellation, refund-on-cancel) — required for subscription mode
- Receipt / invoice format — platform default vs custom
- Tax-handling disclosure — if user is MoR (Stripe direct), surface the VAT-registration / sales-tax-nexus implications; if user picked MoR alternative (Lemon Squeezy / Paddle), surface that the MoR absorbs compliance

Source anchor: `DESIGN-commerce-stripe-checkout.md` § "Phase 24a/24b/24c integration" lines 171-212 for the template shape.

---

## Per-section content guidance — booking adapter highlights

### `## Costs` (booking)

Two distinct cost surfaces:

**SaaS pricing tier table** — typical structure:
- Free tier (often generous — Cal.com is $0/mo for solo)
- Teams tier ($15-19/user/mo for team scheduling)
- Organizations tier ($30-40/user/mo for RBAC + SSO + audit)
- Enterprise tier (custom)

**Self-hosted option (if any):** Cal.com offers AGPLv3 self-hosted at $0 software cost + $5-50/mo typical hosting + real DevOps burden. License callout: AGPLv3 compliance only matters if user modifies + offers as service.

**Per-booking fees:** usually $0 from the booking platform; payment processor fee applies for paid bookings (Stripe / PayPal at their standard rates).

Source anchor: `DESIGN-booking-calcom.md` § "Costs (TRANSPARENT to muggles — they care intensely)" lines 99-125 for the template shape.

### `## Phase 24a/24b/24c integration (booking branch)` (booking)

**Phase 24a — Booking platform setup (booking branch):**
- Pre-conditions check (services / consulting / coaching business?)
- SaaS vs self-hosted decision
- Account / instance setup
- API key generation + 1Password storage
- Event-type creation via API (per `project.yaml.services` or interview) — title / duration / location (video or in-person) / description / price / buffer / booking-window
- Calendar integration (Google / Microsoft / Apple / CalDAV) — read availability + write events
- Video integration per event type (Zoom / Google Meet / Daily / Whereby)
- Embed on user's site (inline / popup / floating button)
- Test booking rehearsal
- `.website-builder/commerce-config.yaml` schema update with booking config

**Phase 24b — Payment provider wiring (for paid bookings):**
- Stripe / PayPal connection in booking platform dashboard
- TWINT enablement in Stripe for CHF event types (Swiss audience)
- Paid-booking rehearsal: book event → checkout fires → test payment → booking confirmed

**Phase 24c — Commerce-specific legal (booking branch, for paid bookings):**
- Cancellation / refund policy (e.g., "refund if canceled >24 hours in advance")
- No-show policy
- T&Cs of service (booking IS a service contract)
- Imprint (DACH)
- GDPR / privacy disclosure (booking data = personal data; platform listed as processor)
- For free bookings: minimal legal (privacy policy + cancellation policy still recommended)

Source anchor: `DESIGN-booking-calcom.md` § "Phase 24a/24b/24c integration" lines 162-213 for the template shape.

---

## Captain L exclusive write zones

| Captain | Adapter(s) | Write paths (exclusive) |
|---|---|---|
| **Captain L** | Commerce (Stripe) + Booking (Cal.com) | `commerce-adapters/commerce-stripe.md` (full file; combines Stripe Checkout + Stripe payment-provider surface per BOARD line 39) + `commerce-adapters/booking-calcom.md` (full file) + `tests/commerce-adapters/stripe/` (full subdirectory: `fixture/`, `expected.yaml`, `README.md`) + `tests/commerce-adapters/calcom/` (full subdirectory) |

### READ-ONLY for Captain L

The following files are shared substrate authored in Phase 4 Captain 0 prep. **Do NOT modify** during Captain L's work:

- `commerce-adapters/README.md` (this file — the schema contract)
- `commerce-adapters/payment-config-schema.md` (canonical `payment-config.yaml` schema — Captain L references but does not invent the schema. Adapter files cross-link to this schema in their § "Phase 24a/24b/24c integration" + § "TWINT-for-Switzerland callout" sections.)
- `tests/commerce-adapters/README.md` (test fixture convention + TWINT-required fixture rule)
- `cms-adapters/README.md` + `cms-adapters/*.md` (Phase 4 CMS adapters — referenced by commerce/booking adapters' § "Stack pairings" when discussing CMS-pairing notes for transactional shapes)
- `adapters/README.md` + `adapters/stack-*.md` (Phase 3 stack adapters — referenced by commerce/booking adapters' § "Stack pairings" for per-stack integration mode)
- `i18n/strings-schema.md`, `i18n/rtl.md`, `i18n/language-switcher.md`, `i18n/hreflang.md` (Phase 3 i18n substrate)

Captain L's adapter files may *reference* (cross-link to) any of these read-only anchors; they may not edit them.

### Worktree discipline

Per Decision 65: Captain L uses a per-callsign worktree under `Projects/Jules.Solutions/Subprojects/website-builder.captain-l/` to avoid filesystem collisions on the read-only shared substrate. No push from Captain — General does sequential merge + single push at end of Phase 4 wave.

---

## S-risk callouts — bake into Captain L's prompt

The pre-dispatch researcher identified S-risks (Captain-specific surprises) that must be explicitly surfaced in Captain L's prompt so they're not buried inside design-doc reading:

### S5 — Two distinct adapter files, NOT one

Captain L produces **TWO** adapter files (`commerce-stripe.md` + `booking-calcom.md`), each following its OWN schema (commerce schema vs booking schema). They are not interchangeable. The two adapters share many H2 names but differ in their phase-24 integration shape, their content-mapping table cells, their cost models, and their TWINT bridge chain. Captain L MUST author both files separately, NOT conflate them.

The reasoning: commerce and booking are distinct primitive shapes. Stripe Checkout creates Products + Prices + Sessions; Cal.com creates Event Types + Availability + Bookings. The phase-24a dialogue branches on which primitive the user wants — products-for-sale OR time-for-sale. Forcing one adapter would smear the two contracts.

### S6 — TWINT-via-Stripe CHF fixture is the canonical Swiss validation

Per BUILD-strategy.md Phase 4 DoD line 202 (*"TWINT path validates on Stripe Checkout (CH-region simulation)"*), the `tests/commerce-adapters/stripe/fixture/` MUST include:

- `project.yaml.audience_regions: [CH]`
- `project.yaml.currencies: [CHF, EUR]` (CHF mandatory; EUR optional)
- `payment-config.yaml.providers[0].name: stripe`
- `payment-config.yaml.providers[0].payment_methods` includes `card`, `twint`, `apple_pay`, `google_pay`
- `payment-config.yaml.providers[0].currencies` includes `CHF`
- `expected.yaml.phase_24b.twint_enabled: true`
- `expected.yaml.phase_24b.chf_currency_enabled: true`

The TWINT fixture is the test-side embodiment of the home-market non-negotiable. Captain L's adapter file (`commerce-stripe.md`) MUST cross-link the fixture in its § "TWINT-for-Switzerland callout" and § "Phase 6.5 ingestion" so the contract is visible from both ends.

Per `tests/commerce-adapters/README.md` (sibling Phase 4 Captain 0 prep file), this is the concrete YAML the fixture loads. Captain L references but does not author the schema rule itself — only fills in the fixture's contents per the rule.

### S7 — Cal.com Stripe-bridge for TWINT (booking-specific surprise)

For `booking-calcom.md`, the TWINT bridge chain is:

```
Cal.com event type (CHF, paid)
   → Cal.com → Stripe connection (configured in Cal.com Dashboard → Apps → Stripe)
   → Stripe Checkout (TWINT payment_method enabled for CHF)
   → TWINT app on customer's phone
   → booking confirmed via Cal.com webhook
```

Captain L's `booking-calcom.md` § "TWINT-for-Switzerland callout" MUST document this chain explicitly — TWINT works ONLY when Cal.com's payment processor is set to Stripe (not PayPal); the bridge is Cal.com → Stripe → TWINT; CHF-only.

Per `DESIGN-booking-calcom.md` lines 150-156 + `DESIGN-payment-providers.md` lines 222-274.

### S8 — `payment-config-schema.md` is read-only canonical anchor

Captain L does NOT author the canonical `payment-config.yaml` schema. The schema lives in `commerce-adapters/payment-config-schema.md` (sibling Phase 4 Captain 0 prep file), which extracts the schema verbatim from `DESIGN-payment-providers.md` (~lines 400-435).

Captain L's `commerce-stripe.md` § "Phase 24a/24b/24c integration" + `booking-calcom.md` § "Phase 24a/24b/24c integration (booking branch)" reference this schema by path — they do not duplicate or modify it. Any future commerce adapter (Shopify, Lemon Squeezy, Paddle, etc., in Phase 10 expansion) likewise references the canonical schema from `payment-config-schema.md`.

This is the same pattern as Phase 3's `i18n/strings-schema.md` (CDJSON schema authored once, referenced by every stack adapter and every CMS adapter).

---

## See also

- `Workstreams/website-builder/BUILD-strategy.md` Phase 4 — DoD + dispatch model (lines 187-209)
- `Workstreams/website-builder/commerce/DESIGN-commerce-stripe-checkout.md` — Captain L's commerce primary design-doc source
- `Workstreams/website-builder/commerce/DESIGN-payment-providers.md` — Captain L's payment-provider matrix + canonical `payment-config.yaml` schema source
- `Workstreams/website-builder/commerce/DESIGN-booking-calcom.md` — Captain L's booking primary design-doc source
- `Workstreams/website-builder/foundation/DESIGN-architecture.md` — plugin directory layout (`commerce-adapters/` per line 100)
- `Workstreams/website-builder/foundation/DESIGN-content-layers.md` — the 5 content layers the §7 table maps
- `Workstreams/website-builder/foundation/DESIGN-i18n.md` — i18n model + currency
- `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` — phase 22 (forms / transactional) + phase 24a (commerce platform) + 24b (payment provider) + 24c (commerce legal)
- `Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md` — phase 6.5 mechanism
- `Workstreams/website-builder/website-builder.md` — decision 26 (Switzerland home market) + decision 47 (TWINT priority) + decision 54 (Cal.com booking default)
- `cms-adapters/README.md` — CMS adapter schema (sibling Phase 4 Captain 0 prep file); commerce + CMS pair via the `## Commerce integration (if transactional=true)` H2 on each side
- `commerce-adapters/payment-config-schema.md` — canonical `payment-config.yaml` schema (sibling Phase 4 Captain 0 prep file; read-only for Captain L)
- `adapters/README.md` — Phase 3 stack adapters; commerce + stack pair via stack adapter's § "Commerce integration (if transactional=true)" H2 and commerce adapter's § "Stack pairings" H2
- `tests/commerce-adapters/README.md` — per-commerce + booking adapter test fixture convention (sibling Phase 4 Captain 0 prep file)
- `skills/wb-architecture/SKILL.md` — phase 24 consumer of commerce + booking adapter files
- Phase 10+ (later) — Shopify, Lemon Squeezy, Paddle, Snipcart, Saleor — all follow this commerce schema. Calendly, SimplyBook — booking schema.
