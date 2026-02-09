# Element Rendering

## Contents

- [Headings](#headings)
- [Code blocks](#code-blocks)
- [Blockquotes](#blockquotes)
- [Lists](#lists)
- [Horizontal rules](#horizontal-rules)
- [Inline elements](#inline-elements)
- [Table of contents](#table-of-contents)
- [Footnotes](#footnotes)
- [Cover page metadata](#cover-page-metadata)

## Headings

| Markdown | Style token | Notes |
|---|---|---|
| `# H1` | `h1` | Force page break before |
| `## H2` | `h2` | |
| `### H3` | `h3` | |
| `#### H4` | `h4` | |

Use `text-heading` color role for all headings.
Never hyphenate. Always left-align unless zone specifies otherwise.

## Code Blocks

- Use `code` style token with mono font
- Background: `background-alt` with `sm` padding
- Left border: 2pt in `highlight` color
- Line numbers: include for blocks over 5 lines, use `caption` style in `text-muted`, right-aligned in dedicated left column
- Syntax highlighting via `codehilite` extension: keywords → `primary`, strings → `success`, comments → `text-muted`, numbers → `accent`
- Split at line boundaries when exceeding page height; repeat language label with "(continued)" on next page

## Blockquotes

- Left border: 3pt in `highlight` color
- Left padding: `md` spacing
- Text: `body` style with italic font variant, `neutral-700` color
- Nested blockquotes: increase left margin by `md` per level

## Lists

- Unordered: filled circle bullet in `text-muted`
- Ordered: number + period in `text-muted`
- Bullet/number indent: `lg` from left margin
- Text indent: `lg` from bullet/number
- Between items: `xs` spacing
- Between list groups: standard paragraph spacing
- Nested: increase indent by `lg` per level, maximum 3 levels

## Horizontal Rules

- 0.5pt line in `border-default` color, full content width
- Vertical spacing: `xl` above and below

## Inline Elements

| Markdown | Rendering |
|---|---|
| `**bold**` | body-bold font |
| `*italic*` | body-italic font |
| `***bold italic***` | body-bold-italic font |
| `` `code` `` | mono font, `background-alt`, `sm` horizontal padding |
| `[link](url)` | `link` color, underline |
| `~~strike~~` | horizontal line through center |

## Table of Contents

Generate from headings when `toc` extension is active.

- Entry format: heading text (left) ... page number (right) with dot leaders
- Indent by heading level
- Use `body` style for h2 entries, `body-sm` for h3 entries, omit h4+

## Footnotes

- Collect at bottom of the page where referenced
- Separator: thin horizontal rule (`border-default`, 33% content width)
- Text: `caption` style, sequential superscript integer numbering

## Cover Page Metadata

Map markdown frontmatter to cover template zones:
- `title` → "title" zone
- `subtitle` → "subtitle" zone
- `date` → "date" zone
- `author` → "author" zone (if defined)

Logo placement is automatic from zone definition.
