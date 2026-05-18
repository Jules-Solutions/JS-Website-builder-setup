# Per-stack phase-18 codegen patterns + context7 manifest + verified-current library notes

> Loaded on demand during phase 18 when the agent writes component code. Canonical sources: the stack adapter docs (`Workstreams/website-builder/stacks/DESIGN-stack-{name}.md`), the per-ecosystem component docs, and `cross-cutting/DESIGN-context7-integration.md`. This reference consolidates the codegen-relevant shape per stack plus the context7 freshness notes verified at authoring (2026-05-18).

## context7 at phase-18 entry — mandatory

Verify the **current** install command, theming-integration shape, primitive-composition pattern, and package name of the chosen library AND the framework *before writing a line*. Training data is stale on all fast-moving libraries here. Resolve→query→cache into `.website-builder/library/docs/{library}.md` (clone-into-project, decision 42); read the local cache first; re-fetch on freshness flag. context7 unreachable = Tier-2 (`.claude/rules/tool-dependency-discipline.md`): surface, WebFetch the canonical docs URL, log the gap — never silently use training data for a named library's API.

### Per-stack context7 library-id manifest (from `cross-cutting/DESIGN-context7-integration.md` + verified 2026-05-18)

| Stack | Primary IDs (phase 18) | Secondary IDs (phase 18) |
|---|---|---|
| Next.js | `/vercel/next.js` | `/tailwindlabs/tailwindcss.com`, `/shadcn-ui/ui` (when shadcn), chosen-CMS id |
| Astro | `/withastro/docs` | `/tailwindlabs/tailwindcss.com`, `/shadcn-ui/ui` |
| Hugo | `/gohugoio/hugo` | `/tailwindlabs/tailwindcss.com` (DaisyUI styling) |
| SvelteKit | `/sveltejs/kit` | `/sveltejs/svelte`, chosen Svelte lib id |
| static-html | `/tailwindlabs/tailwindcss.com` | chosen lib id |
| Framer | `/websites/framer_developers` | `/framer/motion` |
| WordPress | `/wordpress/wp-rest-api` | `/wordpress/block-editor-handbook`, `/woocommerce/woocommerce` (if commerce) |
| Webflow | `/webflow/webflow-api` | — |

Cross-stack: `/stripe/stripe-docs`, `/calcom/cal.com`, `/dequelabs/axe-core`, `/GoogleChrome/lighthouse`.

### Verified-current library notes (2026-05-18 — freshness date of phase contract 18)

