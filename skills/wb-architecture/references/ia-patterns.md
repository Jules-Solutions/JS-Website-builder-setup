# Reference — Information architecture patterns (phase 10)

> Navigation archetypes per zone, the Hick's-Law ceiling rationale, mobile-pattern selection, breadcrumb/SEO rules, the single-page degenerate case, and the annotated `navigation:` block schema. Authoritative source is `phase-contracts/10-information-architecture.md` + `${CLAUDE_PLUGIN_ROOT}/reference-corpus/ECOSYSTEM-CATALOG.md` (IA pattern subset) + `foundation/DESIGN-i18n.md` + `foundation/DESIGN-project-scaffold.md` § sitemap.yaml. This file is the fast-load summary.

## The core IA failure and the agent's job

Information architecture is where most muggle sites quietly fail. A user with 14 pages tries to put all 14 in the primary nav; the result reads as an inventory list, not a site. The agent's job: surface hierarchy — which pages are headlines, which are sub-navigation, which are footer-only, which are reachable only via in-page links. Done right, phase 10 produces a `navigation:` block downstream phases consume without further architectural argument.

Phase 10 is also the last chance to challenge the phase-9 sitemap. If nav work reveals two pages that are really one page with sections, or a planned page with no path users could reach it through, surface the inconsistency and briefly re-open phase 9 to resolve — do not paper over.

## The 8 decisions (each surfaces as one or more AskUserQuestion)

