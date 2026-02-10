# Contributing to Bluewaves Skills

Thank you for your interest in contributing to Bluewaves Skills!

## Adding a New Plugin

### 1. Create the Plugin Structure

```
plugins/your-plugin/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── your-skill/
│       └── SKILL.md
└── README.md
```

### 2. Plugin Manifest

Create `.claude-plugin/plugin.json`:

```json
{
  "name": "your-plugin",
  "version": "1.0.0",
  "description": "Brief description of your plugin",
  "author": {
    "name": "Your Name",
    "email": "your@email.com"
  },
  "license": "MIT",
  "keywords": ["relevant", "keywords"]
}
```

### 3. Skill Definition

Create `skills/your-skill/SKILL.md` with YAML frontmatter:

```yaml
---
name: your-skill-name
description: What this skill does and when Claude should use it. Be specific about trigger conditions.
---

# Your Skill Name

## Instructions
Step-by-step guidance for Claude.

## Examples
Concrete usage examples.
```

### 4. Register in Marketplace

Add your plugin to `.claude-plugin/marketplace.json`:

```json
{
  "plugins": [
    {
      "name": "your-plugin",
      "source": "./plugins/your-plugin",
      "description": "Brief description",
      "version": "1.0.0"
    }
  ]
}
```

## Guidelines

### Skill Naming
- Use lowercase letters, numbers, and hyphens
- Maximum 64 characters
- Be descriptive: `image-generator` not `img`

### Skill Descriptions
- Maximum 1024 characters
- Include:
  - What the skill does
  - When Claude should use it (trigger conditions)
  - Key capabilities

### Documentation
- Include usage examples in SKILL.md
- Document prerequisites (API keys, dependencies)
- Provide code samples for different languages

## Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-plugin`
3. Make your changes
4. Test locally: `/plugin marketplace add ./path/to/repo`
5. Commit with descriptive message
6. Open a Pull Request

## Testing Your Plugin

```bash
# Add local marketplace for testing
/plugin marketplace add /path/to/bluewaves-skills

# Install your plugin
/plugin install your-plugin@bluewaves-skills

# Test the skill
# Ask Claude to perform tasks that should trigger your skill
```

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## Questions?

Open an issue on GitHub or contact the maintainers.
