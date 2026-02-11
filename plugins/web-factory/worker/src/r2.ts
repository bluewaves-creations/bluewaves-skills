/**
 * R2 file serving with MIME type mapping and caching headers.
 */
import type { Context } from "hono";
import type { Env } from "./auth";

const MIME_TYPES: Record<string, string> = {
  html: "text/html; charset=utf-8",
  css: "text/css; charset=utf-8",
  js: "application/javascript; charset=utf-8",
  mjs: "application/javascript; charset=utf-8",
  json: "application/json; charset=utf-8",
  png: "image/png",
  jpg: "image/jpeg",
  jpeg: "image/jpeg",
  gif: "image/gif",
  svg: "image/svg+xml",
  webp: "image/webp",
  avif: "image/avif",
  ico: "image/x-icon",
  pdf: "application/pdf",
  woff: "font/woff",
  woff2: "font/woff2",
  ttf: "font/ttf",
  otf: "font/otf",
  eot: "application/vnd.ms-fontobject",
  xml: "application/xml",
  txt: "text/plain; charset=utf-8",
  mp4: "video/mp4",
  webm: "video/webm",
  mp3: "audio/mpeg",
  wav: "audio/wav",
  zip: "application/zip",
};

export function getMimeType(path: string): string {
  const ext = path.split(".").pop()?.toLowerCase() || "";
  return MIME_TYPES[ext] || "application/octet-stream";
}

/**
 * Serve a file from R2.
 *
 * R2 key format: {brand}/{siteName}/{path}
 * Default: index.html if path ends with /
 */
export async function serveFromR2(
  c: Context<{ Bindings: Env }>,
  brand: string,
  siteName: string,
  filePath: string
): Promise<Response> {
  // Normalize: strip leading slash, default to index.html
  let normalizedPath = filePath.replace(/^\/+/, "");
  if (!normalizedPath || normalizedPath.endsWith("/")) {
    normalizedPath += "index.html";
  }

  const r2Key = `${brand}/${siteName}/${normalizedPath}`;
  const object = await c.env.SITES_BUCKET.get(r2Key);

  if (!object) {
    return c.text("Not found", 404);
  }

  const contentType = getMimeType(normalizedPath);
  const headers = new Headers({
    "Content-Type": contentType,
    "Cache-Control": "public, max-age=3600",
    ETag: object.httpEtag,
  });

  return new Response(object.body, { headers });
}
