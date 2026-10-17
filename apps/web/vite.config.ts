import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In dev, /api requests are proxied to the Django server, so no CORS is needed locally.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
