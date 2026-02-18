---
name: video-from-frames
description: >
  Generate video from first and last frame images using fal.ai Veo 3.1. Use
  when the user wants to create a video transition between two images, morph
  between scenes, or generate smooth video connecting a starting and ending frame.
allowed-tools: Bash, Read, Write
license: MIT
compatibility: Requires credentials.json or FAL_KEY environment variable (fal.ai API key), fal-client Python package
---

# Video from Frames

Generate smooth video transitions between two frames using Google DeepMind's Veo 3.1 model via fal.ai.

See `references/fal-api.md` for setup, Python patterns, and error handling.

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

## CLI Script

```bash
python3 scripts/fal_generate.py \
    --endpoint video-from-frames \
    --prompt "Smooth transition from day to night" \
    --first-frame morning.jpg \
    --last-frame night.jpg \
    --duration 8s \
    --video-resolution 1080p \
    --output video.mp4
```

## Tips

- Ensure both frames have similar composition and framing for smooth transitions
- Describe the transition motion and action clearly in the prompt
- Works best when both frames share the same subject or scene from the same viewpoint
- Use longer duration (8s) for complex transitions with many intermediate states
- The AI interpolates plausible motion between the two frames
- Upload local files with `fal_client.upload_file()` before passing as frame URLs
- Shorter duration (4s) generates faster and works well for simple transitions
