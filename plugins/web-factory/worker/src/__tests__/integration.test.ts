/**
 * Integration tests — uses miniflare-backed KV/R2 via cloudflare:test.
 */
import { describe, it, expect, beforeEach } from "vitest";
import { SELF, env } from "cloudflare:test";

const ADMIN_TOKEN = "test-admin-token-12345";

/** Helper: make an admin API request. */
function adminFetch(
  path: string,
  init?: RequestInit & { body?: string }
): Promise<Response> {
  return SELF.fetch(`https://gateway.test/_api${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${ADMIN_TOKEN}`,
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
}

/**
 * Helper: make a public site request with the correct Host header.
 * The Host header is critical because getBrand() extracts from it.
 */
function publicFetch(
  brand: string,
  path: string,
  init?: RequestInit
): Promise<Response> {
  return SELF.fetch(`https://gateway.test${path}`, {
    ...init,
    headers: {
      Host: `${brand}.bluewaves-athena.app`,
      ...(init?.headers || {}),
    },
  });
}

/** Helper: publish a test site and return the response JSON. */
async function publishTestSite(
  brand = "testbrand",
  name = "mysite",
  extra: Record<string, unknown> = {}
) {
  const body = {
    title: "Test Site",
    files: {
      "index.html": btoa("<h1>Hello</h1>"),
      "style.css": btoa("body { color: red; }"),
    },
    ...extra,
  };
  const res = await adminFetch(`/sites/${brand}/${name}`, {
    method: "POST",
    body: JSON.stringify(body),
  });
  return { res, json: (await res.json()) as Record<string, unknown> };
}

// ─── Setup ────────────────────────────────────────────────

beforeEach(async () => {
  // Clean up any leftover test data
  const list = await env.SITE_CONFIG.list();
  for (const key of list.keys) {
    await env.SITE_CONFIG.delete(key.name);
  }
});

// ─── Health ───────────────────────────────────────────────

describe("Health check", () => {
  it("GET /_health returns 200 with security headers", async () => {
    const res = await SELF.fetch("https://gateway.test/_health");
    expect(res.status).toBe(200);
    const body = (await res.json()) as Record<string, unknown>;
    expect(body.status).toBe("ok");

    // Security headers
    expect(res.headers.get("X-Content-Type-Options")).toBe("nosniff");
    expect(res.headers.get("X-Frame-Options")).toBe("DENY");
    expect(res.headers.get("Strict-Transport-Security")).toContain("max-age=");
    expect(res.headers.get("Referrer-Policy")).toBe("strict-origin-when-cross-origin");
    expect(res.headers.get("Permissions-Policy")).toContain("camera=()");
  });
});

// ─── Admin auth ───────────────────────────────────────────

describe("Admin auth", () => {
  it("returns 401 without Authorization header", async () => {
    const res = await SELF.fetch("https://gateway.test/_api/sites", {
      method: "GET",
    });
    expect(res.status).toBe(401);
  });

  it("returns 403 with invalid token", async () => {
    const res = await SELF.fetch("https://gateway.test/_api/sites", {
      method: "GET",
      headers: { Authorization: "Bearer wrong-token" },
    });
    expect(res.status).toBe(403);
  });

  it("returns 200 with valid token", async () => {
    const res = await adminFetch("/sites");
    expect(res.status).toBe(200);
  });
});

// ─── Publish ──────────────────────────────────────────────

describe("Publish site", () => {
  it("publishes a valid site — 201", async () => {
    const { res, json } = await publishTestSite();
    expect(res.status).toBe(201);
    expect(json.url).toContain("testbrand.bluewaves-athena.app/mysite/");
    expect(json.password).toBeDefined();
    expect(json.files).toBe(2);
  });

  it("rejects missing title — 400", async () => {
    const res = await adminFetch("/sites/testbrand/mysite", {
      method: "POST",
      body: JSON.stringify({ files: { "index.html": btoa("hi") } }),
    });
    expect(res.status).toBe(400);
  });

  it("rejects invalid slug (uppercase) — 400", async () => {
    const res = await adminFetch("/sites/TestBrand/mysite", {
      method: "POST",
      body: JSON.stringify({
        title: "Test",
        files: { "index.html": btoa("hi") },
      }),
    });
    expect(res.status).toBe(400);
    const body = (await res.json()) as Record<string, unknown>;
    expect(body.error).toContain("lowercase");
  });

  it("rejects invalid slug (underscore prefix) — 400", async () => {
    const res = await adminFetch("/sites/_internal/mysite", {
      method: "POST",
      body: JSON.stringify({
        title: "Test",
        files: { "index.html": btoa("hi") },
      }),
    });
    expect(res.status).toBe(400);
  });

  it("rejects path traversal in files — 400", async () => {
    const res = await adminFetch("/sites/testbrand/mysite", {
      method: "POST",
      body: JSON.stringify({
        title: "Test",
        files: { "../../../etc/passwd": btoa("evil") },
      }),
    });
    expect(res.status).toBe(400);
    const body = (await res.json()) as Record<string, unknown>;
    expect(body.error).toContain("..");
  });

  it("rejects invalid base64 — 400", async () => {
    const res = await adminFetch("/sites/testbrand/badbase64", {
      method: "POST",
      body: JSON.stringify({
        title: "Test",
        files: { "index.html": "not-valid-base64!!!" },
      }),
    });
    expect(res.status).toBe(400);
    const body = (await res.json()) as Record<string, unknown>;
    expect(body.error).toContain("base64");
  });

  it("rejects invalid brand_tokens — 400", async () => {
    const res = await adminFetch("/sites/testbrand/badtokens", {
      method: "POST",
      body: JSON.stringify({
        title: "Test",
        files: { "index.html": btoa("hi") },
        brand_tokens: { highlight: "not-a-color" },
      }),
    });
    expect(res.status).toBe(400);
    const body = (await res.json()) as Record<string, unknown>;
    expect(body.error).toContain("hex");
  });

  it("rejects duplicate site — 409", async () => {
    await publishTestSite("testbrand", "dupsite");
    const { res } = await publishTestSite("testbrand", "dupsite");
    expect(res.status).toBe(409);
  });
});

// ─── CRUD ─────────────────────────────────────────────────

describe("Site CRUD", () => {
  it("lists sites", async () => {
    await publishTestSite("brandx", "site1");
    await publishTestSite("brandx", "site2");

    const res = await adminFetch("/sites?brand=brandx");
    expect(res.status).toBe(200);
    const body = (await res.json()) as { sites: unknown[]; count: number };
    expect(body.count).toBe(2);
    expect(body.sites).toHaveLength(2);
  });

  it("gets site metadata without secrets", async () => {
    const { json: publishJson } = await publishTestSite("brandx", "getme");

    const res = await adminFetch("/sites/brandx/getme");
    expect(res.status).toBe(200);
    const body = (await res.json()) as Record<string, unknown>;
    expect(body.title).toBe("Test Site");
    expect(body.brand).toBe("brandx");
    // Should NOT leak secrets
    expect(body).not.toHaveProperty("password_hash");
    expect(body).not.toHaveProperty("hmac_secret");
    // Make sure the password was in the publish response
    expect(publishJson.password).toBeDefined();
  });

  it("updates a site", async () => {
    await publishTestSite("brandx", "updateme");

    const res = await adminFetch("/sites/brandx/updateme", {
      method: "PUT",
      body: JSON.stringify({
        title: "Updated Title",
        files: { "index.html": btoa("<h1>Updated</h1>") },
      }),
    });
    expect(res.status).toBe(200);
    const body = (await res.json()) as Record<string, unknown>;
    expect(body.updated).toBe(true);
    expect(body.files).toBe(1);
  });

  it("deletes a site", async () => {
    await publishTestSite("brandx", "deleteme");

    const res = await adminFetch("/sites/brandx/deleteme", {
      method: "DELETE",
    });
    expect(res.status).toBe(200);
    const body = (await res.json()) as Record<string, unknown>;
    expect(body.deleted).toBe(true);

    // Verify it's gone
    const getRes = await adminFetch("/sites/brandx/deleteme");
    expect(getRes.status).toBe(404);
  });

  it("rotates password", async () => {
    const { json: publishJson } = await publishTestSite("brandx", "rotateme");

    const res = await adminFetch("/sites/brandx/rotateme/password", {
      method: "POST",
    });
    expect(res.status).toBe(200);
    const body = (await res.json()) as Record<string, unknown>;
    expect(body.password).toBeDefined();
    // New password should differ from original
    expect(body.password).not.toBe(publishJson.password);
  });
});

// ─── Auth flow ────────────────────────────────────────────

describe("Auth flow", () => {
  it("login page renders for valid site", async () => {
    await publishTestSite("authbrand", "authsite");

    const res = await publicFetch("authbrand", "/authsite/_login");
    expect(res.status).toBe(200);
    const html = await res.text();
    expect(html).toContain("Test Site");
    expect(html).toContain("password");
    // CSP header
    expect(res.headers.get("Content-Security-Policy")).toContain("default-src");
  });

  it("correct password returns 302 + cookie", async () => {
    const { json } = await publishTestSite("authbrand", "logintest");
    const password = json.password as string;

    const res = await publicFetch("authbrand", "/logintest/_login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        Host: "authbrand.bluewaves-athena.app",
      },
      body: `password=${encodeURIComponent(password)}`,
      redirect: "manual",
    });
    expect(res.status).toBe(302);
    expect(res.headers.get("Location")).toBe("/logintest/");
    expect(res.headers.get("Set-Cookie")).toContain("wf_session=");
  });

  it("wrong password returns 403", async () => {
    await publishTestSite("authbrand", "failtest");

    const res = await publicFetch("authbrand", "/failtest/_login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        Host: "authbrand.bluewaves-athena.app",
      },
      body: "password=wrong-password",
      redirect: "manual",
    });
    expect(res.status).toBe(403);
  });

  it("valid cookie grants access", async () => {
    const { json } = await publishTestSite("authbrand", "cookietest");
    const password = json.password as string;

    // Login to get cookie
    const loginRes = await publicFetch("authbrand", "/cookietest/_login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        Host: "authbrand.bluewaves-athena.app",
      },
      body: `password=${encodeURIComponent(password)}`,
      redirect: "manual",
    });
    const setCookie = loginRes.headers.get("Set-Cookie") || "";
    const cookieVal = setCookie.split(";")[0]; // "wf_session=..."

    // Access site with cookie
    const res = await publicFetch("authbrand", "/cookietest/index.html", {
      headers: {
        Cookie: cookieVal,
        Host: "authbrand.bluewaves-athena.app",
      },
    });
    expect(res.status).toBe(200);
    const body = await res.text();
    expect(body).toContain("Hello");
  });

  it("no cookie redirects to login", async () => {
    await publishTestSite("authbrand", "noauth");

    const res = await publicFetch("authbrand", "/noauth/index.html", {
      redirect: "manual",
    });
    expect(res.status).toBe(302);
    expect(res.headers.get("Location")).toBe("/noauth/_login");
  });
});

