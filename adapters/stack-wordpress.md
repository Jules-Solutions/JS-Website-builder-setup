# Stack adapter — WordPress

> The muggle-friendly server-side MVP stack. Picked when the user wants an audience-familiar admin UI, the largest plugin ecosystem on earth, paid managed hosting that handles backups/SSL/updates, and a content-heavy site managed long-term by non-technical editors. The agent ships a **custom block theme** (Full Site Editing) plus **custom Gutenberg blocks** (one per `sections.yaml` section type), seeds pages + media via the WordPress REST API, layers **Polylang** (default) or **WPML** for i18n, and adds **WooCommerce** when `transactional=true`. Per locked decision 52 (MVP build-now) + BUILD-strategy.md Phase 3 (the WordPress lane in the parallel-stack Captain dispatch).
>
> **Schema contract:** this file follows the canonical 14-H2 schema in `adapters/README.md`. Section names + order are non-negotiable — phase-11 / phase-17 / phase-18 / phase-24a / phase-28-30 / phase-6.5 skill lookups bind to exact H2 names.
> **Source-of-truth:** `Workstreams/website-builder/stacks/DESIGN-stack-wordpress.md` is the design-doc anchor; this adapter is the runtime extraction the skills consume.

## Mental model

### Identity

- **Stack:** WordPress
- **Version baseline:** WordPress **6.6+** (Full Site Editing standard; theme.json **version 3** schema; Block API v3 in `block.json`)
- **Canonical context7 library IDs:** `/wp-api/docs` (REST API; 755 snippets, high reputation, benchmark 67.8), `/websites/developer_wordpress_block-editor` (Block Editor handbook; 5,246 snippets, benchmark 71.35), `/woocommerce/woocommerce-rest-api-docs` (WooCommerce REST; 1,469 snippets, benchmark 76.52 — when `transactional=true`). Verified live 2026-05-20.
- **Freshness-check requirement:** the agent invokes context7 at phases 11 / 17 / 18 / 24a / 28-30 to confirm current surface — WordPress evolves quickly (FSE is the 2026 standard, not the experimental track it was through 2023; theme.json moved 2 → 3 in 6.6; Block API v3 supersedes v2; Block Bindings + Interactivity API are 2026 development models). Training data is stale on the schema transitions. Pair with WebFetch against developer.wordpress.org/themes/ + developer.wordpress.org/block-editor/ when context7 coverage is thin.

WordPress is two things glued together:

1. **A PHP application** running on Apache or Nginx against MySQL/MariaDB, with a templating layer (`wp_theme`), an extension system (plugins), and an admin UI at `/wp-admin`. The user logs in here every day.
2. **A content management surface** with custom post types, taxonomies, meta fields, the **Gutenberg block editor** as the canonical authoring tool, and a sprawling plugin ecosystem (~60,000 plugins as of 2026).

The WordPress **REST API** exposes most of this programmatically at `/wp-json/wp/v2/*` — posts, pages, media, taxonomies, users, custom post types, custom fields (via plugins like ACF or Meta Box). The agent uses the REST API for content operations + writes the custom block theme files (PHP / CSS / `theme.json` / `block.json`) directly into `wp-content/themes/{slug}/`. The user interacts mostly with `/wp-admin` after launch.

Three muggle-facing things to know about how WordPress thinks in 2026:

- **Block themes (Full Site Editing) are the modern standard.** Not experimental, not optional. `theme.json` defines tokens; Gutenberg blocks compose pages + templates; the entire site is composed in the block editor. **The agent ships block themes by default.** Classic PHP themes only with explicit user reason.
- **Custom Gutenberg blocks are the WP equivalent of components.** Registered via `block.json`; rendered by PHP (`render.php`, dynamic blocks) or React (`edit.tsx` + `save.js`, static blocks). The agent writes **one custom block per section type** from `sections.yaml` (matches phase-18 component-build).
- **Page builders (Elementor / Divi / Beaver Builder) are user-territory.** The agent supports them when the user explicitly picks one at phase 12, but does not lead with them — they fight Gutenberg, lock content into proprietary structures, and complicate exports. Trade-offs surfaced at phase 12.

The muggle's mental model is: *the agent ships a custom block theme + custom blocks + seeds content via REST. The user adds posts/pages, swaps images, edits prose in `/wp-admin`. The theme is the contract; everything else is content the editor owns.*

The trade-off vs Framer + Next.js: **WordPress requires a server.** It can't be statically exported (without going headless). Paid hosting is the assumed entry — Kinsta / WP Engine / SiteGround / Cloudways / Bluehost / Hostinger for managed-WP; DigitalOcean / Linode / VPS for self-hosted. The user signs up for a host and provisions a database; the agent works on top.

## Auth + setup

### Self-hosted vs WordPress.com

- **Self-hosted (default for serious sites):** user picks a host. Agent surfaces trade-offs at phase 11 (see §10 `## Deploy`). Self-hosted gives full plugin freedom + custom themes + REST API access.
- **WordPress.com Business+ plan:** user-friendly; agent supports it; some plugin restrictions apply. Lower plans (Free / Personal / Premium) can't install custom themes or arbitrary plugins → agent surfaces at phase 11 and recommends Business+ minimum if WordPress.com is the choice.

### Local dev

Agent recommends `wp-env` (official Docker-backed local environment, ships in the `@wordpress/env` npm package) as the primary local dev path. LocalWP (Flywheel) is the GUI alternative for less-technical users.

```bash
# install wp-env globally
npm install -g @wordpress/env

# in user's project, start a local WordPress at http://localhost:8888
wp-env start

# stop
wp-env stop
```

The agent works on theme + plugin files locally; deploy goes git-push → managed-host integration OR rsync/SFTP for self-hosted VPS.

### REST API auth

- **Application Passwords** (built-in since WP 5.6 — the canonical agent auth path). User generates an Application Password from `/wp-admin/users/profile.php`. Agent stores reference in `.website-builder/keys.yaml` keyed to `WP_APP_PASSWORD` env var; resolution per `secrets-conventions.md` from 1Password — never hardcoded in any file.
- **JWT Authentication plugin** for token-based auth (alternative; rare).
- **OAuth** for advanced flows (rare; agent uses Application Passwords by default).

The agent's REST calls use HTTP Basic Auth over HTTPS:

```bash
# Create a page via REST + Application Password
curl --user "admin:xxxx xxxx xxxx xxxx xxxx xxxx" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "title": "About",
    "slug": "about",
    "status": "publish",
    "content": "<!-- wp:paragraph --><p>...</p><!-- /wp:paragraph -->"
  }' \
  https://example.com/wp-json/wp/v2/pages

# Upload media
curl --user "admin:xxxx xxxx xxxx xxxx xxxx xxxx" \
  -X POST \
  -H "Content-Disposition: attachment; filename=hero.jpg" \
  --data-binary @./media/hero.jpg \
  https://example.com/wp-json/wp/v2/media
```

### CRUD vocabulary

WordPress's REST CRUD vocabulary translates non-obviously into website-builder verbs. The agent uses this mapping at phases 6 / 8 / 13-19 / 24a / 28-29:

