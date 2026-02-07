# .athena Import Format Specification

UTType: `co.bluewaves.athena.package`

The `.athena` format is a ZIP archive designed for LLMs (or other tools) to produce notes that get imported into Athena. It uses human-readable filenames (not UUIDs). Athena's importer remaps all internal references to its UUID-based system.

## Directory Layout

```
package.athena (ZIP)
├── manifest.json              # Required: note index with aurora tags
├── notes/
│   ├── project-plan.md        # Markdown with optional YAML frontmatter
│   ├── meeting-notes.md
│   └── ...
└── assets/
    ├── diagram.png            # Binary assets referenced from notes
    ├── report.pdf
    └── ...
```

## manifest.json

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `version` | Int | Must be `1` |
| `format` | String | Must be `"athena"` |
| `notes` | Array | At least one note entry |
| `notes[].file` | String | Relative path, e.g. `"notes/slug.md"` |
| `notes[].title` | String | Display title |
| `notes[].aurora` | String | Aurora energy classification |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `generatedAt` | String | ISO 8601 timestamp |
| `source` | String | Producer identifier (e.g. `"claude"`) |
| `notes[].assets` | Array | Asset references (may be `null` or omitted) |
| `notes[].assets[].name` | String | Filename, e.g. `"diagram.png"` |
| `notes[].assets[].file` | String | Relative path, e.g. `"assets/diagram.png"` |
| `notes[].assets[].type` | String | Type hint: `"image"`, `"pdf"`, etc. (auto-detected by importer) |

### Example

```json
{
  "version": 1,
  "format": "athena",
  "generatedAt": "2026-02-07T14:30:00Z",
  "source": "claude",
  "notes": [
    {
      "file": "notes/executive-summary.md",
      "title": "Executive Summary",
      "aurora": "focus",
      "assets": []
    },
    {
      "file": "notes/market-analysis.md",
      "title": "Market Analysis",
      "aurora": "explore",
      "assets": [
        { "name": "market-chart.png", "file": "assets/market-chart.png", "type": "image" }
      ]
    }
  ]
}
```

## Aurora Values

Every note requires an aurora tag. Invalid values cause the note to be rejected.

| Value | Description |
|-------|-------------|
| `commitments` | Obligations, promises, deadlines |
| `focus` | Deep work, projects requiring concentration |
| `ops` | Operations, processes, recurring tasks |
| `collab` | Collaboration, meetings, shared work |
| `life` | Personal, wellbeing, non-work |
| `explore` | Research, ideas, exploration |
| `archive` | Completed/archived items |
| `library` | Reference material, resources |

## Mandatory Note Header Format

Every note MUST begin with this exact structure (after any optional YAML frontmatter):

```markdown
# note title

> short description

---

note content here...
```

- `# title` — The note's display name; should match the manifest title
- `> description` — A single-line summary of the note's content
- `---` — Horizontal rule separator; always present before the body
- Body content follows in standard markdown

Notes missing this header structure will trigger a validation warning.

## Note Frontmatter (Optional)

Notes may include YAML frontmatter that overrides manifest values:

```markdown
---
title: Project Plan
aurora: focus
---

# Project Plan

> Detailed project plan for Q1 2026

---

Content here...
```

Only `title` and `aurora` are parsed from frontmatter. If present, they override the corresponding manifest values for that note. The frontmatter block is stripped from imported content.

## Cross-Reference Syntax

### Asset References

Use standard markdown image syntax:

```markdown
![Alt text](assets/filename.ext)
```

The importer remaps `assets/filename.ext` to `assets/<new-uuid>.ext`.

### Inter-Note Links

Use standard markdown link syntax:

```markdown
[Display Title](notes/slug.md)
```

The importer remaps `notes/slug.md` to `athena://document/<new-uuid>`.

References that don't match any file in the package are left unchanged.

## Import Behavior

### Placement
- Notes are created in the **Inbox** of the selected space
- Path format: `Inbox/<title>.md`

### Deduplication
- If a note with the same title exists in Inbox, the new note gets a suffix: `(2)`, `(3)`, etc.

### UUID Remapping
- Each imported note and asset receives a fresh UUID
- All `assets/` and `notes/` paths in content are remapped to the new UUIDs
- Cross-references between package notes become internal Athena links

### Error Handling
- Missing note files referenced in manifest: skipped with warnings (non-fatal)
- Missing asset files: skipped with warnings (non-fatal)
- Invalid aurora values: note is rejected (skipped with warning)
- The package must contain at least one valid note or import fails entirely

## Filename Conventions

### Note Filenames
- Lowercase, hyphenated slugs: `project-plan.md`, `meeting-notes.md`
- Always in the `notes/` directory
- Always `.md` extension

### Asset Filenames
- Descriptive names: `diagram.png`, `report.pdf`, `chart.svg`
- Always in the `assets/` directory
- Any extension; type is auto-detected by the importer

## Differences from .athenabrief

| Aspect | .athena (import) | .athenabrief (export) |
|--------|-------------------|-----------------------|
| Direction | LLM to App | App to LLM |
| Filenames | Human-readable slugs | UUID-based |
| Asset naming | Plain filenames | UUID-prefixed |
| Manifest | Minimal (notes + assets) | Rich (stats, scores, plan) |
| Extra files | None | instructions.md, brief.md, summaries.json |
| Frontmatter | Minimal (title, aurora) | Rich (id, knowledge, summaries) |
