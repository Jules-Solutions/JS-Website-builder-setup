---
phase: 4
name: Project / company info
group: discovery-strategy
pipeline_section: discovery-strategy
skill: wb-discovery
prev_phase: 3
next_phase: 5
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/foundation/DESIGN-project-scaffold.md
---

# Phase 4 — Project / company info

> Capture the underlying entity — person, company, project — that the site represents. The phase that names the *who* behind the site, the concrete assets they already hold, and the verifiable facts that ground the project in reality.

## Mission

Phases 1-3 established the abstract: what the site is for, what it feels like, who it's for. Phase 4 grounds it in the concrete. Behind every site is a real entity — a person, a company, a project, a collective — with a name, a what-they-do, an origin, a location, existing channels, and (often) some pile of pre-existing assets. The agent extracts those facts before any content phase begins, because every piece of downstream content composes from them.

The output is a structured entity record in `.website-builder/project.yaml.entity`. Name; one-sentence what-they-do; origin/founding context; location (city + country + jurisdiction, the latter load-bearing for phase 25 legal); contact channels; inventory of existing assets (logo file? domain owned? social handles? email list? old site? Figma library?). The agent does not invent. The agent does not let the user invent — unless the project is explicitly framed as a fictional / portfolio / speculative piece.

This phase is short relative to phases 1-3, but it is load-bearing in a specific way: the answer to *"what is your jurisdiction"* drives phase 25 (legal pages — imprint mandatory in DACH; cookie consent required under ePrivacy + GDPR for EU users); the answer to *"do you own the domain"* drives phase 28 (domain + DNS + SSL); the inventory of existing assets drives phase 6 (content capture) and phase 6.5 (ingestion).

## Entry conditions

Phase 3 is complete. `.website-builder/project.yaml.requirements` exists with audience + conversion + competitors + positioning; the user has confirmed it. `current_phase: 4` is set.

The phase 1-3 outputs are in scope. The agent rereads the idea + positioning paragraphs before opening the phase 4 conversation — the entity name needs to read as the same voice as the positioning ("Maya & Co" reads differently from "MK Editorial Group"; both could be right, but the choice matters).

For non-greenfield entry modes, prior artifacts often contain entity hints (existing logo in `inbox/`, prior domain in `has-existing-site` mode metadata, contact email in a copied page). The agent surfaces those and asks the user to confirm or correct.

## What Claude must establish

The work product is a structured entity record stored under `.website-builder/project.yaml.entity`:

1. **Entity name.** What the site calls the underlying entity. May or may not match a legal business name — phase 4 records both when they differ ("Trading-as-X for the public; legally Y GmbH").
2. **One-sentence what-they-do.** Specific verbs + specific outcomes + (optionally) specific audience. Not "We help businesses succeed" — *"We design and build editorial sites for cultural magazines and brand-led organizations."*
3. **Origin / founding context.** When did this start? Why? The story behind why-it-exists, captured in 2-4 sentences. Not for the home page yet (phase 16 owns copywriting) — for downstream content phases as raw material.
4. **Location.** City + country + jurisdiction. The jurisdiction is load-bearing — DACH (Germany / Austria / Switzerland) has mandatory imprint laws; EU has cookie consent + GDPR; Switzerland has revFADP; US has state-specific commerce + privacy regimes. The agent does not advise legally; it captures jurisdiction accurately so phase 25 can compose legal pages correctly.
5. **Contact channels.** Email, phone (if applicable), social handles (LinkedIn, Instagram, Twitter/X, Mastodon, Bluesky, GitHub, etc. — only the ones the entity actually uses, not aspirational ones). The agent asks which are public-facing and which are internal-only.
6. **Existing assets inventory.** A structured list of what already exists: logo file (path / URL / status — final or draft?); domain (owned? registered with whom? expires when?); brand colors (locked elsewhere or open?); fonts (licensed? open-source?); old site (URL? to be ingested via phase 6.5?); social presence (handles + follower counts only if relevant to phase 3 secondary audience); email list (size + provider); prior client testimonials (where stored?); existing photography (rights cleared?); existing copy (where? to be ingested via phase 6?).

