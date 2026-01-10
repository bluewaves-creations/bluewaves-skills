# fal-media Plugin

AI-powered media generation using fal.ai's Gemini and Veo models.

## Installation

```bash
# Add the Bluewaves marketplace
/plugin marketplace add bluewaves-creations/bluewaves-skills

# Install this plugin
/plugin install fal-media@bluewaves-skills
```

## Prerequisites

Set your fal.ai API key in your shell configuration (`~/.zshrc`):

```bash
export FAL_KEY="your-api-key-here"
```

Get your API key from [fal.ai](https://fal.ai).

## Skills Included

### Image Generation

| Skill | Description |
|-------|-------------|
| **gemini-image** | Generate images from text prompts using Gemini 3 Pro |
| **gemini-image-edit** | Edit existing images with text instructions |

### Photographer Style Skills

| Skill | Description |
|-------|-------------|
| **photographer-lindbergh** | Peter Lindbergh style - raw B&W, emotional depth, film grain |
| **photographer-ritts** | Herb Ritts style - sculptural forms, California golden hour |
| **photographer-testino** | Mario Testino style - vibrant glamour, bold saturated colors |
| **photographer-lachapelle** | David LaChapelle style - pop surrealism, fluorescent colors |
| **photographer-vonunwerth** | Ellen von Unwerth style - playful vintage, film noir influence |

### Video Generation

| Skill | Description |
|-------|-------------|
| **veo-image-to-video** | Animate a single image into video |
| **veo-reference-video** | Generate video with consistent subject appearance |
| **veo-frames-to-video** | Create video from first and last frame images |

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

| Model | Endpoint |
|-------|----------|
| Gemini Image | `fal-ai/gemini-3-pro-image-preview` |
| Gemini Edit | `fal-ai/gemini-3-pro-image-preview/edit` |
| Veo Image-to-Video | `fal-ai/veo3.1/image-to-video` |
| Veo Reference-to-Video | `fal-ai/veo3.1/reference-to-video` |
| Veo Frames-to-Video | `fal-ai/veo3.1/first-last-frame-to-video` |

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "FAL_KEY not set" | Add `export FAL_KEY="your-key"` to `~/.zshrc` and run `source ~/.zshrc` |
| Images not generating | Check API quota at [fal.ai dashboard](https://fal.ai/dashboard) |
| Poor quality results | Use more specific prompts with style and lighting details |
| Wrong aspect ratio | Use exact format like `"16:9"` not `"16/9"` |
| 401 Unauthorized | Verify your FAL_KEY is correct at fal.ai dashboard |
| 429 Too Many Requests | Rate limit exceeded - wait 60 seconds and retry |
| Timeout errors | Reduce resolution or simplify the prompt |

### Verifying Your Setup

```bash
# Check if FAL_KEY is set
echo $FAL_KEY

# Test API connectivity
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Key $FAL_KEY" \
  https://fal.run/fal-ai/gemini-3-pro-image-preview
# Should return 200 or 400 (not 401)
```

## Prompt Engineering Tips

### General Best Practices

1. **Be specific**: "golden retriever puppy playing in autumn leaves" > "dog"
2. **Include lighting**: "soft natural light", "dramatic shadows", "golden hour"
3. **Specify style**: "photorealistic", "oil painting style", "cinematic"
4. **Add atmosphere**: "moody", "vibrant", "ethereal", "nostalgic"
5. **Composition hints**: "close-up portrait", "wide landscape", "aerial view"

### Photographer Style Prompts

When using photographer style skills, combine with your subject:
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
