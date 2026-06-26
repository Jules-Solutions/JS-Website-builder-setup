---
phase: 10
name: Information architecture / nav strategy
group: architecture
pipeline_section: architecture
skill: wb-architecture
prev_phase: 9
next_phase: 11
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/foundation/DESIGN-project-scaffold.md
  - Workstreams/website-builder/foundation/DESIGN-ecosystem-catalog.md
  - Workstreams/website-builder/foundation/DESIGN-i18n.md
---

# Phase 10 — Information architecture / nav strategy

> The pages exist on paper (phase 9). Now the agent decides how users find them — primary nav, footer nav, utility nav, breadcrumb logic, mobile pattern. This is the last stack-agnostic structural phase before the technology decisions in 11-12.

## Mission

The sitemap from phase 9 lists every page the site needs. Phase 10 turns that list into a navigational structure users can actually move through. The agent decides which pages live in the primary nav (the always-visible top-level menu), which collapse into a footer nav (legal / about-us / company-info / sitemap), which sit in a utility nav (language switcher / search / login / cart), and how breadcrumbs behave on pages nested more than one level deep. The phase also locks per-zone behaviors — active-state styling rules, dropdown-vs-flat decisions, the mobile pattern (hamburger / bottom-tab / inline / mega-menu).

Information architecture is where most muggle sites quietly fail. A user with 14 pages tries to put all 14 in the primary nav; the result reads as an inventory list, not a site. The agent's job in this phase is to surface hierarchy: which pages are headlines, which are sub-navigation, which are footer-only, which are reachable only via in-page links. Done right, phase 10 produces a `sitemap.yaml.nav` block that downstream phases consume without further architectural argument.

This is also the agent's last chance to challenge the sitemap from phase 9. If working through nav reveals that two pages are really one page with sections, or that a planned page has no path users could reach it through, the agent surfaces the inconsistency and re-opens phase 9 briefly to resolve it.

## Entry conditions

- Phase 9 (sitemap) complete. `.website-builder/sitemap.yaml` exists with at least the `pages:` list populated — every page has a slug, page-type, purpose, and parent.
- Phase 5 (brand voice) is complete; nav labels need to sound like the brand, not like a generic template.
- Phase 3 (requirements) is complete; the agent uses the primary conversion outcome (book / buy / read / contact / subscribe) to test whether each nav zone serves the conversion path or fights it.

## What Claude must establish

The agent and user together decide:

