---
phase: 9
name: Sitemap
group: content-foundation
pipeline_section: content-foundation
prev_phase: 8
next_phase: 10
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/foundation/DESIGN-project-scaffold.md
  - Workstreams/website-builder/foundation/DESIGN-content-layers.md
---

# Phase 9 — Sitemap

> Decide what pages exist and their hierarchy. The last phase of content-foundation; the bridge into architecture (phase 10 nav, phase 11 stack). Produces `sitemap.yaml` — the structural backbone every later phase composes against. The discipline: every page earns its existence by contributing to the phase-3 conversion.

## Mission

By phase 9 the user has a purpose (1), a vision (2), requirements with a single conversion outcome (3), an entity (4), a voice (5), captured content (6), a usable-asset audit (7), and an image plan (8). Phase 9 turns all of that into the site's structural skeleton: which pages exist, what type each is, what each is for, and how they nest.

The output is `.website-builder/sitemap.yaml` — a list of pages each with: URL slug, page-type (home / about / service-detail / blog-index / blog-post / contact / legal / etc.), purpose (one sentence), primary conversion contribution, and parent (for breadcrumb hierarchy). This is the document phase 10 (information architecture / nav) builds nav from, phase 13 (content per page) writes a content brief per entry of, and phase 26 (SEO) generates `sitemap.xml` from.

The discipline of phase 9: every page must justify its existence against the phase-3 conversion. The agent challenges pages that don't contribute. The default failure is the user wanting 47 pages because every idea feels like it deserves a page; the agent surfaces the maintenance cost and pushes toward fewer-richer pages. A 5-page site that converts beats a 30-page site nobody finishes building. This is not minimalism for its own sake — it is the recognition that every page is a maintenance liability, a content debt (phase 13-16), and an attention split (against the phase-3 1:1 conversion focus).

## Entry conditions

Phase 8 is complete. `.website-builder/media/IMAGE-PLAN.md` exists with the known-now image set methodized (`status: strategy-set` or later); the user confirmed it. `current_phase: 9` is set.

