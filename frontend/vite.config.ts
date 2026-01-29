import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import checker from 'vite-plugin-checker'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), tailwindcss(), checker({
    typescript: true, // 1. Enable TypeScript checking
    vueTsc: true      // 2. Enable Vue-specific checking
  })],

  // Production: served at /products/text-hunter/ subpath on xergiz.com
  base: "/products/text-hunter/",

  build: {
    outDir: "dist/products/text-hunter",
  },

  // Development: proxy API requests to the local backend server
  server: {
    proxy: {
      '/text-hunter': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})