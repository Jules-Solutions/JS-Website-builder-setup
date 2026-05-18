# Reference — Jurisdiction legal (phases 24c + 25)

> Loaded for phase 24c (commerce-specific legal) and phase 25 (general legal pages). Legal guidance changes; the agent **re-fetches the canonical source at session start** when 24c/25 is active and **never relies on training-data law** the fetched current source can correct. A 404 on a canonical source is a Tier-2 fall-back: WebSearch reputable *current* sources, cite with the fetch date.
>
> Freshness baseline: **2026-05-18** (the phase contracts carry the same baseline cited verbatim in their `## Reference materials`).

## The not-a-lawyer discipline (applies to every page this skill produces)

The agent is not a lawyer. Every legal page is a **current-guidance-informed, user-specific starting point the user should have professionally reviewed for anything consequential** — and the agent still produces it, because a muggle launching a site with *no* policy is in a worse position than one with a careful, sourced, customized draft. Record the not-a-lawyer disclaimer in the audit report (`COMMERCE-LEGAL-REPORT.md` / `LEGAL-REPORT.md`) and surface, for consequential commerce, that professional review is recommended.

The agent does **not invent** the user's terms. It extracts the user's *actual* practice (refunds, shipping, cancellation, legal identity) by conversation (`AskUserQuestion`) and refuses to ship a policy that is a promise the user will break or an identity it made up.

---

## Phase 24c — commerce-specific legal regimes

The agent produces only the regime(s) the user actually falls under = **audience region + seller establishment region** (they can differ; both matter). Cite the fetched source per regime; never apply one regime's rules to a different jurisdiction.

### EU / EEA — Consumer Rights Directive

Confirmed current (2026-05-18, European Commission consumer-contract-law canonical):

- **14-day right of withdrawal** on distance contracts — the consumer can cancel within 14 days without giving a reason, using the model withdrawal form (Annex I(B)). Refund obligation follows a valid withdrawal.
- **Pre-contractual information obligations** — the trader must disclose core information *before* purchase, including the functionality and interoperability of digital content. **Pre-ticked boxes for extra charges are prohibited.** Payment-surcharge and premium-hotline-fee rules apply.
- **The digital-content waiver (frequently missed — surface it explicitly).** "No refunds on digital products" is lawful in the EU **only if** the consumer gave *express prior consent to immediate supply* AND *acknowledged losing the withdrawal right*. The agent wires this exact consent capture into the checkout copy — it is not optional boilerplate. Do not let the user assume "digital = no refunds".
- **EU Withdrawal-Button — Directive (EU) 2023/2673 (the 2026 obligation, NOT in the original 24c contract — surface it).** Amends the Consumer Rights Directive. Online retailers selling to EU consumers must provide a **clearly visible electronic "withdraw/cancel my contract" function** and clearer in-journey withdrawal-rights information. Member-state transposition deadline **19 December 2025**; obligations **apply from 19 June 2026**. This is a near-term, concrete UI obligation for any EU-audience transactional site — the agent surfaces it, wires the withdrawal button into the post-purchase / account flow where the regime applies, and logs the user's awareness. (Applies to non-EU businesses selling into the EU too.)
- **Directive (EU) 2024/825 (Empowering Consumers for the Green Transition)** — in force **27 September 2026**, adds sustainability-information requirements; flag as a near-term obligation for product sellers.

### Switzerland — VAT + commerce

Confirmed current (2026-05-18, admin.ch / Swiss FTA, corroborated Quaderno/Avalara/Marosa/Anrok):

- Standard VAT rate **8.1%** on sales to Swiss customers (incl. B2B digital services).
- Registration duty triggers at **CHF 100,000 annual worldwide turnover** from taxable/zero-rated supplies for any business making *any* taxable supply in Switzerland — catches foreign digital sellers the moment global turnover exceeds CHF 100,000 and they sell into Switzerland, regardless of physical presence.
- Registration with the Swiss Federal Tax Administration; **non-Swiss businesses need a Swiss fiscal representative**; VAT returns typically quarterly via the FTA portal, due 60 days after quarter-end. Revised law introduces the **deemed-supplier** concept for electronic platforms facilitating goods.
- **No EU-equivalent statutory distance-selling cooling-off right** (the Swiss Code of Obligations is more limited). Do **not** import the EU 14-day language into a Swiss-only flow; surface the difference rather than blurring the two regimes.
- The Swiss imprint (phase 25) + Stripe TWINT merchant prerequisites (phase 24b) + Swiss-VAT business-identification are **the same business-transparency surface** — connect them so the user produces it once, correctly.

### US — sales-tax nexus

