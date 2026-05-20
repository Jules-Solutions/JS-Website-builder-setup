// tests/cms-adapters/payload/fixture/blocks/Hero.ts
//
// Synthesized from components.yaml "Hero" entry. Demonstrates Approach 2 — text fields localized INSIDE the block, NOT the block itself.

import type { Block } from 'payload'

export const Hero: Block = {
  slug: 'hero',
  labels: { singular: 'Hero', plural: 'Hero blocks' },
  fields: [
    { name: 'headline', type: 'text', required: true, localized: true },
    { name: 'sub', type: 'textarea', localized: true },
    {
      name: 'cta',
      type: 'group',
      fields: [
        { name: 'label', type: 'text', localized: true },
        { name: 'href', type: 'text' },
        {
          name: 'variant',
          type: 'select',
          options: ['primary', 'secondary', 'ghost'],
          defaultValue: 'primary',
        },
      ],
    },
    { name: 'background', type: 'upload', relationTo: 'media' },
    {
      name: 'variant',
      type: 'select',
      options: ['text-left', 'text-center', 'image-right'],
      defaultValue: 'text-center',
    },
  ],
}