Inputs in scope (all load-bearing here): phase-1 idea (the site's purpose constrains what pages it needs), phase-3 requirements (the single conversion outcome is the test every page must pass; the audience persona shapes which pages matter; competitors inform expected page conventions), phase-4 entity (legal pages depend on jurisdiction — imprint mandatory in DACH, etc.), phase-6 inventory + phase-8 image plan (content/imagery availability constrains realistic page count). The agent rereads the phase-3 conversion outcome before opening the phase-9 conversation — it is the gating test for every proposed page.

For non-greenfield entry modes, a sitemap may have been partially extracted via phase 6.5 (a deployed site's page structure). The agent presents the extracted structure as a *starting point to challenge*, not a structure to preserve — the existing site's 30 pages are exactly the over-structuring phase 9 exists to question. The user decides what survives the conversion test.

## What Claude must establish

The work product is `.website-builder/sitemap.yaml`:

1. **Page list.** Every page that will exist at v1. Each page has:
   - `slug` — the URL path (`/`, `/about`, `/work/project-a`, `/contact`, `/privacy`)
   - `type` — page-type enum (`home` / `about` / `service-index` / `service-detail` / `work-index` / `work-detail` / `blog-index` / `blog-post` / `contact` / `pricing` / `legal` / `landing` / `utility`)
   - `title` — the page's working title
   - `purpose` — one sentence: what this page accomplishes for the user
   - `conversion_contribution` — how this page moves a visitor toward (or supports) the phase-3 single conversion outcome. Every page must have one; "informational only" is challenged.
   - `primary_cta` — the one action this page drives (can reference `{strings.cta.NAME}`; aligns with the phase-3 conversion)
   - `parent` — for breadcrumb hierarchy (`/` for top-level; `/work` for `/work/project-a`)
   - `sections` — *deferred to phase 13*; phase 9 establishes the page exists + its purpose, not its section composition

2. **Hierarchy.** Parent-child relationships forming the breadcrumb + IA tree. Phase 9 establishes the *tree*; phase 10 decides how the tree maps onto nav zones (primary / footer / utility).

3. **Legal-page set.** Driven by phase-4 jurisdiction + phase-3 (transactional flag is set at phase 11, but phase 9 reserves the slots): privacy policy always; imprint if DACH; terms if applicable; cookie-consent page if tracking integrations planned. Phase 9 reserves the slugs; phase 25 authors the content.

4. **Page-count justification.** A short rationale: why this many pages, why not fewer, why not more. Surfaced when the count is contested (it usually is).

Output schema (`.website-builder/sitemap.yaml`):

```yaml
---
type: sitemap
created_at: 2026-05-18T18:40:00Z
page_count: 7
conversion_outcome: book-discovery-call   # mirrors project.yaml.requirements.conversion_outcome.action
status: sitemap-locked                     # sitemap-draft | sitemap-locked
phase: 9
---

pages:
  - slug: /
    type: home
    title: "Home"
    purpose: "Introduce the practice + drive a qualified visitor to book a discovery call"
    conversion_contribution: "Primary conversion surface — hero CTA is the book-call action"
    primary_cta: "{strings.cta.book_call}"
    parent: null

  - slug: /work
    type: work-index
    title: "Work"
    purpose: "Show real projects; build credibility for the book-call decision"
    conversion_contribution: "Trust-builder; every project page ends with the book-call CTA"
    primary_cta: "{strings.cta.book_call}"
    parent: /

  - slug: /work/project-a
    type: work-detail
    title: "Project A"
    purpose: "Deep credibility on one representative project"
    conversion_contribution: "Proof; closes the 'can they do this for me' question"
    primary_cta: "{strings.cta.book_call}"
    parent: /work

  - slug: /about
    type: about
    title: "About"
    purpose: "Establish the practitioner is real + the discipline is the value"
    conversion_contribution: "De-risks the engagement; humanizes before the call"
    primary_cta: "{strings.cta.book_call}"
    parent: /

  - slug: /contact
    type: contact
    title: "Contact"
    purpose: "The conversion endpoint — book the call"
    conversion_contribution: "The conversion itself"
    primary_cta: "{strings.cta.book_call}"
    parent: /

  - slug: /privacy
    type: legal
    title: "Privacy Policy"
    purpose: "Legal compliance (GDPR/revFADP — jurisdiction CH per phase 4)"
    conversion_contribution: "Trust signal; legally required"
    primary_cta: null
    parent: /

  - slug: /imprint
    type: legal
    title: "Imprint"
    purpose: "Legally mandatory in CH/DACH (phase 4 jurisdiction)"
    conversion_contribution: "Legally required; trust signal"
    primary_cta: null
    parent: /

page_count_rationale: |
  7 pages: 1 home (conversion surface), 1 work-index + 1 representative
  work-detail (credibility), 1 about (de-risk), 1 contact (conversion
  endpoint), 2 legal (privacy + imprint, jurisdiction-mandatory). The user
  initially wanted a services breakdown (5 service pages), a blog, and a
  testimonials page; we collapsed services into the home + about narrative
  (the practice is the practitioner, not a service catalogue), deferred the
  blog to a phase-32 roadmap item (content cadence is a post-launch
  commitment, not a launch blocker), and folded testimonials into the
  work-detail pages (proof reads stronger next to the work it describes).
```

## Gating rules

The agent refuses to advance to phase 10 (information architecture / nav strategy) under three conditions:

1. **A page with no conversion contribution.** Every page must contribute to the phase-3 conversion (directly drive it, build trust toward it, or be legally/structurally mandatory). When the user wants a page that does none of those — *"I just want a page about my philosophy because I have things to say"* — the agent challenges it: *"What does this page do for the book-call conversion? If it builds trust toward the call, it earns its place — but then its job is trust-building and it ends with the CTA. If it's purely self-expression with no conversion role, it's a maintenance liability (phase 13-16 content debt, an attention split against the single conversion) for no return. Three options: (a) fold the philosophy into the about page where it builds trust in context; (b) keep it as a page but give it a conversion job (philosophy → 'this is how I work' → book a call); (c) defer it to a post-launch blog (phase 32 roadmap). Which?"* The agent does not forbid the page; it forces it to earn its existence or be honestly classified.

2. **Page sprawl without justification.** When the page count is high (the agent's heuristic threshold scales with site type — a brochure site over ~10 pages, a content site over ~15 top-level sections — but the rule is judgment, not a hard number) and the user resists collapsing, the agent refuses to lock the sitemap without a `page_count_rationale` that survives scrutiny. The agent surfaces the maintenance cost concretely: *"30 pages means 30 content briefs (phase 13), 30 wireframes (phase 14), 30 sets of section content (phase 15), 30 rounds of copywriting (phase 16), 30 pages to keep current forever (post-launch). Most of these 30 don't move the book-call conversion. Which 6-8 actually do? The rest become 'fewer, richer' — collapsed into the ones that convert, or deferred to a post-launch roadmap."* The user can keep a high count, but only with an explicit rationale the agent records (and the agent will have surfaced the true cost).

3. **Missing legally-mandatory pages.** When the phase-4 jurisdiction requires legal pages (imprint in DACH; privacy under GDPR/revFADP/CCPA; cookie-consent when tracking is planned) and the sitemap omits them, the agent refuses. These slots are non-negotiable per the agent's anti-vision lock. The agent reserves the slugs at phase 9 even though phase 25 authors the content: *"Your phase-4 jurisdiction is Switzerland — imprint is legally mandatory, not optional. Privacy is required under revFADP + GDPR (your audience includes EU). I'm reserving `/imprint` and `/privacy` in the sitemap now; phase 25 writes their content. They can't be dropped."*

The override path applies for *page-count* (the user can keep a large site with a recorded rationale and the agent's cost-surfacing on record) and for *non-mandatory pages* (a philosophy page with a weak conversion story can stay if the user insists, recorded as such). The override path does NOT apply to legally-mandatory pages — those are part of the anti-vision lock and are not skippable; the agent can only adjust *when* their content is authored (phase 25), never *whether* they exist.

## Tools and skills used

- **`Read`** — `project.yaml` (idea, vision, requirements, entity, languages), `media/IMAGE-PLAN.md` (image availability constrains realistic page ambition), `inbox/INVENTORY.md` (content availability constrains page count — a blog with no posts isn't a launch page). The phase-3 conversion outcome is reread before the phase-9 conversation.
- **`AskUserQuestion`** — the dominant tool. Every proposed page is interrogated for conversion contribution; every collapse/defer decision is the user's; the page-count rationale is built conversationally.
- **`WebFetch`** — to load competitor sitemaps (from phase-3 competitor URLs) when the user wants to benchmark structure: *"two of your phase-3 competitors have this structure — worth comparing what they include and what you can skip."* Used to ground page-convention expectations (a consulting site is expected to have a work/case-study surface; a SaaS is expected to have pricing), not to copy.
- **`Write` / `Edit`** — author and iterate `.website-builder/sitemap.yaml`; author the page-count rationale.

No `context7` (no library docs at this phase — stack is decided at phase 11, not 9; the sitemap is stack-agnostic per the architecture's stack-late-binding property). No Playwright (competitor structure is surface-fetchable). No image-gen (phase 8 owns that; phase 9 only references the plan to scope realistic ambition). Subagent spawn only for parallel competitor-sitemap scans when the user wants to benchmark several at once; default in-person.

The sitemap produced here is **stack-independent** by design — per `DESIGN-architecture.md`'s stack-late-binding property, all pre-phase-11 artifacts (including this sitemap) survive a later stack change. The agent does not bake any stack assumption into `sitemap.yaml` (no `.astro` / `.tsx` route hints — those are phase-12+ migration-recipe concerns).

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/sitemap.yaml` | Sitemap per schema above | The structural backbone; load-bearing for phase 10 (nav built from the tree), phase 11-12 (stack/CMS scoped to the structure), phase 13 (one content brief per page), phase 14 (one wireframe per page), phase 19 (one route per page), phase 26 (sitemap.xml generated from this), phase 27 (QA walks every page here) |
| `.website-builder/decisions/09-sitemap-scope.md` *(conditional — created when page-count was contested)* | Decision-doc frontmatter + alternatives considered + reasoning | Records the collapse/defer decisions (e.g., "5 service pages → folded into home+about; blog → phase-32 roadmap; testimonials → into work-detail") so phase 13+ and the post-launch maintainer know what was deliberately deferred vs forgotten |

The `sitemap.yaml` is the required artifact. The scope-decision doc is created whenever the agent challenged page count and the user made collapse/defer choices — which is most of the time, since page sprawl is the default failure. The doc matters because phase 32 (iteration roadmap) and the post-launch maintainer's `page-add` skill need to know which deferred pages were *intentional roadmap items* vs *out of scope forever*.

The agent updates `.website-builder/project.yaml.current_phase` to `10` upon user confirmation that the sitemap is locked (`status: sitemap-locked`), every page has a conversion contribution (or an explicit recorded override), and legally-mandatory slugs are reserved. Phase 10 (information architecture / nav strategy) loads next — the first phase of the architecture group, owned by LT-2's batch.

## Common failure modes

**The user wants 47 pages.** Every idea became a page: 8 service pages, a blog, a resources hub, a team page (for a solo practice), a press page, a careers page (no openings), an FAQ, a glossary. The agent surfaces the cost and pushes fewer-richer: *"47 pages is 47 content briefs, 47 wireframes, 47 copywriting passes, and 47 pages to keep current forever — most of which don't move your book-call conversion. Let's test each against the conversion. The 8 services: does a prospect need 8 separate pages, or does one strong 'how I work' narrative + work examples convert better? (Usually the latter — service-page sprawl reads as a catalogue; a focused practice reads as a specialist.) The blog: do you have a content cadence commitment, or is it aspirational? (If aspirational, it's a phase-32 roadmap item, not a launch page — an empty blog hurts more than no blog.) Team page for a solo practice: that's the about page. Press/careers/glossary: zero conversion contribution at v1 — roadmap them. I think this is a 6-8 page site. Let's find which 6-8."*

**The user insists every page is essential.** The agent does not override the user's authority but makes the cost undeniable and reframes around the conversion: *"You're the authority on what the site needs — I won't cut a page you're sure about. But let's be precise about what 'essential' costs and earns. For each page you call essential, tell me the one sentence: how does this move someone toward booking a call? If you can say it cleanly, the page earns its place and that sentence becomes its `purpose` + `conversion_contribution`. If the sentence is a stretch, that's the signal — not that I'm right, but that the page's job isn't clear yet, which makes phase 13-16 (its content) unanchored. Let's go page by page."* This converts the argument from "fewer pages" (the agent's preference) to "every page has a clear job" (the discipline) — a frame the user can engage with.

**The user wants a blog but has no content + no cadence commitment.** The agent surfaces the empty-blog failure: *"A blog at launch with two posts and no posting cadence reads worse than no blog — it signals 'abandoned' on the third visit. Two honest options: (a) launch with no blog; add it at phase 32 (iteration roadmap) when you have a real cadence commitment and a backlog of posts; (b) launch with a blog only if you commit now to a cadence and we treat the first 6-8 posts as phase-16 copywriting deliverables (real work, real scope). Aspirational blogs are the most common post-launch rot. Which?"* Records the decision in the scope doc so phase 32 knows the blog is a *planned* deferral.

**The user under-structures — wants a single one-page site for something that needs more.** The inverse failure. A consulting practice with 4 distinct service lines + a body of case-study work wants everything on one scroll. The agent surfaces: *"A one-pager can work — but with 4 service lines + a case-study body, a single scroll either buries the depth (visitors don't scroll past the fold to find what convinces them) or becomes an endless page (which reads as unstructured). The conversion test: can a prospect evaluating you find the proof they need before they lose patience? If the proof is deep, it usually wants its own surface (a /work index + detail pages) that the home page points to. Not 30 pages — but probably more than 1. What does your specific buyer need to see before they'd book?"* Under-structuring is challenged with the same conversion test as over-structuring.

**Non-greenfield: the extracted sitemap from phase 6.5 has 30 pages.** The agent presents it as a starting point to challenge, not preserve: *"Your old site had 30 pages — phase 6.5 extracted the structure. That extraction is a record of what *was*, not a constraint on what *should be*. Most site rebuilds are also a structure-prune: which of these 30 actually earned visits + moved conversions on the old site (your analytics know)? Which were content debt nobody maintained? The new site is the version you want now. Let's run the 30 through the conversion test the same as if they were proposals."* The prior structure gets no special preservation weight.

**The user wants pages whose content doesn't exist and isn't planned.** A "Resources" page, a "Case Studies" hub, a "Press" page — but phase-6 inventory has no resources, no case studies written, no press. The agent connects the sitemap to content reality: *"This page needs content that doesn't exist yet and isn't in the phase-6 inventory or phase-8 image plan. Three honest options: (a) the content gets created as phase-16 deliverables (real scope — are you committing to writing the 5 case studies?); (b) the page is deferred to a phase-32 roadmap item (launch without it; add when content exists); (c) drop it. A page in the sitemap with no path to content becomes a phase-13 dead end. Which?"*

**The user forgets legally-mandatory pages.** No imprint on a Swiss site; no privacy on a site with an analytics integration planned. The agent reserves them non-negotiably (per gating rule 3 + the anti-vision lock): *"Two pages are missing that aren't optional. Your phase-4 jurisdiction is Switzerland: imprint is legally mandatory. You're planning analytics (phase-3 requirements) + an audience that includes the EU: a privacy policy is required under revFADP + GDPR, and a cookie-consent surface is needed. I'm reserving `/imprint`, `/privacy`, and `/cookie-consent` slugs now — phase 25 writes the content with your actual data-handling facts. These can't be dropped; they can only be authored later. Acknowledged?"*

**The user mixes page-type confusion (treats a section as a page or vice versa).** *"I want a Testimonials page and a Pricing page and a Team page and a Process page."* The agent disambiguates page-vs-section: *"Some of these are pages; some are stronger as sections. Testimonials: usually stronger as a section *next to the work it describes* (proof reads weaker isolated on its own page). Process: often a section on the about or a service page, not a standalone (a lone 'process' page rarely gets visited). Pricing: a real page if pricing is a conversion-relevant decision surface; a section if it's one number. Team: a section on about for a small practice; a page only for a larger org. The test is: would a visitor navigate *to* this deliberately, or encounter it *within* a page they came for? Let's sort these."* This shapes the sitemap (pages) vs feeds phase 13-15 (sections).

## Reference materials

- **Design doc — phase pipeline source:** `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 9 (seed for this contract)
- **Design doc — pipeline integration + stack-late-binding:** `Workstreams/website-builder/foundation/DESIGN-architecture.md` § Stack-agnostic output design (why `sitemap.yaml` is stack-independent and survives a phase-11 stack change) + § Phase contracts
- **Design doc — sitemap.yaml schema:** `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` § `sitemap.yaml` (the canonical structure phase 9 produces; note phase 9 establishes pages + hierarchy + purpose; `sections:` per page is deferred to phase 13, and `navigation:` zones are phase 10's job)
- **Design doc — structural-layer placement:** `Workstreams/website-builder/foundation/DESIGN-content-layers.md` § Layer 2 — Structural specs (sitemap.yaml is Layer 2; the agent touches it at phases 9-10; phase 13-15 add the per-page section composition; phase 18 generates code from it)
- **Design doc — downstream consumers:** phase 10 (nav from the tree), phase 11-12 (stack/CMS scoped to structure), phase 13 (content brief per page), phase 14 (wireframe per page), phase 19 (route per page), phase 26 (sitemap.xml generated), phase 27 (QA walks every page) — all in `DESIGN-phase-contracts.md`; note phases 10-16 are LT-2's batch — the sitemap is the hand-off artifact between this batch (LT-1) and the next (LT-2)
- **Input — phase-3 conversion outcome:** `project.yaml.requirements.conversion_outcome` (the single test every page must pass; the 1:1-attention-ratio discipline established at phase 3 carries into phase 9 — every page either drives or supports the one conversion)
- **Input — phase-4 jurisdiction (legal-page reservation):** `project.yaml.entity.location.jurisdiction` (DACH → imprint mandatory; EU → privacy + cookie-consent; the slugs are reserved at phase 9, content authored at phase 25)
- **Agent profile — anti-vision lock:** `${CLAUDE_PLUGIN_ROOT}/agents/website-builder.md` § What you do NOT do ("Skip mobile, accessibility, or legal pages" — legal-page slugs are non-negotiable, reserved here) + § Anti-pattern cheat sheet (the "fewer-richer pages" discipline; the agent challenges page sprawl without becoming a minimalism zealot — pages earn existence by conversion contribution, not by an arbitrary count)
