---
name: photographer-testino
description: Generate images in Mario Testino's glamorous vibrant style. Use when users ask for Testino style, high fashion glamour, bold saturated colors, warm luxurious photography, dynamic sensual energy.
allowed-tools: Bash, Read, Write
license: MIT
compatibility: Requires credentials.json or FAL_KEY environment variable (fal.ai API key). Claude.ai users provide credentials via credentials.json.
---

# Mario Testino Style Photography

Generate images in the iconic style of Mario Testino - vibrant, glamorous photography with bold colors and luxurious sensuality.

See `references/fal-api.md` for setup, Python patterns, and error handling.

## Style Characteristics

Mario Testino's photography is defined by:
- **Vibrant glamour** - luxurious, high-energy sensuality
- **Bold saturated colors** - rich, contrasting hues that pop
- **Natural warmth** - sun-kissed, luminous skin tones
- **Spontaneous elegance** - authentic connection with genuine emotion
- **Dynamic movement** - sense of liveliness and joyful energy

## API Endpoint

`fal-ai/gemini-3-pro-image-preview`

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

## CLI Script

```bash
python3 scripts/fal_generate.py \
    --endpoint image \
    --prompt "supermodel in flowing red dress, laughing in motion, in the style of Mario Testino, natural light, glamorous fashion, bold saturated colors, warm skin, dynamic composition, spontaneous joyful energy" \
    --aspect-ratio 2:3 \
    --output testino-portrait.png
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

## Reference

Mario Testino (born 1954) is a Peruvian fashion photographer known for his work with British Vogue, Vanity Fair, and major fashion houses. He famously photographed Princess Diana and has captured countless celebrities and supermodels.

**Key Influences**: Peruvian heritage, high fashion culture
**Signature**: Vibrant colors, glamorous warmth, spontaneous luxury
