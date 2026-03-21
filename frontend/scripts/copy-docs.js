/**
 * Copies VitePress docs from dist/products/text-hunter/docs/ to dist/docs/
 * This makes docs accessible at /docs/ in the Tauri desktop app.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const distDir = path.resolve(rootDir, 'dist');
const srcDocsDir = path.resolve(distDir, 'products', 'text-hunter', 'docs');
const destDocsDir = path.resolve(distDir, 'docs');

console.log('Copying docs...');
console.log(`  From: ${srcDocsDir}`);
console.log(`  To:   ${destDocsDir}`);

// Remove existing docs folder if it exists
if (fs.existsSync(destDocsDir)) {
  fs.rmSync(destDocsDir, { recursive: true, force: true });
  console.log('  Removed existing docs folder');
}

// Copy docs
if (fs.existsSync(srcDocsDir)) {
  fs.cpSync(srcDocsDir, destDocsDir, { recursive: true });
  console.log('  Docs copied successfully!');
} else {
  console.error('  Error: Source docs folder not found!');
  console.error(`  Expected at: ${srcDocsDir}`);
  process.exit(1);
}
