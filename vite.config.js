import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Keep CRA's `build/` Output so Existing GH Pages Workflows Stay Unchanged
  build: {
    outDir: 'build',
    emptyOutDir: true,
  },
  // Custom Domain Serves from Site Root
  base: '/',
  // CSV Imported as Asset URL (Fetched + Parsed with PapaParse)
  assetsInclude: ['**/*.csv'],
  server: {
    port: 3000,
    open: true,
  },
  css: {
    preprocessorOptions: {
      scss: {
        // Silence Legacy Sass API Noise from Dependencies
        silenceDeprecations: ['legacy-js-api', 'import'],
      },
    },
  },
});
