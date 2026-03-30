#!/usr/bin/env python3
"""
Skill Initializer - Creates a new skill from template

Usage:
    init_skill.py <skill-name> --path <path> [--category <type>]

Categories:
    document-creation   - Skills that produce files (PDFs, documents, images)
    workflow            - Skills that orchestrate multi-step processes
    mcp-enhancement     - Skills that wrap external tools with knowledge
    generic             - Default template (no category specified)

Examples:
    init_skill.py my-new-skill --path skills/public
    init_skill.py pdf-creator --path skills/public --category document-creation
    init_skill.py deploy-pipeline --path skills/private --category workflow
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def title_case_skill_name(skill_name):
    """Convert hyphenated skill name to Title Case for display."""
    return ' '.join(word.capitalize() for word in skill_name.split('-'))


# --- Category-Specific Templates ---

TEMPLATES = {
    "generic": """---
name: {skill_name}
description: >
  [TODO: Assertive, territory-claiming description of what the skill does
  and when to use it. Include specific trigger contexts and keywords.
  Aim for 100-200 words. Example: "Generate X from Y. Use this skill
  whenever the user wants to Z, needs A, or mentions B."]
---

# {skill_title}

## Overview

[TODO: 1-2 sentences explaining what this skill enables]

## Workflow

[TODO: Main workflow steps. Use imperative form. Explain the WHY behind
each step, not just the what. Keep under 500 lines — move detailed
content to references/ files.]

## Resources

- **scripts/** — Executable code for deterministic/repetitive tasks
- **references/** — Documentation loaded as needed into context
- **assets/** — Files used in output (templates, fonts, images)

Delete any unneeded directories.
""",

    "document-creation": """---
name: {skill_name}
description: >
  [TODO: Generate/create [document type] from [input]. Use this skill
  whenever the user wants to create, generate, render, or produce
  [document type] output. Triggers on mentions of [keywords].]
---

# {skill_title}

## Overview

[TODO: What documents this skill creates and from what inputs]

## Workflow

### Step 1: Gather Inputs
[TODO: What the user needs to provide — content, templates, configuration]

### Step 2: Process Content
[TODO: How content is transformed — parsing, formatting, layout decisions]

### Step 3: Generate Output
[TODO: How the final document is produced — scripts, tools, templates]

### Step 4: Validate
[TODO: Quality checks before delivery — format compliance, content verification]

Validation catches errors that are invisible during creation but break the
final output. Always validate before delivering to the user.

## Output Format

[TODO: Describe the expected output format with a concrete example]

## Resources

- **scripts/** — Document generation and validation scripts
- **references/** — Format specifications, templates, style guides
- **assets/** — Template files, fonts, images, brand assets
""",

    "workflow": """---
name: {skill_name}
description: >
  [TODO: Automate/orchestrate [process]. Use this skill whenever the user
  wants to [action], needs to [action], or mentions [keywords]. Handles
  [specific scenarios].]
---

# {skill_title}

## Overview

[TODO: What workflow this skill automates and when to use it]

## Decision Tree

[TODO: How to determine which workflow path to follow based on input.
Use a simple if/then structure.]

## Workflow Steps

### Step 1: [Name]
[TODO: First step with clear inputs and outputs]

### Step 2: [Name]
[TODO: Second step — explain WHY this order matters]

### Step 3: [Name]
[TODO: Third step — include error handling guidance]

## Error Handling

[TODO: Common failure modes and how to recover. Explain the reasoning
behind each recovery strategy.]

## Resources

- **scripts/** — Automation scripts for each workflow step
- **references/** — Process documentation, API specs, configuration
""",

    "mcp-enhancement": """---
name: {skill_name}
description: >
  [TODO: Enhance [tool/service] with specialized knowledge for [domain].
  Use this skill whenever the user interacts with [tool] for [purpose],
  queries [data source], or needs [specific capability].]
---

# {skill_title}

## Overview

[TODO: What external tool this skill enhances and what knowledge it adds]

## MCP Tools

[TODO: List the MCP tools this skill works with using fully-qualified names:
ServerName:tool_name]

## Patterns

### [Pattern 1 Name]
[TODO: Common usage pattern with the MCP tool]

### [Pattern 2 Name]
[TODO: Another usage pattern — show how skill knowledge improves results]

## Domain Knowledge

[TODO: Key domain information that helps Claude use the tools effectively.
Move detailed schemas and references to references/ files.]

## Resources

- **references/** — API documentation, schemas, domain knowledge
""",

    "subagent": """---
name: {skill_name}
description: >
  [TODO: What this skill does when forked to a subagent. Use when
  the user wants to [action] in isolation, needs parallel processing,
  or mentions [keywords].]
context: fork
agent: general-purpose
---

# {skill_title}

## Task

[TODO: The task this subagent executes. Must be explicit and self-contained —
the subagent has no conversation history. Write as if briefing a colleague
who has never seen the conversation.]

## Steps

### Step 1: [Name]
[TODO: First step with clear inputs and outputs]

### Step 2: [Name]
[TODO: Second step — explain WHY this order matters]

## Output

[TODO: What the subagent returns to the parent conversation.
Be specific — the parent only sees the summary, not the full transcript.]

## Resources

- **scripts/** — Executable code for deterministic tasks
- **references/** — Documentation loaded as needed
""",
}


STARTER_EVAL_YAML = """name: trigger-test
query: "[TODO: Realistic user prompt that should trigger this skill]"
should_trigger: true
checks:
{checks}
assertions:
  - "TODO: Add assertion — what should a good output contain?"
"""

NEGATIVE_EVAL_YAML = """name: negative-test
query: "What's the weather forecast for tomorrow?"
should_trigger: false
checks: []
assertions: []
"""

CATEGORY_CHECKS = {
    "document-creation": '  - type: file_exists\n    target: "output.*"',
    "workflow": '  - type: exit_code\n    expected: 0',
    "mcp-enhancement": '  - type: contains\n    target: "transcript.md"\n    expected: "Tool:"',
    "subagent": '  - type: exit_code\n    expected: 0',
    "generic": "  []",
}


def init_skill(skill_name, path, category="generic"):
    """Initialize a new skill directory with template SKILL.md and eval bootstrapping."""
    skill_dir = Path(path).resolve() / skill_name

    if skill_dir.exists():
        print(f"Error: Skill directory already exists: {skill_dir}")
        return None

    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
    except Exception as e:
        print(f"Error creating directory: {e}")
        return None

    # Create SKILL.md from category template
    skill_title = title_case_skill_name(skill_name)
    template = TEMPLATES.get(category, TEMPLATES["generic"])
    skill_content = template.format(skill_name=skill_name, skill_title=skill_title)

    (skill_dir / "SKILL.md").write_text(skill_content)
    print(f"Created SKILL.md ({category} template)")

    # Create resource directories (empty — user fills as needed)
    for dirname in ("scripts", "references", "assets"):
        (skill_dir / dirname).mkdir(exist_ok=True)

    # Bootstrap .skill-eval/ with manifest and starter evals
    eval_dir = skill_dir / ".skill-eval"
    eval_dir.mkdir()
    (eval_dir / "runs").mkdir()
    evals_dir = eval_dir / "evals"
    evals_dir.mkdir()

    # Manifest
    manifest = {
        "skill_name": skill_name,
        "created": datetime.now(timezone.utc).isoformat(),
        "runs": [],
        "pinned_baseline": None,
    }
    (eval_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    # Starter eval files
    checks = CATEGORY_CHECKS.get(category, CATEGORY_CHECKS["generic"])
    (evals_dir / "trigger-test.eval.yaml").write_text(
        STARTER_EVAL_YAML.format(checks=checks)
    )
    (evals_dir / "negative-test.eval.yaml").write_text(NEGATIVE_EVAL_YAML)
    print(f"Created .skill-eval/ with starter evals")

    print(f"\nSkill '{skill_name}' initialized at {skill_dir}")
    print(f"Category: {category}")
    print(f"\nNext steps:")
    print(f"1. Edit SKILL.md — complete the TODOs, write a pushy description")
    print(f"2. Add scripts/, references/, assets/ as needed (delete empty dirs)")
    print(f"3. Customize .skill-eval/evals/ with realistic trigger queries")
    print(f"4. Validate: skills-ref validate {skill_dir}")

    return skill_dir


def main():
    if len(sys.argv) < 4 or sys.argv[2] != '--path':
        print("Usage: init_skill.py <skill-name> --path <path> [--category <type>]")
        print("\nCategories:")
        print("  document-creation   Skills that produce files (PDFs, documents)")
        print("  workflow            Skills that orchestrate multi-step processes")
        print("  mcp-enhancement    Skills that wrap external tools with knowledge")
        print("  subagent            Skills that fork work to isolated subagents")
        print("  generic             Default template (no category)")
        print("\nExamples:")
        print("  init_skill.py my-skill --path skills/public")
        print("  init_skill.py pdf-creator --path skills/public --category document-creation")
        sys.exit(1)

    skill_name = sys.argv[1]
    path = sys.argv[3]

    # Parse optional --category flag
    category = "generic"
    if "--category" in sys.argv:
        cat_idx = sys.argv.index("--category")
        if cat_idx + 1 < len(sys.argv):
            category = sys.argv[cat_idx + 1]

    valid_categories = ("generic", "document-creation", "workflow", "mcp-enhancement", "subagent")
    if category not in valid_categories:
        print(f"Unknown category '{category}'. Valid: {', '.join(valid_categories)}")
        sys.exit(1)

    result = init_skill(skill_name, path, category)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