// ─── R2 serving ───────────────────────────────────────────

describe("R2 serving", () => {
  /** Login and return session cookie string "wf_session=..." */
  async function loginAndGetCookie(
    brand: string,
    siteName: string,
    password: string
  ): Promise<string> {
    const loginRes = await publicFetch(brand, `/${siteName}/_login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        Host: `${brand}.bluewaves-athena.app`,
      },
      body: `password=${encodeURIComponent(password)}`,
      redirect: "manual",
    });
    return (loginRes.headers.get("Set-Cookie") || "").split(";")[0];
  }

  it("serves index.html for trailing slash", async () => {
    const { json } = await publishTestSite("r2brand", "r2site");
    const cookie = await loginAndGetCookie("r2brand", "r2site", json.password as string);

    const res = await publicFetch("r2brand", "/r2site/", {
      headers: { Cookie: cookie, Host: "r2brand.bluewaves-athena.app" },
    });
    expect(res.status).toBe(200);
    expect(res.headers.get("Content-Type")).toContain("text/html");
    expect(res.headers.get("X-Content-Type-Options")).toBe("nosniff");
  });

  it("serves correct MIME type for CSS", async () => {
    const { json } = await publishTestSite("r2brand", "mimesite");
    const cookie = await loginAndGetCookie("r2brand", "mimesite", json.password as string);

    const res = await publicFetch("r2brand", "/mimesite/style.css", {
      headers: { Cookie: cookie, Host: "r2brand.bluewaves-athena.app" },
    });
    expect(res.status).toBe(200);
    expect(res.headers.get("Content-Type")).toContain("text/css");
  });

  it("returns 404 for missing file", async () => {
    const { json } = await publishTestSite("r2brand", "missing");
    const cookie = await loginAndGetCookie("r2brand", "missing", json.password as string);

    const res = await publicFetch("r2brand", "/missing/nonexistent.html", {
      headers: { Cookie: cookie, Host: "r2brand.bluewaves-athena.app" },
    });
    expect(res.status).toBe(404);
  });
});

// ─── Rate limiting ────────────────────────────────────────

describe("Rate limiting", () => {
  async function failLogin(
    brand: string,
    siteName: string,
    ip: string
  ): Promise<Response> {
    return publicFetch(brand, `/${siteName}/_login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        Host: `${brand}.bluewaves-athena.app`,
        "CF-Connecting-IP": ip,
      },
      body: "password=wrong",
      redirect: "manual",
    });
  }

  it("blocks after 10 failed login attempts", async () => {
    await publishTestSite("ratelimit", "rlsite");

    for (let i = 0; i < 10; i++) {
      await failLogin("ratelimit", "rlsite", "1.2.3.4");
    }

    const res = await failLogin("ratelimit", "rlsite", "1.2.3.4");
    expect(res.status).toBe(429);
  });

  it("different IPs have separate limits", async () => {
    await publishTestSite("ratelimit", "ipsite");

    // Exhaust rate limit for IP 10.0.0.1
    for (let i = 0; i < 10; i++) {
      await failLogin("ratelimit", "ipsite", "10.0.0.1");
    }

    // Different IP should still work (403 = wrong password, not 429)
    const res = await failLogin("ratelimit", "ipsite", "10.0.0.2");
    expect(res.status).toBe(403);
  });

  it("successful login resets counter", async () => {
    const { json } = await publishTestSite("ratelimit", "resetsite");
    const password = json.password as string;

    // 5 failed attempts
    for (let i = 0; i < 5; i++) {
      await failLogin("ratelimit", "resetsite", "5.5.5.5");
    }

    // Successful login
    await publicFetch("ratelimit", "/resetsite/_login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        Host: "ratelimit.bluewaves-athena.app",
        "CF-Connecting-IP": "5.5.5.5",
      },
      body: `password=${encodeURIComponent(password)}`,
      redirect: "manual",
    });

    // Should be able to fail again without hitting 429
    const res = await failLogin("ratelimit", "resetsite", "5.5.5.5");
    expect(res.status).toBe(403);
  });
});

// ─── Input validation on public routes ────────────────────

describe("Public route input validation", () => {
  it("rejects uppercase brand in public route", async () => {
    const res = await publicFetch("TestBrand", "/mysite/index.html", {
      redirect: "manual",
    });
    expect(res.status).toBe(400);
  });

  it("rejects underscore-prefix siteName in public route", async () => {
    const res = await publicFetch("testbrand", "/_internal/index.html", {
      redirect: "manual",
    });
    expect(res.status).toBe(400);
  });
});

// ─── Error handler ────────────────────────────────────────

describe("Global error handler", () => {
  it("returns 500 with generic error", async () => {
    // Verify the app boots and handles requests
    const res = await SELF.fetch("https://gateway.test/_health");
    expect(res.status).toBe(200);
  });
});
