# web-factory

Password-protected branded websites on Cloudflare. A single Hono gateway Worker serves sites from R2 with HMAC cookie-based password protection and an admin API.

## Architecture

- **Gateway Worker**: Hono app on `*.bluewaves-athena.app` — public auth + R2 serving + admin API
- **R2 Bucket**: Static site files (HTML, CSS, images, fonts, PDFs)
- **KV Namespace**: Site config (password hash, HMAC secret, brand tokens)
- **Admin API**: `/_api/` endpoints for publish, list, update, delete, rotate password

URL pattern: `https://{brand}.bluewaves-athena.app/{site-name}/`

## Skills

- **site-factory** — Build branded single-page HTML from markdown using docs-factory brand kits
- **site-publisher** — Publish/manage sites via the admin API (works in Claude.ai + Claude Code)

## Commands

| Command | Description |
|---------|-------------|
| `/web-factory:install-deps` | Install Worker dependencies (`bun install`) |
| `/web-factory:check-cf-key` | Validate Cloudflare and gateway credentials |
| `/web-factory:setup-gateway` | One-time: deploy Worker + create R2/KV + DNS |
| `/web-factory:create-api-key` | Generate a user API key |
| `/web-factory:list-api-keys` | List registered API key users |
| `/web-factory:revoke-api-key` | Revoke a user's API key |

## Prerequisites

- **Gateway (one-time setup)**: bun, wrangler, Cloudflare API token with Workers/R2/KV/DNS permissions
- **Publishing**: `WEB_FACTORY_ADMIN_TOKEN` env var or `credentials.json`
- **Site building**: Python 3.8+ (stdlib only for site_api.py)

## Quick Start

```bash
# 1. Install plugin
/plugin install web-factory@bluewaves-skills

# 2. One-time gateway setup
/web-factory:setup-gateway

# 3. Build a site (uses brand-bluewaves)
# "Create a branded website from this markdown for Bluewaves"

# 4. Publish
# "Publish the site as bluewaves/q1-proposal"
```
