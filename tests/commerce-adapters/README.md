# Per-commerce-adapter test fixtures — convention

> Where Phase 4 (and subsequent) commerce + booking adapter Captains place their adapter-specific test fixtures. **Adapter-type-agnostic convention**; per-adapter fixtures land in subdirectories.
>
> Anchors: `Workstreams/website-builder/BUILD-strategy.md` Phase 4 DoD line 202 (*"TWINT path validates on Stripe Checkout (CH-region simulation)"*) + Phase 4 DoD line 203 (*"Per-CMS adapter test fixtures pass"* — the equivalent contract applies to commerce + booking) + `tests/adapters/README.md` § "How CMS / commerce adapter Captains use this convention (Phase 4+)" lines 131-135 (this file is the sibling that line predicts).
>
> Sibling convention: `tests/cms-adapters/README.md` (Phase 4 sibling). Reference convention: `tests/adapters/README.md` (Phase 3 — same shape, different scope: stack adapters).

## Directory layout

```
tests/commerce-adapters/
├── README.md                       # this file
├── stripe/
│   ├── fixture/                    # synthetic .website-builder/ scaffold
│   │   ├── project.yaml            # MUST include audience_regions: [CH] + CHF
│   │   ├── brand.yaml
│   │   ├── sitemap.yaml
│   │   ├── components.yaml
│   │   ├── commerce-config.yaml    # phase 24a output
│   │   ├── payment-config.yaml     # phase 24b output; MUST satisfy TWINT-required rule
│   │   ├── content/
│   │   │   ├── pages/
│   │   │   │   └── checkout.md
│   │   │   └── strings/
│   │   │       └── en.json
│   │   └── ...
│   ├── expected.yaml               # per-phase expected adapter output
│   └── README.md                   # per-adapter fixture notes (gotchas, run instructions)
└── calcom/
    ├── fixture/
    ├── expected.yaml
    └── README.md
```

Each commerce / booking adapter has its own subdirectory. Subdirectory name matches the adapter file basename **stripped of the type prefix**: `commerce-stripe.md` → `stripe/`; `booking-calcom.md` → `calcom/`. This mirrors the `tests/cms-adapters/` convention (`cms-none.md` → `none/`).

## Fixture baselines — commerce vs booking

Commerce and booking adapter fixtures use slightly different baselines because their phase-24 contracts differ:

| Adapter type | Baseline | Rationale |
|---|---|---|
| **Commerce** (e.g., `stripe/`) | `phase-24-complete` (or `phase-24a-complete` if 24b/24c are not exercised) | The fixture exercises the full commerce flow: platform setup (24a) + payment provider wiring (24b) + commerce-specific legal (24c). For the Phase 4 Stripe fixture, all three are exercised because TWINT validation requires the full 24b cycle (provider methods + currency + 3DS + regional override). |
| **Booking** (e.g., `calcom/`) | `phase-24a-complete` (free bookings) OR `phase-24-complete` (paid bookings) | Free-booking fixtures stop at 24a (no payment). Paid-booking fixtures go through 24b (Stripe bridge for TWINT-on-CHF) and 24c (cancellation + T&Cs of service + GDPR). For the Phase 4 Cal.com fixture, free bookings are sufficient for Phase 4 manual verification; a paid-booking variant is Phase 10+ scope unless Captain L authors it. |

Both fixture types still embed the upstream baselines (phase-11 stack + phase-12 CMS) — the commerce/booking adapter doesn't replace those; it layers on top.

## Minimum contents per adapter

Each per-adapter subdirectory MUST contain:

### `fixture/`

A synthetic `.website-builder/` scaffold representing the project state at the adapter's relevant baseline. Required content (commerce):

- `project.yaml` — minimal but valid; for commerce fixtures: `stack: <stack>`, `cms: <cms>` (often `none`), `transactional: true`, `audience_regions: [...]`, `currencies: [...]`, `default_language: en`
- `brand.yaml` — same shape as `tests/cms-adapters/` baseline
- `sitemap.yaml` — 3-5 pages including checkout / success / cancel where relevant
- `components.yaml` — minimum 2-3 components, including a buy-button or product-card-style component for commerce; embed-block for booking
- **`commerce-config.yaml`** — phase 24a output; declares the commerce platform + products + checkout flow. Schema per `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` phase 24a output line.
- **`payment-config.yaml`** — phase 24b output; declares enabled providers + methods + currencies + regional overrides. Schema per `commerce-adapters/payment-config-schema.md` (sibling Phase 4 Captain 0 prep file). For Stripe fixture, MUST satisfy the TWINT-required rule below.
- `content/pages/*.md` — minimal page MD covering at least: home / checkout-or-booking-page / success / cancel
- `content/strings/en.json` — minimal CDJSON

