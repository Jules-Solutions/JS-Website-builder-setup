---
phase: 25
name: Legal pages
group: pre-launch
pipeline_section: pre-launch
skill: wb-prelaunch
prev_phase: 24
next_phase: 26
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/cross-cutting/DESIGN-secrets-and-keys.md
---

# Phase 25 — Legal pages

> The legal surface every site needs whether it sells anything or not: privacy policy, terms (where applicable), imprint (non-negotiable in DACH), and cookie consent (mandatory before any non-essential cookie in the EU). The phase where the site stops being a legal liability the moment it goes live. `prev_phase` is 24 (or 24c if the commerce branch ran — the agent reads `transactional` to know which). The agent refuses to skip legal pages entirely, refuses a generic copy-pasted privacy policy that does not describe the data the site actually collects, and treats the DACH imprint and EU cookie consent as hard requirements, not optional polish.

## Mission

By phase 25 the site is built, integrated (phase 24), and — if transactional — commerce-legal'd (phase 24c). What it still lacks is the legal surface that applies to *every* site: a privacy policy describing what data this specific site collects and through which integrations, terms of use where the site's nature warrants them, an **imprint** (legally mandatory for any commercial website published in the German-speaking jurisdictions — Switzerland, Germany, Austria), and **cookie consent** wired so that non-essential cookies do not fire before the user opts in (mandatory under the EU ePrivacy Directive + GDPR for any EU-reachable site that uses analytics/tracking).

The split with phase 24c is deliberate and the agent states it: 24c owns the legal surface that exists *only because money changes hands* (refund, returns, sale T&Cs, SCA disclosure, consumer-rights/tax). Phase 25 owns the legal surface that exists whether or not the site sells anything. A non-transactional portfolio with a contact form and Plausible analytics has no 24c but absolutely has a phase 25 — privacy policy (the contact form collects personal data; analytics is a processor) and, if the owner is in or targets DACH, an imprint. The agent does not let "I don't sell anything" become "I don't need legal pages."

The discipline is the same as 24c: **truthfulness and jurisdiction-correctness**. A copy-pasted privacy policy that claims the site uses cookies it does not use, or omits the analytics it does use, is worse than none — it is a false legal statement. The agent does not template a policy; it reads what phase 24 actually wired (which integrations, which cookies, which third-party processors), reads what forms phase 23 actually collect, and produces a privacy policy that describes *this site's actual data practice*. Same not-a-lawyer honesty as 24c: the pages are a current-guidance-informed, site-specific starting point the user should have professionally reviewed for anything consequential — and the agent still produces them, because a live site silently dropping analytics cookies with no consent banner and no privacy policy is the worse failure for a muggle.

Phase 24 (and 24c) recorded dependencies for this phase — the cookie-setting integrations that need consent gating, and the general-legal surface the commerce flow leans on. Phase 25 reads those dependency notes and closes them.

## Entry conditions

- Phase 24 (integrations) complete. `.website-builder/audit/INTEGRATIONS-REPORT.md` exists and — critically — records every cookie-setting integration with the flag that phase 25 must gate it behind consent. This is the input that makes the cookie-consent work concrete (the agent gates exactly the integrations that actually set non-essential cookies, not a generic "we use cookies" hand-wave).
- If the commerce branch ran: phase 24c complete, `.website-builder/audit/COMMERCE-LEGAL-REPORT.md` exists and lists the phase-25 dependencies (the general T&Cs / privacy / imprint / cookie-consent the commerce flow also leans on). The agent reads `project.yaml.transactional` to know whether to expect this input and which `prev_phase` it actually came from (24 if non-transactional, 24c if transactional).
- Phase 23 (forms) complete — `audit/FORMS-REPORT.md` tells the agent what personal data the site's forms collect (name, email, message, phone) so the privacy policy describes real collection, not assumed.
- `.website-builder/project.yaml` — the seller/owner jurisdiction and audience region. Both matter: an owner established in Switzerland needs a Swiss imprint regardless of audience; an EU audience triggers GDPR/ePrivacy cookie-consent regardless of where the owner is.

## What Claude must establish

The general legal pages, truthful to the site's actual data practice, jurisdiction-correct, live in the project, and (for cookie consent) functionally gating non-essential cookies. The work product:

