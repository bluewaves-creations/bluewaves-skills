---
description: Validate Cloudflare credentials and gateway admin token
---
Diagnose the web-factory credential setup by performing these checks:

1. **Check credential resolution** (credentials file or env vars):
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/cf_utils.py" --check-key
   ```

2. **If the check fails**, guide the user:
   - For Claude Code: Add env vars to `~/.zshrc`:
     ```bash
     export WEB_FACTORY_ADMIN_TOKEN="your-admin-token"
     export CLOUDFLARE_API_TOKEN="your-cloudflare-api-token"
     export CLOUDFLARE_ACCOUNT_ID="your-account-id"
     ```
     Then `source ~/.zshrc`
   - For Claude.ai: Create `scripts/credentials.json` from `scripts/credentials.example.json`

3. **Report results** with a clear summary and next steps if anything failed.
