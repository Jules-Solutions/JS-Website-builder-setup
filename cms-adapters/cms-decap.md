# CMS adapter — Decap CMS

> Runtime artifact the website-builder agent loads when `project.yaml.cms` is `decap`. The `wb-architecture` skill consumes this at phase 12 (CMS decision); `wb-component-build` at phase 18 (component build); the phase-6.5 re-runnable ingestion at any project lifecycle point. Authored against the canonical 12-section schema in `cms-adapters/README.md`.
>
> Primary design-doc source: `Workstreams/website-builder/cms/DESIGN-cms-decap.md` (~451 lines). i18n source: `Workstreams/website-builder/foundation/DESIGN-i18n.md`. Content-layer source: `Workstreams/website-builder/foundation/DESIGN-content-layers.md`. Phase contracts: `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md`.

## Mental model

### Identity

- **CMS:** Decap CMS (formerly Netlify CMS) — git-backed, single-page-app admin UI that commits markdown + YAML directly to the user's repo via OAuth
- **Version baseline:** v3.12.x (verified npm + context7 2026-05-20 — v3.12.2 latest, Plate-based richtext widget added April 2026; markdown widget remains but is deprecated since April 2026; agent's default fixture still uses the markdown widget for compatibility — see `### Common pitfalls`)
- **Canonical context7 ID:** `/websites/decapcms` (preferred — benchmark 93.5, High reputation, 299 snippets) — fall back to `/decaporg/decap-cms` (benchmark 50.5, 219 snippets) if the preferred coverage misses a topic; `/withastro/docs` for Astro pairing; `/sveltia/sveltia-cms` if the user pivots to the Sveltia fork
- **Freshness-check requirement:** the agent invokes context7 at phase 12 / 17 / 18 / 22 to confirm the current surface — **Decap's surface evolves; the 2023-2025 maintenance-mode → 2026 revitalization shift is the canonical reason this check is non-optional**. Cached docs at `.website-builder/library/docs/decap-cms-*.md` re-fetch on the 30-day threshold per `skills/wb-architecture/references/context7-protocol.md` (when that skill ships).

Decap thinks in three concepts:

1. **Collections** — sets of content files. Two flavors: `folder` collections (a directory, one file per item — e.g., `src/content/blog/*.md`) and `file` collections (a fixed set of named files — e.g., `src/content/_data/site.yaml`). Each collection has `fields` (the form schema editors fill in).
2. **Fields** — `string`, `text`, `markdown`, `image`, `file`, `boolean`, `number`, `datetime`, `select`, `relation`, `list`, `object`. The `list` + `widget: types` combination (typed union) approximates the "blocks" pattern from richer CMSes.
3. **The git workflow** — every save in admin is a commit. Two modes: `simple` (commits direct to `main`) and `editorial_workflow` (commits to a draft branch, opens a PR, editors merge to publish).

The mental shift: **the repo IS the database**. There's no separate datastore; the user's git history IS the content history. Every revert is `git revert`. Every diff is `git diff`. Every backup is the repo. Decap is a form that produces git commits.

The other shift: **Decap runs in the browser only**. It's static HTML + JS served from the user's site (or a separate static host). The backend is GitHub's REST API, talked to via OAuth. There's no Decap server to deploy, scale, or back up.

This makes Decap the **lightest possible CMS option with a real admin UI**. The cost: everything goes through git — slow saves (one commit per save), no real-time multi-editor, no rich admin UX features that depend on a backend.

**The muggle needs to understand:** the admin lives at `/admin` on their own site. They log in with their GitHub (or GitLab / Bitbucket / Gitea) account. Every save commits to their repo. They see edits in `git log`. Their content is portable forever because it's just markdown + YAML in their repo.

## When to pick this CMS

### Pick Decap when

- **Stack is a static site generator** (Astro / Hugo / Jekyll / Eleventy / Gatsby / Next.js with static export). Decap is designed for this — the cross-CMS × stack table in `cms-adapters/README.md` flags Decap + Astro / Hugo / Jekyll / Eleventy as `Native`.
- **The user is the only editor** or the editor pool is tiny (1-3 people who don't simultaneously edit the same file).
- **The site lives in a public or accessible git repo** the user already controls. Decap reads/writes via the git host's API; no repo, no Decap.
- **Content volume is low-to-medium** — dozens to hundreds of content items, not thousands. Decap loads the full collection list into the browser; performance degrades past a few thousand items.
- **The user values "no third-party data store" / "all my content is in git"** — auditable, portable, never locked-in.
- **Cost matters** — Decap itself is free + self-hosted (no Decap subscription); only host cost (GitHub free tier + Netlify/Vercel/Cloudflare Pages free tier covers most muggle sites).
- **Edit cadence is low** — daily or weekly publishes, not minute-by-minute. (One commit per save means save latency is ~1-3 seconds.)
- **The content shape is markdown + frontmatter + a sprinkle of structured YAML** — exactly what static site generators eat.
- **Sister's "Still Humans" canonical-fit test (per `DESIGN-cms-decap.md` line 44)** — a writer-driven blog with weekly cadence is the canonical Decap fit.

### Don't pick Decap when

- **Real-time multi-editor required.** Two editors saving the same file produces a git conflict. No locks, no presence.
- **Stack is dynamic** (Payload / Strapi territory — Next.js with SSR, Express backends, etc.). Decap can technically work but you're fighting the design.
- **Editor count > 5 with frequent simultaneous edits.** Use Strapi / Sanity / Payload instead.
- **Content volume is in the thousands.** Decap's UI gets slow.
- **You need fine-grained role-based access control.** Decap's auth is "you have repo write access or you don't." (Workaround: editorial workflow + branch-protection rules — see `## Limitations + escape hatches`.)
- **You need an API for content** (mobile app, multiple frontends). Decap doesn't expose an API; it just commits files. (If user later needs an API, that's a phase-12 restart per Decision 34.)
- **The repo is private and the editors don't have git accounts.** OAuth requires git-host accounts. Workaround (Git Gateway via Netlify Identity) exists but adds Netlify dependency.

## Auth + setup

**Account:** the user already has (or creates) a git host account: GitHub (default and best-supported), GitLab, Bitbucket, or Gitea / Forgejo. The git host IS the auth provider — there's no separate Decap account.

**Local dev:** Decap is a static page; there's no local server. The admin loads from `/admin/` (Astro / Next.js static / Hugo `static/admin/`) when the dev server serves it. For local dev WITHOUT real OAuth, use the `test-repo` backend:

```yaml
backend:
  name: test-repo
```

The agent uses this only for the Phase 4 test fixture; real projects use GitHub.

**MCP / tooling (negative findings):**

- **Decap CMS MCP** — no MCP currently exists (WebSearch verified 2026-05-20; see also `adapters/stack-nextjs.md` §"MCP servers" line 203 for the cross-reference). Decap is git-backed; CMS operations ARE git operations. **The agent does NOT keep searching for a Decap MCP at runtime — there isn't one.**
- **Fallback (canonical path):** the user's GitHub MCP (`github/github-mcp-server`) covers commit auditing, branch-protection setup, OAuth-app creation, and editorial-workflow PR observation. The `/admin` UI on the deployed site covers content authoring directly. `gh` CLI covers anything the GitHub MCP doesn't.
- **Sveltia CMS MCP** — no MCP exists (WebSearch verified 2026-05-20). Same reason as Decap: git-backed, no service surface.
- **Static CMS MCP** — no MCP exists; project archived (see `## Limitations + escape hatches`).
- **Git Gateway / Netlify Identity MCP** — no Netlify-specific MCP exists for these; the Netlify MCP (where it exists) covers deploy hooks but not Identity flows. Fallback: Netlify dashboard + `netlify` CLI.

**OAuth provider setup (real-project path):**

The user creates an OAuth App on the git host (GitHub default). For GitHub:

1. github.com → Settings → Developer settings → OAuth Apps → New OAuth App
2. **Homepage URL:** the site's production URL (e.g. `https://example.com`)
3. **Authorization callback URL:** depends on Decap's hosted-OAuth-proxy choice. Three common patterns:
   - **Netlify-hosted (legacy default):** `https://api.netlify.com/auth/done` — works without configuring a callback proxy, requires the site to be hosted on Netlify OR configured for Git Gateway
   - **Self-hosted OAuth proxy:** the user deploys a tiny serverless function (Netlify Function / Vercel Edge / Cloudflare Worker) per `https://decapcms.org/docs/external-oauth-clients/` — agent generates this at phase 28 if the host isn't Netlify
   - **OAuth-client-id-and-secret pasted into `config.yml`:** never — that exposes credentials in static JS. Don't do this.
4. **Client ID** is public (lives in `config.yml`); **Client Secret** is read by the OAuth proxy only — secret per `secrets-conventions.md`.

```yaml
# public/admin/config.yml (Astro convention)
backend:
  name: github
  repo: jules-solutions/example-site
  branch: main
  base_url: https://oauth.example.com   # only when self-hosting OAuth proxy
  auth_endpoint: auth                    # callback path the proxy listens on
```

Per `secrets-conventions.md`: the GitHub OAuth Client Secret lives in 1Password (`op://shared/github-oauth-decap/secret`); the OAuth-proxy serverless function reads it from env at request time. Never committed.

**Git Gateway (the workaround for non-git-account editors)** — when the user has editors who don't have GitHub accounts, the canonical workaround is Netlify Identity + Git Gateway:

1. Site hosted on Netlify (sets up Identity service)
2. Identity → Services → Git Gateway → Enable
3. `config.yml` uses `backend: { name: git-gateway, branch: main }` instead of `name: github`
4. Editors invited via Netlify Identity (email-based; no GitHub account needed)
5. Editors authenticate via Netlify Identity; Git Gateway proxies commits to GitHub with a service token

Trade-off: locks the user to Netlify-the-host. The agent surfaces this at phase 12 if the user's editor list lacks git accounts.

### CRUD vocabulary

For Decap, the editor's CRUD verbs translate to admin-UI actions that compile to git operations under the hood. The agent doesn't expose the git layer to the editor — that's Decap's whole point — but the agent knows the mapping for debugging, audit, and scripting:

| Universal verb | Decap-native concept | Git operation under the hood |
|---|---|---|
| **Create page** | Admin → collection → "New X" → fill form → save | `git commit` to `main` (simple workflow) OR draft branch + PR (editorial workflow) |
| **Edit page** | Admin → collection → click item → form → save | New `git commit` (simple) OR commit on the draft branch (editorial) |
| **Publish page** | Simple: automatic on save. Editorial: "Set status: ready" → "Publish" | Simple: nothing extra. Editorial: PR merges to `main`, draft branch deleted |
| **Unpublish page** | Delete in admin OR set `draft: true` in frontmatter | `git commit` removing the file OR updating the frontmatter |
| **Schedule publish** | NOT natively supported — Decap doesn't have a built-in scheduler | Workaround: editorial workflow + manual merge at the scheduled time; or merge to a `scheduled/` branch + cron-triggered build pipeline |
| **View revisions** | Admin shows last save author (with editorial workflow). Full history via the git host. | `git log <file>` or GitHub UI → file → History |
| **Bulk edit** | Not natively supported in the admin UI | Direct edit in repo via PR — bypasses Decap; agent surfaces this is acceptable |
| **Upload image / asset** | Admin → media library → upload | `git commit` placing the file in `media_folder` (configured in `config.yml`) |

The agent uses this mapping at phase 12 to teach muggles what "saving a page" actually does — a git commit happens automatically; they don't see git, but their repo grows on every save.

## Authoring patterns

### Pattern: Folder collection for a blog

The canonical Decap pattern — a directory of files, one per item.

```yaml
# public/admin/config.yml (Astro convention)
backend:
  name: github
  repo: user/their-repo
  branch: main

media_folder: "src/assets/uploads"
public_folder: "/_astro/uploads"

collections:
  - name: posts
    label: "Blog Posts"
    folder: "src/content/blog"
    create: true
    slug: "{{year}}-{{month}}-{{day}}-{{slug}}"
    fields:
      - { name: title, label: Title, widget: string }
      - { name: date, label: Date, widget: datetime }
      - { name: author, label: Author, widget: relation, collection: authors, value_field: slug, search_fields: [name] }
      - { name: excerpt, label: Excerpt, widget: text }
      - { name: featured_image, label: "Featured Image", widget: image, required: false }
      - { name: tags, label: Tags, widget: list, default: [] }
      - { name: body, label: Body, widget: markdown }
```

Editors see a "Blog Posts" tab in admin → "New Post" → form opens → save → Decap commits `src/content/blog/2026-05-20-launch.md` with frontmatter + markdown body. The static site generator picks it up on next build.

### Pattern: File collection for site settings

A fixed set of named files (not directory-shaped).

```yaml
collections:
  - name: settings
    label: "Site Settings"
    files:
      - name: general
        label: "General"
        file: "src/content/_data/site.yaml"
        fields:
          - { name: site_name, label: "Site Name", widget: string }
          - { name: tagline, label: Tagline, widget: string }
          - { name: logo, label: Logo, widget: image }
          - name: social
            label: Social
            widget: list
            fields:
              - { name: platform, widget: select, options: [twitter, linkedin, instagram, github] }
              - { name: url, widget: string }
```

Editors see "Site Settings → General" → form opens → save commits `src/content/_data/site.yaml`. The static site generator reads this at build time (Astro: `import siteData from '../content/_data/site.yaml'`; Hugo: `site.Data.site.site_name`).

### Pattern: Approximating Blocks via `list` + `types`

Decap doesn't have a native "Blocks" field, but `list` with `types` (typed union) gets close. Per `cms-adapters/README.md` §"Cross-CMS × stack compatibility anchor", this is how Decap maps L2 sections.yaml → CMS-native concept.

```yaml
- name: pages
  label: Pages
  folder: "src/content/pages"
  create: true
  fields:
    - { name: title, widget: string }
    - { name: slug, widget: string }
    - name: layout
      label: Layout
      widget: list
      types:
        - name: hero
          label: Hero
          widget: object
          summary: '{{fields.headline}}'
          fields:
            - { name: headline, widget: string }
            - { name: sub, widget: text }
            - { name: cta_label, widget: string }
            - { name: cta_href, widget: string }
            - { name: background, widget: image, required: false }
            - { name: variant, widget: select, options: [text-left, text-center, image-right] }
        - name: rich_text
          label: "Rich Text"
          widget: object
          fields:
            - { name: body, widget: markdown }
        - name: media_gallery
          label: "Media Gallery"
          widget: object
          fields:
            - name: images
              widget: list
              fields:
                - { name: src, widget: image }
                - { name: alt, widget: string }
        - name: cta
          label: CTA
          widget: object
          fields:
            - { name: headline, widget: string }
            - { name: sub, widget: text }
            - { name: button_label, widget: string }
            - { name: button_href, widget: string }
```

Editors get a "Page Layout" field where they add blocks of any type, in any order. The output is a YAML list with `type` discriminators. The frontend renders by switching on the type:

```astro
---
// Astro example — src/pages/[...slug].astro
import Hero from '@/components/sections/Hero.astro'
import RichText from '@/components/sections/RichText.astro'
import MediaGallery from '@/components/sections/MediaGallery.astro'
import CTA from '@/components/sections/CTA.astro'

const { layout } = Astro.props.frontmatter
---
{layout.map((block) => {
  if (block.type === 'hero') return <Hero {...block} />
  if (block.type === 'rich_text') return <RichText body={block.body} />
  if (block.type === 'media_gallery') return <MediaGallery images={block.images} />
  if (block.type === 'cta') return <CTA {...block} />
})}
```

The agent generates `config.yml`'s `types` list from `components.yaml` (L2 structural specs) at phase 18. When the user adds a new block at phase 18, the agent regenerates `config.yml` so the new block appears in admin.

### Pattern: Editorial workflow (drafts + PRs)

```yaml
# Top-level in config.yml, NOT indented
publish_mode: editorial_workflow
```

With this enabled, every save creates a draft branch (`cms/<collection>/<slug>`) and opens a PR. Editors see "Workflow" → list of in-progress drafts → "Set status: ready for review" → "Publish." On publish, the PR merges to `main` and the site rebuilds.

Optional: squash merges to keep `main` history clean:

```yaml
backend:
  name: github
  repo: owner/repo
  squash_merges: true
```

Useful for sites with multiple editors who want a review step. Adds friction (one commit per save → one PR per edit). Surface trade-off at phase 12.

### Pattern: Custom previews

Decap renders a default preview pane on the right when editing. Customize per-collection by registering preview templates:

```html
<!-- public/admin/index.html -->
<script src="https://unpkg.com/decap-cms@^3.1.2/dist/decap-cms.js"></script>
<script>
CMS.registerPreviewTemplate('posts', PostPreview)
function PostPreview({ entry, widgetFor }) {
  const h = window.h
  return h('div', { class: 'post' },
    h('h1', null, entry.getIn(['data', 'title'])),
    h('div', null, widgetFor('body'))
  )
}
</script>
```

For static-site-generator-shaped projects, custom previews are usually skippable — editors deploy a Netlify draft URL or use `npm run dev` locally to preview. The agent skips this by default at phase 18; mentions it as an optional upgrade.

### Common pitfalls

- **Forgetting to deploy `admin/index.html` + `admin/config.yml`.** Decap's admin IS two files in the user's static-site output. The static site generator must include them in the build output (Astro: `public/admin/`; Hugo: `static/admin/`; Jekyll: `admin/` at root; Eleventy: configured per `eleventy.config.js` passthrough).
- **OAuth setup forgotten.** Decap needs an OAuth provider (GitHub OAuth App, Netlify Identity, etc.). Phase 12 must wire this; otherwise the admin loads but can't authenticate. The Phase 4 fixture documents this gap explicitly (`schema-only-not-runtime`).
- **Image uploads landing in wrong directory.** `media_folder` (repo path where uploads are written) and `public_folder` (URL path the site uses) must align with the static site generator's conventions. Mismatch = broken images at render time. Astro: `media_folder: "src/assets/uploads"` + `public_folder: "/_astro/uploads"`. Hugo: `media_folder: "static/uploads"` + `public_folder: "/uploads"`. Jekyll: `media_folder: "assets/uploads"` + `public_folder: "/assets/uploads"`.
- **Collection schema changes breaking existing content.** Decap doesn't migrate; if you rename a field in `config.yml`, existing files still have the old field name. Manual cleanup or a migration script needed. The agent surfaces this at phase 18 if the user wants to rename a field on existing content.
- **Rich content (HTML embeds, custom shortcodes) doesn't round-trip cleanly through the markdown widget.** Editors paste HTML; markdown widget converts to escaped HTML; render breaks. Use the `code` widget for verbatim HTML snippets, or a custom widget for rich embeds. (The new Plate-based richtext widget — added April 2026 — handles some of this better; the agent's fixture still uses `markdown` for v3-wide compatibility.)
- **Editorial workflow + Netlify auto-deploy = surprise publishes.** When a draft PR merges, Netlify auto-deploys. Make sure editors understand "publish" = "live in ~60 seconds." Phase 28 (deploy) wires this; phase 12 surfaces the timing expectation.
- **Smart quotes from Word paste.** Editors pasting from Word break markdown rendering (smart quotes vs ASCII quotes). The agent's content-validation pre-commit hook (phase 22) sanitizes; without it, content looks fine in admin but renders oddly on the live site.
- **`config.yml` is YAML, not JSON, and YAML is whitespace-sensitive.** A single misindented line breaks the entire admin. The agent generates `config.yml` rather than asking editors to hand-edit; if the user does hand-edit, the agent validates on PR.
- **Markdown widget deprecation (April 2026).** Decap announced Plate-based richtext widget as the new default. The markdown widget remains but is deprecated. Phase 12's context7 check surfaces this; agent recommends the markdown widget for new projects through 2026 (more stable, more pairings) and tracks the migration path.

