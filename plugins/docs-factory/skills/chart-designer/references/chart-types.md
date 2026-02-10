# Chart Type Templates

Complete code templates for all 10 supported chart types.

## Bar Chart

Single-series vertical bars comparing categories.

```json
{
  "type": "bar",
  "title": "Revenue by Quarter",
  "size": "full-width",
  "data": {
    "categories": ["Q1", "Q2", "Q3", "Q4"],
    "series": [{"name": "Revenue", "values": [120, 150, 180, 210]}]
  }
}
```

```python
with theme.apply():
    fig, ax = plt.subplots(figsize=theme.sizes["full-width"])
    ax.bar(categories, values, color=theme.palette.categorical[0])
    ax.set_title("Revenue by Quarter")
    fig.savefig("bar.png")
```

Max recommended: 12 categories, 1 series.

## Grouped Bar Chart

Multi-series vertical bars for category comparison.

```json
{
  "type": "grouped_bar",
  "title": "Revenue by Region",
  "data": {
    "categories": ["Q1", "Q2", "Q3", "Q4"],
    "series": [
      {"name": "EMEA", "values": [80, 90, 100, 120]},
      {"name": "APAC", "values": [40, 60, 80, 90]}
    ]
  }
}
```

```python
import numpy as np
x = np.arange(len(categories))
width = 0.35
with theme.apply():
    fig, ax = plt.subplots(figsize=theme.sizes["full-width"])
    ax.bar(x - width/2, emea, width, label="EMEA")
    ax.bar(x + width/2, apac, width, label="APAC")
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()
    fig.savefig("grouped_bar.png")
```

Max recommended: 8 categories, 4 series.

## Stacked Bar Chart

Part-to-whole breakdown by category.

```json
{
  "type": "stacked_bar",
  "title": "Sales Composition",
  "data": {
    "categories": ["2023", "2024", "2025", "2026"],
    "series": [
      {"name": "Product A", "values": [50, 60, 70, 80]},
      {"name": "Product B", "values": [30, 35, 40, 50]},
      {"name": "Product C", "values": [20, 25, 30, 35]}
    ]
  }
}
```

Max recommended: 8 categories, 5 series.

## Horizontal Bar Chart

Best for long category labels or ranking displays.

```json
{
  "type": "horizontal_bar",
  "title": "Feature Requests",
  "data": {
    "categories": ["Dark mode", "Export PDF", "Offline sync", "Multi-language"],
    "series": [{"name": "Votes", "values": [342, 287, 195, 156]}]
  }
}
```

Max recommended: 15 categories, 3 series.

## Line Chart

Trends and changes over time.

```json
{
  "type": "line",
  "title": "Monthly Active Users",
  "data": {
    "categories": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "series": [
      {"name": "2025", "values": [1200, 1350, 1500, 1420, 1600, 1750]},
      {"name": "2026", "values": [1500, 1700, 1850, 1900, 2100, 2300]}
    ]
  }
}
```

```python
with theme.apply():
    fig, ax = plt.subplots(figsize=theme.sizes["full-width"])
    for series in data["series"]:
        ax.plot(categories, series["values"], marker="o", markersize=4,
                label=series["name"])
    ax.legend()
    fig.savefig("line.png")
```

Max recommended: 24 data points per series, 5 series.

## Area Chart

Volume trends — like line chart with filled regions.

```json
{
  "type": "area",
  "title": "Traffic Sources",
  "data": {
    "categories": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "series": [
      {"name": "Organic", "values": [500, 600, 700, 650, 800, 900]},
      {"name": "Paid", "values": [200, 250, 300, 350, 400, 450]}
    ]
  }
}
```

Max recommended: 24 data points per series, 4 series.

## Pie Chart

Simple part-to-whole composition. Use sparingly.

```json
{
  "type": "pie",
  "title": "Market Share",
  "size": "square",
  "data": {
    "categories": ["Company A", "Company B", "Company C", "Others"],
    "series": [{"values": [35, 28, 22, 15]}]
  }
}
```

Max recommended: 6 slices. Use `square` size.

## Donut Chart

Part-to-whole with space for a center statistic.

```json
{
  "type": "donut",
  "title": "Budget Allocation",
  "size": "square",
  "data": {
    "categories": ["Engineering", "Marketing", "Sales", "Operations"],
    "series": [{"values": [40, 25, 20, 15]}]
  }
}
```

Max recommended: 6 slices. Use `square` size.

## Scatter Chart

Correlation between two variables.

```json
{
  "type": "scatter",
  "title": "Price vs Performance",
  "x_label": "Price ($)",
  "y_label": "Performance Score",
  "data": {
    "series": [
      {
        "name": "Product Line A",
        "x": [10, 20, 30, 40, 50],
        "y": [65, 72, 80, 85, 90]
      },
      {
        "name": "Product Line B",
        "x": [15, 25, 35, 45],
        "y": [60, 68, 75, 82]
      }
    ]
  }
}
```

Max recommended: 200 points per series, 5 series.

## Heatmap

Matrix/grid intensity visualization.

```json
{
  "type": "heatmap",
  "title": "Correlation Matrix",
  "size": "square",
  "data": {
    "x_labels": ["Revenue", "Users", "NPS", "Churn"],
    "y_labels": ["Revenue", "Users", "NPS", "Churn"],
    "matrix": [
      [1.0, 0.8, 0.6, -0.4],
      [0.8, 1.0, 0.5, -0.3],
      [0.6, 0.5, 1.0, -0.7],
      [-0.4, -0.3, -0.7, 1.0]
    ]
  }
}
```

Uses the brand's sequential colormap. Max recommended: 20×20 grid.
