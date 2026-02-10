---
description: Generate an image from a text prompt using fal.ai via Python fal_client
---
Generate an image using the fal.ai Gemini 3 Pro model via the Python fal_client.

$ARGUMENTS

The arguments are the image prompt. If no arguments are provided, ask the user for a prompt.

## Steps

1. Confirm the API key is available:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/fal_utils.py" --check-key
   ```
   If not set, tell the user to run `/media-factory:check-fal-key`.

2. Generate the image using fal_generate.py:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/fal_generate.py" \
     --endpoint image \
     --prompt "<USER_PROMPT>" \
     --aspect-ratio "16:9" \
     --resolution "2K" \
     --output "generated-image.png"
   ```

3. The script automatically:
   - Downloads the result with a timestamped filename
   - Opens the image for the user (macOS/Linux)
   - Displays the file path

4. Show the user the generated image path and any description from the model.
