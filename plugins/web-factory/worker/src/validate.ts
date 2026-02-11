/**
 * Validation and sanitization utilities for the web-factory gateway.
 *
 * All functions are pure and side-effect-free for easy testing.
 */

// ─── Constants ────────────────────────────────────────────

export const MAX_FILE_COUNT = 200;
export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB
export const MAX_TOTAL_SIZE = 50 * 1024 * 1024; // 50 MB
export const RATE_LIMIT_MAX = 10;
export const RATE_LIMIT_WINDOW = 300; // seconds

// ─── Slug validation ──────────────────────────────────────

const SLUG_RE = /^[a-z0-9]([a-z0-9-]*[a-z0-9])?$/;
const MAX_SLUG_LENGTH = 63;

/**
 * Validate a slug (brand name or site name).
 * Must be lowercase alphanumeric with optional hyphens, 1–63 chars.
 * Returns an error string or null if valid.
 */
export function validateSlug(value: string, label: string): string | null {
  if (!value) return `${label} is required`;
  if (value.length > MAX_SLUG_LENGTH)
    return `${label} must be at most ${MAX_SLUG_LENGTH} characters`;
  if (!SLUG_RE.test(value))
    return `${label} must be lowercase alphanumeric with hyphens (a-z, 0-9, -)`;
  return null;
}

// ─── File path sanitization ───────────────────────────────

const MAX_PATH_LENGTH = 512;

/**
 * Sanitize a file path for R2 storage.
 * Returns the sanitized path or throws an error string.
 */
export function sanitizeFilePath(rawPath: string): string {
  if (!rawPath) return "file path is empty";
  if (rawPath.length > MAX_PATH_LENGTH) return "file path too long";
  if (rawPath.includes("..")) return "file path contains '..'";
  if (rawPath.includes("\0")) return "file path contains null byte";
  if (rawPath.includes("\\")) return "file path contains backslash";
  // Reject control characters (0x00–0x1F, 0x7F)
  if (/[\x00-\x1f\x7f]/.test(rawPath)) return "file path contains control characters";
  // Strip leading slashes
  return rawPath.replace(/^\/+/, "");
}

// ─── CSS color validation ─────────────────────────────────

const HEX_COLOR_RE = /^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/;

/** Accept only hex color values: #RGB, #RRGGBB, #RRGGBBAA */
export function isValidCssColor(value: string): boolean {
  return HEX_COLOR_RE.test(value);
}

/** Validate all color values in a brand_tokens record. Returns first error or null. */
export function validateBrandTokens(
  tokens: Record<string, string>
): string | null {
  for (const [key, value] of Object.entries(tokens)) {
    if (!isValidCssColor(value)) {
      return `Invalid color for "${key}": must be hex (#RGB, #RRGGBB, or #RRGGBBAA)`;
    }
  }
  return null;
}

// ─── Timing-safe comparison ───────────────────────────────

/**
 * Timing-safe string comparison using crypto.subtle.
 * Returns true if a === b without leaking timing information.
 */
export async function timingSafeEqual(
  a: string,
  b: string
): Promise<boolean> {
  const encoder = new TextEncoder();
  const aBuf = encoder.encode(a);
  const bBuf = encoder.encode(b);
  if (aBuf.byteLength !== bBuf.byteLength) {
    // Hash both to avoid leaking length via timing
    const key = await crypto.subtle.importKey(
      "raw",
      new Uint8Array(32),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"]
    );
    await crypto.subtle.sign("HMAC", key, aBuf);
    await crypto.subtle.sign("HMAC", key, bBuf);
    return false;
  }
  // Use XOR comparison with constant iteration count
  let diff = 0;
  for (let i = 0; i < aBuf.length; i++) {
    diff |= aBuf[i] ^ bBuf[i];
  }
  return diff === 0;
}

// ─── Base64 decoding ──────────────────────────────────────

/**
 * Safe base64 decode — returns Uint8Array or null (never throws).
 */
export function safeAtob(b64: string): Uint8Array | null {
  try {
    const raw = atob(b64);
    const bytes = new Uint8Array(raw.length);
    for (let i = 0; i < raw.length; i++) {
      bytes[i] = raw.charCodeAt(i);
    }
    return bytes;
  } catch {
    return null;
  }
}
