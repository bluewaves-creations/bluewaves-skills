---
name: video-from-reference
description: >
  Generate video with consistent subject appearance using reference images via
  fal.ai Veo 3.1. Use when the user wants to create a video featuring specific
  people, objects, or characters that should look consistent throughout.
  Supports multiple reference images for better subject consistency.
allowed-tools: Bash, Read, Write
license: MIT
compatibility: Requires credentials.json or FAL_KEY environment variable (fal.ai API key), fal-client Python package
---

# Video from Reference

Generate videos with consistent subject appearance using reference images via Google DeepMind's Veo 3.1 model on fal.ai.

## Prerequisites

- **API key**: `credentials.json` with `{"api_key": "..."}` in the scripts/ directory (Claude.ai standalone ZIPs), or `FAL_KEY` environment variable (add to `~/.zshrc`)
- **Python package**: `uv pip install fal-client`

## API Endpoint

`fal-ai/veo3.1/reference-to-video`

## Parameters

### Required
- `prompt` (string): Text description of the video scene and action
- `image_urls` (array of strings): URLs of reference images for consistent subject appearance (use `fal_client.upload_file()` for local files)

### Optional
| Parameter | Type | Default | Options |
|-----------|------|---------|---------|
| `duration` | string | "8s" | "8s" |
| `resolution` | string | "720p" | "720p", "1080p" |
| `generate_audio` | boolean | true | Disable to save ~50% credits |

## Usage

### Python (fal_client)

```python
import fal_client

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            print(f"  [{log.get('level', 'info')}] {log.get('message', '')}")

result = fal_client.subscribe(
    "fal-ai/veo3.1/reference-to-video",
    arguments={
        "prompt": "The character walks through a sunny park, looking around curiously",
        "image_urls": [
            "https://example.com/character-front.jpg",
            "https://example.com/character-side.jpg",
        ],
        "duration": "8s",
        "resolution": "1080p",
        "generate_audio": True,
    },
    with_logs=True,
    on_queue_update=on_queue_update,
)

video_url = result["video"]["url"]
print(f"Generated video: {video_url}")
```

### Using Local Reference Images

```python
import fal_client
from urllib.request import urlopen

# Upload local reference images to fal.ai CDN
ref_front = fal_client.upload_file("/path/to/character-front.jpg")
ref_side = fal_client.upload_file("/path/to/character-side.jpg")

result = fal_client.subscribe(
    "fal-ai/veo3.1/reference-to-video",
    arguments={
        "prompt": "The character runs through a forest, jumping over fallen logs",
        "image_urls": [ref_front, ref_side],
        "resolution": "1080p",
    },
    with_logs=True,
    on_queue_update=lambda u: None,
)

# Download the video to local filesystem
video_url = result["video"]["url"]
with urlopen(video_url) as resp, open("output.mp4", "wb") as f:
    f.write(resp.read())
print("Video saved to output.mp4")
```

### CLI Script

```bash
python scripts/fal_generate.py \
    --endpoint video-from-reference \
    --prompt "The character walks through a sunny park" \
    --images ref-front.jpg ref-side.jpg \
    --video-resolution 1080p \
    --output video.mp4
```

## Response Format

```json
{
  "video": {
    "url": "https://storage.googleapis.com/.../output.mp4"
  }
}
```

## Error Handling

```python
import fal_client

try:
    result = fal_client.subscribe("fal-ai/veo3.1/reference-to-video", arguments={...})
except fal_client.FalClientError as e:
    print(f"API error: {e}")         # Auth failures, invalid params, bad image URLs
except fal_client.FalClientTimeoutError as e:
    print(f"Timeout: {e}")           # Video generation took too long
except Exception as e:
    print(f"Unexpected error: {e}")
```

| Symptom | Cause | Solution |
|---------|-------|----------|
| `FalClientError` (401) | Invalid FAL_KEY | Verify key at fal.ai dashboard |
| `FalClientError` (429) | Rate limit exceeded | Wait 60 seconds, retry |
| `FalClientError` (400) | Invalid image URLs | Ensure all reference URLs are accessible or use `upload_file()` |
| `FalClientTimeoutError` | Video generation too slow | Use 720p or fewer reference images |
| Missing `video` key | Generation failed | Retry; simplify prompt if persistent |

## Tips

- Provide multiple reference images from different angles for better subject consistency
- Use clear, well-lit reference images with the subject prominently visible
- Describe both the scene environment and the subject's actions in the prompt
- More reference images generally lead to better subject consistency (2-4 recommended)
- Works best with distinct, recognizable subjects (people, pets, products)
- Upload local files with `fal_client.upload_file()` before passing to `image_urls`
