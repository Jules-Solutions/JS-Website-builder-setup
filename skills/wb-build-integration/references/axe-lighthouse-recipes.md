# axe-core + Lighthouse recipes (phases 21-22)

> The automated-audit tooling for the a11y (21) and performance (22) gates. APIs verified current via context7 (`/dequelabs/axe-core`, `/googlechrome/lighthouse-ci`) + WebSearch, 2026-05-18. Always re-verify the current invocation via context7 at phase entry — a11y/perf tooling APIs move.
>
> The cross-phase rule applies: the score is a **signal**, the underlying checks + (for a11y) the manual walk are the **gate**. A high score with a hidden violation is not a pass.

## Part A — axe-core via `@axe-core/playwright` (phase 21 automated pass)

`@axe-core/playwright` is Deque's official Playwright integration. The builder pattern: `new AxeBuilder({ page })`, optionally scoped, then `.analyze()`.

### Full-page scan

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('home — no automatically detectable a11y violations', async ({ page }) => {
  await page.goto('http://localhost:3000/');
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});
```

### Scope to WCAG conformance tags (`withTags`)

axe-core rules carry tags. To gate exactly the conformance level phase 21 targets, scope with the WCAG tags:

```typescript
const results = await new AxeBuilder({ page })
  .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
  .analyze();
```

axe-core WCAG tag map (verified via context7 `/dequelabs/axe-core` API.md):

| Tag | Meaning |
|---|---|
| `wcag2a` | WCAG 2.0 Level A |
| `wcag2aa` | WCAG 2.0 Level AA |
| `wcag21a` | WCAG 2.1 Level A |
| `wcag21aa` | WCAG 2.1 Level AA |
| `wcag22aa` | WCAG 2.2 Level AA |
| `wcag***` | a specific success criterion, e.g. `wcag111` → SC 1.1.1 |
| `best-practice` | common a11y best practices (not a WCAG requirement) |

Phase 21 gates **WCAG 2.1 AA basics** → `['wcag2a','wcag2aa','wcag21a','wcag21aa']`. If the project explicitly targets WCAG 2.2 AA (recommended where the user's jurisdiction expects current conformance — EU EAA / ADA), add `'wcag22aa'`. `best-practice` is reported but not a red-flag gate (it is not a WCAG requirement). The raw axe `axe.run` form takes the same tags via `runOnly: { type: 'tag', values: [...] }`.

### Scope DOM region (`include` / `exclude`)

```typescript
const results = await new AxeBuilder({ page })
  .include('main')
  .exclude('.third-party-widget')
  .analyze();
```

### Interact-then-analyze for state-dependent UI (load-bearing)

axe only sees what's in the DOM at `analyze()` time. Hidden modal/drawer content is invisible to a page-load scan. **Open the state with Playwright, then re-analyze that state:**

```typescript
test('contact modal — a11y', async ({ page }) => {
  await page.goto('http://localhost:3000/');
  await page.getByRole('button', { name: /contact us/i }).click();
  await page.getByRole('dialog').waitFor({ state: 'visible' }); // wait for the state
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .include('[role="dialog"]')
    .analyze();
  expect(results.violations).toEqual([]);
});
```

Run this for every state-dependent surface (nav drawer, accordion, tabs, modal, toast). A page-load-only scan that misses the modal is an incomplete phase-21 automated pass.

### Lighthouse as the alternate automated tool

Lighthouse's accessibility category is a 0-100 aggregate scored from axe-core checks under the hood. `lighthouse <url> --only-categories=accessibility`. Acceptable as the automated pass *only* with the same caveat: the score is a signal; if any underlying check fails it is not a pass regardless of the number, and Lighthouse does not catch keyboard-order at all (the manual walk in `playwright-recipes.md` § 3 is still mandatory).

### MCP-driven form

The website-builder agent runs this via Bash (`npx @axe-core/playwright`-backed runner, or a small project test) against the live dev/preview server, and drives the interact-then-analyze states via the Playwright MCP. Raw axe JSON → `.website-builder/audit/a11y/`. The per-criterion report → `.website-builder/audit/A11Y-REPORT.md`.

## Part B — Lighthouse + Lighthouse CI (phase 22 performance gate)

### The gate

- **Lighthouse performance score ≥ 80** — mobile profile, throttled, **production build** (never the dev server).
- **Core Web Vitals (current thresholds, verified web.dev / corewebvitals.io 2026-05-18):**
  - **LCP < 2.5s** — Largest Contentful Paint (loading)
  - **INP < 200ms** — Interaction to Next Paint (responsiveness; **replaced FID** as a stable CWV in March 2024 — FID retired)
  - **CLS < 0.1** — Cumulative Layout Shift (visual stability)
  - Each assessed at the **75th percentile** of real page views, segmented mobile/desktop. Lighthouse gives **lab** CWV (one synthetic run) — the pre-launch proxy; **field** CWV (real users, 75th pct) is the true target monitored post-launch (phase 30 / the post-launch monitoring template). 43% of sites still fail INP — it is the most commonly failed CWV.

### Lighthouse CLI (one-off)

```bash
# production build first — a dev-build number is meaningless
next build && next start &
npx lighthouse http://localhost:3000/ \
  --only-categories=performance \
  --preset=desktop          # omit --preset for the mobile (gating) profile
  --output=json --output=html \
  --output-path=.website-builder/audit/perf/home
