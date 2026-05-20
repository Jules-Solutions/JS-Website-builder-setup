# CMS Adapter — `none` (file-based markdown)

> **Identity.** "No CMS." Content is markdown files committed to git. The static-site framework (Astro Content Collections / Hugo `content/` / Eleventy data cascade) reads files at build time and produces the deployed site. **CMS name + version baseline:** there is no CMS — the relevant version is whichever static-site framework reads the files. Canonical context7 IDs for the read-path frameworks: `/withastro/docs` (default pairing), `/gohugoio/hugo`, `/11ty/eleventy`. **Freshness-check requirement:** the agent invokes context7 against the chosen framework at phases 12 / 17 / 18 / 22 to confirm current Content Collections / data-cascade / archetype surfaces. Framework APIs evolve; training data is stale.
>
> **Source design doc:** `Workstreams/website-builder/cms/DESIGN-cms-none.md`. Captain-I authored against the 12-section schema in `cms-adapters/README.md`.

## Mental model

There is no CMS. Content is files. The user edits a markdown file in a code editor (or VS Code with markdown preview), commits, pushes — CI/CD auto-deploys. The website-builder's role is to make this workflow **as muggle-friendly as a CMS** without the operational overhead of one: clear directory layout, VS Code workspace pre-configured, schema validation at save AND at build, optional in-browser editing via GitHub Codespaces or github.dev.

The core primitives:

- **Markdown files** in `content/` (Astro: `src/content/`, Hugo: `content/`, 11ty: `src/`). Each file IS a piece of content.
- **YAML frontmatter** as the structured-data layer (title, slug, description, sections array). Body is the long-form prose.
- **Schema** as the discipline mechanism — Astro Content Collections + Zod, or Hugo archetypes + custom layouts, or 11ty data cascade. Bad frontmatter fails the build.
- **Git** as the persistence + history + collaboration mechanism — `git log` IS the revision history; pushes ARE publishes.
- **Pre-commit hooks** for lint + validation. The build is a backstop; the hook is the fast-feedback loop.

What makes this distinct: there's no admin UI, no database, no separate-deploy. The user's stack is the CMS. The website-builder still enforces every other discipline (design tokens, components, accessibility, deploy pipeline) — it just skips CMS-overhead infrastructure.

## When to pick this CMS

The phase-12 dialogue should actively **challenge users who reflexively want a CMS** toward `none` when their cadence + editor count doesn't justify the overhead. *"You have 5 pages and you'll edit them once a month; CMS overhead is bigger than the editing problem. Want me to make this file-based instead?"* CMS choice is a *cost*; `none` has near-zero cost; the website-builder's discipline (design system, components, accessibility) doesn't require a CMS to enforce.

The success criterion: a user picks `none`, edits their site twice in 6 months, and never thinks about CMS overhead. That's the win.

### Pick `none` when

- **The user is the only editor**, or a tiny team comfortable with git.
- **Content updates are infrequent** (weekly / monthly / quarterly cadence).
- **Content shape is markdown + simple frontmatter** — no heavy structured relationships.
- **The user is comfortable in VS Code** (or any text editor) writing markdown.
- **The site is small** — 5-50 pages, dozens of posts.
- **Build time + simplicity matter more than editor UX.**
- **The user wants the lightest-possible operational footprint** — no DB, no admin, no auth, no separate deploy.
- **The stack is static** — Astro / Hugo / 11ty / Jekyll / Gatsby / static-html / Next.js static export.

### Don't pick `none` when

- **Multiple non-developer editors need to publish.** They won't survive git workflows. Use Decap, Tina, Strapi, or Ghost.
- **Content cadence is daily or hourly.** Git friction adds up; admin UI pays back.
- **Editor needs visual editing / WYSIWYG.** Use Tina or Decap.
- **Content has heavy structured relationships** across collections. Use Sanity, Payload, or Directus.
- **Members + paid subscriptions.** Use Ghost.
- **Editor is allergic to opening a code editor.** Use any CMS with an admin UI.

## Auth + setup

There is no auth surface and no setup beyond what the static-site framework requires. The "auth" is **git repo access** — write access to the repo equals full edit rights. There is no fine-grained permissions model. There is no admin URL. There is no API key.

What the agent DOES configure at scaffold:

- **Git remote** (GitHub / Forgejo / GitLab) — the user's existing repo or a fresh one.
- **CI/CD hookup** — Vercel / Netlify / Cloudflare Pages / GitHub Pages integration so push-to-main auto-deploys.
- **VS Code workspace** — `.vscode/extensions.json` + `.vscode/settings.json` + `.vscode/tasks.json` pre-configured with markdown-friendly extensions and a YAML schema reference so frontmatter validates as the user types.
- **Pre-commit hooks** — Husky / pre-commit framework wired to run schema lint + image-path lint + smart-quote sanitizer.
- **Optional: GitHub Codespaces / github.dev** path for editing without local setup. The agent generates `.devcontainer/devcontainer.json` when requested.

No environment variables are required for the CMS itself. Static sites need few secrets in general:

```
GEMINI_API_KEY=...                    # if image-gen used (consumer fallback per decision 56)
NEXT_PUBLIC_PLAUSIBLE_DOMAIN=...      # analytics
```

### CRUD vocabulary

Per **S1** — `cms-none`'s "API" is filesystem + git ops. The phase-12 dialogue must teach muggles what authoring feels like on `none`; the CRUD verbs translate non-obviously into a sequence of file edits + git commands. The agent surfaces this verbatim at phase-12 so the user understands the workflow before lock-in.

