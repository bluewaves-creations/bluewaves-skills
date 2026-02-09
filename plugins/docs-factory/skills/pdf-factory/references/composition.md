# Composition Rules

## Contents

- [Page grid](#page-grid)
- [Vertical rhythm](#vertical-rhythm)
- [Content flow](#content-flow)
- [Widows and orphans](#widows-and-orphans)
- [Page break rules](#page-break-rules)
- [Image placement](#image-placement)
- [Table layout](#table-layout)

## Page Grid

Calculate content area from brand kit spacing tokens:

```
content_width = page_width - margin_left - margin_right
content_height = page_height - margin_top - margin_bottom - header_height - footer_height
```

Use single column spanning full content width.
If content width exceeds `paragraph.max_width_chars` at body font size, center the text block horizontally.

## Vertical Rhythm

Base all vertical spacing on `base_unit_pt` from spacing tokens.

Spacing before elements (multiples of base unit):
- Before h1: 6x
- Before h2: 4x
- Before h3: 3x
- Before h4: 2x
- Between paragraphs: 1x (use `spacing_after_pt`)
- After any heading: 1x

## Content Flow

Track remaining vertical space on each page. Before placing an element, check if it fits. If not, start a new page.

Atomic elements (move whole to next page if they don't fit):
- Code blocks under 20 lines
- Images
- Tables under 10 rows
- Blockquotes under 5 lines

## Widows and Orphans

- Minimum 2 lines of a paragraph at bottom of page
- Minimum 2 lines of a paragraph at top of page
- Headings must have at least 2 lines of following content on same page
- Move heading to next page if it would be the last element on a page

## Page Break Rules

Force page break before:
- h1 headings (new section)
- Elements with explicit page-break-before

Never break inside:
- A heading and its first paragraph
- A code block under 20 lines
- A table under 10 rows
- An image and its caption
- A blockquote under 5 lines

## Image Placement

- Maximum width: 100% of content width
- Maximum height: 60% of body zone height
- Scale proportionally when exceeding limits
- Normalize to 150 DPI for print quality
- Center horizontally in content area
- Place caption in `caption` style, centered below, with `xs` spacing gap

## Table Layout

Column width algorithm:
1. Calculate minimum width per column (longest word + `sm` padding)
2. Calculate preferred width (longest content + `sm` padding)
3. Distribute remaining width proportionally
4. Cap any column at 50% of table width

Styling:
- Header row: bold text, `background-alt` fill, `border-strong` bottom border
- Body rows: alternating `background-page` / `background-alt`
- All rows: `border-default` bottom border
- Cell padding: `sm` on all sides

Repeat header row on continuation pages for tables exceeding page height.
