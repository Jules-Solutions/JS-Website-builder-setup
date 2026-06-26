---
type: REFERENCE
corpus: seo-checklists
title: SEO Checklist (Lighthouse-mapped)
checklist_slug: seo
lighthouse_category: seo
consumed_by_phases: [26]
---

# SEO Checklist — Lighthouse-mapped (Phase 26)

> Walk this top to bottom as a pre-launch SEO gate. Section 1 is the Lighthouse SEO category (mechanical failures Lighthouse scores). Section 2 is what Lighthouse does NOT score but search engines + social platforms require. Audit ids are the stable anchor across Lighthouse versions.

## 1. Lighthouse SEO category (mechanical, machine-checkable)

| Check | Lighthouse audit id | Why it matters | Fix path |
|---|---|---|---|
| Page has a `<title>` | `document-title` | Primary SERP headline + tab/bookmark label | Unique, descriptive `<title>` per page; ~50-60 chars; brand at the end |
| Page has a meta description | `meta-description` | SERP snippet (not a ranking factor, but drives CTR) | Unique `<meta name="description">` per page; ~140-160 chars; written for the click |
| Successful HTTP status | `http-status-code` | Pages returning 4xx/5xx aren't indexed | Ensure 200 for real pages; correct 301s for moved URLs; valid 404 page |
| Page isn't blocked from indexing | `is-crawlable` | A stray `noindex` silently de-indexes the page | Remove `<meta name="robots" content="noindex">` + `X-Robots-Tag: noindex` from pages that should rank |
| `robots.txt` is valid | `robots-txt` | A broken/over-broad `robots.txt` can block the whole site | Serve a valid `robots.txt`; don't `Disallow: /` production; link the sitemap from it |
| Links are crawlable | `crawlable-anchors` | JS-only `onclick` "links" aren't followed | Use real `<a href>` for navigation; never `<span onclick>` or `href="#"`-with-JS |
| Links have descriptive text | `link-text` | "Click here"/"read more" gives crawlers + screen readers no signal | Descriptive anchor text naming the destination ("View pricing", not "click here") |
| Images have alt text | `image-alt` | Alt = image SEO + accessibility; informative images need it | Meaningful `alt` for content images; empty `alt=""` for decorative |
| `hreflang` is valid (multilingual) | `hreflang` | Wrong-language page served to the wrong region | Correct `hreflang` per language variant + a reciprocal `x-default`; mirrors the plugin's i18n output |
| Document has a valid `rel=canonical` | `canonical` | Duplicate URLs split ranking signals | One self-referential canonical per page; canonical the preferred URL for duplicates/params |
| Structured data is valid | `structured-data` *(manual audit)* | Lighthouse flags it for manual review; rich results need valid JSON-LD | Validate JSON-LD in Google's Rich Results Test (see §2) |

> **Version note:** `font-size` (legible text) and `tap-targets` (touch-target sizing) were part of the SEO category in older Lighthouse and were removed/relocated as mobile emulation evolved. They remain real mobile-usability concerns — the agent covers them under accessibility + the component-pattern a11y sections, not as SEO audits.

## 2. Beyond Lighthouse — what search + social actually need (not auto-scored)

Lighthouse passing ≠ SEO-ready. These have no Lighthouse audit but are pre-launch-mandatory:

| Check | Why it matters | Fix path |
|---|---|---|
| **XML sitemap** | Tells crawlers every URL + last-modified | Generate `sitemap.xml` (most stacks have a plugin/integration); reference it in `robots.txt`; submit in Search Console |
| **Open Graph tags** | Controls the link preview on Facebook/LinkedIn/Slack/iMessage | `og:title`, `og:description`, `og:image` (1200×630), `og:url`, `og:type` per page |
| **Twitter/X Card tags** | Controls the X preview | `twitter:card` (`summary_large_image`), `twitter:title/description/image` |
| **JSON-LD structured data** | Eligibility for rich results | Add schema.org JSON-LD per page type (see table below); validate in Rich Results Test |
| **One `<h1>` + logical heading order** | Primary topic signal + a11y | Exactly one `<h1>` per page (the hero headline); no skipped levels (`h1→h2→h3`) |
| **Semantic landmarks** | Helps crawlers + AT parse structure | `<header>`/`<nav>`/`<main>`/`<footer>`; one `<main>` per page |
| **Descriptive, stable URLs** | Readable slugs rank + share better | Lowercase, hyphenated, keyword-bearing slugs from `sitemap.yaml`; avoid IDs/params for content pages |
| **Mobile viewport** | Mobile-first indexing baseline | `<meta name="viewport" content="width=device-width, initial-scale=1">` (Lighthouse `viewport` audit lives in best-practices/PWA, not SEO) |
| **Favicon + touch icons** | Brand in tabs + SERP + bookmarks | Favicon set + `apple-touch-icon`; referenced in `<head>` |
| **HTTPS + canonical host** | Ranking signal + avoids duplicate-host splits | Force HTTPS; pick www-or-non-www and 301 the other; canonical the chosen host |
| **Internal linking** | Spreads ranking signal + aids discovery | Every page reachable in ≤3 clicks; contextual internal links; breadcrumbs (see `component-patterns/breadcrumb.md`) |
| **Performance / Core Web Vitals** | A confirmed ranking signal | Cross-reference `performance.md` — phase 22 must pass before phase 26 signs off |

### JSON-LD structured data by page type

| Page type | schema.org type | Notes |
|---|---|---|
| Any site | `Organization` (or `LocalBusiness`) | On the homepage; name, logo, URL, `sameAs` social links; `LocalBusiness` adds address + hours + geo for local SEO |
| Product / pricing | `Product` + `Offer` | Price, availability, currency; enables price-in-SERP |
| FAQ section | `FAQPage` | One entry per Q/A — pairs with `component-patterns/faq.md`; eligible for FAQ rich results |
| Article / blog post | `Article` / `BlogPosting` | Headline, author, datePublished, image |
| Breadcrumb trail | `BreadcrumbList` | Mirrors the visible breadcrumb component; shows path in SERP |
| Reviews / testimonials | `Review` / `AggregateRating` | Only for genuine, verifiable reviews — never fabricate (Google penalizes fake review markup) |

## 3. The gate

A site is SEO-ready for launch when: every Lighthouse SEO audit passes; `sitemap.xml` + `robots.txt` are valid and reference each other; every page has unique title + meta description + canonical + OG/Twitter tags; JSON-LD is present and validates in the Rich Results Test for each applicable page type; one `<h1>` per page with clean heading order; and phase-22 performance has signed off. Editorial SEO (keyword targeting, content depth, backlinks) is a content/post-launch concern, not part of this mechanical gate.
