# Ecosystem Catalog

> The website-builder's curated, self-contained catalogue of the tools, libraries, platforms, and inspiration sources the agent surfaces across the build pipeline. Muggles don't know what's out there; Claude alone doesn't reliably know either. **This catalogue ships with the plugin** and teaches both. It is also the launching point for the user to grow their own project-local resource library at `.website-builder/library/` as the project progresses.
>
> **Authoring provenance:** this is the shipped distillation of the website-builder workstream's design docs (`DESIGN-ecosystem-catalog.md` + `DESIGN-templates-catalog.md`), which remain the authoring SSOT. This file is synced from them per the catalogue-update workflow in `DESIGN-resource-curation.md`; when the SSOT changes, this distillation is re-synced. Do not treat this as the SSOT — it is the shipped menu.

## How to read this catalogue

Every entry carries a **surfacing tag** telling the agent how the resource reaches the project:

| Tag | Meaning |
|---|---|
| `bundled` | Ships inside the plugin at `${CLAUDE_PLUGIN_ROOT}/reference-corpus/<dir>/`. The orchestration spine auto-clones it into `.website-builder/library/<dir>/` at phase entry (a local copy — no network), where the agent reads it. Always present on any install. |
| `clone-into-project` | A local copy is installed into `.website-builder/library/` at session-start or phase trigger when it is load-bearing for the current phase (via `wb library` / auto-clone). Used for docs queried repeatedly during a phase. |
| `fetch-on-demand` | The agent reaches it via WebFetch / context7 / HTTP API / MCP at the moment of need. Used for large/changing docs, rare lookups, big registries, and inspiration surfaces. |

**Principle — ship the menu, fetch the meals.** The curated menu (this catalogue) + the bundled reference corpora ship with the plugin. Heavy, fast-changing docs (Next.js, Tailwind, Stripe) stay `fetch-on-demand`. The user's `.website-builder/library/` grows organically around what their project actually needed.

---

## Bundled reference corpora

These ship inside the plugin at `${CLAUDE_PLUGIN_ROOT}/reference-corpus/<dir>/`. At phase entry the orchestration spine auto-clones the relevant corpus into `.website-builder/library/<dir>/` (a local copy — no network), where the agent reads it. They are guaranteed present on any install (no vault, no network required).

| Corpus | Path | Surfacing | Consumed at | What it is |
|---|---|---|---|---|
| **Design systems** | `reference-corpus/design-systems/` | `bundled` | Phase 17 (2/5/18 sample) | 5 reference docs on mature design systems (Material 3, Apple HIG, IBM Carbon, Tailwind, Radix/shadcn): tokens + principles + when-to-use |
| **Brand examples** | `reference-corpus/brand-examples/` | `bundled` | Phase 2, 13-16 | 7 complete original brand systems (voice + OKLCH tokens + component patterns) across distinct archetypes |
| **Awesome-design-md corpus** | `reference-corpus/awesome-design-md-corpus/` | `bundled` | Phase 17 (2/13 sample) | Curated 14-exemplar subset of `DESIGN.md`-style brand specs (format from MIT-licensed VoltAgent/awesome-design-md) |
| **Voice archetypes** | `reference-corpus/voice-archetypes/` | `bundled` | Phase 5, 6, 16 | 8 reference voices across the verbal-identity spectrum, grounded in NN4D + Aaker + Jung; attributes, say/never-say, sample copy |
| **Component patterns** | `reference-corpus/component-patterns/` | `bundled` | Phase 18 (9/13/15/16/21 sample) | Canonical specs for the 20 most common component types (purpose + anatomy + slots + a11y + variants) |
| **SEO checklists** | `reference-corpus/seo-checklists/` | `bundled` | Phase 22, 26 | Lighthouse-mapped performance + SEO checklists, each item → audit id → fix path |

> The full VoltAgent corpus (60+ exemplars) is available `clone-into-project` at phase 17 via the `awesome-design-md` key when the bundled 14-exemplar subset is not enough.

---

## Design-system / artifact-extraction tools

Extract a design system or specific elements from an existing URL / Figma file / screenshot into a portable spec the agent ingests.

