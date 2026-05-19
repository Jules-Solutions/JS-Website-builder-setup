# Extraction — Playwright walker

> Real-browser walking of deployed sites. **Paired with Stitch / divmagic when static URL extraction misses dynamic state** — hover effects, scroll-triggered animations, mobile-emulation variants, auth-walled content. **Stack-agnostic** output (screenshots + DOM dumps that feed back into Stitch / AI-output parser). Foundation pack — Playwright MCP is already in the agent's stack.
>
> Anchor: `Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md` §"Playwright walker" (lines 203-210).

## What it does

Drives a real Chromium browser (via Playwright MCP) to:

- Visit deployed URLs
- Walk pages one-by-one per `sitemap.yaml` discovery or user-provided URL list
- Capture per-section screenshots (full-page + per-element)
- Interact with the page: hover states, click handlers, scroll-triggered animations, modal triggers
- Switch viewport sizes (mobile emulation, tablet, desktop) and re-capture
- Handle authentication (user provides creds; Playwright logs in; walks authenticated state)
- Dump the rendered DOM at each viewport for inspection

The output isn't a normalized state directly — Playwright produces **raw artifacts** (screenshots, DOM HTML, network logs, console errors) that **feed into Stitch / divmagic / the AI-output parser** for the actual token + component extraction.

## When the agent invokes it

Playwright walker pairs with the primary extractors. It is **not** typically invoked alone — its purpose is to gather raw artifacts Stitch's URL-only crawl misses:

