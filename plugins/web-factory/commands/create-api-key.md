---
description: Generate a user API key for the web-factory admin API
---
Generate a new API key for a user to access the web-factory admin API.

1. **Ask the user** for a name to identify this key (e.g. "alice", "ci-bot").

2. **Generate the token:**
   ```bash
   TOKEN=$(openssl rand -base64 32) && echo "Token: $TOKEN"
   ```

3. **Compute SHA-256 hash:**
   ```bash
   HASH=$(echo -n "$TOKEN" | shasum -a 256 | cut -d' ' -f1) && echo "Hash: $HASH"
   ```

4. **Store in KV:**
   ```bash
   cd "${CLAUDE_PLUGIN_ROOT}/worker" && bunx wrangler kv key put "_admin:${HASH}" "{\"name\":\"USER_NAME\",\"created\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" --binding SITE_CONFIG
   ```
   Replace `USER_NAME` with the actual name from step 1.

5. **Report the token** to the user. Emphasize:
   - This token is shown **once** and cannot be recovered
   - Store it securely (e.g. in `credentials.json` or as `WEB_FACTORY_ADMIN_TOKEN` env var)
   - The token grants full access to publish, update, and delete all sites
