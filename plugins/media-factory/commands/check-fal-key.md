---
description: Check if FAL_KEY is set and test fal.ai API connectivity
---
Diagnose the fal.ai API key setup by performing these checks:

1. **Check API key resolution** (env var or credentials file):
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/fal_utils.py" --check-key
   ```

2. **If the check fails**, guide the user:
   - For Claude Code: Add `export FAL_KEY="your-api-key"` to `~/.zshrc`, then `source ~/.zshrc`
   - For Claude.ai: Create `scripts/credentials.json` with `{"api_key": "your-key"}`

3. **Test API connectivity** (only if key resolved):
   ```bash
   python3 -c "
   import fal_client, os
   os.environ.setdefault('FAL_KEY', '')
   try:
       result = fal_client.run('fal-ai/gemini-3-pro-image-preview', arguments={'prompt': 'test', 'num_images': 1, 'resolution': '1K'})
       print('API connectivity: OK')
   except Exception as e:
       print(f'API error: {e}')
   "
   ```

4. **Report results** with a clear summary and next steps if anything failed.
