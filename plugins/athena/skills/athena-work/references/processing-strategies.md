# Processing Strategies

Advanced strategies for processing `.athenabrief` packages, covering edge cases, token optimization, and complex workflows.

## Token Optimization

### Early Termination

The progressive disclosure model is designed for early termination. Most queries resolve after reading just 2 files:

| Files Read | Estimated Token Cost | Coverage |
|-----------|---------------------|----------|
| brief.md only | ~500 tokens | Orientation, simple summaries |
| brief.md + summaries.json | ~1,500 tokens | ~80% of interactions |
| + manifest.json | ~3,000 tokens | Statistics, scores, research plan |
| + all references | ~10,000+ tokens | Full detail |

### Selective Reference Loading

Never read all references at once. Use summaries to identify relevant notes:

1. Check `relevanceScore` in manifest — prioritize >0.7 (High)
2. Check `sourceSubQuery` — load notes matching the user's specific question
3. Check `keyContributions` in summaries — load notes with relevant contributions
4. Check `knowledgeEntries` — load notes with matching entities or themes

### Information Deduplication

The same data appears across multiple files. Avoid re-reading:

| Data | Best source | Skip |
|------|------------|------|
| Note titles and aurora tags | brief.md table | summaries.json, manifest |
| Note summaries | summaries.json | manifest, frontmatter |
| Relevance scores | manifest.json | brief.md thresholds |
| Research objective | brief.md | manifest.briefDescription |
| Full note content | references/*.md | — |
| Asset metadata | manifest.json notes[].assets | frontmatter assets |

## Edge Cases

### Empty or Minimal Packages

| Condition | Handling |
|-----------|---------|
| 1 note, no assets | Process the single note; still package results |
| No research objective | Ask user what they want; use note titles for context |
| No research report | Summaries are sufficient; generate your own synthesis |
| No web research instructions | Skip web research unless user requests it |
| Empty summaries.json notes array | Fall back to manifest.json + references |

### Large Packages (20+ Notes)

For packages with many notes:

1. Read brief.md for the overview and note count
2. Read summaries.json — scan `contextualSummary` for relevance
3. Group notes by aurora tag or `sourceSubQuery` for batch processing
4. Process in priority order: High relevance first, then Medium
5. Skip Low relevance notes unless specifically needed
6. Report which notes were skipped and why

### Conflicting Data Between Layers

When manifest and frontmatter disagree:

- **Manifest is authoritative** for: IDs, file paths, relevance scores, sub-query assignments
- **Frontmatter is authoritative** for: nothing (it's convenience data)
- **Summaries are authoritative** for: generalSummary, contextualSummary, keyContributions

If brief.md table shows different data than summaries.json, trust summaries.json (machine-readable is more reliable than the rendered table).

### Malformed JSON

If summaries.json or manifest.json fails to parse:

1. Attempt to extract partial data (e.g., valid JSON prefix before error)
2. Fall back to brief.md table for note inventory
3. Read references directly, scanning frontmatter for metadata
4. Warn the user about reduced accuracy

### Missing References

If a note in summaries.json has no corresponding file in `references/`:

1. Use the summary data as-is — it may be sufficient
2. Note the gap in your output ("Note X was listed but not included in package")
3. Do not fabricate content for missing notes

## Multi-Brief Workflows

### Sequential Processing

When multiple briefs arrive in sequence:

1. Process each brief fully before moving to the next
2. Track entities and themes across briefs using `knowledgeEntries`
3. Build a cumulative understanding — later briefs may reference earlier findings
4. Package all results together unless user wants separate packages

### Cross-Brief Connections

Look for connections using `knowledgeEntries`:

- **Shared entities** — Same `entity.label` across briefs indicates common subjects
- **Shared themes** — Same `theme.label` indicates overlapping topics
- **Linked notes** — `linkedNote.label` referencing notes in another brief
- **Same aurora tags** — Notes with matching tags may serve similar purposes

### Conflict Resolution Across Briefs

When briefs contain contradictory information:

1. Note the contradiction explicitly
2. Prefer the more recent brief (check `generatedAt`)
3. Prefer notes with higher relevance scores
4. When in doubt, present both perspectives and let the user decide

## Advanced Delegation

### When to Delegate vs. Process Directly

| Situation | Action |
|-----------|--------|
| Brief asks for text summarization | Process directly |
| Brief asks for web research | Delegate to web search |
| Brief asks for code analysis | Delegate to code tools |
| Brief asks for creative content | Process directly (then package) |
| Brief asks for data visualization | Delegate if chart tools available |
| Brief asks for "everything" | Break into sub-tasks, delegate as needed |

### Preserving Context During Delegation

When delegating to other tools or skills:

1. Pass the research objective as context
2. Include relevant summaries for background
3. Specify output format (notes with mandatory headers)
4. Collect results and include in the athena-package step

## Quality Checklist

Before packaging results:

- [ ] All user instructions addressed (or clarified why not)
- [ ] Notes use mandatory header format (`# title` + `> description` + `---` + body)
- [ ] Aurora tags assigned appropriately for each output note
- [ ] Cross-references between output notes use `[Title](notes/slug.md)` format
- [ ] Assets referenced correctly with `![Alt](assets/filename.ext)` format
- [ ] No fabricated data — all claims traceable to brief content or web research
- [ ] Degradation warnings included if any package files were missing/malformed
