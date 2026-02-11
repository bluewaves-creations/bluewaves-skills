/**
 * HMAC cookie signing, SHA-256 password check, and auth middleware.
 *
 * Cookie format: {timestamp}-{base64_hmac}
 * HMAC payload: {brand}/{siteName}:{timestamp}
 */
import type { Context, Next } from "hono";
import { renderLoginPage } from "./login";
import { timingSafeEqual, RATE_LIMIT_MAX, RATE_LIMIT_WINDOW } from "./validate";

export interface SiteConfig {
  password_hash: string;
  title: string;
  brand: string;
  hmac_secret: string;
  brand_tokens?: Record<string, string>;
  created: string;
}

export interface Env {
  SITES_BUCKET: R2Bucket;
  SITE_CONFIG: KVNamespace;
  ADMIN_TOKEN: string;
  COOKIE_NAME: string;
  SESSION_TTL_SECONDS: string;
}

/** SHA-256 hash a string, return hex. */
export async function sha256(input: string): Promise<string> {
  const data = new TextEncoder().encode(input);
  const hash = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(hash))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

/** Create an HMAC signature over a payload using the given secret. */
async function hmacSign(secret: string, payload: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sig = await crypto.subtle.sign(
    "HMAC",
    key,
    new TextEncoder().encode(payload)
  );
  return btoa(String.fromCharCode(...new Uint8Array(sig)));
}

/** Verify an HMAC signature. */
async function hmacVerify(
  secret: string,
  payload: string,
  signature: string
): Promise<boolean> {
  const expected = await hmacSign(secret, payload);
  return timingSafeEqual(expected, signature);
}

/** Create a signed session cookie value. */
export async function createSessionCookie(
  brand: string,
  siteName: string,
  hmacSecret: string
): Promise<string> {
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const payload = `${brand}/${siteName}:${timestamp}`;
  const sig = await hmacSign(hmacSecret, payload);
  return `${timestamp}-${sig}`;
}

/** Parse cookie header and extract a named cookie value. */
export function getCookie(cookieHeader: string | null, name: string): string | null {
  if (!cookieHeader) return null;
  const match = cookieHeader.match(new RegExp(`(?:^|;\\s*)${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

/** CSP header value for login pages. */
const LOGIN_CSP =
  "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'";

/**
 * Auth middleware for public site access.
 * Validates HMAC session cookie; redirects to login if invalid.
 */
export async function authMiddleware(
  c: Context<{ Bindings: Env }>,
  next: Next,
  brand: string,
  siteName: string
) {
  const kv = c.env.SITE_CONFIG;
  const cookieName = c.env.COOKIE_NAME || "wf_session";
  const ttl = parseInt(c.env.SESSION_TTL_SECONDS || "86400", 10);

  // Look up site config
  const configRaw = await kv.get(`${brand}/${siteName}`);
  if (!configRaw) {
    return c.text("Site not found", 404);
  }
  const config: SiteConfig = JSON.parse(configRaw);

  // Check cookie
  const cookieHeader = c.req.header("Cookie") ?? null;
  const cookieVal = getCookie(cookieHeader, cookieName);

  if (cookieVal) {
    const dashIdx = cookieVal.indexOf("-");
    if (dashIdx > 0) {
      const timestamp = cookieVal.substring(0, dashIdx);
      const sig = cookieVal.substring(dashIdx + 1);
      const payload = `${brand}/${siteName}:${timestamp}`;
      const age = Math.floor(Date.now() / 1000) - parseInt(timestamp, 10);

      if (age < ttl && age >= 0) {
        const valid = await hmacVerify(config.hmac_secret, payload, sig);
        if (valid) {
          // Store config for downstream handlers
          c.set("siteConfig" as never, config as never);
          return next();
        }
      }
    }
  }

  // No valid session — redirect to login
  return c.redirect(`/${siteName}/_login`);
}

/**
 * Check IP rate limit for login attempts.
 * Returns true if the IP is rate-limited (should be blocked).
 */
async function isRateLimited(
  kv: KVNamespace,
  ip: string
): Promise<boolean> {
  const key = `_ratelimit:${ip}`;
  const raw = await kv.get(key);
  if (!raw) return false;
  return parseInt(raw, 10) >= RATE_LIMIT_MAX;
}

/** Increment the rate limit counter for an IP. */
async function incrementRateLimit(
  kv: KVNamespace,
  ip: string
): Promise<void> {
  const key = `_ratelimit:${ip}`;
  const raw = await kv.get(key);
  const count = raw ? parseInt(raw, 10) + 1 : 1;
  await kv.put(key, String(count), { expirationTtl: RATE_LIMIT_WINDOW });
}

/** Reset the rate limit counter for an IP. */
async function resetRateLimit(
  kv: KVNamespace,
  ip: string
): Promise<void> {
  await kv.delete(`_ratelimit:${ip}`);
}

/** Render the branded login page. */
export async function handleLogin(
  c: Context<{ Bindings: Env }>,
  brand: string,
  siteName: string
): Promise<Response> {
  const configRaw = await c.env.SITE_CONFIG.get(`${brand}/${siteName}`);
  if (!configRaw) {
    return c.text("Site not found", 404);
  }
  const config: SiteConfig = JSON.parse(configRaw);
  const html = renderLoginPage(config.title, brand, siteName, config.brand_tokens);
  return new Response(html, {
    status: 200,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Content-Security-Policy": LOGIN_CSP,
    },
  });
}

/** Handle login form submission. */
export async function handleLoginPost(
  c: Context<{ Bindings: Env }>,
  brand: string,
  siteName: string
): Promise<Response> {
  const ip = c.req.header("CF-Connecting-IP") || c.req.header("X-Forwarded-For") || "unknown";

  // Check rate limit before any processing
  if (await isRateLimited(c.env.SITE_CONFIG, ip)) {
    return c.json({ error: "Too many login attempts. Try again later." }, 429);
  }

  const configRaw = await c.env.SITE_CONFIG.get(`${brand}/${siteName}`);
  if (!configRaw) {
    return c.text("Site not found", 404);
  }
  const config: SiteConfig = JSON.parse(configRaw);

  const body = await c.req.parseBody();
  const password = (body["password"] as string) || "";
  const hash = await sha256(password);

  const hashesMatch = await timingSafeEqual(hash, config.password_hash);
  if (!hashesMatch) {
    await incrementRateLimit(c.env.SITE_CONFIG, ip);
    const html = renderLoginPage(
      config.title,
      brand,
      siteName,
      config.brand_tokens,
      "Incorrect password. Please try again."
    );
    return new Response(html, {
      status: 403,
      headers: {
        "Content-Type": "text/html; charset=utf-8",
        "Content-Security-Policy": LOGIN_CSP,
      },
    });
  }

  // Successful login — reset rate limit counter
  await resetRateLimit(c.env.SITE_CONFIG, ip);

  // Create signed session cookie
  const cookieName = c.env.COOKIE_NAME || "wf_session";
  const ttl = parseInt(c.env.SESSION_TTL_SECONDS || "86400", 10);
  const cookieVal = await createSessionCookie(brand, siteName, config.hmac_secret);

  return new Response(null, {
    status: 302,
    headers: {
      Location: `/${siteName}/`,
      "Set-Cookie": `${cookieName}=${cookieVal}; Path=/${siteName}; HttpOnly; Secure; SameSite=Lax; Max-Age=${ttl}`,
    },
  });
}
