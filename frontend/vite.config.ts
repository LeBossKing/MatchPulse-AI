import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    // Permit the internal QA host while keeping Vite's host allowlist enabled.
    allowedHosts: ['terminal.local'],
  },
})