| Tool | URL | Cost | Surfacing | When |
|---|---|---|---|---|
| **Google Stitch** | https://stitch.withgoogle.com | Free | `fetch-on-demand` | Primary extractor — any URL → portable DESIGN.md. Phase 6.5 (has-existing-site), phase 17 seeding |
| **divmagic** | https://divmagic.com | Freemium | `fetch-on-demand` | Element-precision extraction via HTTP API. Phase 6.5, 17, 18 |
| **Figma design-to-json** | https://www.figma.com/community/plugin/1514601930647701205/design-to-json | Free | `fetch-on-demand` | Export Figma files → structured JSON. Phase 6.5 (has-figma-file), 17 |
| **Peel Studio** | https://peel.studio | Commercial | `fetch-on-demand` | Drag-and-drop screenshot extraction |
| **Codia VisualStruct** | https://codia.ai/visual-struct | Commercial API | `fetch-on-demand` | Computer-vision UI-hierarchy extraction |
| **Tailwind Theme Maker** | https://tailwindthememaker.com | Free | `fetch-on-demand` | Logo/screenshot → palette → Tailwind config |
| **Design Extract / Designstyles.xyz** | https://designstyles.xyz | Pay-per-request | `fetch-on-demand` | Firecrawl-based extraction → Tailwind config |

---

## Design-skill flavors

User-pickable design-skill flavors (onboarding walks the user through picking a primary + complementary). Composition manifests live in the plugin's `skills-bundle/`.

| Skill | URL | Cost | Surfacing | When |
|---|---|---|---|---|
| **UI/UX Pro Max** (default) | `ui-ux-pro-max` skill / public registry | Free | `clone-into-project` if picked | Most comprehensive (50+ styles, 161 palettes, 57 fonts). Phase 17 primary, 18 secondary |
| **Impeccable** | https://impeccable.style | Free | `clone-into-project` if picked | Brand-vs-Product split; 23 commands + 25 anti-patterns. Phase 17/18 when site has both marketing + app UI |
| **Emil Kowalski's skill** | https://emilkowal.ski/skill | Free | `clone-into-project` if picked | Animation + design-engineering focus. Phase 17 (motion), 18, 22 |
| **Taste Skill** | https://tasteskill.dev | Free | `clone-into-project` if picked | 4 aesthetic variants (taste/soft/minimalist/brutalist). Phase 17/18 |
| **21st.dev Magic** | https://21st.dev | Free + paid | `fetch-on-demand` | Agent-UX components (chat, prompt boxes). Phase 18 when site has agent-driven features |
| **Framer Motion skill** | https://motion.dev/docs/ai-kit | Free | `clone-into-project` if Emil picked + React stack | React animation education. Phase 18 animation-heavy components |

---

## Component libraries

Tier list driven by muggle-friendliness × stack diversity. The agent surfaces the relevant subset at phase 18 (component build) per the chosen stack. Chosen library docs are `clone-into-project`; unpicked libraries stay `fetch-on-demand` while the user evaluates.

### S-tier (most muggle-friendly + widely adopted)

| Library | Stack | URL | Why S-tier |
|---|---|---|---|
| **shadcn/ui** | React + Tailwind | https://ui.shadcn.com | Copy-paste; user owns the code; AI-aware docs; massively adopted |
| **DaisyUI** | HTML/CSS + Tailwind | https://daisyui.com | Pure CSS plugin; no JS; 35 themes; muggle-friendliest |
| **Radix Primitives** | React (headless) | https://www.radix-ui.com | 28+ accessible unstyled headless components |

### A-tier (professional, full-featured)

| Library | Stack | URL |
|---|---|---|
| **Mantine** | React | https://mantine.dev |
| **Aceternity UI** | React + Framer Motion | https://ui.aceternity.com |
| **Magic UI** | React + Framer | https://magicui.design |
| **Once UI** | React/Next.js | https://once-ui.com |

### B-tier (niche / specific use cases)

| Library | Stack | URL |
|---|---|---|
| **Chakra UI** | React | https://chakra-ui.com |
| **Park UI** | React/Vue/Solid | https://park-ui.com |
| **NextUI / HeroUI** | React | https://nextui.org |
| **Headless UI** | React + Tailwind | https://headlessui.com |
| **Base UI** | React | https://base-ui.com |

### Enterprise / dense-data

| Library | Stack | URL |
|---|---|---|
| **Material UI (MUI)** | React | https://mui.com |
| **Ant Design** | React | https://ant.design |
| **Tailwind UI** | HTML / React / Vue | https://tailwindui.com |

### Vue ecosystem

| Library | URL | Note |
|---|---|---|
| **PrimeVue** | https://primevue.org | Comprehensive components |
| **Vuetify** | https://vuetifyjs.com | Material Design for Vue |
| **Element Plus** | https://element-plus.org | Desktop-focused enterprise |
| **Quasar** | https://quasar.dev | Straddles library + framework; no dedicated stack adapter (decision 47) — Vue users routed to Vuetify/PrimeVue + Vite |

### Svelte ecosystem

