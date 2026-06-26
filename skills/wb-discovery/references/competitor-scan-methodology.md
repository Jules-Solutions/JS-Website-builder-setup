# Competitor-scan methodology — phase 3 (Requirements)

> Loaded on demand when running phase 3 competitor research. The phase contract (`phase-contracts/03-requirements.md`) is authoritative for *what* phase 3 produces and the gating rules; this file carries the *current methodology* for the scan itself. Researched fresh 2026-05-18 — see Sources at bottom.
>
> The phase-3 contract already cites a richer external-research list (prospeo / Kalungi / CRO guides / Gartner B2B context). This file distills the methodology into a runnable scan procedure so the agent does not reinvent it each project.

## When this fires

Phase 3 needs 3-5 competitors with positioning notes + a positioning paragraph extracted by contrast. The user often cannot name competitors cleanly, or names visual neighbors (phase-2 territory) instead of market neighbors. This methodology gives the agent a structured scan to run *with* the user — not a scan to run *for* the user (the user's perception of the field is the load-bearing input; the agent helps surface and structure it).

## Step 1 — Categorize competitors into three tiers

Do not treat all competitors equally. Categorize:

- **Primary (direct):** offers a substitutable solution to the same buyer for the same job. The buyer actively compares these to the user.
- **Secondary (indirect):** solves the same job a different way, or serves an adjacent buyer. The buyer might consider these instead of buying the category at all.
- **Tertiary (substitute / status quo):** spreadsheets, internal teams, doing nothing, a different category of spend. In B2B this is frequently the *real* competition and users routinely forget it.

Ask the user: *"Who does your buyer call when they consider NOT choosing you? Who do they mention in discovery? What do they do today instead?"* The status-quo answer is often the most diagnostic.

**The ~5 rule:** target about five competitors total across tiers. Quality over quantity — five well-understood neighbors beat fifteen shallow ones. The phase-3 contract enforces a 3-5 minimum; this methodology says do not exceed ~5 either.

## Step 2 — Read the high-value pages (not the whole site)

For each competitor, `WebFetch` the pages that reveal strategic posture. Do not crawl the whole site. The high-signal set:

1. **Home page** — the primary claim + hero CTA + who they say they're for
2. **Pricing page** — pricing model, transparency, packaging, anchor tiers (or its absence — hidden pricing is itself a signal)
3. **Product / features pages** — what they emphasize as the differentiator
4. **About / team page** — company shape (solo / agency / funded startup), origin posture
5. **Blog / press / changelog** — recent strategic shifts, what they're investing in

Feed each summary back to the user for confirmation: *"Competitor A leads with [hero claim], CTA is [X], pricing is [visible/hidden/model]. Does that match how you see them?"* The agent reads competitors; it does not just list URLs.

## Step 3 — Score with a structured matrix

Capture per competitor (Kalungi-style competitive scoring shape, aligned with the phase-3 schema):

| Axis | What to capture |
|---|---|
| Target market | Who they actually serve (vs who they claim) |
| Product strength | What they're genuinely strong at (one sentence) |
| Pricing model | Transparent / hidden / freemium / enterprise-quote / productized |
| GTM strategy | How they reach buyers (content / sales-led / PLG / partner / referral) |
| Where the user differs | One sentence — the contrast that defines the user's position |

This maps directly into `project.yaml.requirements.competitors[]` (`what_they_do` / `strong_at` / `where_user_differs`).

## Step 4 — Apply two analytical lenses

- **SWOT, per competitor and aggregate.** Document strengths / weaknesses / opportunities / threats. Prioritize the *gaps* — where every competitor is weak is the user's opportunity space.
- **Importance-Performance Analysis (IPA).** Map features/attributes on two axes: importance to the buyer (high/low) vs the user's performance vs competitors (high/low). High-importance + low-relative-performance = the urgent gap. High-importance + high-performance = the position to lead with in messaging.
- **Jobs-to-Be-Done breadth.** Force the vision wide: analyze primary rivals *and* indirect threats *and* substitutes through the lens of the job the buyer is hiring a solution to do. This is how the status-quo / spreadsheet / internal-build competitor surfaces — it does the same job differently.

## Step 5 — Extract positioning by contrast

Positioning emerges from the contrasts, never from assertion. Help the user write the phase-3 positioning paragraph in the shape:

> *"We are the [category] that [distinct mechanism] for [primary audience] who [motivation] — unlike [competitor A] which [their tradeoff], unlike [competitor B] which [their tradeoff]."*

The paragraph MUST contain at least one specific mechanism (what the user does differently) and at least one named neighbor it differs from. A paragraph that any competitor could also write is a slogan, not a position — the phase-3 contract refuses it. The agent helps sharpen; the user owns the words (cross-phase discipline rule 3 in SKILL.md).

## Cadence note (informational, not a phase-3 deliverable)

Modern guidance treats competitive analysis as a continuous system, not a one-off task — monthly for fast-moving signals (rankings, ads, content), quarterly for strategy shifts. Phase 3 produces the *founding* scan; this is worth mentioning to the user as a post-launch maintenance habit (it connects to the post-launch maintainer template's monitoring skill), but the phase-3 deliverable is the founding snapshot, not an ongoing dashboard.

## Common failure modes (methodology-specific; complements the contract's list)

- **User lists visual neighbors as competitors.** They admire three consumer apps' design and call them competitors. Separate: visual references are phase-2 territory (`project.yaml.vision`); phase-3 competitors are who the buyer compares against in a purchase decision. Ask the buying-decision question, not the admiration question.
- **User insists "we're first to market / no competitors."** There is almost always a substitute or status quo. Push gently to the tertiary tier (spreadsheets / internal build / different category / doing nothing). Record what the user genuinely compares against, even if it is not a product.
- **Competitor URL 404s / redirects.** Surface it; offer the current version or "former competitor" framing (`status: defunct` / `seen_via: archive` in the schema). A defunct neighbor can still be a relevant historical contrast.
- **User wants the agent to pick the competitors.** Refuse politely — the user's *perception* of the field is the load-bearing input. The agent can `WebSearch` the category to broaden the candidate set ("are there neighbors you might be missing?"), but the user decides who counts as a competitor.

## Sources (researched 2026-05-18)

- [How to Conduct a B2B Competitive Analysis (Webstacks)](https://www.webstacks.com/blog/b2b-competitor-analysis)
- [B2B SaaS Competitive Analysis: Guide, Frameworks, Tools (RAMPIQ)](https://rampiq.agency/blog/saas-competitive-analysis/)
- [Building Your First B2B Competitive Analysis: Step-by-Step Framework (SlashExperts)](https://slashexperts.com/post/building-your-first-b2b-competitive-analysis-step-by-step-framework-with-templates/)
- [Competitor analysis framework (The Growth Syndicate)](https://www.thegrowthsyndicate.com/resources/competitor-analysis-framework)
- [Kicking off B2B SaaS Competitor Research, with template (Kalungi)](https://www.kalungi.com/blog/b2b-saas-competitor-research)
- [Guide to Competitive Analysis Framework (Salesmotion)](https://salesmotion.io/blog/competitive-analysis-framework)
- Cross-referenced with the phase-3 contract's own external-research list (prospeo positioning + persona, Luckyorange CRO, 1:1 attention-ratio research, Gartner B2B buying-group context).
