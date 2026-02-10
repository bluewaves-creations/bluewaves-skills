---
name: chart-designer
description: >
  Brand-consistent chart and data visualization generation using matplotlib.
  Use when the user asks to create charts, graphs, plots, data visualizations,
  or any visual representation of data. Supports 10 chart types with automatic
  brand kit integration for colors, typography, and sizing. Pairs with brand-*
  kits for branded output and pdf-factory for PDF embedding.
allowed-tools: Bash, Read, Write
license: MIT
compatibility: Python 3.8+ with matplotlib, numpy
---
# Chart Designer

Generate brand-consistent charts and data visualizations using matplotlib.

## Dependencies

```bash
uv pip install matplotlib numpy cycler
```

## Quick Start

### Python API (recommended)

```python
import sys; sys.path.insert(0, "scripts")
from chart_theme import load_theme
import matplotlib.pyplot as plt

theme = load_theme(brand_path="path/to/brand-decathlon")

with theme.apply():
    fig, ax = plt.subplots(figsize=theme.sizes["full-width"])
    ax.bar(["Q1", "Q2", "Q3", "Q4"], [120, 150, 180, 210],
           color=theme.palette.categorical[:4])
    ax.set_title("Revenue by Quarter")
    fig.savefig("chart.png")
    plt.close()
```

### JSON CLI (alternative)

```bash
python3 scripts/render_chart.py \
  --spec chart-spec.json \
  --brand path/to/brand-decathlon \
  --output chart.png
```

JSON spec format:

```json
{
  "type": "bar",
  "title": "Revenue by Quarter",
  "subtitle": "FY 2026",
  "size": "full-width",
  "x_label": "Quarter",
  "y_label": "Revenue ($M)",
  "data": {
    "categories": ["Q1", "Q2", "Q3", "Q4"],
    "series": [
      {"name": "Revenue", "values": [120, 150, 180, 210]}
    ]
  }
}
```

## Brand Integration

The theme loader reads `tokens.chart` from a brand kit's `manifest.json`:

1. **Colors** — categorical, sequential, diverging palettes from `tokens.chart.palette`
2. **Typography** — font sizes and colors resolved from `tokens.type_scale` + `tokens.colors`
3. **Axis/Grid** — styling from `tokens.chart.axis` and `tokens.chart.grid`
4. **Fonts** — TTF files registered with matplotlib from `assets/fonts/`

Without a brand kit, sensible defaults are used.

## Chart Types

| Type | JSON `type` | Best for |
|------|-------------|----------|
| Bar | `bar` | Comparing categories |
| Grouped bar | `grouped_bar` | Multi-series category comparison |
| Stacked bar | `stacked_bar` | Part-to-whole by category |
| Horizontal bar | `horizontal_bar` | Long category labels |
| Line | `line` | Trends over time |
| Area | `area` | Volume trends over time |
| Pie | `pie` | Simple part-to-whole (≤6 slices) |
| Donut | `donut` | Part-to-whole with center stat |
| Scatter | `scatter` | Correlation between variables |
| Heatmap | `heatmap` | Matrix/grid intensity |

For complete code templates, see [references/chart-types.md](references/chart-types.md).

## Figure Sizes

Named sizes optimized for A4 PDF integration (25mm margins):

| Name | Width × Height | Use case |
|------|---------------|----------|
| `full-width` | 6.29" × 3.93" | Default, spans content area |
| `full-width-tall` | 6.29" × 5.24" | Complex charts needing height |
| `half-width` | 3.0" × 2.5" | Side-by-side pairs |
| `two-thirds` | 4.19" × 3.0" | Medium placement |
| `square` | 4.0" × 4.0" | Pie, donut |
| `spark` | 3.0" × 1.0" | Inline sparkline |

## PDF Factory Integration

1. Generate chart PNG using this skill
2. Reference the PNG in your markdown: `![Chart title](chart.png)`
3. Render the document with pdf-factory — the image is embedded automatically
4. SVG output is also supported and will be auto-converted to PNG by pdf-factory

Use `<figure>` and `<figcaption>` for captioned charts:

```html
<figure>
  <img src="chart.png" alt="Revenue by Quarter">
  <figcaption>Figure 1: Quarterly revenue growth (FY 2026)</figcaption>
</figure>
```

## Token Reference

For the full `tokens.chart` schema, see [references/chart-tokens.md](references/chart-tokens.md).