Booking-specific:

- `commerce-config.yaml.bookings` — event types + availability + calendar/video integration declarations (schema per `DESIGN-booking-calcom.md` § "Phase 24a/24b/24c integration (booking branch)")
- For paid bookings: `payment-config.yaml` with Stripe + TWINT for CHF event types

The fixture is **synthetic** — no real merchant data, no real Stripe account. Filler products / prices / event types; the contract is the *shape*, not the runtime behavior.

### `expected.yaml`

A declarative spec of what the commerce / booking adapter SHOULD produce at each pipeline phase. Schema (commerce):

```yaml
# tests/commerce-adapters/{adapter}/expected.yaml
fixture_baseline: phase-24-complete       # or phase-24a-complete for partial

expected_per_phase:
  phase_24a_commerce:
    platform_selected: <platform-name>    # stripe-checkout | shopify | lemon-squeezy | etc.
    products_created: [...]                # product slugs / names
    prices_created: [...]                  # price IDs (test-mode)
    checkout_flow_mode: <mode>            # payment-links | checkout-sessions | embedded
    success_url_set: true
    cancel_url_set: true
    test_mode_rehearsal: pass             # test card transaction succeeds

  phase_24b_payment:
    primary_provider: <provider-name>
    enabled_methods: [...]
    enabled_currencies: [...]
    webhook_configured: true
    webhook_signing_verified: true
    sca_3ds_verified_eu: true              # mandatory for EU
    domain_verified_apple_google_pay: true  # mandatory for Apple/Google Pay
    twint_enabled: <bool>                  # CRITICAL: see TWINT-required rule below
    chf_currency_enabled: <bool>           # CRITICAL: see TWINT-required rule below
    ideal_enabled: <bool>                  # mandatory if NL audience
    klarna_enabled: <bool>                 # mandatory if AOV > $100 + BNPL audience

  phase_24c_legal:
    refund_policy_present: true
    shipping_policy_present: <bool>        # true if physical products
    tcs_of_sale_present: true
    imprint_present: <bool>                # true if DACH
    subscription_disclosure_present: <bool>  # true if subscription mode
    receipt_format_configured: true

  phase_22_transactional:                   # if mid-flip per Decision 34
    transactional_change_logged: true       # .website-builder/decisions/transactional-change-{ts}.md

expected_limitations: [...]                 # adapter-specific limitations
expected_failure_modes_covered: [...]       # adapter-specific failure paths handled
```

Schema (booking — distinct sub-phase shape):

```yaml
# tests/commerce-adapters/{booking-adapter}/expected.yaml
fixture_baseline: phase-24a-complete       # or phase-24-complete for paid bookings

expected_per_phase:
  phase_24a_booking:
    platform_selected: <platform-name>    # cal-com | calendly | simplybook
    event_types_created: [...]            # event-type slugs
    availability_configured: true
    calendar_integration: <calendar>      # google | microsoft | apple | caldav
    video_integration: <video>            # zoom | google-meet | daily | whereby
    embed_mode: <mode>                    # inline | popup | floating-button
    test_booking_rehearsal: pass

  phase_24b_payment:                       # ONLY if paid bookings
    bridge_to_payment_processor: <processor>   # stripe | paypal
    twint_enabled: <bool>                  # CRITICAL for CHF event types
    chf_currency_enabled: <bool>           # CRITICAL for CHF event types
    paid_booking_rehearsal: pass

  phase_24c_legal:                         # ONLY if paid bookings (free bookings: minimal)
    cancellation_policy_present: true
    no_show_policy_present: <bool>
    tcs_of_service_present: true
    imprint_present: <bool>                # true if DACH
    gdpr_disclosure_present: true          # mandatory; booking data is personal data

expected_limitations: [...]
expected_failure_modes_covered: [...]
```

