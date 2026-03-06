// frontend/vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // This forwards ALL /api calls to your FastAPI backend
      "^/api/.*": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
      // Also proxy the OpenAPI docs so /docs works
      "/docs": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
      "/openapi.json": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