Output schema:

```yaml
entity:
  captured_at: 2026-05-18T15:45:00Z
  name: "Maya Klein"
  legal_name: "Maya Klein Design (sole proprietor)"  # only when differs from display name
  what_they_do: "Maya designs and builds editorial sites for cultural magazines and brand-led organizations as a solo practitioner."
  origin:
    started_year: 2019
    context: |
      Started after five years inside a magazine's in-house design team;
      Maya kept getting pulled into web-implementation work and found the
      intersection of editorial + web was where her work was sharpest.
      Went independent in 2019.
  location:
    city: Zurich
    country: Switzerland
    jurisdiction: CH
    languages_spoken: [DE, EN, FR]
  contact:
    public_email: hello@example.com
    public_phone: null  # entity does not publish phone
    social:
      - platform: instagram
        handle: "@example"
        url: "https://instagram.com/example"
        relevance: "primary visual portfolio surface"
      - platform: linkedin
        handle: example
        url: "https://linkedin.com/in/example"
        relevance: "professional network; warm intros"
  existing_assets:
    logo:
      status: final
      file: assets/logo-original.svg
      formats: [svg, png-1x, png-2x]
    domain:
      owned: true
      domain: example.com
      registrar: cloudflare
      expires: 2027-04-15
    brand_colors:
      status: open  # open | locked-elsewhere | not-yet-defined
    fonts:
      status: not-yet-defined
    old_site:
      exists: true
      url: https://old.example.com
      ingest_planned: true  # phase 6.5 will run; user confirmed
    photography:
      status: partial
      notes: "Maya has ~30 portfolio images cleared for use; needs 5 more (current sites)"
    email_list:
      exists: false
    prior_testimonials:
      exists: true
      location: "scattered across LinkedIn recommendations + 3 PDF deliverable letters in Dropbox"
      access_path: "user will copy into .website-builder/inbox/ during phase 6"
  fictional_or_portfolio: false  # set true only if user explicitly frames as fictional
  iteration_count: 1
```

## Gating rules

The agent refuses to advance to phase 5 (brand voice & tone) under three conditions:

1. **Fabricated entity passed off as real.** When the user invents a company name, location, origin story, or asset that does not exist — and the project is not explicitly framed as fictional — the agent refuses. The agent reflects: *"I don't think this site represents an entity that actually exists. The address you gave doesn't match any company by this name; the social handles you named are unclaimed; the origin story has specific details that I can't verify. Is this a real project, or a portfolio / speculative / case-study piece? Either is fine — but I need to know which, because the legal pages, the contact form, and the deploy decisions all hinge on it."* If the user confirms the project is fictional / portfolio / speculative, the agent sets `entity.fictional_or_portfolio: true` and proceeds with appropriate caveats (no real contact email, no real domain assumption, no real jurisdiction-bound legal pages).

2. **Missing jurisdiction.** When the user cannot or will not name a location-and-jurisdiction, the agent refuses. The agent surfaces the cost: phase 25 (legal pages) cannot compose without it (imprint requirements differ per country; cookie consent law differs per region; commerce-specific legal in phase 24c is jurisdiction-bound). For Swiss / DACH users specifically, imprint is legally mandatory and non-trivial; for EU users, GDPR + ePrivacy compose into the cookie banner; for US users, state-by-state variability matters at phase 24c if transactional. The agent walks the user through naming the jurisdiction even when it's "I live in X but the business is registered in Y" — both go into the schema.

