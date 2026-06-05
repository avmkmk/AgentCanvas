/// <reference types="vitest" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/setupTests.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov"],
      include: ["src/**/*.{ts,tsx}"],
      exclude: ["src/main.tsx", "src/index.css"],
    },
  },
  server: {
    host: "0.0.0.0",
    port: 3000,
    // Proxy API requests to backend — avoids CORS in development
    // Analytics service on :8001 must be listed before the generic /api entry
    proxy: {
      "/api/v1/analytics": {
        target: "http://localhost:8001",
        changeOrigin: true,
      },
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/ws": {
        target: "ws://localhost:8000",
        ws: true,
      },
    },
  },
  preview: {
    host: "0.0.0.0",
    port: 3000,
  },
});