## Stack pairings

Verbatim verdicts from the cross-CMS × stack compatibility anchor in `cms-adapters/README.md`. The phase-12 skill reads this table to validate the phase-11 stack choice is compatible.

| Stack (phase 11 choice) | Decap fit | Notes |
|---|---|---|
| **Astro** | **Native** | Astro Content Collections + Decap is a top-tier muggle pattern. Astro's `glob()` content loader + Decap's folder collections align cleanly. **Default for "Astro + a CMS."** |
| **Hugo** | **Native** | `static/admin/` for admin files; `content/<section>/*.md` for collections. Hugo's data files map to Decap file collections. |
| **Jekyll** | **Native** | `_posts/`, `_data/` map directly. The original (Netlify CMS-era) Decap target. |
| **Eleventy** | **Native** | Same shape as Jekyll. Passthrough copies `admin/` from input to output. |
| **Gatsby** | **Native (legacy)** | Works but Gatsby's mindshare has shifted — Netlify acquired then de-prioritized Gatsby; the broader ecosystem is moving away. Pick Astro for new projects. |
| **Next.js + shadcn (static export)** | **Possible** | Use with `output: 'export'`. Pages live as MDX in `content/`; Decap commits MDX. Loses Next.js's dynamic features, gains Decap simplicity. Surface at phase 12 — if the user wants Next.js dynamic, Decap is the wrong CMS. |
| **SvelteKit (static)** | **Possible** | `adapter-static` + Decap. Less common but works. |
| **Framer / WordPress / Webflow** | **N/A** | Those have their own CMSes. Decap-on-Framer / Decap-on-WordPress is anti-fit (per `adapters/stack-framer.md` §"CMS pairings to avoid on Framer" line 406 and `adapters/stack-wordpress.md` CMS-pairing table line 746). |
| **Plain static HTML** | **Awkward** | Decap commits markdown, but plain HTML doesn't render markdown without a generator. Use a generator (Astro / Hugo / etc.). Phase 12 should challenge the choice. |

