---
name: site-publisher
description: >
  Publish and manage password-protected branded websites on Cloudflare via the
  web-factory admin API. Publishes build directories as live sites, manages
  passwords, lists and deletes sites. Works in both Claude Code and Claude.ai
  (via Python HTTP client). This skill should be used when the user wants to
  publish a website, deploy a site to Cloudflare, manage hosted sites, rotate
  site passwords, or list/delete published sites. Triggers on requests
  mentioning site publishing, web deployment, Cloudflare hosting, or
  site management.
allowed-tools: Bash, Read, Write
license: MIT
compatibility: Python 3.8+ (stdlib only)
---
# Site Publisher

Publish and manage password-protected branded websites on Cloudflare.

## Prerequisites

Credentials must be configured via one of:
- `scripts/credentials.json` with `gateway_domain` + `admin_token` (Claude.ai)
- Environment variables `WEB_FACTORY_DOMAIN` + `WEB_FACTORY_ADMIN_TOKEN` (Claude Code)

## Operations

### Publish a New Site

1. **Verify** the build directory contains `index.html`:
   ```bash
   ls ./build/index.html
   ```

2. **Collect** from the user:
   - **Brand** (subdomain): e.g. `bluewaves`, `wave-artisans`, `decathlon`
   - **Site name** (URL path): e.g. `q1-proposal`, `annual-report` (lowercase, hyphens)
   - **Title**: Human-readable title for the site

3. **Optionally** read brand kit manifest for login page styling:
   ```bash
   # If a brand kit is available
   python3 scripts/site_api.py publish ./build {brand} {site-name} \
     --title "Document Title" \
     --brand-kit plugins/docs-factory/skills/brand-{brand}/assets/manifest.json
   ```

4. **Publish**:
   ```bash
   python3 scripts/site_api.py publish ./build {brand} {site-name} --title "Title"
   ```

5. **Report** to the user:
   - Live URL: `https://{brand}.bluewaves-athena.app/{site-name}/`
   - Generated password (4-word passphrase)
   - Number of files uploaded

### Update an Existing Site

Replace the content of an existing site without changing the password:

```bash
python3 scripts/site_api.py update ./build {brand} {site-name}
```

### List Sites

List all published sites, optionally filtered by brand:

```bash
# All sites
python3 scripts/site_api.py list

# Filter by brand
python3 scripts/site_api.py list {brand}
```

### Get Site Info

View metadata for a specific site:

```bash
python3 scripts/site_api.py info {brand} {site-name}
```

### Delete a Site

Remove a site and all its files:

```bash
python3 scripts/site_api.py delete {brand} {site-name}
```

### Rotate Password

Generate a new password for a site (invalidates existing sessions):

```bash
python3 scripts/site_api.py rotate-password {brand} {site-name}
```

Reports the new password. Share with authorized users.

## URL Pattern

Sites are served at: `https://{brand}.bluewaves-athena.app/{site-name}/`

- **Brand** = subdomain (must match a Cloudflare DNS wildcard)
- **Site name** = first path segment (lowercase, hyphens, no spaces)

## Password System

- Passwords are system-generated 4-word passphrases (e.g. `coral-sunset-tide-2026`)
- Users never choose passwords
- Passwords are shown once on publish and on rotation
- Each site has an independent password and session cookie

## Troubleshooting

See `references/publish-guide.md` for detailed API reference and troubleshooting.