This is **executable test guidance** — Phase 4 Captain L authors it alongside the adapter files. Phase 5+ runner integration wires the actual diff-check; Phase 4 itself uses `expected.yaml` for manual verification at General review.

### `README.md` (per-adapter)

A short orientation file explaining:

- Which adapter file this fixture tests (`commerce-adapters/{commerce|booking}-{name}.md`)
- Which stack the fixture is paired with (commerce + stack pairings per the adapter file's `## Stack pairings` table)
- Any setup the test runner needs (Stripe sandbox account + test cards? Cal.com sandbox + test calendar? PayPal sandbox?)
- Known platform-specific gotchas the fixture doesn't cover (and where they're documented)
- How to update the fixture when the adapter's contract evolves

## TWINT-required fixture rule (CRITICAL)

Per BUILD-strategy.md Phase 4 DoD line 202 (*"TWINT path validates on Stripe Checkout (CH-region simulation)"*) + `commerce-adapters/README.md` § "TWINT-for-Switzerland — non-negotiable rule" + `commerce-adapters/payment-config-schema.md` § "TWINT contract — non-negotiable for CH-audience projects":

**The `tests/commerce-adapters/stripe/fixture/` MUST embody the TWINT contract.** Specifically:

### Required `project.yaml`

```yaml
# tests/commerce-adapters/stripe/fixture/project.yaml
stack: nextjs                              # or another TWINT-compatible stack
cms: none                                  # CMS choice is orthogonal to TWINT; pick any
transactional: true
audience_regions: [CH]                     # MANDATORY: triggers TWINT-required path
currencies: [CHF, EUR]                     # CHF MANDATORY; EUR optional
default_language: en
languages: [en, de]                        # optional but recommended for muggle realism (Swiss multilingual)
```

The `audience_regions: [CH]` is the trigger that activates the TWINT-required contract. Without it, the fixture is a generic Stripe fixture and the TWINT rule does not apply.

### Required `payment-config.yaml`

```yaml
# tests/commerce-adapters/stripe/fixture/payment-config.yaml
primary_provider: stripe
providers:
  - name: stripe
    enabled: true
    api_key_env: STRIPE_SECRET_KEY
    publishable_key_env: STRIPE_PUBLISHABLE_KEY
    webhook_secret_env: STRIPE_WEBHOOK_SECRET
    payment_methods: [card, apple_pay, google_pay, twint]   # MANDATORY: twint present
    currencies: [CHF, EUR]                                   # MANDATORY: CHF present
    test_mode: true                                          # fixture is test-mode
    test_keys_env:
      api_key: STRIPE_TEST_SECRET_KEY
      publishable_key: STRIPE_TEST_PUBLISHABLE_KEY

regional_overrides:
  CH:
    primary: stripe                        # MANDATORY: matches the TWINT contract point 4
    secondary: paypal                      # optional fallback
```

Schema authority: `commerce-adapters/payment-config-schema.md` (sibling Phase 4 Captain 0 prep file). Captain L's fixture references the schema; this file specifies the TWINT-specific cells.

### Required `expected.yaml.phase_24b` cells

```yaml
# tests/commerce-adapters/stripe/fixture/expected.yaml
expected_per_phase:
  phase_24b_payment:
    primary_provider: stripe
    enabled_methods: [card, apple_pay, google_pay, twint]
    enabled_currencies: [CHF, EUR]
    twint_enabled: true                    # MANDATORY: true (the CH-region-simulation contract)
    chf_currency_enabled: true             # MANDATORY: true
    stripe_account_required_for_live: true # surfaces the test→live cutover requirement
    sca_3ds_verified_eu: true              # mandatory for EU customers
    domain_verified_apple_google_pay: true # surface mandatory
    webhook_configured: true
    webhook_signing_verified: true
```

### Why this is the canonical Swiss validation

Per `DESIGN-payment-providers.md` § "TWINT — CRITICAL for Switzerland" lines 222-274:

- TWINT covers **~35%+ of Swiss e-commerce share** (~3.5M+ active users on ~8.5M Swiss population)
- TWINT is **CHF-only** — protocol constraint, not config — non-CHF transactions cannot use TWINT
- TWINT is **native via Stripe** — no separate aggregator, no second account; Stripe handles the TWINT-backend integration
- Sites that don't offer TWINT lose substantial Swiss revenue

