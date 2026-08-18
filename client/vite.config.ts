import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { tanstackRouter } from '@tanstack/router-plugin/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    tanstackRouter({ target: 'react', autoCodeSplitting: true }),
    react(),
    tailwindcss(),
  ],
  // zustand lists `react` as an *optional* peer dependency. Vite 8 (rolldown)
  // otherwise stubs that import out, so zustand fails to find React at runtime.
  // Pre-bundling zustand resolves its `react` import against the real package,
  // and deduping keeps a single React instance across the app and the dep.
  optimizeDeps: {
    include: ['zustand'],
  },
  resolve: {
    dedupe: ['react', 'react-dom'],
  },
})
