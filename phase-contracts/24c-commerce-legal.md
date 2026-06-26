---
phase: "24c"
name: Commerce-specific legal
group: pre-launch
pipeline_section: pre-launch
skill: wb-prelaunch
prev_phase: "24b"
next_phase: 25
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/commerce/DESIGN-commerce-stripe-checkout.md
  - Workstreams/website-builder/commerce/DESIGN-payment-providers.md
---

# Phase 24c — Commerce-specific legal *(only if transactional)*

> The legal pages a site that takes money must have, distinct from the general legal pages phase 25 produces. Refund policy, returns, shipping terms, terms-and-conditions of sale, SCA/3DS disclosure, and the jurisdiction-specific commerce regulation the user actually falls under — EU consumer-rights 14-day withdrawal, Swiss VAT, US sales-tax nexus, UK consumer law. The phase where "I take payment" becomes "I take payment lawfully." The agent refuses to deploy the commerce flow without these pages in place and linked from checkout, and it refuses a copy-pasted refund policy that does not match what the user actually does.

## Mission

Phase 24a stood up the platform; 24b wired the payment rails. 24c closes the commerce branch by making the transaction *lawful for the user's jurisdiction*. This is the last commerce sub-phase — the chain is 24 → 24a → 24b → 24c → 25 — and it rejoins the main pipeline at phase 25 (general legal pages: privacy, general T&Cs, imprint, cookie consent). The split is deliberate: 24c owns the legal surface that *only exists because money changes hands* (refund policy, returns, shipping, sale-specific T&Cs, SCA disclosure, consumer-rights and tax obligations); phase 25 owns the legal surface every site needs whether it sells anything or not.

The discipline of this phase is **jurisdiction-correctness and truthfulness**. Two failures the agent refuses: a generic copy-pasted refund/returns policy that does not match the user's actual practice (a 30-day-return template on a site that sells non-refundable digital downloads is worse than no policy — it is a promise the user will break), and a commerce flow that deploys without the commerce-legal pages existing and linked from the checkout. The agent does not invent the user's policy; it extracts the user's *actual* terms (what they really do about refunds, what they really ship, what their real cancellation window is) and shapes them into compliant pages — and it surfaces, loudly, the jurisdiction obligations the user may not know they have (EU's mandatory 14-day cooling-off, Switzerland's CHF 100,000 VAT threshold, US sales-tax nexus, the imprint that DACH and TWINT both require).

This is heavy-research work. There is no website-builder design doc that pre-writes legal copy (correctly — legal text must be jurisdiction-current and user-specific, not templated stale). The agent fetches current jurisdiction guidance via `WebFetch`/`WebSearch` at authoring time, cites it, and produces pages the user reviews. The agent is explicit, every time, that it is **not a lawyer and these pages are a structured, current-guidance-informed starting point the user should have reviewed by a professional for anything consequential** — and it still produces them, because a muggle launching a paid site with *no* refund policy is in a worse position than one with a careful, sourced, customized draft.

## Entry conditions

