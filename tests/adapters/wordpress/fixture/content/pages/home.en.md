---
type: page
slug: /
language: en
title: "Home"
seo_title: "Still Humans — The newsletter for people who refuse to optimize"
seo_description: "We won't fight what works. We make it work better."
purpose: "Introduce project + drive newsletter signup"
primary_cta: "{strings.cta.subscribe}"
sections: [hero, signup-cta]
---

## Hero section

[HeroBlock — invoked from sections.yaml. Renders the headline + sub + CTA.]

Headline: "Still Humans"
Sub: "A weekly letter for people who refuse to optimize."

## Signup CTA section

(Uses {strings.cta.subscribe} + {strings.cta.subscribe_loading} + {strings.cta.subscribe_success} from strings/en.json)

The form posts to Mailchimp (endpoint configured at phase 23).
