# Cal.com booking fixture — `booking-calcom.md` adapter validation (free-booking baseline)

> Phase 4 Captain L test fixture for the Cal.com booking adapter. Exercises the **free-booking-only** path; paid-CH-booking variant (Cal.com → Stripe → TWINT bridge chain) is deferred to Phase 10+ as `calcom-paid-ch/`.

## What this fixture tests

- **Adapter file:** [commerce-adapters/booking-calcom.md](../../../commerce-adapters/booking-calcom.md)
- **Adapter type:** booking (sells time — consultations + coaching; not products)
- **Stack pairing:** Next.js + shadcn (the strongest pairing per the adapter file's § "Stack pairings"; `@calcom/embed-react` Cal.com Atoms)
- **CMS:** `none` (file-based content; CMS is orthogonal to the booking surface)
- **Booking mode:** **free bookings only** (both event types are $0 — no payment processor bridge)

## Scenario

A solo independent consultant offers:
- 2 free event types: 30-min intro consult + 60-min coaching session (first session free)
- English-speaking international audience (US / GB / DE)
- Embedded on a Next.js site as the primary "Book a call" CTA

Audience excludes Switzerland because the TWINT contract for booking adapters requires paid CHF event types via the Stripe bridge — deferred to a future paid-CH variant fixture per Captain 0 spec.

## Why free-booking-only (Phase 4 scope vs Phase 10+ paid-CH variant)

Per `tests/commerce-adapters/README.md` § "calcom/ fixture":

- Free-booking is the most common Cal.com entry path for muggles (free intro consultations driving paid engagement separately).
- Paid-booking-with-TWINT requires Cal.com + Stripe + TWINT enablement — a 3-system bridge test that overlaps with the Stripe fixture's TWINT validation (already exercised at [tests/commerce-adapters/stripe/](../stripe/)).
- A `calcom-paid-ch/` fixture (Phase 10+ scope) would exercise the Cal.com → Stripe → TWINT bridge chain end-to-end with CHF event types, `audience_regions: [CH]`, and `expected.yaml.phase_24b_payment.twint_enabled: true` via the bridge.

For Phase 4: the adapter file documents the bridge chain (S7 callout); this fixture demonstrates the free-booking baseline; the paid-CH variant is deferred.

## What the fixture exercises

| Phase | Exercise | Verification anchor |
|---|---|---|
| 22 | Transactional flag set true (booking IS transactional, even when free) | `expected.yaml.phase_22_transactional` |
| 24a | Cal.com Cloud Free + 2 free event types + Google Meet + popup embed + webhooks | `expected.yaml.phase_24a_booking` |
| 24b | **NOT applicable** — no paid bookings, no payment processor bridge | `expected.yaml.phase_24b_payment.applicable: false` |
| 24c | Minimal legal: cancellation policy + GDPR/privacy (Cal.com listed as processor) | `expected.yaml.phase_24c_legal` |

## What the fixture deliberately does NOT exercise

- **Paid bookings + Stripe bridge + TWINT** — deferred to Phase 10+ `calcom-paid-ch/` variant. The S7 contract chain (Cal.com → Stripe → TWINT for CHF) is documented in the adapter file but not exercised in fixture.
- **PayPal bridge** — `tcs of service`, no-show fees, paid-engagement disclosures — not applicable for free-only sessions.
- **Imprint** — audience is en-US international; no DACH legal requirement.
- **Multi-staff round-robin** — solo consultant on Cloud Free tier; Teams tier features absent.
- **Cal.com Atoms full white-label** — fixture uses standard embed + brand-accent override; full white-label requires Organizations / Enterprise tier.
- **Self-hosted deployment** — Cloud Free tier is the muggle default; self-hosted variant would be `calcom-selfhost/` (future scope).
- **Runtime API calls** — fixture uses mock API key `cal_test_mock_xxx`; runtime is Phase 5+ scope.
- **Runtime calendar sync** — fixture declares calendar integration but does not actually connect; runtime is Phase 5+ scope.

## External setup required (Phase 5+ runner)

For Phase 5+ test-runner integration (deferred):

- **Cal.com sandbox account** + test-mode API key (Cloud Free tier acceptable)
- **Google sandbox calendar** for the calendar integration sync test
- **Mock booking flow:** Cal.com supports test-mode bookings; runner verifies booking creation + webhook delivery + email confirmation

For Phase 4 manual verification: **no external setup needed**. The fixture's config-schema shape-validity + embed code shape are what's verified by hand at General review.

## Cal.com MCP status (re-verified 2026-05-20)

Per the adapter file (`commerce-adapters/booking-calcom.md` § "API + MCP availability") + Captain L re-verification 2026-05-20:

- **No official Cal.com MCP.** Cal.com explicitly takes an API-first stance — confirmed via Cal.com's own blog post at https://cal.com/blog/best-mcp-servers: "you can either wrap the API calls using a custom MCP server or call the API directly through tool integrations."
- **NOT in Anthropic plugin catalog** (verified at https://claude.com/plugins 2026-05-20 — catalog has 150+ plugins including Stripe at 27,078 installs, GitHub at 246,383 installs; Cal.com absent).
- **Community FastMCP exists:** `Danielpeter-99/calcom-mcp` (https://github.com/Danielpeter-99/calcom-mcp) — MIT licensed, explicitly NOT affiliated with Cal.com, SSE transport, 8 MCP tools. Optional enhancement; not required.
- **Composio hosted MCP:** `mcp.composio.dev/cal` — alternative community path; optional.
- **Agent default:** REST API directly via Bash + curl, or Next.js stack-specific HTTP client. No MCP dependency at phase 24a.

This **CONFIRMS** the source design doc's line 94 ("No official MCP; agent uses REST API") and updates the Phase 3 stack-nextjs adapter's line 533 phrasing ("custom Claude connector — no install command") with concrete community paths.

## Cross-link to Stripe-bridge contract (for future paid-CH variant)

The TWINT-for-Switzerland contract for Cal.com paid bookings flows through the Stripe bridge, NOT directly. See:

- [booking-calcom.md § TWINT-for-Switzerland callout](../../../commerce-adapters/booking-calcom.md#twint-for-switzerland-callout) — full bridge chain explanation + PayPal incompatibility
- [commerce-stripe.md § TWINT-for-Switzerland callout](../../../commerce-adapters/commerce-stripe.md#twint-for-switzerland-callout) — Stripe-native TWINT (where the bridge terminates)
- [payment-config-schema.md § TWINT contract](../../../commerce-adapters/payment-config-schema.md#twint-contract--non-negotiable-for-ch-audience-projects) — 5-condition canonical contract
- [tests/commerce-adapters/stripe/](../stripe/) — sibling fixture where TWINT contract IS exercised end-to-end

## How to update this fixture when the adapter contract evolves

1. Re-read the adapter file (`commerce-adapters/booking-calcom.md`) — identify what changed.
2. Update `project.yaml` if audience / stack / paid-vs-free assumptions changed.
3. Update `commerce-config.yaml` if event-type schema, integrations, or embed modes changed.
4. Update `content/pages/cancellation-policy.md` + `privacy.md` if legal requirements changed.
5. Update `expected.yaml` to match — especially the `phase_24b_payment.applicable` flag and the future-variant scope notes.
6. Update this README with what changed + why.
7. If adding paid bookings, consider whether to upgrade this fixture or to author a separate `calcom-paid-*/` sibling.

## Cross-links

- Adapter file: [commerce-adapters/booking-calcom.md](../../../commerce-adapters/booking-calcom.md)
- Sibling adapter: [commerce-adapters/commerce-stripe.md](../../../commerce-adapters/commerce-stripe.md) (where TWINT is native — Cal.com paid bookings bridge here)
- Canonical schema: [commerce-adapters/payment-config-schema.md](../../../commerce-adapters/payment-config-schema.md) (referenced only for future paid variant)
- Fixture convention: [tests/commerce-adapters/README.md](../README.md)
- Sibling fixture: [tests/commerce-adapters/stripe/](../stripe/) (Stripe Checkout commerce; TWINT contract end-to-end)
- BUILD strategy Phase 4 DoD: `Workstreams/website-builder/BUILD-strategy.md` lines 187-209