### Per-pairing recipe — Astro + Decap (default Native pairing)

The Phase 4 test fixture uses this pairing. Per Astro docs (context7 `/withastro/docs`):

```bash
# In an existing Astro project (post phase-11)
mkdir -p public/admin
# Author admin/index.html + admin/config.yml (agent generates from sitemap.yaml + components.yaml)
```

`public/admin/index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="robots" content="noindex" />
    <link href="config.yml" type="text/yaml" rel="cms-config-url" />
    <title>Content Manager</title>
  </head>
  <body>
    <script src="https://unpkg.com/decap-cms@^3.1.2/dist/decap-cms.js"></script>
  </body>
</html>
```

`public/admin/config.yml`:

```yaml
backend:
  name: github
  repo: user/repo
  branch: main

media_folder: "src/assets/uploads"
public_folder: "/_astro/uploads"

collections:
  - name: pages
    label: Pages
    folder: "src/content/pages"
    create: true
    fields:
      - { name: title, widget: string }
      - { name: slug, widget: string }
      - { name: pubDate, widget: datetime }
      - { name: body, widget: markdown }
```

Astro picks up the markdown via Content Collections (`src/content/config.ts` Zod schema); Decap commits at `src/content/pages/`.

### Per-pairing recipe — Hugo + Decap