| Library | URL |
|---|---|
| **Skeleton UI** | https://www.skeleton.dev |
| **Melt UI** | https://melt-ui.com |
| **Bits UI** | https://bits-ui.com |

---

## CMS

Each CMS is a complete adapter (`cms-adapters/<name>.md`) covering block + collection authoring + pitfalls + per-stack integration. Chosen CMS docs are `clone-into-project`.

| CMS | URL | Use when | Adapter |
|---|---|---|---|
| **Payload** | https://payloadcms.com | Node/Next backend; git-versioned schema-as-code (TypeScript-first) | `cms-adapters/cms-payload.md` |
| **Decap CMS** | https://decapcms.org | Static stacks; plain markdown in git; muggle-friendliest | `cms-adapters/cms-decap.md` |
| **Strapi** | https://strapi.io | Wants admin UI, no TypeScript | `cms-adapters/cms-strapi.md` |
| **Sanity** | https://sanity.io | Heavy content + cross-page references; team workflows | `cms-adapters/cms-sanity.md` |
| **TinaCMS** | https://tina.io | Static stacks + visual editing of markdown | `cms-adapters/cms-tinacms.md` |
| **Directus** | https://directus.io | Existing SQL database to expose | `cms-adapters/cms-directus.md` |
| **Keystone** | https://keystonejs.com | TypeScript-heavy teams wanting a lighter Payload | `cms-adapters/cms-keystone.md` |
| **Ghost** | https://ghost.org | Newsletter + blog combinations | `cms-adapters/cms-ghost.md` |
| **(none)** | — | Static brochure sites; file-based markdown | `cms-adapters/cms-none.md` |

---

## Commerce platforms

Each is a complete adapter (`commerce-adapters/<name>.md`). Chosen platform docs are `clone-into-project` through the commerce phases.

| Platform | URL | Cost | Use when | Adapter |
|---|---|---|---|---|
| **Shopify** | https://shopify.com | $29-299/mo + 2.9%+30¢ | Mass-market storefronts; physical/hybrid products | `commerce-adapters/commerce-shopify.md` |
| **Lemon Squeezy** | https://lemonsqueezy.com | 5%+50¢ + 1.5% intl | Digital products / SaaS; EU-friendly MoR (VAT/GST handled) | `commerce-adapters/commerce-lemonsqueezy.md` |
| **Stripe Checkout / Payment Links** | https://stripe.com/payments/checkout | 2.9%+30¢ US; 1.5%+local EU | Payment-only flows; single product/service | `commerce-adapters/commerce-stripe.md` |
| **Snipcart** | https://snipcart.com | 2% + $10-20/mo | Drop-in cart for static sites | `commerce-adapters/commerce-snipcart.md` |
| **Paddle** | https://paddle.com | 5%+50¢ all-in | B2B/SaaS subscription billing | `commerce-adapters/commerce-paddle.md` |
| **Gumroad** | https://gumroad.com | 10%+50¢ direct | Creator economy; one-product launches | `commerce-adapters/commerce-gumroad.md` |
| **Sellfy** | https://sellfy.com | $19-299/mo + processing | Multi-channel digital + physical hybrid | `commerce-adapters/commerce-sellfy.md` |
| **Saleor** | https://saleor.io | Free self-hosted or SaaS | Open-source headless commerce; full control | `commerce-adapters/commerce-saleor.md` |
| **WooCommerce** | https://woocommerce.com | Free plugin + processing | WordPress already chosen | `commerce-adapters/commerce-woocommerce.md` |
| **Shopify Hydrogen** | https://hydrogen.shopify.dev | Same as Shopify | Headless React storefront on Shopify | `commerce-adapters/commerce-hydrogen.md` |

---

## Payment providers

