/**
 * Admin API handlers: publish, list, update, delete, rotate password.
 *
 * All endpoints require Bearer token auth (ADMIN_TOKEN or user API key).
 */
import type { Context, Next } from "hono";
import type { Env, SiteConfig } from "./auth";
import { sha256 } from "./auth";
import { generatePassphrase } from "./words";
import {
  validateSlug,
  sanitizeFilePath,
  validateBrandTokens,
  timingSafeEqual,
  safeAtob,
  MAX_FILE_COUNT,
  MAX_FILE_SIZE,
  MAX_TOTAL_SIZE,
} from "./validate";

/** Admin auth middleware: check ADMIN_TOKEN secret, then KV user keys. */
export async function adminAuth(
  c: Context<{ Bindings: Env }>,
  next: Next
): Promise<Response | void> {
  const authHeader = c.req.header("Authorization") || "";
  if (!authHeader.startsWith("Bearer ")) {
    return c.json({ error: "Missing Authorization header" }, 401);
  }
  const token = authHeader.slice(7);

  // Check super-admin secret first (timing-safe)
  if (c.env.ADMIN_TOKEN && (await timingSafeEqual(token, c.env.ADMIN_TOKEN))) {
    return next();
  }

  // Check user API keys in KV
  const tokenHash = await sha256(token);
  const userRecord = await c.env.SITE_CONFIG.get(`_admin:${tokenHash}`);
  if (userRecord) {
    return next();
  }

  return c.json({ error: "Invalid API key" }, 403);
}

