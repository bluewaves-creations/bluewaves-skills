# Site Publisher — API Reference & Troubleshooting

## Admin API Endpoints

All endpoints require `Authorization: Bearer <token>` header.

Base URL: `https://{domain}/_api`

### POST /sites/{brand}/{name}

Publish a new site.

**Request body:**
```json
{
  "title": "Q1 Proposal",
  "brand_tokens": {
    "text-heading": "#B78A66",
    "text-body": "#2C2C2C",
    "background-page": "#FFFFFF",
    "highlight": "#FF375F"
  },
  "files": {
    "index.html": "<base64-encoded content>",
    "style.css": "<base64-encoded content>",
    "assets/images/hero.jpg": "<base64-encoded content>"
  }
}
```

**Response (201):**
```json
{
  "url": "https://bluewaves.bluewaves-athena.app/q1-proposal/",
  "password": "coral-sunset-tide-2026",
  "files": 3
}
```

**Errors:**
- `400` — Missing title or files
- `409` — Site already exists (use PUT to update)

### PUT /sites/{brand}/{name}

Update an existing site's content.

**Request body:** Same as POST but `title` and `brand_tokens` are optional.

**Response (200):**
```json
{
  "updated": true,
  "files": 3
}
```

### GET /sites

List all sites.

**Query params:** `?brand=bluewaves` (optional filter)

**Response:**
```json
{
  "sites": [
    {
      "brand": "bluewaves",
      "name": "q1-proposal",
      "title": "Q1 Proposal",
      "url": "https://bluewaves.bluewaves-athena.app/q1-proposal/",
      "created": "2026-02-11T10:00:00.000Z"
    }
  ],
  "count": 1
}
```

### GET /sites/{brand}/{name}

Get site metadata (without secrets).

**Response:**
```json
{
  "brand": "bluewaves",
  "name": "q1-proposal",
  "title": "Q1 Proposal",
  "url": "https://bluewaves.bluewaves-athena.app/q1-proposal/",
  "brand_tokens": { "text-heading": "#B78A66" },
  "created": "2026-02-11T10:00:00.000Z"
}
```

### DELETE /sites/{brand}/{name}

Delete a site and all R2 objects.

**Response:**
```json
{ "deleted": true }
```

### POST /sites/{brand}/{name}/password

Rotate the site password. Invalidates all existing sessions.

**Response:**
```json
{
  "password": "amber-drift-oak-4521",
  "url": "https://bluewaves.bluewaves-athena.app/q1-proposal/"
}
```

## Storage Structure

### KV (SITE_CONFIG)

Key: `{brand}/{siteName}` (e.g. `bluewaves/q1-proposal`)

Value:
```json
{
  "password_hash": "<sha256 hex>",
  "title": "Q1 Proposal",
  "brand": "bluewaves",
  "hmac_secret": "<32-byte hex>",
  "brand_tokens": { "text-heading": "#B78A66" },
  "created": "2026-02-11T10:00:00.000Z"
}
```

Admin keys: `_admin:{sha256(token)}` → `{"name": "alice", "created": "..."}`

### R2 (SITES_BUCKET)

Keys: `{brand}/{siteName}/{path}`

Examples:
- `bluewaves/q1-proposal/index.html`
- `bluewaves/q1-proposal/style.css`
- `bluewaves/q1-proposal/assets/images/hero.jpg`
- `bluewaves/q1-proposal/files/report.pdf`

## Content Types

Determined by file extension:
- `.html` → `text/html; charset=utf-8`
- `.css` → `text/css; charset=utf-8`
- `.js` → `application/javascript; charset=utf-8`
- `.json` → `application/json; charset=utf-8`
- `.png` → `image/png`
- `.jpg/.jpeg` → `image/jpeg`
- `.svg` → `image/svg+xml`
- `.webp` → `image/webp`
- `.pdf` → `application/pdf`
- `.woff2` → `font/woff2`
- `.ttf` → `font/ttf`

Default: `application/octet-stream`

Caching: `Cache-Control: public, max-age=3600` for all R2-served files.

## Passphrase Generation

- 3 random words from a curated ~300-word list + 4-digit random number
- Joined with hyphens: `coral-sunset-tide-2026`
- Generated using `crypto.getRandomValues()` (CSPRNG)
- Words drawn from nature, colors, fauna, flora, materials, and qualities

## Update vs Publish

- **POST** (publish): Creates new site, generates password, fails if site exists
- **PUT** (update): Overwrites files, preserves password and config, fails if site doesn't exist

## Delete Procedure

1. List all R2 objects with prefix `{brand}/{siteName}/`
2. Delete objects in batches
3. Delete KV config entry
4. Site is immediately unavailable

## Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| `401 Missing Authorization` | No Bearer token | Set `admin_token` in credentials.json or `WEB_FACTORY_ADMIN_TOKEN` env |
| `403 Invalid API key` | Wrong token | Verify token matches what was set via `wrangler secret put` or KV user key |
| `404 Site not found` | Wrong brand/name or not published | Check `python3 site_api.py list` for existing sites |
| `409 Site already exists` | POST to existing site | Use `update` command instead of `publish`, or delete first |
| DNS not resolving | Wildcard DNS missing | Run `/web-factory:setup-gateway` to create `*.bluewaves-athena.app` record |
| Login page unstyled | No `brand_tokens` in KV | Re-publish with `--brand-kit` flag pointing to manifest.json |
| Cookie not working | Wrong domain/path | Ensure browser URL matches `{brand}.bluewaves-athena.app/{siteName}/` |
| Files not found | R2 key mismatch | Check that build dir structure matches expected paths |
