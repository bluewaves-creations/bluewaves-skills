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

## Prerequisites

- **API key**: `credentials.json` with `{"api_key": "..."}` in the scripts/ directory (Claude.ai standalone ZIPs), or `FAL_KEY` environment variable (add to `~/.zshrc`)
- **Python package**: `uv pip install fal-client`

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

## Usage

### Python (fal_client)

```python
import fal_client

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            print(f"  [{log.get('level', 'info')}] {log.get('message', '')}")

result = fal_client.subscribe(
    "fal-ai/gemini-3-pro-image-preview",
    arguments={
        "prompt": "A serene mountain landscape at sunset with golden light",
        "num_images": 1,
        "aspect_ratio": "16:9",
        "resolution": "2K",
        "output_format": "png",
        "safety_tolerance": "6",
        "enable_web_search": True,
    },
    with_logs=True,
    on_queue_update=on_queue_update,
)

image_url = result["images"][0]["url"]
print(f"Generated image: {image_url}")
```

### Sync Mode (recommended for reliability)

Sync mode returns a base64 data URI directly, avoiding a separate download step.

```python
import fal_client
import base64

result = fal_client.subscribe(
    "fal-ai/gemini-3-pro-image-preview",
    arguments={
        "prompt": "A futuristic city skyline at night",
        "sync_mode": True,
        "safety_tolerance": "6",
        "enable_web_search": True,
    },
)

data_uri = result["images"][0]["url"]  # data:image/png;base64,...
header, b64data = data_uri.split(",", 1)
with open("output.png", "wb") as f:
    f.write(base64.b64decode(b64data))
```

### Uploading Local Images (for use as references)

```python
import fal_client

uploaded_url = fal_client.upload_file("/path/to/local/image.jpg")
print(f"Uploaded: {uploaded_url}")
```

### CLI Script

```bash
python scripts/fal_generate.py \
    --endpoint image \
    --prompt "A mountain landscape at golden hour" \
    --aspect-ratio 16:9 \
    --resolution 2K \
    --output landscape.png
```

## Response Format

```json
{
  "images": [
    {
      "file_name": "generated_image.png",
      "content_type": "image/png",
      "url": "https://storage.googleapis.com/..."
    }
  ],
  "description": "A description of the generated image"
}
```

When `sync_mode` is true, the `url` field contains a `data:image/...;base64,...` URI instead of an HTTP URL.

## Error Handling

```python
import fal_client

try:
    result = fal_client.subscribe("fal-ai/gemini-3-pro-image-preview", arguments={...})
except fal_client.FalClientError as e:
    print(f"API error: {e}")         # Auth failures, invalid params
except fal_client.FalClientTimeoutError as e:
    print(f"Timeout: {e}")           # Generation took too long
except Exception as e:
    print(f"Unexpected error: {e}")
```

| Symptom | Cause | Solution |
|---------|-------|----------|
| `FalClientError` (401) | Invalid FAL_KEY | Verify key at fal.ai dashboard |
| `FalClientError` (429) | Rate limit exceeded | Wait 60 seconds, retry |
| `FalClientError` (400) | Invalid parameters | Check aspect_ratio, resolution values |
| `FalClientTimeoutError` | Generation too slow | Reduce resolution or simplify prompt |
| Empty `images` array | Content filtered | Rephrase prompt |

## Tips

- Set `enable_web_search: True` to ground generation in real-world styles, brands, and visual references
- Always include `safety_tolerance: "6"` for maximum creative flexibility
- Use `sync_mode: True` for the most reliable workflow (no separate download)
- Be specific in prompts: include lighting, mood, composition, and style descriptors
- Match aspect ratio to use case: 16:9 for landscapes, 9:16 for portraits, 1:1 for social media
- Higher resolution (4K) produces more detail but takes longer to generate
- Use `seed` to reproduce a specific result
