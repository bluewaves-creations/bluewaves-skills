# .athenabrief Format Specification

UTType: `co.bluewaves.athena.brief`

The `.athenabrief` format is a ZIP archive produced by the Athena Briefing Center's AI pipeline. It contains a curated selection of the user's notes with AI-generated summaries, a research report, and progressive-disclosure reading order.

## Directory Layout

```
package.athenabrief (ZIP)
├── instructions.md            # Static reading guide for LLMs
├── brief.md                   # Research brief, report, and note index table
├── summaries.json             # Machine-readable note summaries with metadata
├── manifest.json              # Full machine-readable index and statistics
├── references/
│   ├── <uuid1>.md             # Full note content with YAML frontmatter
│   ├── <uuid2>.md
│   └── ...
└── assets/
    ├── <uuid1>-photo.jpg      # Binary assets prefixed by owning note UUID
    ├── <uuid2>-diagram.png
    └── ...
```

## instructions.md

Static across all packages. Describes the progressive disclosure reading order:

1. `instructions.md` — Package guide
2. `brief.md` — Research brief and report
3. `summaries.json` — Note summaries overview
4. `manifest.json` — Machine-readable index
5. `references/*.md` — Full note content (when deep detail needed)
6. `assets/*` — Binary attachments (when referenced)

## brief.md

Human-readable research briefing with these sections:

```markdown
# Briefing: <Title>

Generated: <ISO 8601 timestamp>
Notes: <count> | Assets: <count>

## Research Objective
<What this briefing is about>

## Suggested Web Research
<Optional web research instructions>

## Research Report
<AI-generated synthesis, <500 words>

## Included Notes
| # | Title | Aurora | Updated | Relevance | Assets |
|---|-------|--------|---------|-----------|--------|
| 1 | Note Title | focus | Jan 15, 2026 | High | 1 |

## Asset Index
| File | Source Note | Type | Size |
|------|-----------|------|------|
| assets/<uuid>-filename.ext | Note Title | image | 245 KB |
```

Relevance thresholds: >0.7 = High, >0.4 = Medium, <=0.4 = Low.

## summaries.json

```json
{
  "version": 1,
  "briefDescription": "...",
  "notes": [
    {
      "id": "<UUID>",
      "title": "Note Title",
      "aurora": "focus",
      "updatedAt": "2026-01-15T10:30:00Z",
      "generalSummary": "Static summary of the note content...",
      "assetCount": 1
    }
  ]
}
```

### Required fields per note

| Field | Type | Description |
|-------|------|-------------|
| `id` | String | UUID matching the reference filename |
| `title` | String | Note display title |
| `aurora` | String | Aurora energy tag |
| `updatedAt` | String | ISO 8601 last update timestamp |
| `generalSummary` | String | Context-independent note summary |
| `assetCount` | Int | Number of assets for this note |

### Optional fields per note

| Field | Type | Description |
|-------|------|-------------|
| `spaceID` | String | Athena space identifier |
| `path` | String | Original path in Athena (e.g., `Areas/Product/Note.md`) |
| `createdAt` | String | ISO 8601 creation timestamp |
| `contextualSummary` | String | Summary in context of this specific briefing |
| `relevanceRationale` | String | Why this note is relevant to the briefing |
| `keyContributions` | Array[String] | Specific contributions to the research objective |
| `knowledgeEntries` | Array[Object] | Typed knowledge graph entries (see below) |
| `assets` | Array[Object] | Asset metadata (`name`, `type`, `packagePath`) |

### knowledgeEntries types

| Type | Description | Fields |
|------|-------------|--------|
| `entity` | Named entity | `label`, optional `confidence` (0-1) |
| `theme` | Topic/theme | `label` |
| `linkedNote` | Cross-reference | `label` (title of linked note) |

## manifest.json

```json
{
  "version": 1,
  "format": "athenabrief",
  "generatedAt": "2026-02-07T12:00:00Z",
  "appVersion": "1.0",
  "briefDescription": "...",
  "webResearchInstructions": "...",
  "researchPlan": {
    "objective": "...",
    "subQueries": ["query1", "query2"],
    "themes": ["theme1", "theme2"]
  },
  "researchReport": "...",
  "isAIGenerated": true,
  "statistics": {
    "totalNotes": 5,
    "totalAssets": 2,
    "totalSizeBytes": 1494016,
    "auroraDistribution": { "focus": 1, "collab": 1 },
    "subQueryCoverage": { "query1": 2, "query2": 1 }
  },
  "notes": [
    {
      "id": "<UUID>",
      "title": "Note Title",
      "aurora": "focus",
      "relevanceScore": 0.92,
      "sourceSubQuery": "query1",
      "updatedAt": "2026-01-15T10:30:00Z",
      "referencePath": "references/<UUID>.md",
      "assets": [
        {
          "id": "<UUID>",
          "name": "filename.png",
          "type": "image",
          "size": 250880,
          "mimeType": "image/png",
          "packagePath": "assets/<note-uuid>-filename.png"
        }
      ]
    }
  ]
}
```

### Required manifest fields

| Field | Type | Description |
|-------|------|-------------|
| `version` | Int | Must be `1` |
| `format` | String | Must be `"athenabrief"` |
| `notes` | Array | At least one note entry |
| `notes[].id` | String | UUID |
| `notes[].title` | String | Display title |
| `notes[].aurora` | String | Aurora energy tag |
| `notes[].referencePath` | String | Path to reference file in ZIP |

### Optional manifest fields

All other fields are optional: `generatedAt`, `appVersion`, `briefDescription`, `webResearchInstructions`, `researchPlan`, `researchReport`, `isAIGenerated`, `statistics`, `notes[].relevanceScore`, `notes[].sourceSubQuery`, `notes[].updatedAt`, `notes[].spaceID`, `notes[].path`, `notes[].createdAt`, `notes[].assets`.

## Reference Note Format (references/*.md)

Each reference is a markdown file named `<UUID>.md` with YAML frontmatter:

```yaml
---
id: <UUID>
title: Note Title
aurora: focus
spaceID: personal
path: Areas/Product/Note.md
created: 2026-01-10T08:00:00Z
updated: 2026-01-15T10:30:00Z
summary: General summary text...
contextualSummary: Summary in briefing context...
relevanceRationale: Why this note matters...
keyContributions:
  - Contribution 1
  - Contribution 2
knowledge:
  entities:
    - label: Entity Name
      confidence: 0.95
  themes:
    - label: Theme Name
  linkedNotes:
    - label: Other Note Title
assets:
  - name: filename.png
    path: ../assets/<uuid>-filename.png
    type: image
    size: 250880
---

Note body content in markdown...
```

### Required frontmatter fields

`id`, `title`, `aurora`

### Optional frontmatter fields

All others: `spaceID`, `path`, `created`, `updated`, `summary`, `contextualSummary`, `relevanceRationale`, `keyContributions`, `knowledge`, `assets`.

## Asset Naming Convention

```
assets/<owning-note-UUID>-<original-filename>
```

Example: `assets/A1B2C3D4-E5F6-7890-ABCD-EF0123456789-roadmap.png`

The UUID prefix ensures collision-free naming when multiple notes have assets with the same filename.

## Aurora Values

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
