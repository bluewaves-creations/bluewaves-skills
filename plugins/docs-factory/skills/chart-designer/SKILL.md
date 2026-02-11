---
name: chart-designer
description: >
  Brand-consistent chart design system for matplotlib. Provides load_theme(),
  theme.apply(), and named figure sizes — brand guardrails that get out of
  the way. Use when the user asks to create charts, graphs, plots, data
  visualizations, or any visual representation of data. Standard matplotlib
  code works as-is; the theme handles colors, typography, and sizing. Pairs
  with brand-* kits for branded output and pdf-factory for PDF embedding.
allowed-tools: Bash, Read, Write
license: MIT
compatibility: Python 3.8+ with matplotlib, numpy
---
# Chart Designer

A design-system for matplotlib charts. You get brand colors, typography, and
named figure sizes — then write standard matplotlib code for everything else.

## Dependencies

```bash
uv pip install matplotlib numpy cycler
```

## Quick Start

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

## How It Works

### 1. `load_theme()` — Load brand tokens

```python
from chart_theme import load_theme

theme = load_theme(brand_path="path/to/brand-decathlon")
# Reads manifest.json → tokens.chart → palette, typography, axis, grid
# Without a brand kit, returns sensible defaults.
```

### 2. `theme.apply()` — Activate brand rcParams

```python
with theme.apply():
    fig, ax = plt.subplots(...)
    # Inside this block, matplotlib uses brand fonts, colors, grid style.
    # All standard matplotlib code works — bar, plot, scatter, imshow, etc.
    fig.savefig("output.png")
# Outside the block, rcParams are restored to previous values.
```

### 3. `theme.sizes` — Named figure dimensions

```python
fig, ax = plt.subplots(figsize=theme.sizes["full-width"])
```

Pre-defined sizes optimized for A4 PDF integration. See the table below.

## API Reference

### `load_theme(brand_path=None, dpi=200) → ChartTheme`

Loads a brand kit's `manifest.json` and returns a configured theme.
Pass `None` for sensible defaults without a brand kit.

### `ChartTheme`

| Attribute | Type | Description |
|-----------|------|-------------|
| `palette` | `BrandPalette` | Color palettes (categorical, sequential, diverging) |
| `rcparams` | `dict` | matplotlib rcParams dict (applied by `theme.apply()`) |
| `sizes` | `dict` | Named figure size tuples — see table below |
| `dpi` | `int` | Output resolution (default 200) |
| `brand_name` | `str` | Brand name from manifest |

### `BrandPalette`

| Attribute / Method | Description |
|--------------------|-------------|
| `categorical` | `list[str]` — 8 hex colors for discrete series |
| `sequential` | `list[str]` — 7 hex colors light→dark |
| `diverging` | `list[str]` — 7 hex colors neg↔pos |
| `highlight` | `str` — call-out emphasis color |
| `highlight_contrast` | `str` — text on highlight background |
| `categorical_colormap()` | `ListedColormap` from categorical palette |
| `sequential_colormap()` | `LinearSegmentedColormap` from sequential palette |
| `diverging_colormap()` | `LinearSegmentedColormap` from diverging palette |

## Figure Sizes

Named sizes optimized for A4 PDF integration (25mm margins):

| Name | Width × Height | Use case |
|------|---------------|----------|
| `full-width` | 6.29" × 3.93" | Default, spans content area |
| `full-width-tall` | 6.29" × 5.24" | Complex charts needing height |
| `half-width` | 3.0" × 2.5" | Side-by-side pairs |
| `two-thirds` | 4.19" × 3.0" | Medium placement |
| `square` | 4.0" × 4.0" | Pie, donut, heatmap |
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

## QA Checklist

After generating any chart, open the output image and verify:

1. **Labels readable** — No overlapping text on any element: axis labels, tick labels, legends, annotations, pie/donut category names, percentage values. If labels overlap, adjust the chart type, font size, rotation, or layout
2. **Data accurate** — Values in the chart match the source data; spot-check at least two data points
3. **Legend clear** — Multi-series charts have a legend with all series labeled
4. **No clipping** — Title, subtitle, axis labels, and legend are fully visible, not cut off at edges
5. **Contextual fit** — Chart type suits the data story (don't use pie for > 6 categories; use horizontal bar for long labels)
6. **Brand consistent** — When using a brand kit, chart uses brand palette and typography

## References

- [Chart type cookbook](references/chart-types.md) — Complete matplotlib examples for every chart type
- [Chart token schema](references/chart-tokens.md) — Full `tokens.chart` manifest.json specification
