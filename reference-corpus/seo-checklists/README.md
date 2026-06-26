# `reference-corpus/seo-checklists/`

> Two Lighthouse-mapped checklists the agent runs the finished site against before launch. Every item maps to a specific **Lighthouse audit id** (the stable anchor that survives Lighthouse version changes — category membership and weights shift, the audit id does not) plus a concrete **fix path**. The agent doesn't just report a score; it walks the list, finds what's failing, and knows exactly what to change.

## What's here

| File | Phase | Lighthouse category | Covers |
|---|---|---|---|
| `performance.md` | **Phase 22 (performance)** | Performance | Core Web Vitals + lab metrics + load opportunities + diagnostics, each with audit id + fix path |
| `seo.md` | **Phase 26 (SEO)** | SEO (+ beyond-Lighthouse essentials) | Crawlability, metadata, structured data, social cards, sitemaps, each with audit id + fix path |

Both are table-driven: `Check | Lighthouse audit id | Why | Target | Fix path`. The `Fix path` column is what makes these actionable — it names the change, not just the failure.

## How the agent uses this dir

- **Phase 22 (performance):** after the site builds, run Lighthouse (or PageSpeed Insights for field data). For every failing or yellow audit, find its row in `performance.md`, apply the fix path, re-run. The Core Web Vitals section is the gating bar — a launch should hit "good" on LCP / INP / CLS in the field, or have a documented reason it can't.
- **Phase 26 (SEO):** walk `seo.md` top to bottom as a pre-launch SEO gate. The Lighthouse SEO category catches the mechanical failures (missing title, blocked crawling, no alt text); the "beyond Lighthouse" section catches what Lighthouse *doesn't* score but search engines and social platforms need (Open Graph tags, XML sitemap, JSON-LD structured data per page type).

These checklists are a floor, not a ceiling — they ensure nothing mechanical is broken. Editorial SEO (keyword intent, content depth, link earning) lives in the content phases, not here.

## Core Web Vitals — current thresholds (the numbers behind the audits)

| Metric | Good | Needs improvement | Poor | Note |
|---|---|---|---|---|
| **LCP** (Largest Contentful Paint) | ≤ 2.5 s | ≤ 4.0 s | > 4.0 s | Loading |
| **INP** (Interaction to Next Paint) | ≤ 200 ms | ≤ 500 ms | > 500 ms | Responsiveness — **replaced FID as a Core Web Vital in March 2024** |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | ≤ 0.25 | > 0.25 | Visual stability |

CWV thresholds are field (real-user) targets. Lighthouse lab runs report *lab* proxies — **TBT** (Total Blocking Time) is the lab stand-in for INP, since a lab run has no real interactions to measure. Optimize the lab proxies; verify against field data (CrUX / PageSpeed Insights) before declaring a Core Web Vital "good."

## Provenance & licensing

Original reference prose written for the website-builder plugin — plugin-owned and freely usable. Audit ids and category structure summarize the **publicly documented Lighthouse** project (Google Chrome, Apache-2.0; referenced, not copied). Core Web Vitals thresholds are from Google's public web.dev / Chrome documentation. Verified against context7 `/googlechrome/lighthouse` on 2026-06-26 (cached at `.claude/temp/ctx7-docs/lighthouse.md` at authoring time; not shipped).

## See also

- `../component-patterns/` — the per-component `## Accessibility requirements` sections cover the a11y audits Lighthouse also scores; this dir is the perf + SEO half.
- `Workstreams/website-builder/foundation/DESIGN-architecture.md` §332 — the spec this dir satisfies.
- Lighthouse audit reference: https://developer.chrome.com/docs/lighthouse/ · Core Web Vitals: https://web.dev/articles/vitals
