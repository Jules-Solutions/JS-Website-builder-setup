# tests/adapters/nextjs/ — Next.js + shadcn adapter fixture

> Adapter under test: `adapters/stack-nextjs.md` (Phase 3 Captain G's authored adapter).
>
> Verifies the adapter's per-phase output against the canonical `expected.yaml` contract authored alongside this fixture. Per `tests/adapters/README.md`, the **test runner integration is Phase 5+ scope** — for Phase 3, this fixture supports **manual walk-through verification** (mentally trace the adapter through phases 11→27 against the fixture state, confirm the adapter file would produce what `expected.yaml` claims).

## What this fixture verifies

The fixture is a minimal-but-realistic `.website-builder/` project state at the **phase-11-complete** point in the pipeline. It exercises the Next.js + shadcn adapter's:

1. **Content layer mapping** (§4 of `adapters/stack-nextjs.md`) — `brand.yaml` → `app/globals.css` OKLCH + `@theme inline`; `sitemap.yaml` → `app/[lang]/{slug}/page.tsx`; `strings/{lang}.json` → `messages/{lang}.json` (next-intl); `content/pages/{lang}/{slug}.md` → `content/pages/{lang}/{slug}.mdx`; `components.yaml` → `components/{Name}.tsx`.
2. **i18n integration** (§5) — multilingual (en + de) project with prefix routing, default-language `en`, hreflang map across both locales + `x-default`, language switcher generated as Client Component (2 locales → inline variant per `i18n/language-switcher.md#next-js--shadcn`).
3. **Migration recipe** (§3) — `.website-builder/` → Next.js project structure per the table in §3.
4. **CMS pairing** (§8) — fixture's `transactional: false` + `5 pages` should route to `cms: none` (file-based MDX) as the recommendation; the adapter must surface Decap + Payload as alternatives but default to `none` per §"CMS pairing" Default-for-muggle logic.
5. **Component library pairing** (§9) — `HeroBlock` + `NavBar` + `FooterBlock` exercise shadcn primitive composition (`Button`, `Card`, `DropdownMenu` for the language switcher); fixture has `component_library: shadcn-ui` set in `project.yaml`.
6. **Deploy** (§10) — fixture's `host: vercel` + `transactional: false` exercises the basic Vercel-deploy path (Hobby tier; no Stripe wiring needed); `expected.yaml` documents the expected SSL + DNS handoff state.

## Setup the test runner would need

For Phase 3 manual verification: no setup beyond reading the fixture files alongside the adapter. For Phase 5+ automated runner:

- **Vercel CLI** (`pnpm add -g vercel`) if the runner exercises the actual deploy path (preview deploy → walk → teardown).
- **`pnpm` + Node 20+** for any `pnpm install` / `pnpm build` simulation.
- **Playwright** (already in the foundation pack) for the language-switcher + hreflang verification walk.
- **`curl`** + standard POSIX tools for hreflang extraction from rendered HTML.

The fixture itself is fully synthetic — no real brand, no real client data, no real API keys required.

## Per-Next.js-stack gotchas the fixture does NOT cover

The fixture is minimal by design. Known platform gotchas documented in `adapters/stack-nextjs.md` §"Limitations + escape hatches" → `### Failure modes` that are out of scope for this fixture:

- **Next.js 15 `fetch` no-store default** — the adapter file covers it (it's the canonical Lock-3 example); the fixture doesn't exercise data-fetching code (no Route Handlers, no `fetch()` calls).
- **Hydration mismatches** — the fixture has no `Date.now()` / `Math.random()` / browser-API-in-Server-Component patterns; not exercised.
- **Stripe webhook signature verification** — `transactional: false` fixture; commerce path not exercised. A separate `tests/adapters/nextjs-transactional/` fixture (future INST) would cover this.
- **Payload-specific deploy gate (`pnpm payload migrate && next build`)** — `cms: none` fixture; Payload path not exercised. A future `tests/adapters/nextjs-payload/` fixture would cover this.
- **Static export (`output: 'export'`) mode** — fixture uses default Vercel SSR/SSG; static-export trade-offs documented in adapter §"Limitations" → "Escape hatches" but not exercised here.
- **RTL languages** — fixture is en + de only; both LTR. A future `tests/adapters/nextjs-rtl/` fixture would exercise the `dir="rtl"` + Tailwind `rtl:` variants + Playwright RTL walk.

These extensions are deferred Phase 5+ test-fixture INSTs per `BUILD-strategy.md`.

## How to update this fixture when the adapter contract evolves

When `adapters/stack-nextjs.md` changes in ways that affect the fixture's behavior:

1. **Update `expected.yaml`** — the per-phase expected output. The fixture's `project.yaml` + `brand.yaml` + `sitemap.yaml` etc. typically stay stable; what evolves is what the adapter SHOULD produce from them.
2. **If the schema in `adapters/README.md` changes** (e.g., a new H2 section added, a row added to the Content layer mapping table), update `expected.yaml` to assert the new schema-required output is present.
3. **If a Next.js / shadcn / next-intl breaking change drops** (per the Lock-3 freshness pattern), update the adapter file first, then update `expected.yaml` to reflect the new expected codegen patterns. Re-fetch context7 + cross-cite the freshness date in both the adapter file's §"context7 lookups for this stack" and this README.
4. **Commit with a pathspec-scoped change** — never bulk-edit fixture + adapter in one commit; they're independent contracts.

## File map

```
tests/adapters/nextjs/
├── README.md                        # this file
├── expected.yaml                    # per-phase expected adapter output
└── fixture/
    ├── project.yaml                 # stack=nextjs, transactional=false, en+de, vercel host
    ├── brand.yaml                   # 4 OKLCH colors, type scale (h1/h2/body), spacing/motion
    ├── sitemap.yaml                 # 5 pages: home, about, services, contact, blog
    ├── components.yaml              # 3 components: HeroBlock, NavBar, FooterBlock
    └── content/
        ├── pages/
        │   ├── en/
        │   │   ├── home.md
        │   │   └── about.md
        │   └── de/
        │       ├── home.md
        │       └── about.md
        └── strings/
            ├── en.json
            └── de.json
```

## Cross-references

- `tests/adapters/README.md` — the per-adapter test fixture convention this directory implements
- `adapters/stack-nextjs.md` — the adapter file under test
- `adapters/README.md` — the 14-section schema both must satisfy
- `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` — `.website-builder/` layout the fixture mirrors
- `Workstreams/website-builder/foundation/DESIGN-content-layers.md` — the 5-layer structure the fixture must contain
- `Workstreams/website-builder/BUILD-strategy.md` Phase 3 DoD line 179 — "Each adapter passes adapter-specific test fixtures"