| CMS-canonical verb | `cms-none` translation |
|---|---|
| **Create a page** | Create `content/pages/{slug}.md` (or stack-equivalent) with frontmatter + body. `git add content/pages/{slug}.md; git commit -m "add {slug} page"; git push`. |
| **Edit a page** | Open `content/pages/{slug}.md` in editor. Edit frontmatter or body. Save. `git add content/pages/{slug}.md; git commit -m "edit {slug}"; git push`. |
| **Publish a page** | Merge to the `main` branch (or push directly to `main` for solo workflows). CI/CD picks up the next build and deploys. |
| **Unpublish a page** | Either: `git rm content/pages/{slug}.md; git commit; git push`, OR set `draft: true` in the file's frontmatter, commit, push. Most static-site frameworks honor `draft: true` and skip the page at build. |
| **Schedule publish** | Merge to a `scheduled` branch with a `publishDate:` frontmatter field. A CI cron compares dates daily and merges eligible items to `main` on the scheduled date. Native scheduled-publish is NOT built in — the agent wires this only when the user asks. |
| **View revisions** | `git log content/pages/{slug}.md` — the commit history IS the revision history. `git diff <commit>..<commit> content/pages/{slug}.md` shows what changed between versions. No UI for non-git-savvy editors. |
| **Upload media** | Drop the file in `public/images/` (Astro / Next.js / 11ty) or `static/images/` (Hugo). `git add public/images/{name}.jpg; git commit; git push`. Reference in markdown via `![alt](/images/{name}.jpg)`. |
| **Create a new content type** | Extend the schema. **Astro:** edit `src/content/config.ts` to add a new `defineCollection({ ... })`. **Hugo:** create `archetypes/{type}.md` template + `layouts/{type}/single.html` template. **11ty:** add a new collection in `eleventy.config.js` via `addCollection`. |
| **Delete a page** | `git rm content/pages/{slug}.md; git commit -m "remove {slug}"; git push`. Page disappears from next deploy. To preserve content-but-unlist, set `draft: true` instead. |

The `wb-commit` helper script the agent generates in `package.json` reduces the multi-step sequence to one command:

```json
{
  "scripts": {
    "wb:commit": "git add . && git commit",
    "wb:publish": "git add . && git commit && git push"
  }
}
```

So `pnpm wb:publish "edit about page"` collapses create-edit-stage-commit-push into one keystroke for editors who internalize that single command.

## Authoring patterns

Canonical content-authoring patterns + common pitfalls. The phase-12 + phase-18 skills consume this section when generating the content-directory layout + per-stack `config.ts` / archetypes / data cascade config + pre-commit hook wiring.

### Pattern 1 — Per-stack content directory layout

The agent generates a clean content directory matching the chosen stack's expectations. Layouts are stack-specific but follow the same shape: one markdown file per page, frontmatter for structured data, body for prose, plus per-stack schema config.

**Astro (default pairing):**

```
src/content/
├── config.ts               # Zod schemas (Content Collections)
├── pages/
│   ├── home.md
│   ├── about.md
│   └── contact.md
├── posts/
│   ├── 2026-05-10-launch.md
│   └── 2026-05-08-welcome.md
└── strings/
    ├── en.json
    └── de.json
```