1. **Primary nav contents.** Which pages appear in the always-visible top nav. The agent enforces a soft ceiling of 5-7 items (see Gating rules); over 7, the agent forces the user to choose what becomes a dropdown group or moves to the footer.
2. **Primary nav order.** Left-to-right ordering. Convention is left-anchor on the brand name / logo, right-anchor on the primary CTA. Middle slots ordered by user-journey priority: most-likely-next-step first.
3. **Dropdown vs flat per primary-nav item.** Items that point to sub-pages (e.g., "Services" → 3 service-detail pages) either expand on hover/click (dropdown / mega-menu) or sit flat with the children reachable only via the parent page. Phase 10 picks per item.
4. **Footer nav contents.** Pages that should be reachable from anywhere but don't earn a primary slot: legal pages, imprint, careers, press, sitemap, social-media links, secondary CTAs. Footer nav can be longer (10-20 items grouped into columns).
5. **Utility nav contents.** Persistent UI affordances that aren't navigational in the page-to-page sense: language switcher (always present when the site is multilingual per phase 11/12), search, account / login / cart, "skip to content" accessibility link.
6. **Breadcrumb rules.** Required for any site deeper than 2 levels (home → category → item). The agent specifies which page-types render breadcrumbs and how the hierarchy is computed (from `sitemap.yaml`'s `parent:` field).
7. **Active-state behavior.** How the current page is indicated in nav: underline / color shift / weight change / pill. Brand-voice-consistent.
8. **Mobile pattern.** Hamburger menu (most common; works for most sites), bottom-tab nav (app-shaped sites with a few destinations), inline scrolling nav (very simple sites), or mega-menu collapse (complex multi-column nav patterns). The agent picks based on primary-nav count + site shape.

The agent does not write the navigation component code in this phase — that happens at phase 18 (component build) per the chosen stack. Phase 10 produces the structural spec the component will read.

## Gating rules

The agent refuses to advance when:

- **The primary nav has more than 7 items.** Hick's Law plus mobile-screen-width plus muggle scanning capacity all point at 5-7 as the working ceiling. When the user insists on more, the agent surfaces the trade-off — "every additional item halves the visibility of every other" — and forces a grouping decision (dropdowns, mega-menu, or move to footer). The agent does not refuse forever; it refuses once and surfaces the cost. The user can override with explicit confirmation.
- **A page in the sitemap has no path to reach it.** Every page must be reachable from somewhere — primary nav, footer nav, internal link from another page, sitemap.xml indexed by search engines. If a page is in `sitemap.yaml.pages` but the agent cannot map a user journey to it, the agent surfaces the inconsistency and either re-opens phase 9 (drop the page) or finds it a parent link.
- **The mobile pattern doesn't match the primary-nav count.** A 7-item primary nav in a bottom-tab pattern fails on small phones. The agent refuses the combination and offers compatible alternatives.
- **The language switcher is missing on a multilingual site.** If phase 11 or earlier has flagged the site as multilingual, the utility nav must include a language switcher. Phase 10 surfaces this even though the actual decision belongs to phase 11/12 — the IA must accommodate it.
- **Breadcrumbs are omitted on a deep site.** Sites with any page nested two or more levels deep (home → category → item, or home → service-group → service → sub-service) need breadcrumbs. The agent refuses to skip them; users without them get lost.

Override is available for any gating rule via explicit user confirmation. The agent surfaces the specific cost — typically "users will fail to find X% of pages" or "screen readers will not be able to orient on deep pages" — and waits for the user to say "yes, ship it anyway."

## Tools and skills used

- **AskUserQuestion** — the primary tool. Each of the 8 decisions above surfaces as one or more `AskUserQuestion` interactions. The agent presents the trade-offs concretely (with examples from reference sites in `.website-builder/library/brand-examples/` and `reference-corpus/inspiration/`) and lets the user pick.
- **Read** — agent reads `.website-builder/sitemap.yaml` to enumerate pages, parent relationships, and page-types.
- **Reference-data load** — `Workstreams/website-builder/foundation/DESIGN-ecosystem-catalog.md` for accepted IA patterns; `.website-builder/library/component-patterns/navigation.md` (when populated) for nav component archetypes; `.website-builder/library/seo-checklists/ia.md` for SEO-driven IA constraints (URL depth, breadcrumb schema, navigational page-naming for crawlability).
- **WebFetch** (occasional) — the agent may load a competitor or reference URL from phase 2 and walk its nav structure with the user, naming what works and what doesn't.

No `Write` / `Edit` on code files in this phase — those tools are gated until phase 18.

## Output artifacts

The agent writes one block to `.website-builder/sitemap.yaml` under a new `navigation:` key. Schema:

```yaml
# .website-builder/sitemap.yaml
pages: [...]  # from phase 9, unchanged

navigation:
  primary:
    items:
      - { label: "Home",     href: "/",         active_match: exact }
      - { label: "Services", href: "/services", active_match: prefix, dropdown:
          [
            { label: "Strategy",  href: "/services/strategy" },
            { label: "Build",     href: "/services/build" },
            { label: "Maintain",  href: "/services/maintain" }
          ]
        }
      - { label: "Essays",   href: "/essays",   active_match: prefix }
      - { label: "About",    href: "/about",    active_match: prefix }
      - { label: "Contact",  href: "/contact",  active_match: exact, variant: cta }
    style:
      active_state: "underline + weight-600"
      cta_variant: "primary-button"

  footer:
    columns:
      - heading: "Site"
        items:
          - { label: "Home",     href: "/" }
          - { label: "Services", href: "/services" }
          - { label: "About",    href: "/about" }
      - heading: "Legal"
        items:
          - { label: "Privacy", href: "/privacy" }
          - { label: "Terms",   href: "/terms" }
          - { label: "Imprint", href: "/imprint" }  # mandatory in DACH
      - heading: "Connect"
        items:
          - { label: "Email",    href: "mailto:hi@example.com" }
          - { label: "LinkedIn", href: "https://linkedin.com/in/..." }

  utility:
    items:
      - { kind: "skip-to-content", label: "{strings.nav.skip_to_content}" }
      - { kind: "language-switcher" }       # populated when multilingual per phase 11
      - { kind: "search", optional: true }  # configured at phase 24 if integrated

  breadcrumbs:
    enabled_for: [service-detail, blog-post, legal]   # page-types that render breadcrumbs
    home_label: "{strings.nav.home}"
    separator: "›"

  mobile:
    pattern: hamburger                    # hamburger | bottom-tab | inline | mega-menu
    breakpoint: 768
    drawer_position: right
    overlay_dim: true
```

The `{strings.nav.*}` references resolve from `content/strings/{lang}.json` at phase 16 (copywriting) — phase 10 declares the references; phase 16 supplies the values. This keeps the IA stack-agnostic and language-agnostic.

The agent does not write the navigation component code in this phase; that's phase 18 per the chosen stack. The component will read this `navigation:` block as its structural contract.

## Common failure modes

**"I want every page in the primary nav."** The most frequent failure. The user enumerates 14 pages and asks for all of them as top-level items. The agent's response: *"That ships, but it does this: users scan 14 items, find none of them obvious, and bounce. Five strong items beat fourteen weak ones every time. Which pages are first-contact pages, and which are reachable from somewhere else?"* The agent then walks through the pages by user-journey priority and groups the long tail into dropdowns or moves it to footer.

**"The hero CTA and the nav CTA should both say 'Get started.'"** Voice repetition reads as template-shaped. The agent surfaces the two roles: nav CTA is the always-visible commitment path (intent: "I'm ready"); hero CTA is the contextual one (intent: "tell me more first"). Different wording per role. Often the nav CTA stays generic ("Contact" / "Sign up") and hero CTA gets the brand-voice prose ("Let's talk" / "Start the trial").

**"Skip the breadcrumbs — my designer doesn't like them."** Breadcrumbs are not decoration; they are wayfinding for deep pages and structured-data anchors for search engines. The agent surfaces both costs (UX + SEO) and offers compromises: breadcrumbs scoped to only the deepest page-types (blog-post, service-detail) and styled small. The user can still override; the agent logs the override in `.website-builder/decisions/skip-breadcrumbs.md`.

**"What about a sticky nav?"** Sticky vs static is a per-site decision the agent surfaces at phase 17 (design system) or phase 18 (component build), not at phase 10. Phase 10 locks structure; visual behavior comes later. The agent defers the question.

**"My homepage is the contact page."** Some single-page sites map all sitemap entries to in-page anchor links (`/#about`, `/#services`, `/#contact`). The agent handles this as a degenerate IA case: primary nav becomes an in-page anchor jump menu; mobile pattern becomes inline scrolling nav. Surfaces that this works only when the site stays single-page; growth past 1 page requires re-opening phase 10.

**"The language switcher is too big in the utility nav."** Visual question that belongs in phase 17 / 18. Phase 10 only confirms the switcher exists in the utility nav.

**Hidden dependency on phase 11.** Some IA decisions depend on the stack — Framer's canvas-bound nav patterns vs Next.js's app-router nav vs WordPress's wp_nav_menu integration. Phase 10 produces a stack-agnostic spec; the per-stack realization happens at phase 18. The agent surfaces this when the user asks "but how will this look in WordPress / Framer / Next.js" — the answer is "the spec is the same; the component code differs, and we'll write that at phase 18."

## Reference materials

- **`Workstreams/website-builder/foundation/DESIGN-ecosystem-catalog.md`** — the catalog references nav patterns from the inspiration corpus (Vercel Templates / Cruip / Awwwards / Astro Themes) at phase 11+ once stack is chosen. Phase 10 reads the structural-pattern subset.
- **`Workstreams/website-builder/foundation/DESIGN-i18n.md`** — confirms that a multilingual site requires a language switcher in the utility nav and that the IA spec must accommodate it even though the languages decision lives in phase 11/12.
- **`Workstreams/website-builder/foundation/DESIGN-project-scaffold.md`** § `sitemap.yaml` — the schema this phase writes into.
- **`.website-builder/library/component-patterns/navigation.md`** (populated as the agent learns) — canonical nav component archetypes referenced again at phase 18.
- **`.website-builder/library/seo-checklists/ia.md`** — SEO-driven IA constraints (URL depth, sitemap.xml conventions, breadcrumb schema.org markup).
- **Hick's Law** — applied as the soft 5-7 ceiling for primary-nav count. The agent cites it when surfacing the trade-off; the user can override but should know the underlying reason.
- **WCAG 2.2 §2.4 Navigable** — the "skip to content" link, breadcrumb consistency, and consistent navigation across pages are all referenced; phase 21 (a11y audit) verifies.

## Skip authorization

Phase 10 is not generally skippable. Every site has navigation; without an IA decision, phase 18 (component build) has nothing to compile from. The two narrow exceptions:

1. **Single-page sites with anchor-jump nav only.** Treat as a degenerate IA case (see Common failure modes); phase 10 still produces `navigation.primary[]` with `href: "/#section-id"` entries. Not a skip; a thin pass.
2. **Mid-project IA re-open from phase 11 transactional flag change (decision 34).** If phase 11's transactional decision pivots mid-project, the agent may re-run a subset of phase 10 to add commerce-specific nav items (cart, account, checkout-status) without redoing the full pass. Logged in `.website-builder/decisions/inst-replay-phase-10-after-transactional-pivot.md`.

Skipping phase 10 entirely is not authorized. If the user requests it, the agent refuses and surfaces that without an IA spec, the navigation component at phase 18 has no contract and the deployed site will have inconsistent or missing wayfinding.
