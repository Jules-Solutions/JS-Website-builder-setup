// tests/cms-adapters/payload/fixture/blocks/FeaturesGrid.ts
//
// Repeatable feature-items grid. Demonstrates `array` field with localized item titles + descriptions inside.

import type { Block } from 'payload'

export const FeaturesGrid: Block = {
  slug: 'featuresGrid',
  labels: { singular: 'Features Grid', plural: 'Features Grid blocks' },
  fields: [
    { name: 'heading', type: 'text', localized: true },
    {
      name: 'items',
      type: 'array',
      maxRows: 6,
      fields: [
        { name: 'title', type: 'text', required: true, localized: true },
        { name: 'description', type: 'textarea', localized: true },
        {
          name: 'icon',
          type: 'select',
          options: ['check', 'star', 'zap', 'shield'],
          defaultValue: 'check',
        },
      ],
    },
    {
      name: 'variant',
      type: 'select',
      options: ['2-col', '3-col', '4-col'],
      defaultValue: '3-col',
    },
  ],
}
