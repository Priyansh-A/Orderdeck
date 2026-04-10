// import { defineConfig } from 'vite'
// import react from '@vitejs/plugin-react'
// import tailwindcss from '@tailwindcss/vite'

// export default defineConfig({
//   plugins: [
//     react(),
//     tailwindcss(),
//   ],
//   build: {
//     outDir: 'dist',
//     emptyOutDir: true,
//     rollupOptions: {
//       output: {
//         manualChunks: undefined,
//       },
//     },
//   },
//   server: {
//     port: 5173,
//     open: true
//   },
//   css: {
//     devSourcemap: true,
//   },
//   optimizeDeps: {
//     include: ['react', 'react-dom', 'react-router-dom'],
//   },
// })

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    host: true,
    watch: {
      usePolling: true,
      interval: 1000,
    },
    hmr: {
      overlay: true,
    },
  },
})