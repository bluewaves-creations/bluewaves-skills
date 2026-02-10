#!/usr/bin/env python3
"""Brand-aware matplotlib theme loader.

Reads tokens.chart and tokens.colors from a brand kit's manifest.json
and produces a ready-to-apply matplotlib configuration.

Usage as library:
    from chart_theme import load_theme
    theme = load_theme(brand_path="path/to/brand-decathlon")
    with theme.apply():
        fig, ax = plt.subplots(figsize=theme.sizes["full-width"])
        ax.bar(...)

Usage as CLI (info mode):
    python chart_theme.py --brand path/to/brand-decathlon --info
"""
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class BrandPalette:
    """Color palettes extracted from tokens.chart."""

    categorical: list[str] = field(default_factory=lambda: [
        "#4C72B0", "#DD8452", "#55A868", "#C44E52",
        "#8172B3", "#937860", "#DA8BC3", "#8C8C8C",
    ])
    sequential: list[str] = field(default_factory=lambda: [
        "#D4E6F1", "#A9CCE3", "#7FB3D5", "#5499C7",
        "#2980B9", "#2471A3", "#1A5276",
    ])
    diverging: list[str] = field(default_factory=lambda: [
        "#E74C3C", "#F1948A", "#FADBD8", "#F0F0F0",
        "#D5F5E3", "#82E0AA", "#27AE60",
    ])
    highlight: str = "#E74C3C"
    highlight_contrast: str = "#FFFFFF"

    def categorical_colormap(self):
        """Return a matplotlib ListedColormap from categorical palette."""
        from matplotlib.colors import ListedColormap
        return ListedColormap(self.categorical, name="brand_categorical")

    def sequential_colormap(self):
        """Return a matplotlib LinearSegmentedColormap from sequential palette."""
        from matplotlib.colors import LinearSegmentedColormap
        return LinearSegmentedColormap.from_list(
            "brand_sequential", self.sequential
        )

    def diverging_colormap(self):
        """Return a matplotlib LinearSegmentedColormap from diverging palette."""
        from matplotlib.colors import LinearSegmentedColormap
        return LinearSegmentedColormap.from_list(
            "brand_diverging", self.diverging
        )


# Named figure sizes for A4 (25mm margins, 453pt/6.29" content width)
FIGURE_SIZES = {
    "full-width":      (6.29, 3.93),
    "full-width-tall": (6.29, 5.24),
    "half-width":      (3.0, 2.5),
    "two-thirds":      (4.19, 3.0),
    "square":          (4.0, 4.0),
    "spark":           (3.0, 1.0),
}


@dataclass
class ChartTheme:
    """Complete chart theming configuration."""

    palette: BrandPalette = field(default_factory=BrandPalette)
    rcparams: dict = field(default_factory=dict)
    sizes: dict = field(default_factory=lambda: dict(FIGURE_SIZES))
    dpi: int = 200
    brand_name: str = "Default"
    _original_rcparams: dict = field(default_factory=dict, repr=False)

    def apply(self):
        """Context manager that sets/restores matplotlib rcParams."""
        return _ThemeContext(self)


class _ThemeContext:
    """Context manager for applying/restoring rcParams."""

    def __init__(self, theme: ChartTheme):
        self.theme = theme

    def __enter__(self):
        import matplotlib.pyplot as plt
        self.theme._original_rcparams = dict(plt.rcParams)
        plt.rcParams.update(self.theme.rcparams)
        return self.theme

    def __exit__(self, *args):
        import matplotlib.pyplot as plt
        plt.rcParams.update(self.theme._original_rcparams)


def _resolve_color(color_role: str, colors: dict) -> str:
    """Resolve a color role name to a hex value."""
    return colors.get(color_role, "#1A1A1A")


def _resolve_font_path(font_role: str, weight: str, manifest: dict) -> Optional[str]:
    """Resolve font role + weight to an absolute TTF path."""
    base_path = manifest.get("_base_path", "")
    fonts = manifest.get("fonts", {})
    role_fonts = fonts.get(font_role, {})
    if not isinstance(role_fonts, dict):
        return None
    variant = "bold" if weight == "bold" else "regular"
    rel_path = role_fonts.get(variant)
    if not rel_path:
        return None
    font_path = os.path.join(base_path, rel_path) if not os.path.isabs(rel_path) else rel_path
    return font_path if os.path.exists(font_path) else None


