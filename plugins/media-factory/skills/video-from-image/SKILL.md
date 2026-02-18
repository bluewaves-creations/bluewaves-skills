---
name: video-from-image
description: >
  Animate a single image into a video using fal.ai Veo 3.1. Use when the user
  wants to create a video from a still image, animate a photo, or bring an
  image to life. Supports up to 8 seconds of video with optional audio.
allowed-tools: Bash, Read, Write
license: MIT
compatibility: Requires credentials.json or FAL_KEY environment variable (fal.ai API key), fal-client Python package
---

# Video from Image

Animate a single image into a dynamic video using Google DeepMind's Veo 3.1 model via fal.ai.

See `references/fal-api.md` for setup, Python patterns, and error handling.

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

## CLI Script

```bash
python3 scripts/fal_generate.py \
    --endpoint video-from-image \
    --prompt "Camera slowly pans across the landscape" \
    --image /path/to/photo.jpg \
    --duration 8s \
    --video-resolution 1080p \
    --output video.mp4
```

## Tips

- Use descriptive motion language in prompts: pan, zoom, sway, flow, drift
- Describe camera movements for cinematic effects: "slow dolly forward", "aerial pull back"
- Higher resolution (1080p) gives better quality but takes longer and costs more
- Disable audio generation (`generate_audio: False`) to save credits when sound is not needed
- Ensure input image is at least 720p for best results
- Shorter duration (4s) generates faster and is good for quick previews
