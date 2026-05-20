// tests/cms-adapters/payload/fixture/globals/SiteSettings.ts
//
// Site-wide settings global. Demonstrates Global pattern from cms-payload.md § "Pattern: Globals for site-wide settings + brand tokens".

import type { GlobalConfig } from 'payload'

export const SiteSettings: GlobalConfig = {
  slug: 'site-settings',
  access: {
    read: () => true,
    update: ({ req: { user } }) => user?.roles?.includes('admin') || false,
  },
  fields: [
    { name: 'siteName', type: 'text', required: true, localized: true, defaultValue: 'Payload fixture' },
    { name: 'tagline', type: 'text', localized: true },
    { name: 'logo', type: 'upload', relationTo: 'media' },
    { name: 'favicon', type: 'upload', relationTo: 'media' },
    {
      name: 'social',
      type: 'array',
      fields: [
        {
          name: 'platform',
          type: 'select',
          options: ['twitter', 'linkedin', 'instagram', 'github', 'youtube'],
        },
        { name: 'url', type: 'text' },
      ],
    },
  ],
}