- **shadcn/ui** (`/shadcn-ui/ui`, context7-confirmed live): open-code copy-paste (component source lands in the user's repo, not an npm import), **Tailwind CSS v4 + React 19**, semantic CSS-variable theming with **OKLCH** defaults wired via `@theme inline`. `npx shadcn@latest init` then `npx shadcn@latest add <component>`. `components.json` config: `{ style, rsc, tailwind: { config, css, baseColor, cssVariables }, aliases }`. Custom tokens: declare the variable in `:root`/`.dark`, then map via `@theme inline { --color-x: var(--x) }` — exactly the shape phase-17's `brand.yaml.tokens.css` produces. Registry items can ship `cssVars` to add new colors as utility classes.
- **Radix Primitives** (`/radix-ui/primitives`, contract-verified — context7 backend was transiently down at this skill's authoring; phase contract 18 lines 196-207 carry the verbatim verified-current note, freshness 2026-05-18): unstyled accessible React primitives; canonical composition is compound parts (`Dialog.Root → Dialog.Trigger → Dialog.Portal → Dialog.Overlay → Dialog.Content → Dialog.Title/Description/Close`); `Portal` required for correct overlay layering; controlled + uncontrolled both supported; animate via presence + `data-state` attributes (`data-[state=open]`). shadcn wraps these with token-fed defaults — surface Radix directly only for primitives shadcn doesn't expose. **Maintenance drift (WebSearch 2026-05): Radix WorkOS-acquired, update velocity slowed; verify status + the Radix-vs-Base-UI trade-off via context7 at phase entry rather than assuming.**
- **Tailwind v4** (`/tailwindlabs/tailwindcss.com`, contract-verified — same transient context7 outage; contract line 198 carries the verbatim note; the live shadcn pull independently confirms the shape): CSS-first `@theme` directive; OKLCH theme tokens become utility classes *and* CSS variables automatically. Same lookup as phase 17 (re-pull fresh is fine — identical scope: the OKLCH `@theme` token API the components style against).
- **Next.js App Router** (`/vercel/next.js`, context7-confirmed live): `'use client'` directive must be at the file top, before imports — it marks the server/client module-graph boundary; once a file is `'use client'`, all its imports and directly-rendered components join the client bundle (don't re-add the directive to every child). `next/dynamic` with `ssr: false` for client-only. shadcn forms are Client components; pages can be Server components.
- **Payload v3** (`/payloadcms/payload`, context7-confirmed live): Next-native (Payload v3 runs in the same Next.js app, one-line install); **all custom components are React Server Components by default**, enabling the Local API on the front-end; field server-component pattern uses `@payloadcms/ui` base components.
- **Framer Code Components** (`/websites/framer_developers`, context7-confirmed live): `import { addPropertyControls, ControlType } from "framer"`; export the component, set `Component.defaultProps`, then `addPropertyControls(Component, { prop: { type: ControlType.X, title: "..." } })` — props become canvas controls in the properties panel.

Verify-at-entry reminders (naming/version drift): NextUI → **HeroUI** rebrand in flight. Base UI extracted from deprecated `@mui/base`, relaunched standalone — verify package name + maturity. Chakra v2→v3 non-trivial migration. Skeleton UI v2→v3 major rewrite. Don't mix major-version patterns.

## Per-stack codegen shape

### Next.js (App Router — the most flexible MVP stack)

- Server Components by default; `'use client'` only where interactivity (forms, animation, state) is needed. Put the directive at the **file top before imports**; shadcn forms are Client, pages are Server — wrong placement breaks hydration.
- Components: `npx shadcn add <primitive>` lands in `components/ui/`; composite components in `components/{Name}.tsx` import + compose primitives; animation companions in `components/magicui/` (kept namespace-clean). Customized shadcn components copied to `components/custom/` to escape the regenerate path (overwrite-on-`npx shadcn add` risk — note it in `components.yaml`).
- Tokens: `brand.yaml.tokens.css` → `app/globals.css` `:root`/`.dark` OKLCH vars + `@theme inline` mapping; Tailwind utilities reference them. Never hardcode.
- Variants via `class-variance-authority` (ships with shadcn). Forms via React Hook Form + Zod (shadcn `Form`).
- Animation-heavy components: dynamic import + `prefers-reduced-motion` gate + static SSR fallback **at build time here**, so phase 22 doesn't rediscover the perf cost (the phase-17 motion budget pre-allocated this).

### Framer (canvas WYSIWYG + code-extensible runtime)

- The agent ships **Custom (Code) Components**, not whole pages — page composition stays a user activity on the canvas (fighting that fights Framer's value prop). Components in `code/{Name}.tsx`.
- Pattern: export component → `Component.defaultProps` → `addPropertyControls(Component, { prop: { type: ControlType.String|Color|..., title } })`. Push via `framer push` or the Server API code endpoint.
- Tokens: Framer has no first-class spacing tokens — put spacing + motion in `code/tokens.ts` and reference from components; colors → Framer Style tokens via `POST /v1/projects/{id}/styles`. No official Framer MCP; use Bash (curl) against the REST Server API or a small wrapper script.

### WordPress (block themes + custom Gutenberg blocks)

- Ship **block themes (Full Site Editing)** by default; `theme.json` defines tokens (the phase-17 tokens land here). Classic themes only with a strong reason.
- Components = **custom Gutenberg blocks**: `npx @wordpress/create-block <name>` scaffolds; one block per section type, registered via `block.json`, rendered by `render.php` (dynamic/PHP) or `edit.tsx` (React editor view). Blocks plugin at `wp-content/plugins/{slug}-blocks/blocks/{name}/`.
- Content seeded via REST API (`POST /wp-json/wp/v2/pages`); markdown body → Gutenberg block composition. The theme is the contract; everything else is content the user edits in `/wp-admin`.

### Astro (React/Vue/Svelte islands)

- shadcn/Radix/etc. work in islands; components marked `'use client'` or wrapped with `client:load` / `client:visible` directives. Whole-page animation forcing `client:load` on a large island costs performance — surface it.

### Vue (Nuxt / Vite+Vue)

- `.vue` SFCs, Composition API (`<script setup>`), Pinia for non-trivial state. Tokens → the chosen library's theme object (Vuetify `createVuetify` theme, PrimeVue `definePreset(Aura,…)`, Element Plus CSS vars `--el-color-*`). Single-library norm.

### Svelte / SvelteKit

- Svelte 5 runes for new code. Bits UI / shadcn-svelte primitives land in `src/lib/components/ui/`; composites are custom `.svelte` files. Tokens → Tailwind theme + CSS vars (shadcn pattern) or Skeleton's theme generator. Animation via Svelte `transition:` directives by default. Verify CLI/package surface via context7 (Svelte shadcn ecosystem in flux).

### Hugo / static-HTML (non-React Tailwind)

- DaisyUI custom theme in Tailwind config from `brand.yaml` OKLCH (`daisyui.themes` custom object). Raw markup with DaisyUI classes (`<button class="btn btn-primary">`) per the templating language. JS interactivity via Alpine.js / Headless UI (DaisyUI is CSS-only). Run phase 21 a11y aggressively + add ARIA where CSS-only patterns (checkbox-hack modal) fall short.
