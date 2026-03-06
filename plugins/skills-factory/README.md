# Skills Factory

Complete skill lifecycle platform: creation, evaluation, benchmarking, description optimization, quality gates, packaging, and cross-platform conversion for Agent Skills.

## Skills

| Skill | Description |
|-------|-------------|
| `skill-shaper` | Guide for creating effective Agent Skills with category-aware templates, bundled scripts, references, and eval bootstrapping |
| `skill-eval` | Evaluate, benchmark, and optimize skills through automated testing with two-tier grading, token budget analysis, and description optimization |
| `gemini-gem-converter` | Convert Agent Skills to Gemini Gems format with platform constraint awareness |
| `openai-gpt-converter` | Convert Agent Skills to Custom GPT format with 8K instruction limit strategies |

## Commands

| Command | Description |
|---------|-------------|
| `/init-skill` | Scaffold a new skill directory from template (supports `--category`) |
| `/validate-skill` | Validate a skill folder using quick_validate.py |
| `/package-skill` | Package a skill into a distributable `.skill` ZIP file |
| `/eval-skill` | Run evaluation suite against a skill |
| `/benchmark-skill` | Aggregate benchmark statistics from eval runs |
| `/optimize-description` | Run automated description optimization loop |
| `/review-evals` | Open interactive HTML eval viewer |
| `/ship-skill` | Full pipeline: validate, eval, quality-gate, package |

## Installation

```bash
/plugin install skills-factory@bluewaves-skills
```

## Prerequisites

- **skill-shaper**: `skills-ref` recommended for validation (`uv pip install -e deps/agentskills/skills-ref/`). Fallback: PyYAML (`uv pip install pyyaml`) for `quick_validate.py`.
- **skill-eval**: `claude` CLI required for trigger evaluation (`run_eval.py`). PyYAML recommended for eval files.
- **gemini-gem-converter**: No dependencies (knowledge-only skill)
- **openai-gpt-converter**: No dependencies (knowledge-only skill)

## Usage

```
# Create a new skill with category-aware template
"Help me create a skill for processing CSV files"
/init-skill my-skill --category workflow

# Evaluate and optimize a skill
"Test my pdf-rotation skill and optimize its description"
/eval-skill plugins/my-plugin/skills/my-skill

# Ship a skill (validate → eval → quality gate → package)
/ship-skill plugins/my-plugin/skills/my-skill

# Convert a skill to other platforms
"Convert my skill to a Gemini Gem"
"Adapt this skill for use as a Custom GPT"
```

## Skill Development Workflow

1. **Create** — `skill-shaper` guides intent capture, planning, and SKILL.md authoring
2. **Scaffold evals** — `eval_scaffold.py` auto-generates test cases from trigger queries
3. **Test** — `eval_workspace.py run` executes two-tier grading (programmatic + agent)
4. **Review** — `generate_review.py` produces interactive HTML viewer
5. **Optimize** — `run_loop.py` iterates description improvements with train/test split
6. **Ship** — `/ship-skill` validates, evaluates, quality-gates, and packages

## Key Features

- **Two-tier grading** — Programmatic checks first (0 tokens), agent grading only for subjective assertions. Saves 60-80% grading tokens.
- **Token budget analysis** — Level 1/2/3 context cost breakdown with optimization recommendations.
- **Category-aware templates** — Document creation, workflow, MCP enhancement, or generic scaffolding.
- **Regression testing** — Pin baselines and detect PASS→FAIL transitions.
- **Description optimization** — Train/test split with iterative improvement loop.
- **Blind A/B comparison** — Comparator + analyzer agents for objective skill comparison.
