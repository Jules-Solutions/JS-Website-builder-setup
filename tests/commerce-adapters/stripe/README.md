# Stripe Checkout fixture — `commerce-stripe.md` adapter validation

> Phase 4 Captain L test fixture for the Stripe Checkout commerce adapter. Embodies the **TWINT-required CH-region simulation contract** per `BUILD-strategy.md` Phase 4 DoD line 202.

## What this fixture tests

- **Adapter file:** [commerce-adapters/commerce-stripe.md](../../../commerce-adapters/commerce-stripe.md)
- **Adapter type:** commerce (sells products — courses + consulting; not bookings)
- **Stack pairing:** Next.js + shadcn (the strongest pairing per the adapter file's § "Stack pairings"; the Next.js Route Handler + webhook pattern)
- **Commerce mode:** Mode 2 — server-side Stripe Checkout Session (vs Mode 1 = Payment Links)
- **CMS:** `none` (file-based content; CMS is orthogonal to the Stripe commerce surface)

## Scenario

A Swiss knowledge-worker (Still Humans) sells:
- 2 cohort-based courses (one-time CHF 49 + CHF 149; bilingual EN/DE)
- 1 quarterly consulting subscription (CHF 299/quarter, recurring via Stripe subscriptions + Customer Portal)

Audience: primary Swiss (CHF, TWINT critical), secondary DACH (DE/AT, EUR), with PayPal as a legacy-trust secondary provider.

## Why CH-region + TWINT (S6 contract)

`project.yaml.audience_regions: [CH, DE, AT]` + `currencies: [CHF, EUR]` triggers the **TWINT-required path** per:

- `commerce-adapters/README.md` § "TWINT-for-Switzerland — non-negotiable rule"
- `commerce-adapters/payment-config-schema.md` § "TWINT contract — non-negotiable for CH-audience projects"
- `tests/commerce-adapters/README.md` § "TWINT-required fixture rule"
- `BUILD-strategy.md` Phase 4 DoD line 202

The fixture's `payment-config.yaml` embodies all 5 conditions of the TWINT contract:
1. Stripe provider entry with `enabled: true`
2. Stripe `payment_methods[]` includes `twint`
3. Stripe `currencies[]` includes `CHF`
4. `regional_overrides.CH.primary: stripe`
5. THIS fixture (per `tests/commerce-adapters/README.md` § "TWINT-required fixture rule")

The fixture's `expected.yaml.phase_24b_payment.twint_enabled: true` + `chf_currency_enabled: true` close the validation loop — Phase 5+ test runner will assert these fields programmatically (Phase 4 = manual verification at General review).

## What the fixture exercises

| Phase | Exercise | Verification anchor |
|---|---|---|
| 22 | Transactional flag set true from project init (not mid-flip) | `expected.yaml.phase_22_transactional` |
| 24a | Stripe Checkout Mode 2 with 3 products + 5 prices + Customer Portal | `expected.yaml.phase_24a_commerce` |
| 24b | Stripe + TWINT + CHF + EUR + PayPal secondary + regional overrides | `expected.yaml.phase_24b_payment` (TWINT assertions) |
| 24c | DACH legal: refund + TCs of sale + Imprint + subscription disclosure | `expected.yaml.phase_24c_legal` |

## What the fixture deliberately does NOT exercise

- **Catalog / browse / search UI** — out of scope for Stripe Checkout (payment-only); route to Shopify (Phase 10+ adapter) for catalog.
- **Inventory tracking** — Stripe doesn't manage stock; not exercised.
- **Shipping calculator** — digital products only; no shipping.
- **Stripe Elements custom checkout** — Mode 3 out of scope for this adapter; not exercised.
- **Runtime TWINT payment test** — requires Stripe-side TWINT simulator (Dashboard → Test mode → Payment method simulators); Phase 4 fixture exercises config-shape validity at schema level, runtime is Phase 5+ test-runner scope.

## External setup required (Phase 5+ runner)

For Phase 5+ test-runner integration (deferred):

- **Stripe sandbox account** + test-mode keys (`sk_test_*`, `pk_test_*`, `whsec_*`)
- **Domain verification mock** for Apple Pay / Google Pay (Stripe test mode supports unverified-domain Apple Pay / Google Pay)
- **TWINT test simulator** activated in Stripe Dashboard Test mode

For Phase 4 manual verification: **no external setup needed**. The fixture's config-schema shape-validity is what's verified by hand at General review.

## Stripe MCP integration (verified 2026-05-20)

- **Anthropic plugin:** `claude.com/plugins/stripe` — Anthropic-blessed plugin wrapping `@stripe/mcp` + shipping `stripe-mcp` subagent. Install: `claude plugin install stripe@anthropic`. 27,078 installations as of 2026-05-20.
- **Direct MCP:** local stdio via `npx -y @stripe/mcp@latest` OR remote HTTP at `https://mcp.stripe.com` (OAuth).
- **Fallback per `tool-dependency-discipline.md` Tier 2:** Stripe Node SDK + `docs.stripe.com` REST reference. Functional; loses canonical-pattern surface.

## Known platform-specific gotchas (NOT covered by this fixture)

- **TWINT max transaction = 5,000 CHF.** Fixture's largest single payment is CHF 299 (consult quarterly); well under the limit. For a fixture exercising the limit, future variant `stripe-twint-limit-edge/` (Phase 10+).
- **TWINT eligible merchant countries: 35 European countries** (per `docs.stripe.com/payments/twint`). Fixture's hypothetical Stripe account assumed Swiss; multi-country merchant scenarios deferred.
- **Stripe Tax (+0.5%) optional.** Fixture asserts `stripe_tax_optional: true` but does NOT enable it; the user remains MoR. A Stripe-Tax-enabled variant (Phase 10+) would exercise tax automation.
- **Customer Portal flow.** Fixture asserts `customer_portal_configured: true` but doesn't enumerate the Portal session creation endpoint output; runtime testing is Phase 5+ scope.

## How to update this fixture when the adapter contract evolves

1. Re-read the adapter file (`commerce-adapters/commerce-stripe.md`) — identify what changed.
2. Update `project.yaml` if audience/stack/currency assumptions changed.
3. Update `payment-config.yaml` if the canonical schema (`payment-config-schema.md`) added/changed fields — verify the 5 TWINT contract conditions still hold.
4. Update `commerce-config.yaml` if Mode / Customer Portal / webhook patterns changed.
5. Update `expected.yaml` to match — especially the `phase_24b_payment.twint_*` cells.
6. Update this README with what changed + why.

## Cross-links

- Adapter file: [commerce-adapters/commerce-stripe.md](../../../commerce-adapters/commerce-stripe.md)
- Canonical schema: [commerce-adapters/payment-config-schema.md](../../../commerce-adapters/payment-config-schema.md)
- Fixture convention: [tests/commerce-adapters/README.md](../README.md)
- Sibling fixture: [tests/commerce-adapters/calcom/](../calcom/) (Cal.com booking adapter; free-booking-only path)
- BUILD strategy Phase 4 DoD: `Workstreams/website-builder/BUILD-strategy.md` lines 187-209 (line 202 — TWINT path validates on Stripe Checkout (CH-region simulation))
