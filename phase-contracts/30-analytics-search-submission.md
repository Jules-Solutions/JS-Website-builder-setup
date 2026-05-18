---
phase: 30
name: Analytics installation + search engine submission
group: deployment
pipeline_section: deployment
skill: wb-deploy
prev_phase: 29
next_phase: 31
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/cross-cutting/DESIGN-deploy-providers.md
---

# Phase 30 — Analytics installation + search engine submission

> The post-deploy operational confirmation. Verify analytics is actually firing on the *live* site (a real test pageview shows up in the provider's real-time view), and submit the sitemap.xml to Google Search Console and Bing Webmaster Tools. The phase that closes the deployment group. No gating — this is operational, not a quality gate — but the agent still proves the analytics fires for real rather than assuming the snippet works, and flags the Safari/ITP measurement gap honestly.

## Mission

The site is live (phase 29). Phase 30 is the operational coda of the deployment group: confirm the analytics that was wired at phase 24 (and consent-gated at phase 25) is *actually recording visits on the production site*, and tell the search engines the site exists by submitting the phase-26 sitemap.xml to Google Search Console and Bing Webmaster Tools. This is the difference between "I built a site" and "I built a site that I can see is working and that search engines know about."

Per the seed, **phase 30 has no quality gate** — it is operational, not a refusal point. A user *can* launch without analytics (some deliberately do) and the site still functions. But "no gate" is not "no rigor": the agent still proves the analytics fires by firing a real test pageview against the live site and watching it appear in the provider's real-time view — not by assuming the snippet that worked on a preview works in production (the phase-29 parity discipline applies to measurement too). And it surfaces the honest caveat that GA4 (and cookie-based analytics generally) under-measures Safari/iOS traffic because of Intelligent Tracking Prevention — so the user understands their numbers are a floor, not a census, and is not confused later when "the analytics says fewer visitors than my logs."

There is a clean interaction with phase 25 here: if cookie-based analytics is consent-gated, a test pageview only fires *after* accepting consent — the agent's verification accounts for that (it accepts consent, then fires the pageview, then confirms it arrived), and it confirms that *without* consent the cookie-based analytics correctly does *not* fire (re-affirming the phase-25 statutory behavior on the live site). For cookieless analytics (Plausible/Fathom/Cloudflare Web Analytics — no consent gate needed), the pageview should register regardless of consent state.

## Entry conditions

- Phase 29 (hosting deployment) complete. `audit/DEPLOY-REPORT.md` confirms the site is live at the real domain, every page 200, with the post-launch maintainer materialized.
- `audit/INTEGRATIONS-REPORT.md` (phase 24) records the analytics provider chosen and where its snippet lives. If phase 24 explicitly chose "no analytics for now," phase 30's analytics half is a no-op the agent records (and the post-launch maintainer's wizard offers adding it later).
- `audit/LEGAL-REPORT.md` (phase 25) records whether the analytics is consent-gated (cookie-based) or not (cookieless) — drives whether the test pageview is fired pre- or post-consent.
- `sitemap.xml` exists and is reachable at the live domain (phase 26 generated it; phase 29 deployed it). Search-console submission needs the real, live sitemap URL.
- The user has (or creates, guided here) a Google Search Console account and a Bing Webmaster Tools account, with the live domain as a verified property.

## What Claude must establish

Analytics confirmed firing on the live site, and the sitemap submitted + received at both search consoles. The work product:

1. **Analytics firing — proven, not assumed.** The agent loads the live site, accepts consent if the analytics is cookie-based (and confirms it does *not* fire pre-consent), fires a test pageview (a navigation the agent performs), and confirms the visit appears in the provider's real-time view (GA4 Realtime / Plausible live / Fathom live / Cloudflare Web Analytics). For cookieless analytics, the pageview registers regardless of consent. The agent records the provider, the test, and the confirmed receipt — "the snippet is on the page" is not the deliverable; "a real pageview was observed arriving" is.
2. **Google Search Console: sitemap submitted + received.** The live domain is a verified GSC property (verification via DNS TXT — ties cleanly to the phase-28 DNS the agent already controls — or the HTML-tag/file method); the agent submits the live `sitemap.xml` URL in the Sitemaps report and confirms the status is "Success" (or surfaces "Has errors"/"Couldn't fetch" with the diagnosis and fix). Redirects are not followed by GSC — the agent submits the *actual* sitemap location, the canonical-domain one matching phase 28's apex/www decision.
3. **Bing Webmaster Tools: sitemap submitted + received.** The site is added + verified in Bing (the simplest path is **Import from Google Search Console** — Bing auto-imports ownership verification *and* existing sitemaps within minutes; alternatively XML-file / meta-tag / CNAME verification). The agent confirms the sitemap is received (the GSC import often carries it automatically; otherwise the agent submits it explicitly in Bing's Sitemaps section).
4. **Honest measurement caveats recorded.** The Safari/iOS-ITP under-measurement note for cookie-based analytics; the consent-gating effect on measured numbers (a chunk of visitors who reject consent are not counted by cookie-based analytics — by design, lawfully); the "this is a floor not a census" framing so the user reads their numbers correctly.
5. **`.website-builder/audit/POST-DEPLOY-REPORT.md`** — the analytics provider + the observed-test-pageview evidence (pre/post consent behavior), the GSC property + sitemap-submission status, the Bing property + sitemap-submission status (and whether via GSC import), and the recorded measurement caveats.

The agent updates `.website-builder/project.yaml.current_phase` to `31` upon completion. Phase 31 (launch announcement) begins the post-launch group.

## Gating rules

Per the seed, **phase 30 has no refusal gate** — it is operational confirmation, not a quality checkpoint. The site is already live (phase 29 gated that). The agent does not block the pipeline here. But "no gate" does not mean "no standard":

- **Analytics is proven, not assumed.** If the agent cannot observe the test pageview arriving in the provider's real-time view, it does not record analytics as "working" — it surfaces the gap ("the snippet is present but no pageview arrived — likely consent not accepted in the test, an ad-blocker, an ITP block on the test browser, or a misconfigured property ID") and diagnoses it. Not a pipeline gate, but a flagged operational issue, not a silent pass.
- **The sitemap submitted is the live, canonical one.** Submitting a preview-URL sitemap, or the non-canonical-host one (apex when phase 28 chose www-canonical, or vice-versa), to GSC is an operational error the agent catches — GSC does not follow redirects, so the wrong sitemap URL silently does nothing.
- **Consent-gating behavior re-confirmed on the live analytics.** As an operational by-product, the agent confirms (again, on the live site) that cookie-based analytics does *not* fire pre-consent — a phase-25 statutory behavior; if phase 30's test reveals it firing pre-consent on production, that is a phase-25 regression the agent surfaces loudly (escalating it back, since phase 25's gate *was* overridable-only-by-explicit-decision and a live violation is serious) even though phase 30 itself does not gate.

There is nothing to override here — the phase does not block. The discipline is honesty (proven not assumed) and correctness (the live canonical sitemap), not refusal.

## Tools and skills used