```yaml
# static/admin/config.yml (Hugo serves static/ at /)
backend:
  name: github
  repo: user/repo

media_folder: "static/uploads"
public_folder: "/uploads"

collections:
  - name: posts
    folder: "content/posts"
    create: true
    slug: "{{slug}}"
    fields:
      - { name: title, widget: string }
      - { name: date, widget: datetime }
      - { name: draft, widget: boolean, default: false }
      - { name: body, widget: markdown }
```

Hugo's `static/` directory is served at the site root, so `static/admin/` becomes `/admin/` on the live site. Hugo's data files (`data/*.yaml`) map to Decap file collections.

### Per-pairing recipe — Jekyll + Decap (legacy-canonical)

```yaml
# admin/config.yml (Jekyll serves admin/ at /)
backend:
  name: github
  repo: user/repo

media_folder: "assets/uploads"
public_folder: "/assets/uploads"

collections:
  - name: posts
    folder: "_posts"
    create: true
    slug: "{{year}}-{{month}}-{{day}}-{{slug}}"
    fields:
      - { name: title, widget: string }
      - { name: date, widget: datetime }
      - { name: layout, widget: hidden, default: post }
      - { name: body, widget: markdown }
```

The original Netlify CMS use case. `_posts/`, `_data/`, `_drafts/` all map cleanly.

### Per-pairing recipe — Next.js static export + Decap (Possible, not Native)

```js
// next.config.mjs
const nextConfig = {
  output: 'export',  // static export (loses SSR / API routes)
  trailingSlash: true,
}
export default nextConfig
```

```yaml
# public/admin/config.yml
backend:
  name: github
  repo: user/repo

media_folder: "public/uploads"
public_folder: "/uploads"

collections:
  - name: pages
    folder: "content/pages"
    create: true
    fields:
      - { name: title, widget: string }
      - { name: slug, widget: string }
      - { name: body, widget: markdown }
```

Content lives as MDX in `content/`; the app reads via `fs` + `gray-matter` at build time. Loses Next.js's dynamic capabilities — if the user wants those, this is the wrong combination; phase 12 surfaces Payload (Next.js-native) or `none` (filesystem) instead.

## Content layer mapping

The 5-layer content stack (`Workstreams/website-builder/foundation/DESIGN-content-layers.md`) maps onto Decap's native concepts. Row labels identical to `adapters/README.md` §"Content layer mapping" + sibling CMS adapters (`cms-none.md` / `cms-payload.md`) per the cross-anchor consistency rule.