The Phase 4 DoD's "CH-region simulation" requirement is the test-side embodiment of the home-market non-negotiable per `Workstreams/website-builder/website-builder.md` decision 26 (Switzerland home market) + decision 47 (TWINT priority). The `stripe/` fixture exercises this end-to-end at the config-schema level: a CH-audience project pre-configured with TWINT + CHF on Stripe, with the `expected.yaml.phase_24b.twint_enabled: true` cell asserting the contract.

A future testing INST (Phase 5+ test-runner integration) will enforce this contract programmatically: load `project.yaml`; if `audience_regions` includes `CH`, walk `payment-config.yaml` and assert TWINT + CHF + stripe primary. Failure = phase 4 DoD violation.

### Cross-link in adapter file

Captain L's `commerce-stripe.md` § "TWINT-for-Switzerland callout" + § "Phase 6.5 ingestion" MUST cross-link this fixture (e.g., `> Test fixture: tests/commerce-adapters/stripe/fixture/`) so the contract is visible from both ends of the adapter ↔ test boundary.

## Per-adapter fixture notes

### `stripe/` fixture — `commerce-stripe.md`

- `project.yaml.audience_regions: [CH]` — triggers the TWINT-required path (per the rule above)
- **Paired stack:** Next.js + shadcn — Captain L's adapter file documents all 8 stack pairings; the fixture exercises Next.js as the strongest pairing for Stripe Checkout's server-endpoint pattern. Other paired-stack fixtures are Phase 10+ scope.
- **Commerce mode:** Mode 2 (Stripe Checkout server-side Session) — exercises the API-driven flow with TWINT enabled. Mode 1 (Payment Links) is documented in the adapter file but not exercised by the Phase 4 fixture (simpler, less to validate).
- **Test rehearsal:** test-mode Stripe keys; standard Stripe test cards (`4242 4242 4242 4242` succeeds; `4000 0000 0000 9995` declines; etc.). TWINT test rehearsal at runtime requires Stripe-side TWINT test setup (Phase 5+ runner scope); Phase 4 manual verification confirms the config-schema declarations.
- **Phase 24c legal coverage:** include `content/pages/refund-policy.md` + `content/pages/tcs-of-sale.md` + (CH audience → DACH legal applicable) `content/pages/imprint.md`. Stub content; the fixture verifies presence + path, not content quality.
- **External setup required:** Phase 5+ runner integration needs a Stripe sandbox account + test-mode keys. Phase 4 manual verification does NOT need this; the fixture's config-schema shape-validity is what's verified by hand.

### `calcom/` fixture — `booking-calcom.md`

