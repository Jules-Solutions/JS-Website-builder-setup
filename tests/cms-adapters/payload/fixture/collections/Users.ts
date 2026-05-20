// tests/cms-adapters/payload/fixture/collections/Users.ts
//
// Required by Payload — admin auth lives here. Standard pattern: text + auth + roles.

import type { CollectionConfig } from 'payload'

export const Users: CollectionConfig = {
  slug: 'users',
  auth: true,            // Payload generates email + password + hashed-password fields + reset/verify flows
  admin: {
    useAsTitle: 'email',
    defaultColumns: ['email', 'name', 'roles'],
  },
  access: {
    read: ({ req: { user } }) => user?.roles?.includes('admin') || false,
    create: ({ req: { user } }) => user?.roles?.includes('admin') || false,
    update: ({ req: { user }, id }) => {
      if (user?.roles?.includes('admin')) return true
      // users can edit themselves
      return user?.id === id
    },
    delete: ({ req: { user } }) => user?.roles?.includes('admin') || false,
  },
  fields: [
    { name: 'name', type: 'text' },
    {
      name: 'roles',
      type: 'select',
      hasMany: true,
      required: true,
      defaultValue: ['editor'],
      options: ['admin', 'editor', 'author'],
    },
  ],
}