- Phase 24b (payment provider wiring) complete. `.website-builder/payment-config.yaml` exists — the agent reads it to know which SCA/3DS disclosure the build needs (EU/Swiss flows require SCA-context language; a US-only flow does not), which payment methods are live (the methods disclosed in the T&Cs of sale must match what is actually offered), and whether the build is Merchant-of-Record or user-as-merchant (Stripe = user-as-merchant; tax/refund liability is the user's — drives the depth of the tax and refund sections).
- `.website-builder/commerce-config.yaml` (24a) — what the user actually sells (physical goods → shipping/returns sections; digital → download/license terms + the digital-content withdrawal exception; services/bookings → cancellation/no-show policy).
- `.website-builder/project.yaml` audience + the user's own jurisdiction — drives which legal regime applies (EU consumer-rights directive, Swiss law, UK consumer law, US state sales tax). The agent reads both the audience region *and* the seller's establishment region; they can differ and both matter.
- Phase 25 (general legal) has *not* run yet — 24c precedes it. 24c writes commerce-legal pages and records, in its output, the dependencies phase 25 must satisfy (the general T&Cs, privacy, imprint, and cookie consent that the commerce flow also leans on) so phase 25 cannot miss them.

## What Claude must establish

The commerce-specific legal pages, jurisdiction-correct, truthful to the user's actual practice, existing on the site and linked from the checkout flow. The work product:

1. **Refund / cancellation policy** — the user's *actual* policy, extracted by conversation, shaped into clear page copy. For physical goods: return window, condition requirements, who pays return shipping, refund timing. For digital: the policy honestly stated (often "no refunds on delivered digital goods" — which is *legal* in the EU only if the user got the explicit pre-purchase consent-to-immediate-supply that waives the withdrawal right; the agent surfaces this exact mechanism rather than letting the user assume "digital = no refunds"). For bookings: the cancellation window and no-show terms (mirrors what 24a configured in Cal.com).
2. **Returns / shipping terms** (physical goods only) — shipping destinations, timeframes, costs, customs/duties responsibility, who bears loss in transit.
3. **Terms & Conditions of sale** — distinct from phase 25's general T&Cs. The contract of the sale itself: what is being sold, price + currency + tax treatment, payment methods accepted (must match `payment-config.yaml`), delivery, the consumer's statutory rights, dispute/chargeback handling, governing law.
4. **SCA / 3DS disclosure** — for EU/EEA/UK/Swiss-card flows, the customer-facing language explaining the authentication step and, for any off-session/subscription billing, the merchant-initiated-transaction consent (explicit authorization, expected frequency, amount basis) that 24b's `off_session` technical flag legally requires.
5. **Jurisdiction-specific commerce regulation** — the sections the user's regime mandates (see the jurisdiction sub-section below): EU 14-day withdrawal + pre-contractual disclosure, Swiss VAT registration/display obligations, US sales-tax nexus disclosure, UK consumer-rights statements.
6. **Pages live + linked from checkout.** Not drafts in a folder — actual pages in the user's project, reachable from the checkout flow (a "by completing this purchase you agree to [Terms of Sale] and [Refund Policy]" link at the point of payment).

The agent updates `.website-builder/project.yaml.current_phase` to `25` upon completion. 24c is the last commerce sub-phase; it rejoins the main pipeline at phase 25.

## Jurisdiction-specific commerce regulation (the research-heavy core)

The agent fetches current guidance fresh and produces only the sections the user's actual regime requires. Key regimes for this product's audience:

### EU / EEA — Consumer Rights Directive

Confirmed current (2026-05-18 fetch, European Commission consumer-rights source): distance contracts carry a **14-day right of withdrawal** (cooling-off period) — the consumer can cancel within 14 days without giving a reason, using the model withdrawal form (Annex I(B)). Pre-contractual information obligations: the trader must disclose core information *before* purchase, including the functionality and interoperability of digital content. **Pre-ticked boxes for extra charges are prohibited.** Payment-surcharge and premium-hotline-fee rules apply. Refund obligation follows a valid withdrawal. A key, frequently-missed mechanism the agent surfaces: the 14-day withdrawal right *can* be waived for digital content delivered immediately, **but only if the consumer gave express prior consent and acknowledged losing the withdrawal right** — so "no refunds on digital products" is lawful in the EU only with that specific captured consent, which the agent wires into the checkout copy (it is not optional boilerplate). Update on the horizon: Directive (EU) 2024/825 (Empowering Consumers for the Green Transition) enters force 27 September 2026, adding sustainability-information requirements — the agent flags this as a near-term obligation for product sellers.

### Switzerland — VAT + commerce

Confirmed current (2026-05-18 WebSearch, Quaderno/Avalara/Marosa/Anrok): the Swiss standard VAT rate is **8.1%** on sales to Swiss customers (including B2B digital services). The registration duty triggers at **CHF 100,000 annual worldwide turnover** from taxable/zero-rated supplies for businesses making *any* taxable supply in Switzerland — this catches foreign digital sellers (SaaS, streaming, online media) the moment global turnover exceeds CHF 100,000 and they sell into Switzerland, regardless of physical presence. Registration is with the Swiss Federal Tax Administration; **non-Swiss businesses need a Swiss fiscal representative**; VAT returns are typically quarterly via the FTA portal, due 60 days after quarter-end. The revised law introduces the **deemed-supplier** concept for electronic platforms facilitating goods. Note: Switzerland has **no statutory distance-selling cooling-off right** equivalent to the EU's 14 days (the Swiss Code of Obligations is more limited) — the agent does not import the EU 14-day language into a Swiss-only flow, and surfaces this difference rather than blurring the two regimes. The agent also connects the Swiss imprint requirement (phase 25) and Stripe's TWINT merchant prerequisites (phase 24b) to the Swiss-VAT business-identification obligations — they are the same business-transparency surface.

### US — sales-tax nexus

No federal cooling-off for general online sales (some state-level exceptions). The dominant obligation is **state sales-tax nexus** post-*Wayfair*: economic nexus thresholds vary by state (commonly $100,000 in sales or 200 transactions). The agent surfaces that the user is responsible for tax collection/remittance unless using Stripe Tax (+0.5%, automates calculation but not liability) or a Merchant-of-Record platform (Lemon Squeezy/Paddle — expansion). It does not produce a 50-state tax matrix; it surfaces the obligation and the two ways to discharge it, and recommends professional advice for multi-state sellers.

### UK — Consumer Contracts Regulations

Post-Brexit the UK retains a 14-day cancellation right closely modelled on the EU directive, with the same immediate-digital-supply consent mechanism. The agent treats UK like EEA for the withdrawal-right structure while sourcing UK-current guidance fresh.

The agent produces the regime(s) the user actually falls under (audience region + seller establishment), cites the fetched source for each, and never silently applies one regime's rules to a different jurisdiction.

## Gating rules

The agent refuses to advance / deploy when:

- **Commerce flow without commerce-legal pages in place + linked from checkout.** The defining gate. A working Stripe Checkout with no refund policy and no terms-of-sale link at the point of payment is not deployable. **Not overridable** — paid flows ship with their legal surface or they do not ship.
- **Copy-pasted policy that contradicts the user's actual practice.** A 30-day-return template on a no-refund digital-download site; a "free worldwide shipping" template on a Switzerland-only physical seller. The agent forces customization: it extracts what the user *actually does* and refuses to ship a policy that is a promise the user will break. **Not overridable** — an inaccurate policy is a legal liability, not a placeholder.
- **EU/Swiss/UK audience without the mandatory jurisdiction sections.** An EU-audience paid site missing the 14-day withdrawal information and the digital-supply-consent mechanism; a Swiss seller over the VAT threshold with no VAT treatment disclosed. The agent surfaces the obligation and produces the section. Overridable only with an explicit logged decision that the user is taking professional responsibility for the gap (e.g., "my lawyer is drafting this section separately") — never silently skipped.
- **SCA disclosure missing for an EU/Swiss off-session/subscription flow.** 24b wired `off_session`; the merchant-initiated-transaction consent language is legally required for it. The agent will not let a subscription-billing EU flow deploy without the consent disclosure. Not overridable.
- **Tax obligation unsurfaced.** A Swiss seller plausibly over CHF 100,000, or a multi-state US seller, with no tax position taken. The agent does not file taxes for the user, but it refuses to let the user launch *unaware* — it surfaces the threshold and the discharge options and records the user's acknowledged position.

Override (where available) requires an explicit decision doc in `.website-builder/decisions/` recording the user's informed acceptance and, where relevant, that professional review is being handled separately.

## Tools and skills used

- **`WebFetch`** — **mandatory at this phase**: current EU consumer-rights commerce guidance (European Commission consumer-contract-law canonical) and current Swiss VAT rules for digital sales (admin.ch / FTA canonical, with reputable secondary sources where the primary 404s). Cited per-jurisdiction in `## Reference materials`.
- **`WebSearch`** — to surface current jurisdiction specifics the canonical pages do not directly answer (Swiss VAT threshold + fiscal-representative rule; US economic-nexus thresholds; the 2024/825 green-transition date). Used when a primary source is unreachable (the agent treats a 404 on a canonical legal source as a Tier-2 fall-back, not a reason to use stale training data — it WebSearches reputable current sources and cites them).
- **`Edit` / `Write`** — to write the legal pages into the user's project (per stack — MDX/markdown page, WordPress page, Framer page) and to wire the checkout-flow links.
- **`AskUserQuestion`** — the core tool of this phase. The user's *actual* refund/returns/cancellation practice, what they really ship and where, their business jurisdiction, whether they have professional legal support. The agent extracts the user's real terms; it does not invent them.
- **`Read`** — `payment-config.yaml` (SCA/methods/MoR-status — drives which disclosures are needed), `commerce-config.yaml` (what is sold — drives which sections apply), `project.yaml` (audience + seller jurisdiction).

No subagent spawn. `wb-prelaunch` phase-group skill carries the commerce branch (Decision 64 — no separate commerce skill). The cross-phase contract: 24c's commerce-legal pages and phase 25's general-legal pages compose into one coherent legal surface; 24c records the phase-25 dependencies (general T&Cs, privacy, imprint, cookie consent the commerce flow also leans on) in its output so phase 25 cannot miss them.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| Commerce-legal pages in the user's project | Per stack convention; one page per concern (refund, returns/shipping, terms-of-sale) or a combined commerce-terms page, linked from checkout | The live, jurisdiction-correct, user-truthful legal surface for the transaction |
| `.website-builder/audit/COMMERCE-LEGAL-REPORT.md` | Per-page: concern covered, jurisdiction regime applied, source cited (fetched URL + date), the user's actual-practice statement it reflects, the checkout link wired, the not-a-lawyer disclaimer recorded | Audit trail proving the pages are sourced, current, customized, and linked; read by phase 25 (which composes the general legal surface on top) and phase 29 (deploy gate) |
| `.website-builder/decisions/commerce-legal-{topic}.md` *(when applicable)* | Standard decision-doc frontmatter + body | Created when a jurisdiction gate was overridden with the user taking professional responsibility, or a contested policy choice was logged |

The `COMMERCE-LEGAL-REPORT.md` is the required artifact, and it explicitly lists the phase-25 dependencies so the general-legal phase inherits them.

## Common failure modes

**Copy-pasted refund policy that does not match reality.** The template says "30-day money-back guarantee"; the user actually sells non-refundable bespoke consulting hours. The agent extracts the *actual* policy by conversation and refuses to ship a promise the user will break — an inaccurate policy is worse than a careful honest one.

**"Digital products, so no refunds, simple."** Not in the EU. The 14-day withdrawal right applies to digital content *unless* the consumer gave express prior consent to immediate supply and acknowledged losing the withdrawal right. The agent surfaces this exact mechanism and wires the consent capture into checkout copy — "no refunds on digital" is lawful in the EU only with that captured consent, and the agent makes it real rather than letting the user assume.

**The Swiss seller does not know about the CHF 100,000 VAT threshold.** A growing Swiss (or foreign-into-Switzerland) digital seller crosses CHF 100,000 worldwide turnover and silently incurs a registration + fiscal-representative obligation. The agent surfaces the threshold, the 8.1% rate, the FTA registration and quarterly-return mechanics, and the fiscal-representative requirement for non-Swiss businesses — and records the user's acknowledged position rather than letting them launch unaware.

**EU and Swiss rules blurred together.** The agent imports the EU 14-day cooling-off into a Swiss-only flow (Switzerland has no equivalent statutory distance-selling withdrawal right) or vice-versa. The agent applies each regime only to the jurisdiction it governs, sources each separately, and surfaces the difference instead of producing one mushed "EU/Swiss" policy that is wrong for both.

**Pages exist but are not linked from checkout.** The refund policy is a page nobody can find from the point of payment. EU pre-contractual disclosure (and basic enforceability of the terms) requires the customer can see and agree to the terms *at* checkout. The agent wires the "by purchasing you agree to [Terms of Sale] / [Refund Policy]" link at the payment step, not just a footer link.

**The agent presents legal copy as authoritative.** The agent is not a lawyer; the pages are a current-guidance-informed, customized starting point. The agent records the not-a-lawyer disclaimer in the report and surfaces, for consequential commerce, that professional review is recommended — while still producing the pages, because a paid site with no policy is the worse failure.

**A canonical legal source 404s and the agent falls back to training data.** Legal rules change; stale training data on consumer law is a liability. When a primary source (admin.ch, the Commission page) is unreachable, the agent treats it as a Tier-2 tool fall-back: it WebSearches reputable *current* sources, cites them with the fetch date, and never silently substitutes its own (possibly outdated) knowledge.

**Subscription billing with no merchant-initiated-transaction consent.** 24b wired `off_session` for a subscription; the recurring charge legally needs recorded customer consent (authorization, frequency, amount basis). The agent ensures the consent disclosure exists in the sale terms and is captured at signup — the technical flag without the legal consent is incomplete.

## Reference materials

- **Design doc — Stripe Checkout commerce-legal sub-section:** `Workstreams/website-builder/commerce/DESIGN-commerce-stripe-checkout.md` § Phase 24c — commerce-specific legal (user-as-merchant tax burden, subscription disclosures, receipt/invoice)
- **Design doc — payment providers (MoR vs user-merchant, tax burden):** `Workstreams/website-builder/commerce/DESIGN-payment-providers.md` § Stripe (Stripe Tax +0.5%, user is merchant of record)
- **Design doc — Cal.com commerce-legal (paid bookings):** `Workstreams/website-builder/commerce/DESIGN-booking-calcom.md` § Phase 24c — commerce-specific legal (cancellation/no-show, service-contract T&Cs, GDPR processor disclosure)
- **Design doc — phase pipeline source:** `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 24c (seed) — note the explicit pairing with phase 25 (general legal)
- **Phase 25 (the general legal surface 24c hands dependencies to):** `phase-contracts/25-legal-pages.md` § What Claude must establish
- **Phase 24b (the SCA/methods/off-session config 24c discloses):** `phase-contracts/24b-payment-provider.md` § SCA / 3DS jurisdiction sub-section
- **External research (loaded fresh 2026-05-18 for this contract):**
  - EU Consumer Rights Directive — https://commission.europa.eu/law/law-topic/consumer-protection-law/consumer-contract-law/consumer-rights-directive_en — 14-day withdrawal (Annex I(B) model form), pre-contractual disclosure incl. digital-content functionality/interoperability, prohibited pre-ticked boxes, payment-surcharge rules, Directive (EU) 2024/825 in force 2026-09-27. Confirmed 2026-05-18.
  - Swiss VAT (digital/e-commerce) — admin.ch / Swiss FTA canonical, corroborated via Quaderno/Avalara/Marosa/Anrok 2026 guides — 8.1% standard rate, CHF 100,000 worldwide-turnover registration threshold, mandatory fiscal representative for non-Swiss businesses, quarterly FTA returns due +60 days, deemed-supplier concept for platforms, no EU-equivalent statutory cooling-off. Confirmed 2026-05-18.
  - US sales-tax nexus — economic-nexus thresholds post-*Wayfair* (commonly $100k / 200 transactions, varies by state); discharge via Stripe Tax or MoR. Surfaced, not exhaustively templated.
- **Config/secrets discriminator (legal copy is not secret; provider names are config):** `.claude/rules/config-conventions.md`
- **Locked decision 54** (Stripe MVP, user-as-merchant tax model) — STATE doc: `Workstreams/website-builder/website-builder.md`

Freshness date for this contract: **2026-05-18**. Legal guidance changes; the agent re-fetches jurisdiction sources at session start when phase 24c is active and never relies on training-data knowledge of consumer/tax law that the fetched current source can correct.
