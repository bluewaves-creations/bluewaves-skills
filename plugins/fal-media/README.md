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

## License

MIT