1. **Privacy policy** describing *this site's actual data practice*: what personal data is collected (from which forms — sourced from `FORMS-REPORT.md`), through which integrations (from `INTEGRATIONS-REPORT.md` — named processors: "we use Plausible for privacy-friendly analytics" / "form submissions are processed by Formspree" / "we use Cal.com to schedule calls"), the legal basis, retention, the data subject's rights (access/rectification/erasure/portability — GDPR Arts. 15-20; the revFADP equivalents for Swiss data subjects), and how to exercise them. Generated from real inputs, not a template.
2. **Terms of use / terms of service** where the site's nature warrants them (a content site with user-generated comments, an app-shaped site, a site with accounts). A pure brochure site may legitimately not need general T&Cs — the agent makes that call honestly rather than padding the site with a contract nobody needs (and does not confuse this with 24c's *terms of sale*, which is a different document for transactional sites).
3. **Imprint** — for any commercial website where the owner is established in or targets Switzerland / Germany / Austria. See the DACH sub-section. This is **non-negotiable** for DACH; the agent does not let the user skip it.
4. **Cookie consent** — a consent mechanism wired so that **non-essential cookies do not fire until the user opts in**, with a banner that offers Accept and Reject at equal visual prominence, a manage-preferences path, and no dark patterns. See the cookie-consent sub-section. The agent wires this against the *actual* cookie-setting integrations phase 24 flagged — it is real gating, not a decorative banner.
5. **Pages live + discoverable.** Footer links, imprint reachable in ≤2 clicks from any page, cookie banner shown before any non-essential cookie loads.

The agent updates `.website-builder/project.yaml.current_phase` to `26` upon completion.

## DACH imprint sub-section (non-negotiable for the German-speaking jurisdictions)

