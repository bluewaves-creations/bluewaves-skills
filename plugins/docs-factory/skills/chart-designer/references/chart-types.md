# Chart Type Cookbook

Complete matplotlib examples for every common chart type. Each example runs
inside `with theme.apply():` and uses brand palette colors automatically.

## Bar Chart

Single-series vertical bars comparing categories.

```python
with theme.apply():
    fig, ax = plt.subplots(figsize=theme.sizes["full-width"])
    categories = ["Q1", "Q2", "Q3", "Q4"]
    values = [120, 150, 180, 210]
    ax.bar(categories, values, color=theme.palette.categorical[0])
    ax.set_title("Revenue by Quarter")
    ax.set_ylabel("Revenue ($M)")
    fig.savefig("bar.png")
    plt.close()
```

Max recommended: 12 categories. For more, switch to horizontal bar.
Tip: Rotate x-labels with `ax.tick_params(axis="x", rotation=45)` if they overlap.

## Grouped Bar Chart

Multi-series vertical bars for category comparison.

```python
import numpy as np

categories = ["Q1", "Q2", "Q3", "Q4"]
emea = [80, 90, 100, 120]
apac = [40, 60, 80, 90]
x = np.arange(len(categories))
width = 0.35

with theme.apply():
    fig, ax = plt.subplots(figsize=theme.sizes["full-width"])
    ax.bar(x - width/2, emea, width, label="EMEA")
    ax.bar(x + width/2, apac, width, label="APAC")
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_title("Revenue by Region")
    ax.legend()
    fig.savefig("grouped_bar.png")
    plt.close()
```

Max recommended: 8 categories, 4 series. Adjust `width = 0.7 / n_series`.

## Stacked Bar Chart

Part-to-whole breakdown by category.

```python
import numpy as np

categories = ["2023", "2024", "2025", "2026"]
product_a = [50, 60, 70, 80]
product_b = [30, 35, 40, 50]
product_c = [20, 25, 30, 35]

with theme.apply():
    fig, ax = plt.subplots(figsize=theme.sizes["full-width"])
    ax.bar(categories, product_a, label="Product A")
    ax.bar(categories, product_b, bottom=product_a, label="Product B")
    ax.bar(categories, product_c,
           bottom=np.array(product_a) + np.array(product_b), label="Product C")
    ax.set_title("Sales Composition")
    ax.legend()
    fig.savefig("stacked_bar.png")
    plt.close()
```

Max recommended: 8 categories, 5 series. More stacks become hard to read.

## Horizontal Bar Chart

Best for long category labels or ranking displays.

```python
categories = ["Dark mode", "Export PDF", "Offline sync", "Multi-language"]
votes = [342, 287, 195, 156]

with theme.apply():
    fig, ax = plt.subplots(figsize=theme.sizes["full-width"])
    ax.barh(categories, votes, color=theme.palette.categorical[0])
    ax.set_title("Feature Requests")
    ax.set_xlabel("Votes")
    ax.invert_yaxis()  # highest value at top
    fig.savefig("horizontal_bar.png")
    plt.close()
```

Max recommended: 15 categories. Natural choice when labels are sentences or long names.

## Line Chart

Trends and changes over time.

```python
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
y2025 = [1200, 1350, 1500, 1420, 1600, 1750]
y2026 = [1500, 1700, 1850, 1900, 2100, 2300]

with theme.apply():
    fig, ax = plt.subplots(figsize=theme.sizes["full-width"])
    ax.plot(months, y2025, marker="o", markersize=4, label="2025")
    ax.plot(months, y2026, marker="o", markersize=4, label="2026")
    ax.set_title("Monthly Active Users")
    ax.legend()
    fig.savefig("line.png")
    plt.close()
```

Max recommended: 24 data points per series, 5 series.
Tip: For dense time series, drop `marker` to keep the chart clean.

## Area Chart

Volume trends — like line chart with filled regions.

