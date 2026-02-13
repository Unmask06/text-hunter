import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'TextHunter',
  description: 'Hunt and extract text patterns from PDF documents',
  outDir: '../../../dist/products/text-hunter/docs',
  
  themeConfig: {
    nav: [
      { text: 'Overview', link: '/overview' },
      { text: 'How to Use', link: '/how-to-use' },
      { text: 'Use Cases', link: '/use-cases' },
      { text: 'Launch App', link: 'http://localhost:5173', target: '_blank', rel: 'noopener' }
    ],

    sidebar: [
      {
        text: 'Getting Started',
        items: [
          { text: 'Overview', link: '/overview' },
          { text: 'How to Use', link: '/how-to-use' }
        ]
      },
      {
        text: 'Applications',
        items: [
          { text: 'Use Cases', link: '/use-cases' }
        ]
      }
    ],

    socialLinks: [],

    footer: {
      message: 'Built for high-performance PDF data extraction',
      copyright: 'Copyright © 2026 TextHunter'
    }
  }
})
