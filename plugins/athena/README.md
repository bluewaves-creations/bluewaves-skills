# Athena Plugin

Bidirectional document exchange with the [Athena](https://athena.bluewaves.boutique) note-taking app. Process `.athenabrief` research packages exported from Athena and create `.athena` import packages to send notes back.

## Installation

```bash
/plugin install athena@bluewaves-skills
```

## Prerequisites

- **Python 3.8+** (stdlib only, no additional packages required)

## Skills

| Skill | Description |
|-------|-------------|
| `athena-work` | Process `.athenabrief` research packages with progressive disclosure and zero-instruction support |
| `athena-package` | Create validated `.athena` import packages with manifest, notes, aurora tags, and assets |

## Usage Examples

### Process a research brief

Upload a `.athenabrief` file to Claude or provide the path:

```
"Here's my research brief — summarize the key findings"
"Process this athenabrief and create action items"
"What's in this research package?"
```

The athena-work skill reads the brief progressively (brief.md first, then summaries, then full notes only when needed) and packages results automatically using athena-package.

### Create notes for Athena

Ask Claude to create notes and package them:

```
"Package these meeting notes for Athena"
"Create a research summary and send it to Athena"
"Turn this conversation into Athena notes"
```

### Zero-instruction processing

The brief itself contains all the context needed. Upload without instructions:

```
"[uploads quarterly-review.athenabrief]"
```

Claude reads the research objective from the brief, processes accordingly, and packages results.

### End-to-end workflow

```
User: [uploads q1-strategy.athenabrief]
Claude: Reads brief → identifies 5 notes about Q1 strategy
        → synthesizes executive summary + action items
        → packages as research-output.athena
User: Imports research-output.athena into Athena
```

## Workflow

```
                    .athenabrief                          .athena
  Athena ──export──► [athena-work] ──process──► [athena-package] ──import──► Athena
                    (progressive                (validate → fix
                     disclosure)                 → create ZIP)
```

## Commands

| Command | Description |
|---------|-------------|
| `/athena:inspect-package <path>` | Inspect contents of a `.athenabrief` or `.athena` package |
| `/athena:validate-package <path>` | Validate a `.athena` package against the import spec |

## Aurora Tags Reference

Every note in an `.athena` package requires an aurora energy tag:

| Tag | Use For |
|-----|---------|
| `commitments` | Obligations, promises, deadlines |
| `focus` | Deep work, projects, concentration |
| `ops` | Operations, processes, recurring tasks |
| `collab` | Collaboration, meetings, shared work |
| `life` | Personal, wellbeing, non-work |
| `explore` | Research, ideas, exploration |
| `archive` | Completed/archived items |
| `library` | Reference material, resources |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Python 3 required" | Install Python 3.8+ from python.org or `brew install python3` |
| Validation errors | Run `/athena:validate-package` for specific error messages and fixes |
| Import fails in Athena | Check that all notes have valid aurora tags and the header format |
| Missing notes after import | Check manifest.json lists all note files correctly |
| Broken cross-references | Ensure referenced `notes/*.md` and `assets/*` files exist in package |

## License

MIT
