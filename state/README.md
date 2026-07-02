# `.website-builder/` state directory

> Reference schema for every file and directory the website-builder plugin writes into the user's project.
> All paths below are relative to the user's project root (the directory where the user ran `wb`).
>
> Canonical design reference: `DESIGN-project-scaffold.md`

---

## Directory map

```
.website-builder/
├── project.yaml              # master project record — identity, phase, entry mode
├── brand.yaml                # design tokens + brand voice decisions
├── sitemap.yaml              # navigation tree + page inventory
├── components.yaml           # component library — shapes, slots, variants
├── tasks.yaml                # agent task ledger (internal; not surfaced directly to user)
├── keys.yaml                 # third-party API keys (write-once per project; never committed)
├── content/
│   ├── sections.yaml         # section blueprints — content architecture for each section
│   ├── pages/
│   │   └── {slug}.md         # one file per page — frontmatter + content outline
│   └── strings/
│       └── {lang}.json       # microcopy strings per language (default: en.json)
├── briefs/
│   └── {phase}-{slug}.json   # per-phase agent context snapshots
├── decisions/
│   └── {slug}.md             # architectural / design decisions with rationale
├── media/
│   ├── raw/                  # uploaded or linked originals
│   ├── processed/            # optimised/resized outputs
│   └── manifest.json         # catalogue of all media assets
├── audit/
│   ├── accessibility.json    # phase 21 output
│   └── performance.json      # phase 22 output
├── library/                  # auto-cloned reference corpora (populated by wb_library.py)
│   └── {slug}/               # one dir per corpus key
└── outputs/
    └── {slug}/               # per-phase rendered outputs (briefs, wireframes, etc.)
```

---

## File schemas

### `project.yaml`

Written by `wb-bootstrap` at project initialisation; updated by each phase on exit.

```yaml
# Identity
name: "Acme Studio"
slug: "acme-studio"
started_at: 2026-06-01T09:00:00Z
entry_mode: "greenfield"   # greenfield | has-existing-site | has-ai-output | has-framer-attempt | has-figma-file

# Progress
current_phase: 7           # integer — the next phase to execute
completed_phases: [1, 2, 3, 4, 5, 6]

# Idea (written at phase 1 exit)
idea:
  captured_at: 2026-06-01T09:15:00Z
  paragraph: |
    ...
  captured_via: conversation   # conversation | pasted-by-user | freewrite
  iteration_count: 2

# Stack (written at phase 11 exit)
stack: astro                   # astro | next | nuxt | svelte | html

# CMS (written at phase 12 exit)
cms: payload                   # payload | decap | none

# Component library (written at phase 18 during design)
component_library: shadcn      # shadcn | radix | headless-ui | custom | none

# Localisation (written at phase 4 exit if multilingual)
default_language: en
languages: [en, de]
```

**Required at bootstrap:** `name`, `slug`, `started_at`, `entry_mode`, `current_phase: 1`.
All other fields are added progressively by their authoring phase.

---

### `brand.yaml`

Written across phases 2 (vision), 5 (brand voice), and 17 (design system). Tokens section may be pre-seeded at phase 6.5 from extraction.

```yaml
# Vision direction (written at phase 2 exit)
vision:
  headline: "The tool serious textile artists reach for on deadline"
  feeling_words: [sharp, considered, unhurried]
  anti_patterns: [corporate, playful, trendy]

# Brand voice (written at phase 5 exit)
voice:
  archetype: "The expert friend"
  tone: [direct, warm, never-ironic]
  vocabulary:
    in: ["craft", "build", "make"]
    out: ["leverage", "synergy", "exciting"]

# Design tokens (seeded at 6.5 extraction or authored at phase 17)
tokens:
  colors:
    primary: "#1A1A2E"
    secondary: "#E94560"
    background: "#FAFAFA"
    surface: "#FFFFFF"
    text: "#1A1A1A"
    text-muted: "#6B7280"
  typography:
    heading: "Fraunces"
    body: "Inter"
    mono: "JetBrains Mono"
    scale:
      xs: "0.75rem"
      sm: "0.875rem"
      base: "1rem"
      lg: "1.25rem"
      xl: "1.5rem"
      "2xl": "2rem"
      "3xl": "3rem"
      "4xl": "4rem"
  spacing:
    unit: "4px"
    scale: [0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64]
  border_radius:
    sm: "2px"
    base: "4px"
    lg: "8px"
    full: "9999px"
```