def load_theme(brand_path: Optional[str] = None, dpi: int = 200) -> ChartTheme:
    """Load a ChartTheme from a brand kit directory.

    Args:
        brand_path: Path to brand kit skill directory (e.g., brand-decathlon).
                    If None, returns sensible defaults.
        dpi: Output resolution for charts.

    Returns:
        ChartTheme ready to use with matplotlib.
    """
    if brand_path is None:
        return ChartTheme(dpi=dpi)

    brand_dir = Path(brand_path)
    manifest_path = brand_dir / "assets" / "manifest.json"
    if not manifest_path.exists():
        print(f"Warning: manifest.json not found at {manifest_path}, using defaults",
              file=sys.stderr)
        return ChartTheme(dpi=dpi)

    with open(manifest_path) as f:
        manifest = json.load(f)

    manifest["_base_path"] = str(brand_dir / "assets")
    tokens = manifest.get("tokens", {})
    colors = tokens.get("colors", {})
    type_scale = tokens.get("type_scale", {})
    chart_tokens = tokens.get("chart", {})
    brand_name = manifest.get("brand", {}).get("name", "Unknown")

    # Build palette (use a default instance to pull fallback values)
    _defaults = BrandPalette()
    palette_data = chart_tokens.get("palette", {})
    palette = BrandPalette(
        categorical=palette_data.get("categorical", _defaults.categorical),
        sequential=palette_data.get("sequential", _defaults.sequential),
        diverging=palette_data.get("diverging", _defaults.diverging),
        highlight=palette_data.get("highlight", _defaults.highlight),
        highlight_contrast=palette_data.get("highlight_contrast", _defaults.highlight_contrast),
    )

    # Register brand fonts with matplotlib
    font_family = "sans-serif"
    try:
        import matplotlib.font_manager as fm
        fonts_dir = brand_dir / "assets" / "fonts"
        if fonts_dir.exists():
            for ttf in fonts_dir.glob("*.ttf"):
                fm.fontManager.addfont(str(ttf))
            # Use the heading font as primary
            heading_path = _resolve_font_path("heading", "bold", manifest)
            if heading_path:
                font = fm.FontProperties(fname=heading_path)
                font_family = font.get_name()
    except Exception:
        pass

    # Build rcParams
    chart_typo = chart_tokens.get("typography", {})
    axis_tokens = chart_tokens.get("axis", {})
    grid_tokens = chart_tokens.get("grid", {})
    fig_tokens = chart_tokens.get("figure", {})

    # Resolve title font size from type_scale
    title_style = chart_typo.get("title", {}).get("style", "h3")
    title_size = type_scale.get(title_style, {}).get("size_pt", 18)
    title_color = _resolve_color(
        chart_typo.get("title", {}).get("color_role", "text-heading"), colors
    )

    axis_label_style = chart_typo.get("axis_label", {}).get("style", "body-sm")
    axis_label_size = type_scale.get(axis_label_style, {}).get("size_pt", 9)
    axis_label_color = _resolve_color(
        chart_typo.get("axis_label", {}).get("color_role", "text-body"), colors
    )

    tick_style = chart_typo.get("tick_label", {}).get("style", "caption")
    tick_size = type_scale.get(tick_style, {}).get("size_pt", 8)
    tick_color = _resolve_color(
        chart_typo.get("tick_label", {}).get("color_role", "text-body"), colors
    )

    legend_style = chart_typo.get("legend", {}).get("style", "caption")
    legend_size = type_scale.get(legend_style, {}).get("size_pt", 8)

    rcparams = {
        # Figure
        "figure.facecolor": fig_tokens.get("background", "#FFFFFF"),
        "figure.dpi": dpi,
        "savefig.dpi": dpi,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.1,
        # Axes
        "axes.facecolor": fig_tokens.get("plot_background", "#FFFFFF"),
        "axes.edgecolor": axis_tokens.get("color", "#4A4A4A"),
        "axes.linewidth": axis_tokens.get("width", 0.8),
        "axes.labelcolor": axis_label_color,
        "axes.labelsize": axis_label_size,
        "axes.titlesize": title_size,
        "axes.titlecolor": title_color,
        "axes.titleweight": "bold",
        "axes.prop_cycle": __import__("cycler").cycler(color=palette.categorical),
        # Grid
        "axes.grid": True,
        "grid.color": grid_tokens.get("color", "#B0B0B0"),
        "grid.alpha": grid_tokens.get("alpha", 0.3),
        "grid.linewidth": grid_tokens.get("width", 0.5),
        "grid.linestyle": grid_tokens.get("style", "--"),
        # Ticks
        "xtick.color": tick_color,
        "ytick.color": tick_color,
        "xtick.labelsize": tick_size,
        "ytick.labelsize": tick_size,
        # Legend
        "legend.fontsize": legend_size,
        "legend.framealpha": 0.9,
        "legend.edgecolor": "#CCCCCC",
        # Font
        "font.family": font_family,
        "font.size": axis_label_size,
    }

    return ChartTheme(
        palette=palette,
        rcparams=rcparams,
        sizes=dict(FIGURE_SIZES),
        dpi=dpi,
        brand_name=brand_name,
    )


def main():
    """CLI entry point for theme inspection."""
    import argparse

    parser = argparse.ArgumentParser(description="Inspect brand chart theme")
    parser.add_argument("--brand", default=None, help="Path to brand kit directory (omit for defaults)")
    parser.add_argument("--info", action="store_true", help="Print theme info")
    parser.add_argument("--dpi", type=int, default=200, help="Output DPI")
    args = parser.parse_args()

    theme = load_theme(args.brand, dpi=args.dpi)

    if args.info:
        print(f"Brand: {theme.brand_name}")
        print(f"DPI: {theme.dpi}")
        print(f"Categorical colors ({len(theme.palette.categorical)}): {theme.palette.categorical}")
        print(f"Sequential colors ({len(theme.palette.sequential)}): {theme.palette.sequential}")
        print(f"Diverging colors ({len(theme.palette.diverging)}): {theme.palette.diverging}")
        print(f"Highlight: {theme.palette.highlight} on {theme.palette.highlight_contrast}")
        print(f"Figure sizes: {list(theme.sizes.keys())}")
        print(f"rcParams keys: {len(theme.rcparams)}")


if __name__ == "__main__":
    main()
