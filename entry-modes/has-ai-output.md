# Entry mode: has-ai-output

> The user generated a one-shot landing page using ChatGPT, Claude.ai, v0, Lovable, Bolt, or a similar AI tool. They now want to take that raw output and turn it into a real, intentional website — proper structure, brand voice, their own stack, their own content. The one-shot output is an artifact to ingest, not a design to copy.

## Who this is for

- Someone who used "build me a website" in an AI chatbot and got back an HTML/CSS file or a preview URL
- Someone who got a component scaffold from v0 and wants to build it out into a full site
- Someone whose freelancer delivered AI-generated HTML and they now need proper structure around it

The AI output is raw material. The agent does NOT continue building from it as if it were a finished design — it extracts the useful parts and routes them into the correct pipeline phases.

## Onboarding flow

At session start:

1. The agent sets `project.yaml.entry_mode = "has-ai-output"`.
2. The user pastes or provides the AI output: HTML file, pasted code block, or a live preview URL.
3. The agent confirms the output type (raw HTML / React JSX / v0 export / Lovable JSON / etc.).

Phase 6.5 fires immediately to ingest the artifact before phase 1.

## Phase 6.5 ingestion strategy

### Primary extractor: AI-output parser

The agent reads the pasted HTML / JSX / code directly using its code-reading capabilities (no external tool required). The parser extracts:

- **Design tokens**: `background-color`, `color`, `font-family`, `font-size`, `border-radius`, `padding` values pulled from inline styles or Tailwind class patterns → seeds `brand.yaml.tokens` (draft)
- **Component shapes**: identified heading + body + CTA slots per section → seeds `components.yaml` (draft)
- **Text strings**: all visible text content (headlines, body copy, CTA labels, microcopy) → seeds `content/pages/home.md` and `content/strings/{lang}.json` (draft)
- **Page structure**: section sequence and rough layout → seeds `sitemap.yaml.pages.home.sections` (draft)

### Secondary: divmagic (when element-precision is needed)

If the AI output is a live preview URL (v0 / Lovable / Bolt), the agent can use the divmagic API for element-precision extraction — capturing the exact CSS values for specific components rather than inferring from class names. The user provides a divmagic API key in `keys.yaml` if they have one; free tier is fetch-on-demand.

### What the parser does NOT extract

- **Visual intent** — AI-generated color palettes are often bland defaults. The extracted tokens are starting points for the phase-17 conversation, not decisions.
- **Brand voice** — AI-generated copy is generic by definition. Extracted strings flow into phase 6 (wild content capture) as raw material for phase-16 rewriting. They are NOT used as the final copy.
- **Architecture decisions** — the AI picked a stack (often React + Tailwind); the user chooses their stack at phase 11 independently of what the AI used.

### Conflict detection

If the user already has `brand.yaml` or `components.yaml` from a prior ingestion, the agent compares and surfaces conflicts (e.g., incoming primary color differs from established primary color). The user decides: keep current / use incoming / merge.

### Output files seeded

| Extracted artifact | Destination |
|---|---|
| Color / type / spacing tokens | `brand.yaml.tokens` (draft) |
| Section sequence | `sitemap.yaml.pages.home.sections` (draft) |
| Text content | `content/pages/home.md` + `content/strings/{lang}.json` (draft) |
| Component shapes | `components.yaml` (draft) |

## Resume point after ingestion

The pipeline starts at phase 1. Phases 2-5 run in full — the AI output tells you what the tool guessed; the conversation tells you what the user actually wants. The extracted tokens and copy are available as starting points that can be confirmed, adjusted, or discarded at each relevant phase. Phase 6 (wild content capture) can ingest additional sections the user generates later in external tools.