Tokens marked `status: extracted-pending-review` when seeded by phase 6.5. Confirmed at phase 17 by removing the status key.

---

### `sitemap.yaml`

Written at phase 9 exit; extended at phases 10, 13, and 14.

```yaml
navigation:
  type: top-nav          # top-nav | hamburger | sidebar | none
  items:
    - label: "Home"
      slug: home
    - label: "Work"
      slug: work
    - label: "About"
      slug: about
    - label: "Contact"
      slug: contact

pages:
  - slug: home
    title: "Home"
    purpose: "Primary conversion entry — above-fold conviction"
    sections: [hero, problem-band, process, testimonials, cta]
    meta:
      title: "Acme Studio — handmade textile objects"
      description: "..."
  - slug: work
    title: "Work"
    purpose: "Portfolio proof — show, don't tell"
    sections: [gallery-grid, case-study-preview]
```

---

### `content/sections.yaml`

Written at phase 15 exit. One entry per section type the project uses.

```yaml
sections:
  hero:
    purpose: "First impression — orient and compel"
    components: [hero-block]
    slots:
      headline: string
      subline: string
      cta_label: string
      cta_href: string
      background: image-ref | video-ref | null
  problem-band:
    purpose: "Name the problem the visitor already has"
    components: [band-block]
    slots:
      headline: string
      body: markdown
  testimonials:
    purpose: "Third-party proof"
    components: [testimonial-grid]
    slots:
      items:
        - quote: string
          attribution: string
          avatar: image-ref | null
```

---

### `content/pages/{slug}.md`

One file per page. Written at phase 13 exit (content per page); content added at phases 15-16.

```markdown
---
slug: home
title: Home
phase: 13
status: draft                 # draft | reviewed | final
sections:
  - hero
  - problem-band
  - process
  - testimonials
  - cta
meta:
  title: "Acme Studio — handmade textile objects"
  description: "..."
---

## hero

Headline: "Handmade textile objects for people who care how things are made."
Subline: "Small runs. Long waits. Worth it."
CTA: "See the work" → /work

## problem-band

Headline: "The gifting market is full of things that look handmade and aren't."
...
```

`status: extracted-pending-review` is used when the file is seeded by phase 6.5 ingestion before the user has reviewed the content.

---

### `content/strings/{lang}.json`

Written at phase 16 exit (copywriting). Default: `en.json`. One file per language listed in `project.yaml.languages`.

```json
{
  "nav": {
    "home": "Home",
    "work": "Work",
    "about": "About",
    "contact": "Contact"
  },
  "footer": {
    "tagline": "Made slowly. Worth the wait.",
    "copyright": "© 2026 Acme Studio"
  },
  "cta": {
    "primary": "See the work",
    "secondary": "Get in touch"
  },
  "hero": {
    "headline": "Handmade textile objects for people who care how things are made."
  }
}
```

All languages must share the default language's key structure. Missing keys in non-default languages are warnings (not errors) at validation — the runtime falls back to the default language value. See cross-layer check 7.

---

### `components.yaml`

Written at phase 18 exit. One entry per component the project uses.

```yaml
components:
  hero-block:
    purpose: "Full-width hero section"
    variants: [with-image, with-video, text-only]
    props:
      headline:
        type: string
        ref: "{strings.hero.headline}"
      subline:
        type: string
        required: false
      background:
        type: image-ref | video-ref | null
      cta:
        label:
          type: string
          ref: "{strings.cta.primary}"
        href:
          type: string
    tokens_used:
      - "{tokens.colors.primary}"
      - "{tokens.typography.heading}"
      - "{tokens.spacing.scale[12]}"
    status: draft            # draft | spec-complete | built | tested
```

---

### `tasks.yaml`

Internal ledger written by the orchestrator. Not surfaced to the user in normal operation. Documents agent-tracked sub-tasks within and across phases.

```yaml
tasks:
  - id: wb-20260601-001
    phase: 17
    description: "Confirm color token: primary"
    status: done             # pending | in-progress | done | deferred
    decided_at: 2026-06-01T14:20:00Z
    decided_value: "#1A1A2E"
  - id: wb-20260601-002
    phase: 18
    description: "Build hero-block component"
    status: in-progress
```

