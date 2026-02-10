---
name: photographer-testino
description: Generate images in Mario Testino's glamorous vibrant style. Use when users ask for Testino style, high fashion glamour, bold saturated colors, warm luxurious photography, dynamic sensual energy.
allowed-tools: Bash, Read, Write
license: MIT
compatibility: Requires FAL_KEY environment variable (fal.ai API key). Claude.ai users can provide credentials via credentials.json.
---

# Mario Testino Style Photography

Generate images in the iconic style of Mario Testino - vibrant, glamorous photography with bold colors and luxurious sensuality.

## Style Characteristics

Mario Testino's photography is defined by:
- **Vibrant glamour** - luxurious, high-energy sensuality
- **Bold saturated colors** - rich, contrasting hues that pop
- **Natural warmth** - sun-kissed, luminous skin tones
- **Spontaneous elegance** - authentic connection with genuine emotion
- **Dynamic movement** - sense of liveliness and joyful energy

## Prerequisites

Set your fal.ai API key:
```bash
export FAL_KEY="your-fal-api-key"
```

For Claude.ai users, provide your key via `credentials.json`:
```json
{ "api_key": "your-fal-api-key" }
```

Install the fal client:
```bash
pip install fal-client
```

## API Endpoint

```
fal-ai/gemini-3-pro-image-preview
```

## Prompt Construction

### Core Style Elements

Always include these elements for authentic Testino style:

```
in the style of Mario Testino, natural light photography,
glamorous fashion, bold saturated colors, warm skin tones,
dynamic composition, sensual energy, spontaneous pose,
luxurious atmosphere, vibrant and luminous
```

### Mood Keywords

| Category | Keywords |
|----------|----------|
| Energy | `dynamic`, `spontaneous`, `energetic`, `joyful`, `alive` |
| Glamour | `luxurious`, `glamorous`, `sensual`, `alluring`, `radiant` |
| Color | `bold colors`, `saturated`, `vibrant`, `rich hues`, `warm tones` |
| Light | `natural light`, `sun-kissed`, `luminous`, `warm`, `golden` |

## Usage

### Fashion Portrait Example

```python
import fal_client

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            print(log["message"])

result = fal_client.subscribe(
    "fal-ai/gemini-3-pro-image-preview",
    arguments={
        "prompt": "supermodel in flowing red dress, laughing in motion, in the style of Mario Testino, natural light photography, glamorous fashion, bold saturated colors, warm sun-kissed skin, dynamic composition, spontaneous joyful energy, luxurious Peruvian setting, vibrant and radiant",
        "aspect_ratio": "2:3",
        "output_format": "png",
        "safety_tolerance": "6",
        "enable_web_search": True,
    },
    with_logs=True,
    on_queue_update=on_queue_update,
)
print(result["images"][0]["url"])
```

### Celebrity Portrait Example

```python
import fal_client

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            print(log["message"])

result = fal_client.subscribe(
    "fal-ai/gemini-3-pro-image-preview",
    arguments={
        "prompt": "celebrity portrait with confident smile, in the style of Mario Testino, natural light photography, glamorous high fashion, bold saturated colors, luminous warm skin tones, dynamic energy, sensual elegance, spontaneous charm, luxurious atmosphere, vibrant color palette",
        "aspect_ratio": "3:4",
        "output_format": "png",
        "safety_tolerance": "6",
        "enable_web_search": True,
    },
    with_logs=True,
    on_queue_update=on_queue_update,
)
print(result["images"][0]["url"])
```

## Response Format

```json
{
  "images": [
    {
      "url": "https://fal.media/files/...",
      "content_type": "image/png"
    }
  ]
}
```

## Examples

### 1. Classic Testino Portrait
```
beautiful woman with confident gaze, slight smile,
in the style of Mario Testino, natural light photography,
glamorous high fashion, bold saturated colors,
warm luminous skin, sensual elegance,
dynamic energy, luxurious setting,
vibrant color palette, radiant beauty
```

### 2. Fashion Editorial
```
model in designer gown, dynamic movement,
in the style of Mario Testino, golden hour light,
glamorous fashion photography, rich saturated colors,
flowing fabric in motion, warm skin tones,
spontaneous elegance, luxurious atmosphere,
joyful sensual energy, vibrant backdrop
```

### 3. Royal or Celebrity Style
```
elegant woman in formal attire, confident pose,
in the style of Mario Testino, soft natural light,
royal portrait aesthetic, rich color palette,
warm glowing skin, dignified yet approachable,
glamorous sophistication, luxurious setting,
vibrant jewel tones, radiant presence
```

### 4. Beach or Vacation
```
model in bikini on tropical beach, carefree moment,
in the style of Mario Testino, bright natural sunlight,
glamorous lifestyle photography, bold saturated blues and golds,
sun-kissed bronzed skin, spontaneous joyful pose,
luxurious vacation aesthetic, sensual energy,
vibrant summer colors, dynamic composition
```

### 5. Intimate Sensuality
```
close-up beauty portrait, intense gaze,
in the style of Mario Testino, soft warm light,
glamorous sensual beauty, rich skin tones,
bold lip color, luminous complexion,
intimate yet powerful, luxurious feeling,
vibrant contrast, alluring presence
```

## Tips for Best Results

1. **Embrace color** - Testino is known for COLOR; use "bold saturated", "vibrant", "rich hues"
2. **Warm lighting** - Specify "natural light", "golden hour", "sun-kissed", "warm tones"
3. **Add energy** - Include "dynamic", "spontaneous", "joyful", "movement"
4. **Glamour focus** - Use "luxurious", "glamorous", "sensual", "elegant"
5. **Skin quality** - Add "luminous skin", "glowing complexion", "radiant"
6. **Fashion context** - Reference high fashion, designer, editorial styling
7. **Web search grounding** - `enable_web_search: True` lets Gemini look up Testino's actual style for authentic results

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `fal_client.AuthenticationError` | Invalid FAL_KEY | Verify key at fal.ai dashboard |
| `fal_client.RateLimitError` | Rate limit exceeded | Wait 60 seconds, retry |
| `fal_client.ValidationError` | Invalid parameters | Check aspect_ratio format (e.g., "2:3") |
| `fal_client.ServerError` | API temporary issue | Retry after 30 seconds |
| `fal_client.TimeoutError` | Generation taking too long | Simplify prompt or reduce resolution |

## Reference

Mario Testino (born 1954) is a Peruvian fashion photographer known for his work with British Vogue, Vanity Fair, and major fashion houses. He famously photographed Princess Diana and has captured countless celebrities and supermodels.

**Key Influences**: Peruvian heritage, high fashion culture
**Signature**: Vibrant colors, glamorous warmth, spontaneous luxury
