---
name: athena-work
description: Processes .athenabrief research packages exported from the Athena note-taking app. This skill should be used when the user uploads a .athenabrief file, mentions Athena briefs, research briefings, exported notes, or asks to work with research packages from Athena. Supports zero-instruction processing where the brief itself contains all necessary context. Always packages final results using the athena-package skill.
allowed-tools: Bash, Read, Write
---

# Athena Brief Processor

Process `.athenabrief` research packages exported from the Athena note-taking app. These are ZIP archives containing curated notes, AI-generated summaries, a research brief, and binary assets arranged for progressive disclosure.

## Package Structure Overview

```
package.athenabrief (ZIP)
├── instructions.md        # Static reading guide (start here)
├── brief.md               # Research brief, report, and note index
├── summaries.json         # Machine-readable note summaries
├── manifest.json          # Full machine-readable index and statistics
├── references/*.md        # Full note content with YAML frontmatter
└── assets/*               # Binary attachments (images, PDFs)
```

Read `references/athenabrief-spec.md` for full schema details when encountering unusual fields or edge cases.

## Processing Workflow

### Step 1: Extract and Orient

Extract the `.athenabrief` ZIP to a temporary working directory. Read `instructions.md` first to understand the package's progressive disclosure model. This file is static across all packages and confirms the reading order.

### Step 2: Progressive Disclosure Reads

Read files in this order, stopping as early as possible:

1. **`brief.md`** — Read the research objective, suggested web research, research report, and note index table. This provides the high-level context and tells you what the brief is about.

2. **`summaries.json`** — Read the machine-readable note summaries. Each entry has `generalSummary`, `contextualSummary`, `keyContributions`, and `knowledgeEntries`. This gives you enough detail to plan your approach.

3. **Short-circuit check** — Decide whether you need deeper detail (see decision matrix below). In ~80% of cases, brief.md + summaries.json provide sufficient context.

4. **`manifest.json`** — Read only when you need statistics, relevance scores, sub-query coverage, or the full research plan. Skip if summaries.json was sufficient.

5. **`references/*.md`** — Read individual notes only when you need the full text. Use the manifest or summaries to identify which notes are relevant. Each note has YAML frontmatter with metadata and the full markdown body.

6. **`assets/*`** — Read binary assets only when referenced in the work or explicitly requested by the user.

### Step 3: Short-Circuit Decision Matrix

After reading brief.md and summaries.json, use this matrix:

| Signal | Action |
|--------|--------|
| User gave specific instructions | Follow them; read references only for cited notes |
| Brief has clear research objective + report covers it | Summarize findings from brief.md + summaries; skip references |
| User asks "what's in this brief?" | Summarize from brief.md table + summaries.json; skip references |
| Task requires synthesis across notes | Read relevant references (use summaries to pick which) |
| Task requires exact quotes or data | Read the specific reference notes cited |
| Task requires web research | Note the `webResearchInstructions` from brief.md; search the web |
| No user instructions at all | Use brief's research objective as the task; process accordingly |

### Step 4: Engagement Rules

Ask the user for clarification when ANY of these apply:

- **Imprecise brief** — The research objective is vague and multiple interpretations exist
- **Fuzzy search instructions** — The web research instructions are ambiguous
- **Insufficient knowledge** — The brief references domains you cannot reliably address
- **Contradictory data** — Notes contain conflicting information with no clear resolution
- **Scope ambiguity** — Unclear whether the user wants a summary, analysis, new content, or something else

When the brief contains clear instructions and no ambiguity exists, proceed without asking. Zero-instruction processing is a core feature: the brief itself is the instruction set.

### Step 5: Execute and Package

Execute the work based on the brief content and any user instructions. Delegate to other installed skills as needed (e.g., web search, image generation, document creation).

When producing notes as output, ALWAYS use this mandatory header format:

```markdown
# note title

> short description

---

note content here...
```

The `# title` is the note's display name. The `> description` is a one-line summary. The `---` separator always precedes body content.

After completing the work, ALWAYS use the **athena-package** skill to package results for import back into Athena. Pass all produced notes, relevant assets, and appropriate aurora tags to the packaging step.

## Metadata Precedence

When the same data appears in multiple files:
- **manifest.json is authoritative** for IDs, paths, and scores
- **summaries.json is authoritative** for note summaries
- **YAML frontmatter in references** is convenience — use when reading individual notes
- **brief.md tables** are human-readable summaries — use for quick orientation

## Multi-Brief Workflows

When the user uploads multiple `.athenabrief` packages:

1. Process each brief independently first
2. Look for cross-brief connections using `knowledgeEntries` (shared entities, themes, linked notes)
3. Synthesize findings across briefs when the user asks for combined analysis
4. Package all results into a single `.athena` package unless the user requests separate packages

## Delegation Patterns

The brief may require capabilities beyond text processing:

| Brief content | Delegate to |
|---------------|-------------|
| Web research instructions present | Web search tools |
| "Create a presentation" in objective | Presentation skills if available |
| "Generate images" in objective | Image generation skills if available |
| Code-related analysis | Code analysis tools |
| No delegation needed | Process directly |

Always check what skills and tools are available before promising delegation.

## Error Handling

| Error | Recovery |
|-------|----------|
| ZIP extraction fails | Report the error; ask user to re-export from Athena |
| `instructions.md` missing | Proceed with brief.md; the reading order is documented here |
| `brief.md` missing | Fall back to summaries.json for orientation; warn user |
| `summaries.json` malformed | Fall back to manifest.json + brief.md table |
| `manifest.json` malformed | Use brief.md table + read references directly |
| Reference note missing | Skip it; warn user; use summary data instead |
| Asset file missing | Note the broken reference; continue processing |
| All core files missing | Report package appears corrupt; ask for re-export |

## Graceful Degradation Hierarchy

If files are missing or malformed, fall back in this order:

1. `brief.md` + `summaries.json` (ideal path)
2. `brief.md` + `manifest.json` (summaries unavailable)
3. `brief.md` alone (both JSON files broken)
4. `manifest.json` + `references/*.md` (brief missing)
5. `references/*.md` scanned directly (minimal package)

At each level, warn the user about missing data and reduced accuracy.

## Example

**Input:** User uploads `q1-strategy.athenabrief`

**Processing:**
1. Extract ZIP, read `instructions.md` (standard reading guide)
2. Read `brief.md` — Research objective: "Review Q1 product strategy and roadmap priorities"
3. Read `summaries.json` — 5 notes covering roadmap, standups, competitor analysis, sprint retros, launch checklist
4. Short-circuit: User said "summarize this brief" — brief.md + summaries.json sufficient
5. Produce executive summary note + key findings note + action items note

**Output:** Hand off 3 notes to athena-package skill:
- "Q1 Strategy Summary" (aurora: `focus`)
- "Key Findings" (aurora: `explore`)
- "Action Items" (aurora: `commitments`)

## Reference Materials

- **`references/athenabrief-spec.md`** — Full `.athenabrief` format specification: ZIP structure, brief.md sections, summaries.json schema, manifest.json schema, reference note YAML frontmatter, asset naming conventions. Read when encountering unusual fields, debugging malformed packages, or building custom extraction logic.

- **`references/processing-strategies.md`** — Edge case handling, token optimization strategies, graceful degradation details, and advanced multi-brief workflows. Read when facing complex briefs, performance concerns, or unusual package configurations.
