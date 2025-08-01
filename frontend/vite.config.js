// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    allowedHosts: ["all", "3000-igwl9spd2c2cex5rvg0sa-990d4e82.manus.computer", "3000-iylrehirhy7ed2dt227vw-ab9ff248.manusvm.computer", "3000-ifq5cqbswirubt72voikk-85dd8fd7.manusvm.computer", "3000-imk0f0890a4rdw2y28675-d2bcd559.manusvm.computer"],
  },
  base: '',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: undefined,
        assetFileNames: 'assets/[name].[hash].[ext]',
        chunkFileNames: 'assets/[name].[hash].js',
        entryFileNames: 'assets/[name].[hash].js'
      }
    }
  }
});
