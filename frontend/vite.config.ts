import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vitest/config'
import checker from 'vite-plugin-checker'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    // Don't run type-checking during vitest runs — tests have their own tsconfig
    // needs (vitest globals, relaxed noUncheckedIndexedAccess) and the checker
    // would report false positives on test files.
    ...(process.env.NODE_ENV !== 'test'
      ? [checker({ typescript: true, vueTsc: true })]
      : []),
  ],

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
  },

  test: {
    environment: 'jsdom',
    globals: true,
    include: ['src/**/__tests__/**/*.test.ts'],
    alias: {
      // @tauri-apps/plugin-http is injected at runtime by Tauri and is not an
      // npm package. Redirect to a stub so vitest can resolve it.
      '@tauri-apps/plugin-http': fileURLToPath(
        new URL('./src/__mocks__/@tauri-apps/plugin-http.ts', import.meta.url)
      ),
    },
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
    },
  },
})