| Website-builder verb | WordPress REST verb | Endpoint |
|---|---|---|
| Create a page | `POST` page | `/wp-json/wp/v2/pages` |
| Update a page | `POST` page (by id) | `/wp-json/wp/v2/pages/{id}` |
| Create a post (blog article) | `POST` post | `/wp-json/wp/v2/posts` |
| Set page hierarchy | `parent` field on page | `/wp-json/wp/v2/pages/{id}` `{"parent": 42}` |
| Upload media | `POST` media (binary) | `/wp-json/wp/v2/media` |
| Create custom post type entry | `POST` to CPT route | `/wp-json/wp/v2/{cpt-slug}` |
| Add tag/category | `POST` taxonomy | `/wp-json/wp/v2/categories` |
| Publish | `status: "publish"` field | (any of the above) |
| Unpublish | `status: "draft"` field | (any of the above) |
| Delete | `DELETE` | `/wp-json/wp/v2/{type}/{id}` |
| Set featured image | `featured_media: {media_id}` | on the page/post POST |

**Native CLI peer:** `wp-cli` (`wp post create ...`, `wp media import ...`) is available on self-hosted + managed-WP that offer SSH. The agent uses REST as primary, `wp-cli` over SSH as fallback when REST is rate-limited or auth is unavailable.

### MCP servers (verify at phase 11)

The WordPress ecosystem has multiple MCP servers in active development as of 2026-05. **Agent invokes `mcp__context7__resolve-library-id` for "WordPress MCP" at phase 11 to confirm which is most-maintained.** Common surfaces (subject to drift):

- **WordPress MCP** — REST API wrapper; CRUD on posts, pages, media, custom post types.
- **WooCommerce MCP** — products, orders, customers, coupons.
- **Gutenberg block MCP** — block registration + content insertion.
- **WP-CLI MCP** — wraps WordPress' command-line tool for plugin/theme management, user creation, DB operations.
- **ACF MCP** — Advanced Custom Fields management.

Where MCPs aren't available or aren't reliable, agent falls back to direct REST API calls via `Bash` (curl) or `wp-cli` via SSH (self-hosted).

### Custom block-theme scaffold

The agent writes theme files directly into `wp-content/themes/{slug}/`. Canonical FSE block-theme layout (verified against developer.wordpress.org 2026-05-20):

```
wp-content/themes/{slug}/
├── theme.json              # version: 3 — color/typography/spacing presets (from brand.yaml)
├── style.css               # theme metadata (name, version, URI, license)
├── functions.php           # register custom blocks, enqueue assets, theme supports
├── templates/              # HTML templates (block-markup files; FSE)
│   ├── index.html          # main archive template
│   ├── single.html         # single-post template
│   ├── page.html           # default page template
│   ├── page-{slug}.html    # per-page-slug template
│   └── 404.html
├── parts/                  # reusable template parts
│   ├── header.html
│   └── footer.html
├── patterns/               # block patterns — auto-registered from PHP files
│   ├── hero.php
│   └── footer-cta.php
└── styles/                 # optional theme-style variations (JSON)
    └── dark.json
```

### Custom Gutenberg block scaffold

Each section type from `sections.yaml` becomes a custom Gutenberg block. The agent scaffolds via `@wordpress/create-block`:

```bash
# from the user's project root (or wp-content/plugins/{slug}-blocks/)
npx @wordpress/create-block@latest hero-block --variant=dynamic
```

The `--variant=dynamic` flag picks PHP-side rendering (`render.php`) — the agent's default for blocks that need server-rendered output. `--variant=static` (omit the flag) for blocks where the markup is fully serialized in `post_content`.

Generated structure per block:

```
wp-content/plugins/{slug}-blocks/blocks/hero-block/
├── block.json              # apiVersion: 3 — Block API metadata
├── render.php              # server render (dynamic) — receives $attributes, $content, $block
├── edit.tsx                # block editor view (React)
├── save.js                 # static save (omit for dynamic-only)
├── style.scss              # frontend styles
└── editor.scss             # editor-only styles
```

Per-block `block.json` follows current Block API v3 schema (verified context7 + developer.wordpress.org 2026-05-20):

```json
{
  "$schema": "https://schemas.wp.org/trunk/block.json",
  "apiVersion": 3,
  "name": "still-humans/hero-block",
  "title": "Hero Block",
  "category": "design",
  "description": "Top-of-page hero with headline, sub, and CTA.",
  "textdomain": "still-humans",
  "attributes": {
    "headline": { "type": "string" },
    "sub": { "type": "string" },
    "ctaText": { "type": "string" }
  },
  "supports": {
    "html": false,
    "anchor": true,
    "color": { "background": true, "text": true }
  },
  "editorScript": "file:./index.js",
  "editorStyle": "file:./editor.css",
  "style": "file:./style.css",
  "render": "file:./render.php"
}
```

## Migration recipe

Pre-step-11 canonical `.website-builder/` content → WordPress block theme + custom blocks + REST-seeded content. The deeper version of the §4 table — narrative + recipes + edge cases.

```
.website-builder/                            →  user-website-project/ (WordPress)
├── brand.yaml.tokens                        →  wp-content/themes/{slug}/theme.json
│                                                version: 3 (current — verified against
│                                                https://schemas.wp.org/trunk/theme.json)
│                                                colors  → settings.color.palette[] (slug + color + name)
│                                                typography → settings.typography.fontFamilies[] +
│                                                              settings.typography.fontSizes[] (+ fluid: {min, max})
│                                                spacing → settings.spacing.spacingScale OR
│                                                          settings.spacing.spacingSizes[]
│                                                motion → CSS custom properties in style.css (no native theme.json
│                                                          slot — emit via styles.css.additional + custom CSS vars)
│                                                shadow → settings.shadow.presets[]
│                                                dark-mode → styles/dark.json (theme style variation)
│                                                Auto-generates --wp--preset--color--{slug}, --wp--preset--font-size--{slug},
│                                                --wp--preset--spacing--{slug} CSS custom properties for custom-block CSS use
│
├── content/strings/{lang}.json              →  Polylang (default) or WPML String Translation +
│                                                theme `lang/{slug}.pot` + per-locale `lang/{slug}-{lang}.po`/.mo
│                                                Keys → `__()`-wrapped strings in PHP/JS via `wp_localize_script`
│                                                Plurals → ICU pattern preserved in .po (msgid_plural + msgstr[N])
│                                                Variables {name} → printf %s sprintf substitution
│                                                See §5 i18n integration + Polylang/WPML choice
│
├── sitemap.yaml + sections.yaml             →  WP page hierarchy (post_parent + menu_order on pages)
│                                                One page per sitemap entry via POST /wp-json/wp/v2/pages
│                                                + Yoast SEO or RankMath for sitemap.xml emission
│                                                + nav menus registered via wp_nav_menu in functions.php
│                                                navigation: block → custom Navigation block configured in
│                                                  parts/header.html + the navigation post type (FSE)
│                                                Each unique section-type from sections.yaml →
│                                                  one custom Gutenberg block (see L5 row below)
│
├── content/pages/{slug}.{lang}.md           →  POST /wp-json/wp/v2/pages with body converted to
│                                                Gutenberg block-markup composition:
│                                                  - Markdown paragraphs → core/paragraph blocks
│                                                  - Markdown headings → core/heading blocks (level matched)
│                                                  - Markdown images → core/image blocks
│                                                  - Markdown links → inline anchor tags inside core/paragraph
│                                                  - Per-section content → invocation of the custom block for that section
│                                                Frontmatter sections: [...] → ordered list of block invocations in
│                                                content (or page-{slug}.html template + block-bound attributes)
│                                                Pattern A (per DESIGN-i18n.md): one page row per language, linked via
│                                                Polylang/WPML post-meta or the plugin's translations table
│                                                Pattern B (per-locale variation): same — each locale is its own
│                                                wp_posts row with different content per slug-{lang}.md
│
├── components.yaml + components/code        →  Custom Gutenberg blocks (one per section type):
│                                                wp-content/plugins/{slug}-blocks/blocks/{section-name}/
│                                                  ├── block.json (apiVersion: 3)
│                                                  ├── render.php (dynamic — for content-bound blocks)
│                                                  └── edit.tsx (React — editor view)
│                                                Component props → block.json.attributes entries
│                                                Variants → block.json.variations
│                                                A11y constraints → render.php emits proper heading levels,
│                                                  alt text, ARIA per components.yaml.accessibility
│                                                Responsive → Tailwind utilities (when DaisyUI option picked) OR
│                                                  theme.json fluid typography + CSS logical properties
│
├── briefs/{component}-{ts}.json             →  Stays in user's git repo at .website-builder/briefs/
│                                                (gitignored at user project; round-trip artifacts only)
│                                                output_format payload for WP: framework=php, library=wp-gutenberg,
│                                                style_system=tailwind (when DaisyUI) OR theme-json + custom CSS,
│                                                language=php (render.php) + tsx (edit.tsx)
│                                                Per handoff-spec/component-request-v1.md
│
├── decisions/                               →  Kept in user's git repo (theme repo or sidecar
│                                                `.website-builder/`); not synced to WP
│
└── media/                                   →  WP Media Library via POST /wp-json/wp/v2/media
                                                 Sizes auto-generated by WP per add_image_size() registered
                                                 in functions.php from brand.yaml breakpoints
                                                 Featured image set via featured_media on the page POST
```

