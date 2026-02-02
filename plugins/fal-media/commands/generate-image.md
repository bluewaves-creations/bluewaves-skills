---
description: Generate an image from a text prompt using Gemini 3 Pro via fal.ai
---
Generate an image using the Gemini 3 Pro model via fal.ai.

$ARGUMENTS

The arguments are the image prompt. If no arguments are provided, ask the user for a prompt.

## Steps

1. Confirm `FAL_KEY` is set. If not, tell the user to run `/fal-media:check-fal-key`.

2. Generate the image using cURL:
   ```bash
   curl --request POST \
     --url https://fal.run/fal-ai/gemini-3-pro-image-preview \
     --header "Authorization: Key $FAL_KEY" \
     --header "Content-Type: application/json" \
     --data '{
       "prompt": "<USER_PROMPT>",
       "num_images": 1,
       "aspect_ratio": "1:1",
       "resolution": "2K",
       "output_format": "png"
     }'
   ```

3. Extract the image URL from the JSON response (`.images[0].url`).

4. Download the image to the current directory:
   ```bash
   curl -sL "<image_url>" -o "generated-image.png"
   ```

5. Open the image for the user:
   ```bash
   open "generated-image.png"
   ```

6. Display the image path and URL to the user.
