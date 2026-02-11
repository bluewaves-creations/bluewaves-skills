/**
 * Unit tests for pure functions — no Workers bindings needed.
 */
import { describe, it, expect } from "vitest";
import {
  validateSlug,
  sanitizeFilePath,
  isValidCssColor,
  validateBrandTokens,
  timingSafeEqual,
  safeAtob,
} from "../validate";
import { escapeHtml, capitalize } from "../login";
import { getMimeType } from "../r2";
import { getCookie, sha256 } from "../auth";
import { generatePassphrase } from "../words";

// ─── validateSlug ─────────────────────────────────────────

describe("validateSlug", () => {
  it("accepts valid slugs", () => {
    expect(validateSlug("my-site", "name")).toBeNull();
    expect(validateSlug("a", "name")).toBeNull();
    expect(validateSlug("site123", "name")).toBeNull();
    expect(validateSlug("my-cool-site-2", "name")).toBeNull();
    expect(validateSlug("a1b2c3", "name")).toBeNull();
  });

  it("rejects empty string", () => {
    expect(validateSlug("", "brand")).toBe("brand is required");
  });

  it("rejects uppercase", () => {
    expect(validateSlug("MyBrand", "brand")).toContain("lowercase");
  });

  it("rejects leading hyphen", () => {
    expect(validateSlug("-site", "name")).toContain("lowercase");
  });

  it("rejects trailing hyphen", () => {
    expect(validateSlug("site-", "name")).toContain("lowercase");
  });

  it("rejects underscores", () => {
    expect(validateSlug("my_site", "name")).toContain("lowercase");
  });

  it("rejects special characters", () => {
    expect(validateSlug("my.site", "name")).toContain("lowercase");
    expect(validateSlug("my/site", "name")).toContain("lowercase");
    expect(validateSlug("my site", "name")).toContain("lowercase");
  });

  it("rejects too-long values", () => {
    const long = "a".repeat(64);
    expect(validateSlug(long, "name")).toContain("at most 63");
  });

  it("accepts max-length slug", () => {
    expect(validateSlug("a".repeat(63), "name")).toBeNull();
  });
});

// ─── sanitizeFilePath ─────────────────────────────────────

describe("sanitizeFilePath", () => {
  it("accepts valid paths", () => {
    expect(sanitizeFilePath("index.html")).toBe("index.html");
    expect(sanitizeFilePath("css/style.css")).toBe("css/style.css");
    expect(sanitizeFilePath("assets/img/logo.png")).toBe("assets/img/logo.png");
  });

  it("strips leading slashes", () => {
    expect(sanitizeFilePath("/index.html")).toBe("index.html");
    expect(sanitizeFilePath("///deep/path.js")).toBe("deep/path.js");
  });

  it("rejects path traversal", () => {
    expect(sanitizeFilePath("../etc/passwd")).toContain("..");
    expect(sanitizeFilePath("foo/../../bar")).toContain("..");
  });

  it("rejects null bytes", () => {
    expect(sanitizeFilePath("file\0.html")).toContain("null byte");
  });

  it("rejects backslashes", () => {
    expect(sanitizeFilePath("path\\file.html")).toContain("backslash");
  });

  it("rejects control characters", () => {
    expect(sanitizeFilePath("file\x01.html")).toContain("control");
  });

  it("rejects empty path", () => {
    expect(sanitizeFilePath("")).toContain("empty");
  });

  it("rejects too-long paths", () => {
    expect(sanitizeFilePath("a".repeat(513))).toContain("too long");
  });
});

// ─── isValidCssColor ──────────────────────────────────────

describe("isValidCssColor", () => {
  it("accepts #RGB", () => {
    expect(isValidCssColor("#fff")).toBe(true);
    expect(isValidCssColor("#ABC")).toBe(true);
  });

  it("accepts #RRGGBB", () => {
    expect(isValidCssColor("#ff0066")).toBe(true);
    expect(isValidCssColor("#AABBCC")).toBe(true);
  });

  it("accepts #RRGGBBAA", () => {
    expect(isValidCssColor("#ff006680")).toBe(true);
  });

  it("rejects named colors", () => {
    expect(isValidCssColor("red")).toBe(false);
    expect(isValidCssColor("transparent")).toBe(false);
  });

  it("rejects rgb() notation", () => {
    expect(isValidCssColor("rgb(255,0,0)")).toBe(false);
  });

  it("rejects invalid hex", () => {
    expect(isValidCssColor("#gggggg")).toBe(false);
    expect(isValidCssColor("#12345")).toBe(false);
    expect(isValidCssColor("ff0066")).toBe(false);
  });
});

// ─── validateBrandTokens ─────────────────────────────────

describe("validateBrandTokens", () => {
  it("accepts valid tokens", () => {
    expect(
      validateBrandTokens({ highlight: "#0066CC", background: "#FFFFFF" })
    ).toBeNull();
  });

  it("returns error for invalid color", () => {
    const err = validateBrandTokens({ highlight: "blue", bg: "#FFF" });
    expect(err).toContain("highlight");
    expect(err).toContain("hex");
  });
});

// ─── timingSafeEqual ──────────────────────────────────────

