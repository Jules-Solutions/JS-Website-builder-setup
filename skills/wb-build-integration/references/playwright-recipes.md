# Playwright MCP recipes (phases 19-23)

> Concrete Playwright patterns this phase group depends on. The website-builder agent drives the **Playwright MCP** (`mcp__playwright__browser_*`) interactively, not a `@playwright/test` file — but the API shapes below (verified current via context7 `/microsoft/playwright`, 2026-05-18) are the same primitives the MCP exposes. Where a stack test harness exists, the `@playwright/test` form is also given so the agent can write a committed test if the project wants one.
>
> The cross-phase rule: **the snapshot/aria record is the exit criterion, not the agent's claim.** Produce the artifact.

## 1. Viewport resize + screenshot per breakpoint (phase 20)

The phase-20 record is `.website-builder/audit/responsive/{slug}-{360,768,1280}.png` per page. With the Playwright MCP: `browser_resize` to each width, `browser_navigate` to the page, `browser_take_screenshot` to the audit path. Mobile-first order: 360 → 768 → 1280.

The three reference breakpoints (per the phase-20 contract): **~360px phone, ~768px tablet, ~1280px desktop.**

`@playwright/test` equivalent (committed-test form):

```typescript
import { test, expect } from '@playwright/test';

const BREAKPOINTS = [
  { name: '360', width: 360, height: 740 },   // phone
  { name: '768', width: 768, height: 1024 },  // tablet
  { name: '1280', width: 1280, height: 800 }, // desktop
];

for (const bp of BREAKPOINTS) {
  test(`home @ ${bp.name}`, async ({ page }) => {
    await page.setViewportSize({ width: bp.width, height: bp.height });
    await page.goto('http://localhost:3000/');
    await page.screenshot({
      path: `.website-builder/audit/responsive/home-${bp.name}.png`,
      fullPage: true,
    });
  });
}
```

For a whole test file at one viewport, `test.use({ viewport: { width, height } })` (file- or describe-scoped) is the documented pattern. For true mobile emulation (touch + device pixel ratio + UA), a context with `setViewportSize` + `deviceScaleFactor` + `hasTouch: true` + `isMobile: true` — used when a layout genuinely depends on touch/mobile UA, not just width.

## 2. Interact-then-snapshot for state-dependent layout (phase 20)

When the layout depends on UI state — the mobile nav drawer, an open accordion, a revealed section — **interact before snapshotting** or the snapshot records the wrong state.

```typescript
test('mobile nav drawer @ 360', async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 740 });
  await page.goto('http://localhost:3000/');
  // open the drawer FIRST — the responsive record must show it open
  await page.getByRole('button', { name: /menu/i }).click();
  await page.getByRole('navigation').waitFor({ state: 'visible' });
  await page.screenshot({ path: '.website-builder/audit/responsive/home-360-navopen.png' });
});
```

MCP form: `browser_resize` → `browser_navigate` → `browser_click` the menu trigger → `browser_wait_for` the nav visible → `browser_take_screenshot`.

## 3. Keyboard tab-walk (phase 21 — the manual pass)

Automated axe catches ~30-50% of issues. The manual keyboard walk catches keyboard order, focus management, traps. Tab through every page; at each stop verify a visible focus indicator and that the tab order is logical; operate + escape every modal/menu by keyboard.

```typescript
test('keyboard walk — home', async ({ page }) => {
  await page.goto('http://localhost:3000/');
  const stops: string[] = [];
  for (let i = 0; i < 40; i++) {
    await page.keyboard.press('Tab');
    const focused = await page.evaluate(() => {
      const el = document.activeElement as HTMLElement | null;
      if (!el || el === document.body) return null;
      return `${el.tagName}${el.id ? '#' + el.id : ''} "${(el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 40)}"`;
    });
    if (focused) stops.push(focused);
  }
  // assert: every interactive element is reachable, order is logical,
  // and focus never lands nowhere (a trap or a skipped control)
  expect(stops.length).toBeGreaterThan(0);
});
```