3. **Generic-description backslide.** When the user's one-sentence what-they-do reads as a slogan or marketing line ("We provide world-class solutions to forward-thinking clients"), the agent refuses. The agent reflects: *"That sentence could fit any neighbor. What's the specific verb? Who specifically does it apply to? Look at phase 3's positioning paragraph — the entity description should have the same level of specificity."* The phase 3 positioning paragraph is the anchor; the entity what-they-do is its shorter sibling.

The override path applies. The user may proceed with fictional framing (legitimate), missing jurisdiction (cost: phase 25 stalls until provided), or generic description (cost: phase 5 voice + phase 16 copywriting inherit the genericness).

## Tools and skills used

- **`AskUserQuestion`** — the primary tool. Used for the entity name, what-they-do extraction, origin story, location + jurisdiction, contact channels, and the existing-assets inventory walkthrough.
- **`WebFetch`** — used to verify entity claims when warranted. If the user names a domain they own, the agent fetches the homepage to confirm it resolves + reflects what's currently there. If the user names social handles, the agent (optionally, with user permission) fetches each profile to verify the handle is claimed and active. This is not surveillance — it's confirming the asset inventory matches reality before phases 6-9 compose around it.
- **`Read`** — to read `.website-builder/project.yaml.idea`, `.vision`, `.requirements` at phase entry; to read any prior artifact's entity hints when entry mode is non-greenfield (e.g., a copied "About" page from `has-existing-site` mode).
- **`Bash`** — for file inventory operations: when the user mentions a logo file or photo library, the agent uses `ls` + `file` to confirm the file exists, its format, and its size; updates the asset record accordingly.
- **`Write` / `Edit`** — to update `.website-builder/project.yaml.entity`.

No `WebSearch` mandate. No `context7`. No Playwright. No subagent spawns.

