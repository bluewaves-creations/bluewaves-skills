---
description: List all registered API key users for the web-factory admin API
---
List all users who have API keys for the web-factory admin API.

```bash
cd "${CLAUDE_PLUGIN_ROOT}/worker" && bunx wrangler kv key list --prefix="_admin:" --binding SITE_CONFIG
```

For each entry, display the user name and creation date from the value.
