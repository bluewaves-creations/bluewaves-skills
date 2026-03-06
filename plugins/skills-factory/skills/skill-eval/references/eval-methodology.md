# Eval Methodology

Philosophy, iteration guidance, multi-environment support, and advanced patterns for skill evaluation.

## Table of Contents

1. Core Philosophy
2. Two-Tier Grading Rationale
3. Assertion Design
4. Claims Extraction
5. Eval Feedback Loop
6. Iteration Guidance
7. Multi-Environment Workflow
8. Subagent Patterns
9. Extended Thinking
10. When to Stop

---

## 1. Core Philosophy

**Measure before optimizing.** Run evals before changing the skill. Without a baseline, you can't tell if changes helped.

**Generalize over overfit.** You're testing on a handful of queries, but the skill will be used on thousands. If a fix only works for one test case, it's an overfit. Prefer changes that improve the category, not just the example.

**Discriminate, don't rubber-stamp.** An assertion that trivially passes is worse than no assertion. Every check should distinguish good output from bad. If it passes for both a correct and a broken output, it wastes everyone's time.

---

## 2. Two-Tier Grading Rationale

**Tier 1 (programmatic):** Zero token cost, instant results. Catches structural failures before spending tokens on agent grading. Check types: file_exists, regex, json_valid, yaml_valid, exit_code, contains, not_contains, line_count_range, file_size_range.

**Tier 2 (agent-graded):** Only runs if ALL Tier 1 checks pass. Uses the grader agent (references/agents/grader.md) to evaluate subjective assertions with evidence.

**Token savings:** When a Tier 1 check fails (missing file, wrong format), Tier 2 is skipped entirely. For typical eval suites, this saves 60-80% of grading tokens by catching obvious failures early.

**When to use which:**
- Tier 1: Anything verifiable by pattern matching — file existence, content presence, format validity
- Tier 2: Subjective quality, completeness, correctness of complex output, nuanced behavior

---

## 3. Assertion Design

**Objectively verifiable.** Each assertion should have a clear pass/fail boundary. "Output is well-formatted" is ambiguous. "Output contains a table with headers Name, Date, Amount" is verifiable.

**Descriptive names.** Assertions appear in the viewer and reports. They should read clearly: someone glancing at results should immediately understand what each one checks.

**Discriminating.** The most important quality. A discriminating assertion:
- PASSES when the skill genuinely succeeds
- FAILS when the skill fails or produces garbage
- Does NOT pass trivially (e.g., checking filename existence without content)
- Does NOT pass for both correct and incorrect outputs

**Test your tests:** After writing assertions, mentally ask: "Would a completely wrong output also pass this?" If yes, the assertion needs work.

---

## 4. Claims Extraction

Beyond explicit assertions, the grader extracts implicit claims from outputs:

- **Factual claims:** "Processed 12 pages" — verify by counting
- **Process claims:** "Used pypdf to fill fields" — verify from transcript
- **Quality claims:** "All fields filled correctly" — evaluate against evidence

Classification: factual (checkable against data), subjective (requires judgment). Unverifiable claims are flagged separately.

This catches issues that predefined assertions miss — especially when the output contains specific numbers or makes promises about its own quality.

---

## 5. Eval Feedback Loop

The grader doesn't just grade — it critiques the evals themselves:

- **Non-discriminating assertions:** Flags assertions that trivially pass (e.g., checking file existence when both good and bad runs create the file)
- **Missing coverage:** Notes important outcomes that no assertion checks
- **Unverifiable assertions:** Assertions that can't be checked from available outputs

The `eval_feedback` field in grading.json contains these suggestions. Before improving the skill, review eval feedback first — fixing the measurement tool is higher priority than tuning what you're measuring.

---

## 6. Iteration Guidance

**Read transcripts, not just results.** The transcript shows what the skill made Claude do. Look for:
- Wasted steps (reading unnecessary files, redoing work)
- Repeated code across runs (signal to bundle as a script)
- Misunderstandings of instructions (signal to rewrite with why)

**Explain the why.** If you find yourself writing MUST or ALWAYS in all caps, reframe as reasoning. "Always validate output" becomes "Validation catches formatting errors that are invisible in the editor but break the final PDF — run validate.py after every render."

**Keep prompts lean.** After each iteration, check whether removed content actually hurt. Shorter skills that work are better than verbose skills that waste tokens on instructions Claude ignores.

**Extract repeated work.** If all test runs independently wrote similar helper scripts (e.g., all three created a `parse_csv.py`), that's a strong signal to bundle the script. Write it once, put it in `scripts/`, and tell the skill to use it.

---

## 7. Multi-Environment Workflow

### Environment Detection

1. Check `which claude` — if available, you're in **Claude Code** (full subagents + browser)
2. Check for subagent Task tools — if available, you're in **Cowork** (subagents + `--static` HTML)
3. Fallback — you're in **Claude.ai** (inline testing only)

### Claude Code

Full capabilities: spawn parallel subagents for with-skill and baseline runs, open HTML viewer in browser, run `claude -p` for trigger testing.

### Cowork

Subagents work, but no display. Use `--static <path>` for HTML viewer output. Feedback comes via file download from the viewer's "Submit All Reviews" button.

### Claude.ai

No subagents, no `claude` CLI. Run test cases inline (read the skill, follow its instructions yourself). Skip benchmarking. Focus on qualitative feedback. Description optimization requires Claude Code.

---

## 8. Subagent Patterns

**`isolation: "worktree"`** — Use for parallel benchmark runs. Each subagent gets an isolated repo copy, preventing file conflicts when multiple runs execute simultaneously.

**`background: true`** — Use for non-blocking eval execution. Launch eval runs in background, draft assertions while waiting, then collect results.

**`skills` preloading** — When spawning a test subagent, preload the skill under test so it's available in that agent's context.

---

## 9. Extended Thinking

For deep analysis passes (description improvement, benchmark analysis), the "ultrathink" keyword in the prompt enables extended thinking. This gives the model more reasoning time for:

- Generating improved descriptions with nuanced trigger coverage
- Analyzing patterns across multiple eval runs
- Identifying subtle regressions in transcript behavior

Use sparingly — extended thinking is significantly more expensive.

---

## 10. When to Stop

Stop iterating when:
- User says they're happy
- All feedback is empty (everything looks good)
- Pass rate isn't meaningfully improving between iterations
- You're making fiddly changes that only help one test case
- The skill is overfitting to specific eval queries rather than generalizing
