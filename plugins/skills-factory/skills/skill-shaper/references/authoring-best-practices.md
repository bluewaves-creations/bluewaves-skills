# Authoring Best Practices

Principles, patterns, and checklist for writing effective skills.

## Table of Contents

1. Pushy Descriptions
2. Explain the Why
3. Writing Patterns
4. Keep Prompts Lean
5. Generalize over Overfit
6. Extract Repeated Work
7. Pre-Distribution Checklist

---

## 1. Pushy Descriptions

Skills tend to undertrigger — Claude doesn't use them when it should. Combat this with assertive, territory-claiming descriptions.

**Weak vs Strong examples:**

| Weak | Strong |
|------|--------|
| "A tool for PDF creation" | "Generate production-quality PDF documents from markdown. Use this skill whenever the user wants to create a PDF, render markdown to PDF, generate a report, or produce any formatted document output." |
| "Helps with data analysis" | "Analyze datasets, generate statistical summaries, and create visualizations. Use this skill whenever the user mentions data analysis, CSV processing, statistical testing, data visualization, pivot tables, or wants to explore any kind of structured data." |
| "Image generation using fal.ai" | "Generate images from text prompts using fal.ai. Use this skill whenever the user asks to create, generate, or make an image from a text description, wants AI-generated artwork, needs a visual for a project, or mentions image generation in any context." |
| "Code review tool" | "Review code for quality, security, and best practices. Use this skill whenever the user asks for a code review, wants feedback on their code, mentions code quality, asks about security vulnerabilities, or wants to improve existing code." |
| "Converts documents" | "Convert documents between formats (markdown, PDF, DOCX, EPUB). Use this skill whenever the user needs to transform a document from one format to another, export content, or generate a different file type from existing text." |

**Guidelines:**
- Start with what it does (imperative form)
- Follow with "Use this skill whenever..." listing specific triggers
- Include adjacent keywords users might mention
- Cover edge cases (indirect mentions, partial matches)
- 100-200 words, max 1024 characters

---

## 2. Explain the Why

Today's LLMs are smart. They have good theory of mind. When given reasoning, they can go beyond rote instructions. Heavy-handed MUSTs are a yellow flag — reframe as reasoning.

**Before:** "ALWAYS use the brand font. NEVER use system fonts."
**After:** "The brand font (Inter) maintains visual consistency across all documents. System fonts would break the brand identity and look unprofessional to clients."

**Before:** "MUST validate output before returning."
**After:** "Validation catches formatting errors invisible in the editor but that break the final PDF — run validate.py after every render."

**Before:** "NEVER exceed 500 lines in SKILL.md."
**After:** "SKILL.md shares the context window with everything else. Every line costs tokens. Move detailed content to reference files that load only when needed."

**Principle:** Give Claude the context you'd give a smart colleague. Explain reasoning so they make good decisions in edge cases you didn't anticipate.

---

## 3. Writing Patterns

### Imperative Form
- "Extract text from the PDF" (not "The skill extracts text")
- "Validate the output against the schema" (not "Output should be validated")

### Output Templates
```markdown
## Report Structure
ALWAYS use this exact template:
# [Title]
## Executive Summary
## Key Findings
## Recommendations
```

### Examples Pattern
```markdown
## Commit Message Format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### Visual Output Pattern
For skills producing visual results:
```markdown
## Reviewing Results
1. Generate self-contained HTML with embedded CSS and data
2. Write to /tmp/<skill-name>-output.html
3. Open: open /tmp/<skill-name>-output.html
```

### Structured Data Pattern
```markdown
## Output Schema
Write results as JSON:
{ "status": "success|failure", "items": [...], "summary": "..." }
```

---

## 4. Keep Prompts Lean

**Default assumption:** Claude is already very smart. Only add context it doesn't have.

**Challenge every paragraph:** "Does Claude need this?" and "Does this justify its token cost?"

**Remove dead weight:** Cut anything that's obvious to a capable AI, repeated, or only relevant to edge cases (move those to references).

**Measure:** Run `token_budget.py --skill-path <dir>` to see per-section token costs.

**Prefer examples over explanations:** 3 input/output pairs teach better than 10 paragraphs.

---

## 5. Generalize over Overfit

The skill will be used on thousands of prompts. Changes must help the category, not just one test case.

**Red flags for overfitting:**
- Rules that only make sense for one specific test case
- Increasingly specific constraints that limit flexibility
- "If the user mentions X, always do Y" (too narrow)

**Better:** Use general principles and patterns, not hardcoded responses.

---

## 6. Extract Repeated Work

Read transcripts from test runs. If subagents independently wrote similar helper scripts:
- All 3 runs created `parse_csv.py` → Bundle in `scripts/`
- All runs followed same 5-step sequence → Document as workflow
- All runs read same reference data → Include in `references/`

Use `extract_scripts.py` from skill-eval to identify repeated patterns automatically.

---

## 7. Pre-Distribution Checklist

### Before starting
- [ ] Clear success criteria (trigger queries, output quality)
- [ ] Category identified (document, workflow, MCP)
- [ ] Reusable contents planned (scripts, references, assets)

### During development
- [ ] Description is pushy and territory-claiming
- [ ] Instructions explain the why, not just the what
- [ ] SKILL.md under 500 lines
- [ ] Reference files linked with "when to read" guidance
- [ ] Scripts tested with realistic inputs
- [ ] No TODO markers in content

### Before distribution
- [ ] Passes `skills-ref validate`
- [ ] 5+ trigger queries succeed
- [ ] 3+ negative queries don't trigger
- [ ] Token budget reasonable (`token_budget.py`)
- [ ] All referenced files exist
- [ ] Edge cases tested

### After distribution
- [ ] Monitor for under/overtriggering
- [ ] Monitor context bloat
- [ ] Iterate based on real usage feedback
