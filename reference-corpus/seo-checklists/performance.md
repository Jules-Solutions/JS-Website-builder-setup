---
type: REFERENCE
corpus: seo-checklists
title: Performance Checklist (Lighthouse-mapped)
checklist_slug: performance
lighthouse_category: performance
consumed_by_phases: [22]
---

# Performance Checklist — Lighthouse-mapped (Phase 22)

> Run Lighthouse (or PageSpeed Insights for field data) against the built site. For every yellow/red audit, find its row, apply the fix path, re-run. Audit ids are the stable anchor — Lighthouse weights and category grouping change between versions; the `id` does not.

## 1. Core Web Vitals + lab metrics (the score drivers)

Lighthouse's Performance score is dominated by these. In current Lighthouse, **LCP, CLS, and TBT carry the highest weight** (confirmed against `/googlechrome/lighthouse` docs) — fix these first.

| Metric | Lighthouse audit id | Lab target | Why it matters | Fix path |
|---|---|---|---|---|
| First Contentful Paint | `first-contentful-paint` | < 1.8 s | First pixel of content; perceived start | Reduce render-blocking CSS/JS; inline critical CSS; cut server response time |
| Largest Contentful Paint | `largest-contentful-paint` | < 2.5 s | Main content loaded (a CWV) | Optimize/preload the LCP image; serve modern formats; remove render-blockers above it; `fetchpriority="high"` on the hero image |
| Total Blocking Time | `total-blocking-time` | < 200 ms | Lab proxy for **INP** (responsiveness) | Split long tasks; defer/remove non-critical JS; reduce third-party scripts; code-split |
| Cumulative Layout Shift | `cumulative-layout-shift` | < 0.1 | Visual stability (a CWV) | Set explicit `width`/`height` (or `aspect-ratio`) on all media; reserve space for ads/embeds; preload fonts + `font-display: optional/swap` to avoid FOUT shift |
| Speed Index | `speed-index` | < 3.4 s | How quickly content visually populates | Same levers as FCP/LCP; reduce above-the-fold work |
| Time to Interactive | `interactive` | < 3.8 s | When the page reliably responds | Reduce main-thread JS; defer hydration; trim bundles |

> INP itself is a field metric (no lab equivalent) — verify it in PageSpeed Insights / CrUX, not in a lab Lighthouse run. TBT is the lab signal you optimize to move it.

## 2. Opportunities (load-time wins Lighthouse quantifies in seconds saved)

| Check | Lighthouse audit id | Fix path |
|---|---|---|
| No render-blocking CSS/JS in `<head>` | `render-blocking-resources` | Inline critical CSS; `defer`/`async` scripts; move non-critical CSS to `media`/preload-swap |
| Ship only used JavaScript | `unused-javascript` | Code-split by route; tree-shake; drop unused libraries; dynamic-import below-the-fold widgets |
| Ship only used CSS | `unused-css-rules` | Purge unused selectors (Tailwind JIT does this); split per-route CSS |
| Serve images in modern formats | `modern-image-formats` | WebP/AVIF with fallback; use the stack's image pipeline (Next/Astro `<Image>`, etc.) |
| Compress / right-size images | `uses-optimized-images` | Recompress; strip metadata; quality 75-85 for photos |
| Serve responsively-sized images | `uses-responsive-images` | `srcset` + `sizes`; never ship a 2000px image into a 400px slot |
| Defer offscreen images | `offscreen-images` | `loading="lazy"` on below-the-fold images (never on the LCP image) |
| Preload the LCP image | `prioritize-lcp-image` | `<link rel="preload" as="image">` + `fetchpriority="high"` on the hero |
| Enable text compression | `uses-text-compression` | Gzip/Brotli on HTML/CSS/JS at the host/CDN (Vercel/Netlify/Cloudflare do this by default) |
| Preconnect to required origins | `uses-rel-preconnect` | `<link rel="preconnect">` for fonts/CDN/API origins used early |
| Fast server response | `server-response-time` | CDN/edge caching; static-generate (SSG/ISR) instead of per-request SSR where possible |
| Avoid multiple redirects | `redirects` | Link directly to the final URL; collapse www/non-www + http/https chains to one hop |
| Efficient animated content | `efficient-animated-content` | Replace animated GIFs with `<video>` (MP4/WebM) |
| Avoid legacy/duplicated JS | `legacy-javascript`, `duplicated-javascript` | Target modern browsers in the build; dedupe bundled deps |

## 3. Diagnostics (structural health — not always scored, always worth fixing)

| Check | Lighthouse audit id | Fix path |
|---|---|---|
| Reasonable total page weight | `total-byte-weight` | Budget the page; the biggest wins are images + fonts + JS |
| Small, shallow DOM | `dom-size` | Avoid thousand-node pages; paginate/virtualize long lists |
| Low JS execution cost | `bootup-time`, `mainthread-work-breakdown` | Less JS, split tasks, defer non-critical work |
| Minimal third-party impact | `third-party-summary` | Audit every embed/pixel/widget; lazy-load or remove; self-host fonts |
| Fonts render without blocking | `font-display` | `font-display: swap` (or `optional`); preload the primary font; subset to used glyphs |
| Long cache lifetimes on static assets | `uses-long-cache-ttl` | Far-future `Cache-Control` + content hashing on static assets (host default on Vercel/Netlify) |

## 4. Stack-aware fix notes (website-builder defaults)

- **Astro / Hugo / static-html** — already near-zero JS; the dominant levers are image optimization + font loading + CDN caching. Use the stack's built-in image component.
- **Next.js** — use `next/image` (handles responsive + modern formats + lazy), `next/font` (eliminates font-shift), and prefer SSG/ISR over SSR for `server-response-time`.
- **SvelteKit** — prerender static routes; `enhanced:img`; code-split per route.
- **WordPress / Webflow / Framer** — perf is partly host-controlled; the agent's levers are image discipline, plugin/embed minimization, and caching config.

## 5. The gate

A site is performance-ready for launch when, on **field** data (PageSpeed Insights / CrUX), **LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1** — or there is a documented, accepted reason it can't (e.g., a required heavy third-party embed). Lab Lighthouse green is necessary but not sufficient; the field is the truth.
