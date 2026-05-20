# Canonical `payment-config.yaml` schema

> The single source of truth for `.website-builder/payment-config.yaml`. Every commerce + booking adapter (Phase 4 Captain L + future Phase 10 adapters) references this schema instead of duplicating it inline. Read-only during Phase 4 Captain L work — any change requires General review (same pattern as Phase 3's `i18n/strings-schema.md`).

## Status

**Read-only canonical anchor.** Phase 4 Captain L authors `commerce-stripe.md` + `booking-calcom.md` referencing this file by path — Captain L does not duplicate or modify the schema. Future commerce-adapter Captains (Shopify, Lemon Squeezy, Paddle, Snipcart, Saleor — Phase 10 expansion) likewise reference this schema. Any schema evolution flows through a General-reviewed prep packet (this file), not through individual adapter files.

> Source: `Workstreams/website-builder/commerce/DESIGN-payment-providers.md` § "Payment provider config schema" (~lines 398-435). Quoted verbatim below.

## Canonical schema

`.website-builder/payment-config.yaml`:

```yaml
primary_provider: stripe
providers:
  - name: stripe
    enabled: true
    api_key_env: STRIPE_SECRET_KEY
    publishable_key_env: STRIPE_PUBLISHABLE_KEY
    webhook_secret_env: STRIPE_WEBHOOK_SECRET
    payment_methods: [card, apple_pay, google_pay, sepa, ideal, twint, klarna]
    currencies: [USD, EUR, GBP, CHF]
    test_mode: false
    test_keys_env:
      api_key: STRIPE_TEST_SECRET_KEY
      publishable_key: STRIPE_TEST_PUBLISHABLE_KEY

  - name: paypal
    enabled: true
    client_id_env: PAYPAL_CLIENT_ID
    client_secret_env: PAYPAL_CLIENT_SECRET
    payment_methods: [paypal, pay_later]
    currencies: [USD, EUR, GBP, CHF]

  - name: mollie
    enabled: false
    # ...

regional_overrides:
  CH:
    primary: stripe   # forces TWINT-enabled flow
    secondary: paypal
  NL:
    primary: mollie   # iDeal-cheap
    secondary: stripe
```

> End verbatim quote from `DESIGN-payment-providers.md`.

## Field meanings

One-sentence explanations of each key. Adapter files do NOT re-explain these — they reference this section by anchor.

### Top-level keys

| Field | Purpose |
|---|---|
| `primary_provider` | The default payment provider used when no regional override applies. String; one of the values in `providers[].name`. |
| `providers[]` | List of payment providers configured for this site. Each provider has its own subfield set (see below). Multiple providers may be enabled simultaneously (e.g., Stripe + PayPal). |
| `regional_overrides` | Per-region overrides for `primary_provider` + a secondary fallback. Region keys are ISO 3166-1 alpha-2 codes (e.g., `CH`, `NL`, `DE`). |

### Per-provider keys (provider-specific)

| Field | Purpose |
|---|---|
| `name` | The provider identifier. Canonical values per `DESIGN-payment-providers.md`: `stripe`, `mollie`, `paypal`, `square`, `klarna`. TWINT is NOT a separate provider — it's a payment method enabled inside Stripe (or other Stripe-bridged platforms). |
| `enabled` | Boolean — whether this provider is wired and live. When `false`, the provider stays in config but is not invoked at checkout. |
| `api_key_env` | Env var name (not the secret value) pointing to the provider's primary server-side secret key. Stored in 1Password per `secrets-conventions.md`. Stripe: `STRIPE_SECRET_KEY`. |
| `publishable_key_env` | Env var name for the provider's browser-safe key (when applicable). Stripe + Square: yes. Mollie + PayPal: not applicable. |
| `webhook_secret_env` | Env var name for the provider's webhook signature verification secret. Required for any provider with webhook callbacks. Per Captain L's adapter file, webhook handlers MUST verify signatures — refusing to ship without verification per `DESIGN-commerce-stripe-checkout.md` lines 251-252. |
| `client_id_env` / `client_secret_env` | Env var names for OAuth-style provider auth (PayPal uses these). Stored in 1Password. |
| `payment_methods[]` | List of payment-method identifiers the provider should expose at checkout. Canonical values: `card`, `apple_pay`, `google_pay`, `sepa`, `ideal`, `bancontact`, `twint`, `klarna`, `paypal`, `pay_later`, `afterpay`, `alipay`, `wechat_pay`, etc. The actual rendered set at checkout is the intersection of (provider's enabled methods) × (current transaction's currency support). |
| `currencies[]` | List of ISO 4217 currency codes this provider is configured to charge in. Cross-checked against transaction currency at session creation. |
| `test_mode` | Boolean — whether to use the provider's test-mode keys + sandbox endpoints. Default `false` for production; flip to `true` during Phase 24a rehearsal. |
| `test_keys_env` | Nested map of env var names for test-mode credentials. Per `DESIGN-commerce-stripe-checkout.md` lines 248: agent enforces explicit user confirmation before flipping from test keys to live keys. |

### `regional_overrides` keys

Each region key (ISO 3166-1 alpha-2) maps to:

| Field | Purpose |
|---|---|
| `primary` | The provider to prefer for transactions originating from this region. Per the `DESIGN-payment-providers.md` decision tree (lines 22-52): CH → Stripe (for TWINT); NL → Mollie (for iDeal); DACH → Stripe; etc. |
| `secondary` | A fallback provider for the same region. Used when the primary provider rejects the transaction or for user-choice "pay with X instead" flows. |

## TWINT contract — non-negotiable for CH-audience projects

Per BUILD-strategy.md Phase 4 DoD line 202 + `commerce-adapters/README.md` § "TWINT-for-Switzerland — non-negotiable rule" + `DESIGN-payment-providers.md` § "TWINT — CRITICAL for Switzerland" (lines 222-274):

**When `project.yaml.audience_regions` includes `CH`, the `payment-config.yaml` MUST satisfy ALL of:**

1. **A `stripe` provider entry** must exist in `providers[]` with `enabled: true`. (Reason: TWINT integrates natively only via Stripe; other providers either don't support TWINT or use a Stripe-bridge — `payment-config.yaml` always names Stripe as the provider that handles TWINT.)

2. **The Stripe provider's `payment_methods[]` must include `twint`.** (Reason: this is what the agent's Checkout Session / Payment Intent creation code reads to populate `payment_method_types` per `DESIGN-commerce-stripe-checkout.md` lines 159-165.)

3. **The Stripe provider's `currencies[]` must include `CHF`.** (Reason: TWINT is CHF-only per `DESIGN-payment-providers.md` line 226; the agent's per-currency payment-method picker only renders TWINT when transaction currency is CHF.)

