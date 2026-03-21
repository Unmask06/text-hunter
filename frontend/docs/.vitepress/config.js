import { defineConfig } from "vitepress";

// Determine build target from environment
const isDesktop = process.env.VITE_BUILD_TARGET === 'desktop';
const isWeb = process.env.VITE_BUILD_TARGET === 'web';

// Default to desktop (Tauri) build
const base = isWeb ? "/products/text-hunter/docs/" : "/docs/";
const outDir = isWeb ? "../dist/products/text-hunter/docs" : "../dist/docs";
const canonical = isWeb ? "/products/text-hunter/docs/" : "/docs/";

// For dev mode, use command-line API to set base path
// vitepress dev docs --base /products/text-hunter/docs/
export default defineConfig({
  title: "TextHunter",
  description: "Hunt and extract text patterns from PDF documents",
  base,
  outDir,
  head: [["link", { rel: "canonical", href: canonical }]],

  themeConfig: {
    nav: [
      { text: "Home", link: "/" },
      { text: "Overview", link: "/overview" },
      { text: "How to Use", link: "/how-to-use" },
      { text: "Use Cases", link: "/use-cases" },
      { text: "Launch App", link: "../", target: "_blank", rel: "noopener" },
    ],

    sidebar: [
      {
        text: "Getting Started",
        items: [
          { text: "Overview", link: "/overview" },
          { text: "How to Use", link: "/how-to-use" },
          { text: "Use Cases", link: "/use-cases" },
        ],
      },
    ],

    socialLinks: [],

    footer: {
      message: "Built for high-performance PDF data extraction",
      copyright: "Copyright © 2026 TextHunter Team",
    },
  },
});
