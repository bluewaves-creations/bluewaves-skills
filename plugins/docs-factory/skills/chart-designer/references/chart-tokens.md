# Chart Token Schema

Documentation for the `tokens.chart` section of brand kit `manifest.json`.

## Schema

```json
{
  "chart": {
    "palette": {
      "categorical": ["#hex", ...],
      "sequential": ["#hex", ...],
      "diverging": ["#hex", ...],
      "highlight": "#hex",
      "highlight_contrast": "#hex"
    },
    "axis": {
      "color": "#hex",
      "width": 0.8,
      "label_color": "#hex",
      "tick_color": "#hex"
    },
    "grid": {
      "color": "#hex",
      "alpha": 0.3,
      "width": 0.5,
      "style": "--"
    },
    "typography": {
      "title": { "style": "h3", "color_role": "text-heading" },
      "subtitle": { "style": "body", "color_role": "text-muted" },
      "axis_label": { "style": "body-sm", "color_role": "text-body" },
      "tick_label": { "style": "caption", "color_role": "text-body" },
      "annotation": { "style": "caption", "color_role": "text-muted" },
      "legend": { "style": "caption", "color_role": "text-body" }
    },
    "figure": {
      "background": "#hex",
      "plot_background": "#hex"
    }
  }
}
```

## Field Reference

### palette

| Field | Type | Description |
|-------|------|-------------|
| `categorical` | array of 8 hex colors | Discrete series differentiation |
| `sequential` | array of 7 hex colors | Ordered magnitude (light → dark) |
| `diverging` | array of 7 hex colors | Bipolar data (negative ↔ positive) |
| `highlight` | hex color | Call-out emphasis color |
| `highlight_contrast` | hex color | Text on highlight background |

**Categorical** colors are cycled for bar, line, pie series. First color is the brand primary.

**Sequential** colormaps are generated via `LinearSegmentedColormap.from_list()` for heatmaps and choropleth-style fills.

**Diverging** colormaps center on the 4th color (neutral).

### axis

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `color` | hex | #4A4A4A | Axis line color |
| `width` | float | 0.8 | Axis line width in points |
| `label_color` | hex | #212121 | Axis label text color |
| `tick_color` | hex | #7A7A7A | Tick mark and label color |

### grid

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `color` | hex | #B0B0B0 | Grid line color |
| `alpha` | float | 0.3 | Grid line opacity (0–1) |
| `width` | float | 0.5 | Grid line width in points |
| `style` | string | "--" | Line style: "--" dashed, "-" solid, ":" dotted |

### typography

Each typography element references:
- `style` — a key in `tokens.type_scale` (e.g., "h3", "body-sm", "caption")
- `color_role` — a key in `tokens.colors` (e.g., "text-heading", "text-body")

The theme loader resolves these to actual font sizes and hex colors.

### figure

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `background` | hex | #FFFFFF | Figure (outer) background |
| `plot_background` | hex | #FFFFFF | Plot area background |

Wave Artisans uses `#F5F5F7` for figure background to match their page color.

## Brand-Specific Notes

### Decathlon
- Categorical starts with brand blue (#3643BA), accent green (#7AFFA6)
- Highlight is green accent — high contrast against dark text

### Bluewaves
- Categorical starts with brown sand (#B78A66), teal (#00D2E0), sun red (#FF375F)
- Highlight is sun red — strong visual emphasis

### Wave Artisans
- Gray-only palette — no color in charts
- Matches the brand's monochrome identity
- Figure background #F5F5F7 aligns with page background
