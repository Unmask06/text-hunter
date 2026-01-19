import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), tailwindcss()],

  // Production: served at /products/text-hunter/ subpath on xergiz.com
  base: "/products/text-hunter/",

  build: {
    outDir: "dist/products/text-hunter",
  },

  // Development: proxy API requests to the local backend server
  server: {
    proxy: {
      '/texthunter': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})