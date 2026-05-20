# Booking adapter — Cal.com

> The canonical booking adapter for service / consulting / coaching / appointment businesses. Open-source, self-hostable Calendly alternative — same scheduling primitives (event types, availability, time-zone handling, integrations with Google/Microsoft calendars), but AGPLv3 licensed, fully API-driven, and self-hostable. The MVP default per `Workstreams/website-builder/website-builder.md` decision 54.
>
> Cal.com sells **time** (1-many event types: 30-min consult, 1-hour coaching, 2-hour workshop). For sites that sell **things** (products / digital downloads / subscriptions), pair Cal.com with a commerce adapter (Stripe Checkout per [commerce-adapters/commerce-stripe.md](commerce-stripe.md) is the most common pairing).

## Mental model

### Identity

- **Platform name:** Cal.com
- **Version surface:** REST API v2 at `https://api.cal.com/v2/`; embed scripts versioned via the `@calcom/embed-*` npm packages (current line: `@calcom/embed-snippet`, `@calcom/embed-react` for Cal.com Atoms). Cal.com itself is open-source at https://github.com/calcom/cal.com — release tags track major + minor versions.
- **Canonical context7 IDs:**
  - `/websites/cal_api-reference_v2` — Cal.com API v2 reference (benchmark 83.3, 2,663 code snippets; verified 2026-05-20)
  - `/calcom/cal.com` — Cal.com source repo (benchmark 77.91; verified 2026-05-20)
  - `/llmstxt/cal_llms-full_txt` — Cal.com llms.txt full extract (benchmark 63.83)
- **Freshness-check requirement:** agent invokes `resolve-library-id` for `/websites/cal_api-reference_v2` at phase 24a entry; if cached docs in `.website-builder/library/docs/calcom-*.md` are >30 days old, re-fetch before generating embed code or API calls.
- **Deployment-mode summary:**
  1. **Cal.com Cloud (SaaS)** — Cal-hosted at `cal.com/{username}`; subscription pricing (Free / Teams / Organizations / Enterprise — see § "Costs"). Default for muggles.
  2. **Self-hosted (open-source)** — user runs Cal.com via Docker / Vercel / Railway / etc.; full data ownership; AGPLv3 license. Default for users who value data ownership / want operational control / have DevOps capacity.

Cal.com is **scheduling as a platform**:

- **Event types** — bookable services (30-min consult, 1-hour coaching, 2-hour workshop, etc.) with availability rules, location (Zoom / Google Meet / Daily / Whereby / in-person), price (free or paid), payment requirement.
- **Availability** — user's calendar; rules per event type, working hours, buffers, booking window (e.g., 1-day notice; 90-day-ahead booking limit).
- **Calendar integrations** — Google Calendar, Microsoft 365, Apple Calendar (iCloud), CalDAV (read availability + write events).
- **Video integrations** — Zoom, Google Meet, Microsoft Teams, Daily, Whereby (auto-generate meeting links per booking).
- **Payment integrations** — Stripe (default; first-class), PayPal (alternative; bridged via Cal.com → PayPal Checkout). Cal.com itself does NOT process payments; it bridges to a processor at booking-creation time.
- **Embed options** — inline widget, popup overlay, floating button (persistent CTA), full-page redirect.

For the website-builder, Cal.com fits when:

1. User runs a service / consulting / coaching business with bookable appointments
2. User values open-source / data ownership (route to self-hosted) or prefers a managed SaaS (route to Cloud)
3. User wants embedded booking on their site (not just a link out)
4. User needs payment collection at booking time (paid bookings) OR offers free initial consultations (free bookings)
5. User has 1-many staff (Cal supports team scheduling via Teams plan)

## Auth model

Cal.com auth surfaces. All secrets via `secrets-conventions.md` — env-var indirection only; 1Password is the SSOT.

| Auth method | Used for | Key shape | Env var | 1Password reference |
|---|---|---|---|---|
| **API key** (Cloud + self-hosted) | Server-side admin operations | `cal_live_xxx` | `CALCOM_API_KEY` (live), `CALCOM_TEST_API_KEY` (test/sandbox) | `op://shared/calcom/api-key` |
| **Embed token (per user)** | Frontend booking widget (white-label embed via Cal.com Atoms) | OAuth-style token | `CALCOM_EMBED_TOKEN` | `op://shared/calcom/embed-token` |
| **OAuth access token (Platform billing)** | Cal.com Platform / Atoms enterprise integrations | OAuth2 access + refresh tokens | per-user issued | per-user 1P refs |

**Cloud users** generate API keys in Cal.com Dashboard → Settings → Developer → API Keys. **Self-hosted users** have admin-level API access via their deployment (default admin user created on first run; API keys generated through the same Settings → Developer surface).

**OAuth note for Cal.com Platform:** users on Cal.com Platform (Organizations + Enterprise tiers) provision OAuth tokens per end-user — agent surfaces this at phase 24a only when the user has chosen the Platform / Atoms path (most muggle muggles use the simpler API-key + embed-script path).

## CRUD vocabulary

Cal.com API v2 at `https://api.cal.com/v2/` — JSON REST. All API calls require `Authorization: Bearer $CALCOM_API_KEY` header. Header `cal-api-version` may pin to a specific date-versioned snapshot.

