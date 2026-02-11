#!/usr/bin/env python3
"""CLI chart renderer from JSON spec.

Renders brand-consistent charts from a JSON specification using matplotlib
and the chart_theme module.

Usage:
    python render_chart.py --spec chart.json --brand path/to/brand-kit --output chart.png

JSON spec format:
    {
        "type": "bar",
        "title": "Revenue by Quarter",
        "subtitle": "FY 2026",
        "size": "full-width",
        "data": {
            "categories": ["Q1", "Q2", "Q3", "Q4"],
            "series": [
                {"name": "Revenue", "values": [120, 150, 180, 210]}
            ]
        }
    }

Supported chart types:
    bar, grouped_bar, stacked_bar, horizontal_bar,
    line, area, pie, donut, scatter, heatmap
"""
import argparse
import json
import sys
from pathlib import Path

# Import theme loader from same directory
sys.path.insert(0, str(Path(__file__).parent))
from chart_theme import load_theme


def render_bar(ax, data, theme, stacked=False):
    """Render a vertical bar chart."""
    import numpy as np
    categories = data.get("categories", [])
    series_list = data.get("series", [])
    x = np.arange(len(categories))
    width = 0.7 / max(len(series_list), 1) if not stacked else 0.7
    bottom = np.zeros(len(categories)) if stacked else None

    for i, series in enumerate(series_list):
        values = series.get("values", [])
        label = series.get("name", f"Series {i+1}")
        if stacked:
            ax.bar(x, values, width, bottom=bottom, label=label)
            bottom = bottom + np.array(values)
        else:
            offset = (i - len(series_list) / 2 + 0.5) * width
            ax.bar(x + offset, values, width, label=label)

    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    if len(series_list) > 1:
        ncol = min(len(series_list), 4)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=ncol, frameon=False)


def render_horizontal_bar(ax, data, theme):
    """Render a horizontal bar chart."""
    import numpy as np
    categories = data.get("categories", [])
    series_list = data.get("series", [])
    y = np.arange(len(categories))
    height = 0.7 / max(len(series_list), 1)

    for i, series in enumerate(series_list):
        values = series.get("values", [])
        label = series.get("name", f"Series {i+1}")
        offset = (i - len(series_list) / 2 + 0.5) * height
        ax.barh(y + offset, values, height, label=label)

    ax.set_yticks(y)
    ax.set_yticklabels(categories)
    if len(series_list) > 1:
        ncol = min(len(series_list), 4)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=ncol, frameon=False)


def render_line(ax, data, theme, fill=False):
    """Render a line chart (or area chart if fill=True)."""
    categories = data.get("categories", [])
    series_list = data.get("series", [])

    for series in series_list:
        values = series.get("values", [])
        label = series.get("name", "")
        line, = ax.plot(categories, values, marker="o", markersize=4, label=label)
        if fill:
            ax.fill_between(categories, values, alpha=0.3, color=line.get_color())

    if len(series_list) > 1:
        ncol = min(len(series_list), 4)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=ncol, frameon=False)


def render_pie(ax, data, theme, donut=False):
    """Render a pie or donut chart."""
    categories = data.get("categories", [])
    values = data.get("series", [{}])[0].get("values", [])
    colors = theme.palette.categorical[:len(values)]
    wedge_props = {"edgecolor": "white", "linewidth": 1.5}

    total = sum(values) if values else 1
    pcts = [(v / total) * 100 for v in values]
    has_small_slice = any(p < 5 for p in pcts)

    if has_small_slice:
        def smart_autopct(pct):
            return f"{pct:.0f}%" if pct >= 5 else ""

        pct_distance = 0.78 if donut else 0.7
        wedges, _, autotexts = ax.pie(
            values, labels=None, autopct=smart_autopct,
            pctdistance=pct_distance,
            colors=colors, wedgeprops=wedge_props, startangle=90,
        )
        for text in autotexts:
            text.set_fontsize(7)

        legend_labels = []
        for cat, pct in zip(categories, pcts):
            if pct < 1:
                legend_labels.append(f"{cat} (<1%)")
            else:
                legend_labels.append(f"{cat} ({pct:.0f}%)")

        ncol = min(len(categories), 3)
        ax.legend(wedges, legend_labels, loc="upper center",
                  bbox_to_anchor=(0.5, -0.12), ncol=ncol, frameon=False)
    else:
        wedges, texts, autotexts = ax.pie(
            values, labels=categories, autopct="%1.0f%%",
            colors=colors, wedgeprops=wedge_props, startangle=90,
        )
        for text in autotexts:
            text.set_fontsize(7)

    if donut:
        centre_circle = __import__("matplotlib.patches", fromlist=["Circle"]).Circle(
            (0, 0), 0.55, fc="white"
        )
        ax.add_artist(centre_circle)

    ax.set_aspect("equal")


