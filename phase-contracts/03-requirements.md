---
phase: 3
name: Requirements
group: discovery-strategy
pipeline_section: discovery-strategy
skill: wb-discovery
prev_phase: 2
next_phase: 4
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/foundation/DESIGN-ecosystem-catalog.md
---

# Phase 3 — Requirements

> Establish hard requirements — audience, conversion goal, competitors, positioning. The phase that converts *what the site is* and *what it feels like* into *who it is for*, *what it asks them to do*, and *how it differs from neighbors*.

## Mission

By phase 3 the user has an idea (phase 1) and a vision (phase 2). The agent now establishes the constraints those decisions have to satisfy in production. Three artifacts emerge:

1. A **primary audience** — one or two specific personas with named motivations, not "small business owners" or "anyone interested in our services". A 2026 B2B buying group has 6-10 decision-makers averaging 13 stakeholders per purchase; the agent does not pretend a single persona maps onto that reality, but it does force the user to name the *one* most-load-bearing buyer.
2. A **single conversion outcome** — the *one* thing the site is for. Book, buy, read, contact, subscribe. Current 2026 conversion-design consensus is a 1:1 attention ratio per page; the site overall composes around one primary conversion the agent surfaces explicitly here.
3. **3-5 competitor sites with positioning notes** — what each does, what they do well, where the user's site differs. Positioning emerges by contrast, not by assertion; you cannot describe your position until you can describe the neighbors' positions.

Requirements is the discipline phase that prevents downstream drift. Pages without an audience drift into "writing for ourselves". Sites without a conversion outcome drift into "informational" (which is a non-conversion in disguise). Sites without positioning notes drift into looking-like-competitors. Phase 3 forces the user to make these three load-bearing decisions before phase 4 (project entity), phase 5 (voice), and phase 9 (sitemap) lock structure around them.

## Entry conditions

Phase 2 is complete. `.website-builder/project.yaml.vision` exists with references, feel statement, and adjective set; the user has confirmed it. `current_phase: 3` is set.

The idea (phase 1) and vision (phase 2) are in scope as context. Audience suggestions that surface here are checked against the idea ("does this persona match the underlying purpose?"); competitor selection draws on the visual references from phase 2 ("you cited X.com as a visual reference — is X also a market competitor, or just a visual one?").

For non-greenfield entry modes, an existing site or AI-generated artifact may have implicit audience/conversion assumptions baked in (a "Get Started Free" CTA implies SaaS; a "Book a Call" CTA implies services). The agent surfaces those assumptions and asks the user to confirm they're still right, or to revise them.

## What Claude must establish

The work product has four parts, stored under `.website-builder/project.yaml.requirements`:

