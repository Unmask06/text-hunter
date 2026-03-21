import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import checker from 'vite-plugin-checker'

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Plugin to serve pre-built VitePress docs from dist folder during dev
function serveStaticDocs() {
  return {
    name: "serve-static-docs",
    configureServer(server: any) {
      server.middlewares.use((req: any, res: any, next: any) => {
        const url = req.url || "";
        // Handle both the full path and the short path /docs
        if (url.startsWith("/products/text-hunter/docs") || url.startsWith("/docs")) {
          const docsPath = path.resolve(
            __dirname,
            "dist/products/text-hunter/docs",
          );
          
          let urlPath = url;
          if (urlPath.startsWith("/products/text-hunter/docs")) {
            urlPath = urlPath.replace("/products/text-hunter/docs", "");
          } else if (urlPath.startsWith("/docs")) {
            urlPath = urlPath.replace("/docs", "");
          }

          // Remove query params
          urlPath = urlPath.split('?')[0] || "/index.html";

          // Handle trailing slash or empty path
          if (urlPath === "/" || urlPath === "") {
            urlPath = "/index.html";
          }

          let filePath = path.join(docsPath, urlPath);

          // Try adding .html if file not found and no extension present
          if (!fs.existsSync(filePath) && !path.extname(urlPath)) {
            if (fs.existsSync(filePath + ".html")) {
              filePath += ".html";
            } else if (fs.existsSync(path.join(filePath, "index.html"))) {
              filePath = path.join(filePath, "index.html");
            }
          }

          if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
            const ext = path.extname(filePath);
            const contentTypes: Record<string, string> = {
              ".html": "text/html",
              ".css": "text/css",
              ".js": "application/javascript",
              ".json": "application/json",
              ".svg": "image/svg+xml",
              ".png": "image/png",
              ".jpg": "image/jpeg",
              ".woff": "font/woff",
              ".woff2": "font/woff2",
            };
            res.setHeader("Content-Type", contentTypes[ext] || "text/html");
            fs.createReadStream(filePath).pipe(res);
            return;
          }
        }
        next();
      });
    },
  };
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [serveStaticDocs(), vue(), tailwindcss(), checker({
    typescript: true,
    vueTsc: true
  })],

  // Base path for production: /products/text-hunter/
  // For desktop (Tauri) and dev, use "/" (overridden by environment)
  base: process.env.VITE_BASE_PATH || "/",

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