Modal/drawer check: open it (click), Tab inside, confirm focus is contained while open and returns to the trigger on `Escape` (no trap, focus restored). MCP form: `browser_press_key("Tab")` repeatedly + `browser_evaluate` to read `document.activeElement` + `browser_snapshot` to confirm the focus ring is visible at each stop.

## 4. Accessibility-tree capture — the screen-reader sniff test (phase 21)

`locator.ariaSnapshot()` (Playwright v1.49+) serializes the accessibility tree as structured YAML — the structure a screen reader announces. Confirm: one `heading` at the top level (the h1), logical heading nesting, landmarks present, link text meaningful (no bare "click here"), image alts read sensibly.

```typescript
test('aria sniff — home', async ({ page }) => {
  await page.goto('http://localhost:3000/');
  const tree = await page.locator('body').ariaSnapshot();
  // tree is YAML like:
  //   - banner:
  //     - navigation "Main": ...
  //   - main:
  //     - heading "Welcome to Acme" [level=1]
  //   - contentinfo: ...
  // Read it: one h1, no skipped levels, landmarks present, link text not "click here"
  console.log(tree);
});
```

Or assert an expected shape directly with `toMatchAriaSnapshot`:

```typescript
await expect(page.locator('main')).toMatchAriaSnapshot(`
  - heading "Welcome to Acme" [level=1]
  - paragraph
  - link "Get started"
`);
```

MCP form: `browser_snapshot` returns the accessibility-tree snapshot the agent reads for the sniff test.

## 5. Form fill + submit + effect verification (phase 23)

The phase-23 exit is the **verified effect**, not "submitted without error." Playwright fills + submits with test data; then verify the effect.

```typescript
test('contact form submits and the effect is verified', async ({ page, request }) => {
  await page.goto('http://localhost:3000/contact');
  await page.getByLabel('Name').fill('Test Visitor');
  await page.getByLabel('Email').fill('wb-test@example.com');
  await page.getByLabel('Message').fill('Phase 23 end-to-end verification.');
  await page.getByRole('button', { name: /send/i }).click();

  // 1. the success STATE shows (necessary, not sufficient)
  await expect(page.getByText(/thanks|we'll be in touch|message sent/i)).toBeVisible();

  // 2. the EFFECT is verified — pick the path that fits the endpoint:
  //  a) web-visible effect (a success page, a list that shows the new entry) → assert it in the browser
  //  b) provider API queryable → Bash/`request` to the provider to confirm the test message landed
  //  c) only the user can see the inbox → AskUserQuestion: "Did the test email arrive at <inbox>? (yes/no)"
});
```

Honeypot + challenge note: the test submission must pass the honeypot (leave the honeypot field empty) and, where a challenge (Turnstile) is wired, use the provider's test/sitekey so the automated submission can complete — and the server-side token verification still runs (never bypass it in the test; verify it accepts the test token and rejects a forged one).

MCP form: `browser_navigate` → `browser_fill_form` (or per-field `browser_type`) → `browser_click` submit → `browser_wait_for` the success text → then the effect-verification path (browser assertion / Bash provider query / `AskUserQuestion`).

## 6. Robust accessibility-violation snapshots (phase 21, optional)

When committing an a11y regression test, snapshot a *fingerprint* (rule id + target selectors) not the full violations array — far less fragile to irrelevant HTML changes:

```typescript
function violationFingerprints(results) {
  return JSON.stringify(
    results.violations.map(v => ({ rule: v.id, targets: v.nodes.map(n => n.target) })),
    null, 2);
}
expect(violationFingerprints(accessibilityScanResults)).toMatchSnapshot();
```

## Notes

- The website-builder runs against the **live dev/preview server** for phases 20-21 and the **production build** for phase 22 (see `axe-lighthouse-recipes.md` — a dev-build Lighthouse number is meaningless).
- Playwright works across Chromium / Firefox / WebKit; the phase-27 cross-browser QA extends these same snapshots — phases 20-23 establish the baseline.
- Source freshness: Playwright API patterns verified via context7 `/microsoft/playwright`, 2026-05-18 (`test.use` viewport, `setViewportSize`, mobile context emulation, `@axe-core/playwright` `AxeBuilder().analyze()`, `ariaSnapshot`/`toMatchAriaSnapshot`, violation-fingerprint pattern).
