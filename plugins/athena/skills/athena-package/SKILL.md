---
name: athena-package
description: Creates validated .athena import packages for the Athena note-taking app. This skill should be used when the user wants to send notes, research results, or documents back into Athena, when packaging conversation results for Athena, or at the end of an athena-work processing session. Produces ZIP packages conforming to the .athena import specification with manifest, markdown notes, aurora tags, and optional assets.
allowed-tools: Bash, Read, Write
---

# Athena Package Creator

Create validated `.athena` import packages for the Athena note-taking app. These are ZIP archives containing a manifest, markdown notes with aurora tags, and optional assets.

## Package Format Overview

```
package.athena (ZIP)
├── manifest.json              # Required: note index with aurora tags
├── notes/
│   ├── project-plan.md        # Markdown notes with optional YAML frontmatter
│   ├── meeting-notes.md
│   └── ...
└── assets/
    ├── diagram.png            # Binary assets referenced from notes
    └── ...
```

Read `references/athena-spec.md` for full schema details when handling unusual configurations.

## Creation Workflow

### Step 1: Gather Content

Collect all content to package:
- From an athena-work processing session (most common)
- From conversation results the user wants to save
- From uploaded files the user wants to import
- From generated content (research, summaries, analyses)

### Step 2: Prepare Notes

For each note, create a markdown file with:

1. **Slug filename** — lowercase, hyphenated, `.md` extension (e.g., `project-plan.md`)
2. **Mandatory header format** (see below)
3. **Optional YAML frontmatter** — only `title` and `aurora` are parsed; these override manifest values

Place all note files in the `notes/` directory.

### Mandatory Note Header Format

ALWAYS use this exact structure for every note:

```markdown
# note title

> short description

---

note content here...
```

- `# title` — Must match the manifest title for this note
- `> description` — One-line summary of the note's content
- `---` — Horizontal rule separator; always present before body content
- Body content follows in standard markdown

Example:

```markdown
# Market Analysis Q1 2026

> Competitive landscape analysis covering AI assistant market trends and growth

---

## Overview

The AI assistant market grew 40% year-over-year...
```

### Step 3: Assign Aurora Tags

Every note requires an aurora tag. Use this table for selection:

| Aurora Value | Use When | Examples |
|-------------|----------|---------|
| `commitments` | Obligations, promises, deadlines, action items | Task lists, deadline trackers, promises made |
| `focus` | Deep work, projects needing concentration | Project plans, strategy docs, specs |
| `ops` | Operations, processes, recurring tasks | Runbooks, checklists, SOPs |
| `collab` | Collaboration, meetings, shared work | Meeting notes, team decisions, feedback |
| `life` | Personal, wellbeing, non-work | Personal goals, health notes, hobbies |
| `explore` | Research, ideas, exploration | Research findings, brainstorms, discoveries |
| `archive` | Completed/archived items | Finished projects, historical records |
| `library` | Reference material, resources | Guides, documentation, collected resources |

**Default selection guidance:**
- Documentation and guides: `library`
- Research and analysis: `explore`
- Actionable items with owners/deadlines: `commitments`
- Project plans and strategy: `focus`
- Meeting summaries: `collab`

Ask the user when the appropriate tag is ambiguous or when notes span multiple categories.

### Step 4: Handle Cross-References

**Note-to-note links** — Use relative paths:
```markdown
[Display Title](notes/other-note.md)
```

**Asset references** — Use standard markdown image/link syntax:
```markdown
![Alt text](assets/filename.ext)
[Download report](assets/report.pdf)
```

Athena's importer remaps these paths to internal UUIDs. References that don't match any file in the package are left unchanged.

### Step 5: Build manifest.json

Create the manifest with this structure:

```json
{
  "version": 1,
  "format": "athena",
  "generatedAt": "<ISO 8601 timestamp>",
  "source": "claude",
  "notes": [
    {
      "file": "notes/slug-name.md",
      "title": "Display Title",
      "aurora": "focus",
      "assets": [
        { "name": "diagram.png", "file": "assets/diagram.png", "type": "image" }
      ]
    }
  ]
}
```

**Required fields:** `version` (must be 1), `format` (must be `"athena"`), `notes` array (at least one entry), and for each note: `file`, `title`, `aurora`.

**Optional fields:** `generatedAt`, `source`, `notes[].assets` (may be omitted or empty array).

### Step 6: Validate, Fix, and Create

Run the validation-fix-revalidation loop:

1. **Prepare staging directory** — Create a temporary directory with `manifest.json`, `notes/`, and `assets/` subdirectories
2. **Validate** — Run the validation script:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/athena-package/scripts/validate_athena_package.py <staging-dir>
   ```
3. **Fix issues** — If validation reports errors, fix them:
   - Missing files: create or remove from manifest
   - Invalid aurora tags: correct to valid values
   - Header format errors: add/fix `# title` + `> description` + `---`
   - Cross-reference targets missing: fix paths or remove references
4. **Revalidate** — Run validation again until clean (exit code 0)
5. **Create package** — Run the creation script:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/athena-package/scripts/create_athena_package.py <staging-dir> [output-path]
   ```
6. **Deliver** — Report the output file path and summary to the user

## Validation Feedback Loop

Never skip validation. The `.athena` format is strict — Athena's importer rejects malformed packages. The validate-fix-revalidate cycle catches issues before the user tries to import.

Common validation errors and fixes:

| Error | Fix |
|-------|-----|
| "manifest.json not found" | Create the manifest file |
| "invalid aurora tag 'X'" | Replace with a valid aurora value |
| "note file 'notes/X.md' not found" | Create the file or remove from manifest |
| "disk file 'notes/X.md' not in manifest" | Add to manifest or remove the file |
| "note missing header format" | Add `# title\n\n> description\n\n---` |
| "cross-reference target 'notes/X.md' not found" | Fix the path or create the target |
| "asset 'assets/X.png' not found" | Add the file or remove the reference |

## Example

**Input:** 2 notes from a research session with 1 image asset.

**Staging directory:**
```
research-output/
├── manifest.json
├── notes/
│   ├── executive-summary.md
│   └── market-analysis.md
└── assets/
    └── market-chart.png
```

**manifest.json:**
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

**notes/executive-summary.md:**
```markdown
# Executive Summary

> High-level overview of Q1 2026 strategy findings

---

Based on our [Market Analysis](notes/market-analysis.md), three key themes emerge...

### Key Decisions
1. Prioritize mobile-first experience
2. Launch AI features in March
```

**notes/market-analysis.md:**
```markdown
# Market Analysis

> Competitive landscape analysis for the AI assistant market

---

## Overview

![Market Share Chart](assets/market-chart.png)

The AI assistant market grew 40% YoY...
```

**Result:** `research-output.athena` (ZIP, 3 files, ready for import)

## Error Handling

| Error | Recovery |
|-------|----------|
| No content to package | Ask the user what to include |
| Validation fails after 3 fix attempts | Show remaining errors; ask user for guidance |
| Script not found | Report the issue; manually create the ZIP structure |
| Python not available | Report the issue; manually create the ZIP |
| Output directory not writable | Try current directory; ask user for alternative |

## Reference Materials

- **`references/athena-spec.md`** — Full `.athena` import format specification: manifest.json schema, required/optional fields, note format with frontmatter override rules, asset handling, cross-reference syntax, aurora tag values, and import behavior (Inbox placement, deduplication, UUID remapping). Read when handling unusual package configurations or debugging import failures.