```python
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
organic = [500, 600, 700, 650, 800, 900]
paid = [200, 250, 300, 350, 400, 450]

with theme.apply():
    fig, ax = plt.subplots(figsize=theme.sizes["full-width"])
    line1, = ax.plot(months, organic, marker="o", markersize=4, label="Organic")
    ax.fill_between(months, organic, alpha=0.3, color=line1.get_color())
    line2, = ax.plot(months, paid, marker="o", markersize=4, label="Paid")
    ax.fill_between(months, paid, alpha=0.3, color=line2.get_color())
    ax.set_title("Traffic Sources")
    ax.legend()
    fig.savefig("area.png")
    plt.close()
```

Max recommended: 24 data points per series, 4 series.
Tip: Use `ax.stackplot()` for stacked area charts when series represent parts of a whole.

## Pie Chart

Simple part-to-whole composition. Use sparingly.

```python
labels = ["Company A", "Company B", "Company C", "Others"]
sizes = [35, 28, 22, 15]

with theme.apply():
    fig, ax = plt.subplots(figsize=theme.sizes["square"])
    ax.pie(sizes, labels=labels, autopct="%1.0f%%",
           colors=theme.palette.categorical[:len(sizes)],
           wedgeprops={"edgecolor": "white", "linewidth": 1.5},
           startangle=90)
    ax.set_title("Market Share")
    ax.set_aspect("equal")
    fig.savefig("pie.png")
    plt.close()
```

Max recommended: 6 slices. Use `square` size. Group small slices into "Others".
Tip: For slices < 5%, hide the autopct and use a legend instead to avoid label overlap.

## Donut Chart

Part-to-whole with space for a center statistic.

```python
from matplotlib.patches import Circle

labels = ["Engineering", "Marketing", "Sales", "Operations"]
sizes = [40, 25, 20, 15]

with theme.apply():
    fig, ax = plt.subplots(figsize=theme.sizes["square"])
    ax.pie(sizes, labels=labels, autopct="%1.0f%%",
           colors=theme.palette.categorical[:len(sizes)],
           wedgeprops={"edgecolor": "white", "linewidth": 1.5},
           pctdistance=0.78, startangle=90)
    ax.add_artist(Circle((0, 0), 0.55, fc="white"))
    ax.set_title("Budget Allocation")
    ax.set_aspect("equal")
    fig.savefig("donut.png")
    plt.close()
```

Max recommended: 6 slices. Use `square` size.
Tip: Add a center label with `ax.text(0, 0, "$2.4M", ha="center", va="center", fontsize=18, fontweight="bold")`.

## Scatter Chart

Correlation between two variables.

```python
x_a = [10, 20, 30, 40, 50]
y_a = [65, 72, 80, 85, 90]
x_b = [15, 25, 35, 45]
y_b = [60, 68, 75, 82]

with theme.apply():
    fig, ax = plt.subplots(figsize=theme.sizes["full-width"])
    ax.scatter(x_a, y_a, alpha=0.7, s=40, label="Product Line A")
    ax.scatter(x_b, y_b, alpha=0.7, s=40, label="Product Line B")
    ax.set_title("Price vs Performance")
    ax.set_xlabel("Price ($)")
    ax.set_ylabel("Performance Score")
    ax.legend()
    fig.savefig("scatter.png")
    plt.close()
```

Max recommended: 200 points per series, 5 series.
Tip: Use `s=` to encode a third variable (bubble chart). Add a trend line with `np.polyfit`.

## Heatmap

Matrix/grid intensity visualization.

```python
import numpy as np

data = np.array([
    [1.0, 0.8, 0.6, -0.4],
    [0.8, 1.0, 0.5, -0.3],
    [0.6, 0.5, 1.0, -0.7],
    [-0.4, -0.3, -0.7, 1.0],
])
labels = ["Revenue", "Users", "NPS", "Churn"]

with theme.apply():
    fig, ax = plt.subplots(figsize=theme.sizes["square"])
    im = ax.imshow(data, cmap=theme.palette.sequential_colormap(), aspect="auto")
    fig.colorbar(im, ax=ax, shrink=0.8)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_title("Correlation Matrix")
    ax.grid(False)
    fig.savefig("heatmap.png")
    plt.close()
```

Max recommended: 20×20 grid. Uses `theme.palette.sequential_colormap()`.
Tip: Use `theme.palette.diverging_colormap()` for data centered on zero (e.g., correlation matrices).
