// tests/cms-adapters/payload/fixture/blocks/CallToAction.ts
//
// Standard CTA block — headline + sub + button. All text fields localized; href + variant shared across locales.

import type { Block } from 'payload'

export const CallToAction: Block = {
  slug: 'cta',
  labels: { singular: 'Call to Action', plural: 'CTA blocks' },
  fields: [
    { name: 'headline', type: 'text', required: true, localized: true },
    { name: 'sub', type: 'textarea', localized: true },
    {
      name: 'cta',
      type: 'group',
      fields: [
        { name: 'label', type: 'text', required: true, localized: true },
        { name: 'href', type: 'text', required: true },
      ],
    },
    {
      name: 'variant',
      type: 'select',
      options: ['primary', 'secondary', 'ghost'],
      defaultValue: 'primary',
    },
  ],
}