- **Entry mode `has-existing-site`** when the site has dynamic state Stitch can't see. Triggers:
  - SPA without server-rendered content (Stitch's URL crawl returns empty / skeleton HTML)
  - Hover-revealed UI (dropdowns, tooltips, lightboxes)
  - Scroll-triggered animations / lazy-loaded sections
  - Different mobile vs desktop layouts (responsive design with breakpoint-specific components)
- **Auth-walled sites** — user provides credentials; Playwright authenticates; walks the post-login state. Stitch alone can't reach the authenticated UI.
- **Phase 22 (a11y audit)** + **phase 20 (responsive)** + **phase 29 (deploy verification)** — Playwright walks the live deployed site to verify behavior post-launch. Different purpose (verification vs extraction), same tool.
- **Phase 17 (design system)** — agent uses Playwright to walk user-provided reference URLs across viewports for design comparison.

The pair is: Playwright captures raw artifacts → Stitch / divmagic / AI-output parser extracts tokens/shapes from the captured artifacts. Never standalone except for verification phases.

## Invocation path

Via Playwright MCP (already in foundation pack). The tool surface:

```
mcp__playwright__browser_navigate(url, ...)
mcp__playwright__browser_snapshot(...)
mcp__playwright__browser_take_screenshot(...)
mcp__playwright__browser_resize(width, height)
mcp__playwright__browser_click(selector, ...)
mcp__playwright__browser_hover(selector, ...)
mcp__playwright__browser_fill_form(...)
mcp__playwright__browser_evaluate(js, ...)
```

The agent orchestrates these per the walk plan below.

## Walk plan template

For an extraction walk against `https://example.com`, the agent runs:

```
1. browser_navigate https://example.com
2. browser_snapshot                                  # capture DOM accessibility tree
3. browser_take_screenshot --fullPage                # desktop fullpage screenshot
4. browser_resize 375 667                            # mobile emulation iPhone SE
5. browser_snapshot                                  # capture mobile DOM
6. browser_take_screenshot --fullPage                # mobile fullpage screenshot
7. browser_resize 768 1024                           # tablet emulation
8. browser_snapshot
9. browser_take_screenshot --fullPage
10. browser_resize 1440 900                          # back to desktop
11. For each interactive element identified in step 2:
    - browser_hover {selector} ; browser_snapshot ; browser_take_screenshot
    - (capture hover state artifacts)
12. Scroll-trigger probing:
    - browser_evaluate `window.scrollTo(0, document.body.scrollHeight / 2)`
    - browser_take_screenshot
    - browser_evaluate `window.scrollTo(0, document.body.scrollHeight)`
    - browser_take_screenshot
13. Network + console capture:
    - browser_network_requests   # what loaded
    - browser_console_messages   # any errors
14. For multi-page walks: iterate steps 1-13 for each URL in sitemap.yaml or user-provided list
```

All artifacts saved to `.website-builder/outputs/playwright-{ts}/` with:

```
playwright-2026-05-19T16-30-00Z/
├── walk-plan.md           # the executed walk plan + any deviations
├── pages/
│   ├── home/
│   │   ├── desktop.png
│   │   ├── tablet.png
│   │   ├── mobile.png
│   │   ├── dom-desktop.html
│   │   ├── dom-mobile.html
│   │   ├── hover-states/*.png
│   │   └── network-log.json
│   └── about/
│       └── ...
└── console-errors.log
```

## Auth-walled walks

When the target site requires login:

1. Agent prompts user for credentials: *"this site requires login — can you provide test credentials? I'll use them via Playwright; they're not stored after the session."*
2. User pastes credentials inline (per chat-state — never written to disk).
3. Agent invokes `browser_fill_form` against the login UI; verifies post-login state.
4. Walk proceeds against authenticated routes.
5. Session cleaned up at walk end (`browser_close`).

**Security discipline:** test credentials only. The agent surfaces to user: *"only use test credentials, never production admin creds — Playwright sessions can be observed in transcripts."*

## Pairing — what happens with the artifacts

The Playwright walker's output is **raw**. Other extractors take it from there:

- **Screenshots → Stitch (screenshot mode)** — for design-token extraction from visual capture
- **DOM HTML → AI-output parser** — for component-shape + content extraction from the rendered DOM
- **Hover-state screenshots → component variants** — surfaced at phase 18 for variant inference
- **Mobile + desktop DOMs side-by-side → responsive specs** — surfaced at phase 14 (wireframes) + phase 20 (responsive pass)
- **Console errors → phase 22 (a11y / perf)** — pre-existing issues flagged for the user

Each downstream extractor's output flows back into project state per its own normalization (`extraction/stitch.md`, `extraction/ai-output.md`).

## Configuration

```yaml
# project.yaml
extraction:
  playwright_walker:
    enabled: true   # foundation pack — always available
    default_viewports:
      - { width: 1440, height: 900, name: "desktop" }
      - { width: 768, height: 1024, name: "tablet" }
      - { width: 375, height: 667, name: "mobile" }
    max_pages_per_walk: 20         # safety limit; user can raise per walk
    hover_state_probing: auto       # auto detects interactive elements
    capture_network_log: true
    capture_console: true
```

## Failure modes

| Failure | Cause | Recovery |
|---|---|---|
| `browser_navigate` fails (DNS / 4xx / 5xx) | Site unreachable | Surface error; user verifies URL + connectivity; try with `Accept-Language` header tweak if locale-routed |
| Site blocks Playwright (anti-bot, Cloudflare challenge, etc.) | Bot-detection | Surface trade-off: user can manually accept challenge in the Playwright window, OR provide screenshots they take themselves for the agent to pass to Stitch's screenshot mode |
| Auth fails | Wrong credentials / 2FA required | Surface to user; 2FA-walled sites can't be auto-walked — user provides screenshots from their own session |
| Mobile viewport renders desktop layout | Site doesn't use responsive design | Capture both; flag as "responsive issue" at phase 20 |
| Screenshots truncated (extremely tall page) | Browser memory limit on fullpage | Switch to per-section screenshots; capture viewport-by-viewport scroll |
| Console errors flood | Site has lots of JS errors | Capture all; flag at phase 22 (a11y/perf) as "pre-existing issues" the user owns |
| Walk takes too long (large site) | Many pages × many viewports × many hover states | Reduce viewport count / cap pages per walk; user prioritizes specific routes |
| Captured DOM doesn't reflect what user sees | Server-side rendering vs client hydration mismatch | Wait for `networkidle` before snapshot; flag SSR drift to user |

## Quality discipline

- **Artifacts are reference material, not blueprint copying.** Same discipline as `extraction/divmagic.md`: extract pattern + token values, then re-implement per user's brand.
- **Walks are session-scoped.** Cached at `.website-builder/outputs/playwright-{ts}/` for audit; archived if not used in current ingestion.
- **Auth is ephemeral.** Credentials never persisted. Browser session closed at walk end.
- **Log walks** in `.website-builder/decisions/ingest-{ts}.md` per phase-6.5 schema (`extractor: playwright-walker` paired with whichever downstream extractor processed the artifacts).
- **Verification walks (phases 20 / 22 / 29) are separate** from extraction walks — different artifact destinations, different decision logging.

## See also

- `Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md` §"Playwright walker" — design-doc anchor
- `phase-contracts/06.5-artifact-ingestion.md` — invocation contract
- `extraction/stitch.md` — primary extractor; Playwright feeds Stitch's screenshot mode
- `extraction/ai-output.md` — secondary extractor; Playwright feeds the DOM-dump path
- `extraction/divmagic.md` — element-precision peer (can also use Playwright-captured pages)
- Playwright MCP tools: `mcp__playwright__browser_*` (foundation pack)
- https://playwright.dev — Playwright official docs
