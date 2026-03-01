import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const DEBUG_ENABLED = process.env.DEBUG === "true";

if (DEBUG_ENABLED) {
  console.debug("[FluxMod:vite]", {
    mode: process.env.NODE_ENV,
    port: 5173,
  });
}

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
});
