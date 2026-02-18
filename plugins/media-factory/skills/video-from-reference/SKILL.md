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

See `references/fal-api.md` for setup, Python patterns, and error handling.

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

## CLI Script

```bash
python3 scripts/fal_generate.py \
    --endpoint video-from-reference \
    --prompt "The character walks through a sunny park" \
    --images ref-front.jpg ref-side.jpg \
    --video-resolution 1080p \
    --output video.mp4
```

## Tips

- Provide multiple reference images from different angles for better subject consistency
- Use clear, well-lit reference images with the subject prominently visible
- Describe both the scene environment and the subject's actions in the prompt
- More reference images generally lead to better subject consistency (2-4 recommended)
- Works best with distinct, recognizable subjects (people, pets, products)
- Upload local files with `fal_client.upload_file()` before passing to `image_urls`
