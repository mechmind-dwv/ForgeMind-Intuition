import express from "express";
import { createServer } from "http";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function startServer() {
  const app = express();
  const server = createServer(app);

  // Serve static files from dist/public in production
  const staticPath =
    process.env.NODE_ENV === "production"
      ? path.resolve(__dirname, "public")
      : path.resolve(__dirname, "..", "dist", "public");

  app.use(express.json({ limit: "2mb" }));

  const engineBaseUrl = (process.env.FORGEMIND_ENGINE_URL || "http://127.0.0.1:8787").replace(/\/$/, "");
  app.use("/api/engine", async (req, res, next) => {
    if (!req.path.startsWith("/health") && !req.path.startsWith("/v1/evaluate")) {
      return next();
    }
    try {
      const upstream = await fetch(`${engineBaseUrl}${req.path}`, {
        method: req.method,
        headers: { "content-type": "application/json" },
        body: req.method === "GET" || req.method === "HEAD" ? undefined : JSON.stringify(req.body),
      });
      const body = await upstream.text();
      res.status(upstream.status).type(upstream.headers.get("content-type") || "application/json").send(body);
    } catch (error) {
      res.status(503).json({ detail: `ForgeMind engine unavailable: ${error instanceof Error ? error.message : "unknown error"}` });
    }
  });

  app.use(express.static(staticPath));

  // Handle client-side routing - serve index.html for all routes
  app.get("*", (_req, res) => {
    res.sendFile(path.join(staticPath, "index.html"));
  });

  const port = process.env.PORT || 3000;

  server.listen(port, () => {
    console.log(`Server running on http://localhost:${port}/`);
  });
}

startServer().catch(console.error);
