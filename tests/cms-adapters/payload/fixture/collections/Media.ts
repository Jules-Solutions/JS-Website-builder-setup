// tests/cms-adapters/payload/fixture/collections/Media.ts
//
// Standard upload collection — referenced by `relationTo: 'media'` in BrandTokens / Pages / Blocks.
// In production: paired with @payloadcms/storage-s3 / -vercel-blob / -cloudinary plugin.
// In fixture: default local-filesystem storage (ephemeral on Vercel; sufficient for schema-only fixture).

import type { CollectionConfig } from 'payload'

export const Media: CollectionConfig = {
  slug: 'media',
  upload: {
    staticDir: 'media',
    mimeTypes: ['image/*', 'application/pdf', 'video/mp4'],
    imageSizes: [
      { name: 'thumbnail', width: 300, height: 200, position: 'centre' },
      { name: 'card', width: 768, height: 512, position: 'centre' },
      { name: 'hero', width: 1920, height: 1080, position: 'centre' },
    ],
  },
  admin: {
    useAsTitle: 'alt',
  },
  access: {
    read: () => true,            // media is public — anyone can view
    create: ({ req: { user } }) =>
      user?.roles?.some((r: string) => ['admin', 'editor'].includes(r)) || false,
    update: ({ req: { user } }) =>
      user?.roles?.some((r: string) => ['admin', 'editor'].includes(r)) || false,
    delete: ({ req: { user } }) => user?.roles?.includes('admin') || false,
  },
  fields: [
    { name: 'alt', type: 'text', required: true, localized: true },
    { name: 'caption', type: 'text', localized: true },
  ],
}
