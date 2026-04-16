import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// Railway's edge proxy forces 'Access-Control-Allow-Origin: https://railway.com'
// on all responses, which blocks browser requests from any other origin.
// To work around this platform limitation during local development, the Vite
// dev-server proxy is ALWAYS enabled so that /api requests are forwarded to
// the local backend (http://localhost:8000) and never hit the Railway edge
// proxy directly. VITE_API_URL is intentionally ignored here — it is only
// relevant for production deployments where both services share the same origin.

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    // Always proxy /api → local backend in development.
    // This bypasses the Railway edge proxy CORS limitation entirely.
    proxy: {
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