The agent selects via a decision tree (shipped in `commerce-adapters/payment-providers.md`). Providers are `fetch-on-demand` (chosen provider's API docs go `clone-into-project` at phase 24b).

| Provider | URL | Cost | Best for |
|---|---|---|---|
| **Stripe** | https://stripe.com | 2.9%+30¢ US; 1.5%+local EU | Global default; 40+ countries |
| **Mollie** | https://mollie.com | 1.8-2.9%+€0.25 EU | EU-heavy; iDeal/SEPA; strong Benelux/Nordics |
| **PayPal** | https://paypal.com | 3.49%+$0.49 | Legacy brand-trust; better US/UK conversion |
| **TWINT** | https://www.twint.ch | Per acquirer | Switzerland (3.5M+ users; native via Stripe; CHF-only) |
| **Square** | https://squareup.com | 2.9%+30¢ | US-heavy; in-person + online (POS) |
| **Klarna** | https://klarna.com | Per region | BNPL EU + US; higher AOV |

**Decision tree:**

```
IF user country in [US, UK, EU, AU, CA, SG, JP] → Stripe (primary)
ELSE IF user in [NL, BE, DE, AT, CH]            → offer Mollie alongside Stripe
ELSE IF Switzerland                             → Stripe + TWINT native
ELSE IF legacy/aged audience                    → offer PayPal alongside Stripe
ELSE                                            → Stripe (broadest fallback)
```

---

## Booking platforms

| Platform | URL | Cost | Best for |
|---|---|---|---|
| **Cal.com** | https://cal.com | Free self-hosted; $99/mo SaaS | Open-source; data ownership; 70+ integrations; Stripe/PayPal collection |
| **Calendly** | https://calendly.com | Free basic; $10-20/mo pro | "Just works" simplicity; 100+ integrations |
| **SimplyBook.me** | https://simplybook.me | Tiered SaaS | Multi-service businesses |

---

## Stack adapters

Each stack has a complete authoring + integration recipe at `adapters/stack-<name>.md`. The 8-stack set is locked (decision 47).

| Stack | Hosting | Strengths | Adapter |
|---|---|---|---|
| **Framer** | Framer Hosting | Visual canvas + custom React + CMS; Server API | `adapters/stack-framer.md` |
| **WordPress** | self-host or .com | Massive ecosystem; mature plugins; admin UI | `adapters/stack-wordpress.md` |
| **Webflow** | Webflow Cloud | Designer-friendly; mature CMS Data API | `adapters/stack-webflow.md` |
| **Next.js + Vercel** | Vercel | Most flexible; ISR/SSG/SSR; API routes | `adapters/stack-nextjs.md` |
| **Astro** | Vercel / Netlify | Zero-JS by default; fast builds; islands | `adapters/stack-astro.md` |
| **Hugo** | Vercel / Netlify | Fastest static generator (Go); 50K pages in seconds | `adapters/stack-hugo.md` |
| **SvelteKit** | Vercel / Netlify | Compile-time framework; smaller bundles | `adapters/stack-sveltekit.md` |
| **Plain static HTML** | Vercel / Cloudflare / GH Pages | Simplest; no build step | `adapters/stack-static-html.md` |

---

## Hosting + DNS

| Service | Use | Cost | Surfacing |
|---|---|---|---|
| **Vercel** | Hosting (Next/Astro/static) | Free Hobby; $20/mo Pro | `fetch-on-demand` (MCP + docs) |
| **Cloudflare** | DNS / CDN / Workers / Pages | Free DNS; $20/yr Pro | `fetch-on-demand` (official MCP) |
| **Netlify** | Hosting (static / SSG) | Free starter; $19/mo Pro | `fetch-on-demand` (CLI) |
| **GitHub Pages** | Hosting (static) | Free | `fetch-on-demand` (gh CLI) |
| **Render** | Hosting (full-stack apps) | Free tier; paid scaling | `fetch-on-demand` (API) |
| **Railway** | Hosting (apps + databases) | Pay-as-you-go | `fetch-on-demand` (CLI) |
| **AWS Amplify** | Hosting (full-stack) | Pay-as-you-go | `fetch-on-demand` (AWS CLI) |

**Domain registrars:** Namecheap (API + IP whitelist), Cloudflare Registrar (at-cost), Porkbun (cheap), Gandi (EU-friendly). All `fetch-on-demand`.

---

## Inspiration galleries

Browse-and-discuss surfaces — visited for inspiration, **never cloned or imported**. All `fetch-on-demand`. Surface most heavily at phase 2 (vision) + phase 17 (design system).

| Resource | URL | Used for |
|---|---|---|
| **Awwwards** | https://www.awwwards.com | Award-winning sites by style + stack; mood-board source |
| **Dribbble** | https://dribbble.com | Designer portfolios; visual inspiration |
| **Behance** | https://behance.net | Adobe's portfolio platform |
| **Land-book** | https://land-book.com | Landing-page gallery |
| **One Page Love** | https://onepagelove.com | Single-page site gallery |
| **Mobbin** | https://mobbin.com | Mobile app patterns |
| **SaaS Pages** | https://saaspages.xyz | SaaS-specific landing patterns |
| **nicolesaidy/awesome-web-design** | https://github.com/nicolesaidy/awesome-web-design | Curated gateway to inspiration / colors / typography / icons |

---

## Templates + starter sources

Templates are **studied for inspiration, never imported** (VISION anti-vision). The agent surfaces a per-stack subset at phase 11+ once the stack is chosen; discussion produces aesthetic vocabulary for the design system. All `fetch-on-demand`.

### Free / freemium

| Source | URL | Stack focus |
|---|---|---|
| **Vercel Templates** | https://vercel.com/templates | Next / Astro / SvelteKit (~1000+, MIT) |
| **Astro Themes** | https://astro.build/themes | Astro (~300+) |
| **CloudCannon Themes** | https://cloudcannon.com/themes | Static (Hugo/Jekyll/Astro) |
| **Cruip** | https://cruip.com | Tailwind (HTML/React/Vue); SaaS aesthetic |
| **Statichunt** | https://getstatichunt.com | Multi-stack (Hugo/Jekyll/Astro/11ty/Next/Nuxt) |
| **GetAstroThemes** | https://getastrothemes.com | Astro |
| **Once UI Starters** | https://once-ui.com | Next.js + Once UI |

### Paid

| Source | URL | Cost | Use when |
|---|---|---|---|
| **Tailwind UI (Tailwind Plus)** | https://tailwindui.com | $299 one-time | Professional Tailwind reference (also component library) |
| **Framer Marketplace** | https://framer.com/marketplace | $10-100+/template | Framer-specific (studied, never auto-imported) |
| **ThemeForest** | https://themeforest.net | $20-90/template | WordPress primary; HTML/React/Shopify (variable quality) |

### Per-stack / per-CMS additional sources

- **Framer:** Framer Marketplace + framer.university
- **WordPress:** ThemeForest + WordPress.org Theme Directory + StudioPress
- **Webflow:** https://webflow.com/templates + Made in Webflow showcase
- **Next.js:** Vercel Templates + Vercel showcase + awesome-nextjs
- **Astro:** astro.build/themes + GetAstroThemes + Statichunt
- **Hugo:** https://themes.gohugo.io + Statichunt
- **SvelteKit:** https://www.sveltesociety.dev/templates + awesome-svelte
- **Static HTML:** HTML5UP + Templated.co + Bootswatch
- **Payload:** Payload GitHub examples + Payload Cloud templates
- **Sanity:** Sanity Exchange
- **Strapi:** Strapi Marketplace
- **Ghost:** https://ghost.org/marketplace

---

## Framework documentation (context7-served)

The plugin fetches fresh framework docs via context7 MCP. Chosen-stack docs go `clone-into-project`; the rest stay `fetch-on-demand`.

| Tech | context7 library ID | Usual surfacing |
|---|---|---|
| **Next.js** | `/vercel/next.js` | `fetch-on-demand` (huge docs; specific lookups) |
| **Astro** | `/withastro/docs` | `fetch-on-demand`; `clone-into-project` if chosen |
| **Hugo** | `/gohugoio/hugo` | `fetch-on-demand` |
| **SvelteKit** | `/sveltejs/kit` | `fetch-on-demand` |
| **shadcn/ui** | `/shadcn/ui` | `clone-into-project` (queried repeatedly at phase 18) |
| **Tailwind CSS** | `/tailwindlabs/tailwindcss.com` | `fetch-on-demand` (huge utility docs) |
| **Payload** | `/payloadcms/payload` | `clone-into-project` if Payload chosen |
| **Decap CMS** | `/decaporg/decap-cms` | `clone-into-project` if Decap chosen |
| **Framer Server API** | `/framer/server-api-docs` | `clone-into-project` if Framer chosen |
| **WordPress REST API** | `/wordpress/wp-rest-api` | `clone-into-project` if WordPress chosen |
| **Stripe API** | `/stripe/stripe-docs` | `clone-into-project` if commerce + Stripe |
| **Cal.com API** | `/calcom/cal.com` | `clone-into-project` if booking + Cal.com |

---

## How the user grows their own library

As the project progresses, `clone-into-project` resources land in `.website-builder/library/` (via auto-clone at phase triggers, or `wb library add <url>`). By ship time the user has a project-scoped resource library they can carry forward to their next site:

```
.website-builder/library/
├── docs/              # cloned framework / library / API docs
├── awesome-design-md/ # cloned design exemplars (full corpus when the bundled subset isn't enough)
├── inspiration/       # collected reference URLs + mood-board notes
├── community-skills/  # cloned CC skills they used
└── README.md          # what's here + when each was cloned
```

Bundled corpora (the six above) always ship with the plugin (in `reference-corpus/`); the orchestration spine auto-clones the relevant ones into `.website-builder/library/<dir>/` at phase entry (a local copy, no network), where the agent reads them alongside the runtime-cloned resources.
