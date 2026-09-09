import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";
import path from "node:path";
import fs from "node:fs";

const here = path.dirname(fileURLToPath(import.meta.url));
const siteRoot = path.resolve(here, "..");

/** I dev serveres fontene fra repo-roten (/fonts.css, /fonts/*) slik produksjonen gjør. */
type Srv = { middlewares: { use: (fn: (req: { url?: string }, res: NodeJS.WritableStream & { setHeader: (k: string, v: string) => void }, next: () => void) => void) => void } };
function siteFonts() {
  const use = (server: Srv): void => {
    server.middlewares.use((req, res, next) => {
      const url = (req.url ?? "").split("?")[0] ?? "";
      if (url === "/fonts.css" || url.startsWith("/fonts/") || url === "/favicon.svg") {
        const file = path.join(siteRoot, url);
        if (fs.existsSync(file)) {
          res.setHeader("Content-Type", url.endsWith(".css") ? "text/css" : url.endsWith(".svg") ? "image/svg+xml" : "font/woff2");
          fs.createReadStream(file).pipe(res);
          return;
        }
      }
      next();
    });
  };
  return { name: "era-site-fonts", configureServer: use, configurePreviewServer: use };
}

export default defineConfig({
  base: "/app/",
  plugins: [react(), siteFonts()],
  resolve: { alias: { "@": path.resolve(here, "src") } },
  build: { outDir: path.resolve(siteRoot, "app"), emptyOutDir: true, sourcemap: false },
  server: { port: 5178, strictPort: true },
  preview: { port: 5179, strictPort: true },
  test: { environment: "node", include: ["src/**/*.test.ts"] },
});
