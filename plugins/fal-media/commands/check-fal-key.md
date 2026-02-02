---
description: Check if FAL_KEY is set and test fal.ai API connectivity
---
Diagnose the fal.ai API key setup by performing these checks:

1. **Check FAL_KEY is set:**
   ```bash
   if [[ -z "${FAL_KEY:-}" ]]; then
     echo "FAL_KEY is NOT set."
     echo ""
     echo "To fix, add to ~/.zshrc:"
     echo '  export FAL_KEY="your-api-key"'
     echo "Then run: source ~/.zshrc"
   else
     echo "FAL_KEY is set (${#FAL_KEY} characters)"
   fi
   ```

2. **Test API connectivity** (only if key is set):
   ```bash
   curl -s -o /dev/null -w "%{http_code}" \
     --max-time 10 \
     --url https://fal.run/fal-ai/gemini-3-pro-image-preview \
     --header "Authorization: Key $FAL_KEY" \
     --header "Content-Type: application/json" \
     --data '{"prompt": "test", "num_images": 1, "resolution": "1K"}'
   ```
   - **200**: Key is valid, API is reachable
   - **401/403**: Key is invalid or expired
   - **Other**: Network or service issue

3. **Report results** with a clear summary and next steps if anything failed.