```bash
# List event types
GET https://api.cal.com/v2/event-types
  -H "Authorization: Bearer $CALCOM_API_KEY"

# Create an event type (free booking — no price)
POST https://api.cal.com/v2/event-types
  -H "Authorization: Bearer $CALCOM_API_KEY"
  -H "Content-Type: application/json"
  -d '{
    "title": "30-min Consultation",
    "slug": "consult-30",
    "lengthInMinutes": 30,
    "locations": [{"type": "integrations:google:meet"}],
    "description": "Free intro call to discuss your needs"
  }'

# Create a paid event type (CHF — Swiss audience)
POST https://api.cal.com/v2/event-types
  -H "Authorization: Bearer $CALCOM_API_KEY"
  -H "Content-Type: application/json"
  -d '{
    "title": "1-hour Strategy Session",
    "slug": "strategy-60",
    "lengthInMinutes": 60,
    "locations": [{"type": "integrations:google:meet"}],
    "price": 15000,
    "currency": "CHF"
  }'

# Get availability slots for an event type
GET https://api.cal.com/v2/slots/available?startTime=...&endTime=...&eventTypeId=...
  -H "Authorization: Bearer $CALCOM_API_KEY"

# Create a booking (server-side; ordinarily customers book via embed)
POST https://api.cal.com/v2/bookings
  -H "Authorization: Bearer $CALCOM_API_KEY"
  -H "Content-Type: application/json"
  -d '{
    "eventTypeId": 123,
    "start": "2026-06-01T10:00:00.000Z",
    "attendee": {
      "name": "Sarah Müller",
      "email": "sarah@example.ch",
      "timeZone": "Europe/Zurich"
    }
  }'

# List bookings
GET https://api.cal.com/v2/bookings
  -H "Authorization: Bearer $CALCOM_API_KEY"

# Cancel a booking
DELETE https://api.cal.com/v2/bookings/{id}
  -H "Authorization: Bearer $CALCOM_API_KEY"
  -d '{"reason": "Customer requested cancellation"}'

# List teams
GET https://api.cal.com/v2/teams
  -H "Authorization: Bearer $CALCOM_API_KEY"

# List webhooks
GET https://api.cal.com/v2/webhooks
  -H "Authorization: Bearer $CALCOM_API_KEY"
```

For most muggle sites, agent uses the API for one-time setup (creating event types + setting availability + configuring calendar/video integrations) and lets customers book via the embed script — the embed handles availability fetch + booking creation client-side.

## API + MCP availability

| Surface | Type | Use | Captain L verification |
|---|---|---|---|
| **REST API v2** | JSON | Event types, bookings, availability, users, teams, webhooks | verified context7 `/websites/cal_api-reference_v2` 2026-05-20 |
| **Webhooks** | HTTP callbacks | `BOOKING_CREATED`, `BOOKING_RESCHEDULED`, `BOOKING_CANCELLED`, `BOOKING_PAID`, `MEETING_STARTED` | verified 2026-05-20 |
| **Embed scripts** (`@calcom/embed-snippet`) | Browser JS | Inline widget, popup overlay, floating button (CTA) | verified 2026-05-20 |
| **Cal.com Atoms** (`@calcom/embed-react`) | React components | White-label React components for booking flows (full-control embed) | verified 2026-05-20 |
| **Cal.com Dashboard** | Web UI | Primary management interface for non-API operations | verified 2026-05-20 |

### Cal.com MCP — community FastMCP exists; NO official Cal.com MCP (re-verified 2026-05-20)

**Status update vs source design doc `DESIGN-booking-calcom.md` line 95:** the design doc says "No official MCP; agent uses REST API; community MCPs may exist." Phase 4 re-verification confirms:

- **No official Cal.com MCP.** Cal.com itself explicitly does NOT publish a first-party MCP — see Cal.com's "Best MCP Servers" blog (https://cal.com/blog/best-mcp-servers): "you can either wrap the API calls using a custom MCP server or call the API directly through tool integrations." Cal.com positions its API as the primary integration surface.
- **NOT in Anthropic plugin catalog.** Confirmed via `https://claude.com/plugins` scan 2026-05-20 — no Cal.com plugin listed (catalog has 150+ plugins including Stripe at 27,078 installs, GitHub at 246,383 installs; Cal.com absent).
- **Community FastMCP server exists:** `Danielpeter-99/calcom-mcp` at https://github.com/Danielpeter-99/calcom-mcp — MIT licensed, community-maintained, **explicitly NOT affiliated with Cal.com**. FastMCP-based; SSE transport. Tools: `get_api_status`, `list_event_types`, `get_bookings`, `create_booking`, `list_schedules`, `list_teams`, `list_users`, `list_webhooks`. 6 commits as of verification — modest scope but functional.
- **Composio integration also exists:** `mcp.composio.dev/cal` — hosted MCP via Composio (community marketplace); subset of Cal.com API exposed.

**Agent path (per `tool-dependency-discipline.md` Tier 2):**

1. **Default:** agent uses Cal.com REST API directly (Bash + curl, or stack-specific HTTP client). No MCP dependency at phase 24a — the API is well-documented and the operations agent needs are simple (create event types, list bookings, configure webhook).
2. **Optional enhancement:** if the user has installed Danielpeter-99/calcom-mcp (self-hosted FastMCP) OR uses Composio's hosted Cal.com MCP, agent can route calls through the MCP — but the operation set is REST-API-equivalent; no canonical-pattern advantage like the Stripe MCP offers.
3. **Custom Claude connector:** users who want tighter Cal.com-CC integration can wrap the API themselves following the Cal.com Atoms / Embed React patterns. Out of scope for v1; surface as a future enhancement at phase 24a if user explicitly asks.

**Negative findings (other MCP ecosystem checks, 2026-05-20):**

- **Google Calendar MCP** — none official; community implementations exist for calendar read/write. Cal.com handles Google Calendar integration internally; agent doesn't need a separate Calendar MCP at phase 24a.
- **Microsoft 365 / Outlook MCP** — none official; same disposition as Google Calendar — Cal.com handles internally.
- **Zoom / Google Meet / Daily / Whereby MCPs** — none official; Cal.com handles video integration internally via OAuth flows configured in Cal.com Dashboard → Apps.

### Sandbox + freshness re-fetch

For phase 24a setup: agent invokes context7 `/websites/cal_api-reference_v2` at entry; checks `https://cal.com/docs/api-reference/v2` for any breaking API changes (Cal.com API v2 is stable but adds endpoints; date-version header pins to a specific snapshot if needed).

