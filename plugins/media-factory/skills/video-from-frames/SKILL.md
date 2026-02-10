---
name: video-from-frames
description: >
  Generate video from first and last frame images using fal.ai Veo 3.1. Use
  when the user wants to create a video transition between two images, morph
  between scenes, or generate smooth video connecting a starting and ending frame.
allowed-tools: Bash, Read, Write
license: MIT
compatibility: Requires FAL_KEY environment variable or credentials.json (fal.ai API key), fal-client Python package
---

# Video from Frames

Generate smooth video transitions between two frames using Google DeepMind's Veo 3.1 model via fal.ai.

## Prerequisites

- **API key**: `FAL_KEY` environment variable (add to `~/.zshrc`) or `credentials.json` with `{"api_key": "..."}` in the scripts/ directory (Claude.ai standalone ZIPs)
- **Python package**: `uv pip install fal-client`

## API Endpoint

`fal-ai/veo3.1/first-last-frame-to-video`

## Parameters

### Required
- `prompt` (string): Text description of how the video should transition between frames
- `first_frame_url` (string): URL of the first/starting frame (use `fal_client.upload_file()` for local files)
- `last_frame_url` (string): URL of the last/ending frame (use `fal_client.upload_file()` for local files)

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
    "fal-ai/veo3.1/first-last-frame-to-video",
    arguments={
        "prompt": "Smooth time-lapse transition from day to night as the sun sets",
        "first_frame_url": "https://example.com/daytime-scene.jpg",
        "last_frame_url": "https://example.com/nighttime-scene.jpg",
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

### Using Local Frame Images

```python
import fal_client
from urllib.request import urlopen

# Upload local frames to fal.ai CDN
first_url = fal_client.upload_file("/path/to/morning-scene.jpg")
last_url = fal_client.upload_file("/path/to/night-scene.jpg")

result = fal_client.subscribe(
    "fal-ai/veo3.1/first-last-frame-to-video",
    arguments={
        "prompt": "Time-lapse of the city from morning to night, lights gradually turning on",
        "first_frame_url": first_url,
        "last_frame_url": last_url,
        "duration": "8s",
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
python plugins/media-factory/scripts/fal_generate.py \
    --endpoint video-from-frames \
    --prompt "Smooth transition from day to night" \
    --first-frame morning.jpg \
    --last-frame night.jpg \
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
    result = fal_client.subscribe("fal-ai/veo3.1/first-last-frame-to-video", arguments={...})
except fal_client.FalClientError as e:
    print(f"API error: {e}")         # Auth failures, invalid params, bad frame URLs
except fal_client.FalClientTimeoutError as e:
    print(f"Timeout: {e}")           # Video generation took too long
except Exception as e:
    print(f"Unexpected error: {e}")
```

| Symptom | Cause | Solution |
|---------|-------|----------|
| `FalClientError` (401) | Invalid FAL_KEY | Verify key at fal.ai dashboard |
| `FalClientError` (429) | Rate limit exceeded | Wait 60 seconds, retry |
| `FalClientError` (400) | Invalid frame URLs or mismatch | Use similar composition frames, verify URL accessibility |
| `FalClientTimeoutError` | Video generation too slow | Use 720p or shorter duration (4s) |
| Missing `video` key | Generation failed | Retry; simplify prompt if persistent |

## Tips

- Ensure both frames have similar composition and framing for smooth transitions
- Describe the transition motion and action clearly in the prompt
- Works best when both frames share the same subject or scene from the same viewpoint
- Use longer duration (8s) for complex transitions with many intermediate states
- The AI interpolates plausible motion between the two frames
- Upload local files with `fal_client.upload_file()` before passing as frame URLs
- Shorter duration (4s) generates faster and works well for simple transitions