The agent does NOT run reverse-domain lookups, business registry queries, or any external verification beyond what the user explicitly confirms is OK. Phase 4 is about capturing what the user says exists; verification is courtesy, not investigation.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/project.yaml` | adds `entity:` key per schema above | Entity facts; load-bearing for phases 5, 6, 16, 25, 28, 31 |
| `.website-builder/inbox/INVENTORY.md` *(seeded)* | One row per existing asset with status (ready / needs-conversion / missing) | Pre-populates phase 6's content-capture inventory with the assets named here |
| `.website-builder/decisions/04-jurisdiction.md` *(optional)* | Standard decision-doc frontmatter + body | Created when the jurisdiction had complexity (e.g., user lives in CH but business is registered as a UK Ltd; both jurisdictions apply differently to legal pages) |

The entity block in `project.yaml` is the required artifact. The `inbox/INVENTORY.md` seed is created to bridge phase 4 → phase 6; the user is told this file exists and phase 6 will resume from it.

The agent updates `.website-builder/project.yaml.current_phase` to `5` upon user confirmation. Phase 5 (brand voice & tone) loads next.

## Common failure modes

**The user gives a generic what-they-do.** *"We help businesses succeed with cutting-edge solutions."* The agent reflects against phase 3 positioning: *"Your phase 3 positioning paragraph names a specific category, a specific mechanism, a specific audience. The what-they-do sentence should match that level of specificity. Let me try: based on your positioning, you design and build editorial sites for cultural magazines as a solo practitioner. Is that the version you'd say out loud?"* The agent offers a draft; the user revises.

**The user invents details.** *"My company is called Quantum Synergy LLC, based in Delaware, started 1995, with offices in 12 countries."* The agent gently probes: *"Some of those details don't match what we've discussed earlier — your phase 1 idea read like a solo practice. Is Quantum Synergy LLC the real entity behind this site, or is this a portfolio piece exploring what a different kind of company might look like? Either is fine; I just want to capture it accurately."* If the user backtracks ("OK it's just me — I was inflating"), the agent records the accurate version. If the user insists, the agent surfaces the gap and lets the user resolve.

**The user does not have a domain yet.** The agent records `domain.owned: false` and notes: *"We'll address domain acquisition at phase 28 (domain + DNS + SSL). For now, the agent uses a placeholder URL in phase-9 sitemap and phase-26 SEO; phase 28 swaps in the real domain once you've registered it."* No blocking on this; just clear flagging.

**The user's logo is "I'll send it later" / a screenshot from another tool / not finalized.** The agent records `logo.status: draft` (or `pending`) and notes: *"Phase 17 (design system) needs a final logo to extract palette anchors from. If the logo is still pending at phase 17 entry, we'll either: (a) pause phase 17 until it lands; (b) treat the current draft as load-bearing knowing rework lands later; (c) run phase 17 without a logo anchor and revise on logo arrival. Which fits?"* The user picks; the agent records the choice for phase 17.

**The jurisdiction is dual or unclear.** User lives in Switzerland, business is registered as a UK Ltd, primary customer base is German. The agent captures all three: *"Three jurisdictions matter for different phases. Swiss revFADP applies to your data handling (where you operate); UK Companies House rules apply to imprint-equivalent disclosures (legal home); German GDPR enforcement applies to your customers (audience location). Phase 25 will compose legal pages covering all three; phase 24c (if transactional) will need VAT handling for all three."* The agent records `jurisdiction: { operating: CH, legal: UK, audience_primary: DE }` and continues.

**The user names social handles aspirationally.** *"My Instagram is @example."* The agent (with permission) WebFetches `@example` and finds it claimed by someone else. The agent reflects: *"That handle appears to belong to someone else on Instagram. Did you mean a different handle, or do you want to acquire the handle as part of the launch prep? Phase 31 (launch announcement) is the natural place to address this."* The agent records the gap; the user resolves it.

**The "existing site" is actually a one-shot AI-generated page hosted on a Vercel preview URL.** The agent reflects: *"That URL looks like a preview / one-shot from v0 / Lovable / a similar tool. Treating it as 'existing site' implies stability; treating it as 'AI output' implies ingestion via phase 6.5. Which is closer to truth — is this site live serving real users, or is it a sketch from a tool you tried?"* The user clarifies; the entity record gets `old_site.status: ai-output-not-deployed` or `old_site.status: live-serving-users` accordingly.

**The user is uncomfortable sharing a real email or phone.** The agent honors privacy: *"You can use a separate routing address (hello@yourdomain.com forwarding to your real inbox) — phase 28 will set that up. For now, we record the routing address you intend to use; the real inbox stays private."* `contact.public_email` records the routing address; the real inbox is never captured.

**The user mentions a logo file that doesn't actually exist where they said.** Agent `ls` finds nothing at the claimed path. Agent reflects: *"I can't find that file at the path you gave. Is it in a different location, or still on a different machine?"* Records `logo.status: pending` with the user's note on retrieval. No blocking; phase 17 will resume from whatever state exists then.

## Reference materials

- **Design doc — phase pipeline source:** `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 4 (seed for this contract)
- **Design doc — pipeline integration:** `Workstreams/website-builder/foundation/DESIGN-architecture.md` § Phase contracts
- **Design doc — output location:** `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` § `project.yaml` (schema for the `entity:` key + the `inbox/INVENTORY.md` seed)
- **Design doc — jurisdiction-driven downstream:** `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 25 (legal pages) + § 24c (commerce legal) — what the jurisdiction field controls in phases 24-25
- **Library / external (when the user wants jurisdiction-mapping help):**
  - DACH imprint requirements (admin.ch source) — surfaced in phase 25; phase 4 only captures the jurisdiction
  - EU GDPR + ePrivacy interplay — surfaced in phase 25
  - Swiss revFADP overview — surfaced in phase 25
- **Agent profile — voice characteristics:** `${CLAUDE_PLUGIN_ROOT}/agents/website-builder.md` § Voice characteristics (the entity what-they-do sentence must read in the voice phase 5 is about to lock — the agent stays close to phase 3 positioning vocabulary)
