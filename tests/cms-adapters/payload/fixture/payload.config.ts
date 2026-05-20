// tests/cms-adapters/payload/fixture/payload.config.ts
//
// Synthetic Payload v3 config at phase-12-complete baseline.
// SCHEMA-ONLY — no Postgres bootstrap, no Node runtime required for Phase 4 manual verification.
// Phase 5+ runner integration (per tests/cms-adapters/README.md "Out-of-scope for Phase 4 itself") will instantiate against a Neon free-tier sandbox.
//
// Demonstrates the Phase 12 sub-decisions from project.yaml:
// - db_decision: vercel-marketplace-neon (Postgres adapter via @payloadcms/db-vercel-postgres)
// - blocks_localization_approach: 2 (fields-inside-blocks localized, NOT the layout itself — Decision 39 Pattern A default)
// - strings_layer_option: A (CDJSON kept in messages/{lang}.json; Payload doesn't store strings)
// - localization with Decision 39/40/41 defaults: locales [en, de], defaultLocale: en, fallback: true

import { buildConfig } from 'payload'
import { vercelPostgresAdapter } from '@payloadcms/db-vercel-postgres'
import { lexicalEditor, BlocksFeature } from '@payloadcms/richtext-lexical'
import path from 'path'
import { fileURLToPath } from 'url'

import { Pages } from './collections/Pages'
import { Users } from './collections/Users'
import { Media } from './collections/Media'
import { BrandTokens } from './globals/BrandTokens'
import { SiteSettings } from './globals/SiteSettings'

const filename = fileURLToPath(import.meta.url)
const dirname = path.dirname(filename)

export default buildConfig({
  admin: {
    user: Users.slug,
    meta: {
      titleSuffix: '— Payload fixture',
    },
  },

  collections: [Pages, Users, Media],
  globals: [BrandTokens, SiteSettings],

  editor: lexicalEditor({
    features: ({ defaultFeatures }) => [
      ...defaultFeatures,
      // BlocksFeature lets the Lexical editor embed full Payload Blocks inline in rich text
      // (per cms-payload.md § "Pattern: Lexical rich text with embedded Blocks (BlocksFeature)")
      // — populated post-Phase-4 when blocks are richer
    ],
  }),

  // Decision 39 Pattern A default + Decision 41 fallback:true
  localization: {
    locales: [
      { label: 'English', code: 'en' },
      { label: 'Deutsch', code: 'de' },
    ],
    defaultLocale: 'en',
    fallback: true,
  },

  // S4 — three-way DB/hosting decision: vercel-marketplace-neon (the canonical muggle default per DESIGN-cms-payload.md line 564)
  // Connection string from env; not invoked in fixture (schema-only).
  db: vercelPostgresAdapter({
    pool: {
      connectionString: process.env.DATABASE_URI || '',
    },
  }),

  secret: process.env.PAYLOAD_SECRET || '',

  typescript: {
    outputFile: path.resolve(dirname, 'payload-types.ts'),
  },

  // CORS open in fixture; production deploys constrain to known origins.
  cors: ['http://localhost:3000'],
  csrf: ['http://localhost:3000'],
})
