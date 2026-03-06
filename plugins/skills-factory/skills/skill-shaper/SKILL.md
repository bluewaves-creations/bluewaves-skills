---
name: skill-shaper
description: >
  Guide for creating effective skills. Use when users want to create a new skill
  (or update an existing skill) that extends Claude's capabilities with
  specialized knowledge, workflows, or tool integrations. Triggers on skill
  creation, skill authoring, building a new skill, writing SKILL.md, or
  scaffolding skill directories. For testing, evaluation, and description
  optimization, see skill-eval.
allowed-tools: Bash, Read, Write
license: MIT
compatibility: skills-ref recommended (uv pip install -e deps/agentskills/skills-ref/), PyYAML as fallback
---

# Skill Shaper

A guide for creating effective skills that extend Claude's capabilities.

Your job is to figure out where the user is in this process and jump in. Maybe they have a workflow they want to capture ("turn this into a skill"). Maybe they want to create something from scratch. Maybe they have an existing skill that needs work. Be flexible — if the user doesn't want evals, skip them. Adapt your language to their technical level.

## Communication

Pay attention to cues about the user's familiarity with technical terms:
- "Evaluation" and "benchmark" are borderline OK for most users
- "JSON" and "assertion" need signals that the user knows what they mean
- When in doubt, briefly explain terms with a short definition

## Step 1: Capture Intent

Start by understanding what the user wants. The conversation may already contain a workflow to capture — check history for tools used, steps taken, corrections made.

