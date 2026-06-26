# Analytics Verification + Search-Console Submission — phase 30

> Reference for phase 30. The phase contract `phase-contracts/30-analytics-search-submission.md` is the substantive source of truth; this file is the procedural condensation the skill loads on demand.
>
> External state confirmed fresh 2026-05-18 via WebSearch (GA4/Plausible/PostHog comparison + Safari ITP, Google Search Console + Bing Webmaster Tools sitemap submission + import-from-GSC). Console UIs + analytics-provider state evolve — re-fetch the GSC/Bing submission UX via WebFetch at session start when phase 30 is active. **Phase 30 has no refusal gate** (the site is already live, phase 29 gated that) — but the discipline is honesty (proven, not assumed) and correctness (the live canonical sitemap).

## Proving the pageview (analytics — proven, not assumed)

Read the context first:
- `audit/INTEGRATIONS-REPORT.md` — the analytics provider + where its snippet lives. If phase 24 chose "no analytics for now," the analytics half is a recorded no-op (the post-launch maintainer's wizard offers adding it later).
- `audit/LEGAL-REPORT.md` — whether analytics is **consent-gated (cookie-based)** or **cookieless** — this drives the test sequence.

Via `Playwright` MCP against the **live production domain** (never a preview — same parity discipline as phase 29):

**Cookie-based analytics (GA4 etc. — consent-gated per phase 25):**
1. Load the live site fresh (no prior consent cookie).
2. Confirm the analytics beacon does **not** fire pre-consent (network inspection: no request to the analytics collector). This re-affirms the phase-25 statutory behavior on the live site.
3. Accept consent via the banner.
4. Perform a test navigation (a real pageview the agent triggers).
5. Confirm the visit appears in the provider's real-time view: **GA4 → Realtime report**; verify the property ID matches production (not the dev property). Network-inspect the collect beacon as corroboration.

**Cookieless analytics (Plausible / Fathom / Cloudflare Web Analytics — no consent gate):**
1. Load the live site.
2. Perform the test navigation — the pageview should register **regardless of consent state**.
3. Confirm in the provider's live view (Plausible live / Fathom live / Cloudflare Web Analytics).

"Snippet present" is not the deliverable; "a real pageview observed arriving in the provider's real-time view" is. If the pageview does not arrive, surface the gap and diagnose — likely causes: consent not accepted in the test, an ad-blocker / ITP on the test browser ate the beacon, a misconfigured (dev) property ID, or the snippet not actually deployed to production. This is a flagged operational issue, not a pipeline gate, but never a silent pass.

**Escalation:** if the test reveals cookie-based analytics firing *pre-consent* on production, surface it **loudly as a phase-25 statutory regression** and escalate (a live cookie-consent violation is serious). Phase 30 does not gate, but "no gate" is not license to ignore a compliance break the operational test exposed.

## GSC submission (Google Search Console)

1. **Confirm the sitemap is reachable + well-formed first:**
   ```bash
   curl -sI https://example.com/sitemap.xml | grep -iE '^HTTP/|^content-type:'
   curl -s  https://example.com/sitemap.xml | head -c 400
   ```
   Submitting before the sitemap route is actually live (build timing) records a "Couldn't fetch" the user then has to chase.
2. **Verify the live domain as a GSC property.** DNS-TXT verification is the cleanest path — it ties to the phase-28 DNS the agent already controls (add the Google-provided `TXT` record at the registrar/DNS provider, confirm with `dig +short example.com TXT`). HTML-tag / HTML-file methods are alternatives. Owner permission on the GSC account is required — the account is the **user's**; the agent guides verification, the user owns the property.
3. **Submit the sitemap.** GSC → Sitemaps report → enter the **live canonical** sitemap URL — the one matching phase 28's apex/www decision. **GSC does not follow redirects** — submitting the non-canonical-host sitemap (apex when www is canonical, or vice-versa) silently does nothing. Submit the actual canonical location.
4. **Confirm status.** Expect "Success". If "Has errors" / "Couldn't fetch", surface the diagnosis (unreachable, wrong host, malformed XML) and the fix.

## Bing submission (Bing Webmaster Tools)

The cheapest path is **Import from Google Search Console** (confirmed 2026-05-18):

1. Bing Webmaster Tools → **Settings → Import from Google Search Console**.
2. Authenticate with the Google account linked to the GSC property.
3. Bing auto-imports **ownership verification *and* existing sitemaps** within minutes — no separate Bing verification needed.

If GSC import is unavailable, verify directly: XML-file / meta-tag / **CNAME** (create the Bing-provided CNAME at the registrar pointing to `verify.bing.com`), then Bing → **Sitemaps** section → Submit sitemap (the live canonical XML URL). Confirm the sitemap is received.

2026 note: Bing Webmaster Tools added an **AI Performance Report** (separates AI citations from traditional search) — Bing-powered + AI surfaces are real discovery the disciplined build earns; "Google is what matters" is not a reason to skip Bing, especially when the GSC-import path makes it minutes of work.

## Measurement caveats (the floor-not-census framing)

Record these in `POST-DEPLOY-REPORT.md` and surface them conversationally so the user reads their numbers correctly from day one — lawful under-counting is not a broken site:

- **Safari/iOS ITP under-measurement.** Intelligent Tracking Prevention blocks or caps cookie-based analytics (GA4) on Safari/iOS. GA4 structurally loses ~30-50% of conversion signal to consent loss + ad-blockers + ITP without server-side augmentation (confirmed via WebSearch 2026-05-18). The user will see fewer visitors in GA4 than server logs show — this is expected, not a bug.
- **Consent-rejection effect.** Visitors who reject cookie consent are lawfully **not counted** by cookie-based analytics — by design, by GDPR/ePrivacy. The measured number is a floor.
- **Cookieless hash rotation.** Privacy-first cookieless tools (Plausible, Fathom) rotate visitor hashes daily, so a returning visitor the next day is counted as **new** — they often show *higher* visitor counts than GA4 (they don't lose consent-rejecters) but inflate unique-visitor counts across days. Different distortion, opposite direction — surface it so the user does not over-read growth.
- **Framing:** "These numbers are a floor, not a census. They lawfully under-count consent-rejecters and Safari/iOS users (cookie-based) or over-count returning visitors across days (cookieless). Read trends, not absolute precision; cross-check with server logs or the host's edge analytics if exact counts matter."

## POST-DEPLOY-REPORT.md evidence checklist

The phase-30 artifact `.website-builder/audit/POST-DEPLOY-REPORT.md` records (per the contract schema):

- Analytics provider + the **observed test-pageview evidence** (the pre/post-consent behavior on the live site — what fired, when, confirmed in which real-time view).
- GSC property + sitemap-submission status (Success / Has errors + diagnosis).
- Bing property + sitemap-submission status (via GSC-import or direct), and which path.
- The recorded measurement caveats (ITP/Safari, consent-rejection, hash-rotation, floor-not-census framing).

The artifact's value is the *observed* pageview evidence + both consoles' confirmed submission — not "analytics was set up" but "a real pageview was observed arriving and both consoles confirmed the sitemap".