1. **Primary nav contents** — which pages get always-visible top-level slots. Soft ceiling 5-7 (see Hick's Law below).
2. **Primary nav order** — left-to-right. Convention: left-anchor brand/logo, right-anchor primary CTA. Middle slots by user-journey priority (most-likely-next-step first).
3. **Dropdown vs flat per primary item** — items pointing at sub-pages either expand on hover/click (dropdown / mega-menu) or sit flat with children reachable only via the parent page. Decide per item.
4. **Footer nav contents** — reachable-from-anywhere but no primary slot: legal, imprint, careers, press, sitemap, social links, secondary CTAs. Can be longer (10-20 items grouped into columns).
5. **Utility nav contents** — persistent non-page-to-page affordances: language switcher (mandatory when multilingual), search, account/login/cart, skip-to-content.
6. **Breadcrumb rules** — required for any site deeper than 2 levels. Specify which page-types render them and how hierarchy is computed (from `sitemap.yaml`'s `parent:` field).
7. **Active-state behavior** — how the current page is indicated: underline / color shift / weight change / pill. Brand-voice-consistent.
8. **Mobile pattern** — hamburger / bottom-tab / inline-scroll / mega-menu collapse. Picked from primary-nav count + site shape (table below).

## Hick's Law — the 5-7 primary-nav ceiling

Hick's Law + mobile-screen-width + muggle scanning capacity all point at 5-7 as the working primary-nav ceiling. Over 7, the agent **refuses once and surfaces the cost** — *"every additional item halves the visibility of every other"* — and forces a grouping decision (dropdowns, mega-menu, or move to footer). The agent does not refuse forever; it refuses once and surfaces the cost; the user can override with explicit confirmation. The standard reframe for "I want every page in the primary nav": *"That ships, but it does this: users scan 14 items, find none of them obvious, and bounce. Five strong items beat fourteen weak ones every time. Which pages are first-contact pages, and which are reachable from somewhere else?"* Then walk pages by user-journey priority and group the long tail.

## Mobile-pattern selection

| Pattern | Use when | Fails when |
|---|---|---|
| **hamburger** | Most sites; works for most primary-nav counts | Rarely a wrong choice; the safe default |
| **bottom-tab** | App-shaped sites with a few destinations (3-5) | 7-item primary nav on small phones — agent refuses this combination |
| **inline-scroll** | Very simple sites; single-page anchor-jump nav | Multi-level hierarchy (no room for sub-nav) |
| **mega-menu collapse** | Complex multi-column nav patterns | Tiny sites (over-engineered) |

The agent refuses a mobile-pattern / primary-nav-count mismatch and offers compatible alternatives.

## Breadcrumbs — UX + SEO

Required for any site with any page nested two or more levels deep (home → category → item, or home → service-group → service → sub-service). Two costs when omitted: UX wayfinding (users get lost) + SEO (breadcrumbs are schema.org structured-data anchors search engines consume). The agent refuses to skip on a deep site; offers a compromise — breadcrumbs scoped to only the deepest page-types (blog-post, service-detail) styled small. User can still override; agent logs to `.website-builder/decisions/skip-breadcrumbs.md`. Standard reframe for "skip breadcrumbs, my designer doesn't like them": *"Breadcrumbs are not decoration; they are wayfinding for deep pages and structured-data anchors for search engines"* + the scoped-and-small compromise.

## Reachability gate

Every page in `sitemap.yaml.pages` must be reachable from somewhere — primary nav, footer nav, internal link from another page, or sitemap.xml indexed by search engines. If a page exists in the sitemap but the agent cannot map a user journey to it, surface the inconsistency and either re-open phase 9 (drop the page) or find it a parent link. Not overridable by hand-wave — the page either gets a path or gets dropped.

## Language switcher (multilingual sites)

If phase 11 or earlier flagged the site as multilingual, the utility nav must include a language switcher. Phase 10 surfaces and accommodates this even though the actual languages decision belongs to phase 11/12 — the IA must reserve the slot. The decision-39 i18n strategy (Pattern A shared structure / Pattern B per-locale layouts) locks at phase 12; phase 10 only confirms the switcher exists in `utility:`.

## Single-page degenerate case

Some single-page sites map all sitemap entries to in-page anchor links (`/#about`, `/#services`, `/#contact`). Handle as a degenerate IA case — primary nav becomes an in-page anchor jump menu; mobile pattern becomes inline-scroll. **Not a skip; a thin pass** — phase 10 still produces `navigation.primary[]` with `href: "/#section-id"` entries. Surface that this works only while the site stays single-page; growth past one page requires re-opening phase 10.

## Deferred-to-later questions (do not resolve at phase 10)

- **Sticky vs static nav** → phase 17 (design system) or 18 (component build). Phase 10 locks structure, not visual behavior.
- **"Language switcher is too big"** → phase 17/18. Phase 10 only confirms it exists.
- **"How will this look in WordPress/Framer/Next.js?"** → the spec is the same; per-stack component realization happens at phase 18. Phase 10 produces a stack-agnostic spec.
- **Hero CTA vs nav CTA wording** → surface the two roles (nav CTA = always-visible commitment path, intent "I'm ready"; hero CTA = contextual, intent "tell me more first"). Different wording per role — nav CTA often stays generic ("Contact"/"Sign up"), hero CTA gets brand-voice prose ("Let's talk"/"Start the trial"). This is an IA-adjacent ruling phase 10 does make.

## The `navigation:` block schema (written to `.website-builder/sitemap.yaml`)

`{strings.nav.*}` references resolve from `content/strings/{lang}.json` at phase 16 — phase 10 declares the references, phase 16 supplies values. Keeps the IA stack- and language-agnostic.

```yaml
# .website-builder/sitemap.yaml
pages: [...]                                 # from phase 9, unchanged

navigation:
  primary:
    items:
      - { label: "Home",     href: "/",         active_match: exact }
      - { label: "Services", href: "/services", active_match: prefix, dropdown:
          [ { label: "Strategy", href: "/services/strategy" },
            { label: "Build",    href: "/services/build" },
            { label: "Maintain", href: "/services/maintain" } ] }
      - { label: "Essays",   href: "/essays",   active_match: prefix }
      - { label: "About",    href: "/about",    active_match: prefix }
      - { label: "Contact",  href: "/contact",  active_match: exact, variant: cta }
    style:
      active_state: "underline + weight-600"
      cta_variant: "primary-button"
  footer:
    columns:
      - heading: "Site"
        items: [ { label: "Home", href: "/" }, { label: "Services", href: "/services" }, { label: "About", href: "/about" } ]
      - heading: "Legal"
        items: [ { label: "Privacy", href: "/privacy" }, { label: "Terms", href: "/terms" }, { label: "Imprint", href: "/imprint" } ]  # imprint mandatory in DACH
      - heading: "Connect"
        items: [ { label: "Email", href: "mailto:hi@example.com" }, { label: "LinkedIn", href: "https://linkedin.com/in/..." } ]
  utility:
    items:
      - { kind: "skip-to-content", label: "{strings.nav.skip_to_content}" }
      - { kind: "language-switcher" }              # populated when multilingual per phase 11
      - { kind: "search", optional: true }         # configured at phase 24 if integrated
  breadcrumbs:
    enabled_for: [service-detail, blog-post, legal]
    home_label: "{strings.nav.home}"
    separator: "›"
  mobile:
    pattern: hamburger                             # hamburger | bottom-tab | inline | mega-menu
    breakpoint: 768
    drawer_position: right
    overlay_dim: true
```

## Reference materials cited by the contract

- `${CLAUDE_PLUGIN_ROOT}/reference-corpus/ECOSYSTEM-CATALOG.md` — accepted IA patterns; nav-pattern subset from the inspiration corpus (Vercel Templates / Cruip / Awwwards / Astro Themes) referenced again at phase 11+ once stack is chosen.
- `DESIGN-i18n.md` — confirms multilingual sites require a utility-nav language switcher.
- `DESIGN-project-scaffold.md` § sitemap.yaml — the schema this phase writes into.
- `.website-builder/library/component-patterns/navigation.md` (populated as the agent learns) — canonical nav component archetypes, referenced again at phase 18.
- `.website-builder/library/seo-checklists/ia.md` — SEO-driven IA constraints (URL depth, sitemap.xml conventions, breadcrumb schema.org markup).
- Hick's Law — the soft 5-7 primary-nav ceiling rationale. WCAG 2.2 §2.4 Navigable — skip-to-content link, breadcrumb consistency, consistent navigation across pages; phase 21 (a11y audit) verifies.

## Skip authorization

Phase 10 is not generally skippable — every site has navigation; without an IA decision, phase 18 has nothing to compile from. Two narrow exceptions: (1) single-page anchor-jump sites (degenerate thin pass, above); (2) mid-project IA re-open from a phase-11 transactional-flag change (decision 34) — re-run a subset to add commerce nav items (cart, account, checkout-status), logged in `.website-builder/decisions/inst-replay-phase-10-after-transactional-pivot.md`. Skipping entirely is not authorized; if requested, refuse and surface that the phase-18 nav component would have no contract and the deployed site would have inconsistent/missing wayfinding.