```

Run the **mobile** profile (default, throttled) as the gating run; `--preset=desktop` for the alongside report.

### Lighthouse CI (`lighthouserc` assertion gate — the canonical CI form)

`@lhci/cli` (LHCI 0.15.x / Lighthouse 12.x). The 80+ gate as a blocking assertion (verified via context7 `/googlechrome/lighthouse-ci` configuration.md):

```jsonc
// lighthouserc.json
{
  "ci": {
    "collect": {
      "numberOfRuns": 3,
      "startServerCommand": "next start",        // production server, NOT next dev
      "url": ["http://localhost:3000/", "http://localhost:3000/about", "http://localhost:3000/contact"]
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.8 }],
        "largest-contentful-paint": ["error", { "maxNumericValue": 2500 }],
        "cumulative-layout-shift":  ["error", { "maxNumericValue": 0.1 }],
        "interaction-to-next-paint": ["error", { "maxNumericValue": 200 }]
      }
    }
  }
}
```

Run: `npx @lhci/cli autorun`.

- Assertion levels: `"error"` → non-zero exit (blocking; the phase-22 gate); `"warn"` → stderr only, non-blocking. The phase-22 score/CWV gates are `error`.
- `categories:performance` asserts the category score only (the 80+ gate); the CWV audits (`largest-contentful-paint`, `cumulative-layout-shift`, `interaction-to-next-paint`) are asserted as individual audit `maxNumericValue` properties.
- `preset: "lighthouse:recommended"` plus per-audit overrides is the broader form when the project wants the full recommended assertion set; for the phase-22 gate the explicit four assertions above are the minimum.

### Fix priorities (from Lighthouse's own output)

Lighthouse's "Opportunities" + "Diagnostics" sections name the largest wins. The recurring phase-22 fixes (detail in `phase-procedures.md` § Phase 22): unoptimized hero → responsive variants + AVIF/WebP + explicit dimensions + preload the LCP image; render-blocking font → `font-display` + `preconnect`/`preload` + metrics-matched fallback; heavy JS/animation → dynamic-import + static fallback + code-split. Verify the stack's current image/font/dynamic-import primitives via context7 (`next/image`, `next/font`, `next/dynamic`, Astro `<Image>`) — these evolve.

### Output

Raw Lighthouse JSON/HTML per page (mobile + desktop) → `.website-builder/audit/perf/`. The per-page report (score / LCP / CLS / INP / top opportunities / fixes) → `.website-builder/audit/PERF-REPORT.md`.

## Source freshness

- axe-core API + WCAG tag map: context7 `/dequelabs/axe-core` (API.md, context.md), 2026-05-18.
- `@axe-core/playwright` `AxeBuilder().analyze()`: context7 `/microsoft/playwright` accessibility-testing-js.md, 2026-05-18.
- Lighthouse CI `lighthouserc` assertion config: context7 `/googlechrome/lighthouse-ci` configuration.md, 2026-05-18.
- Core Web Vitals 2026 thresholds + INP-replaced-FID + 75th-pct + 43%-fail-INP: WebSearch web.dev / corewebvitals.io / Google Search Central, 2026-05-18.
