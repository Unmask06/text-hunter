import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig, type Plugin } from 'vite'
import checker from 'vite-plugin-checker'

// Custom Vite plugin to serve static docs from dist folder
// especially useful during development when using a subpath base
function serveStaticDocs(): Plugin {
  return {
    name: 'serve-static-docs',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const url = req.url;
        if (!url || !url.startsWith('/docs')) {
          next();
          return;
        }
        
        const isWeb = process.env.VITE_BUILD_TARGET === 'web';
        const basePath = isWeb ? '/products/text-hunter/docs/' : '/docs/';
        
        if (url.startsWith(basePath) || url === '/docs' || url === '/docs/') {
          let reqPath = url.replace(basePath, '');
          if (url === '/docs' || url === '/docs/') reqPath = '';
          
          // Remove query string from path
          const cleanPath = reqPath.includes('?') ? reqPath.split('?')[0] ?? '' : reqPath;
          
          // Determine dist directory based on target
          const docsDistDir = isWeb 
            ? path.join(process.cwd(), 'dist', 'products', 'text-hunter', 'docs')
            : path.join(process.cwd(), 'dist', 'docs');
            
          let filePath = path.join(docsDistDir, cleanPath);
          
          // Serve index.html for directory root
          if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
            filePath = path.join(filePath, 'index.html');
          }
          
          if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
            const ext = path.extname(filePath);
            const mimeTypes: Record<string, string> = {
              '.html': 'text/html',
              '.js': 'text/javascript',
              '.css': 'text/css',
              '.png': 'image/png',
              '.jpg': 'image/jpeg',
              '.svg': 'image/svg+xml',
              '.json': 'application/json'
            };
            res.setHeader('Content-Type', mimeTypes[ext] || 'application/octet-stream');
            res.end(fs.readFileSync(filePath));
            return;
          }
        }
        next();
      });
    }
  };
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(), 
    tailwindcss(), 
    checker({
      typescript: true,
      vueTsc: true
    }),
    serveStaticDocs()
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
  }
})
