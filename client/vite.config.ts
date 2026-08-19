import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { tanstackRouter } from '@tanstack/router-plugin/vite'

export default defineConfig({
  server: {
    port: 5173,
    strictPort: true,
    // Same-origin in the browser: forward API calls to the FastAPI backend so
    // the client can use an empty base path (see src/api.ts). 127.0.0.1 (not
    // localhost) because uvicorn binds IPv4 only.
    //
    // Match `/api` as a path segment (regex key) so it doesn't also swallow
    // sibling paths like /api-client/index.ts — the generated client source
    // that Vite must serve itself in dev.
    //
    // The backend target is overridable (VITE_API_PROXY_TARGET) so the e2e
    // suite can point a dev server at its isolated API on a non-default port.
    proxy: {
      '^/api(?:/|$)': process.env.VITE_API_PROXY_TARGET ?? 'http://127.0.0.1:8000',
    },
  },
  plugins: [
    tanstackRouter({ target: 'react', autoCodeSplitting: true }),
    react(),
    tailwindcss(),
  ],
  optimizeDeps: {
    include: ['zustand'],
  },
  resolve: {
    dedupe: ['react', 'react-dom'],
  },
})