1. **Primary audience persona.** One persona with: role / occupation, the trigger that brings them to the site (the problem they're trying to solve), their evaluation criteria (what makes them say yes), the channel they arrived through (search? referral? social? direct?). Optional secondary persona with the same shape, ranked below primary.

2. **Conversion outcome.** The *one* thing the site is for, expressed as a single user action. Common shapes: book (a call / demo / appointment), buy (a product / subscription), read (sign up for newsletter / RSS), contact (form submission / email reply), subscribe (recurring product / community / service). The agent enforces *one* — never two or three.

3. **Competitor list with positioning notes.** 3-5 competitor URLs. Per competitor: one sentence on what they do, one sentence on where they're strong, one sentence on where they're weak or where the user's project differs. Format aligns with the kalungi-style competitive scoring (target market / product strength / pricing model / GTM strategy).

4. **Positioning summary.** One paragraph extracting the user's distinct position from the competitor contrasts. *"We are the [category] that [distinct mechanism] for [primary audience] who [motivation], unlike [competitor] which [their tradeoff]."* The agent helps the user shape this; the user owns the words.

Output schema:

```yaml
requirements:
  captured_at: 2026-05-18T15:12:00Z
  primary_audience:
    persona_name: "Maya, Editorial Director at a mid-size cultural magazine"
    trigger: "Annual content-strategy planning; senior leadership pushing for a digital-first refresh"
    evaluation_criteria:
      - "Track record with editorial brands"
      - "Voice + design discipline visible in portfolio"
      - "Budget transparent before discovery call"
    likely_arrival_channel: search-via-portfolio
  secondary_audience:
    persona_name: "Solo designer-developers in Maya's network considering subcontract"
    trigger: "Maya mentions her freelancer in their channel"
    evaluation_criteria: ["Reads as a real practitioner; not a marketing site"]
  conversion_outcome:
    action: book-discovery-call
    one_sentence: "The one thing this site exists to do is convert a qualified prospect into a 30-minute discovery call."
  competitors:
    - url: https://competitor-a.com
      what_they_do: "Generalist web-design freelance practice; broad client list"
      strong_at: "Polished portfolio; named clients"
      where_user_differs: "We specialize in editorial + brand-led sites; they're stack-agnostic generalists"
    - url: https://competitor-b.com
      what_they_do: "Agency-shaped; 5-person team"
      strong_at: "Project management; predictable timelines"
      where_user_differs: "We work solo and stay closer to the writing; agency overhead changes the relationship"
    - url: https://competitor-c.com
      what_they_do: "Template-led service productized at a price point"
      strong_at: "Low-friction onboarding; transparent pricing"
      where_user_differs: "We refuse templates; the discipline is the product"
  positioning:
    paragraph: |
      We are the solo design + build practice for editorial-and-brand-led
      organizations that want a site they can read, modify, and maintain
      themselves — unlike agencies which keep the keys, unlike productized
      services which ship a template, unlike generalist freelancers who
      pick whatever stack feels current that month.
  iteration_count: 3
```

## Gating rules

The agent refuses to advance to phase 4 (project entity) under four conditions:

1. **"Everyone is the audience".** When the user names no primary audience or names a category so broad it cannot guide any downstream decision ("anyone who needs a website", "small business owners", "creators"), the agent refuses. The agent surfaces the cost: phase 13-16 (content) will produce generic copy; phase 17 (design system) will produce neutral-by-default tokens; the site will resemble its competitors because it isn't speaking to anyone specific. The agent then probes: *"If you imagine the perfect person reading your site on the perfect day — who is that person? What just happened in their life? What did they type into search?"* If the user still cannot specify, the agent walks through the persona-construction frame (role / trigger / evaluation criteria / channel) one field at a time.

2. **No conversion outcome, or multiple competing outcomes.** When the user says "people will read about us and then decide what to do" — that is a non-conversion. When the user says "they should sign up for the newsletter AND book a call AND buy the course" — that is three sites in one. The agent enforces one. The agent surfaces the 2026 1:1-attention-ratio consensus and the cost of multiple CTAs (split attention; lower per-CTA rate; ambiguous brand promise) and asks the user to rank: *"If you could only have one outcome — the user could only do one thing on the site — which one is the foundation? The others can exist; they're just secondary CTAs that compose around the primary."*

3. **Zero competitor research.** When the user cannot name three competitors — or names three but cannot articulate what they do — the agent refuses. Positioning is impossible without comparison; the agent surfaces this and walks the user through competitor sourcing: WebSearch the user's category, ask the user "who do clients mention as alternatives?", ask "who do you find yourself frustrated with in this space?". The agent helps but does not pick the competitors itself — the user's perception of the field matters more than an objective scan.

4. **Positioning-as-marketing-slogan.** When the user writes a positioning paragraph that reads as a slogan ("We're the best in the business", "Cutting-edge solutions for forward-thinking clients"), the agent refuses. Slogan-positioning gives downstream phases nothing to compose against; phase 5 (voice) will inherit the slogan's emptiness; phase 16 (copywriting) will produce more of the same. The agent reflects: *"That sentence could be said by anyone in this category. What does it mean for *you* specifically? What is the mechanism that makes 'best' or 'cutting-edge' actually different in your hands?"* The positioning paragraph must include at least one specific mechanism (what the user does differently) and at least one named neighbor it differs from.

The override path applies — the user can advance with under-defined audience or vague positioning and the agent flags downstream consequences (phase 5 voice will lean default; phase 13-16 content will be hard to scope; phase 27 polish will discover what's missing too late).

## Tools and skills used

- **`AskUserQuestion`** — heavy use, especially for persona construction and conversion-outcome ranking. Used at every gating decision in this phase.
- **`WebFetch`** — to load each competitor URL the user names, summarize the visible positioning (header copy, primary CTA, hero claim, pricing visibility), and feed the summary back to the user for confirmation. The agent reads competitors, not just lists them.
- **`WebSearch`** — used when the user cannot name competitors or wants to broaden the scan ("are there competitors in this space I might be missing?"). Industry-specific positioning frameworks (B2B research questionnaire patterns; named methodologies like Kalungi's competitive scoring; the prospeo / product-marketing-alliance persona templates) are surfaced when the user wants structured templates instead of conversational extraction.
- **`Read`** — to read `.website-builder/project.yaml.idea` and `.vision` at phase entry; to read any prior artifact's audience/CTA hints when entry mode is non-greenfield.
- **`Write` / `Edit`** — to update `.website-builder/project.yaml` with the captured requirements.
- **Reference-data load** — the agent may surface 2026 B2B persona templates and conversion-design playbooks when the user wants structured guides (catalogued in `.website-builder/library/seo-checklists/` and external resources cited in `Reference materials`).

No subagent spawn by default. When the user wants a parallel competitor scan ("WebFetch all 5 competitor sites at once and summarize each"), the agent may spawn a research subagent — but the default is sequential, in-conversation, so each competitor becomes a real anchor for the positioning discussion.

No context7 (no library docs needed at this phase). No Playwright (competitor sites are surface-fetchable; phase 6.5 owns deep walks).

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/project.yaml` | adds `requirements:` key per schema above | Audience + conversion + competitors + positioning; load-bearing for phases 4-9, 13-16, 24-26, 31 |
| `.website-builder/library/competitor-scan-<date>.md` *(when load-bearing)* | One section per competitor with full notes, screenshots, CTA inventory | Persists detail beyond what fits in `project.yaml`; referenced by phase 27 (polish/QA) to compare-and-contrast final site against the field |
| `.website-builder/decisions/03-positioning.md` *(optional)* | Standard decision-doc frontmatter + body | Created when the positioning paragraph went through 3+ rewrites or had contested tradeoffs (e.g., "premium positioning vs accessible positioning" — both could work; user picked one) |

The requirements block in `project.yaml` is the required artifact. The competitor-scan file is created when more detail emerges than fits cleanly in YAML; when 3 competitors are clean, they live entirely inside `project.yaml.requirements.competitors`.

The agent updates `.website-builder/project.yaml.current_phase` to `4` upon user confirmation. Phase 4 (project / company info) loads next.

## Common failure modes

**The user lists four audiences and refuses to rank.** *"I sell to enterprise, mid-market, SMB, and freelancers."* The agent forces a primary + secondary ranking: *"Each audience needs different copy, different proof points, different conversion paths. Trying to serve all four on one page produces a page that converts none of them. Which one represents the largest revenue today? Which one represents the easiest sale right now? Which one represents the future growth bet? The site picks one of those; the others become secondary."* The agent does not allow phase advancement until one is named primary and the others have explicit secondary or "future" ranking.

**The user names "everyone interested in X" as the audience.** *"Anyone who cares about sustainable fashion."* The agent refuses + reflects: *"'Anyone' is the absence of a choice. Who is the most-likely buyer? Someone who already buys sustainable fashion and is upgrading? Someone considering their first purchase? Someone gifting? Pick one — the others become secondary."* The persona-construction frame surfaces (role / trigger / evaluation criteria / channel) and the agent walks the user through it one field at a time.

**The user names a conversion outcome that is actually three CTAs.** *"They should sign up for the newsletter and book a discovery call and download the white paper."* The agent reflects on 2026 conversion design: *"The 1:1 attention ratio research is consistent — every additional clickable action lowers conversion on the primary. Your three options are all legitimate, but the site needs to *lead* with one. Which is the load-bearing one for revenue? The others can exist on the page; they just stop being the primary CTA in the hero."* The user picks; secondaries get the explicit-secondary tag.

**The user lists "competitors" that are visually similar but in adjacent markets.** A B2B SaaS lists three consumer apps because they admire the design. The agent surfaces: *"Those are visual references — we captured them in phase 2. Phase 3 competitors are the alternatives your buyer compares you against when deciding. Who does your buyer call when they consider not choosing you? Who do they mention in discovery calls?"* The agent helps separate visual neighbors from market neighbors.

**The user cannot name any competitors and insists "we're first to market".** The agent gently pushes back: *"There's almost always something a buyer considers as 'not buying you'. Spreadsheets. The status quo. A different category of solution. An internal team building it themselves. Who does the buyer compare you to in their head?"* The "competitors" may not be direct product competitors — they can be substitutes, status quo, or alternative spend. The agent records whatever the user genuinely compares against.

**The user writes a positioning slogan that could be anyone's.** *"We deliver world-class solutions that empower our clients to succeed."* The agent refuses and reflects: *"Every neighbor in this category could write that sentence. What does *world-class* mean in your hands specifically? What is the mechanism? What is the named alternative you're choosing not to be?"* The agent helps the user replace generics with specifics by asking the questions the slogan answers in the abstract.

**The user wants the agent to "just write the positioning".** *"You're better at marketing copy than me — write a positioning statement."* The agent refuses: *"This is the one sentence where your voice has to lead. If I write it, it inherits my voice, not yours, and phase 5 (brand voice) won't have an anchor that's actually you. I can help you sharpen — give me a rough draft, even one sentence, and I'll show you where it's specific and where it's still generic."*

**The competitor URL the user names returns a 404 or major redirect.** The agent surfaces: *"That URL didn't load — looks like the competitor changed domains or shut down. Want to point at the current version, or treat this as 'former competitor' and pick a different one?"* Dead competitors can still be relevant historical neighbors; the agent honors that with `seen_via: archive` or `status: defunct` in the schema.

## Reference materials

- **Design doc — phase pipeline source:** `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 3 (seed for this contract)
- **Design doc — pipeline integration:** `Workstreams/website-builder/foundation/DESIGN-architecture.md` § Phase contracts
- **Design doc — competitor reference catalogue:** `Workstreams/website-builder/foundation/DESIGN-ecosystem-catalog.md` § Reference resources (competitor + inspiration source list)
- **External research (loaded fresh 2026-05-18 for this contract):**
  - B2B 2026 positioning + persona framework — https://prospeo.io/s/product-positioning-b2b (positioning vectors as 1-10 axes across target market / product strength / pricing model / GTM strategy)
  - B2B 2026 buyer persona playbook — https://prospeo.io/s/b2b-buyer-persona-research (role / decision authority / evaluation criteria / information sources / proof points)
  - Kalungi B2B SaaS competitor research template — https://www.kalungi.com/blog/b2b-saas-competitor-research (kickoff template with competitive scoring matrix)
  - Conversion-Rate-Optimization 2026 guide — https://www.luckyorange.com/blog/posts/conversion-rate-optimization-guide (macro-conversion definition; revenue-tied primary outcomes)
  - 1:1 attention-ratio research — https://technologyaloha.com/conversion-focused-web-design-ultimate-guide/ (single primary CTA; every additional link lowers conversion)
  - Hubspot CRO strategy 2026 — https://blog.hubspot.com/marketing/conversion-rate-optimization-guide
  - Product Marketing Alliance B2B persona template — https://www.productmarketingalliance.com/b2b-persona-questions-template-framework/
- **Gartner 2026 B2B context:** the average B2B purchase involves ~13 stakeholders with 6-10-person buying groups, ~89% of decisions cross departments — agent surfaces this when the user wants to over-simplify "the audience" into a single individual purchaser
- **2026 AI-discovery context (LLMs as first brand interpreter):** ChatGPT now commands ~84% of trackable AI discovery traffic — relevant to the positioning paragraph because LLMs read it and represent it to buyers in conversational search; the paragraph must read coherently to a model as well as a human (informs phase 26 SEO + schema.org)
