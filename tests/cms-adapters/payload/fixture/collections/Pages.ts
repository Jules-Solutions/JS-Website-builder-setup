// tests/cms-adapters/payload/fixture/collections/Pages.ts
//
// The load-bearing collection for the marketing-site pattern. Composes per-page layouts from a Blocks field.
// Demonstrates the cms-payload.md § "Pattern: Pages collection with Blocks field for composable layouts" canonical pattern.
//
// i18n approach: APPROACH 2 (Decision 39 Pattern A default) — `localized: true` on text fields INSIDE each block,
// NOT on the `layout` blocks field itself. This keeps the layout structure shared across locales; only text varies per locale.

import type { CollectionConfig } from 'payload'
import { Hero } from '../blocks/Hero'
import { RichText } from '../blocks/RichText'
import { FeaturesGrid } from '../blocks/FeaturesGrid'
import { CallToAction } from '../blocks/CallToAction'

export const Pages: CollectionConfig = {
  slug: 'pages',
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'slug', '_status', 'updatedAt'],
    livePreview: {
      url: ({ data, locale }) =>
        `${process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'}/${locale?.code || 'en'}${data.slug || ''}?draft=true`,
      breakpoints: [
        { label: 'Mobile', name: 'mobile', width: 375, height: 667 },
        { label: 'Tablet', name: 'tablet', width: 768, height: 1024 },
        { label: 'Desktop', name: 'desktop', width: 1440, height: 900 },
      ],
    },
  },
  versions: {
    drafts: {
      autosave: { interval: 2000 },
      schedulePublish: true,
      validate: true,
    },
    maxPerDoc: 50,
  },
  access: {
    // Public read for published only; authenticated users see drafts too.
    read: ({ req: { user } }) => {
      if (user) return true
      return { _status: { equals: 'published' } }
    },
    create: ({ req: { user } }) =>
      user?.roles?.some((r: string) => ['admin', 'editor'].includes(r)) || false,
    update: ({ req: { user } }) =>
      user?.roles?.some((r: string) => ['admin', 'editor'].includes(r)) || false,
    delete: ({ req: { user } }) => user?.roles?.includes('admin') || false,
  },
  fields: [
    { name: 'title', type: 'text', required: true, localized: true },
    {
      name: 'slug',
      type: 'text',
      required: true,
      unique: true,
      index: true,
      admin: { position: 'sidebar' },
    },
    {
      name: 'meta',
      type: 'group',
      fields: [
        { name: 'title', type: 'text', localized: true },
        { name: 'description', type: 'textarea', localized: true },
        { name: 'image', type: 'upload', relationTo: 'media' },
      ],
    },
    {
      name: 'layout',
      type: 'blocks',
      // INTENTIONALLY NOT `localized: true` HERE — Approach 2 (Decision 39 Pattern A default).
      // Localization happens at the text-field level INSIDE each Block (see blocks/Hero.ts, blocks/RichText.ts, etc.).
      blocks: [Hero, RichText, FeaturesGrid, CallToAction],
      minRows: 1,
    },
  ],
  hooks: {
    beforeChange: [
      ({ data }) => {
        if (!data.slug && data.title) {
          data.slug = '/' + data.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
        }
        return data
      },
    ],
    afterChange: [
      async ({ doc, operation }) => {
        // ISR revalidation on change — fires against the user's Next.js frontend.
        if (operation === 'update' || operation === 'create') {
          try {
            await fetch(
              `${process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'}/api/revalidate`,
              {
                method: 'POST',
                body: JSON.stringify({
                  path: doc.slug,
                  secret: process.env.REVALIDATE_SECRET,
                }),
              }
            )
          } catch {
            // best-effort; do not fail the save on revalidation errors
          }
        }
      },
    ],
  },
}