Confirmed current (2026-05-18 WebSearch): the imprint (*Impressum*) is legally obligatory on every commercial website published in the German-speaking jurisdictions — Switzerland, Germany, Austria (and Belgium's German-speaking community). The agent treats this as a hard requirement, not a recommendation, whenever the site is commercial and the owner is established in or targeting DACH.

- **Switzerland** — basis: the Federal Act against Unfair Competition (UCA/UWG), Art. 3(1)(s) — anyone offering goods/services online must provide clear, complete identity and contact information including an email address. Required: full first + last name for natural persons; the company/association name *as in the statutes and commercial register* plus the legal form (full or abbreviated) for legal entities; full postal address; telephone and email (a means of direct, efficient communication). Placement: footer link labelled "Impressum", reachable in ≤2 clicks from any page, published as **text, not an image**. Penalties: fines up to CHF 10,000, cease-and-desist exposure, reputational damage. The same identity surface is what Stripe's TWINT onboarding (phase 24b) and the Swiss VAT business-identification (phase 24c) require — the agent connects them so the user produces it once, correctly.
- **Germany** — the *Digitale-Dienste-Gesetz* (DDG, the successor to the TMG) imposes a closely analogous *Impressumspflicht*: provider name + legal form, address, contact (phone/email), register entry + register number where applicable, VAT ID where applicable, and the responsible person for journalistic-editorial content where relevant.
- **Austria** — the *E-Commerce-Gesetz* (ECG) and *Mediengesetz* impose comparable disclosure. Per the cross-DACH guidance: a site compliant with the German DDG imprint is generally compliant in Austria and Switzerland too — but the agent sources each jurisdiction fresh rather than assuming.
- **revFADP note (Switzerland)** — the revised Federal Act on Data Protection (in force September 2023) requires the data controller to inform data subjects of data collection (drives the privacy policy's content for Swiss data subjects); the maximum fine rose to CHF 250,000 with extended criminal liability. The agent surfaces revFADP as the Swiss privacy-policy basis, distinct from GDPR (Swiss data subjects have revFADP rights; EU data subjects have GDPR rights — the policy addresses both where the audience spans both).

**Gate:** a commercial DACH site without an imprint, or with an image-only/buried imprint, does not pass phase 25. Not overridable — the imprint is a statutory requirement with real fines, not a stylistic choice.

## Cookie-consent sub-section (mandatory before non-essential cookies in the EU)

Confirmed current (2026-05-18 WebSearch): the EU ePrivacy Directive + GDPR require **prior, opt-in consent before any non-essential cookie or tracking technology loads**. The 2026 enforcement landscape is materially stricter — regulators are actively penalizing pre-consent cookie-setting and dark-pattern banners (France's CNIL fined Google €325M and Shein €150M in a single day in September 2025, both for cookie violations). The agent treats this as a hard requirement for any EU-reachable site that wired a cookie-setting integration at phase 24.

Valid-consent requirements the agent's wiring must satisfy:

- **Prior**: the banner shows and non-essential cookies do **not** fire until the user opts in. This is the load-bearing technical fact — the agent verifies (via Playwright network inspection) that the analytics/tracking cookie genuinely does not set before consent, not just that a banner is visible.
- **Equal prominence**: Accept and Reject on the same layer, equal visual weight. "Accept all" + a faint "Settings" link is invalid (a dark pattern regulators now fine).
- **Granular + revocable**: per-category choice (analytics / advertising / personalisation / social), a manage-preferences path, and the ability to withdraw consent as easily as it was given.
- **No invalid mechanisms**: no pre-ticked boxes, no consent-by-silence/inactivity, no cookie walls (access conditioned on accepting), no consent bundled with other agreements.
- **Essential cookies are exempt** (session/login/cart) — they do not need consent but must be documented in the cookie policy. The agent classifies the site's actual cookies (from `INTEGRATIONS-REPORT.md`) into essential vs non-essential and gates only the non-essential ones.

Implementation: the agent picks a Consent Management Platform appropriate to the stack and the user's scale — a CMP (Cookiebot / CookieYes / Iubenda — hosted, muggle-friendly, auto-scan) or an open-source/self-hosted option (Klaro / a lightweight first-party banner) when the user prefers no third-party dependency or wants cookieless analytics that sidesteps the banner entirely. If phase 24 chose cookieless analytics (Plausible / Fathom / Cloudflare Web Analytics set no cookies), the agent surfaces that the consent burden may largely vanish — the cleanest compliance is often *not setting non-essential cookies in the first place*, and the agent raises that as the preferred path before wiring a banner.

**Gate:** an EU-reachable site that fires a non-essential cookie before consent, or shows a dark-pattern banner, does not pass phase 25. The agent's verification is the network-level proof (cookie absent pre-consent), not the banner's presence. Not overridable.

## Gating rules

The agent refuses to advance when:

- **Legal pages skipped entirely.** "Let's just launch, I'll add legal later" — the agent refuses. A live site collecting form data with no privacy policy, or a DACH commercial site with no imprint, is an immediate liability. **Not overridable.**
- **Privacy policy that does not match the site's actual data practice.** Claims cookies the site does not set, or omits the analytics/CRM/processor it does use. The agent generates from `INTEGRATIONS-REPORT.md` + `FORMS-REPORT.md` and refuses a template that lies about the data practice. **Not overridable** — a false privacy statement is a legal exposure.
- **DACH commercial site without a compliant imprint.** Missing, image-only, or buried >2 clicks. **Not overridable** (statutory, fined).
- **EU-reachable site setting non-essential cookies before consent.** The agent's network-level check shows the analytics cookie firing pre-banner. **Not overridable** (statutory, actively fined in 2026).
- **Dark-pattern consent banner.** Unequal Accept/Reject prominence, pre-ticked categories, cookie wall. The agent refuses to ship a banner that is itself a violation. **Not overridable.**
- **Phase-24 cookie dependency unclosed.** `INTEGRATIONS-REPORT.md` flagged GA4 as needing consent gating and the gating is not wired. The agent refuses to mark phase 25 done with a known unclosed dependency from phase 24.

There is no override path on the hard statutory gates. Where the user's *specific policy content* is contested (a particular retention period, a particular T&Cs clause), the agent logs the user's chosen position in `.website-builder/decisions/` with the not-a-lawyer disclaimer and the recommendation to have it professionally reviewed — but it does not skip the page.

## Tools and skills used

- **`WebFetch`** — **mandatory at this phase**: current Swiss imprint + revFADP guidance (admin.ch / fedlex.admin.ch canonical, reputable secondary where the primary 404s) and current EU GDPR/ePrivacy cookie-consent guidance (EDPB / Your Europe / current canonical). Cited per-jurisdiction in `## Reference materials`.
- **`WebSearch`** — for current cookie-banner provider patterns (Cookiebot / CookieYes / Iubenda / Klaro feature + compliance state) and the 2026 enforcement landscape, and as the Tier-2 fall-back when a canonical legal source is unreachable (cite reputable current sources with date — never silently use stale training-data law).
- **`Edit` / `Write`** — to write the legal pages into the project (per stack) and to wire the CMP/consent mechanism so it actually gates the flagged integrations (the consent script loads first; the analytics script loads only on opt-in).
- **`Playwright` MCP** — the consent verification workhorse: load the page, inspect network/cookies, confirm the non-essential cookie does **not** set before consent and **does** after opt-in, and confirm the banner is not a dark pattern (Accept/Reject equally prominent, on the same layer).
- **`AskUserQuestion`** — the user's actual business identity for the imprint (legal name, register entry, address — the agent does not invent these), the data-retention positions, whether the site warrants general T&Cs, professional-legal-support status.
- **`Read`** — `INTEGRATIONS-REPORT.md` (cookie-setting integrations + the phase-25 dependency flags), `FORMS-REPORT.md` (what data the forms collect), `COMMERCE-LEGAL-REPORT.md` if transactional (the phase-25 dependencies 24c handed forward), `project.yaml` (owner + audience jurisdiction).

No subagent spawn. `wb-prelaunch` phase-group skill carries phases 24-27; phase 25's cookie gating composes with phase-24's integrations and is verified again in phase 27's cross-browser pass.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| Legal pages in the user's project | Per stack convention — privacy, terms (where warranted), imprint, cookie policy; footer-linked; imprint ≤2 clicks; text not image | The live general-legal surface |
| Consent mechanism wired in the project | CMP integration or first-party banner; gates the phase-24-flagged non-essential cookies | Real prior-consent gating, network-verifiable |
| `.website-builder/audit/LEGAL-REPORT.md` | Per page: concern, jurisdiction regime, source cited (URL + date), the actual-data-practice/identity inputs it reflects, cookie-consent network-verification evidence (cookie absent pre-consent, present post-opt-in), the not-a-lawyer disclaimer recorded | Audit trail proving the pages are sourced, current, truthful, and the consent gating actually works; read by phase 27 (QA re-verifies consent cross-browser) and phase 29 (deploy gate) |
| `.website-builder/decisions/legal-{topic}.md` *(when applicable)* | Standard decision-doc frontmatter + body | Created when a contested policy position was logged with the user taking professional responsibility |

The `LEGAL-REPORT.md` — including the network-level cookie-consent proof — is the required artifact.

## Common failure modes

**"I'll add the legal pages after launch."** The most common and most dangerous. A live site collecting contact-form data with no privacy policy, or a Swiss commercial site with no imprint, is an immediate, fineable liability — not deferred polish. The agent refuses to advance; legal pages ship *before* launch, with the site, every time.

**Copy-pasted privacy policy that lies about the data practice.** The template mentions Google Analytics cookies; the site actually uses cookieless Plausible. Or the template omits the Mailchimp integration the site does use. The agent generates from the *real* `INTEGRATIONS-REPORT.md` + `FORMS-REPORT.md` — the policy describes what this site actually does, because a false privacy statement is a worse legal position than a careful true one.

**The cookie banner is decorative, not functional.** A "We use cookies — OK" banner shows, but GA4 already dropped its cookie on page load before the user clicked anything. The banner is theatre; the violation already happened. The agent's gate is the network-level fact (Playwright confirms the non-essential cookie does not set pre-consent), not the banner's mere presence. This is the single most common cookie-consent failure and the agent's verification is built specifically to catch it.

**Dark-pattern banner that is itself a violation.** Big "Accept all", faint grey "Settings", no "Reject" — exactly what CNIL fined €325M+€150M for in 2025. The agent refuses to ship a banner with unequal Accept/Reject prominence or pre-ticked categories; the compliance mechanism cannot itself be the violation.

**DACH imprint missing, buried, or an image.** The owner is a Swiss sole proprietor; there is no imprint, or it is a screenshot, or it is four clicks deep. Swiss UCA Art. 3(1)(s) requires text-form identity reachable in ≤2 clicks; the agent treats this as non-negotiable and produces it from the user's *actual* legal identity (which it asks for — it does not invent a company name).

**EU and Swiss privacy regimes blurred.** The policy cites only GDPR for a Swiss-owner site whose data subjects fall under revFADP, or vice-versa. The agent addresses each regime for the data subjects it governs (revFADP for Swiss, GDPR for EU) and sources each fresh — it does not produce one mushed policy that is imprecise for both.

**The user thinks cookieless analytics still needs the full banner.** Phase 24 chose Plausible (sets no cookies). The agent surfaces that the cleanest compliance is *not setting non-essential cookies at all* — a cookieless-analytics site may need only a brief privacy-policy mention and no consent gate at all. The agent does not bolt an unnecessary banner onto a site that does not set the cookies a banner would gate.

**A canonical legal source 404s and the agent uses training-data law.** Privacy/imprint law changes; stale training knowledge is a liability. The agent treats an unreachable canonical source as a Tier-2 fall-back — WebSearch reputable *current* sources, cite with date — never a silent substitution of its own possibly-outdated knowledge.

## Reference materials

- **Design doc — phase pipeline source:** `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 25 (seed) — explicit DACH-imprint + EU-cookie-consent callout, pairs with phase 24c
- **Design doc — pipeline integration:** `Workstreams/website-builder/foundation/DESIGN-architecture.md` § Phase contracts
- **Phase 24 (the integrations whose cookies phase 25 gates):** `phase-contracts/24-integrations.md` § Gating rules — the cookie-setting-integration dependency this phase closes
- **Phase 24c (the commerce-legal surface phase 25 composes with, if transactional):** `phase-contracts/24c-commerce-legal.md` § Output artifacts — the phase-25 dependency list 24c hands forward
- **External research (loaded fresh 2026-05-18 for this contract):**
  - Swiss imprint — UCA/UWG Art. 3(1)(s); full name (natural) / registered company name + legal form (entity), postal address, phone + email, footer "Impressum" ≤2 clicks, text not image, fines to CHF 10,000. Sources: alpineexcellence.ch/en/guides/imprint-obligation-switzerland-requirements, hostpoint.ch legal-notice guidance, termsfeed Impressum template. Confirmed 2026-05-18.
  - Swiss revFADP — in force Sept 2023, controller must inform data subjects of collection, max fine raised to CHF 250,000 + extended criminal liability. Sources: dlapiperdataprotection.com (CH), dataguidance.com/jurisdictions/switzerland. Confirmed 2026-05-18.
  - Germany/Austria imprint — DDG (ex-TMG) Impressumspflicht; Austrian ECG + Mediengesetz; DDG-compliant generally compliant in AT/CH. Confirmed 2026-05-18.
  - EU cookie consent — ePrivacy + GDPR prior opt-in; banner Accept/Reject equal prominence same layer, granular, revocable; no pre-ticked/silence/cookie-wall/bundled consent; essential cookies exempt-but-documented; 2026 enforcement (CNIL Google €325M + Shein €150M, Sept 2025). Sources: cookiechimp.com EU GDPR/ePrivacy guide, clym.io GDPR cookie checklist 2026, cookieyes.com EU cookie compliance, europa.eu/youreurope online-privacy, consenteo.com gdpr_cookie_consent_2026. Confirmed 2026-05-18.
  - CMP options — Cookiebot / CookieYes / Iubenda (hosted, auto-scan); Klaro / first-party (self-hosted); cookieless analytics (Plausible/Fathom/Cloudflare) sidesteps the gate.
- **Secrets/config discriminator (legal copy is not secret):** `.claude/rules/secrets-conventions.md` + `.claude/rules/config-conventions.md`

Freshness date for this contract: **2026-05-18**. Privacy/imprint/cookie law changes; the agent re-fetches jurisdiction sources at session start when phase 25 is active and never relies on training-data privacy law the fetched current source can correct.