---

### `keys.yaml`

Written by the user at session start when a phase requires a third-party API key. Contains only references — never literal key values.

```yaml
# keys.yaml — API keys for this project's integrations.
# This file is in .gitignore; never commit it.
# Each key is a vault reference or an env-var pointer.

divmagic_api_key: "${DIVMAGIC_API_KEY}"   # env var, set in shell
figma_token: "${FIGMA_TOKEN}"
```

**Never contains literal key values.** The file tells the agent where to look; the value is always in the shell environment or the user's 1Password vault.

---

### `briefs/{phase}-{slug}.json`

Agent context snapshots written at phase entry by the orchestrator. Contain the resolved inputs the agent needs for the phase: relevant decisions, state-file summaries, and the phase contract path.

```json
{
  "phase": 17,
  "slug": "design-system",
  "contract": "phase-contracts/17-design-system.md",
  "created_at": "2026-06-01T13:00:00Z",
  "inputs": {
    "vision_headline": "The tool serious textile artists reach for on deadline",
    "voice_archetype": "The expert friend",
    "tokens_draft": "brand.yaml.tokens (extracted-pending-review)"
  }
}
```

---

### `decisions/{slug}.md`

One file per significant architectural or design decision. Written when a choice is made that has non-obvious rationale or that constrains future phases.

```markdown
---
slug: ingest-2026-06-01
phase: 6.5
decided_at: 2026-06-01T09:30:00Z
affects_phases: [17, 18]
---

## Decision: color palette kept from Stitch extraction

Stitch extracted 6 colors from the existing site. All 6 are retained as-is rather than redesigning from scratch. Rationale: the user has existing printed materials (brochures, business cards) that use these exact colors. Rebuilding the palette would require reprinting.

Constraint: the token `primary` is `#2B4D66` — any component spec must treat this as fixed.
```

---

### `media/manifest.json`

Written at phase 7 (media asset audit) and updated as new assets are added.

```json
{
  "assets": [
    {
      "id": "hero-bg",
      "type": "image",
      "source": "raw/hero-bg-original.jpg",
      "processed": "processed/hero-bg-1920w.webp",
      "alt": "Close-up of hand-woven textile in natural light",
      "dimensions": { "w": 1920, "h": 1080 },
      "phase_added": 7
    }
  ]
}
```

---

### `audit/accessibility.json` and `audit/performance.json`

Written at phases 21 and 22. Structured audit results used as input to phase 27 (SEO + launch prep).

```json
{
  "phase": 21,
  "audited_at": "2026-06-15T10:00:00Z",
  "tool": "axe-core",
  "violations": [
    {
      "id": "color-contrast",
      "impact": "serious",
      "description": "...",
      "fix": "Increase contrast ratio of body text from 3.2:1 to 4.5:1"
    }
  ],
  "score": { "a11y": 87, "wcag_aa_violations": 2 }
}
```

---

### `library/{slug}/`

Auto-populated at phase entry by `wb_library.autoclone_for_state()`. Each slug corresponds to a key in `CATALOGUE_CLONE_KEYS` in `scripts/wb_library.py`. The library directory is the runtime copy of reference corpora; it is excluded from the user's project git history (added to `.gitignore` by `wb-bootstrap`).

| Key | Source type | Default subdir | Populated when |
|---|---|---|---|
| `brand-examples-corpus` | bundled | `brand-examples-corpus` | Phase 2 entry |
| `design-systems-corpus` | bundled | `design-systems-corpus` | Phase 2 entry |
| `voice-archetypes` | bundled | `voice-archetypes` | Phase 5 entry |
| `component-patterns` | bundled | `component-patterns` | Phase 13/15/16/21 entry |
| `seo-checklists` | bundled | `seo-checklists` | Phase 22/26 entry |
| `awesome-design-md-corpus` | bundled | `awesome-design-md-corpus` | Phase 17 entry |
| `astro-content-collections` | github-docs | `astro-content-collections` | Phase 11 entry (when: stack == "astro") |
| `payload-docs` | github-docs | `payload-docs` | Phase 12 entry (when: cms == "payload") |
| `decap-cms` | github-docs | `decap-cms` | Phase 12 entry (when: cms == "decap") |
| `shadcn-components` | github-docs | `shadcn-components` | Phase 18 entry (when: component_library == "shadcn") |
| `awesome-design-md` | github-repo | `awesome-design-md` | Phase 17 entry (upstream HEAD) |

Idempotent: if a library directory already exists and is non-empty, `autoclone_for_state` skips it (`status: "skipped"`). Conditional keys with a `when:` predicate are only cloned when the predicate matches `project.yaml`.

---

### `outputs/{slug}/`

Per-phase rendered outputs. Examples:

- `outputs/wireframes/` — ASCII wireframe markdown files from phase 14
- `outputs/briefs/` — human-readable phase summary docs
- `outputs/build/` — generated code (written by build phases 18-20)

---

## Cross-layer validation checks

The 7 checks run by `wb_validate_layers.py` (`scripts/wb_validate_layers.py`), called at action 4 of each phase and on session start. All 7 checks are **skip-on-absent**: if the file being validated doesn't exist yet, the check is a no-op (not an error). A greenfield project with only `project.yaml` passes with zero findings.

| # | Check | What it validates | Error type |
|---|---|---|---|
| 1 | **Parse** | All YAML / JSON / MD layer files that exist parse without syntax errors | Hard error |
| 2 | **Page frontmatter schema** | Every file in `content/pages/` has a `slug:` field in its frontmatter | Hard error |
| 3 | **String refs resolve** | All `{strings.x.y.z}` references in `components.yaml` and `sections.yaml` resolve to a key in the relevant `content/strings/{lang}.json` | Hard error |
| 4 | **Section refs resolve** | All section names listed in `content/pages/{slug}.md` frontmatter `sections:` exist as entries in `content/sections.yaml` | Hard error |
| 5 | **Component refs resolve** | All component names listed in `content/sections.yaml` entries exist in `components.yaml` | Hard error |
| 6 | **Token refs resolve** | All `{tokens.x.y}` references in `components.yaml.tokens_used` resolve to a key path in `brand.yaml.tokens` | Hard error |
| 7 | **Cross-language key parity** | Every key present in the default-language strings file (`en.json`) is present in every other language file | Warning only (runtime falls back to default-language value per Decision 41) |

Findings are returned as human-readable strings with concrete fix paths. An empty list means everything that exists is internally consistent.

**Invocation:**

```python
from scripts.wb_validate_layers import validate_content_layers

