---
type: page
slug: /
language: en
title: "Home"
seo_title: "Payload fixture — Home"
seo_description: "Synthetic fixture for Payload CMS adapter validation."
sections: [hero, features-grid, cta]
---

## Hero section

[Synthetic content. Payload Block: hero. Headline + sub + CTA.]

Welcome to the Payload fixture site. This is filler content seeded via `payload.create({collection: 'pages', locale: 'en'})` at phase 18 per the seed pattern in cms-payload.md.

## Features Grid section

[Payload Block: featuresGrid. 3 items.]

(Items defined in components.yaml. Each item title + description localized.)

## CTA section

[Payload Block: cta. References {strings.cta.subscribe} from messages/en.json — Option A strings layer.]

(Section uses strings reference; agent resolves at render time via next-intl.)
