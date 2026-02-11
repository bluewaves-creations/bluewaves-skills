---
description: Revoke a user's API key for the web-factory admin API
---
Revoke a user's access to the web-factory admin API.

1. **Ask the user** which key to revoke (by name).

2. **List existing keys** to find the matching entry:
   ```bash
   cd "${CLAUDE_PLUGIN_ROOT}/worker" && bunx wrangler kv key list --prefix="_admin:" --binding SITE_CONFIG
   ```

3. **Find the key** whose value JSON contains the matching `name` field.

4. **Delete the KV entry:**
   ```bash
   cd "${CLAUDE_PLUGIN_ROOT}/worker" && bunx wrangler kv key delete "_admin:HASH_HERE" --binding SITE_CONFIG
   ```

5. **Confirm** the revocation to the user.