`src/content/config.ts` enforces frontmatter shape via Zod — validates at build AND at IDE-save (via VS Code's YAML schema integration). Cross-reference: cached context7 at `.website-builder/library/docs/cms-none-astro.md`.

**Hugo:**

```
content/
├── _index.md               # homepage
├── about.md
├── contact.md
└── posts/
    ├── _index.md           # blog index page
    ├── 2026-05-10-launch.md
    └── 2026-05-08-welcome.md
archetypes/
├── default.md              # base template
└── post.md                 # blog-post template
data/
└── strings/                # data files for i18n strings
    ├── en.toml
    └── de.toml
i18n/                       # per-language string files (Hugo native)
├── en.toml
└── de.toml
```

Hugo's `archetypes/` provides creation templates; `i18n/` holds translation strings (Hugo-native i18n). Cross-reference: cached context7 at `.website-builder/library/docs/cms-none-hugo.md`.

**11ty:**

```
src/
├── pages/
│   ├── home.md
│   ├── about.md
│   └── contact.md
├── posts/
│   └── ...
└── _data/
    ├── site.js
    ├── strings.en.json
    └── strings.de.json
eleventy.config.js          # data cascade + I18nPlugin config
```

Cross-reference: cached context7 at `.website-builder/library/docs/cms-none-11ty.md`.

### Pattern 2 — Section-composition via frontmatter array

A page is a markdown file whose frontmatter declares ordered sections; the static-site template renders each section by `type` discriminator. This is the primary cross-stack pattern that bridges L2 `sections.yaml` to per-page markdown.

```markdown
---
title: "Home"
slug: "/"
description: "Weekly essays on staying human."
sections:
  - type: hero
    headline: "Still Humans"
    sub: "Weekly essays on staying a person in 2026."
    cta_text: "Get the newsletter"
    cta_href: "#signup"
    background_image: /images/hero.jpg
  - type: feature_grid
    heading: "What you get"
    features:
      - title: "One essay per week"
        description: "Always Monday morning."
        icon: /icons/calendar.svg
      - title: "Always free"
        description: "No paywall, no upsell."
        icon: /icons/heart.svg
  - type: cta
    headline: "Ready?"
    button_text: "Subscribe"
    button_href: "#signup"
---

(optional long-form prose body — rendered as markdown after the structured sections)
```

The stack's template iterates `sections[]` and renders each block. Astro example (using a `blockComponents` lookup table):

```astro
---
// src/pages/[...slug].astro
import { getEntry } from 'astro:content'
import Hero from '../components/Hero.astro'
import FeatureGrid from '../components/FeatureGrid.astro'
import Cta from '../components/Cta.astro'

const { slug } = Astro.params
const page = await getEntry('pages', slug || 'home')

const blockComponents = { hero: Hero, feature_grid: FeatureGrid, cta: Cta }
---

<Layout title={page.data.title} description={page.data.description}>
  {page.data.sections.map((section) => {
    const Component = blockComponents[section.type]
    return Component ? <Component {...section} /> : null
  })}
  <slot />  <!-- markdown body if any -->
</Layout>
```

The Zod schema for the section array uses a discriminated union so the validator enforces per-type field shapes:

```typescript
sections: z.array(
  z.discriminatedUnion('type', [
    z.object({
      type: z.literal('hero'),
      headline: z.string().max(60),
      sub: z.string().max(120).optional(),
      cta_text: z.string().max(24).optional(),
      cta_href: z.string().optional(),
      background_image: z.string().optional(),
    }),
    z.object({
      type: z.literal('feature_grid'),
      heading: z.string(),
      features: z.array(
        z.object({
          title: z.string(),
          description: z.string(),
          icon: z.string().optional(),
        })
      ),
    }),
    z.object({
      type: z.literal('cta'),
      headline: z.string(),
      button_text: z.string(),
      button_href: z.string(),
    }),
  ])
)
```

This is the primary discipline mechanism — the agent's lint runs at every save (via VS Code YAML schema) AND at build (via the Zod validator). Bad frontmatter fails the build before deploy.

### Pattern 3 — VS Code workspace at scaffold

The agent generates `.vscode/` to make file-based authoring feel as muggle-friendly as a CMS:

`.vscode/extensions.json`:

```json
{
  "recommendations": [
    "yzhang.markdown-all-in-one",
    "redhat.vscode-yaml",
    "astro-build.astro-vscode",
    "eamodio.gitlens",
    "esbenp.prettier-vscode"
  ]
}
```

`.vscode/settings.json`:

```json
{
  "editor.formatOnSave": true,
  "files.associations": { "*.md": "markdown" },
  "yaml.schemas": {
    "./.website-builder/schemas/page.json": "src/content/pages/*.md"
  }
}
```

The YAML schema gives the user inline validation as they type frontmatter — closest equivalent to a CMS's required-field hint.

`.vscode/tasks.json` provides quick-commit, build, deploy shortcuts via VS Code's command palette (`Cmd+Shift+P → Tasks: Run Task → wb:publish`).

### Pattern 4 — Image pasting

VS Code extensions like "Paste Image" let editors paste screenshots directly into markdown. The agent configures the destination path (`public/uploads/{slug}/`) per page in `.vscode/settings.json`. The image goes into the right folder; the markdown reference is inserted at cursor; no manual file management.

### Pattern 5 — Pre-commit hook for validation

```bash
# .husky/pre-commit
pnpm lint:content       # runs Zod schema validation on all content files
pnpm lint:images        # checks every image reference resolves
pnpm lint:strings       # checks every {strings.x.y} reference resolves in strings/
pnpm lint:smart-quotes  # sanitizes smart quotes / non-breaking spaces from Word paste
```

`lint:content`, `lint:images`, `lint:strings` are agent-emitted scripts in `package.json`. Pre-commit failures stop the commit; user fixes; re-commits. The CI build re-runs these as backstop (catches `--no-verify` bypasses).

### Common pitfalls

Muggle-level gotchas. The phase-12 dialogue surfaces these as caveats before lock-in. Most are caught by the pre-commit hook; some require manual discipline.

- **Frontmatter typos.** `tile:` instead of `title:`. Schema validation catches at lint OR build time. The agent wires the VS Code YAML schema for inline real-time validation.
- **Forgetting to commit a new file.** User creates `posts/new.md` but forgets `git add`. The `wb:publish` helper script does `git add . && git commit && git push` in one step.
- **Image references break after rename.** Move `images/x.jpg` → `images/y.jpg`; markdown still references `x.jpg`. The `lint:images` hook walks all `![...](...)` references.
- **Markdown body vs frontmatter sections confusion.** User writes prose in frontmatter or structured data in body. Schema lint flags structurally-misplaced fields.
- **Deploy fails silently** because of build-time schema violations. The agent wires CI to surface failures in a checkable summary (Vercel / Netlify deploy webhook payloads include build errors).
- **Conflict on push** when working from two machines. Standard git conflict resolution. The agent's bootstrap surfaces the workflow + suggests `git pull --rebase` before edits as the muggle-friendly default.
- **Forgetting frontmatter delimiters.** `---` open + close required. YAML lint catches.
- **Date format issues** (Jekyll `YYYY-MM-DD-slug.md` requires the date prefix). Stack-specific; the agent enforces via filename lint per Pattern 1's stack-specific layout.
- **Whitespace stripping in YAML lists.** Tabs vs spaces. YAML is whitespace-sensitive; the agent enforces 2-space YAML in `.editorconfig` + Prettier config.
- **Smart quotes from Word / Google Docs paste** break markdown. The `lint:smart-quotes` hook sanitizes pre-commit.
- **Long body markdown gets unwieldy.** No editor split-view by section. The agent surfaces *"consider splitting into a CMS at {threshold} pages"* guidance during regular session-start checks if the page count crosses ~25.

## Stack pairings

Phase 12 cross-CMS × stack pairings from `cms-none`'s perspective. Verdicts use the canonical words **Native / Possible / Awkward / Anti-fit / N/A** verbatim per the cross-CMS × stack compatibility anchor in `cms-adapters/README.md`. The phase-12 skill reads these cell verdicts to validate the user's phase-11 stack choice is compatible with `cms-none`.

| Stack | Fit verdict | Notes |
|---|---|---|
| **Framer** | **N/A** | Framer has its own first-party CMS (Framer CMS); pages are canvas documents, not file-based routes. Pairing `cms-none` with Framer makes no sense. |
| **Next.js + shadcn** | **Possible** | Static export mode (`output: 'export'`) with MDX + `gray-matter` for frontmatter. Less natural than Astro's first-class Content Collections. Surface the trade-off at phase 12 — most file-based-on-Next.js users would be happier on Astro. |
| **WordPress** | **N/A** | WordPress IS the CMS; the `wordpress-core` `project.yaml.cms` value is the default for the WordPress stack. File-based content is a category error against WordPress. |
| **Astro** | **Native** (default) | First-class — Astro Content Collections + Zod is the gold standard for file-based content. **This is the default recommendation when the user picks `none` and hasn't already committed to a stack.** Cached context7 snapshot at `.website-builder/library/docs/cms-none-astro.md`. |
| **Hugo** | **Native** | First-class — Hugo's `content/` directory is exactly this pattern. Built-in i18n via `i18n/{lang}.toml`. Fastest build times of any static-site framework (50k pages in seconds). Cached context7 snapshot at `.website-builder/library/docs/cms-none-hugo.md`. |
| **SvelteKit (static)** | **Possible** | Works via `mdsvex` for markdown-in-Svelte. Per Phase 3 stack-pairing symmetry — SvelteKit is not in the v1 stack adapter set (Phase 3 ships framer / nextjs / wordpress); flagged for future Phase 10+ expansion. |
| **Webflow** | **N/A** | Webflow has its own first-party CMS (Webflow CMS); pages are visual-builder documents, not file-based routes. Same category-error as Framer / WordPress pairings. |
| **Plain static HTML** | **Possible** | A build script (Pandoc / custom Node / Python markdown library) renders markdown to HTML. Niche; the agent prefers Astro for muggle-friendliness. |
| **11ty (Eleventy)** | **Native** (supplementary — not in cross-CMS anchor's 8-stack row, but `DESIGN-cms-none.md` line 299 documents 11ty Native) | First-class — Eleventy's data cascade reads markdown + frontmatter natively. Cached context7 snapshot at `.website-builder/library/docs/cms-none-11ty.md`. Per Phase 3 stack-pairing symmetry — 11ty is not in the v1 stack adapter set; flagged for future Phase 10+ expansion. |

**Default pairing when the user picks `none` without a prior stack choice:** **Astro.** Schema validation via Zod is the cleanest match for the website-builder's discipline; Astro Content Collections give first-class typed-content APIs; Astro's image optimization + view transitions + zero-JS-by-default match the muggle-site profile best.

### Per-pairing recipe — `none` + Astro (Native default)

Setup commands at phase 17/18 scaffold:

```bash
# Initialize Astro
pnpm create astro@latest -- --template minimal --typescript strict --no-git
# Add Content Collections (built into Astro 5+, no extra package needed)
# Configure src/content/config.ts with Zod schemas — agent generates from components.yaml
# Wire i18n if multilingual — agent generates src/content/{lang}/{slug}.md layout
```

Minimum config — `src/content/config.ts`:

```typescript
import { defineCollection, z } from 'astro:content'
import { glob } from 'astro/loaders'

const pages = defineCollection({
  loader: glob({ pattern: '**/[^_]*.md', base: './src/content/pages' }),
  schema: z.object({
    title: z.string().max(60),
    slug: z.string(),
    description: z.string().max(160),
    sections: z.array(/* per Pattern 2 above */),
  }),
})

export const collections = { pages }
```

Dynamic routing — `src/pages/[...slug].astro` catches all pages; `getEntry('pages', slug)` fetches content; the `blockComponents` lookup renders each section.

### Per-pairing recipe — `none` + Hugo (Native)

Setup commands:

```bash
hugo new site mysite
cd mysite
git init
# Configure hugo.toml — agent generates from project.yaml
# Place markdown files in content/ per Pattern 1 layout
hugo new content content/posts/hello.md   # uses archetypes/default.md
hugo server                                # dev preview
hugo                                       # build → public/
```

Hugo's `_index.md` files define list pages (homepage = `content/_index.md`; blog index = `content/posts/_index.md`).

### Per-pairing recipe — `none` + 11ty (Native)

Setup commands:

```bash
pnpm init -y
pnpm add -D @11ty/eleventy
# Configure eleventy.config.js — agent generates from project.yaml
# Place markdown files in src/ per Pattern 1 layout
npx @11ty/eleventy --serve  # dev server
npx @11ty/eleventy           # build → dist/
```

Wire `I18nPlugin` for multilingual sites — see cached `.website-builder/library/docs/cms-none-11ty.md` for the canonical config.

### Per-pairing recipe — `none` + Next.js (static export, Possible)

Used only when the user has a strong Next.js preference but doesn't want a CMS. Less natural than Astro:

```bash
pnpm create next-app@latest --typescript
# Configure next.config.js with output: 'export'
pnpm add gray-matter @next/mdx
# Build content reader at lib/content.ts using fs + gray-matter
# MDX files in content/ — read at build via getStaticProps / generateStaticParams
```

Surface the trade-off at phase 12: *"You can do file-based markdown on Next.js, but Astro is built for this. If you don't need React/Next-specific features, switching to Astro saves you a lot of boilerplate."*

### Per-pairing recipe — `none` + SvelteKit (static, Possible)

Used only when the user has SvelteKit preference. Reads as: `mdsvex` for `.md.svelte` (or `.svx`) files; `adapter-static` for static output.

```bash
pnpm create svelte@latest mysite
cd mysite
pnpm i
pnpm add -D @sveltejs/adapter-static mdsvex
# Configure svelte.config.js with mdsvex({extensions: ['.svx']}) and adapter-static
# Place markdown content as src/routes/.../+page.svx
pnpm dev      # dev server
pnpm build    # build static output to build/
```

Trade-off surfaced at phase 12: SvelteKit doesn't have first-class Content Collections like Astro; you wire your own loader on top of `mdsvex`. Functional but more boilerplate.

### Per-pairing recipe — `none` + Plain static HTML (Possible, niche)

Used when the user has a strong preference for hand-rolled static HTML and is comfortable with a custom build script. The agent generates:

```bash
# Project structure
mysite/
├── content/                  # source markdown
├── templates/                # HTML templates (Handlebars / EJS / Pug / etc.)
├── src/build.js              # custom Node build script using gray-matter + markdown-it
└── dist/                     # build output
```

```bash
pnpm init -y
pnpm add gray-matter markdown-it
node src/build.js              # reads content/*.md, applies templates/*.html, writes dist/
```

Niche pairing. The agent prefers Astro for muggle-friendliness — the static-HTML path requires the user to maintain their own build script.

## Content layer mapping

The 5-layer content stack from `DESIGN-content-layers.md` maps to `cms-none` primitives as follows. **Row labels are IDENTICAL across `adapters/README.md` §4 (stack), `cms-adapters/README.md` §4 (CMS), and `commerce-adapters/README.md` §4 (commerce) per the cross-anchor consistency rule.**

| Layer | CMS native concept |
|---|---|
| **L1 brand.yaml.tokens** | No CMS layer involved. Compiles to `src/styles/tokens.css` (Astro) / `assets/css/tokens.css` (Hugo) / `src/styles/tokens.css` (11ty) at build. The user does NOT edit tokens through any CMS — they edit `.website-builder/brand.yaml` directly. Token regeneration is a phase-17 task, not a per-edit task. |
| **L2 sitemap.yaml + sections.yaml** | One markdown file per page in `content/pages/` (Astro) / `content/` (Hugo) / `src/pages/` (11ty). Sections via frontmatter array (per Pattern 2 above). Schema validation in `src/content/config.ts` (Astro Zod) / `archetypes/*.md` + `layouts/_default/*.html` (Hugo) / `eleventy.config.js` (11ty data cascade). `sitemap.yaml.navigation` lives in `src/data/navigation.yaml` (Astro) / `data/navigation.yaml` (Hugo) / `src/_data/navigation.json` (11ty). |
| **L3 strings/{lang}.json** | Per-language JSON / TOML files. Astro: `src/content/strings/{lang}.json`. Hugo: `i18n/{lang}.toml` (Hugo-native) + optionally `data/strings.{lang}.toml`. 11ty: `src/_data/strings.{lang}.json` (read via data cascade) or single nested-locale `src/_data/strings.json`. CDJSON schema (per `i18n/strings-schema.md`) preserved verbatim. |
| **L4 content/pages/*.md** | Markdown body of each page file. The editor authors directly in the file. Body renders below the structured `sections[]` array — typical muggle pattern is sections do the heavy lifting and body is short-or-empty. |
| **L5 briefs/{component}.json** | Stays in `.website-builder/briefs/`. Briefs are agent-internal — no CMS sees them. Same for all CMSes per `DESIGN-content-layers.md`. |

### Migration recipe (Astro example)

```
.website-builder/                            →  user-website-project/ (Astro)
├── content/pages/{slug}.md                  →  src/content/pages/{slug}.md
├── content/strings/{lang}.json              →  src/content/strings/{lang}.json
├── content/sections.yaml                    →  src/content/config.ts (Zod schema for frontmatter)
├── components.yaml + components/code        →  src/components/{Name}.astro
├── brand.yaml.tokens                        →  src/styles/tokens.css
├── sitemap.yaml                             →  src/pages/[...slug].astro (catch-all + index)
├── .vscode/                                 →  generated workspace config
├── .husky/                                  →  pre-commit hooks
└── decisions/                               →  decisions/ (kept in repo)
```

Seed step: agent writes initial markdown files matching `sitemap.yaml`. User opens VS Code; starts editing.

## i18n integration

Per-CMS i18n model. Cross-references the shared anchors at `i18n/strings-schema.md`, `i18n/language-switcher.md`, `i18n/hreflang.md`, `i18n/rtl.md` for stack-agnostic specifics.

### Configuration mechanism

For `cms-none`, i18n configuration is **stack-native** — there's no separate CMS-side config. Per stack:

- **Astro:** per-language folders under `src/content/pages/`. Dynamic route `src/pages/[lang]/[...slug].astro` uses `getStaticPaths` + `getEntry('pages', `${lang}/${slug}`)`.
- **Hugo:** `defaultContentLanguage` + `[languages]` block in `hugo.toml`; per-language folders under `content/` OR filename suffix `post.{lang}.md`.
- **11ty:** `I18nPlugin` from `@11ty/eleventy`; per-language folders under `src/`; `locale_url` + `locale_links` filters for routing.

Per **Decision 39** the website-builder's default storage pattern is **per-language folders** (matches Astro's recommendation + Hugo's `defaultContentLanguageInSubdir = true` + 11ty's per-locale dir convention). Per-language filename suffix is the alternative pattern, surfaced at phase 12 if the user prefers single-folder browsing.

### Per-locale storage

```
src/content/pages/          (Astro)         |    content/             (Hugo)         |   src/                  (11ty)
├── en/                                     |   ├── en/                              |   ├── en/
│   ├── home.md                             |   │   ├── _index.md                    |   │   ├── home.md
│   └── about.md                            |   │   └── about.md                     |   │   └── about.md
└── de/                                     |   └── de/                              |   └── de/
    ├── home.md                             |       ├── _index.md                    |       ├── home.md
    └── about.md                            |       └── about.md                     |       └── about.md
```

Strings cross-stack:

```
src/content/strings/en.json     (Astro)
i18n/en.toml                    (Hugo — native i18n)
src/_data/strings.en.json       (11ty)
```

### The blocks-localization decision

Since `cms-none` doesn't have a CMS-side "blocks" primitive — sections are inline in frontmatter — the localization decision is implicit. **Per-locale markdown files contain per-locale frontmatter AND body**, meaning *the layout AND the prose are both translated*. This is approach 1 (per-locale layouts), not the Decision 39 Pattern A default (approach 2 = shared layout, translated text).

For `cms-none` the trade-off is reframed:

- Markdown-per-locale is the only practical model. Trying to share `sections[]` across locales while only varying `headline` / `sub` / `cta_text` strings would require either a JSON-side variants file (defeats markdown simplicity) or string references like `{strings.home.hero.headline}` inside frontmatter (works but ugly; supported via the L3 string-reference mechanism).
- **Default for `none`:** per-locale files have full per-locale frontmatter (translators see the layout AND can adapt it for their market — e.g., DE market wants 3-column features, EN market wants 2-column). The `strings/{lang}.json` files handle the truly-shared microcopy (nav, CTAs, error messages).
- **Trade-off surfaced at phase 12:** "Your DE/FR/IT pages will be separate files, not parameterized variants of the EN file. You can keep them in lockstep with discipline, OR let each market have its own layout — your call." Most muggles pick "in lockstep" by default; the agent enforces drift detection via the session-start completeness walk (per Decision 41).

### Translation pattern

Per **Decision 40** the default pattern is **Pattern 1 (agent translates inline at phase 16)**:

1. Agent at phase 16 drafts source-language markdown files (typically EN).
2. For each target locale, agent writes translated copies to per-language folders.
3. User reviews per-language in VS Code (with the split editor — both `home.md` files open side-by-side).

**Pattern 2 (translator handoff)** is the upgrade: per-locale markdown files become the brief / translated-output. Phase 6.5 ingests by writing to the right locale folder. Pattern 3 (user-driven external) is rarely picked.

### Routing

Per **Decision 38** the default routing strategy is **prefix routing** (`example.com/de/about`). Astro's `src/pages/[lang]/[...slug].astro` + Hugo's `defaultContentLanguageInSubdir = true` + 11ty's `I18nPlugin` filters all produce prefix-routed output by default.

Subdomain (`de.example.com`) and TLD (`example.de`) strategies are advanced; the agent surfaces at phase 12 only when the user signals geo-targeting requirements.

### String-missing fallback

Per **Decision 41** the fallback is **default-locale string at render-time with a build warning**. The phase-12 lint walks every page across all configured locales; warns on missing files. The frontend's i18n lib (Astro: `astro-i18n` or hand-rolled; Hugo: native `i18n` template func; 11ty: `I18nPlugin.errorMode: "strict"` or `"allow-fallback"`) falls back to the default-locale string at render-time so the user never sees an empty UI element.

The session-start hook (per Pattern 5 pre-commit) walks for locale completeness when new sections / strings are added and flags drift.

## Phase 6.5 ingestion

Phase 6.5 is re-runnable at any project lifecycle point. The agent reads this section on every re-ingestion to map external content into `cms-none`'s primitives. Per `DESIGN-cms-none.md` § "Phase 6.5 ingestion" lines 415-436, the entry modes for `cms-none` resolve as:

### Greenfield (Scenario B in source design)

Standard flow. Agent generates `.website-builder/content/` from the user's sitemap; writes initial markdown files matching the schema; user opens VS Code and begins editing.

### Has-AI-output (Scenario C — the "Mom's pattern")

User has ChatGPT / Claude / similar drafts pasted into `outputs/` or referenced as files. Agent at phase 6.5:

1. Reads the AI output.
2. Parses into the L2 `sections[]` shape (heuristics: H1 → page title, ## H2 → section heading, etc.).
3. Writes a new `content/{collection}/{slug}.md` file with the parsed structure.
4. User reviews + commits.

Per **Decision 36** conflict resolution — if the AI output collides with an existing markdown file (same slug), the agent halts and forces the user to decide (overwrite / merge / discard / rename).

### Has-existing-site (Scenario A — markdown already in tree)

User already has a `content/` directory with markdown files. Agent at phase 6.5:

1. Reads `content/` directory directly.
2. Reverse-maps file shapes to website-builder primitives (frontmatter → L2 structural specs; body → L4 prose).
3. Seeds `.website-builder/content/` from existing files.
4. If frontmatter doesn't match the Zod schema, agent surfaces drift + asks user to either update schema OR migrate frontmatter.

### Has-existing-site, exporting from another CMS (Scenario D)

User runs CMS export to markdown — e.g.:

- **Ghost → markdown:** `gh-pages` JSON export + a transformation script.
- **WordPress → markdown:** `wordpress-export-to-markdown` (npm package).
- **Notion → markdown:** Notion's native markdown export.
- **Contentful → markdown:** custom GROQ-like query + markdown serializer.

Agent ingests the markdown directly via the Scenario A flow.

### Has-Figma-file

Not a `cms-none`-specific scenario — Figma extraction lives in the stack-adapter ingestion path. The agent ingests Figma → component briefs (L5) and tokens (L1); these don't touch the CMS layer.

### JSON-handoff round-trip (v0 / Cursor pattern)

Per **Decision 35**, when a brief is sent to an external generator (v0.dev / Cursor / similar) and the result returns, the JSON-handoff output for `cms-none` becomes a **new markdown file the agent commits**. Where:

- Astro: `src/content/pages/{slug}.md` (or per-locale subfolder).
- Hugo: `content/{section}/{slug}.md`.
- 11ty: `src/pages/{slug}.md` (or per-locale subfolder).

The agent doesn't "send to CMS API" — the round-trip output is a file change committed alongside the user's normal git workflow.

### Mid-project re-runs

If the user changes `components.yaml` block types after pages already exist, phase 6.5 re-validates all existing markdown against the new Zod schema; drift is surfaced as a lint warning batch the user reviews + reconciles. Per Decision 36 — halt + force user decision on each conflict.

## Commerce integration (if transactional=true)

`cms-none` does NOT natively support commerce. The CMS layer is files; commerce requires server-side endpoints (Stripe checkout sessions / webhook handlers / inventory tracking). When `project.yaml.transactional: true` AND `cms: none`:

- **The commerce adapter takes over** the transactional surface. Default per `commerce-adapters/payment-config-schema.md`: external Stripe Checkout or Stripe Payment Links (no server code; redirect to hosted Stripe pages); Snipcart (client-side cart on static sites); Lemon Squeezy (similar Stripe-Checkout-like model).
- **Authoring stays file-based.** Product / pricing data lives in markdown files OR `src/data/products.yaml` (Astro) / `data/products.yaml` (Hugo) / `src/_data/products.json` (11ty). The build reads product files and renders product pages; the cart / checkout flow runs in the browser via the commerce adapter's JS.
- **Phase 24a/b/c branching:** the CMS adapter's role is to document HOW products surface as content files (per Pattern 1 layout — products as a markdown collection); the commerce adapter (`commerce-adapters/commerce-stripe.md`) handles the payment-provider wiring, webhook endpoints (if any — most pure-static patterns avoid webhooks), and Phase 24c legal (refund / terms / GDPR).

### Pairing example — `cms-none` + Stripe Checkout (external) + Astro

The most common transactional configuration for a `cms-none` site:

```
src/content/products/
├── tshirt.md           # frontmatter: name, price, stripe_price_id, description
└── poster.md
```

Each product file references a pre-created Stripe Price ID. The Astro page reads the product file, renders the product page, and embeds a "Buy now" button that calls `stripe.redirectToCheckout({lineItems: [{price: stripe_price_id, quantity: 1}]})`. No server runtime required.

Reference: `commerce-adapters/commerce-stripe.md` (Captain L's deliverable; may not exist at the time of this writing — forward reference per Phase 4 wave coordination).

### Phase 22 transactional mid-flip (Decision 34)

If the user starts with `transactional: false` (pure brochure) and later flips to `transactional: true`:

- The agent re-runs phase 24a (commerce platform setup) — picks the commerce adapter.
- Adds the commerce adapter's required files (cart component, checkout button, Stripe webhook handler if needed).
- Adds the product collection to `src/content/config.ts` (Astro) / `archetypes/product.md` (Hugo) / `eleventy.config.js` (11ty).
- The CMS layer (`cms-none`) is **unchanged** — products are just more markdown files. The migration is purely commerce-adapter-side.

This is one of `cms-none`'s strengths — the file-based layer doesn't fight commerce additions; it just absorbs them as new content files.

## Limitations + escape hatches

What `cms-none` CAN'T do (surfaced at phase 12 for user override). Hard limitations vs. soft limitations vs. escape hatches per the schema contract.

| Limitation | Type | Escape hatch |
|---|---|---|
| **Editor must be comfortable in a code editor.** Non-developer editors struggle without onboarding. | Hard | Add a non-developer editor → flip to Decap/Tina/Strapi/Ghost via phase-12 restart + migration recipe. |
| **No live preview from a separate admin UI.** VS Code's markdown preview is the closest. | Hard | Use VS Code's split-view markdown preview + dev server (`pnpm dev`). For full visual preview, flip to a CMS with native preview (Tina, Decap with media-library, Payload). |
| **No multi-user real-time collab.** Git-based; merge conflicts on simultaneous edits. | Hard | Use sequential editing (one person edits, commits, pushes; next person pulls then edits). For real-time, flip to Notion-as-CMS or Payload. |
| **No fine-grained permissions.** Repo write access = full edit rights. | Hard | Use git branch protection + PR review for limited "edit-via-PR" workflows. For role-based permissions, flip to Payload / Sanity / Strapi. |
| **No scheduled publishing built-in.** | Soft | Implementable via CI cron + dated frontmatter + a `scheduled` branch (per CRUD vocabulary above). Native scheduled publish only via Payload / Ghost / Decap-with-workflow. |
| **No member-only content / paywalls / subscriptions.** | Hard | That's Ghost or Payload territory. Flip CMS at phase 12. |
| **Search is build-time only.** | Soft | Implement via **Pagefind** (build-time index, ~300KB for 10k pages) / Lunr (client-side) / Algolia (hosted). Pagefind is the recommended muggle default. WebFetch verified live at https://pagefind.app (2026-05-20). |
| **No revision history beyond git.** Git log IS the history; no UI for non-git-savvy editors. | Hard | Use GitHub's web UI for browsing history (works for muggles). For per-page revision viewer, build a static "history" page via custom build step. For non-git revision UI, flip to Payload. |
| **Rich-text editing limited to markdown's expressiveness.** No drag-drop block editor. | Hard | Markdown + MDX (Astro / Next.js) extends to embedded components. For drag-drop blocks, flip to Tina / Payload / Sanity / Decap-with-rich-text-widget. |
| **Image management is filesystem.** No transformations / variants without explicit build-time scripts. | Soft | Astro's built-in image optimization (`<Image>` component, automatic responsive variants); Hugo's image processing (resize, crop, fit); 11ty's `eleventy-img` plugin. All handle most muggle needs. For full DAM, flip to Cloudinary integration. |
| **Build times slow on huge sites.** Hugo handles 50k pages in seconds; Astro / Gatsby start to crawl past few thousand. | Soft (stack-dependent) | Switch to a faster builder (Hugo > Astro > Next.js for raw build speed). For content > ~5k pages, the agent surfaces a stack-change suggestion. |
| **No webhook receivers / server-side endpoints.** | Hard | Add serverless functions (Vercel / Netlify / Cloudflare Workers) per-need. The CMS layer stays file-based; dynamic surfaces are added per the stack-adapter's serverless story. |
| **No editor mobile workflow.** Editing on a phone is painful. | Hard | github.dev / GitHub Codespaces gives a browser-based editor that works on tablets / iPad. For phone-first authoring, flip to a CMS with a mobile app (Forestry/Tina had mobile; Decap has limited mobile-web). |

### Common failure modes

The agent's authoring discipline addresses these proactively; the lint hooks catch most automatically:

- **Build fails on bad frontmatter.** Pre-commit hook prevents; CI is backstop.
- **Image references 404 in production.** `lint:images` walks references.
- **Markdown renders raw HTML weirdly.** `lint:smart-quotes` sanitizes pre-commit.
- **YAML frontmatter parsing fails.** YAML lint catches missing delimiters / bad indentation.
- **Per-locale file drift.** Session-start hook walks for completeness per Decision 41.
- **Slug collisions.** Lint detects two files claiming the same slug.
- **Pre-commit hook bypass.** User commits with `--no-verify`. CI build re-runs lint as backstop.
- **Deploy succeeds but site shows old content.** CDN cache. Agent's deploy purges cache (Cloudflare API call) automatically.
- **Editor opens wrong project.** Agent generates `{site-name}.code-workspace` file so VS Code restores per-project state.

## context7 lookups for this CMS

Per Lock-3 freshness pattern. The agent re-validates the chosen static-site framework's API surface at each phase entry, NOT just at scaffold time. Re-fetch threshold: **30 days** per locked Lock-3 norm. Cache home: `.website-builder/library/docs/cms-none-{framework}.md`.

### Phase-by-phase context7 invocations

| Phase | Framework | Library ID | Query template |
|---|---|---|---|
| 12 (CMS decision — confirms stack pairing) | Astro | `/withastro/docs` | "Astro Content Collections + Zod schema validation; per-language file naming or per-language folders" |
| 12 | Hugo | `/gohugoio/hugo` | "Hugo content management; data files; archetypes; native i18n with per-language content folders" |
| 12 | 11ty | `/11ty/eleventy` | "Eleventy data cascade; markdown frontmatter; I18nPlugin per-locale strings" |
| 17 (design system) | per stack | (same IDs) | "{framework} CSS variable theming; @theme inline pattern OR equivalent; dark-mode strategy" |
| 18 (component build) | per stack | (same IDs) | "{framework} component conventions; slot patterns; image optimization" |
| 22 (i18n / forms) | per stack | (same IDs) | "{framework} per-locale routing; language switcher; hreflang emission" |
| 24a (commerce, if transactional) | per stack | (same IDs) | "{framework} Stripe Checkout integration; client-side cart; serverless function patterns" |
| 28 (deploy) | per stack | (same IDs) | "{framework} Vercel / Netlify / Cloudflare Pages deploy; build hooks; environment variables" |

### Cache discipline

- Cache file naming: `.website-builder/library/docs/cms-none-{framework}.md` (e.g., `cms-none-astro.md`, `cms-none-hugo.md`, `cms-none-11ty.md`).
- Cache rotation: re-fetch when stale (>30 days since file mtime) OR when phase entry signals "verify current API".
- Cache format: free-form markdown extracted from context7 response, with header noting `Cached YYYY-MM-DD by {callsign}`.

### MCP availability audit (per round-3 MCP audit doctrine)

The agent checks for relevant MCP servers at phase entry. Findings as of **2026-05-20** (Captain-I audit):

| MCP | Status | Source | Use case |
|---|---|---|---|
| **Astro Docs MCP** (`withastro/docs-mcp`) | ✅ exists | https://github.com/withastro/docs-mcp | Live access to Astro documentation via MCP for AI tools (Cursor, VS Code, Claude). Recommended at phase 12 / 17 / 18 / 22 when stack is Astro. Equivalent to context7 for Astro-specific queries; either works. |
| **Astro project-aware MCP** (community) | ✅ exists | https://github.com/morinokami/astro-mcp | Project-context MCP for Astro development. Mounts at `http://localhost:4321/__mcp/sse` as an Astro integration. Useful at phase 18 component-build. |
| **Hugo MCP** (community) | ✅ exists | https://github.com/SunnyCloudYang/hugo-mcp | Community-built Hugo MCP with site / theme / deploy management. Official Hugo MCP request is open (https://github.com/gohugoio/hugo/issues/14747) — not yet released. Use community fork when stack is Hugo. |
| **11ty MCP** | ❌ no canonical MCP found | (none) | Searched 2026-05-20 via WebSearch — no canonical Eleventy MCP server. Agent uses context7 `/11ty/eleventy` directly. |
| **Pagefind MCP** | ❌ no canonical MCP found | (none) | Searched 2026-05-20 — no dedicated MCP. Agent uses Pagefind via its standard CLI (`npx pagefind --site dist/`) at build time. |
| **markdownlint MCP** (`ernestgwilsonii/markdownlint-mcp`) | ✅ exists | https://github.com/ernestgwilsonii/markdownlint-mcp | Auto-fixes 30/52 official markdownlint rules. Useful when wiring `lint:content` / pre-commit. Recommended at phase 18 wire-up if user wants AI-assisted lint fixes. |
| **mcp-server-markdown** (`ofershap/mcp-server-markdown`) | ✅ exists | https://github.com/ofershap/mcp-server-markdown | Searches and extracts from markdown directories. Useful at phase 6.5 ingestion when reverse-mapping existing markdown trees. |
| **Image-optimization MCP** | ❌ no canonical MCP found | (none) | Astro / Hugo / 11ty all have built-in image optimization (`<Image>`, Hugo image-processing, `eleventy-img`). No need for external MCP. |
| **git operations MCP** (`mcp__jules-local__git_manage`) | ✅ bundled | (jules-local) | Already in the bundled plugin's MCP servers. The CRUD vocabulary's "create / edit / publish" verbs route through this — the agent uses `mcp__jules-local__git_manage` for commit + push operations on the user's behalf. |
| **filesystem MCP** (`mcp__jules-local__file_manage`) | ✅ bundled | (jules-local) | Already in the bundled plugin. The agent uses this for markdown file CRUD at phase 18 / 6.5 / mid-project edits. |

Negative findings (11ty MCP, Pagefind MCP, image-optimization MCP) are documented to save future agents redundant searches. If the user installs the optional Astro / Hugo / markdownlint MCPs, the agent surfaces availability at phase 12 and routes operations through them when applicable.

## References

Foundation design-doc paths (vault-root-relative per `vault-workstreams.md` link standard):

- `Workstreams/website-builder/cms/DESIGN-cms-none.md` — source design doc (this adapter's primary source)
- `Workstreams/website-builder/foundation/DESIGN-architecture.md` — `cms-adapters/` directory placement
- `Workstreams/website-builder/foundation/DESIGN-content-layers.md` — the 5-layer content stack `## Content layer mapping` maps
- `Workstreams/website-builder/foundation/DESIGN-i18n.md` — i18n model + Decision 38/39/40/41 defaults
- `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` — phase 12 (CMS decision) + phase 22 (forms/i18n/transactional) + phase 24a/b/c (commerce branching) + phase 6.5 (ingestion)
- `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` — `.website-builder/` layout the migration recipe mirrors
- `Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md` — phase 6.5 mechanism

Cross-adapter references (Phase 3 + Phase 4 substrate):

- `cms-adapters/README.md` — the 12-section schema this adapter conforms to + cross-CMS × stack compatibility anchor (verdict words for `## Stack pairings` table)
- `adapters/README.md` — Phase 3 stack-adapter contract; `## Content layer mapping` row labels MUST match this adapter's table
- `adapters/stack-framer.md`, `adapters/stack-nextjs.md`, `adapters/stack-wordpress.md` — Phase 3 stack adapters; `## CMS pairing` sections cross-reference `cms-none` for their own pairing verdicts (Framer N/A, Next.js Possible, WordPress N/A)
- `commerce-adapters/README.md` — Phase 4 sibling Captain 0 schema for commerce + booking adapters
- `commerce-adapters/payment-config-schema.md` — canonical `payment-config.yaml` schema for commerce pairings (TWINT-via-Stripe-on-CHF)
- `tests/cms-adapters/README.md` — per-CMS-adapter test fixture convention; `tests/cms-adapters/none/` is the matching fixture set
- `i18n/strings-schema.md`, `i18n/language-switcher.md`, `i18n/hreflang.md`, `i18n/rtl.md` — Phase 3 i18n substrate referenced by `## i18n integration`
- `handoff-spec/component-request-v1.md`, `handoff-spec/component-output-v1.md` — Phase 3 handoff contracts (referenced at phase 6.5 JSON round-trip)

External references:

- Astro Content Collections: https://docs.astro.build/en/guides/content-collections/
- Astro i18n recipe: https://docs.astro.build/en/recipes/i18n/
- Astro Docs MCP: https://github.com/withastro/docs-mcp
- Hugo Content Management: https://gohugo.io/content-management/
- Hugo Multilingual: https://gohugo.io/content-management/multilingual/
- 11ty Data Cascade: https://www.11ty.dev/docs/data-cascade/
- 11ty I18n Plugin: https://www.11ty.dev/docs/plugins/i18n/
- Pagefind (build-time search): https://pagefind.app
- VS Code Markdown All in One: https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one
- gray-matter (Next.js frontmatter parser): https://github.com/jonschlinkert/gray-matter
- markdownlint MCP: https://github.com/ernestgwilsonii/markdownlint-mcp

Cached context7 snapshots (re-fetch threshold 30 days):

- `.website-builder/library/docs/cms-none-astro.md` — Astro Content Collections + Zod + i18n
- `.website-builder/library/docs/cms-none-hugo.md` — Hugo content + frontmatter + i18n
- `.website-builder/library/docs/cms-none-11ty.md` — Eleventy data cascade + I18nPlugin
