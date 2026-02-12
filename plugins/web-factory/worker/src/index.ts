/**
 * Web Factory Gateway — Hono app serving branded websites from R2
 * with HMAC cookie-based password protection and an admin API.
 *
 * Deployed as a single Worker on *.bluewaves-athena.app
 */
import { Hono } from "hono";
import type { Env } from "./auth";
import { authMiddleware, handleLogin, handleLoginPost } from "./auth";
import {
  adminAuth,
  publishSite,
  updateSite,
  listSites,
  getSite,
  downloadSite,
  deleteSite,
  rotatePassword,
} from "./admin";
import { serveFromR2 } from "./r2";
import { validateSlug } from "./validate";

const app = new Hono<{ Bindings: Env }>();

// ─── Global security headers ─────────────────────────────

app.use("*", async (c, next) => {
  await next();
  c.res.headers.set("X-Content-Type-Options", "nosniff");
  c.res.headers.set("X-Frame-Options", "DENY");
  c.res.headers.set(
    "Strict-Transport-Security",
    "max-age=63072000; includeSubDomains; preload"
  );
  c.res.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  c.res.headers.set("Permissions-Policy", "camera=(), microphone=(), geolocation=()");
});

// ─── Global error handler ────────────────────────────────

app.onError((err, c) => {
  console.error("Unhandled error:", err);
  return c.json({ error: "Internal server error" }, 500);
});

// ─── Admin API ────────────────────────────────────────────

const api = new Hono<{ Bindings: Env }>();
api.use("*", adminAuth);

api.post("/sites/:brand/:name", publishSite);
api.put("/sites/:brand/:name", async (c) => {
  const brand = c.req.param("brand");
  const name = c.req.param("name");
  return updateSite(c, brand, name);
});
api.get("/sites", listSites);
api.get("/sites/:brand/:name", async (c) => {
  const brand = c.req.param("brand");
  const name = c.req.param("name");
  return getSite(c, brand, name);
});
api.get("/sites/:brand/:name/files", async (c) => {
  const brand = c.req.param("brand");
  const name = c.req.param("name");
  return downloadSite(c, brand, name);
});
api.delete("/sites/:brand/:name", async (c) => {
  const brand = c.req.param("brand");
  const name = c.req.param("name");
  return deleteSite(c, brand, name);
});
api.post("/sites/:brand/:name/password", async (c) => {
  const brand = c.req.param("brand");
  const name = c.req.param("name");
  return rotatePassword(c, brand, name);
});

app.route("/_api", api);

// ─── Health check ─────────────────────────────────────────

app.get("/_health", (c) => c.json({ status: "ok", service: "web-factory-gateway" }));

// ─── Public site routes ───────────────────────────────────

// Extract brand from subdomain
function getBrand(c: { req: { header: (name: string) => string | undefined } }): string | null {
  const host = c.req.header("Host") || "";
  // Expected: {brand}.bluewaves-athena.app
  const match = host.match(/^([^.]+)\.bluewaves-athena\.app/);
  return match ? match[1] : null;
}

/** Validate brand and siteName on public routes. Returns error Response or null. */
function validatePublicParams(
  c: { text: (body: string, status: number) => Response },
  brand: string | null,
  siteName: string
): Response | null {
  if (!brand) return c.text("Invalid host", 400);
  if (validateSlug(brand, "brand")) return c.text("Invalid brand", 400);
  if (validateSlug(siteName, "siteName")) return c.text("Invalid site name", 400);
  return null;
}

// Login routes (exempt from auth)
app.get("/:siteName/_login", async (c) => {
  const brand = getBrand(c);
  const siteName = c.req.param("siteName");
  const err = validatePublicParams(c, brand, siteName);
  if (err) return err;
  return handleLogin(c, brand!, siteName);
});

app.post("/:siteName/_login", async (c) => {
  const brand = getBrand(c);
  const siteName = c.req.param("siteName");
  const err = validatePublicParams(c, brand, siteName);
  if (err) return err;
  return handleLoginPost(c, brand!, siteName);
});

// Catch-all: auth middleware + R2 file serving
app.get("/:siteName/*", async (c) => {
  const brand = getBrand(c);
  const siteName = c.req.param("siteName");
  const err = validatePublicParams(c, brand, siteName);
  if (err) return err;

  const fullPath = c.req.path;
  // Strip /{siteName}/ prefix to get the file path
  const filePath = fullPath.replace(`/${siteName}`, "");

  // Run auth middleware
  let authPassed = false;
  const authResponse = await authMiddleware(
    c,
    async () => { authPassed = true; },
    brand!,
    siteName
  );
  if (!authPassed) {
    return authResponse;
  }

  return serveFromR2(c, brand!, siteName, filePath);
});

// Root redirect for /:siteName (no trailing slash)
app.get("/:siteName", async (c) => {
  const brand = getBrand(c);
  const siteName = c.req.param("siteName");
  const err = validatePublicParams(c, brand, siteName);
  if (err) return err;
  return c.redirect(`/${siteName}/`, 301);
});

export default app;
