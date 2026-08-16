import express, { type Express } from "express";
import rateLimit from "express-rate-limit";
import { createServer } from "http";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export function createApp(): Express {
  const app = express();
  const staticPath =
    process.env.NODE_ENV === "production"
      ? path.resolve(__dirname, "public")
      : path.resolve(__dirname, "..", "dist", "public");

  app.use(express.json({ limit: "2mb" }));

  const engineLimiter = rateLimit({
    windowMs: 60 * 1000,
    limit: 60,
    standardHeaders: "draft-8",
    legacyHeaders: false,
    message: { detail: "Too many engine requests; retry shortly." },
  });
  const spaLimiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    limit: 120,
    standardHeaders: "draft-8",
    legacyHeaders: false,
    message: { detail: "Too many page requests; retry shortly." },
  });

  const engineBaseUrl = (process.env.FORGEMIND_ENGINE_URL || "http://127.0.0.1:8787").replace(/\/$/, "");
  app.use("/api/engine", engineLimiter, async (req, res, next) => {
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

  // Handle client-side routing - serve index.html for all routes.
  app.get("*", spaLimiter, (_req, res) => {
    res.sendFile(path.join(staticPath, "index.html"));
  });

  return app;
}

async function startServer() {
  const app = createApp();
  const server = createServer(app);
  const port = process.env.PORT || 3000;

  server.listen(port, () => {
    console.log(`Server running on http://localhost:${port}/`);
  });
}

if (process.env.NODE_ENV !== "test" && process.env.VITEST !== "true") {
  startServer().catch(console.error);
}