- **`Playwright` MCP** — the analytics-verification workhorse: load the live site, handle the consent banner per the phase-25 mode (accept → expect pageview for cookie-based; no-consent → expect *no* cookie-based pageview), perform the test navigation, and (via the provider's real-time view or network inspection of the analytics beacon) confirm the pageview was recorded.
- **`WebFetch`** — **mandatory at this phase**: Google Search Console current sitemap-submission UX (`https://search.google.com/search-console/about` / the Sitemaps-report help — add property, verify, submit, confirm status) and Bing Webmaster Tools current sitemap-submission UX (`https://www.bing.com/webmasters` / its help — add+verify, the GSC-import path, submit sitemap). Also current GA4/Plausible/Fathom/Cloudflare-Web-Analytics provider state. Cited in `## Reference materials`. When a help page returns no content, the agent treats it as a Tier-2 fall-back and WebSearches reputable current guidance with the date, never substituting stale training data.
- **`Bash`** — `curl` against the live `sitemap.xml` to confirm it is reachable + well-formed before submission; DNS TXT inspection for GSC verification (the phase-28 DNS the agent already manages).
- **`AskUserQuestion`** — the GSC/Bing account access (the user owns these properties; the agent guides verification but the accounts are the user's), the verification-method choice (DNS TXT ties to phase 28 cleanly), and surfacing the measurement-caveat acknowledgement.
- **`Read`** — `audit/DEPLOY-REPORT.md` (the live domain), `audit/INTEGRATIONS-REPORT.md` (the analytics provider + snippet location), `audit/LEGAL-REPORT.md` (consent-gated or cookieless — drives the test sequence), the live `sitemap.xml` (the submission target).

No subagent spawn. The `wb-deploy` phase-group skill closes here (phases 28-30); phase 31 begins the post-launch group under `wb-postlaunch`. The materialized post-launch maintainer (phase 29) inherits the analytics + search-console setup as ongoing monitoring touch-points.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/audit/POST-DEPLOY-REPORT.md` | Analytics provider + observed-test-pageview evidence (pre/post-consent behavior on the live site), GSC property + sitemap-submission status, Bing property + sitemap-submission status (via GSC-import or direct), recorded measurement caveats (ITP/Safari under-measurement, consent-rejection effect, floor-not-census framing) | The operational-confirmation record; read by the post-launch maintainer (which monitors analytics + search-console health ongoing) |
| GSC + Bing properties verified, sitemap submitted | At the search consoles (user-owned accounts) | The site is discoverable to the search engines |
| Measurement-caveat note surfaced to the user | In the report + conversationally | The user reads their analytics numbers correctly (a floor, lawfully under-counting consent-rejecters + ITP) |

The `POST-DEPLOY-REPORT.md` with the observed-pageview evidence + both consoles' submission status is the artifact.

## Common failure modes

**GA4 not firing on the live site and nobody noticed.** The snippet is present; the property ID is the dev one, or consent was never accepted in the (non-existent) test, or an ITP/ad-blocker on the test browser ate the beacon — and the user launches believing they have analytics and have nothing. The agent fires a *real* test pageview against the live site and confirms it *arrived in the provider's real-time view*; "snippet present" is not "analytics working."

**GA4 under-measures and the user thinks the site is dead.** Safari/iOS ITP blocks or caps GA4 measurement; consent-rejecters are lawfully not counted. The user sees "200 visitors" while server logs show 600 and panics. The agent records the floor-not-census caveat *up front* so the user interprets the numbers correctly from day one rather than misreading lawful under-counting as a broken site or no traffic.

**Wrong sitemap URL submitted to GSC.** The agent submits the preview-deploy sitemap, or the non-canonical-host one (apex when www is canonical). GSC does not follow redirects — the wrong URL silently does nothing and the site is not actually submitted. The agent submits the *live canonical* sitemap matching phase 28's apex/www decision and confirms GSC status "Success."

**Bing skipped because "Google is what matters."** Bing (and Bing-powered surfaces, plus its 2026 GEO/AI-performance tooling) is real discovery the user paid for the whole disciplined build to capture. The agent does Bing too — and the cheapest path is **Import from Google Search Console** (Bing auto-imports verification *and* sitemaps in minutes), so "Bing is extra work" is not a real excuse.

**Consent-gating regressed on production and only phase 30's test reveals it.** The phase-25 consent gate passed on a preview; on the live site a config difference lets GA4's cookie fire pre-consent. Phase 30 does not gate — but it surfaces this loudly as a phase-25 *statutory* regression and escalates it (a live cookie-consent violation is serious), rather than treating "phase 30 has no gate" as license to ignore a compliance break the operational test happened to expose.

**Analytics "verified" on a preview, not the live site.** The same parity failure phase 29 fights. A pageview confirmed on the preview deploy is not confirmation the *production* analytics works (different env, different property, different consent config). The agent verifies against the live production domain, every time.

**Sitemap submitted before it is actually reachable.** The agent submits the GSC sitemap URL while the deploy's sitemap route still 404s (build timing). The agent `curl`s the live sitemap and confirms it is reachable + well-formed *before* submitting, so the console does not record a "Couldn't fetch" the user then has to chase.

## Reference materials

- **Design doc — phase pipeline source:** `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 30 (seed — explicitly no gate, operational; common failure = GA4 not firing on Safari due to ITP, agent flags + tests on mobile)
- **Design doc — pipeline integration:** `Workstreams/website-builder/foundation/DESIGN-architecture.md` § Phase contracts
- **Design doc — deploy/provider context (analytics provider state, the live site this verifies):** `Workstreams/website-builder/cross-cutting/DESIGN-deploy-providers.md` § Phase contracts that invoke this concern (phase 30 = "verify deploy live; submit sitemap to GSC + Bing")
- **Phase 24 (the analytics this phase verifies fires):** `phase-contracts/24-integrations.md` § What Claude must establish — analytics class, the cookie-consent dependency it flagged for phase 25
- **Phase 25 (the consent gate whose live behavior phase 30 re-confirms):** `phase-contracts/25-legal-pages.md` § Cookie-consent sub-section
- **Phase 26 (the sitemap.xml this phase submits):** `phase-contracts/26-seo-structured-data.md` § What Claude must establish — sitemap generation, the canonical-URL/host the submission must match
- **Phase 29 (the live site this phase confirms):** `phase-contracts/29-hosting-deployment.md` § Output artifacts
- **External research (loaded fresh 2026-05-18 for this contract):**
  - Google Search Console — https://search.google.com/search-console/about + the Sitemaps-report help — owner permission required; host the sitemap (root recommended); verify reachable via URL Inspection; submit URL in Sitemaps report; status Success / Has errors / Couldn't fetch; redirects not followed (submit the actual location). Confirmed 2026-05-18.
  - Bing Webmaster Tools — https://www.bing.com/webmasters + its help — add+verify via XML file / meta tag / CNAME / **Import from Google Search Console** (auto-imports verification + existing sitemaps in minutes); Sitemaps section → Submit sitemap (XML/RSS/Atom/text); 2026 AI-Performance/GEO beta report. (Bing help page returned no content on direct fetch; corroborated via WebSearch reputable 2026 guides — promodo.com, supporthost.com, impressiondigital.com — Tier-2 fall-back, dated.) Confirmed 2026-05-18.
  - Analytics providers — GA4 (cookie-based, ITP-limited on Safari/iOS), Plausible / Fathom / Cloudflare Web Analytics (cookieless, no consent gate). Confirmed 2026-05-18.

Freshness date for this contract: **2026-05-18**. Search-console UIs + analytics-provider state evolve; the agent re-fetches the GSC/Bing submission UX at session start when phase 30 is active and verifies analytics by an *observed live-site test pageview*, never by snippet presence.