describe("timingSafeEqual", () => {
  it("returns true for equal strings", async () => {
    expect(await timingSafeEqual("hello", "hello")).toBe(true);
  });

  it("returns false for unequal strings", async () => {
    expect(await timingSafeEqual("hello", "world")).toBe(false);
  });

  it("returns false for different-length strings", async () => {
    expect(await timingSafeEqual("short", "much-longer-string")).toBe(false);
  });

  it("returns true for empty strings", async () => {
    expect(await timingSafeEqual("", "")).toBe(true);
  });
});

// ─── safeAtob ─────────────────────────────────────────────

describe("safeAtob", () => {
  it("decodes valid base64", () => {
    const result = safeAtob(btoa("hello world"));
    expect(result).not.toBeNull();
    const text = new TextDecoder().decode(result!);
    expect(text).toBe("hello world");
  });

  it("returns null for invalid base64", () => {
    expect(safeAtob("not-valid-base64!!!")).toBeNull();
  });

  it("handles empty string", () => {
    const result = safeAtob(btoa(""));
    expect(result).not.toBeNull();
    expect(result!.length).toBe(0);
  });
});

// ─── escapeHtml ───────────────────────────────────────────

describe("escapeHtml", () => {
  it("escapes angle brackets", () => {
    expect(escapeHtml("<script>")).toBe("&lt;script&gt;");
  });

  it("escapes ampersand", () => {
    expect(escapeHtml("A & B")).toBe("A &amp; B");
  });

  it("escapes double quotes", () => {
    expect(escapeHtml('"hello"')).toBe("&quot;hello&quot;");
  });

  it("escapes single quotes", () => {
    expect(escapeHtml("it's")).toBe("it&#39;s");
  });

  it("passes through plain strings", () => {
    expect(escapeHtml("hello world")).toBe("hello world");
  });
});

// ─── capitalize ───────────────────────────────────────────

describe("capitalize", () => {
  it("capitalizes first letter", () => {
    expect(capitalize("hello")).toBe("Hello");
  });

  it("handles single character", () => {
    expect(capitalize("a")).toBe("A");
  });

  it("handles already capitalized", () => {
    expect(capitalize("Hello")).toBe("Hello");
  });

  it("handles empty string", () => {
    expect(capitalize("")).toBe("");
  });
});

// ─── getMimeType ──────────────────────────────────────────

describe("getMimeType", () => {
  it("returns correct MIME for known extensions", () => {
    expect(getMimeType("file.html")).toBe("text/html; charset=utf-8");
    expect(getMimeType("style.css")).toBe("text/css; charset=utf-8");
    expect(getMimeType("app.js")).toBe("application/javascript; charset=utf-8");
    expect(getMimeType("photo.jpg")).toBe("image/jpeg");
    expect(getMimeType("image.png")).toBe("image/png");
    expect(getMimeType("doc.pdf")).toBe("application/pdf");
  });

  it("returns octet-stream for unknown extensions", () => {
    expect(getMimeType("file.xyz")).toBe("application/octet-stream");
    expect(getMimeType("noext")).toBe("application/octet-stream");
  });

  it("handles nested paths", () => {
    expect(getMimeType("assets/css/main.css")).toBe("text/css; charset=utf-8");
  });
});

// ─── getCookie ────────────────────────────────────────────

describe("getCookie", () => {
  it("extracts a cookie value", () => {
    expect(getCookie("wf_session=abc123; other=456", "wf_session")).toBe("abc123");
  });

  it("returns null for missing cookie", () => {
    expect(getCookie("other=456", "wf_session")).toBeNull();
  });

  it("returns null for null header", () => {
    expect(getCookie(null, "wf_session")).toBeNull();
  });

  it("handles cookie at start of header", () => {
    expect(getCookie("token=xyz", "token")).toBe("xyz");
  });
});

// ─── sha256 ───────────────────────────────────────────────

describe("sha256", () => {
  it("produces correct hash for known input", async () => {
    // SHA-256 of empty string
    const hash = await sha256("");
    expect(hash).toBe("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
  });

  it("produces consistent results", async () => {
    const a = await sha256("test-input");
    const b = await sha256("test-input");
    expect(a).toBe(b);
  });

  it("produces different hashes for different inputs", async () => {
    const a = await sha256("hello");
    const b = await sha256("world");
    expect(a).not.toBe(b);
  });
});

// ─── generatePassphrase ───────────────────────────────────

describe("generatePassphrase", () => {
  it("matches word-word-word-NNNN format", () => {
    const passphrase = generatePassphrase();
    const parts = passphrase.split("-");
    // 3 words + 1 number (but words could have been split — check at least 4 parts)
    expect(parts.length).toBeGreaterThanOrEqual(4);
    // Last part should be a 4-digit number
    const lastPart = parts[parts.length - 1];
    expect(lastPart).toMatch(/^\d{4}$/);
    const num = parseInt(lastPart, 10);
    expect(num).toBeGreaterThanOrEqual(1000);
    expect(num).toBeLessThanOrEqual(9999);
  });

  it("generates different passphrases", () => {
    const a = generatePassphrase();
    const b = generatePassphrase();
    // With 272 words and 9000 numbers, collision probability is negligible
    expect(a).not.toBe(b);
  });
});