No federal cooling-off for general online sales. Dominant obligation: **state sales-tax nexus** post-*Wayfair* — economic-nexus thresholds vary by state (commonly $100,000 in sales or 200 transactions). The user is responsible for collection/remittance unless using Stripe Tax (+0.5%, automates calculation not liability) or a Merchant-of-Record expansion platform (Lemon Squeezy/Paddle). Do not produce a 50-state matrix; surface the obligation + the two discharge paths; recommend professional advice for multi-state sellers.

### UK — Consumer Contracts Regulations

Post-Brexit the UK retains a 14-day cancellation right closely modelled on the EU directive, with the same immediate-digital-supply consent mechanism. Treat like EEA for the withdrawal-right structure while sourcing UK-current guidance fresh.

### Phase 24c work product

Refund/cancellation policy (the user's *actual* policy), returns/shipping (physical goods), Terms & Conditions *of sale* (distinct from phase 25's general T&Cs — must list the payment methods that match `payment-config.yaml`), SCA/3DS disclosure (+ the merchant-initiated-transaction consent for off-session/subscription), the jurisdiction sections the regime mandates, all **live + linked from checkout**. Output `.website-builder/audit/COMMERCE-LEGAL-REPORT.md` (per page: concern, regime applied, source cited URL+date, the user's actual-practice statement it reflects, the checkout link wired, the disclaimer recorded) which **explicitly lists the phase-25 dependencies** it hands forward.

---

## Phase 25 — general legal regimes

The surface every site needs whether it sells or not. "I don't sell anything" never becomes "I don't need legal pages": a non-transactional portfolio with a contact form + analytics still needs a privacy policy (the form collects personal data; analytics is a processor) and, if the owner is in or targets DACH, an imprint.

`prev_phase` is 24 if non-transactional, **24c if transactional** — read `project.yaml.transactional` to know which, and read `COMMERCE-LEGAL-REPORT.md`'s phase-25 dependency list if it ran.

### DACH imprint (Impressum) — non-negotiable for German-speaking jurisdictions

Confirmed current (2026-05-18 WebSearch). The imprint is **legally obligatory on every commercial website** published in or targeting Switzerland / Germany / Austria. Hard requirement, not a recommendation.

- **Switzerland** — basis: Federal Act against Unfair Competition (UWG/UCA) **Art. 3(1)(s)** — anyone offering goods/services online must provide clear, complete identity + contact including an email address. Required: full first+last name (natural persons); company/association name *as in the statutes and commercial register* + legal form (legal entities); full postal address; telephone and email. Placement: **footer link labelled "Impressum", reachable in ≤2 clicks from any page, published as text not an image**. Penalties: fines up to CHF 10,000, cease-and-desist, reputational damage. Same identity surface as Stripe TWINT onboarding (24b) + Swiss VAT (24c) — produce once, correctly.
- **Germany** — *Digitale-Dienste-Gesetz* (DDG, successor to TMG) *Impressumspflicht*: provider name + legal form, address, contact (phone/email), register entry + number where applicable, VAT ID where applicable, responsible person for journalistic-editorial content where relevant.
- **Austria** — *E-Commerce-Gesetz* (ECG) + *Mediengesetz*, comparable. A DDG-compliant imprint is generally compliant in AT/CH — but source each fresh rather than assuming.
- **revFADP (Switzerland)** — revised Federal Act on Data Protection (in force Sept 2023): the controller must inform data subjects of collection (drives the privacy policy's content for Swiss data subjects); max fine raised to **CHF 250,000** + extended criminal liability. Swiss data subjects have revFADP rights; EU data subjects have GDPR rights — address each regime for the data subjects it governs; do not produce one mushed policy.

**Gate (not overridable — statutory, fined):** a commercial DACH site without an imprint, or with an image-only / >2-clicks-buried imprint, does not pass phase 25.

### EU cookie consent — mandatory before non-essential cookies

Confirmed current (2026-05-18 WebSearch). EU ePrivacy Directive + GDPR require **prior, opt-in consent before any non-essential cookie or tracking technology loads**. 2026 enforcement is materially stricter — France's CNIL fined **Google €325M and Shein €150M in a single day in September 2025**, both for cookie violations. (Per EDPB Cookie Banner Task Force findings, over 35% of platforms still use interfaces that make rejection difficult.)

Valid-consent requirements the wiring must satisfy:

- **Prior** — the banner shows and non-essential cookies do **not** fire until opt-in. *This is the load-bearing technical fact.* The gate is the **network-level proof** (Playwright confirms the analytics/tracking cookie genuinely does not set before consent), NOT the banner's mere presence. The single most common cookie failure is a decorative banner over a cookie that already dropped on page load.
- **Equal prominence** — "Accept all" and "Reject all" on the **same layer**, equal visual weight (same size, colour, position). "Accept all" + a faint "Settings" link is invalid. A compliant 2026 banner typically has four visible controls: Accept all, Reject all, Customize, X (close).
- **Granular + revocable** — per-category choice (analytics / advertising / personalisation / social), a manage-preferences path, withdraw as easily as given (GDPR Art. 7(3) — a permanently accessible preference centre).
- **No invalid mechanisms** — no pre-ticked boxes, no consent-by-silence/scrolling/continued-browsing, no cookie walls, no consent bundled with other agreements.
- **Essential cookies exempt** (session/login/cart) — no consent needed but documented in the cookie policy. Classify the site's actual cookies (from `INTEGRATIONS-REPORT.md`) into essential vs non-essential; gate only the non-essential.

Implementation: pick a CMP appropriate to stack + scale — hosted/muggle-friendly (Cookiebot / CookieYes / Iubenda — auto-scan) or open-source/self-hosted (Klaro / a lightweight first-party banner). **If phase 24 chose cookieless analytics (Plausible / Fathom / Cloudflare Web Analytics — set no cookies), surface that the cleanest compliance is not setting non-essential cookies at all** — a cookieless site may need only a brief privacy-policy mention and no consent gate. Do not bolt an unnecessary banner onto a site that does not set the cookies a banner would gate.

**Gate (not overridable — statutory, actively fined in 2026):** an EU-reachable site that fires a non-essential cookie before consent, or shows a dark-pattern banner (unequal Accept/Reject, pre-ticked, cookie wall), does not pass phase 25. The compliance mechanism cannot itself be the violation.

### Phase 25 work product

Privacy policy (from the *real* `INTEGRATIONS-REPORT.md` + `FORMS-REPORT.md` — named processors, legal basis, retention, GDPR Arts. 15-20 / revFADP rights), terms of use *where the site's nature warrants them* (a pure brochure site may legitimately not need general T&Cs — make that call honestly; do not pad), imprint (DACH), cookie consent (real network-verified gating). Pages footer-linked, imprint ≤2 clicks, banner before any non-essential cookie. Output `.website-builder/audit/LEGAL-REPORT.md` including the **network-level cookie-consent proof** (cookie absent pre-consent, present post-opt-in) — the required artifact.

**Gate (not overridable):** legal pages skipped entirely ("I'll add legal later") is refused — a live site collecting form data with no privacy policy, or a DACH commercial site with no imprint, is an immediate fineable liability. Where the user's *specific content* is contested (a retention period, a T&Cs clause), log the position in `.website-builder/decisions/legal-{topic}.md` with the disclaimer + professional-review recommendation — but do not skip the page.

## Sources (confirmed 2026-05-18)

- EU Consumer Rights Directive — `https://commission.europa.eu/law/law-topic/consumer-protection-law/consumer-contract-law/consumer-rights-directive_en`; EUR-Lex summary; **Directive (EU) 2023/2673 withdrawal-button — apply from 19 June 2026, transposition by 19 Dec 2025** (Taylor Wessing / Lexology / REVER / Your Europe 2026 coverage); Directive (EU) 2024/825 in force 27 Sept 2026.
- Swiss VAT — admin.ch / Swiss FTA; 8.1%, CHF 100k worldwide-turnover threshold, mandatory fiscal representative for non-Swiss, quarterly FTA returns +60 days, deemed-supplier; no EU-equivalent cooling-off.
- Swiss imprint — UWG/UCA Art. 3(1)(s); full name (natural) / registered company name + legal form (entity), postal address, phone+email, footer "Impressum" ≤2 clicks, text not image, fines to CHF 10,000 (alpineexcellence.ch, hostpoint.ch, activemind.ch, snplegal.com). Swiss revFADP in force Sept 2023, controller-inform duty, max fine CHF 250,000.
- Germany/Austria imprint — DDG (ex-TMG) Impressumspflicht; Austrian ECG + Mediengesetz; DDG-compliant generally compliant AT/CH.
- EU cookie consent — ePrivacy + GDPR prior opt-in; EDPB Cookie Banner Task Force (Reject-All equal prominence, same layer); no pre-ticked/silence/cookie-wall/bundled; essential exempt-but-documented; 2026 enforcement CNIL Google €325M + Shein €150M Sept 2025 (cookiechimp.com, clym.io, cookieyes.com, consenteo.com, europa.eu/youreurope). GDPR Art. 7(3) withdrawal-as-easy-as-given.
- US sales-tax nexus — economic-nexus post-*Wayfair* (commonly $100k / 200 transactions, varies by state); discharge via Stripe Tax or MoR.