/** Generate a random HMAC secret (hex). */
async function generateHmacSecret(): Promise<string> {
  const bytes = new Uint8Array(32);
  crypto.getRandomValues(bytes);
  return Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

/**
 * Validate brand and siteName from route params.
 * Returns error Response or null if valid.
 */
function validateParams(
  c: Context<{ Bindings: Env }>,
  brand: string,
  siteName: string
): Response | null {
  const brandErr = validateSlug(brand, "brand");
  if (brandErr) return c.json({ error: brandErr }, 400) as unknown as Response;
  const nameErr = validateSlug(siteName, "siteName");
  if (nameErr) return c.json({ error: nameErr }, 400) as unknown as Response;
  return null;
}

interface PublishRequestBody {
  title: string;
  brand_tokens?: Record<string, string>;
  files: Record<string, string>; // path → base64 content
}

/** POST /_api/sites/:brand/:name — Publish a new site. */
export async function publishSite(
  c: Context<{ Bindings: Env }>
): Promise<Response> {
  const brand = c.req.param("brand");
  const siteName = c.req.param("name");

  const paramErr = validateParams(c, brand, siteName);
  if (paramErr) return paramErr;

  let body: PublishRequestBody;
  try {
    body = await c.req.json<PublishRequestBody>();
  } catch {
    return c.json({ error: "Invalid JSON body" }, 400);
  }

  if (!body.title || !body.files || Object.keys(body.files).length === 0) {
    return c.json({ error: "title and files are required" }, 400);
  }

  // Validate brand_tokens if provided
  if (body.brand_tokens) {
    const tokensErr = validateBrandTokens(body.brand_tokens);
    if (tokensErr) return c.json({ error: tokensErr }, 400);
  }

  // Check if site already exists
  const existing = await c.env.SITE_CONFIG.get(`${brand}/${siteName}`);
  if (existing) {
    return c.json(
      { error: "Site already exists. Use PUT to update or DELETE first." },
      409
    );
  }

  // Generate passphrase and HMAC secret
  const passphrase = generatePassphrase();
  const passwordHash = await sha256(passphrase);
  const hmacSecret = await generateHmacSecret();

  // Store files in R2 (validates paths, sizes, and base64 before writing)
  const result = await storeFiles(c, brand, siteName, body.files);
  if (typeof result === "string") {
    return c.json({ error: result }, 400);
  }

  // Store config in KV
  const config: SiteConfig = {
    password_hash: passwordHash,
    title: body.title,
    brand,
    hmac_secret: hmacSecret,
    brand_tokens: body.brand_tokens,
    created: new Date().toISOString(),
  };
  await c.env.SITE_CONFIG.put(`${brand}/${siteName}`, JSON.stringify(config));

  const siteUrl = `https://${brand}.bluewaves-athena.app/${siteName}/`;
  return c.json({ url: siteUrl, password: passphrase, files: result }, 201);
}

/** PUT /_api/sites/{brand}/{name} — Update site content. */
export async function updateSite(
  c: Context<{ Bindings: Env }>,
  brand: string,
  siteName: string
): Promise<Response> {
  const paramErr = validateParams(c, brand, siteName);
  if (paramErr) return paramErr;

  const configRaw = await c.env.SITE_CONFIG.get(`${brand}/${siteName}`);
  if (!configRaw) {
    return c.json({ error: "Site not found" }, 404);
  }

  let body: PublishRequestBody;
  try {
    body = await c.req.json<PublishRequestBody>();
  } catch {
    return c.json({ error: "Invalid JSON body" }, 400);
  }

  if (!body.files || Object.keys(body.files).length === 0) {
    return c.json({ error: "files are required" }, 400);
  }

  // Validate brand_tokens if provided
  if (body.brand_tokens) {
    const tokensErr = validateBrandTokens(body.brand_tokens);
    if (tokensErr) return c.json({ error: tokensErr }, 400);
  }

  // Store new files (validates then writes, with rollback on failure)
  const result = await storeFiles(c, brand, siteName, body.files);
  if (typeof result === "string") {
    return c.json({ error: result }, 400);
  }

  // Update config if title or brand_tokens changed
  const config: SiteConfig = JSON.parse(configRaw);
  if (body.title) config.title = body.title;
  if (body.brand_tokens) config.brand_tokens = body.brand_tokens;
  await c.env.SITE_CONFIG.put(`${brand}/${siteName}`, JSON.stringify(config));

  return c.json({ updated: true, files: result });
}

/** GET /_api/sites — List all sites, optionally filtered by ?brand=. */
export async function listSites(
  c: Context<{ Bindings: Env }>
): Promise<Response> {
  const brandFilter = c.req.query("brand");
  const prefix = brandFilter ? `${brandFilter}/` : undefined;

  // Paginate through all KV keys
  const sites: Array<{
    brand: string;
    name: string;
    title: string;
    url: string;
    created: string;
  }> = [];

  let cursor: string | undefined;
  do {
    const list = await c.env.SITE_CONFIG.list({ prefix, cursor });

    for (const key of list.keys) {
      // Skip internal keys
      if (key.name.startsWith("_")) continue;

      const raw = await c.env.SITE_CONFIG.get(key.name);
      if (!raw) continue;
      const config: SiteConfig = JSON.parse(raw);

      const parts = key.name.split("/");
      if (parts.length < 2) continue;

      sites.push({
        brand: parts[0],
        name: parts[1],
        title: config.title,
        url: `https://${parts[0]}.bluewaves-athena.app/${parts[1]}/`,
        created: config.created,
      });
    }

    cursor = list.list_complete ? undefined : list.cursor;
  } while (cursor);

  return c.json({ sites, count: sites.length });
}

/** GET /_api/sites/{brand}/{name} — Get site metadata (without secrets). */
export async function getSite(
  c: Context<{ Bindings: Env }>,
  brand: string,
  siteName: string
): Promise<Response> {
  const paramErr = validateParams(c, brand, siteName);
  if (paramErr) return paramErr;

  const configRaw = await c.env.SITE_CONFIG.get(`${brand}/${siteName}`);
  if (!configRaw) {
    return c.json({ error: "Site not found" }, 404);
  }
  const config: SiteConfig = JSON.parse(configRaw);

  return c.json({
    brand: config.brand,
    name: siteName,
    title: config.title,
    url: `https://${brand}.bluewaves-athena.app/${siteName}/`,
    brand_tokens: config.brand_tokens,
    created: config.created,
  });
}

/** DELETE /_api/sites/{brand}/{name} — Delete site and all R2 objects. */
export async function deleteSite(
  c: Context<{ Bindings: Env }>,
  brand: string,
  siteName: string
): Promise<Response> {
  const paramErr = validateParams(c, brand, siteName);
  if (paramErr) return paramErr;

  const configRaw = await c.env.SITE_CONFIG.get(`${brand}/${siteName}`);
  if (!configRaw) {
    return c.json({ error: "Site not found" }, 404);
  }

  // Delete all R2 objects with the site prefix
  const prefix = `${brand}/${siteName}/`;
  let cursor: string | undefined;
  do {
    const listed = await c.env.SITES_BUCKET.list({ prefix, cursor });
    if (listed.objects.length > 0) {
      await c.env.SITES_BUCKET.delete(listed.objects.map((o) => o.key));
    }
    cursor = listed.truncated ? listed.cursor : undefined;
  } while (cursor);

  // Delete KV config
  await c.env.SITE_CONFIG.delete(`${brand}/${siteName}`);

  return c.json({ deleted: true });
}

/** POST /_api/sites/{brand}/{name}/password — Rotate password. */
export async function rotatePassword(
  c: Context<{ Bindings: Env }>,
  brand: string,
  siteName: string
): Promise<Response> {
  const paramErr = validateParams(c, brand, siteName);
  if (paramErr) return paramErr;

  const configRaw = await c.env.SITE_CONFIG.get(`${brand}/${siteName}`);
  if (!configRaw) {
    return c.json({ error: "Site not found" }, 404);
  }

  const config: SiteConfig = JSON.parse(configRaw);
  const newPassphrase = generatePassphrase();
  config.password_hash = await sha256(newPassphrase);

  // Also rotate HMAC secret to invalidate existing sessions
  const bytes = new Uint8Array(32);
  crypto.getRandomValues(bytes);
  config.hmac_secret = Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");

  await c.env.SITE_CONFIG.put(`${brand}/${siteName}`, JSON.stringify(config));

  return c.json({
    password: newPassphrase,
    url: `https://${brand}.bluewaves-athena.app/${siteName}/`,
  });
}

/**
 * Store base64-encoded files in R2.
 *
 * Two-pass approach:
 *  1. Validate all paths, decode all base64, enforce size limits
 *  2. Write all to R2; on failure, compensating-delete written keys
 *
 * Returns file count on success, or error string on validation failure.
 */
async function storeFiles(
  c: Context<{ Bindings: Env }>,
  brand: string,
  siteName: string,
  files: Record<string, string>
): Promise<number | string> {
  const entries = Object.entries(files);

  // Check file count
  if (entries.length > MAX_FILE_COUNT) {
    return `Too many files: ${entries.length} exceeds maximum of ${MAX_FILE_COUNT}`;
  }

  // Pass 1: validate and decode all files
  const decoded: Array<{ r2Key: string; bytes: Uint8Array }> = [];
  let totalSize = 0;

  for (const [path, b64Content] of entries) {
    // Sanitize path
    const sanitized = sanitizeFilePath(path);
    if (sanitized !== path.replace(/^\/+/, "")) {
      // sanitizeFilePath returned an error string
      return `Invalid file path "${path}": ${sanitized}`;
    }

    // Decode base64
    const bytes = safeAtob(b64Content);
    if (!bytes) {
      return `Invalid base64 content for file "${path}"`;
    }

    // Check per-file size
    if (bytes.byteLength > MAX_FILE_SIZE) {
      return `File "${path}" exceeds maximum size of ${MAX_FILE_SIZE / (1024 * 1024)} MB`;
    }

    totalSize += bytes.byteLength;
    if (totalSize > MAX_TOTAL_SIZE) {
      return `Total payload exceeds maximum of ${MAX_TOTAL_SIZE / (1024 * 1024)} MB`;
    }

    decoded.push({ r2Key: `${brand}/${siteName}/${sanitized}`, bytes });
  }

  // Pass 2: write to R2 with rollback on failure
  const writtenKeys: string[] = [];
  try {
    for (const { r2Key, bytes } of decoded) {
      await c.env.SITES_BUCKET.put(r2Key, bytes);
      writtenKeys.push(r2Key);
    }
  } catch (err) {
    // Compensating delete for any keys already written
    if (writtenKeys.length > 0) {
      try {
        await c.env.SITES_BUCKET.delete(writtenKeys);
      } catch {
        // Best-effort cleanup
      }
    }
    throw err;
  }

  return decoded.length;
}
