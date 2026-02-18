# fal.ai API Reference

Shared reference for all fal.ai media generation skills. Read when setting up credentials, writing Python generation code, or debugging API errors.

## Prerequisites

**API key** — provide via one of:

- `credentials.json` with `{"api_key": "..."}` in the skill's `scripts/` directory (Claude.ai standalone ZIPs)
- `FAL_KEY` environment variable: `export FAL_KEY="your-fal-api-key"` (add to `~/.zshrc`)

For Claude.ai users, copy `scripts/credentials.example.json` to `scripts/credentials.json` and add your key.

**Python package:**

```bash
uv pip install fal-client
```

If `uv` is not available, fall back to: `pip install fal-client`

## Python Patterns

### Queue-based generation (standard)

```python
import fal_client

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            print(f"  [{log.get('level', 'info')}] {log.get('message', '')}")

result = fal_client.subscribe(
    "fal-ai/ENDPOINT",
    arguments={...},
    with_logs=True,
    on_queue_update=on_queue_update,
)
```

### Sync mode (images only, recommended for reliability)

Returns a base64 data URI directly, avoiding a separate download step:

```python
result = fal_client.subscribe(
    "fal-ai/gemini-3-pro-image-preview",
    arguments={
        "prompt": "...",
        "sync_mode": True,
        "safety_tolerance": "6",
        "enable_web_search": True,
    },
)

data_uri = result["images"][0]["url"]  # data:image/png;base64,...
header, b64data = data_uri.split(",", 1)
import base64
with open("output.png", "wb") as f:
    f.write(base64.b64decode(b64data))
```

### Uploading local files

```python
uploaded_url = fal_client.upload_file("/path/to/local/image.jpg")
```

Use the returned URL in `image_url`, `image_urls`, `first_frame_url`, or `last_frame_url` parameters.

## Response Formats

### Image response

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

### Video response

```json
{
  "video": {
    "url": "https://storage.googleapis.com/.../output.mp4"
  }
}
```

## CLI Reference

All skills share the `fal_generate.py` CLI script:

```bash
# Image generation
python3 scripts/fal_generate.py \
    --endpoint image \
    --prompt "description" \
    --aspect-ratio 16:9 --resolution 2K --output image.png

# Image editing
python3 scripts/fal_generate.py \
    --endpoint edit \
    --prompt "edit instruction" \
    --image /path/to/image.jpg --output edited.png

# Video from image
python3 scripts/fal_generate.py \
    --endpoint video-from-image \
    --prompt "motion description" \
    --image /path/to/photo.jpg --duration 8s --video-resolution 1080p --output video.mp4

# Video from reference images
python3 scripts/fal_generate.py \
    --endpoint video-from-reference \
    --prompt "scene description" \
    --images ref1.jpg ref2.jpg --video-resolution 1080p --output video.mp4

# Video from first/last frames
python3 scripts/fal_generate.py \
    --endpoint video-from-frames \
    --prompt "transition description" \
    --first-frame start.jpg --last-frame end.jpg --duration 8s --video-resolution 1080p --output video.mp4
```

## Error Handling

```python
try:
    result = fal_client.subscribe("fal-ai/ENDPOINT", arguments={...})
except fal_client.FalClientError as e:
    print(f"API error: {e}")
except fal_client.FalClientTimeoutError as e:
    print(f"Timeout: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

| Symptom | Cause | Solution |
|---------|-------|----------|
| `FalClientError` (401) | Invalid FAL_KEY | Verify key at fal.ai dashboard |
| `FalClientError` (429) | Rate limit exceeded | Wait 60 seconds, retry |
| `FalClientError` (400) | Invalid parameters or image URLs | Check parameter values; ensure URLs are accessible or use `upload_file()` |
| `FalClientTimeoutError` | Generation too slow | Reduce resolution, simplify prompt, or use shorter duration |
| Empty `images` array | Content filtered | Rephrase prompt |
| Missing `video` key | Video generation failed | Retry; simplify prompt if persistent |
