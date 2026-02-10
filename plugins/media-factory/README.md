# media-factory Plugin

AI-powered image and video generation using fal.ai with Python fal_client.

## Installation

```bash
# Add the Bluewaves marketplace
/plugin marketplace add bluewaves-creations/bluewaves-skills

# Install this plugin
/plugin install media-factory@bluewaves-skills

# Install dependencies
/media-factory:install-deps
```

## Prerequisites

1. Install the Python client: `uv pip install fal-client`

2. Set your fal.ai API key in `~/.zshrc`:
   ```bash
   export FAL_KEY="your-api-key-here"
   ```

   For Claude.ai (standalone ZIPs): place `credentials.json` with `{"api_key": "..."}` in the skill's `scripts/` directory.

Get your API key from [fal.ai](https://fal.ai).

## Skills Included

### Image Generation

| Skill | Description |
|-------|-------------|
| **image-generator** | Generate images from text prompts |
| **image-editor** | Edit existing images with text instructions |

### Video Generation

| Skill | Description |
|-------|-------------|
| **video-from-image** | Animate a single image into video |
| **video-from-reference** | Generate video with consistent subject appearance |
| **video-from-frames** | Create video from first and last frame images |

### Photographer Style Skills

| Skill | Description |
|-------|-------------|
| **photographer-lindbergh** | Peter Lindbergh style - raw B&W, emotional depth, film grain |
| **photographer-ritts** | Herb Ritts style - sculptural forms, California golden hour |
| **photographer-testino** | Mario Testino style - vibrant glamour, bold saturated colors |
| **photographer-lachapelle** | David LaChapelle style - pop surrealism, fluorescent colors |
| **photographer-vonunwerth** | Ellen von Unwerth style - playful vintage, film noir influence |

## Usage Examples

### Generate an Image
> "Generate a 4K image of a futuristic Tokyo street at night in cyberpunk style"

### Edit an Image
> "Take this photo and add falling cherry blossoms to the scene"

### Create Video from Image
> "Animate this landscape photo with gentle wind movement and flowing water"

### Video with Reference Images
> "Create a video of this character walking through a park using these reference photos"

### Frame-to-Frame Video
> "Generate a video transitioning from this sunrise photo to this sunset photo"

## API Endpoints

| Capability | Endpoint |
|-----------|----------|
| Image Generation | `fal-ai/gemini-3-pro-image-preview` |
| Image Editing | `fal-ai/gemini-3-pro-image-preview/edit` |
| Video from Image | `fal-ai/veo3.1/image-to-video` |
| Video from Reference | `fal-ai/veo3.1/reference-to-video` |
| Video from Frames | `fal-ai/veo3.1/first-last-frame-to-video` |

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "API key not found" | Set `FAL_KEY` in `~/.zshrc` or use `credentials.json` |
| Images not generating | Check API quota at [fal.ai dashboard](https://fal.ai/dashboard) |
| Poor quality results | Use more specific prompts; enable `enable_web_search: True` |
| Wrong aspect ratio | Use exact format like `"16:9"` not `"16/9"` |
| `ModuleNotFoundError` | Run `uv pip install fal-client` |

### Verifying Your Setup

```bash
# Check API key
python3 scripts/fal_utils.py --check-key

# Or use the slash command
/media-factory:check-fal-key
```

## Prompt Engineering Tips

### General Best Practices

1. **Be specific**: "golden retriever puppy playing in autumn leaves" > "dog"
2. **Include lighting**: "soft natural light", "dramatic shadows", "golden hour"
3. **Specify style**: "photorealistic", "oil painting style", "cinematic"
4. **Enable web search**: `enable_web_search: True` lets Gemini look up style references
5. **Composition hints**: "close-up portrait", "wide landscape", "aerial view"

### Photographer Style Prompts

When using photographer style skills, `enable_web_search: True` is critical —
Gemini uses grounding to look up each photographer's actual style:
- **Lindbergh**: Best for emotional portraits, fashion with authenticity
- **Ritts**: Best for athletic subjects, outdoor California settings
- **Testino**: Best for glamour, fashion editorials, celebrity-style
- **LaChapelle**: Best for surreal concepts, elaborate sets, bold statements
- **von Unwerth**: Best for playful fashion, narrative scenes, feminine energy

### Video Generation Tips

- Use descriptive motion language: "pan", "zoom", "sway", "flow"
- Describe camera movements for cinematic effects
- For frame-to-frame: ensure both images have similar composition
- Longer duration (8s) works better for complex transitions

## License

MIT
