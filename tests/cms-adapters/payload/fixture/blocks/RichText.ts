// tests/cms-adapters/payload/fixture/blocks/RichText.ts
//
// Lexical-powered rich text block. Stores structured JSON (NOT HTML). Frontend renders via @payloadcms/richtext-lexical/react <RichText /> component.
// content field is `localized: true` per Approach 2.

import type { Block } from 'payload'
import { lexicalEditor } from '@payloadcms/richtext-lexical'

export const RichText: Block = {
  slug: 'richText',
  labels: { singular: 'Rich Text', plural: 'Rich Text blocks' },
  fields: [
    {
      name: 'content',
      type: 'richText',
      localized: true,
      editor: lexicalEditor({
        features: ({ defaultFeatures }) => [
          ...defaultFeatures,
          // BlocksFeature could embed Banner / CTA / Quote here for editorial-richness use cases per cms-payload.md
        ],
      }),
    },
  ],
}
