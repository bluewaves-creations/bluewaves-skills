# Skills Factory

Skill creation, validation, and cross-platform conversion tools for Agent Skills.

## Skills

| Skill | Description |
|-------|-------------|
| `skill-shaper` | Guide for creating effective Agent Skills with bundled scripts, references, and templates |
| `gemini-gem-converter` | Convert Agent Skills to Gemini Gems format with platform constraint awareness |
| `openai-gpt-converter` | Convert Agent Skills to Custom GPT format with 8K instruction limit strategies |

## Installation

```bash
/plugin install skills-factory@bluewaves-skills
```

## Prerequisites

- **skill-shaper**: `skills-ref` recommended for validation (`uv pip install -e deps/agentskills/skills-ref/`). Fallback: PyYAML (`uv pip install pyyaml`) for `quick_validate.py`.
- **gemini-gem-converter**: No dependencies (knowledge-only skill)
- **openai-gpt-converter**: No dependencies (knowledge-only skill)

## Usage

```
# Create a new skill
"Help me create a skill for processing CSV files"

# Convert a skill to Gemini Gem
"Convert my pdf-processor skill to a Gemini Gem"

# Convert a skill to Custom GPT
"Adapt this skill for use as a Custom GPT"
```
