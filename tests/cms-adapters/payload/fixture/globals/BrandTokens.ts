// tests/cms-adapters/payload/fixture/globals/BrandTokens.ts
//
// Maps website-builder Layer 1 (brand.yaml.tokens) into a Payload Global. Phase 17 seeds initial values from brand.yaml; ongoing edits via admin.
// Frontend reads at build time (or via Server Component fetch) and emits CSS custom properties.
// Demonstrates afterChange ISR revalidation pattern from cms-payload.md.

import type { GlobalConfig } from 'payload'

export const BrandTokens: GlobalConfig = {
  slug: 'brand-tokens',
  access: {
    read: () => true,
    update: ({ req: { user } }) => user?.roles?.includes('admin') || false,
  },
  fields: [
    {
      name: 'colors',
      type: 'group',
      fields: [
        { name: 'primary', type: 'text', defaultValue: 'oklch(64% 0.18 30)' },
        { name: 'secondary', type: 'text', defaultValue: 'oklch(72% 0.12 180)' },
        { name: 'neutral_50', type: 'text', defaultValue: 'oklch(98% 0.01 80)' },
        { name: 'neutral_900', type: 'text', defaultValue: 'oklch(15% 0 0)' },
        { name: 'semantic_error', type: 'text', defaultValue: 'oklch(60% 0.20 25)' },
        { name: 'semantic_success', type: 'text', defaultValue: 'oklch(60% 0.15 145)' },
      ],
    },
    {
      name: 'typography',
      type: 'group',
      fields: [
        { name: 'displayFamily', type: 'text', defaultValue: 'Fraunces, serif' },
        { name: 'bodyFamily', type: 'text', defaultValue: 'Inter, sans-serif' },
        { name: 'monoFamily', type: 'text', defaultValue: 'JetBrains Mono, monospace' },
      ],
    },
    {
      name: 'darkMode',
      type: 'select',
      options: ['auto', 'light', 'dark'],
      defaultValue: 'auto',
    },
  ],
  hooks: {
    afterChange: [
      async () => {
        // Trigger ISR revalidation across all pages — brand changes affect every route.
        try {
          await fetch(
            `${process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'}/api/revalidate`,
            {
              method: 'POST',
              body: JSON.stringify({
                tag: 'brand-tokens',
                secret: process.env.REVALIDATE_SECRET,
              }),
            }
          )
        } catch {
          // best-effort
        }
      },
    ],
  },
}