**Page builder fallback (when user explicitly picks Elementor / Divi / Beaver Builder at phase 12):**

- Pages composed via the chosen builder's UI; agent writes a starter template per page using the builder's API where available (Elementor's REST endpoints + template import; Divi's library JSON; Beaver's row-template export).
- Custom blocks become the builder's widgets (Elementor) / modules (Divi) / modules (Beaver). Different artifact shape; agent writes the equivalent rather than Gutenberg blocks.
- Trade-offs flagged at phase 12: page-builder lock-in (content tightly coupled to the builder), heavier page weight, harder to migrate later. Agent surfaces explicitly; user accepts before proceeding.

## Content layer mapping

The mandatory five-row table. This is the cross-stack verification anchor — same labels appear in `stack-framer.md` + `stack-nextjs.md`, one column "WordPress native concept" filled. Side-by-side comparison across all three Phase 3 stacks proves *"same `.website-builder/` content produces equivalent sites on all 3 stacks (modulo platform-specific limitations)."*

| Layer | WordPress native concept |
|---|---|
| L1 brand.yaml.tokens | `theme.json` (`version: 3`) — `settings.color.palette[]`, `settings.typography.fontFamilies[]` + `fontSizes[]` (+ `fluid: {min, max}` per-font-size), `settings.spacing.spacingScale` or `spacingSizes[]`, `settings.shadow.presets[]`. Auto-generates `--wp--preset--color--{slug}` / `--wp--preset--font-size--{slug}` / `--wp--preset--spacing--{slug}` CSS custom properties for custom-block CSS references. Dark-mode + alternate palettes via `styles/{name}.json` theme style variations. Motion has no native theme.json slot — emit as custom CSS variables (e.g. `--wb-motion-duration-med`) declared in `style.css` and referenced from block CSS. |
| L2 sitemap.yaml + sections.yaml | WordPress page hierarchy (`post_parent` + `menu_order` on `wp_posts` rows of `post_type=page`) via REST `POST /wp-json/wp/v2/pages`. Nav menus registered via `wp_nav_menu` in `functions.php`; navigation block (`core/navigation`) in `parts/header.html`. One custom Gutenberg block per unique `sections.yaml` section type. Block patterns (auto-registered from `patterns/*.php` via file header comments — `Title:`, `Slug:`, `Categories:`) act as composable page-section primitives. |
| L3 strings/{lang}.json | **Polylang** (default per S5 framing — free, ~80% of WPML's features) OR **WPML** (paid; commercial sites with serious i18n needs). Keys map to text-domain strings consumed by `__()` / `_e()` / `_n()` in PHP + JS. Source bundle generated as `theme.json`-adjacent `lang/{slug}.pot`; per-locale `lang/{slug}-{lang}.po`/`.mo` files compiled. Plugin's String Translation table handles UI strings. ICU plurals preserved in `.po` `msgid_plural` + `msgstr[N]` entries; variables `{name}` mapped via `sprintf`/`printf` substitution. |
| L4 content/pages/*.md | `POST /wp-json/wp/v2/pages` with `content` field carrying Gutenberg block-markup serialization. Markdown body converted: `# Heading` → `<!-- wp:heading -->`, paragraph → `<!-- wp:paragraph -->`, image → `<!-- wp:image -->`, frontmatter `sections: [...]` → ordered invocation of the matching custom blocks. Pattern A multilingual: one page row per language, linked via Polylang/WPML post-meta. Pattern B: each locale is its own `wp_posts` row with different content. SEO frontmatter → Yoast/RankMath custom-field meta. |
| L5 briefs/{component}.json | **Gutenberg block brief format** — `output_format.framework=php`, `output_format.library=wp-gutenberg`, `output_format.language=php` (`render.php`) + `tsx` (`edit.tsx`) + `json` (`block.json`), `output_format.style_system=tailwind` (when DaisyUI option picked per §9) OR `theme-json + custom CSS`, `output_format.file_path_hint=wp-content/plugins/{slug}-blocks/blocks/{slug}/`, `output_format.file_count_hint=3` (block.json + render.php + edit.tsx). Brief format per `handoff-spec/component-request-v1.md`; stack-portable except for this `output_format` block. |

## i18n integration

WordPress has two production-grade i18n plugins. The agent picks at phase 12 (CMS decision) given stack is WordPress.

- **Polylang (free + Pro) — default per S5 framing.** Covers ~80% of WPML's features; free for muggle-budget projects. Handles posts, taxonomies, menus, strings translation. Pro adds advanced sync. Recommended unless user has commercial-translation-tooling requirements.
- **WPML (paid).** Most feature-complete; premium support; commercial-translation-vendor integration (translation services natively). Recommended when translation quality materially affects business outcomes + user has the budget.
- **TranslatePress (alternative).** Visual translation editor; lower-friction muggle UX; less complete i18n model. Agent surfaces when user explicitly asks for visual translation.

**Routing strategy:** prefix (per locked decision 38 default). All three plugins support prefix. Subdomain requires extra DNS setup; TLD requires multi-site network config.

**Per-language pages:** Polylang/WPML represent each translation as a separate `wp_posts` row linked via plugin-specific post-meta. Agent creates one post per language per page via REST + the plugin's API.

**Strings:** the agent generates `theme.pot` from `__()`-wrapped strings in PHP + JS; per-locale `.po`/`.mo` files compiled. CDJSON keys map to WordPress text-domain strings; values translated via Pattern 1 (agent inline at phase 16) OR Pattern 2 (translator handoff via brief) OR Pattern 3 (user-driven external tool) per `DESIGN-i18n.md` §"Translation workflow".

**hreflang:** auto-emitted by Polylang/WPML. Agent verifies at phase 26 + provides manual-emission fallback when plugin output is wrong (see `i18n/hreflang.md#wordpress`).

**Language switcher:** plugin ships widgets; agent customizes markup to match brand (custom Gutenberg block reading the plugin's API). See `i18n/language-switcher.md#wordpress`.

**RTL:** WordPress has first-class RTL support — block themes' `style.css` can include `rtl.css` overrides; `theme.json` settings respect directional tokens via CSS logical properties. Agent generates RTL-safe CSS via CSS logical properties from phase 18 onward (per `i18n/rtl.md`); `lang="ar"`-scoped overrides for typography (line-height, letter-spacing). RTL languages auto-set `dir="rtl"` via the theme's `body` filter + the `<html lang>` `lang_attributes` filter when Polylang/WPML mark a language as RTL.

**Cross-references for deep specifics:**

- `i18n/language-switcher.md#wordpress` — switcher component (Polylang/WPML widget choice + custom template part fallback + localStorage persistence via inline JS in `wp_footer`)
- `i18n/hreflang.md#wordpress` — hreflang emission (Polylang/WPML auto-emit + manual `header.php` fallback + caching-plugin gotchas)
- `i18n/strings-schema.md` — stack-agnostic CDJSON contract (consumption recipe described in this section's "Strings" paragraph)
- `i18n/rtl.md` — RTL discipline (stack-agnostic; CSS logical properties + `dir="rtl"` mechanism is the same here as everywhere)

## Phase 6.5 ingestion

Phase 6.5 is re-runnable at any project lifecycle point — `entry-mode` set at session start drives the initial ingestion; user can invoke at any phase to integrate a new artifact (mom's pattern). For WordPress-targeted projects:

### Entry mode mapping

- **`greenfield`** — no ingestion at session start; phase 11 picks WordPress; phase 17 onward authors theme + blocks from scratch.
- **`has-existing-site`** (existing WordPress site to migrate or extend):
  - Agent walks live URL with **`extraction/playwright-walk.md`** (Playwright MCP) — captures screenshots per section + DOM dumps across desktop/tablet/mobile viewports + hover states + scroll-triggered animations. Artifacts in `.website-builder/outputs/playwright-{ts}/`.
  - For published WordPress sites, agent ALSO calls `GET /wp-json/wp/v2/{posts,pages,media}` via REST to enumerate existing content (read-only at this phase; no writes until user confirms).
  - Playwright DOM + REST inventory feed into **`extraction/stitch.md`** for design-token extraction and **`extraction/ai-output.md`** for component-shape extraction from rendered HTML.
- **`has-existing-site`** (existing non-WordPress site to rebuild as WordPress):
  - Same Playwright walk + Stitch extraction; agent treats the site as a reference, then builds the theme + blocks from extracted tokens + structure.
- **`has-ai-output`** (one-shot landing page from ChatGPT / Claude.ai / v0 / Lovable / etc.):
  - **`extraction/ai-output.md`** parses the HTML/JSX. Tokens → `brand.yaml` (conflict-halt protocol). Component shapes → `components.yaml`. Page prose → `content/pages/{slug}.md`. Reusable strings → `content/strings/{lang}.json`.
  - Translated into Gutenberg-block form at phase 18 — the AI tool's React/HTML doesn't run directly in WP; agent re-implements as custom blocks against the same component spec.
- **`has-framer-attempt`** (partial Framer / Webflow / Wix project user wants to rebuild on WordPress):
  - Same Playwright walk + Stitch path; agent treats artifacts as reference and rebuilds in WP. Trade-offs surfaced ("you're effectively starting over; the design carries; the implementation doesn't").
- **`has-figma-file`** (Figma file delivered by a designer):
  - **`extraction/figma-design-to-json.md`** (user runs the Figma plugin) → JSON. Agent normalizes design tokens into `theme.json`; section/component shapes into `sections.yaml` + `components.yaml`. Phase 18 authors the custom blocks.

### Normalization output paths (WordPress-specific)

Once `.website-builder/` state is normalized, the WordPress-specific landing paths at phases 17 / 18 are:

- Tokens → `wp-content/themes/{slug}/theme.json` `settings.*`
- Custom CSS (motion, override) → `wp-content/themes/{slug}/style.css` `:root { --wb-motion-duration-med: 300ms; ... }`
- Pages → `POST /wp-json/wp/v2/pages` with `content` field carrying serialized Gutenberg block markup
- Media → `POST /wp-json/wp/v2/media` (binary upload via `Content-Disposition: attachment; filename=...`)
- Strings → theme `lang/*.po`/`.mo` + Polylang/WPML String Translation entries
- Custom blocks → `wp-content/plugins/{slug}-blocks/blocks/{section-name}/`

### Auth-walled site handling

If the target WordPress site requires authentication (private dev site, staging, member-only routes), the agent walks Playwright through the login flow:

1. User provides credentials inline (chat-state only; never written to disk).
2. Playwright `browser_fill_form` against `/wp-login.php`.
3. Walks authenticated routes per the configured walk plan.
4. Session cleaned up at walk end.

Two-factor-authenticated sites can't be auto-walked — user provides screenshots from their own session for the agent to pass into Stitch's screenshot mode (per `extraction/playwright-walk.md` §"Failure modes").

### Round-trip ingestion output paths (phase-18 handoff round-trip)

When the agent emits a `component-request-v1` brief and the user goes external (v0 / Cursor / ChatGPT / human freelancer), the round-trip back through phase 6.5 with **`extraction/ai-output.md`** lands in:

- `.website-builder/outputs/{component}-{ts}.{ext}` — raw pasted-back output (audit trail)
- Component code translated into custom-block form at `wp-content/plugins/{slug}-blocks/blocks/{section-name}/render.php` + `edit.tsx`
- `components.yaml` entry updated with the new shape (conflict-halt if existing)
- `briefs/{component}-{ts}.json` `iteration_history` appended

Per locked decision 36, every conflict halts and forces user resolution before phase 6.5 completes. No silent merge.

## Commerce integration (if transactional=true)

When phase-11's transactional sibling resolves to `true`, phase 24a/b/c branches per the WooCommerce path (canonical for WordPress).

### Phase 24a — Commerce platform

**WooCommerce is the canonical default** for transactional WordPress sites. ~28% of all e-commerce sites worldwide use it. Agent installs WooCommerce + scaffolds shop pages + creates products via WC REST API.

```bash
# Activate WooCommerce + create a product
curl --user "admin:xxxx xxxx xxxx xxxx xxxx xxxx" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Newsletter Subscription",
    "type": "simple",
    "regular_price": "9.99",
    "description": "Monthly subscription to the Still Humans letter.",
    "status": "publish"
  }' \
  https://example.com/wp-json/wc/v3/products
```

Other commerce options (surface at phase 24a only when WooCommerce is wrong for the use case):

- **Easy Digital Downloads (EDD)** — digital-only stores; lighter than WC. Pick when user is digital-only + WC's physical-product features are unused weight.
- **WP eCommerce, MemberPress, LearnDash** — niche specialty (memberships, courses). Pick when user has explicit need.
- **External commerce embedded in WP** — Shopify Buy Button, Lemon Squeezy embed, Stripe Checkout links. Pick when WP is the marketing layer + commerce is somewhere else (rare; surface trade-off — split-system maintenance burden).

### Phase 24b — Payment provider wiring

WooCommerce supports all canonical providers via official plugins (verified active 2026; verify currency via context7 `/woocommerce/woocommerce-rest-api-docs` at phase 24b):

- **Stripe for WooCommerce** — primary recommendation; supports SCA / 3DS, regional methods (Apple Pay, Google Pay, link).
- **Mollie for WooCommerce** — strong EU coverage including TWINT (Switzerland — per locked decision 47 the canonical Swiss payment method), iDeal (NL), SEPA, Bancontact. Recommended for Swiss + EU-consumer markets.
- **PayPal for WooCommerce** — legacy; recommend only when user explicitly requires.
- **Square for WooCommerce** — US-heavy stores.
- **Klarna** — BNPL; EU consumer market.

Agent configures the chosen plugin via WC REST or by direct DB update (admin-only); verifies test purchase at phase 24a exit.

### Phase 24c — Commerce-specific legal

Refund / shipping / T&Cs pages created as WP pages via REST. Linked from checkout flows in WC settings (Checkout endpoints registered in `wp-admin/admin.php?page=wc-settings&tab=advanced`). EU-specific compliance (revFADP for Switzerland / GDPR / EU consumer rights) addressed via Iubenda / CookieYes / Complianz WP plugins installed at phase 25.

### Booking flows (transactional_kind: bookings or both)

- **Cal.com / Calendly / SimplyBook.me** embedded via custom Gutenberg block wrapping the embed script (per locked decision 54 — Cal.com is MVP default for free booking).
- **Native WP booking plugins** (Bookly, Amelia) — agent supports when user prefers in-WP booking + has the operational appetite for the plugin maintenance.

## CMS pairing

**WordPress IS the CMS.** Phase 12 (CMS decision) is essentially a thin confirmation pass when stack is WordPress — the user uses WP's native admin (`/wp-admin`). `project.yaml.cms = "wordpress-core"` is the default. Decoupling only when user has explicit reason.

### Default — WordPress core

The canonical pairing. Agent writes the block theme + custom blocks; user edits pages/posts in `/wp-admin/edit.php?post_type=page`; everything is one system. No separate CMS host, no separate auth, no API surface between front + back.

### Rare cases — Headless WordPress (WP as backend, decoupled frontend)

User runs WordPress as headless (REST API only) + a separate frontend stack (Next.js / Astro / SvelteKit) consuming WP content. When user explicitly picks this:

- **Treat the project as a Next.js / Astro / SvelteKit project at heart** with WP as the CMS layer. The actual *stack* per `project.yaml.stack` is the frontend — not WordPress.
- The frontend-stack adapter (`adapters/stack-nextjs.md` etc.) takes over for phases 17 / 18 / 28-30.
- This adapter (`stack-wordpress.md`) covers only the WP-backend operations: content auth, REST access, custom post type registration for the consumed-by-frontend content shapes.
- Re-opens phase 11 (the stack decision must be re-resolved — the user picked WordPress as backend, but the actual frontend stack is what governs build/deploy/component work).

### Rare cases — Heavily decoupled WP (custom themes layered on a third-party CMS)

When user wants to keep WordPress content but use a different CMS abstraction layer:

- **ACF (Advanced Custom Fields)** — richer field types than WP's native post meta. Agent installs when `components.yaml` requires custom fields beyond paragraph/image/embed/etc. Common for testimonials, case studies, team members, product catalogs.
- **Meta Box** — same category as ACF; lighter; alternative.
- **Pods, Toolset** — niche.

These are addons within WP-core CMS — not replacements. Agent installs the chosen plugin when content shape demands it.

### Compatibility matrix

| CMS | Pairs with WordPress? | Notes |
|---|---|---|
| `wordpress-core` | ✅ default | The canonical path |
| `wordpress-core + ACF` | ✅ structured-content addon | For richer custom-field needs |
| `wordpress-core + Meta Box` | ✅ alternative addon | ACF peer |
| Decap | ⚠️ anti-fit | Decap is git-backed-markdown; not designed for WP backend. Possible via headless WP + Decap to manage markdown alongside, but split-source-of-truth is anti-pattern |
| Payload | ⚠️ anti-fit | Payload is its own backend; choosing both = two CMSes. Pick one |
| Strapi / Sanity / Directus / Keystone / Ghost | ⚠️ anti-fit | Same — pick one CMS |

Per-CMS deep specifics for headless usage live in `cms-adapters/{cms}.md` (Phase 4 authoring).

## Component library pairing

Phase 18 component-build pairings. WordPress block themes use `theme.json` tokens + native block patterns as primitives; the agent's component library options layer on top.

### Default — WordPress core blocks

- **Always available; agent leans on them as primitives.** Paragraph, Image, Columns, Button, Group, Gallery, Heading, List, Quote, Code, Cover, Media-and-Text, Embed (oEmbed for YouTube/Vimeo/etc.), Spacer, Separator, Navigation, Site-Logo, Site-Title, Site-Tagline, Query Loop.
- Agent composes pages from these + the custom blocks (per `sections.yaml`).

### Custom Gutenberg blocks (the agent-written layer)

- **One custom block per section type from `sections.yaml`** (matches phase-18 component-build doctrine).
- Scaffolded via `@wordpress/create-block` (verified context7 `/websites/developer_wordpress_block-editor` 2026-05-20):
  ```bash
  npx @wordpress/create-block@latest hero-block --variant=dynamic
  ```
  Generates `block.json` (apiVersion 3) + `render.php` + `edit.tsx` + `style.scss` + `editor.scss`.
- Block plugin lives at `wp-content/plugins/{slug}-blocks/`. Agent's first commit adds the plugin; subsequent component INSTs add one folder per block.

### Tailwind + DaisyUI option (per BUILD-strategy.md line 176 — paired with this Captain)

Block CSS can use **Tailwind v4 + DaisyUI** as the styling layer. DaisyUI is pure-CSS Tailwind plugin (no JS), works in any WordPress theme that has Tailwind in the build chain. Recommended when:

- User wants the 88%-fewer-class-names DaisyUI ergonomic + the 35+ theme palettes as a starting point;
- Custom blocks need rich pre-styled UI (buttons, cards, alerts, navbars, modals) without writing every utility class;
- User accepts the per-block Tailwind build (PostCSS + `@wordpress/scripts` integration via `wp-scripts build`).

Per `Workstreams/website-builder/components/DESIGN-components-tailwind.md`, the DaisyUI custom theme accepts `oklch()` colors directly — `brand.yaml.tokens` map cleanly. context7 ID at phase 17/18: `/saadeghi/daisyui` for current setup syntax; `/tailwindlabs/tailwindcss.com` for Tailwind v4 config.

**Trade-off:** mixing DaisyUI classes inside Gutenberg blocks adds a Tailwind build step the user didn't have before. For muggle-budget WP sites where simple theme.json-styled blocks suffice, skip DaisyUI; theme.json + custom CSS in `style.css` is enough.

### Alternative addon block libraries

- **GenerateBlocks** — popular addon block library; lightweight; integrates cleanly with `theme.json`.
- **Kadence Blocks** — heavier; richer functionality. Pick when user picks a Kadence-paired theme.
- **Stackable, Otter, Spectra** — alternative block libraries. Pick by user preference / phase-12 research.

### Page-builder territory (when user explicitly picks at phase 12)

Each builder has its own widget/module library. When user picks one at phase 12, the agent's component recipe shifts to that builder's primitives:

- **Elementor** — its own widgets + theme builder; agent writes Elementor templates JSON.
- **Divi** — its own modules + Divi Builder; agent writes Divi library JSON.
- **Beaver Builder** — its own modules; agent writes Beaver row templates.

Lock-in trade-off flagged at phase 12. Phase 18 component-build doctrine changes to the chosen builder's pattern.

### Cross-reference

- `skills/wb-component-build/references/per-stack-codegen.md#wordpress` — phase-18 codegen patterns + per-block scaffold flow + theme.json token-mapping recipe (the read-only Phase-2.B anchor).
- `Workstreams/website-builder/components/DESIGN-components-tailwind.md` — DaisyUI + Tailwind UI + Park UI selection logic.

## Deploy

WordPress is unique among the three Phase-3 MVP stacks: **hosting is a real user-decision branch**, separate from the CMS choice. The user picks where WordPress runs; the agent walks them through trade-offs. The CMS decision (§8 above — WordPress core, ACF addon, etc.) is orthogonal to where the site is hosted.

### Hosting decision (separate from CMS choice)

The five hosting branches. Picked at phase 11 alongside the stack decision (since hosting affects plugin/theme freedom). Hosting is **not** picked at phase 12 — that's CMS only.

### Managed-WP hosts (Kinsta / WP Engine / SiteGround / etc.)

Recommended default for muggle users. The host handles updates, backups, SSL, server-tuning. User pays a monthly fee; in return gets less operational burden.

- **Kinsta** — premium tier; Google Cloud infra; strong dev tooling (built-in git deploy, staging, daily backups, SSH access). Trade-off: priciest of the muggle-managed hosts.
- **WP Engine** — premium peer to Kinsta; longer-established; strong support.
- **SiteGround** — mid-tier; great for first WP site; cheaper than Kinsta/WP Engine; smaller plugin ecosystem freedom (some plugins restricted on shared plans).
- **Cloudways** — cloud-agnostic managed-WP layer (you pick the underlying DigitalOcean / AWS / Linode / Vultr droplet; Cloudways manages the stack on top). Power-user-friendly while still managed.
- **Bluehost, Hostinger, DreamHost** — budget shared-WP. Cheapest entry; lower performance ceilings; agent surfaces trade-offs.

Deploy mechanism: git push to host's integration OR SFTP/SSH. Most managed hosts ship CI-integrated deploy (git-push triggers atomic deploy). Agent uses host's native flow when present.

### Self-hosted (VPS / cloud)

User runs WordPress on a VPS or cloud instance. Maximum control, lowest cost at scale, most operational burden.

- **DigitalOcean droplet + LAMP/LEMP stack** — classic; cheap; user provisions OS + DB + nginx/Apache + PHP-FPM themselves OR uses DigitalOcean's WordPress one-click image.
- **Linode, Vultr, Hetzner** — DigitalOcean peers; similar trade-offs.
- **AWS Lightsail** — Amazon's beginner-VPS offering; WP one-click image.
- **Bare-metal / OVH / similar** — for users with operational chops + cost-at-scale concerns.

Deploy mechanism: SSH + git pull OR SFTP. Agent surfaces the manual-update burden (security patches, plugin/core updates, backup automation are the user's responsibility).

### WordPress.com (managed but constrained)

Automattic's own managed-WP offering at `wordpress.com`. The simplest path; comes with significant constraints on lower plans.

- **Free / Personal / Premium plans:** can't install custom themes or arbitrary plugins. **Agent surfaces at phase 11 that these plans are NOT compatible with the website-builder's custom-theme + custom-block approach.**
- **Business plan ($25/mo as of 2026-05):** custom themes + plugins allowed. Minimum viable WordPress.com tier for this stack.
- **Commerce plan ($45/mo):** Business + WooCommerce-ready.
- **Enterprise (WP VIP):** for very large sites; rarely the muggle's target.

Agent recommends Business+ minimum if WordPress.com is the user's choice. Surfaces the cost premium vs equivalent managed-WP at Kinsta/SiteGround.

### Containerized (Bedrock / Trellis / wp-env for local)

For power-user setups with reproducible infrastructure:

- **Bedrock** (Roots) — modern WP boilerplate (Composer, dotenv, structured directory layout, isolated wp-content).
- **Trellis** (Roots) — Ansible-based WP server provisioning + deploy pipeline.
- **wp-env** — official Docker-backed local dev environment (already covered in §2 Auth + setup).
- **Custom Docker compose** — user runs their own WP container against a separate MySQL container.

Agent recommends Bedrock for users coming from modern PHP backgrounds; trade-off is the additional learning curve vs vanilla WP.

### DNS + SSL

Cloudflare MCP (when available) for DNS configuration; host-provided SSL (Let's Encrypt automated by every modern managed-WP host; agent verifies at phase 28). For self-hosted, agent walks user through `certbot` setup or recommends Cloudflare's free SSL proxy.

### Analytics injection

Agent installs **MonsterInsights plugin** (GA4 integration) OR injects directly via theme's `functions.php` with the `wp_head` hook (lighter-weight; avoids the plugin). Server-side analytics (**Plausible self-hosted**, **Matomo**) supported when user has privacy-first requirements.

### Performance budget

WordPress requires explicit perf tuning more than the static stacks. Agent installs:

- **Caching:** WP Rocket (paid; recommended) OR W3 Total Cache (free) OR LiteSpeed Cache (when on LiteSpeed-equipped host).
- **Image optimization:** ShortPixel / Imagify / Smush.
- **CDN:** Cloudflare (free or paid tier) configured at phase 28.

Agent runs Lighthouse at phase 22 + tunes; targets **80+** Performance score for managed-WP-hosted sites. (Static stacks routinely score 95+; WP's PHP-bootstrap floor caps the achievable; surface honestly at phase 11.)

### Phase 29 deploy verification

Playwright walks the live deployed site per `extraction/playwright-walk.md` (verification mode, not extraction). Checks: every page renders, no console errors, hreflang correct, language switcher works, contact form submits, checkout flow works (when transactional). RSS + sitemap + robots.txt resolve.

## Post-launch maintenance pattern

Per locked decision 37 (launch-once phases 31-34 vs ongoing post-launch maintainer template). WordPress-specific adaptations:

### Content edits — `/wp-admin` is the user's loop

- User edits in `/wp-admin` directly (the canonical WP loop). Maintainer template does NOT automatically mirror back to `.website-builder/content/` (WP is the source of truth post-launch).
- Exception: user explicitly invokes phase 6.5 with the live site URL → agent re-walks via REST + Playwright → updates `.website-builder/content/` from production state.

### Component edits — agent edits theme + block plugin

- Agent edits `wp-content/plugins/{slug}-blocks/blocks/{name}/` (`block.json`, `render.php`, `edit.tsx`) locally.
- Build via `wp-scripts build` (when using Tailwind/DaisyUI option) OR directly.
- Deploy via git push to host integration OR rsync/SSH.
- User sees the change after the next page render (no editor refresh needed unless block edit script changed).

### Style token updates — agent edits theme.json

- Agent edits `wp-content/themes/{slug}/theme.json` `settings.*` and `styles.*`.
- WordPress auto-regenerates `--wp--preset--*` CSS custom properties on next render.
- For Tailwind/DaisyUI option: agent regenerates the DaisyUI custom theme + Tailwind config + rebuilds.

### Plugin + theme + core updates

- Maintainer template documents the update cadence: **weekly recommended** for plugins/themes; **immediately for security releases** of core.
- Staging-test-then-prod pattern: update on staging (host-provided OR `wp-env` locally) → smoke-test → promote to prod.
- Agent provides update-check script: `wp-cli plugin list --update=available` + `wp-cli core check-update`.

### Backups

- **UpdraftPlus** (free + Pro), **BackupBuddy** (paid), or **host-provided** backups (Kinsta / WP Engine / SiteGround ship daily backups; user verifies retention).
- Maintainer template surfaces backup verification monthly — restore a backup to staging, confirm it works.

### Security

- **Wordfence**, **Sucuri**, or **iThemes Security** plugins for firewall + malware-scan.
- Maintainer template walks user through monthly security-review checklist (login attempts, suspicious users, file-integrity scan, plugin-vulnerability scan).

### Image-gen iteration (per `consumers/image-gen.md`)

- Agent generates images (Gemini, Imagen, etc.) → uploads to WP Media Library via REST → references in pages/blocks.
- Maintainer template documents how the user can iterate on hero images post-launch (paste new image URL or new image into a Gutenberg block; agent re-uploads + swaps `featured_media` ids).

### Plugin choice changes (structural pivot)

Mid-project plugin swap is **structural pivot per locked decision 34** — e.g., switching i18n from Polylang → WPML, or commerce from WooCommerce → EDD. Agent forces phase restart of relevant downstream phases (12 / 22 / 24a/b/c when applicable).

### Long-term description (one sentence)

*"Edit content in /wp-admin like any WordPress site; let the agent rebuild + redeploy the theme + block plugin when the design or component shapes change; expect monthly plugin/core updates that the maintainer template walks you through."*

## Limitations + escape hatches

### Hard limitations (the stack's structural constraints)

- **Paid hosting required for serious sites.** Free wordpress.com plans can't run custom themes/blocks; the agent's approach requires Business+ on .com OR any self-hosted/managed-WP option. Surface this LOUDLY at phase 11 — *"WordPress is the muggle-friendly stack, but the hosting bill is the ticket of admission."*
- **PHP runtime required.** Can't be statically exported (without going headless). Each request goes through WP's PHP bootstrap; caching mitigates, never matches static-export latency.
- **Plugin sprawl risk.** WordPress's strength (60,000+ plugins) is also its risk surface — each plugin adds maintenance burden, attack surface, performance cost. Maintainer template enforces plugin discipline (audit quarterly; uninstall unused).
- **PHP version coupling.** WP runs on PHP 8.0+; older hosts may pin 7.4 or 8.0. Modern blocks + `@wordpress/scripts` need 8.1+. Agent verifies at phase 11.

### Soft limitations (awkward but workable)

- **Compose finished pages programmatically with high visual fidelity.** REST can create pages + insert block markup, but Gutenberg's block content is serialized HTML with comment-based delimiters — getting complex layouts exactly right via API requires the agent to write the block markup precisely. Agent uses **block patterns** (auto-registered from `patterns/*.php` files via header comments — verified developer.wordpress.org 2026-05-20) as composable units.
- **Override host-level constraints.** Some managed-WP hosts disable `eval()` / file-write / specific plugins. Agent surfaces during phase 11 host research; works within constraints.
- **Visual-canvas-after-launch is awkward.** Unlike Framer, WordPress's block editor is the canvas — works fine, but if the user wants Webflow/Framer-style direct-manipulation editing, Gutenberg is a step down. Surface the trade-off at phase 11.
- **PHP processing model.** Each page request hits the full bootstrap (mitigated by caching). Surface perf trade-offs vs static stacks at phase 11.

### Failure modes

| Failure | Cause | Recovery |
|---|---|---|
| REST returns 401 / 403 on a write | Application Password expired / revoked | Regenerate AP at `/wp-admin/users/profile.php`; refresh `WP_APP_PASSWORD` env |
| REST returns 429 | Rate-limited by host (Kinsta + WP Engine throttle aggressive write loops) | Backoff; switch to wp-cli over SSH for bulk operations |
| Block doesn't render in editor | `block.json` schema invalid OR `editorScript` path wrong | Validate against `https://schemas.wp.org/trunk/block.json`; verify file paths relative to `block.json` |
| theme.json changes don't appear | Block editor caches theme.json | Toggle theme in `/wp-admin/themes.php` (deactivate + reactivate) OR run `wp transient delete --all` via SSH |
| Polylang/WPML serves wrong language | Caching plugin (WP Rocket, W3 Total Cache) doesn't vary cache by locale | Configure cache plugin's "exclude per language" OR clear cache on locale change |
| Custom block doesn't show in inserter | Plugin not activated OR block category invalid | Activate at `/wp-admin/plugins.php`; verify `block.json` `"category"` is in the registered list |
| `wp-env` start fails | Port collision (8888 in use) | `WP_ENV_PORT=8889 wp-env start` |
| Migration recipe content has unicode glitch | Some hosts run MySQL with `latin1` charset | Convert DB to `utf8mb4` via WP-CLI: `wp db query "ALTER DATABASE ..."` |
| Page builder content gone after switching to Gutenberg | User picked Elementor/Divi at phase 12, then changed mind | Mid-project pivot per decision 34 — force phase restart |
| Performance budget missed | Plugin sprawl / no caching / unoptimized images | Audit at phase 22; install missing perf plugins; reduce plugin count |

### Escape hatches

- **User wants modern frontend with WP backend:** **headless WP** + Next.js/Astro frontend. Agent treats as Next.js/Astro project per `adapters/stack-nextjs.md` with WP as CMS layer. Re-opens phase 11.
- **User outgrows shared hosting:** migrate to managed-WP host (Kinsta / WP Engine / SiteGround) or VPS. Agent walks through. Backup + DNS + SSL handled per host's migration tooling.
- **User wants to leave WordPress entirely:** export content via WP REST or `wp-cli` export; ingest via phase 6.5; agent rebuilds in target stack. Theme + blocks don't migrate (different framework); only content + tokens carry.
- **User picks a page builder mid-project (Elementor / Divi / Beaver Builder):** structural pivot per decision 34. Phase 12 + phase 18 restart with the builder's primitives.

## context7 lookups for this stack

The agent invokes context7 at these phases (per `cross-cutting/DESIGN-context7-integration.md` + Lock-3 freshness pattern). Cached docs land in `.website-builder/library/docs/wordpress-*.md`; re-fetch threshold **30 days** per locked Lock-3 norm.

### Manifest

| Phase | Trigger | Library ID | Question template |
|---|---|---|---|
| 11 | Stack decision — confirm WordPress 6.6+ current surface | `/wp-api/docs` | "current REST API endpoints + Application Passwords + custom post type registration" |
| 11 | Stack decision — confirm Block Editor + FSE state | `/websites/developer_wordpress_block-editor` | "Full Site Editing state, theme.json version 3, block themes vs classic themes" |
| 12 | CMS decision (Polylang vs WPML) | `/wp-api/docs` + WebFetch `https://polylang.pro/doc/` | "current i18n plugin capabilities + REST integration" |
| 12 | If `transactional=true` — WooCommerce confirm | `/woocommerce/woocommerce-rest-api-docs` | "current WooCommerce REST API + Stripe-for-WC integration" |
| 17 | Design system — theme.json schema | `/websites/developer_wordpress_block-editor` | "theme.json version 3 settings.color/typography/spacing/shadow schema + fluid typography + style variations" |
| 18 | Component build — block.json + create-block | `/websites/developer_wordpress_block-editor` | "block.json apiVersion 3 schema + @wordpress/create-block CLI variant=dynamic + render.php + edit.tsx" |
| 18 | If DaisyUI option — Tailwind v4 + DaisyUI | `/tailwindlabs/tailwindcss.com` + `/saadeghi/daisyui` | "Tailwind v4 + DaisyUI custom theme with oklch() colors + WordPress build chain" |
| 24a | Commerce (if transactional) — WooCommerce | `/woocommerce/woocommerce-rest-api-docs` | "product create + Stripe gateway + tax/shipping configuration via REST" |
| 28-30 | Deploy — host integration + Cloudflare | (verify per host) + Cloudflare context7 | "managed-WP git deploy + DNS + SSL + Cloudflare integration" |

### WebFetch fallback (when context7 coverage is thin)

WordPress + Block Editor coverage on context7 is moderate-to-thin in places. WebFetch the canonical sources at these phases (per Lock 3 #3):

- **Phase 17 — theme.json v3 schema:** `https://developer.wordpress.org/themes/global-settings-and-styles/` + `https://developer.wordpress.org/themes/global-settings-and-styles/settings/` + `https://developer.wordpress.org/block-editor/reference-guides/theme-json-reference/theme-json-living/` — the living reference is authoritative.
- **Phase 18 — Block API v3 + `block.json`:** `https://developer.wordpress.org/block-editor/reference-guides/block-api/block-metadata/` + `https://developer.wordpress.org/block-editor/getting-started/create-block/` + `https://developer.wordpress.org/block-editor/getting-started/fundamentals/`.
- **Phase 18 — block patterns auto-registration:** `https://developer.wordpress.org/themes/patterns/registering-patterns/` — the file-header-based auto-registration is current 2026 standard.
- **Phase 24a — WooCommerce REST:** `https://woocommerce.github.io/woocommerce-rest-api-docs/`.

Cache fetched docs to `.website-builder/library/docs/wordpress-{surface}.md` (e.g. `wordpress-theme-json.md`, `wordpress-block-api.md`, `wordpress-rest.md`, `wordpress-woocommerce.md`). Re-fetch threshold 30 days; freshness flag on cache files.

### Verified-current notes (freshness 2026-05-20)

- **theme.json schema:** **version 3** (current living reference, WordPress 6.6+). Earlier "introduction" page on developer.wordpress.org returns version 2 (last updated Dec 2023; pre-v3); the [living reference](https://developer.wordpress.org/block-editor/reference-guides/theme-json-reference/theme-json-living/) is authoritative. Use `"version": 3` + `"$schema": "https://schemas.wp.org/trunk/theme.json"`.
- **Block API:** **apiVersion 3** (introduced WordPress 6.3; current as of 6.6+). Older blocks at `apiVersion: 2` still supported; new blocks should be 3.
- **Block patterns auto-registration:** PHP files in theme's `patterns/` directory with file-header comments (`Title:`, `Slug:`, `Categories:`, etc.) are auto-registered — no `register_block_pattern()` call needed for the file-based path. Older `register_block_pattern()` API still works for conditional registration.
- **Application Passwords:** built-in since WordPress 5.6 (mature; the canonical agent auth path).
- **`@wordpress/create-block`:** ships `--variant=dynamic` flag for `render.php`-rendered blocks; `--variant=static` (default) for save-serialized blocks.
- **Full Site Editing:** standard as of WordPress 6.0+; the 2026 default for new themes (not experimental, not optional).

## References

### Foundation design docs (vault-root-relative)

- [VISION-website-builder.md](Workstreams/website-builder/VISION-website-builder.md)
- [BUILD-strategy.md](Workstreams/website-builder/BUILD-strategy.md) — Phase 3 DoD + dispatch model (lines 164-184)
- [DESIGN-architecture.md](Workstreams/website-builder/foundation/DESIGN-architecture.md) — plugin directory layout + skill / agent / hook surfaces (lines 160-260)
- [DESIGN-content-layers.md](Workstreams/website-builder/foundation/DESIGN-content-layers.md) — the 5-layer content stack the §4 table maps
- [DESIGN-i18n.md](Workstreams/website-builder/foundation/DESIGN-i18n.md) — i18n model the §5 section consumes
- [DESIGN-ingestion-and-extraction.md](Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md) — phase 6.5 mechanism + extractor pairing
- [DESIGN-phase-contracts.md](Workstreams/website-builder/foundation/DESIGN-phase-contracts.md) — phase contracts the adapter binds against
- [DESIGN-project-scaffold.md](Workstreams/website-builder/foundation/DESIGN-project-scaffold.md) — `.website-builder/` directory layout + migration recipes
- [DESIGN-stack-wordpress.md](Workstreams/website-builder/stacks/DESIGN-stack-wordpress.md) — primary source (this adapter is the runtime extraction)
- [DESIGN-components-tailwind.md](Workstreams/website-builder/components/DESIGN-components-tailwind.md) — DaisyUI selection logic + Tailwind v4 setup
- [DESIGN-ecosystem-catalog.md](Workstreams/website-builder/foundation/DESIGN-ecosystem-catalog.md) — full component-library tier list

### Cross-stack plugin anchors (read-only — Captain H references; does not modify)

- `adapters/README.md` — the canonical 14-section schema this file follows
- `i18n/strings-schema.md` — stack-agnostic CDJSON contract
- `i18n/rtl.md` — stack-agnostic RTL discipline
- `i18n/language-switcher.md` — Overview + Required behavior + `### WordPress` H3 (authored by this Captain)
- `i18n/hreflang.md` — Overview + Required behavior + `### WordPress` H3 (authored by this Captain)
- `extraction/playwright-walk.md` — Playwright walker (phase 6.5)
- `extraction/ai-output.md` — AI-output parser (phase 6.5 + phase-18 round-trip)
- `extraction/stitch.md` — Stitch design-token extractor (URL mode)
- `extraction/divmagic.md` — element-precision extractor
- `extraction/figma-design-to-json.md` — Figma plugin handler
- `handoff-spec/component-request-v1.md` — brief contract; this adapter's `output_format` defaults populate per §4 row 5
- `handoff-spec/component-output-v1.md` — return contract; AI-output parser ingests
- `skills/wb-architecture/SKILL.md` + `references/stack-matrix.md` — phase 11 consumer of this adapter
- `skills/wb-component-build/references/per-stack-codegen.md#wordpress` — phase 18 consumer of this adapter

### External — WordPress core

- WordPress: https://wordpress.org
- WordPress Developer Resources: https://developer.wordpress.org
- Block Editor Handbook: https://developer.wordpress.org/block-editor/
- theme.json Living Reference: https://developer.wordpress.org/block-editor/reference-guides/theme-json-reference/theme-json-living/ — authoritative for version 3
- theme.json Settings + Styles overview: https://developer.wordpress.org/themes/global-settings-and-styles/
- theme.json Settings reference: https://developer.wordpress.org/themes/global-settings-and-styles/settings/
- Block API metadata (block.json): https://developer.wordpress.org/block-editor/reference-guides/block-api/block-metadata/
- `@wordpress/create-block`: https://developer.wordpress.org/block-editor/getting-started/create-block/
- Block patterns registration: https://developer.wordpress.org/themes/patterns/registering-patterns/
- WP REST API Handbook: https://developer.wordpress.org/rest-api/
- WP-CLI: https://wp-cli.org
- Schema URL: `https://schemas.wp.org/trunk/theme.json` + `https://schemas.wp.org/trunk/block.json`

### External — commerce + i18n + page-builders

- WooCommerce: https://woocommerce.com
- WooCommerce REST API: https://woocommerce.github.io/woocommerce-rest-api-docs/
- WPML: https://wpml.org
- Polylang: https://polylang.pro
- TranslatePress: https://translatepress.com
- Elementor: https://elementor.com
- Divi: https://www.elegantthemes.com/gallery/divi/
- Beaver Builder: https://www.wpbeaverbuilder.com

### External — managed hosts

- Kinsta: https://kinsta.com
- WP Engine: https://wpengine.com
- SiteGround: https://www.siteground.com
- Cloudways: https://www.cloudways.com
- WordPress.com plans: https://wordpress.com/pricing/

### External — power-user infra

- Bedrock (Roots): https://roots.io/bedrock/
- Trellis (Roots): https://roots.io/trellis/
- wp-env: https://developer.wordpress.org/block-editor/reference-guides/packages/packages-env/
- LocalWP: https://localwp.com
