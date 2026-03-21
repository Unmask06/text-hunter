import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import checker from 'vite-plugin-checker'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), tailwindcss(), checker({
    typescript: true,
    vueTsc: true
  })],

  // Base path configuration:
  // - Web mode: /products/text-hunter/ (for deployed web app)
  // - Desktop (Tauri) and dev: "/" (Tauri serves root, docs at /docs/)
  base: process.env.VITE_BUILD_TARGET === 'web' ? '/products/text-hunter/' : '/',

  build: {
    outDir: "dist",
  },

  // Development: proxy API requests to the local backend server
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // Consistent with desktop app port
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    },
    fs: {
      allow: [".", "../docs"],
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})