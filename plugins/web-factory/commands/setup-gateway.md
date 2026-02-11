---
description: One-time setup for the web-factory gateway Worker on Cloudflare
---
Deploy the web-factory gateway Worker to Cloudflare. This is a **one-time** setup operation.

**Prerequisites:** Cloudflare API token with Workers, R2, KV, and DNS permissions. Account ID configured.

Follow these steps in order:

1. **Validate Cloudflare credentials:**
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/cf_utils.py" --check-key
   ```

2. **Create R2 bucket:**
   ```bash
   bunx wrangler r2 bucket create web-factory-sites
   ```

3. **Create KV namespace** and capture the namespace ID:
   ```bash
   bunx wrangler kv namespace create SITE_CONFIG
   ```
   Copy the `id` from the output.

4. **Update wrangler.jsonc** with the KV namespace ID:
   - Open `${CLAUDE_PLUGIN_ROOT}/worker/wrangler.jsonc`
   - Replace `REPLACE_AFTER_SETUP` with the actual KV namespace ID

5. **Set the super-admin token secret:**
   ```bash
   cd "${CLAUDE_PLUGIN_ROOT}/worker" && bunx wrangler secret put ADMIN_TOKEN
   ```
   Enter a strong token when prompted. Save this token — it's the master API key.

6. **Install deps and deploy:**
   ```bash
   cd "${CLAUDE_PLUGIN_ROOT}/worker" && bun install && bunx wrangler deploy
   ```

7. **Create wildcard DNS** (if not already set):
   ```bash
   bunx wrangler dns create bluewaves-athena.app --type A --name "*.bluewaves-athena.app" --content 192.0.2.0 --proxied
   ```

8. **Verify** the deployment:
   ```bash
   curl https://bluewaves.bluewaves-athena.app/_health
   ```
   Should return `{"status":"ok","service":"web-factory-gateway"}`.

Report the results of each step to the user.
