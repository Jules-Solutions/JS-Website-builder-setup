---
slug: about
title: About
language: en
layout:
  - type: hero
    headline: About this fixture
    sub: Phase-4 Captain J authored this to exercise the Decap CMS adapter contract.
    cta_label: Back to home
    cta_href: /
    variant: text-center
  - type: rich_text
    body: |
      ## What this fixture exercises

      - **L1 design tokens** in `brand.yaml`
      - **L2 sitemap + sections** in `sitemap.yaml` + `components.yaml`
      - **L3 strings** in `content/strings/{en,de}.json`
      - **L4 page prose** in this file + `home.md` + per-locale variants
      - **L5 briefs** out of band (Decap doesn't see them)

      The Decap `admin/config.yml` (at `public/admin/config.yml` per Astro convention) shapes the collections so the editor sees a Pages tab, a Strings tab (per locale), and the layout list+types Blocks approximation.
---
