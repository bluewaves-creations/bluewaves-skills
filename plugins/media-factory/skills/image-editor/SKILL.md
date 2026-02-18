---
name: image-editor
description: >
  Edit existing images with text prompts using fal.ai. Use when the user wants
  to modify, edit, transform, or change an existing image based on a text
  description. Supports multiple input images and local file upload.
allowed-tools: Bash, Read, Write
license: MIT
compatibility: Requires credentials.json or FAL_KEY environment variable (fal.ai API key), fal-client Python package
---

# Image Editor

Edit and transform existing images using text prompts with Google's Gemini 3 Pro model via fal.ai.

See `references/fal-api.md` for setup, Python patterns, and error handling.

## API Endpoint

`fal-ai/gemini-3-pro-image-preview/edit`

## Parameters

### Required
- `prompt` (string): The editing instruction describing what changes to make
- `image_urls` (array of strings): URLs of the images to edit (use `fal_client.upload_file()` for local files)

### Optional
| Parameter | Type | Default | Options |
|-----------|------|---------|---------|
| `num_images` | integer | 1 | 1-4 |
| `aspect_ratio` | string | "auto" | "auto", "21:9", "16:9", "3:2", "4:3", "5:4", "1:1", "4:5", "3:4", "2:3", "9:16" |
| `output_format` | string | "png" | "jpeg", "png", "webp" |
| `resolution` | string | "1K" | "1K", "2K", "4K" |
| `sync_mode` | boolean | false | Returns data URI directly (no download needed) |
| `enable_web_search` | boolean | true | Grounds editing in current web data |
| `safety_tolerance` | string | "6" | Always set to "6" for maximum creative freedom |
| `seed` | integer | - | Fix seed for reproducible results |
| `limit_generations` | boolean | false | Restricts to 1 image per prompt round |

Note: `aspect_ratio` defaults to "auto" for editing, which preserves the original image proportions.

## CLI Script

```bash
python3 scripts/fal_generate.py \
    --endpoint edit \
    --prompt "Add snow to this mountain scene" \
    --image /path/to/mountain.jpg \
    --output edited.png
```

## Tips

- Be specific about what changes you want: "make the sky sunset orange" is better than "change the sky"
- Use `aspect_ratio: "auto"` (the default) to preserve original image proportions
- Multiple images can be provided for context, style transfer, or combining elements
- Set `enable_web_search: True` for style-grounded edits ("make it look like a Monet painting")
- Always include `safety_tolerance: "6"` for maximum creative flexibility
- Upload local files with `fal_client.upload_file()` before passing to `image_urls`