- `project.yaml.transactional: true` + free bookings (no paid event types) — exercises phase 24a fully, phase 24b skipped (no payment), phase 24c minimal (cancellation policy + GDPR; no T&Cs of sale)
- **Paired stack:** Next.js + shadcn — same rationale as stripe fixture. Cal.com's embed works on all 8 stacks; Next.js is the most-instrumented pairing.
- **Event types:** 2 event types — "30-min consultation" (30min, Google Meet, free) + "1-hour coaching" (60min, Google Meet, free). Fixture sets `price: 0` for both — paid-booking variant is Phase 10+ scope.
- **Calendar integration:** declared as `google` in `commerce-config.yaml.bookings`; not actually connected at fixture (no real Google OAuth). Phase 5+ runner scope includes sandbox Google account.
- **Embed mode:** popup (overlay on user's site) — the default per Cal.com docs.
- **Cal.com API key:** mock value in `.env.test` — the API key in the fixture is `cal_test_mock_xxx`. Actual API call is out of scope for Phase 4 manual verification; the fixture verifies the adapter's recipe shape + the embed-code snippet shape.
- **Phase 24b TWINT note:** since fixture has no paid bookings, `phase_24b_payment` is `n/a` in `expected.yaml`. A paid-booking variant fixture (Phase 10+) would exercise the Cal.com → Stripe → TWINT bridge chain (S7 callout) — for CHF event types, the bridge requires Stripe (not PayPal) as Cal.com's payment processor.
- **CH-region note:** the calcom fixture does NOT have `audience_regions: [CH]` because Cal.com's TWINT support is conditional on paid bookings + Stripe bridge, and this Phase 4 fixture exercises free bookings only. A future CH-paid-booking variant (`calcom-paid-ch/`) at Phase 10+ would carry CH region + Stripe bridge + TWINT validation.
- **External setup required:** Phase 5+ runner integration needs a Cal.com sandbox account + Google sandbox calendar. Phase 4 manual verification does NOT need this.

## What lives OUTSIDE per-adapter subdirectories

- **Shared fixtures** for protocol-level tests (handoff-spec JSON validation, payment-config schema validation) live at `tests/walkthroughs/` or `tests/` root — not here.
- **Plugin-level tests** (PreToolUse gating, phase-detection) live at `tests/test_pre_tool_use.py`. Not here.
- **Skill-level tests** live alongside their skills (`skills/wb-{group}/tests/`) when authored. Not here.
- **Stack-adapter fixtures** live at `tests/adapters/` (Phase 3 surface). Not here.
- **CMS-adapter fixtures** live at `tests/cms-adapters/` (Phase 4 sibling). Not here.

`tests/commerce-adapters/` is **specifically for commerce + booking adapter-output validation**.

## Out-of-scope for Phase 4 itself

The full **test runner integration** (CI hook wiring `tests/run-tests.sh` to load commerce / booking fixtures, invoke adapter phases, diff against `expected.yaml`) is **Phase 5+ scope** per `BUILD-strategy.md`. Captain L:

- Authors the `fixture/` + `expected.yaml` + `README.md` per their adapter (commerce + booking → 2 fixtures total)
- Runs **manual** verification: walk the fixture through pipeline phases 24a / 24b / 24c (commerce) and 24a / 24b-or-not / 24c-minimal (booking) mentally, confirms the adapter file would produce what `expected.yaml` claims
- Surfaces gaps in the adapter file (or the fixture) and resolves them before commit

Captain L does **not** need to wire the runner. That's a future INST.

## File naming

- Subdirectory names: kebab-case matching adapter slug (`stripe` / `calcom`; future: `shopify` / `lemon-squeezy` / `paddle` / etc.).
- Fixture file names: standard `.website-builder/` conventions (per `DESIGN-project-scaffold.md`) + commerce-specific files (`commerce-config.yaml`, `payment-config.yaml`).
- `expected.yaml`: exactly that filename.
- `README.md`: exactly that filename.

## See also

- `Workstreams/website-builder/BUILD-strategy.md` Phase 4 DoD line 202 — the TWINT-CH-simulation contract this fixture convention's TWINT-required rule satisfies
- `commerce-adapters/README.md` — commerce + booking adapter schema contract (sibling Phase 4 Captain 0 prep file)
- `commerce-adapters/payment-config-schema.md` — canonical `payment-config.yaml` schema (sibling Phase 4 Captain 0 prep file); referenced by the TWINT-required rule
- `tests/adapters/README.md` — Phase 3 stack-adapter fixture convention; this file follows the same shape
- `tests/cms-adapters/README.md` — sibling Phase 4 CMS-adapter fixture convention
- `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` — `.website-builder/` layout the fixtures mirror
- `Workstreams/website-builder/foundation/DESIGN-content-layers.md` — the 5-layer structure each fixture must contain
- `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` — phase 24a (commerce platform) + 24b (payment provider) + 24c (commerce legal) — the phases this fixture's `expected.yaml` validates
- `Workstreams/website-builder/commerce/DESIGN-commerce-stripe-checkout.md` — `commerce-stripe.md` source design doc
- `Workstreams/website-builder/commerce/DESIGN-payment-providers.md` — payment-provider matrix + TWINT critical section
- `Workstreams/website-builder/commerce/DESIGN-booking-calcom.md` — `booking-calcom.md` source design doc
- `Workstreams/website-builder/website-builder.md` — decision 26 (Switzerland home market) + decision 47 (TWINT priority) + decision 54 (Cal.com booking default)
- `tests/walkthroughs/` — sibling test surface (end-to-end pipeline dogfood, not per-adapter)
- `tests/run-tests.sh` — current Python test runner (does not yet load commerce-adapter fixtures; future INST)