| Layer | Decap native concept |
|---|---|
| **L1 brand.yaml.tokens** | Stays in `src/styles/tokens.css` (or stack equivalent). Decap doesn't manage design tokens by default — they're code, not content. **Optional opt-in:** a `BrandTokens` file collection at `src/content/_data/brand.yaml` lets the editor change colors / fonts / spacing via admin; the build regenerates `tokens.css` from `brand.yaml` on every save. Surface this option at phase 12 only if the user explicitly asks (the muggle default is code-managed tokens). |
| **L2 sitemap.yaml + sections.yaml** | The sitemap = the set of files in folder collections (one Page per file in `src/content/pages/`). Section / component shapes = the `widget: list` + `types: [...]` typed-union list on each Page's `layout` field. `components.yaml` translates 1:1 to a `types` definition the agent generates at phase 18. |
| **L3 strings/{lang}.json** | A file collection per language (`src/content/_data/strings.{lang}.json`). Editors see "Strings → English" / "Strings → Deutsch" tabs. Each is a structured form (one field per top-level namespace: `nav`, `cta`, `errors`, ...). The frontend's i18n library (`astro-i18n` / Hugo native i18n / next-intl on static export) reads from these files. |
| **L4 content/pages/*.md** | The markdown body (`widget: markdown`) of folder-collection items. Phase 16 copywriting prose copies almost verbatim into Decap-managed files. With i18n: `multiple_files` produces `home.en.md` + `home.de.md`; `multiple_folders` produces `en/home.md` + `de/home.md`. |
| **L5 briefs/{component}.json** | Out of band — same as every other CMS. Briefs live in `.website-builder/briefs/`; Decap never sees them. (Briefs are a handoff-protocol artifact, not user-editable content.) |

### Seed pattern — porting `.website-builder/` to Decap at phase 18

```bash
# Move .website-builder content into the static-site-generator's content tree
cp .website-builder/content/pages/*.md src/content/pages/
cp .website-builder/content/strings/*.json src/content/_data/
cp -r .website-builder/media src/assets/uploads/
```

Then the agent writes `public/admin/config.yml` (or stack-equivalent path) mirroring the file shapes:

```yaml
# Auto-generated by the agent at phase 12 from sitemap.yaml + components.yaml
collections:
  - name: pages
    folder: "src/content/pages"
    fields:
      - name: layout
        widget: list
        types: [hero, rich_text, media_gallery, cta]   # generated from components.yaml
  - name: strings
    files:
      - { name: en, file: "src/content/_data/strings.en.json", fields: [...] }
      - { name: de, file: "src/content/_data/strings.de.json", fields: [...] }   # if i18n
```

When the user adds a new block at phase 18, the agent regenerates `config.yml` so the new block type appears in admin without manual editing.

## i18n integration

Per `Workstreams/website-builder/foundation/DESIGN-i18n.md` + locked Decisions 38-41. Decap natively supports i18n via top-level + per-collection + per-field configuration.

### Configuration mechanism

Three structures (Decap's `structure` setting under `i18n:`):

| Structure | File layout | Use when |
|---|---|---|
| **`multiple_files`** (DEFAULT per Decision 39 Pattern A) | `<folder>/<slug>.<locale>.<extension>` — e.g., `pages/home.en.md`, `pages/home.de.md` | The agent's default. Aligns with `DESIGN-i18n.md` Pattern A (shared structure, translated prose). |
| `multiple_folders` | `<folder>/<locale>/<slug>.<extension>` — e.g., `pages/en/home.md`, `pages/de/home.md` | When the user wants per-locale folders (some static-site generators prefer this — Hugo's content/<locale>/ convention). |
| `single_file` | One file per slug with locale-keyed frontmatter | Rare. Useful for content where the locale variants are tightly coupled (e.g., a glossary). |

### Top-level i18n (whole CMS)

```yaml
i18n:
  structure: multiple_files
  locales: [en, de, fr]
  default_locale: en
```

### Collection-level i18n

Inherit top-level OR override:

```yaml
collections:
  - name: posts
    folder: "src/content/blog"
    create: true
    i18n: true                                                   # inherit top-level
    fields:
      - { name: title, widget: string, i18n: true }              # translatable
      - { name: date, widget: datetime, i18n: duplicate }        # shared across locales (date is universal)
      - { name: body, widget: markdown, i18n: true }             # translatable
```

Field-level `i18n` values:

- `i18n: true` — field is translatable per locale (separate value per locale)
- `i18n: duplicate` — same value across locales (e.g., dates, slugs, refs to non-localized collections)
- `i18n: none` (default) — field exists only in default locale

### File-collection i18n (Strings — Layer 3)

```yaml
- name: strings
  label: "UI Strings"
  files:
    - { name: en, file: "src/content/_data/strings.en.json", fields: [...] }
    - { name: de, file: "src/content/_data/strings.de.json", fields: [...] }
    - { name: fr, file: "src/content/_data/strings.fr.json", fields: [...] }
```

One file per locale (file-collection convention); the agent generates these from the seed strings file at phase 22. Per `i18n/strings-schema.md`: structure (namespaces) identical across files; only values differ. The frontend's i18n library consumes `strings.{lang}.json` directly.

### The blocks-localization decision (Decision 39)

Pattern A (default) = **shared layout, translated text inside blocks**:

- The `layout` field on a Page is NOT localized (`i18n: duplicate` or omitted) — same blocks in same order across locales
- Text fields INSIDE each block ARE localized (`i18n: true`)
- Result: the German site has the same Hero block in the same position as the English site, but with German `headline` / `sub` / `cta_label`
- Why: the muggle's structural intent is the same per locale; only the prose differs. Cheaper to translate; easier for editors to keep in sync.

Pattern B (per-locale layouts) = each locale has its own `layout` array entirely — harder to keep in sync; only pick if markets need structurally different content. Per `DESIGN-i18n.md` lines 204-213 (Layer 4 Pattern B).

### Translation workflow (Decisions 40-41)

**Pattern 1 (default per Decision 40):** the agent at phase 16 translates inline before committing to Decap-managed files. Decap reads already-translated files; editors see a complete site in admin from day one.

**Pattern 2 (upgrade path):** the agent emits `briefs/translation-{lang}-{ts}.json` (per `i18n/strings-schema.md`). User sends to professional translator. Translator returns translated `strings.{lang}.json` + per-language page MDs. Phase 6.5 ingests, commits to repo. Recommended for sites with carefully-crafted brand voice or regulatory copy per `DESIGN-i18n.md` line 323.

**Pattern 3 (user-driven external):** user uses their own tooling (DeepL, ChatGPT, in-house translator). Agent doesn't endorse a specific tool; same handoff format as Pattern 2.

**String-missing fallback (Decision 41):** when a target-locale string is empty, the frontend's i18n library falls back to the default-locale string + emits a console warning. The agent doesn't pre-empt missing strings at build time (would suppress real issues) but the per-stack PR-check enforces no-missing-keys for production deploys.

### Cross-references for deep specifics

- `i18n/strings-schema.md` — stack-agnostic CDJSON contract (Layer 3 schema)
- `i18n/language-switcher.md` — switcher implementation per-stack (Astro: `astro-i18n` component; Next.js: `next-intl` `useLocale`; Hugo: `lang.AlternateOutputFormats` partial)
- `i18n/hreflang.md` — hreflang emission per-stack
- `i18n/rtl.md` — CSS logical properties + `dir="rtl"` discipline (CMS-agnostic)

## Phase 6.5 ingestion

Phase 6.5 is re-runnable at any project lifecycle point. For Decap-stack projects, the per-entry-mode recipes:

| Entry mode | Decap-specific extraction → CMS-native primitive |
|---|---|
| **Greenfield** | No extraction. Agent generates `config.yml` from `sitemap.yaml` + `components.yaml` at phase 18. |
| **Has-AI-output** | AI-output parser extracts content + maps to Decap field shapes. New page → new markdown file with frontmatter + body in the appropriate folder collection. New block-shape in the parsed output → agent appends a new entry to `config.yml`'s `types` list and regenerates. |
| **Has-existing-site** | Stitch / Playwright extracts page structure. Each extracted page → a markdown file in `src/content/pages/`. Tokens → `tokens.css` OR (if `BrandTokens` file collection opted in) `src/content/_data/brand.yaml`. |
| **Has-Figma-file** | Figma plugin output normalizes to Decap field shapes; new component shapes become new `types` entries in the Page collection's `layout` field. |
| **Mid-project** | User generates a section in ChatGPT, pastes back. Agent identifies which page + which block type; appends to existing markdown file's `layout` array (preserves prior work) or creates a new file. |
| **JSON-handoff round-trip** | Same as has-AI-output but with iteration history tracked. Each round-trip generates a new commit on a draft branch; user reviews via `git diff`. |

### Conflict resolution per Decision 36 (halt + force user decision)

File-level conflicts are git's natural conflict surface. The agent:

1. Surfaces the diff via `git diff` (or GitHub UI for PR-flow editorial-workflow projects)
2. Halts pipeline progression
3. Asks user: **keep-mine** / **take-incoming** / **manual-merge**
4. Resumes only after user picks

The agent NEVER auto-resolves. Decap's whole point is "the user owns the git history"; auto-resolving violates that contract.

### JSON handoff round-trip output paths

Per the handoff-spec contract (`handoff-spec/component-output-v1.md`): the v0/Cursor/external-AI round-trip output lands in `.website-builder/briefs/<component>-<timestamp>.received.json`. The agent's ingestion routine parses, validates against the schema, then writes Decap-shaped artifacts:

- Page-level prose → `src/content/pages/<slug>.<lang>.md`
- Block-shape additions → new entry in `config.yml`'s `types` list (agent regenerates)
- Token changes → `tokens.css` (or `brand.yaml` if BrandTokens file collection opted in)
- Strings changes → `src/content/_data/strings.<lang>.json` (per-namespace merge — never overwrite the whole file)

Same handoff-spec contract as every other CMS; CMS-shaped destination differs.

## Commerce integration (if transactional=true)

Decap doesn't natively support commerce. Per `cms-adapters/README.md` §9: Decap + `none` delegate to stack + commerce adapter. The commerce adapter (`commerce-adapters/commerce-stripe.md` — Captain L's Phase 4 deliverable) sits next to Decap and writes into the stack's commerce-config path.

### How external commerce surfaces in Decap-authoring

Two integration patterns:

**Pattern A: Decap manages product catalog metadata; Stripe is the source of truth for pricing + checkout**

```yaml
collections:
  - name: products
    label: Products
    folder: "src/content/products"
    create: true
    fields:
      - { name: name, widget: string }
      - { name: stripe_product_id, widget: string }   # link to Stripe Product
      - { name: stripe_price_id, widget: string }      # link to Stripe Price
      - { name: featured_image, widget: image }
      - { name: description, widget: markdown }
```

Editor manages display metadata (name, image, description) in Decap; Stripe Dashboard manages prices + inventory + checkout. The frontend renders the catalog from `src/content/products/*.md` + calls Stripe Checkout with the linked `stripe_price_id`.

Trade-off: two surfaces (Decap for display, Stripe for transaction). Acceptable for small product catalogs (~10-50 SKUs); breaks down at scale.

**Pattern B: Stripe is the catalog source of truth; Decap is read-only for products**

Build script (custom; agent writes at phase 24a) fetches Stripe products at build time and writes them to `src/content/_data/products.json`. Decap-managed pages reference products by Stripe ID. No Decap collection for products.

Trade-off: editor can't add a product from Decap admin (must use Stripe Dashboard). But pricing changes propagate without manual sync.

The agent at phase 24a asks the user: "Do you want to edit product metadata in Decap (Pattern A) or only in Stripe (Pattern B)?"

### Phase 22 transactional mid-flip (Decision 34)

If the user starts at phase 11 with `transactional: false` then later flips to `transactional: true` (Decision 34):

1. Phase 12 reruns CMS-decision validation. Decap stays viable for commerce (Pattern A or B above).
2. Agent generates `commerce-config.yaml` (per `commerce-adapters/payment-config-schema.md`) — defines provider (Stripe), currencies, tax handling.
3. If user picks Pattern A: agent appends a `products` collection to `config.yml`; regenerates.
4. If user picks Pattern B: agent writes build-time fetch script; no `config.yml` change.
5. Phase 24b wires Stripe webhooks (e.g. `checkout.session.completed`) for order-confirmation pages or order data → static-site-generator regenerates relevant pages.
6. Phase 24c surfaces commerce-specific legal (privacy, ToS, refunds) — adds new pages to `src/content/pages/` that editors author in Decap.

**Per-CMS commerce limitation:** because Decap is build-time-only, order data can't render dynamically in a Decap-managed page. Order-confirmation pages either render at build time (after a webhook triggers a rebuild — minutes of delay) OR via a separate serverless function the agent generates at phase 28 (real-time but outside Decap). Phase 12 surfaces this trade-off; if the user needs real-time order pages, Payload or another dynamic CMS is the right pick.

### Cross-references

- `commerce-adapters/commerce-stripe.md` — Stripe commerce-adapter (Captain L Phase 4)
- `commerce-adapters/booking-calcom.md` — Cal.com booking-adapter (Captain L Phase 4)
- `commerce-adapters/payment-config-schema.md` — canonical `payment-config.yaml` schema for TWINT-via-Stripe-on-CHF Swiss-market constraint
- `Workstreams/website-builder/commerce/` — design surface
- `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` — phase 22 / 24a / 24b / 24c contracts

## Limitations + escape hatches

| Limitation | Escape hatch |
|---|---|
| **Project maintenance status disclosure (S2 — REQUIRED prominent).** Decap was in self-described "maintenance mode" 2023-2025 after the Netlify→Decap rename (February 2023). **As of 2026, Decap has been revitalized** — v3.12.2 released April 2026 with the new Plate-based richtext widget; the website migrated from Gatsby to Hugo; npm release cadence is back to ≥1 release per 3 months, classifying Decap as "sustainable" per npm-cadence-monitoring services. The original design-doc framing (line 403 of `DESIGN-cms-decap.md`, written 2026-05-10) said *"Decap is in maintenance mode; active forks exist."* That framing is outdated as of 2026-05-20. **The accurate current status: Decap is in active maintenance again; Sveltia CMS is an actively-developed alternative with claimed Decap-config compatibility; Static CMS is archived (no longer maintained, archived 2024-09-09).** | **Decap (default, recommended):** still the most-supported option; active 2026 development. Stay on Decap unless the user's editor needs Sveltia-specific features. **Sveltia CMS (active alternative, https://github.com/sveltia/sveltia-cms):** Svelte-based; 559 releases; latest v0.162.3 on 2026-05-20; 4,361 commits. Documented as "the de facto successor to Netlify CMS" with "high compatibility with the existing configuration format and API." Migration guide available; near-drop-in for most projects (verify per-widget at the time of migration). 2.4k GitHub stars. Pick this if: user wants the newest UX + i18n improvements, or wants confidence in long-term maintenance. **Static CMS (ARCHIVED — DO NOT pick as new):** https://github.com/StaticJsCMS/static-cms — archived 2024-09-09 per repo README. Final release v4.3.0 (April 2024). The README explicitly states "Decap CMS has been revitalized" and recommends alternatives (Tina CMS) over Static CMS. **The agent surfaces this verbatim at phase 12 so users don't pick an archived fork.** |
| **No real API.** Content is files; the static site generator builds them. | If user later needs an API (mobile app, headless rendering), they outgrow Decap → re-run phase 12 (CMS choice). Decision 34 (transactional mid-flip) is the canonical pattern — the agent runs phase 12 again, recommends Payload / Strapi / Sanity, runs migration. |
| **No real-time multi-editor.** | Editorial workflow + small teams (1-3 editors) usually suffices. For >5 editors with frequent simultaneous edits: switch CMSes. |
| **Slow saves (one git commit per save).** | Acceptable for editorial cadence (weekly publishes). Surface to user at phase 12 so they know "save" = "git commit + push" = ~2-3 seconds. |
| **OAuth requires git accounts for editors.** | Git Gateway (Netlify Identity) allows non-git-account editors. Adds Netlify dependency. Phase 28 wires this if needed. |
| **No fine-grained role-based access.** | Repo branch protection rules approximate this (editors get write to `cms/*` draft branches; admins merge PRs to `main`). Editorial workflow makes this enforceable. |
| **Image management = files in repo.** | Configure a media library (Cloudinary, Uploadcare, Bunny) at phase 8. The agent generates the media-library widget config in `config.yml`; uploads land at the library instead of the repo. |
| **Schema migrations are manual.** Decap doesn't migrate; renaming a field in `config.yml` doesn't update existing files. | Agent's phase-6.5 conflict-resolution flow handles ingestion-time schema changes; long-term schema drift requires manual cleanup (or a one-off migration script — the agent can author this when the user asks). |
| **Markdown widget deprecation (April 2026).** The Plate-based richtext widget is the new recommended default; markdown widget remains but deprecated. | Phase 12 surfaces the choice. Agent's fixture defaults to markdown widget through 2026 for ecosystem-wide compatibility (most stack adapters expect markdown frontmatter); when Plate-based richtext widget stabilizes (verify via context7 at next phase-12 lookup), the agent can swap. |
| **Build-time only.** Decap commit → site rebuilds → live ~30-60s later (depending on host). | Phase 12 surfaces the timing. For sites needing instant publish: not Decap. |
| **OAuth `repo` scope.** Decap requires full repo write access on GitHub. Some users uncomfortable with that. | Git Gateway via Netlify Identity scopes to one repo. Adds Netlify dependency; surface trade-off at phase 12 if security-sensitive. |

## context7 lookups for this CMS

Per Lock-3 freshness pattern. Cache home: `.website-builder/library/docs/decap-cms-*.md`. Re-fetch threshold: **30 days**.

| Phase | Library | Question |
|---|---|---|
| 12 (CMS decision) | `/websites/decapcms` (primary) | "Decap CMS config reference — backend, media_folder, collections, fields, widgets" |
| 12 (CMS decision) | `/websites/decapcms` | "Editorial workflow setup — draft branches, PR-based publishing" |
| 12 (CMS decision) | `/websites/decapcms` | "Maintenance status + release cadence 2026" — confirms active/maintenance status before final lock-in |
| 12 (CMS decision) | `/sveltia/sveltia-cms` | "Sveltia CMS Decap-config compatibility — drop-in replacement claims" — surfaces fork as alternative |
| 12 (CMS decision) | `/withastro/docs` (when stack is Astro) | "Astro Content Collections with Decap CMS admin folder integration" |
| 17 (design system) | `/websites/decapcms` | "BrandTokens file collection — design tokens via admin" — only if user opts in |
| 18 (component build) | `/websites/decapcms` | "List + types widget — block-style page layouts in Decap" |
| 18 (component build) | `/websites/decapcms` | "Custom widgets / preview templates" — only if user wants custom previews |
| 18 (component build) | `/websites/decapcms` | "Plate-based richtext widget vs markdown widget — when to use which" — for the markdown-deprecation pivot |
| 22 (forms / i18n / transactional) | `/websites/decapcms` | "i18n config — multiple_files vs multiple_folders structure; per-collection enable" |
| 22 (forms / i18n / transactional) | `/withastro/docs` or `/gohugoio/hugo` | "Static-site i18n integration — astro-i18n / hugo native i18n + Decap-managed strings" |
| 24a (commerce) | `/websites/decapcms` | "Stripe integration patterns with Decap — products collection" — when transactional=true |
| 28 (deploy) | `/websites/decapcms` | "OAuth provider setup — GitHub OAuth app + repo scope" |
| 28 (deploy) | (Netlify Identity docs via WebFetch) | "Git Gateway setup if scope-limiting needed" — context7 coverage for Netlify Identity is thin; WebFetch fallback to https://docs.netlify.com/security/secure-access-to-sites/identity/ |

### MCP-audit verbatim (Round-3 doctrine)

| Surface | Negative-finding status (2026-05-20) | Canonical fallback |
|---|---|---|
| **Decap CMS MCP** | No MCP exists. Decap is git-backed; ops are git ops. WebSearch verified 2026-05-20. | `/admin` UI for editing + GitHub MCP / `gh` CLI for git-side observation. |
| **Sveltia CMS MCP** | No MCP exists. Same reason as Decap — git-backed, no service surface. WebSearch verified 2026-05-20. | Same: `/admin` UI + GitHub MCP / `gh` CLI. |
| **Static CMS MCP** | No MCP exists; project archived 2024-09-09. | N/A — fork not recommended. |
| **GitHub OAuth MCP** | The GitHub MCP (`github/github-mcp-server`) covers OAuth-App creation flows + repo operations. Verified 2026-05-20. | Use the GitHub MCP for OAuth-App provisioning; `gh` CLI as fallback. |
| **Git Gateway / Netlify Identity MCP** | No dedicated MCP exists. Netlify MCP (where present) covers deploy hooks but not Identity flows. | Netlify dashboard UI + `netlify` CLI. WebFetch `https://docs.netlify.com/security/secure-access-to-sites/identity/` for freshness. |
| **Astro MCP** | Covered by Captain I's `cms-none.md` audit + `adapters/stack-nextjs.md`. No first-party Astro MCP. | context7 `/withastro/docs` for docs freshness; direct file edits via `Edit` / `Write`. |
| **Hugo MCP** | No first-party Hugo MCP (verified 2026-05-20 — same finding as Captain I). Hugo is a CLI + filesystem tool. | context7 `/gohugoio/hugo` for docs; `hugo` CLI directly. |
| **Eleventy / Jekyll MCPs** | No MCPs exist. Same shape as Hugo. | context7 for docs; CLI tools directly. |
| **Markdown linting MCP** | `remark-cli` / `markdownlint` are CLI tools, not MCPs. No dedicated MCP found. | Pre-commit hooks at phase 22 wire `markdownlint` or `remark` directly; agent reads/writes via `Edit` / `Write`. |

**Round-3 doctrine note:** all negative findings above are themselves load-bearing — the agent at runtime should NOT keep searching for these MCPs. If user requests Decap-specific operations beyond what the `/admin` UI handles, fall back to GitHub MCP + `gh` CLI immediately, without a new search.

## References

### Foundation design docs (this workstream)

- `Workstreams/website-builder/foundation/DESIGN-architecture.md` — plugin directory layout (`cms-adapters/` per line 115)
- `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` — `.website-builder/` layout
- `Workstreams/website-builder/foundation/DESIGN-content-layers.md` — the 5 content layers this adapter's §6 table maps
- `Workstreams/website-builder/foundation/DESIGN-i18n.md` — i18n model + per-CMS hooks (Patterns A/B, Decisions 38-41)
- `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` — phase 12 (CMS decision) + phase 22 (forms / transactional) + phase 24a/b/c (commerce)
- `Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md` — phase 6.5 mechanism
- `Workstreams/website-builder/cms/DESIGN-cms-decap.md` — **primary source** for this adapter

### Sibling adapters (this plugin)

- `cms-adapters/README.md` — the 12-section schema this file follows + cross-CMS × stack compatibility anchor
- `cms-adapters/cms-none.md` — Captain I's file-based-markdown CMS adapter (parallel Phase 4)
- `cms-adapters/cms-payload.md` — Captain K's Payload CMS adapter (parallel Phase 4)
- `adapters/stack-framer.md`, `adapters/stack-nextjs.md`, `adapters/stack-wordpress.md` — Phase 3 stack adapters referenced in §"Stack pairings"
- `commerce-adapters/README.md` — commerce + booking schema contract (referenced by §9)
- `commerce-adapters/payment-config-schema.md` — `payment-config.yaml` canonical schema
- `i18n/strings-schema.md`, `i18n/rtl.md`, `i18n/language-switcher.md`, `i18n/hreflang.md` — Phase 3 i18n substrate
- `handoff-spec/component-request-v1.md`, `handoff-spec/component-output-v1.md` — Phase 3 handoff contracts

### External — Decap

- **Decap official docs:** https://decapcms.org/docs/
- **Decap GitHub:** https://github.com/decaporg/decap-cms — 4,515 commits, 191 releases, latest v3.12.2 (April 2026)
- **Decap configuration options:** https://decapcms.org/docs/configuration-options/
- **Decap i18n docs:** https://decapcms.org/docs/i18n/
- **Decap editorial workflow:** https://decapcms.org/docs/editorial-workflows/
- **Decap variable-type widgets (Blocks pattern):** https://decapcms.org/docs/variable-type-widgets/
- **Decap external OAuth clients:** https://decapcms.org/docs/external-oauth-clients/
- **Decap backends:** GitHub https://decapcms.org/docs/github-backend/ · GitLab https://decapcms.org/docs/gitlab-backend/ · Bitbucket https://decapcms.org/docs/bitbucket-backend/ · Gitea https://decapcms.org/docs/gitea-backend/ · Git Gateway https://decapcms.org/docs/git-gateway-backend/
- **Decap blog (release notes):** https://decapcms.org/blog/

### External — Active fork

- **Sveltia CMS GitHub:** https://github.com/sveltia/sveltia-cms — active alternative
- **Sveltia CMS docs:** https://sveltiacms.app/ (production site)
- **Sveltia migration guide:** https://sveltiacms.app/en/docs/migration

### External — Archived (do not pick)

- **Static CMS GitHub:** https://github.com/StaticJsCMS/static-cms — ARCHIVED 2024-09-09; documented for awareness only

### External — Stack pairings

- **Astro Content Collections:** https://docs.astro.build/en/guides/content-collections/
- **Astro + Decap CMS guide:** https://docs.astro.build/en/guides/cms/decap-cms/
- **Hugo data files:** https://gohugo.io/templates/data-templates/
- **Hugo + Decap CMS guide:** https://gohugo.io/content-management/static-files/

### Phase-12 / Phase-18 skill consumers (when authored)

- `skills/wb-architecture/SKILL.md` — phase 12 reads `## Mental model` + `## When to pick this CMS` + `## Stack pairings` from this file
- `skills/wb-component-build/SKILL.md` — phase 18 reads `## Authoring patterns` + `## Content layer mapping` from this file