findings = validate_content_layers(project_root=Path(".website-builder"))
for f in findings:
    print(f)
```

**CLI:**

```bash
python scripts/wb_validate_layers.py              # human-readable output
python scripts/wb_validate_layers.py --json       # JSON array
```

---

## Progressive authoring contract

The state files are written one layer at a time across the phase pipeline. No file is complete at phase 1. At any given phase, the validator should be quiet — it only checks references among files that already exist.

| Phase | Files written / extended |
|---|---|
| Bootstrap | `project.yaml` (identity fields), `.gitignore` (excludes `library/`, `keys.yaml`, `outputs/`) |
| 1 (idea) | `project.yaml.idea` |
| 2 (vision) | `brand.yaml.vision` |
| 4 (project info) | `project.yaml.languages`, `project.yaml.default_language` |
| 5 (brand voice) | `brand.yaml.voice` |
| 6.5 (ingestion) | `brand.yaml.tokens` (draft), `sitemap.yaml` (draft), `content/pages/*.md` (draft), `components.yaml` (draft), `decisions/ingest-{ts}.md` |
| 7 (media audit) | `media/manifest.json` |
| 9 (sitemap) | `sitemap.yaml` (authoritative) |
| 11 (stack) | `project.yaml.stack` |
| 12 (CMS) | `project.yaml.cms` |
| 13 (content per page) | `content/pages/{slug}.md` (authoritative) |
| 15 (content per section) | `content/sections.yaml` |
| 16 (copywriting) | `content/strings/{lang}.json` |
| 17 (design system) | `brand.yaml.tokens` (confirmed) |
| 18 (components) | `components.yaml` (authoritative), `project.yaml.component_library` |
| 21 (accessibility) | `audit/accessibility.json` |
| 22 (performance) | `audit/performance.json` |
| All phases | `tasks.yaml` (ongoing), `briefs/{phase}-{slug}.json` (per phase), `decisions/` (as decisions are made) |