Key questions (don't ask all at once — start with the most important):

1. **What should this skill enable Claude to do?**
2. **When should it trigger?** Collect 5+ trigger queries and 3+ negative queries (things that should NOT trigger it)
3. **What's the expected output format?**

Check available MCPs — if useful for research (searching docs, finding similar skills), research in parallel via subagents if available.

Define success criteria before moving on: trigger queries, minimum acceptable output quality.

## Step 2: Plan Reusable Contents

Identify the skill's category — this affects directory structure, testing approach, and templates:
- **Document/Asset Creation** — produces files (PDFs, images, documents)
- **Workflow Automation** — orchestrates multi-step processes
- **MCP Enhancement** — wraps external tools with specialized knowledge

See `references/skill-categories.md` for detailed guidance.

Analyze each concrete example to identify what to bundle:

| Pattern | Signal | Bundle As |
|---------|--------|-----------|
| Same code rewritten each time | PDF rotation logic | `scripts/rotate_pdf.py` |
| Same boilerplate needed | Frontend starter code | `assets/hello-world/` |
| Complex domain knowledge | API schemas, policies | `references/api_docs.md` |
| Template with variable parts | Report structure | `references/template.md` |

## Step 3: Initialize

For new skills, always run the init script:

```bash
python3 scripts/init_skill.py <skill-name> --path <directory> [--category <type>]
```

Categories: `document-creation`, `workflow`, `mcp-enhancement` (default: generic).

Each category generates a tailored SKILL.md template with relevant patterns, plus a `.skill-eval/` directory with starter eval files.

Skip this step if updating an existing skill.

## Step 4: Write the Skill

This is where the skill comes to life. Read `references/authoring-best-practices.md` before writing — it covers the principles below in depth with examples.

### Description (Most Important)

The description is the primary triggering mechanism. Make it **pushy** — assertive and territory-claiming:

**Weak:** "A tool for creating PDF documents from markdown."

**Strong:** "Generate production-quality PDF documents from markdown content with professional typography and brand-consistent styling. Use this skill whenever the user wants to create a PDF, render markdown to PDF, generate a report, produce a document, or needs any kind of formatted output from text content."

Guidelines:
- Use imperative form ("Generate...", "Process...", "Create...")
- Focus on user intent, not implementation
- List specific trigger contexts and keywords
- Include both what it does AND when to use it
- Aim for 100-200 words, max 1024 characters
- Generalize: cover the category, not just specific examples

### Body

**Explain the why.** Today's LLMs are smart. They have good theory of mind and when given a good harness can go beyond rote instructions. If you find yourself writing MUST or NEVER in all caps, reframe as reasoning:

**Before:** "ALWAYS validate output before returning."

**After:** "Validation catches formatting errors that are invisible in the editor but break the final PDF — run validate.py after every render."

**Keep prompts lean.** Challenge every paragraph: "Does this justify its token cost?" Prefer concise examples over verbose explanations. The context window is a shared resource.

**Progressive disclosure.** Keep SKILL.md body under 500 lines. Split content into reference files when approaching this limit. Each reference file should be clearly linked from SKILL.md with guidance on when to read it.

**Bundled resources:**
- `scripts/` — Deterministic code that's rewritten repeatedly. Execute without loading into context.
- `references/` — Documentation loaded as needed. Include grep patterns for large files (>10k words).
- `assets/` — Files used in output (templates, fonts, images). Not loaded into context.

See `references/output-patterns.md` for template and visual output patterns. See `references/workflows.md` for sequential, conditional, iterative, and multi-MCP patterns.

### Specification Compliance

See `references/skill-specification.md` for:
- Frontmatter constraints (name: max 64 chars, hyphen-case; description: max 1024 chars)
- Supported frontmatter fields (name, description, allowed-tools, license, compatibility, context, agent, hooks, model, user-invocable, argument-hint, disable-model-invocation)
- String substitutions ($ARGUMENTS, $N, ${CLAUDE_SESSION_ID})
- Dynamic context injection (`!`command`` preprocessing)
- Validation rules

## Step 5: Validate and Package

### Validation

**Primary:** `skills-ref validate <path/to/skill-folder>`

If not installed: `uv pip install -e deps/agentskills/skills-ref/`

**Fallback:** `python3 scripts/quick_validate.py <path/to/skill-folder>`

### Packaging

```bash
python3 scripts/package_skill.py <path/to/skill-folder> [output-dir]
```

Validates automatically, then creates a `.skill` ZIP file.

## Step 6: Test, Eval, Ship

### Quick Manual Testing

Before automated evals, do a quick sanity check:
- Try 5+ paraphrased trigger queries — does the skill activate?
- Try 3+ unrelated queries — does it stay quiet?
- Run the primary workflow end-to-end with realistic inputs
- Test at least one edge case

### Automated Evaluation

For thorough testing, use the **skill-eval** skill. It provides:
- Automated eval scaffolding from trigger queries
- Two-tier grading (programmatic + agent)
- Token budget analysis
- Regression testing with pinned baselines
- Description optimization loop with train/test split
- Interactive HTML review viewer

### Ship Pipeline

When the skill is ready: validate → eval (all checks pass, 80%+ assertions) → quality gate (under 500 lines, no TODOs, refs exist, token budget OK) → package.

See `references/distribution-guide.md` for distribution channels and positioning.

## Reference Materials

Consult these based on your needs during skill creation:

- **[references/skill-specification.md](references/skill-specification.md)** — Frontmatter constraints, naming rules, validation rules, supported fields, string substitutions, dynamic context injection
- **[references/authoring-best-practices.md](references/authoring-best-practices.md)** — Pushy descriptions (5+ examples), explain the why, writing patterns, keep prompts lean, extract repeated work, pre-distribution checklist
- **[references/workflows.md](references/workflows.md)** — Sequential, conditional, iterative, plan-validate-execute, multi-MCP, subagent delegation, visual output patterns
- **[references/output-patterns.md](references/output-patterns.md)** — Template, example, visual output, and structured data patterns
- **[references/testing-and-debugging.md](references/testing-and-debugging.md)** — Pointer to skill-eval, two-tier testing, description testing, regression testing, debugging triggers and context
- **[references/skill-categories.md](references/skill-categories.md)** — Document/asset creation, workflow automation, MCP enhancement, subagent-based skills, knowledge/reference skills, category-to-template mapping
- **[references/distribution-guide.md](references/distribution-guide.md)** — Channels, packaging formats, plugin distribution, managed settings, ship-skill pipeline, quality gate checklist
