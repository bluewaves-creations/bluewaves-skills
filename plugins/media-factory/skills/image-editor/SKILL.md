---
name: image-editor
description: >
  Edit existing images with text prompts using fal.ai. Use when the user wants
  to modify, edit, transform, or change an existing image based on a text
  description. Supports multiple input images and local file upload.
allowed-tools: Bash, Read, Write
license: MIT
compatibility: Requires FAL_KEY environment variable or credentials.json (fal.ai API key), fal-client Python package
---

# Image Editor

Edit and transform existing images using text prompts with Google's Gemini 3 Pro model via fal.ai.

## Prerequisites

- **API key**: `FAL_KEY` environment variable (add to `~/.zshrc`) or `credentials.json` with `{"api_key": "..."}` in the scripts/ directory (Claude.ai standalone ZIPs)
- **Python package**: `uv pip install fal-client`

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

## Usage

### Python (fal_client)

```python
import fal_client

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            print(f"  [{log.get('level', 'info')}] {log.get('message', '')}")

result = fal_client.subscribe(
    "fal-ai/gemini-3-pro-image-preview/edit",
    arguments={
        "prompt": "Add snow to this mountain scene and make it winter",
        "image_urls": ["https://example.com/mountain.jpg"],
        "num_images": 1,
        "output_format": "png",
        "safety_tolerance": "6",
        "enable_web_search": True,
    },
    with_logs=True,
    on_queue_update=on_queue_update,
)

edited_url = result["images"][0]["url"]
print(f"Edited image: {edited_url}")
```

### Editing a Local File

```python
import fal_client

# Upload local image to fal.ai CDN first
uploaded_url = fal_client.upload_file("/path/to/local/photo.jpg")

result = fal_client.subscribe(
    "fal-ai/gemini-3-pro-image-preview/edit",
    arguments={
        "prompt": "Convert this photo to a watercolor painting style",
        "image_urls": [uploaded_url],
        "safety_tolerance": "6",
        "enable_web_search": True,
    },
)

edited_url = result["images"][0]["url"]
print(f"Edited image: {edited_url}")
```

### Multiple Input Images

Provide multiple images in `image_urls` to combine elements or provide additional context.

```python
import fal_client

result = fal_client.subscribe(
    "fal-ai/gemini-3-pro-image-preview/edit",
    arguments={
        "prompt": "Combine elements from these images into a cohesive scene",
        "image_urls": [
            "https://example.com/background.jpg",
            "https://example.com/subject.jpg",
        ],
        "safety_tolerance": "6",
        "enable_web_search": True,
    },
)
```

### CLI Script

```bash
python scripts/fal_generate.py \
    --endpoint edit \
    --prompt "Add snow to this mountain scene" \
    --image /path/to/mountain.jpg \
    --output edited.png
```

## Response Format

```json
{
  "images": [
    {
      "file_name": "edited_image.png",
      "content_type": "image/png",
      "url": "https://storage.googleapis.com/..."
    }
  ],
  "description": "A description of the edited image"
}
```

## Error Handling

```python
import fal_client

try:
    result = fal_client.subscribe("fal-ai/gemini-3-pro-image-preview/edit", arguments={...})
except fal_client.FalClientError as e:
    print(f"API error: {e}")         # Auth failures, invalid params, bad image URLs
except fal_client.FalClientTimeoutError as e:
    print(f"Timeout: {e}")           # Generation took too long
except Exception as e:
    print(f"Unexpected error: {e}")
```

| Symptom | Cause | Solution |
|---------|-------|----------|
| `FalClientError` (401) | Invalid FAL_KEY | Verify key at fal.ai dashboard |
| `FalClientError` (429) | Rate limit exceeded | Wait 60 seconds, retry |
| `FalClientError` (400) | Invalid image URL or parameters | Ensure image URLs are publicly accessible or use `upload_file()` |
| `FalClientTimeoutError` | Generation too slow | Reduce resolution or simplify edit |
| Empty `images` array | Content filtered | Rephrase prompt |

## Tips

- Be specific about what changes you want: "make the sky sunset orange" is better than "change the sky"
- Use `aspect_ratio: "auto"` (the default) to preserve original image proportions
- Multiple images can be provided for context, style transfer, or combining elements
- Set `enable_web_search: True` for style-grounded edits ("make it look like a Monet painting")
- Always include `safety_tolerance: "6"` for maximum creative flexibility
- Upload local files with `fal_client.upload_file()` before passing to `image_urls`
