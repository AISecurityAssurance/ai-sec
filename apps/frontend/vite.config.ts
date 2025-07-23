import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Explicitly bind to all interfaces
    port: 5173,
    strictPort: true,
    hmr: {
      clientPort: 3002, // Use the mapped port for HMR
      host: 'localhost',
    },
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://backend:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: process.env.VITE_WS_URL || 'ws://backend:8000',
        ws: true,
      },
    },
    fs: {
      strict: false, // Allow serving files from outside root
    },
    // Add custom middleware to bypass any host checking
    configure: (app) => {
      app.use((req, res, next) => {
        // Allow any host
        res.setHeader('X-Permitted-Cross-Domain-Policies', 'all');
        next();
      });
    },
  },
  // Disable any built-in security features that might block hosts
  legacy: {
    buildSsrCjsExternalHeuristics: true,
  },
})