def render_scatter(ax, data, theme):
    """Render a scatter chart."""
    series_list = data.get("series", [])

    for series in series_list:
        x = series.get("x", [])
        y = series.get("y", [])
        label = series.get("name", "")
        ax.scatter(x, y, alpha=0.7, label=label, s=40)

    if len(series_list) > 1:
        ncol = min(len(series_list), 4)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=ncol, frameon=False)


def render_heatmap(ax, data, theme):
    """Render a heatmap."""
    import numpy as np
    matrix = np.array(data.get("matrix", [[]]))
    x_labels = data.get("x_labels", [])
    y_labels = data.get("y_labels", [])

    cmap = theme.palette.sequential_colormap()
    im = ax.imshow(matrix, cmap=cmap, aspect="auto")
    ax.figure.colorbar(im, ax=ax, shrink=0.8)

    if x_labels:
        ax.set_xticks(range(len(x_labels)))
        ax.set_xticklabels(x_labels, rotation=45, ha="right")
    if y_labels:
        ax.set_yticks(range(len(y_labels)))
        ax.set_yticklabels(y_labels)

    ax.grid(False)


RENDERERS = {
    "bar": lambda ax, d, t: render_bar(ax, d, t),
    "grouped_bar": lambda ax, d, t: render_bar(ax, d, t),
    "stacked_bar": lambda ax, d, t: render_bar(ax, d, t, stacked=True),
    "horizontal_bar": render_horizontal_bar,
    "line": lambda ax, d, t: render_line(ax, d, t),
    "area": lambda ax, d, t: render_line(ax, d, t, fill=True),
    "pie": lambda ax, d, t: render_pie(ax, d, t),
    "donut": lambda ax, d, t: render_pie(ax, d, t, donut=True),
    "scatter": render_scatter,
    "heatmap": render_heatmap,
}


def render_chart(spec: dict, theme, output_path: str):
    """Render a chart from a JSON spec using a ChartTheme."""
    import matplotlib.pyplot as plt

    chart_type = spec.get("type", "bar")
    title = spec.get("title", "")
    subtitle = spec.get("subtitle", "")
    size_name = spec.get("size", "full-width")
    data = spec.get("data", {})
    x_label = spec.get("x_label", "")
    y_label = spec.get("y_label", "")

    figsize = theme.sizes.get(size_name, theme.sizes["full-width"])

    with theme.apply():
        fig, ax = plt.subplots(figsize=figsize)

        renderer = RENDERERS.get(chart_type)
        if renderer is None:
            print(f"Error: Unknown chart type '{chart_type}'", file=sys.stderr)
            print(f"Supported types: {', '.join(RENDERERS.keys())}", file=sys.stderr)
            sys.exit(1)

        renderer(ax, data, theme)

        if title:
            fig.suptitle(title, fontsize=theme.rcparams.get("axes.titlesize", 18),
                         fontweight="bold", color=theme.rcparams.get("axes.titlecolor", "#1A1A1A"))
        if subtitle:
            ax.set_xlabel(subtitle, fontsize=8, color="#7A7A7A", labelpad=8)
        if x_label and not subtitle:
            ax.set_xlabel(x_label)
        if y_label:
            ax.set_ylabel(y_label)

        fig.savefig(output_path)
        plt.close(fig)

    print(f"Chart saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Render a chart from JSON spec")
    parser.add_argument("--spec", required=True, help="Path to JSON chart spec")
    parser.add_argument("--brand", required=False, help="Path to brand kit directory")
    parser.add_argument("--output", required=True, help="Output image path (.png/.pdf/.svg)")
    parser.add_argument("--dpi", type=int, default=200, help="Output DPI")
    args = parser.parse_args()

    with open(args.spec) as f:
        spec = json.load(f)

    theme = load_theme(args.brand, dpi=args.dpi)
    render_chart(spec, theme, args.output)


if __name__ == "__main__":
    main()
