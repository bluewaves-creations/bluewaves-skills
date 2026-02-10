---
name: video-from-image
description: >
  Animate a single image into a video using fal.ai Veo 3.1. Use when the user
  wants to create a video from a still image, animate a photo, or bring an
  image to life. Supports up to 8 seconds of video with optional audio.
allowed-tools: Bash, Read, Write
license: MIT
compatibility: Requires FAL_KEY environment variable or credentials.json (fal.ai API key), fal-client Python package
---

# Video from Image

Animate a single image into a dynamic video using Google DeepMind's Veo 3.1 model via fal.ai.

## Prerequisites

- **API key**: `FAL_KEY` environment variable (add to `~/.zshrc`) or `credentials.json` with `{"api_key": "..."}` in the scripts/ directory (Claude.ai standalone ZIPs)
- **Python package**: `uv pip install fal-client`
- **Input image**: Should be 720p or higher resolution for best results

## API Endpoint

`fal-ai/veo3.1/image-to-video`

## Parameters

### Required
- `prompt` (string): Text description of the video motion and action to generate
- `image_url` (string): URL of the input image to animate (use `fal_client.upload_file()` for local files)

### Optional
| Parameter | Type | Default | Options |
|-----------|------|---------|---------|
| `duration` | string | "8s" | "4s", "6s", "8s" |
| `aspect_ratio` | string | "auto" | "auto", "9:16", "16:9" |
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
    "fal-ai/veo3.1/image-to-video",
    arguments={
        "prompt": "The camera slowly pans across the scene as leaves gently sway in the breeze",
        "image_url": "https://example.com/landscape.jpg",
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

### Animating a Local Image

```python
import fal_client
from urllib.request import urlopen

# Upload local image to fal.ai CDN
uploaded_url = fal_client.upload_file("/path/to/photo.jpg")

result = fal_client.subscribe(
    "fal-ai/veo3.1/image-to-video",
    arguments={
        "prompt": "Gentle waves roll onto the shore, water sparkles in sunlight",
        "image_url": uploaded_url,
        "duration": "8s",
        "resolution": "720p",
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
python plugins/media-factory/scripts/fal_generate.py \
    --endpoint video-from-image \
    --prompt "Camera slowly pans across the landscape" \
    --image /path/to/photo.jpg \
    --duration 8s \
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
    result = fal_client.subscribe("fal-ai/veo3.1/image-to-video", arguments={...})
except fal_client.FalClientError as e:
    print(f"API error: {e}")         # Auth failures, invalid params, bad image URL
except fal_client.FalClientTimeoutError as e:
    print(f"Timeout: {e}")           # Video generation took too long
except Exception as e:
    print(f"Unexpected error: {e}")
```

| Symptom | Cause | Solution |
|---------|-------|----------|
| `FalClientError` (401) | Invalid FAL_KEY | Verify key at fal.ai dashboard |
| `FalClientError` (429) | Rate limit exceeded | Wait 60 seconds, retry |
| `FalClientError` (400) | Invalid image URL or low resolution | Use 720p+ image, verify URL accessibility |
| `FalClientTimeoutError` | Video generation too slow | Use 720p or shorter duration |
| Missing `video` key | Generation failed | Retry; simplify prompt if persistent |

## Tips

- Use descriptive motion language in prompts: pan, zoom, sway, flow, drift
- Describe camera movements for cinematic effects: "slow dolly forward", "aerial pull back"
- Higher resolution (1080p) gives better quality but takes longer and costs more
- Disable audio generation (`generate_audio: False`) to save credits when sound is not needed
- Ensure input image is at least 720p for best results
- Shorter duration (4s) generates faster and is good for quick previews
