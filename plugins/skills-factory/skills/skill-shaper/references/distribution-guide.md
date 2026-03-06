# Distribution Guide

Packaging, distribution channels, and positioning for skills.

## Distribution Channels

### Claude.ai Upload

Users upload `.skill` or ZIP files via Settings > Capabilities.

**Best for:** Personal skills, prototyping, sharing with individuals.
**Limitations:** Manual, no version management, one user at a time.

### Claude Code Plugin Marketplace

Skills distributed as part of a plugin.

**Best for:** Teams, curated collections, skills bundled with commands and hooks.
**Process:** Structure within plugin, register in `marketplace.json`, install via `/plugin install`.
**Advantages:** Version management, bundled dependencies, marketplace discovery.

### Plugin Distribution

For skills that are part of a plugin ecosystem:

1. Create plugin directory with `.claude-plugin/plugin.json`
2. Place skills in `skills/<skill-name>/` directories
3. Register in marketplace `marketplace.json`
4. Users install: `/plugin marketplace add <url>` then `/plugin install <name>`

### Managed Settings (Enterprise)

Enterprise deployments can push skills via managed settings:

- Skills installed at the organization level
- Priority: enterprise > personal > project > plugin
- Useful for company-wide standards, compliance tools, internal workflows

### API / SDK Usage

Attach skills programmatically via `container.skills` in API calls.

**Best for:** Automated pipelines, applications using Claude as backend.

### GitHub Hosting

Host in a repository for sharing and collaboration.

**Best for:** Open-source skills, community contributions.

## Packaging Formats

### `.skill` ZIP File

Standard portable format. Created by `package_skill.py`:

```bash
python3 scripts/package_skill.py <skill-dir> [output-dir]
```

Structure inside:
```
skill-name.skill (ZIP)
└── skill-name/
    ├── SKILL.md
    ├── scripts/
    ├── references/
    └── assets/
```

### Directory (for plugins)

Unpackaged skill directory on the filesystem. Used within plugins and during development.

### Format Selection

| Scenario | Format |
|----------|--------|
| Sharing with a colleague | `.skill` file |
| Publishing to marketplace | Directory within plugin |
| API integration | Directory (by path) |
| Open-source | GitHub repository |
| Active development | Local directory |

## Ship Pipeline

The recommended distribution workflow (via skill-eval's ship command):

1. **Validate** — `skills-ref validate` (format compliance)
2. **Eval** — Run full eval suite (all Tier 1 checks pass, 80%+ Tier 2)
3. **Quality gate:**
   - SKILL.md under 500 lines
   - No TODO markers
   - All referenced files exist
   - Token budget under threshold
4. **Package** — Generate `.skill` file
5. **Summary card** — Skill name, pass rate, token budget, package size

## Quality Gate Checklist

Before shipping:
- [ ] `skills-ref validate` passes
- [ ] All Tier 1 eval checks pass
- [ ] 80%+ Tier 2 assertions pass
- [ ] SKILL.md < 500 lines
- [ ] No TODO markers in content
- [ ] All referenced files exist
- [ ] Token budget reasonable
- [ ] Description < 1024 chars

## Positioning

### Lead with the Problem

**Weak:** "Uses pdfplumber to extract text from PDFs"
**Strong:** "Turn any PDF into clean, structured text — handles scans, tables, and forms"

### Before/After Examples

```
Without skill: Claude writes extraction code from scratch, misses tables
With skill: Optimized pipeline, handles tables and forms, validates output
```

### Scope Clarity

```
Handles: Text extraction, table extraction, form filling
Does NOT handle: PDF creation (see pdf-factory), image extraction
```

### Target Audience

- **Developers:** API details, configuration, script interfaces
- **End users:** What to ask Claude, example queries
- **Teams:** Consistency, shared workflows, integration
