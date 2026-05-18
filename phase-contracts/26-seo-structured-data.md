---
phase: 26
name: SEO + structured data + metadata
group: pre-launch
pipeline_section: pre-launch
skill: wb-prelaunch
prev_phase: 25
next_phase: 27
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/foundation/DESIGN-ecosystem-catalog.md
---

# Phase 26 — SEO + structured data + metadata

> Make every page discoverable and machine-readable: title tags, meta descriptions, Open Graph, Twitter cards, schema.org structured data (the right type per page — Organization, LocalBusiness, Product, Article, Event, Review), sitemap.xml, robots.txt. The phase where the site stops being invisible to search engines and to the LLMs that now interpret brands. The agent refuses to advance with missing or duplicated metadata on any page, and enforces page-specific descriptions over the single-template-everywhere failure.

## Mission

By phase 26 the site is built, integrated, legally sound, and the words are written (phase 16) — but to a search crawler or an LLM-discovery agent it is a wall of unlabelled HTML. Phase 26 adds the metadata and structured-data layer that makes every page (a) discoverable (it appears in search), (b) correctly previewed (its social share card and search snippet say the right thing), and (c) machine-readable (schema.org structured data tells Google and LLMs *what kind of thing* this page is — a local business, an article, a product, an event — so it can be represented as a rich result and interpreted accurately in conversational search).

The discipline is **per-page specificity**. The single most common SEO failure on muggle sites is the same title tag and the same meta description on every page — because a template set them once and nobody differentiated. The agent refuses this: every page gets a title that describes *that page*, a meta description written for *that page's* intent and SERP snippet, an Open Graph image and card appropriate to *that page*, and schema.org structured data of the *type that page actually is*. A 200-char identical description across 12 pages is not "SEO done"; it is SEO actively working against the site.

The second discipline is **truthful structured data**. schema.org markup that claims a `Product` with an `AggregateRating` the site does not actually have, or `Event` data that does not match the visible page, is a Google structured-data policy violation that can earn a manual action. The agent emits structured data that describes what the page genuinely contains — markup mirrors content, never invents it.

This contract is the canonical SEO reference for the pipeline. There is no website-builder design doc dedicated to SEO; the agent confirms current schema.org type surface and Google's current structured-data guidance via `WebFetch` at authoring time (both evolve) and applies them per page.

## Entry conditions

- Phase 25 (legal pages) complete. The legal pages exist and are part of the page set phase 26 must give metadata to (a privacy/imprint page still needs a title and a `robots`-appropriate directive — typically indexable but not a priority in the sitemap).
- Phase 16 (copywriting) complete — finalized prose exists. Meta descriptions are written *from* the real page content and voice (phase 5), not invented; the SEO title relates to the real headline. Phase 26 does not write new marketing copy; it writes the metadata layer over finalized content.
- `.website-builder/sitemap.yaml` (phase 9/10) — the canonical list of every page + its type (home / about / service-detail / blog-post / contact / legal). The page-type drives which schema.org type applies (a service-detail page → `Service`/`Product`; a blog post → `Article`/`BlogPosting`; the home/about of a local business → `LocalBusiness`/`Organization`).
- `.website-builder/project.yaml.requirements` (phase 3) — the primary audience and conversion outcome inform which pages are SEO-priority and what search intent each title/description targets.

## What Claude must establish

A complete, per-page-specific metadata + structured-data layer plus the crawl-control files. The work product:

1. **Per-page title tags** — unique per page, describing that page, front-loading the distinguishing term, within the practical SERP-display length, ending with the brand where it helps recognition.
2. **Per-page meta descriptions** — unique per page, written for the SERP snippet and the page's actual intent, in the brand voice (phase 5), no two pages sharing a description. (Google may rewrite descriptions, but a specific human-written one is still the right input and the right fallback.)
3. **Open Graph + Twitter/X cards** — per page: `og:title`, `og:description`, `og:image` (an image appropriate to the page, correctly sized), `og:type`, `og:url`; `twitter:card` (summary or summary_large_image) + the matching fields. The share preview says the right thing for *that* page.
4. **schema.org structured data, JSON-LD, the right type per page** — Google's recommended format is JSON-LD. The agent emits the type the page actually is, with the type's core properties populated from real content:
   - **Organization** / **LocalBusiness** — site-wide / home / about for a business or local business: `name`, `url`, `logo`, contact, and for LocalBusiness `address`, `telephone`, `openingHours`, `geo`.
   - **WebSite** (with `SearchAction` where site-search exists) + **WebPage** — site/page baseline.
   - **Article** / **BlogPosting** — blog/essay/news pages: `headline`, `author`, `datePublished`, `image`, `articleBody`.
   - **Product** / **Service** + **Offer** — for transactional sites: `name`, `description`, `offers` (price, currency, availability). `AggregateRating`/`Review` only if real reviews exist.
   - **Event** — event pages: `name`, `startDate`, `location`, `offers`.
   - **Person** — personal-brand/portfolio: `name`, `jobTitle`, `sameAs` (social profiles).
   - **BreadcrumbList** — navigational hierarchy for deep sites.
   - **FAQPage** — only on pages with genuine Q&A content (Google's FAQ rich result eligibility narrowed; the agent surfaces current eligibility rather than blanket-adding FAQ markup).
5. **sitemap.xml** — every indexable page, generated (build-step wired so it regenerates on content change, not a stale one-time file), excluding noindex/thin pages.
6. **robots.txt** — allowing crawl of the public site, disallowing what should not be indexed (admin/preview paths), pointing at the sitemap.
7. **`.website-builder/audit/SEO-REPORT.md`** — per page: title, description, OG/Twitter set, schema.org type + properties emitted, validation result (Rich Results Test / Schema Markup Validator), and the LLM-discoverability note (does the page's metadata + structured data read coherently to a model, not just a crawler).

The agent updates `.website-builder/project.yaml.current_phase` to `27` upon completion.

## Gating rules

The agent refuses to advance when:

- **Any page has missing metadata.** A page with no `<title>`, no meta description, no OG tags. Every page in `sitemap.yaml` has the full metadata set. Not overridable for missing title/description (a titleless page is a broken SERP entry).
- **Identical title or description across pages.** The defining gate of this phase. Two or more pages sharing a title tag or a meta description means the template was set once and never differentiated — the agent enforces page-specific text and refuses the single-template-everywhere state. Overridable only for genuinely-equivalent pages (rare; e.g., paginated archive pages) with the rel-canonical/pagination handled correctly and logged.
- **Structured data that does not match visible content.** `AggregateRating` markup with no real reviews on the page; `Event` JSON-LD whose date contradicts the visible date; `Product` offer price not matching the page. Google's policy treats this as spam; the agent emits only structured data the page genuinely supports. **Not overridable** — invented structured data risks a manual action.
- **Invalid structured data.** The JSON-LD fails the Rich Results Test / Schema Markup Validator (syntax error, missing required property for the claimed type). The agent validates before marking done and fixes errors rather than shipping invalid markup.
- **sitemap.xml stale or hand-frozen.** A one-time sitemap that will not regenerate when content changes. The agent wires the sitemap into the build so it stays accurate; a frozen sitemap is a phase-29 (deploy) and post-launch drift source.
- **robots.txt blocking the whole site or leaking admin paths into the index.** A `Disallow: /` left from a staging config (the site will deindex), or no disallow on preview/admin paths. The agent verifies robots.txt does what the launched site needs.

## Tools and skills used

- **`Edit` / `Write`** — to embed per-page metadata (title/description/OG/Twitter) and JSON-LD structured data into the project per the stack's mechanism (Next.js Metadata API / `generateMetadata`; Astro `<head>` / component; WordPress SEO via theme or a plugin's structured-data; Framer page settings), and to generate/wire sitemap.xml + robots.txt into the build.
- **`WebFetch`** — **mandatory at this phase**: `https://schema.org/` (current type surface — confirm the page-relevant types and their core properties: LocalBusiness, Organization, Article/BlogPosting, Product/Service, Offer, Event, Review/AggregateRating, BreadcrumbList, FAQPage, Person, WebSite) and `https://developers.google.com/search/docs/appearance/structured-data` (Google's current supported rich-result types, JSON-LD recommendation, the Rich Results Test, current FAQ/HowTo eligibility narrowing, structured-data policies). Cited in `## Reference materials`.
- **Validation tooling** — Google Rich Results Test (Google-specific rich-result eligibility) and the schema.org Markup Validator (generic schema validity). The agent validates every page's JSON-LD before marking the page done; via `WebFetch`/`Bash` against the validator endpoints or the public test tools.
- **`Playwright` MCP** — to confirm the metadata actually renders into the served HTML `<head>` (SSR/SSG correctness — a meta tag that only appears after client hydration is invisible to many crawlers; the agent checks the server-rendered source).
- **`Read`** — `sitemap.yaml` (the page set + types — drives schema.org type per page), `project.yaml.requirements` (audience/intent — drives title/description targeting), the finalized `content/pages/*.md` (the real content the metadata + structured data must mirror), `brand.yaml.voice` (descriptions in voice).
- **Reference-data load** — `${CLAUDE_PLUGIN_ROOT}/reference/seo-checklists/` (per `DESIGN-phase-contracts.md` seed) and `foundation/DESIGN-ecosystem-catalog.md` for schema.org corpus reference data.

No subagent spawn. `wb-prelaunch` phase-group skill carries phases 24-27; the structured data emitted here is re-verified rendering-correct in phase 27's cross-browser pass and submitted to Search Console/Bing in phase 30.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| Per-page metadata + JSON-LD in the project | Per stack convention; unique title/description/OG/Twitter + page-appropriate schema.org JSON-LD per page | The discoverability + machine-readability layer — live in the served HTML head |
| `sitemap.xml` (build-generated) | Standard sitemap protocol; every indexable page; regenerates on content change | Crawl map; submitted to Search Console + Bing at phase 30 |
| `robots.txt` | Allow public, disallow admin/preview, sitemap reference | Crawl control |
| `.website-builder/audit/SEO-REPORT.md` | Per page: title, description, OG/Twitter, schema.org type + properties, validation result, LLM-discoverability note | Audit trail proving per-page specificity + valid truthful structured data; read by phase 27 (render verification), phase 29 (deploy), phase 30 (sitemap submission) |

The `SEO-REPORT.md` is the required artifact.

## Common failure modes

**Identical meta description across every page.** The single most common SEO failure on muggle sites — a template set one description and 12 pages share it. The agent's defining gate: every page gets a description written for *that page's* intent and SERP snippet. "SEO done" with one description everywhere is SEO done wrong; the agent enforces per-page text.

**Invented structured data.** `AggregateRating` 4.8 from 200 reviews — on a site with zero reviews. A `Product` `Offer` with a price the page does not show. Google treats markup-not-matching-content as spam and can issue a manual action that tanks the whole domain. The agent emits only structured data the page genuinely supports; markup mirrors content, never decorates it.

**Structured data that fails validation.** The JSON-LD has a syntax error or omits a required property for the claimed type, so Google ignores it (or flags it). The agent runs the Rich Results Test / Markup Validator before marking the page done and fixes errors rather than shipping markup that does nothing.

**Metadata only present after client hydration.** A SPA sets the title via JS after load; the server-rendered HTML the crawler sees has a generic `<title>`. The agent verifies the metadata is in the *server-rendered* head (Playwright against view-source), because client-only metadata is invisible to many crawlers and to LLM fetchers.

**`Disallow: /` left from staging.** A robots.txt copied from a staging config that blocked all crawling ships to production and the site silently deindexes. The agent verifies robots.txt is the *production* file and reflects what the launched site needs — a classic parity failure analogous to phase 24's.

**Stale hand-frozen sitemap.** A one-time sitemap.xml that lists 10 pages forever while the site grows to 30. The agent wires sitemap generation into the build so it stays accurate; a frozen sitemap is a slow-rotting discoverability failure the post-launch maintainer would otherwise inherit.

**Blanket FAQ/HowTo markup for rich results that no longer exist.** Google narrowed FAQ and HowTo rich-result eligibility. Adding `FAQPage` markup to every page chasing a rich result Google no longer shows for most sites is cargo-culting. The agent confirms *current* eligibility via the fetched Google guidance and adds FAQ markup only where the content is genuinely Q&A and the rich result is still attainable.

**Metadata written ignoring the brand voice.** The page copy is warm and specific (phase 16); the meta description is generic SEO-keyword soup. The description is the SERP's first impression and the agent writes it in the phase-5 voice — discoverable *and* on-brand, not one at the cost of the other.

**SEO treated as only-for-Google.** In 2026 LLMs are a primary brand interpreter (conversational search reads the page's metadata + structured data to represent the brand). The agent checks that each page's title/description/structured-data reads coherently to a *model*, not just a crawler — the positioning paragraph (phase 3) and the structured `Organization`/`Person` data are what an LLM surfaces when a user asks it about the brand.

## Reference materials

- **Design doc — phase pipeline source:** `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 26 (seed)
- **Design doc — pipeline integration:** `Workstreams/website-builder/foundation/DESIGN-architecture.md` § Phase contracts
- **Design doc — schema.org corpus reference data:** `Workstreams/website-builder/foundation/DESIGN-ecosystem-catalog.md` § Reference resources (schema.org corpus + SEO checklist source list)
- **Phase 16 (the finalized content the metadata mirrors + the voice):** `phase-contracts/16-copywriting.md` § What Claude must establish — descriptions are written from real content in the phase-5 voice; the 2026 AI-discovery context note (LLMs as first brand interpreter) directly informs this phase
- **Phase 9/10 (the page set + types driving schema.org type selection):** `sitemap.yaml` page-type field
- **Phase 30 (where sitemap.xml is submitted):** `phase-contracts/30-analytics-search-submission.md` § What Claude must establish
- **External research (loaded fresh 2026-05-18 for this contract):**
  - schema.org full type hierarchy — https://schema.org/docs/full.html — confirmed core types + properties for Organization, LocalBusiness, Product, Service, Offer, Article, BlogPosting, Event, Review, AggregateRating, BreadcrumbList, FAQPage, Person, WebSite, WebPage. Confirmed 2026-05-18.
  - Google structured-data guidance — https://developers.google.com/search/docs/appearance/structured-data — JSON-LD recommended; Rich Results Test is the primary Google-specific validator; Schema Markup Validator for generic validity; supported rich-result types in the search-gallery; structured-data must match visible content (policy). Confirmed 2026-05-18.
- **Voice (descriptions in brand voice):** `.website-builder/brand.yaml.voice` (phase-5 output)

Freshness date for this contract: **2026-05-18**. schema.org types + Google's rich-result eligibility evolve; the agent re-fetches both at session start when phase 26 is active and validates every page's JSON-LD against the current tools rather than trusting training-data schema knowledge.
