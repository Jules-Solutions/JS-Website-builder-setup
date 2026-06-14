---
name: wb-maintain-content-add
description: This skill should be used by the website-maintainer when the user wants to add a NEW piece of content to a live site within an existing content type — "add an essay", "write a new blog post", "add a case study", "publish a new article", "add a portfolio item", "new entry for the journal". For content that fits an archive/collection the site already supports. If the content type does NOT yet exist (the first essay on a site with no blog), this skill escalates to a light sitemap+wireframe addition. NOT for adding a section to a page (wb-maintain-section-add) or a whole new page type (wb-maintain-page-add).
version: 0.1.0
---

# wb-maintain-content-add — add new content

> Add a new essay / blog post / case study / portfolio item to an existing collection. The maintainer's eager path — this is exactly the ongoing work the template exists for. Single-pass; no re-run of discovery. Typically under an hour.

## When invoked

The user wants to publish a new piece of content. First question: **does the site already support this content type?**

## Behavior

1. **Check the content type is supported.** Read `.website-builder/sitemap.yaml`. Does an archive/collection exist for this content (e.g. `/essays/`, `/blog/`, `/work/`)?
   - **Supported** → proceed (the common, fast case).
   - **Not supported** (e.g. the first essay on a site that has never had a blog) → this is bigger than a content-add. You need a light Phase 9 (sitemap) update + Phase 14 (wireframe) for the archive/index page. Surface it: *"You don't have an essays archive yet — adding the first one means setting up the `/essays/` index + the per-essay layout. That's a small structural addition, not just dropping in content. Want me to walk you through it?"* If the archive page is genuinely new page-shaped work, route to `wb-maintain-page-add`; if it just needs the index + the entry template, do the light update here with the user's confirmation.
2. **Walk the user through writing the piece.** Keep it light — single-pass, in the phase-5 brand voice. The substance is the user's; you shape it to voice. Don't invent the content.
3. **Apply to project state.** Write `.website-builder/content/pages/{slug}.md` (or the collection's content file per the CMS). Update the collection index. For multi-language sites, follow `config.yaml.translation_preference` (translate inline / emit brief / ask).
4. **Optional hero image.** Offer to generate a brand-consistent hero via the image-gen consumer (when present), prompted with the site's palette + voice + style.
5. **Verify + deploy.** Confirm the new entry renders, the archive lists it, links resolve. Deploy on user confirmation via `deploy_provider`.

## Time-box

**Under 1 hour** for a typical essay/post into an existing collection. The "first of a new type" case is larger — flag it, don't silently absorb it.

## Runbook

Content process: `runbooks/content-update.md` (the add path is the same shape as the edit path, plus collection-index + nav).

## Anti-patterns

- Inventing the content instead of shaping the user's substance.
- Silently creating a new content type when the site has none (that's a structural addition — surface it).
- Forgetting the collection index / nav update (a published essay nobody can navigate to).