4. **`regional_overrides.CH.primary` must be `stripe`.** (Reason: forces the TWINT-enabled flow for Swiss-origin transactions per the canonical schema's CH override.)

5. **Captain L's stripe-fixture (`tests/commerce-adapters/stripe/fixture/`) MUST embody this contract.** Per `tests/commerce-adapters/README.md` § "TWINT-required fixture rule": the fixture's `project.yaml.audience_regions: [CH]` plus `payment-config.yaml` matching the above 4 conditions. `expected.yaml.phase_24b.twint_enabled: true` + `expected.yaml.phase_24b.chf_currency_enabled: true` close the validation loop.

**Validation contract.** A future testing INST (Phase 5+ test-runner integration scope per `tests/adapters/README.md` line 116) will enforce this contract programmatically: load `project.yaml`; if `audience_regions` includes `CH`, walk `payment-config.yaml` and assert all 5 conditions. Failure = phase 4 DoD violation.

**Pause-and-report.** If the user's project has CH audience and the user picks a TWINT-incompatible commerce adapter (Paddle / Gumroad / Sellfy / Snipcart / Lemon Squeezy direct), the phase-24a/b skill MUST surface a critical decision per `commerce-adapters/README.md` § "TWINT-for-Switzerland — non-negotiable rule" point 4: either switch adapter OR accept losing TWINT (with explicit user confirmation of the ~35%+ Swiss revenue impact).

## Adapter file integration pattern

Every commerce + booking adapter file MUST cross-link this schema in two places:

1. **§ "Phase 24a/24b/24c integration"** — when the adapter's phase-24b sub-phase recipe describes payment-method enablement: link to this file with the anchor reference (e.g., `> Canonical payment-config.yaml schema: see [commerce-adapters/payment-config-schema.md](commerce-adapters/payment-config-schema.md)`).

2. **§ "TWINT-for-Switzerland callout"** — when the adapter documents TWINT support: link to this file's § "TWINT contract" subsection (e.g., `> TWINT contract: see [commerce-adapters/payment-config-schema.md § TWINT contract](commerce-adapters/payment-config-schema.md#twint-contract--non-negotiable-for-ch-audience-projects)`).

The cross-link pattern lets the phase-24 skill resolve from the active adapter file to the canonical schema in a single hop. Future Captains adding new commerce / booking adapters follow the same pattern.

## Future-adapter rule

All future commerce adapter Captains (Shopify in Phase 10, Lemon Squeezy in Phase 10, Paddle in Phase 10, Snipcart in Phase 10, Saleor in Phase 10, etc.) reference THIS file for the canonical `payment-config.yaml` schema. They do NOT inline the schema in their adapter files; they cross-link.

Adapter-specific provider configurations layer on top (e.g., a future `commerce-shopify.md` would document Shopify Payments as a provider in `payment-config.yaml.providers[]` following the same field shape), but the schema's structure — `primary_provider` / `providers[]` / `regional_overrides` — is locked in this file.

When a new payment provider is added (e.g., a future Asian payment provider for a new market), the additive change happens HERE (this file gets a new entry under § "Per-provider keys") + the relevant commerce adapter's payment-method enumeration. The schema's top-level shape does not change.

## See also

- `Workstreams/website-builder/commerce/DESIGN-payment-providers.md` — source design doc; this file is the verbatim-extract canonical anchor for the schema portion
- `Workstreams/website-builder/commerce/DESIGN-commerce-stripe-checkout.md` — Stripe-specific integration patterns; consumes this schema
- `Workstreams/website-builder/commerce/DESIGN-booking-calcom.md` — Cal.com Stripe-bridge for TWINT-on-paid-bookings; consumes this schema
- `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` — phase 24b contract; this schema is phase 24b's primary output artifact (per phase-contracts line 173: *"Output: `payment-config.yaml` + transaction-test report."*)
- `Workstreams/website-builder/BUILD-strategy.md` Phase 4 DoD line 202 — *"TWINT path validates on Stripe Checkout (CH-region simulation)"* — the contract this schema's TWINT section makes concrete
- `commerce-adapters/README.md` — commerce + booking adapter schema (sibling Phase 4 Captain 0 prep file); both schemas' § "TWINT-for-Switzerland callout" reference this file
- `tests/commerce-adapters/README.md` — per-commerce + booking adapter test fixture convention (sibling Phase 4 Captain 0 prep file); the TWINT-required fixture rule embodies this schema's TWINT contract
- `.claude/rules/secrets-conventions.md` — secrets handling for env vars referenced by this schema (`*_env` fields point to env var names; secret values via 1Password)
