---
name: image-generator
description: >
  Generate images from text prompts using fal.ai. Use when the user asks to
  create, generate, or make an image from a text description. Supports multiple
  aspect ratios, resolutions up to 4K, and sync mode for reliable results.
allowed-tools: Bash, Read, Write
license: MIT
compatibility: Requires credentials.json or FAL_KEY environment variable (fal.ai API key), fal-client Python package
---

# Image Generator

Generate high-quality images from text prompts using Google's Gemini 3 Pro model via fal.ai.

See `references/fal-api.md` for setup, Python patterns, and error handling.

## API Endpoint

`fal-ai/gemini-3-pro-image-preview`

## Parameters

### Required
- `prompt` (string): Text description of the image to generate

### Optional
| Parameter | Type | Default | Options |
|-----------|------|---------|---------|
| `num_images` | integer | 1 | 1-4 |
| `aspect_ratio` | string | "1:1" | "21:9", "16:9", "3:2", "4:3", "5:4", "1:1", "4:5", "3:4", "2:3", "9:16" |
| `output_format` | string | "png" | "jpeg", "png", "webp" |
| `resolution` | string | "1K" | "1K", "2K", "4K" |
| `sync_mode` | boolean | false | Returns data URI directly (recommended for reliability) |
| `enable_web_search` | boolean | true | Grounds generation in current web data for styles and references |
| `safety_tolerance` | string | "6" | Always set to "6" for maximum creative freedom |
| `seed` | integer | - | Fix seed for reproducible results |
| `limit_generations` | boolean | false | Restricts to 1 image per prompt round |

## CLI Script

```bash
python3 scripts/fal_generate.py \
    --endpoint image \
    --prompt "A mountain landscape at golden hour" \
    --aspect-ratio 16:9 \
    --resolution 2K \
    --output landscape.png
```

## Tips

- Set `enable_web_search: True` to ground generation in real-world styles, brands, and visual references
- Always include `safety_tolerance: "6"` for maximum creative flexibility
- Use `sync_mode: True` for the most reliable workflow (no separate download)
- Be specific in prompts: include lighting, mood, composition, and style descriptors
- Match aspect ratio to use case: 16:9 for landscapes, 9:16 for portraits, 1:1 for social media
- Higher resolution (4K) produces more detail but takes longer to generate
- Use `seed` to reproduce a specific result