## Costs

Two distinct cost surfaces — SaaS pricing tiers AND self-hosted option. Cloud pricing verified at `https://cal.com/pricing` 2026-05-20 (note: pricing differs from the source design doc — Cal.com lowered Teams + Organizations pricing since the design was authored).

### Cal.com Cloud (SaaS) — pricing as of 2026-05-20

| Plan | Cost | Features |
|---|---|---|
| **Free** | $0/month | 1 user account, unlimited event types, unlimited calendars, unlimited integrations, unlimited bookings — generous for solo consultants |
| **Teams** | $12/user/month (annual billing — 25% savings) — was $15-19 in 2025 | Team scheduling, round-robin, managed event types, 14-day free trial |
| **Organizations** | $28/user/month (annual billing — 25% savings) — was $37 in 2025 | Unlimited sub-teams, SAML SSO, compliance checks (SOC 2, HIPAA, ISO 27001), 14-day free trial |
| **Enterprise** | Custom (contact sales) | Dedicated support, SLA guarantees, HRIS integrations, unlimited limits |

### Self-hosted (open-source AGPLv3)

- **Software cost: $0** (AGPLv3)
- **Hosting cost: variable** — typical: PostgreSQL + Node, $5-50/month on Railway / Vercel / DigitalOcean / Fly.io / Render
- **DevOps cost: real** — backups, upgrades, security patches, schema migrations — user's burden
- **License obligation:** AGPLv3 — only matters if the user modifies Cal.com's source AND offers Cal.com-as-a-service to third parties. For users using Cal.com as-is (the muggle case), AGPLv3 doesn't trigger anything.

### Payment processor fees (paid bookings)

Cal.com itself charges $0 for bookings (free or paid). For paid bookings, Cal.com bridges to Stripe / PayPal — the bridged processor charges their standard rates:

- **Cal.com → Stripe:** Stripe charges 2.9% + 30¢ (or regional equivalent — see [commerce-stripe.md § Costs](commerce-stripe.md#costs)). For CHF event types paid via TWINT, the rate is Stripe's standard CHF rate.
- **Cal.com → PayPal:** PayPal charges 3.49% + $0.49 US / 1.99-2.49% + €0.35 EU intra-EU / 4.4% + fixed for cross-border (per [DESIGN-payment-providers.md lines 186-192](../Workstreams/website-builder/commerce/DESIGN-payment-providers.md)). Higher cost — appropriate when legacy-trust audiences matter or for international customers paying via PayPal.

### Critical disclosures

1. **Free tier is generous.** Solo consultants on the Free plan get every core feature ($0/mo with unlimited event types, calendars, integrations, bookings).
2. **Self-hosted is "free" but operationally heavy.** AGPLv3-compliant; ~$5-50/mo hosting; real DevOps. Not for muggles unless they have an ops person.
3. **AGPLv3 license matters only if forking + offering as service.** Most muggle users (using Cal.com as-is, embedded on their site) don't trigger AGPLv3 obligations.
4. **Payment processor fees apply on top.** Cal.com is a $0 booking platform; the payment processor (Stripe / PayPal) charges their normal rates for paid bookings.
5. **Cal.com is NOT the Merchant of Record.** For paid bookings, the user is the MoR — tax compliance for the service revenue is the user's burden (or via Stripe Tax, +0.5%).
6. **Multi-staff scheduling requires Teams plan.** Solo founder is Free; round-robin booking across a 2-person team is Teams ($12/user/mo annual = $24/mo total).

## Stack pairings

Per locked decision 18 (full coverage). Cal.com integration is light-touch on every stack — the embed script is a single `<script>` tag + a CSS-targeted container; Cal.com Atoms is a React component drop-in.

| Stack | Integration mode | Notes |
|---|---|---|
| **Next.js + shadcn** *(strongest pairing)* | `@calcom/embed-react` (Cal.com Atoms) for inline/popup; works in both Server Components (popup mode) and Client Components (inline mode). Embed script also available via `<Script>` from `next/script`. | Per `adapters/stack-nextjs.md` line 570: "MVP default per decision 54 — `pnpm add @calcom/embed-react` for inline + popup embeds". Phase 4 fixture exercises this pairing. |
| **Framer** | Cal.com embed via Framer Code Component wrapping the embed script — popup or inline; agent ships `code/CalEmbed.tsx` Code Component with `addPropertyControls` for event-type slug + theme | Per `adapters/stack-framer.md` line 382: "embedded as Code Components wrapping the official embed scripts. Framer's iframe support is solid." |
| **WordPress** | Custom Gutenberg block wrapping the Cal.com embed script — agent generates the block; user inserts into pages via WP block editor. Also: Cal.com plugin for WP available (lighter integration, less customization). | Per `adapters/stack-wordpress.md` line 698: "embedded via custom Gutenberg block wrapping the embed script (per locked decision 54 — Cal.com is MVP default for free booking)." |
| **Astro** | Cal.com embed script in `.astro` pages — `<script>` import + `<div data-cal-namespace>` container; works server-rendered or client-hydrated | Solid; same pattern as static HTML with Astro's component conveniences |
| **Hugo** | Cal.com embed script in HTML via Hugo partial template — `<script>` + `<div>` | Solid; static-first |
| **SvelteKit** | Cal.com embed script in `+page.svelte` — same pattern as static HTML with `onMount()` for client-side bootstrap | Solid |
| **Webflow** | Embed code via Webflow's Embed element (custom code block) — pastes `<script>` + `<div>` directly | Solid |
| **Plain static HTML** | `<script src="https://embed.cal.com/embed/embed.js" async>` + `<div data-cal-namespace>` + Cal.com's `Cal('init', ...)` invocation | The simplest path — agent generates a 5-line embed snippet |

## Content layer mapping

Same 5-row contract as `adapters/README.md` §4 + `cms-adapters/README.md` §6 — IDENTICAL row labels in exact order. For booking adapters, most rows are "n/a / handled via stack adapter" — Cal.com's hosted booking UI doesn't ingest the website-builder's design system. L4 carries the booking-page intro/description content + booking-success page content + cancellation-policy page content. L1 may carry embed-widget styling tokens (Cal.com Atoms accepts theme override via props).

| Layer | Cal.com native concept |
|---|---|
| **L1 brand.yaml.tokens** | Limited token surface. Cal.com hosted UI has its own design (Cal-styled); embed script accepts `theme: 'light' | 'dark' | 'auto'`. Cal.com Atoms (React) accepts `themeOverrides` prop for color + typography (subset of brand tokens — agent maps `brand.yaml.tokens.colors.primary` to the Atoms `themeOverrides.colors.primary`). Full white-label requires Cal.com Platform + Atoms (Organizations / Enterprise tier). |
| **L2 sitemap.yaml + sections.yaml** | n/a / handled via stack adapter — the stack adapter owns `/book`, `/booking-confirmed`, `/booking-cancelled` page registrations in `sitemap.yaml`. Cal.com adds off-site `cal.com/{username}/{event-slug}` URLs (Cloud) or `{self-hosted-domain}/{username}/{event-slug}` URLs (self-hosted) for direct event-type bookings. |
| **L3 strings/{lang}.json** | n/a / handled via stack adapter for the marketing-site's booking-CTA labels + booking-confirmed page copy. Cal.com's own UI strings auto-translate per browser locale (~25 languages — see § "i18n + currency"). |
| **L4 content/pages/*.md** | Carries booking-page intro content (`content/pages/book.md` — "Book a consultation; choose a time that works"), booking-success page (`content/pages/booking-confirmed.md` — confirmation + onboarding next steps), cancellation policy (`content/pages/cancellation-policy.md` — refund window, no-show terms), and event-type descriptions (`content/event-types/{slug}.md` — long-form description that Cal.com event type's `description` field references via summary, or the website-builder renders alongside the embed). |
| **L5 briefs/{component}.json** | n/a / handled via stack adapter — booking-CTA / event-type-card / availability-display components are generated by the stack adapter at phase 18; the brief targets the stack-native component shape, not Cal.com's hosted booking UI. The Cal.com embed is a *destination* the booking-CTA component triggers, not a component itself. |

The mandatory table preserves cross-adapter consistency for the General's row-by-row verification across booking adapters AND against stack adapters AND against commerce adapters.

## i18n + currency

Cal.com has native i18n + first-class timezone handling. Booking adapters are TZ-aware in a way commerce adapters aren't — customer-TZ + provider-TZ are distinct concepts.

- **Booking UI languages:** Cal.com auto-translates booking UI to ~25 languages (EN / DE / FR / IT / ES / PT / NL / PL / RU / JA / ZH / etc.) based on browser locale.
- **Time zones:** customer's local time zone shown by default (Cal.com auto-detects via browser); user's (the host's) time zone respected for availability rules. Customer sees "10:00 in your time zone" alongside the host's time zone if they differ.
- **Currencies:** for paid bookings, Cal.com supports ~30 currencies depending on Stripe / PayPal support — see § "TWINT-for-Switzerland callout" for CHF + TWINT specifics.
- **Date formats:** locale-aware (DD.MM.YYYY for de-CH, MM/DD/YYYY for en-US, etc.) — Cal.com handles this.

For the website-builder's i18n integration:

- **Marketing-site i18n** → handled by the stack adapter (next-intl on Next.js, etc.); agent generates `content/strings/{lang}.json` for the site itself.
- **Cal.com UI i18n** → automatic via Cal.com's browser-locale detection. Agent may pass `lang` parameter on the embed snippet to force a specific locale (`Cal('init', {lang: 'de'})`).
- **Per-event-type translation:** for users serving multiple languages, agent can create per-language event-type variants (e.g., `consult-30-en` + `consult-30-de`) with localized titles and descriptions. The site's language switcher routes to the matching event type. Alternative: a single event type with bilingual title/description.
- **Timezone display on marketing site:** agent uses `Intl.DateTimeFormat(locale, { timeZoneName: 'short' })` per locale when displaying availability summaries outside the Cal.com embed.

## TWINT-for-Switzerland callout

**TWINT is the non-negotiable Swiss-market payment method.** Per `commerce-adapters/README.md` § "TWINT-for-Switzerland — non-negotiable rule" + `Workstreams/website-builder/website-builder.md` decision 26 (Switzerland home market) + decision 47 (TWINT priority) + `DESIGN-booking-calcom.md` lines 150-156 + 196-200.

This adapter's TWINT support classification: **Via Stripe bridge from another platform** (NOT direct). Cal.com itself does NOT process payments; for TWINT-on-paid-bookings, Cal.com bridges to Stripe (which provides native TWINT support per [commerce-stripe.md § TWINT-for-Switzerland callout](commerce-stripe.md#twint-for-switzerland-callout)). **PayPal-bridge does NOT support TWINT** — agent enforces Stripe selection for Swiss-audience paid bookings.

### The TWINT bridge chain

```
Cal.com event type (CHF currency, paid)
   ↓
Cal.com → Stripe connection (configured in Cal.com Dashboard → Apps → Stripe)
   ↓
Stripe Checkout (TWINT payment_method enabled for CHF Session)
   ↓
TWINT app on customer's phone (QR scan / push approval)
   ↓
Payment confirmation → Stripe webhook → Cal.com webhook → booking confirmed
```

The chain MUST be Stripe — not PayPal. PayPal does not bridge TWINT.

### CHF-only constraint inherited from Stripe

All TWINT constraints from the Stripe layer apply:

- **Currency:** TWINT is **CHF-only** (per `docs.stripe.com/payments/twint`). Cal.com event types using TWINT MUST set `currency: CHF`. For multi-currency users (CH + EU customers), agent creates per-currency event types: a CHF variant (TWINT enabled via Stripe) and a EUR variant (card / SEPA / iDeal — TWINT not offered).
- **Maximum transaction:** 5,000 CHF per booking (Stripe-enforced; agent surfaces this at phase 24b if any event-type price exceeds CHF 5,000).
- **Eligible merchant countries:** the user's Stripe account can be in any of 35 European countries (AT, BE, BG, CH, ...); the customer must be in Switzerland to use TWINT.

### Configuration at phase 24b (paid bookings, Swiss audience)

Step-by-step:

1. **In Cal.com Dashboard:** user goes to Settings → Apps → connects Stripe (OAuth flow — Cal.com redirects to Stripe, user authorizes, Cal.com stores the connected account ID).
2. **In Cal.com event type:** for the paid event type (e.g., "Strategy Session 60min CHF 150"), user enables "Require payment" in event-type settings + sets price = `15000` (minor units) + currency = `CHF`.
3. **In Stripe Dashboard (the user's Stripe account):** TWINT enabled in Settings → Payment methods (Dashboard-driven; Stripe auto-surfaces TWINT for CHF Sessions Cal.com creates).
4. **Agent verifies the bridge:** runs a paid-booking rehearsal in test mode — books the CHF event type → Stripe Checkout fires → TWINT shows as a payment option alongside card → simulator confirms payment → Cal.com webhook fires → booking confirmed.

### PayPal-bridge incompatibility (CRITICAL surface)

If a Swiss-audience user has Cal.com bridging to PayPal instead of Stripe, **TWINT will not appear** in checkout. This is a Cal.com configuration choice — Cal.com supports either Stripe or PayPal as the bridge processor, NOT both simultaneously per event type.

For Swiss-audience users: **agent enforces Stripe selection at phase 24a/b** for any paid event type with CHF currency. If the user already has Cal.com → PayPal connected for non-CHF event types, agent surfaces that CHF event types need a Stripe connection (Cal.com supports per-event-type payment processor selection on Organizations / Enterprise tier; on Cloud tiers, the connection is account-wide — agent surfaces the trade-off).

### Phase 4 fixture scope vs Phase 10+ paid-CH variant

The Phase 4 Cal.com fixture (`tests/commerce-adapters/calcom/`) exercises **free bookings only** — `expected.yaml.phase_24b_payment.applicable: false`. Reasoning:

- Free-booking is the most common Cal.com entry path for muggles (free intro consultations driving paid engagement separately).
- Paid-booking-with-TWINT requires both Cal.com + Stripe + TWINT enablement — a 3-system bridge test that overlaps with the Stripe fixture's TWINT validation.
- A `calcom-paid-ch/` fixture (Phase 10+ scope) would exercise the Cal.com → Stripe → TWINT bridge chain end-to-end with CHF event types, audience_regions: [CH], and `expected.yaml.phase_24b_payment.twint_enabled: true` via the bridge.

For Phase 4: the adapter file documents the chain; the fixture demonstrates the free-booking baseline; the paid-CH variant is deferred. Per `tests/commerce-adapters/README.md` line 266: "A future CH-paid-booking variant (`calcom-paid-ch/`) at Phase 10+ would carry CH region + Stripe bridge + TWINT validation."

### Cross-link to canonical contracts

- TWINT contract (5-condition rule): [commerce-adapters/payment-config-schema.md § TWINT contract](payment-config-schema.md#twint-contract--non-negotiable-for-ch-audience-projects)
- Sibling Stripe adapter (where TWINT lives natively): [commerce-adapters/commerce-stripe.md § TWINT-for-Switzerland callout](commerce-stripe.md#twint-for-switzerland-callout)
- Phase 4 DoD anchor: `Workstreams/website-builder/BUILD-strategy.md` line 202 — *"TWINT path validates on Stripe Checkout (CH-region simulation)"* — booking-adapter side bridges to Stripe for the same contract

### Pause-and-report rule

If a Swiss-audience user picks Cal.com + PayPal (not Stripe) AND has paid CHF event types AND wants TWINT — surface this as a critical decision per `commerce-adapters/README.md` § "TWINT-for-Switzerland — non-negotiable rule" point 4:

- **(a)** Switch Cal.com's payment processor to Stripe — enables the TWINT bridge for CHF event types
- **(b)** Accept losing TWINT — requires **explicit user confirmation** of the ~35%+ Swiss revenue impact on paid-booking conversion

## Phase 24a/24b/24c integration (booking branch)

> Canonical `payment-config.yaml` schema for paid-booking phase-24b output: see [commerce-adapters/payment-config-schema.md](payment-config-schema.md). Adapter file does not duplicate the schema — only documents the Cal.com → Stripe bridge cells (per Captain 0 spec, S8).

### Phase 24a — Booking platform setup (booking branch)

Phase 24a applies to booking-only sites even when there's no traditional storefront. The booking branch differs from commerce in that "platform setup" means event-type creation + availability + integrations rather than product/price/checkout creation.

1. Agent confirms Cal.com is the right choice (services / appointments business, 1-many event types, time-based pricing). Decision tree per `DESIGN-booking-calcom.md` lines 34-41 — if the user is selling products (not time), route to a commerce adapter.
2. Agent helps the user pick Cal.com Cloud (Free / Teams / Organizations) vs self-hosted:
   - **Cloud, muggle default:** solo user → Free; 2+ staff → Teams ($12/user/mo); enterprise → Organizations ($28/user/mo) or Enterprise (custom).
   - **Self-hosted, ops-capable user:** Docker / Railway / Vercel deployment; agent generates `docker-compose.yml` per the Cal.com self-hosting guide (https://cal.com/docs/self-hosting).
3. **Cloud signup:** user signs up at `cal.com/signup`; agent guides through username selection + initial profile setup; user generates API key in Dashboard → Settings → Developer → API Keys; copies to 1Password.
4. **Self-hosted deployment:** agent guides Docker Compose setup or one-click Railway / Vercel deploy; user creates admin account; generates API key through the deployed Settings UI.
5. Agent uses Cal.com REST API (or community FastMCP if installed per § "API + MCP availability") to create event types matching `project.yaml.services` or interview output. Per-event-type configuration:
   - Title, slug, duration (15/30/45/60/90 min typical), location (`integrations:google:meet`, `integrations:zoom`, `integrations:daily`, etc.), description
   - Price (if paid booking) + currency (`CHF` for Swiss audience — see § "TWINT-for-Switzerland callout"; `EUR`/`USD`/`GBP`/etc. per audience)
   - Buffer time (before / after) — 5-15 min typical
   - Booking window (e.g., 1-day notice; 90-day-ahead booking limit)
   - Availability rules (working hours, days of week)
6. **Calendar integration:** agent guides user to connect Google Calendar / Microsoft 365 / Apple Calendar / CalDAV in Cal.com Dashboard → Apps → Calendars; verifies the integration syncs (Cal.com reads calendar for availability + writes booked events back).
7. **Video integration:** agent guides user to connect Zoom / Google Meet / Daily / Whereby per event type; auto-generated meeting links populate each booking.
8. **Embed on user's site:** agent generates per-stack embed code (per § "Stack pairings"):
   - **Inline:** event-type page renders Cal widget directly (booking-flow on the site)
   - **Popup:** "Book a call" button opens overlay (mode default for muggle "schedule a consult" CTA)
   - **Floating button:** persistent CTA on every page (high-conversion bookings business)
9. Agent runs **booking-flow rehearsal**: book a test event type → confirms Cal.com booking creation → confirms calendar event creation → confirms confirmation email + video link.
10. Agent updates `.website-builder/commerce-config.yaml.bookings` with Cal.com config + key env-var names + event-type IDs.

### Phase 24b — Payment provider wiring (for paid bookings)

**Only runs if `commerce-config.yaml.bookings[].price > 0` on any event type.** For free-booking-only sites, phase 24b is skipped entirely (this is the Phase 4 fixture's scope).

For paid bookings, Cal.com bridges to a payment processor:

1. **Connect Stripe in Cal.com Dashboard:** user goes to Dashboard → Apps → Stripe → connects (OAuth flow). Cal.com stores the connected Stripe account ID.
2. **Verify Stripe is in live mode for production deploy** — Cal.com bridges to whatever mode the Stripe account is in; agent enforces the live-key flip per the Stripe adapter's discipline (see [commerce-stripe.md § Auth model](commerce-stripe.md#auth-model)).
3. **Enable TWINT on Stripe for Swiss audience (if applicable):** agent guides user to Stripe Dashboard → Settings → Payment methods → enable TWINT. TWINT methods will then appear in the bridged Stripe Checkout when Cal.com creates a Session for a CHF event type. Per § "TWINT-for-Switzerland callout".
4. **Configure webhook:** Cal.com webhook fires on `BOOKING_PAID`; agent verifies the user's site receives + processes the webhook (booking-confirmed flow downstream of payment).
5. **Run paid-booking rehearsal:** book the paid event type → Stripe Checkout fires (with TWINT visible for CHF) → test payment (Stripe test cards: `4242 4242 4242 4242` succeeds) → Cal.com booking confirmed → calendar event + video link generated.

For PayPal-bridged sites: same flow but TWINT does NOT appear (per § "TWINT-for-Switzerland callout"); agent surfaces this trade-off at phase 24b.

The `.website-builder/payment-config.yaml` for Cal.com → Stripe-bridge paid-booking projects mirrors the commerce-adapter's Stripe configuration (see [payment-config-schema.md](payment-config-schema.md) — the same canonical schema; the Stripe-side `providers[0]` block applies; Cal.com adds `commerce-config.yaml.bookings[].payment_processor: stripe` to declare the bridge).

### Phase 24c — Commerce-specific legal (booking branch, for paid bookings)

For paid bookings — bookings are service contracts; legal is non-trivial:

1. **Cancellation / refund policy** — REQUIRED. Agent generates from user's actual policy (e.g., "Full refund if canceled >24 hours in advance; 50% refund 12-24 hours; no refund <12 hours"). Stored at `content/pages/cancellation-policy.md`; referenced from Cal.com event-type settings.
2. **No-show policy** — REQUIRED if relevant. Policy on what happens when the customer doesn't attend.
3. **T&Cs of service** — REQUIRED. The booking IS a service contract; the T&Cs cover scope, deliverables, confidentiality.
4. **Tax handling** — user's responsibility (Cal.com is NOT MoR). Same disposition as Stripe adapter — see [commerce-stripe.md § Phase 24c — Commerce-specific legal](commerce-stripe.md#phase-24c--commerce-specific-legal). User as MoR; Stripe Tax (+0.5%) or accept manual tax handling.
5. **Imprint (DACH)** — REQUIRED for Germany / Austria / Switzerland audiences.
6. **GDPR / privacy** — REQUIRED. Booking data IS personal data (name, email, phone, calendar event metadata) — user's privacy policy must disclose Cal.com as a data processor. For self-hosted: user is data controller AND processor (simplifies the disclosure).

For **free bookings**: minimal legal — cancellation policy + privacy policy still recommended (free intro consult is still a service interaction; GDPR applies if EU customers).

## Mid-project transactional change handling

Per Decision 34 (transactional flag changes mid-project):

| Scenario | Re-runs |
|---|---|
| User adds Cal.com mid-project (was non-transactional or had no booking flow) | **Phase 12 (CMS)** — Cal.com is independent of CMS; no conflict. **Phase 22 (forms)** — existing forms continue; agent adds booking embed alongside. **Phase 24a runs from scratch** (event types + availability + integrations). **Phase 24b only if paid bookings.** **Phase 25 (legal)** — existing pages supplemented with booking-specific legal (cancellation policy + GDPR disclosure of Cal.com). |
| User changes from free booking → paid booking mid-project | **Phase 24b only** (light touch) — agent enables Stripe / PayPal bridge in Cal.com, updates event-type pricing, adds TWINT for CHF if Swiss audience. **Phase 24c additions** — cancellation/refund policy + T&Cs of service + GDPR. |
| User switches from Cal.com → Calendly (Phase 10+ scope) | Phase 24a full restart on Calendly adapter; event-type migration (titles, durations, availability) — agent surfaces the migration cost. |
| User switches Cal.com payment processor (Stripe ↔ PayPal) | Partial phase 24b: agent reconfigures the bridge in Cal.com Dashboard; updates `commerce-config.yaml.bookings[].payment_processor`; if switching FROM Stripe TO PayPal for CHF event types with Swiss audience, fires the TWINT pause-and-report rule. |

Decision logged in `.website-builder/decisions/transactional-change-{ts}.md`.

## Phase 6.5 ingestion (existing setup)

When `entry_mode = has-existing-site` AND the existing user already has Cal.com:

1. Agent connects via Cal.com API using user-supplied API key (or via the community FastMCP if the user has one installed).
2. Lists existing event types → seeds `commerce-config.yaml.bookings[]` with title / slug / duration / location / price / currency.
3. Lists recent bookings (last 30 days typical) → understands volume + booking mix + whether the user is doing free vs paid bookings.
4. Identifies enabled integrations (calendar, video, payment) → seeds `commerce-config.yaml.bookings.integrations` and (if paid) `payment-config.yaml` Stripe block.
5. Lists configured webhooks → identifies live webhook endpoint URLs.
6. **TWINT presence check (paid CHF event types):** if any event type has `currency: CHF` AND audience suggests CH (per `project.yaml.audience_regions` or languages), agent verifies the Stripe bridge has TWINT enabled. If not, flags the gap + recommends enabling.
7. Logs ingestion in `.website-builder/decisions/ingest-{ts}.md` with: event types found, bookings volume, payment processor (Stripe / PayPal / none), TWINT-presence verdict for CHF event types, gaps flagged.

> Test fixture cross-link: [tests/commerce-adapters/calcom/fixture/](../tests/commerce-adapters/calcom/fixture/) — the Phase 4 fixture demonstrates the canonical free-booking baseline (Cal.com + 2 free event types + Next.js stack).

## Limitations

- **Booking-only.** Not a full commerce platform — no products / catalog / cart / inventory. For mixed-mode (products + bookings), agent pairs Cal.com with a commerce platform (Stripe Checkout per [commerce-stripe.md](commerce-stripe.md) is the most common pairing; Shopify + Cal.com for product-heavy + booking-heavy is Phase 10+ scope).
- **Self-hosted operational burden.** AGPLv3 + ~$5-50/mo hosting + real DevOps for self-hosters. Not muggle-friendly unless the user has an ops resource.
- **AGPLv3 license restrictions (self-hosted).** Only matters if user modifies + offers Cal.com-as-a-service; doesn't trigger for ordinary use.
- **Embed customization is moderate.** Cal.com Atoms (React components) for white-label; standard embed is Cal-styled with limited theming. Full white-label requires Cal.com Platform (Organizations / Enterprise tier).
- **Payment processor required for paid bookings.** Cal.com doesn't process payment itself — it bridges to Stripe or PayPal. User must have a Stripe or PayPal account.
- **Multi-staff scheduling requires Teams plan.** $12/user/mo annual minimum for round-robin / team event types / managed event types.
- **TWINT only via Stripe bridge.** PayPal-only paid-booking setups CANNOT use TWINT — per § "TWINT-for-Switzerland callout". CHF event types + Swiss audience MUST be on Stripe bridge.
- **Calendar integration required for live bookings.** Cal.com can technically run without an external calendar (uses its own data store) but availability conflicts become invisible — agent enforces calendar connection at phase 24a.
- **Cal.com Free tier is single-user.** No team scheduling, no managed event types — solo only.
- **Per-event-type payment processor on Cloud tiers is account-wide.** Only Organizations / Enterprise tiers support per-event-type processor selection — agent surfaces this if user has mixed-currency paid bookings on Cloud Free / Teams.

## Common failure modes

- **Calendar integration not configured before launch.** Agent enforces calendar connection at phase 24a; refuses to mark phase 24a complete without it. Symptom: bookings get created but don't appear on user's calendar; double-bookings silent.
- **Time-zone confusion.** Customer books in their TZ; agent / user expects user's TZ. Cal.com handles TZ conversion natively — agent uses Cal.com's TZ-aware API consistently; emails customer in customer-TZ, emails user in user-TZ.
- **Test bookings appear on user's real calendar.** Agent uses Cal.com test mode (Cloud) or a dedicated test event type with a non-production calendar integration; runs rehearsal bookings against the test setup to avoid polluting the user's real calendar.
- **TWINT not enabled for Swiss audience paid bookings.** Agent flags at phase 24b for any paid CHF event type with CH audience; verifies Stripe bridge has TWINT enabled (NOT PayPal bridge). Per § "TWINT-for-Switzerland callout".
- **Buffer time not configured (back-to-back bookings).** Agent prompts user at phase 24a for realistic buffer (10-15 min typical for video calls; longer for in-person sessions).
- **Payment confirmation webhook not configured.** Agent enforces Cal.com webhook setup so booking is only confirmed AFTER payment success. Without the webhook, bookings can be created (pending payment) but never auto-confirmed when payment lands; agent generates the webhook handler code per stack.
- **PayPal bridge selected for CHF event types.** Symptom: TWINT doesn't appear in checkout for Swiss customers. Agent enforces Stripe selection for CHF event types per § "TWINT-for-Switzerland callout".
- **Webhook signature not verified (Cal.com side).** Cal.com webhooks include a `X-Cal-Signature` header for verification (HMAC-SHA256 of payload using the webhook secret). Agent enforces signature verification in generated webhook handler code; refuses to ship handler that accepts unsigned webhooks.
- **Embed script not loading on stack X.** Cal.com embed expects to bootstrap a `<script>` in the page head/body; stack adapters that use strict CSP (Next.js with strict Content-Security-Policy headers) may block the script — agent generates a CSP exception for `embed.cal.com` at phase 24a when CSP is in use.
- **Free-booking event type left enabled in paid mode.** User configures price > 0 but doesn't enable "Require payment" toggle in Cal.com Dashboard — symptom: booking succeeds, customer never charged. Agent verifies "Require payment" is on after setting price > 0.

## References

### Foundation cross-references

- `Workstreams/website-builder/foundation/DESIGN-architecture.md` — plugin directory layout (`commerce-adapters/` per line 100)
- `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` — phase 22 (forms / transactional) + phase 24a (booking platform setup, booking branch) + 24b (payment provider, paid bookings only) + 24c (booking legal)
- `Workstreams/website-builder/foundation/DESIGN-content-layers.md` — the 5 content layers the § "Content layer mapping" table maps
- `Workstreams/website-builder/foundation/DESIGN-i18n.md` — i18n model + timezone + currency
- `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` — `.website-builder/` directory layout
- `Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md` — phase 6.5 mechanism

### Source design docs

- `Workstreams/website-builder/commerce/DESIGN-booking-calcom.md` — Cal.com source design doc (lines 17-267)
- `Workstreams/website-builder/commerce/DESIGN-payment-providers.md` — payment-provider matrix + TWINT-critical section (lines 222-274 for the TWINT-via-Stripe-bridge specifics)

### Captain 0 prep packet (sibling Phase 4 files)

- [commerce-adapters/README.md](README.md) — commerce + booking adapter schema contract (read-only)
- [commerce-adapters/payment-config-schema.md](payment-config-schema.md) — canonical `payment-config.yaml` schema (read-only; this adapter references for paid-booking config via Stripe bridge)
- [commerce-adapters/commerce-stripe.md](commerce-stripe.md) — sibling commerce adapter (Stripe); cross-link for TWINT-via-Stripe-bridge specifics
- [tests/commerce-adapters/README.md](../tests/commerce-adapters/README.md) — fixture convention; free-booking-only fixture for Phase 4; paid-CH variant deferred to Phase 10+
- [tests/commerce-adapters/calcom/fixture/](../tests/commerce-adapters/calcom/fixture/) — Phase 4 Captain L deliverable: free-booking baseline fixture
- [tests/commerce-adapters/calcom/expected.yaml](../tests/commerce-adapters/calcom/expected.yaml) — Phase 4 Captain L deliverable: expected phase-24a free-booking output

### Stack pairing cross-references

- `adapters/stack-framer.md` § "Commerce integration → Booking flows" — Cal.com via Framer Code Component
- `adapters/stack-nextjs.md` § "Commerce integration → Booking flows" — Cal.com via `@calcom/embed-react` (MVP default per decision 54)
- `adapters/stack-wordpress.md` § "Commerce integration → Booking flows" — Cal.com via custom Gutenberg block

### External (verified 2026-05-20)

- Cal.com homepage: https://cal.com
- Cal.com API reference v2: https://cal.com/docs/api-reference/v2
- Cal.com self-hosting guide: https://cal.com/docs/self-hosting
- Cal.com GitHub: https://github.com/calcom/cal.com (AGPLv3, open-source)
- Cal.com Atoms (React white-label components): https://cal.com/docs/platform
- Cal.com Pricing (verified 2026-05-20 — lower than design-doc figures): https://cal.com/pricing
  - Free $0/mo, Teams $12/user/mo annual (was $15-19), Organizations $28/user/mo annual (was $37), Enterprise custom
- Cal.com "Best MCP Servers" blog (Cal.com's stance: no official MCP, API-first): https://cal.com/blog/best-mcp-servers
- Community FastMCP: https://github.com/Danielpeter-99/calcom-mcp (MIT, NOT affiliated with Cal.com; tools: list_event_types, get_bookings, create_booking, list_schedules, list_teams, list_users, list_webhooks)
- Composio hosted Cal.com MCP: https://mcp.composio.dev/cal
- context7 library IDs: `/websites/cal_api-reference_v2` (benchmark 83.3), `/calcom/cal.com` (benchmark 77.91), `/llmstxt/cal_llms-full_txt`

### Phase 4 / Phase 10+ booking-adapter siblings

- (future, Phase 10) `booking-calendly.md` — proprietary Calendly alternative; Calendly Embed JS / React widget
- (future, Phase 10) `booking-simplybook.md` — SimplyBook.me; multi-service salon-style booking with package + payment

### Phase 10+ commerce-adapter pairings (for sites that need BOTH bookings + products)

- [commerce-stripe.md](commerce-stripe.md) — Stripe Checkout for one-off product sales alongside Cal.com bookings (most common pairing)
- (future, Phase 10) `commerce-shopify.md` — Shopify + Cal.com for product-heavy + booking-heavy businesses

### Decision anchors

- `Workstreams/website-builder/website-builder.md` decision 18 (full stack coverage), decision 26 (Switzerland home market), decision 34 (transactional flag mid-flip), decision 47 (TWINT priority), decision 54 (Cal.com booking default — THIS adapter), decision 58 (parallel-to-platform subproject location), decision 65 (per-callsign worktree)
- `Workstreams/website-builder/BUILD-strategy.md` Phase 4 DoD lines 187-209 (booking adapter scope; line 202 TWINT contract bridged via Stripe for Cal.com paid bookings)
