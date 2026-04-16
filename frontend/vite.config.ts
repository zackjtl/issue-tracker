import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// NOTE: vite.config.ts runs in Node.js, so import.meta.env is NOT available
// here. Use process.env to read variables set in the shell / .env files that
// are loaded by Vite's own dotenv handling before this config is evaluated.
// VITE_API_URL is read via process.env so we can decide whether to enable the
// dev-server proxy (only needed when there is no external API URL configured).
const viteApiUrl = process.env.VITE_API_URL;

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    // Only proxy /api → localhost:8000 when VITE_API_URL is not set.
    // When VITE_API_URL is set (e.g. https://issue-tracker.railway.app/api)
    // the frontend makes direct requests and no proxy is needed.
    proxy: viteApiUrl ? undefined : {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  // Build configuration
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
