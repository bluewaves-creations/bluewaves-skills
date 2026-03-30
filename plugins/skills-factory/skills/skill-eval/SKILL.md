---
name: skill-eval
description: >
  Evaluate, benchmark, and optimize skills through automated testing.
  Use when a skill needs trigger testing, functional testing, baseline
  comparison, description optimization, regression testing, or quality
  benchmarking. Features two-tier grading (programmatic fast-path +
  agent grading), token budget analysis, automated eval scaffolding,
  and interactive HTML reports. Use this skill whenever someone mentions
  testing a skill, evaluating skill quality, optimizing a description,
  running evals, benchmarking skill performance, or shipping a skill.
allowed-tools: Bash, Read, Write
compatibility: >
  claude CLI optional (for full-fidelity trigger testing). Description
  optimization works in-session (zero cost) or via claude CLI. Anthropic
  Python SDK optional for API-based improvement (pip install anthropic).
  PyYAML recommended for eval files.
license: MIT
---

# Skill Eval

Eval-driven development for skills: draft, scaffold evals, test, grade, review, improve, repeat.

Your job is to figure out where the user is in this process and jump in. Maybe they want to test an existing skill. Maybe they want to optimize a description. Maybe they want the full ship pipeline. Be flexible — if the user doesn't want evals, skip them.

## Environment Detection

Before starting, detect the environment:

1. **Claude Code** — check `which claude`. Full capabilities: subagents, browser, `claude -p` for trigger testing.
2. **Cowork** — check for Task tools. Subagents work, but no display. Use `--static <path>` for HTML viewer output.
3. **Claude.ai** — fallback. Inline testing only. Description optimization works in-session (no CLI needed). Skip benchmarking.

Adapt workflows below based on detected environment.

## Quick Start

Three steps to evaluate any skill:

1. **Scaffold evals** from the skill's trigger queries:
   ```bash
   python3 scripts/eval_scaffold.py --skill-path <skill-dir>
   ```

2. **Initialize and run** the workspace:
   ```bash
   python3 scripts/eval_workspace.py init <skill-dir>
   python3 scripts/eval_workspace.py run <skill-dir>
   ```

3. **Review results** in the interactive viewer:
   ```bash
   python3 scripts/generate_review.py <skill-dir>/.skill-eval --skill-name <name>
   ```

## Eval Workspace

The `.skill-eval/` directory lives inside the skill. It contains sequential numbered runs, eval definitions, and a manifest tracking history.

```
.skill-eval/
├── manifest.json          # Tracks all runs, pinned baseline
├── evals/                 # .eval.yaml test case files
│   ├── trigger-query-1.eval.yaml
│   └── negative-test.eval.yaml
└── runs/
    ├── 001/               # Sequential run directories
    │   ├── outputs/       # Files created during eval
    │   ├── transcript.md  # Execution transcript
    │   ├── grading.json   # Tier 1 + Tier 2 grades
    │   ├── timing.json    # Tokens, duration (capture immediately!)
    │   ├── metrics.json   # Tool calls, errors, file counts
    │   └── skill-snapshot.md  # SKILL.md at time of run
    └── 002/
```

**Commands:**
- `eval_workspace.py init <skill>` — Create workspace
- `eval_workspace.py run <skill>` — Create next run dir with snapshot
- `eval_workspace.py compare <skill> [--run-a N] [--run-b M]` — Compare runs
- `eval_workspace.py clean <skill> --keep-last N` — Prune old runs
- `eval_workspace.py pin <skill> [run_id]` — Pin regression baseline
- `eval_workspace.py regress <skill>` — Compare against pinned baseline

For benchmark mode, use nested layout: `runs/NNN/eval-E/{with_skill,without_skill}/run-R/`

## Defining Test Cases

Test cases are `.eval.yaml` files in `.skill-eval/evals/`. Each has two tiers:

**Tier 1 — Checks (programmatic, zero tokens):**
```yaml
checks:
  - type: file_exists
    target: "output.pdf"
  - type: contains
    target: "output.txt"
    expected: "Summary"
```

Check types: `file_exists`, `regex`, `json_valid`, `yaml_valid`, `exit_code`, `contains`, `not_contains`, `line_count_range`, `file_size_range`.

**Tier 2 — Assertions (agent-graded):**
```yaml
assertions:
  - "The report includes a revenue trend chart"
  - "The summary table has correct quarterly totals"
```

Assertions run ONLY if all Tier 1 checks pass. This saves 60-80% of grading tokens by catching obvious failures early.

See `references/eval-format.md` for the complete format spec with category-specific examples.

## Two-Tier Grading

Run the grader on eval results:

```bash
python3 scripts/eval_grader.py \
  --eval-file <.eval.yaml> \
  --outputs-dir <outputs/> \
  --transcript <transcript.md> \
  --metrics <metrics.json> \
  --timing <timing.json>
```

**Tier 1:** Runs all programmatic checks instantly. If any fail, Tier 2 is skipped entirely.

**Tier 2:** Spawns a grader agent using `references/agents/grader.md` as system prompt. The grader:
- Evaluates each assertion with evidence (PASS/FAIL)
- Extracts and verifies implicit claims from output
- Reads executor's user_notes from metrics.json
- Critiques eval quality (flags non-discriminating assertions)
- Outputs grading.json with all fields per `references/schemas.md`

## Running Evaluations

### Trigger Testing

Test whether the skill activates for realistic queries:

```bash
python3 scripts/run_eval.py \
  --eval-set <queries.json> \
  --skill-path <skill-dir> \
  --runs-per-query 3 \
  --timeout 30
```

### Full Evaluation (with subagents)

For each test case, spawn two subagents in the same turn:

1. **With-skill run:** Execute the eval prompt with the skill loaded, save outputs
2. **Baseline run:** Same prompt, no skill (or old skill version)

**Critical:** When subagent tasks complete, the notification includes `total_tokens` and `duration_ms`. Save to timing.json IMMEDIATELY — this data is NOT persisted elsewhere.

Capture execution metrics (tool_calls, errors, user_notes) from the executor into metrics.json.

## Reviewing Results

### Terminal Diff

Quick comparison between runs:
```bash
python3 scripts/eval_diff.py --workspace <.skill-eval/>
```
Shows: SKILL.md section changes, pass/fail deltas, regressions (PASS→FAIL flagged prominently), timing changes.

### Interactive HTML Viewer

Deep review with Outputs + Benchmark tabs:
```bash
python3 scripts/generate_review.py <workspace> \
  --skill-name <name> \
  --benchmark <benchmark.json>
```

For headless/Cowork: add `--static <output.html>`. For iteration comparison: add `--previous-workspace <prev>`.

Wait for user feedback before improving the skill.

## Token Budget Analysis

Understand the skill's context cost:
```bash
python3 scripts/token_budget.py --skill-path <skill-dir>
```

Reports three levels:
- **Level 1 (metadata):** Name + description tokens (always loaded)
- **Level 2 (body):** Per-section token breakdown (loaded on trigger)
- **Level 3 (references):** Per-file token cost (loaded on demand)

Flags heavy sections and recommends extraction to references.

## Improving the Skill

After reviewing results and user feedback:

1. **Generalize from feedback** — changes should help the category, not just one test case. Avoid overfitty constraints.
2. **Explain the why** — reframe MUSTs as reasoning. Theory of mind over rigid instructions.
3. **Keep prompts lean** — remove content that isn't pulling its weight. Read transcripts to spot wasted work.
4. **Extract repeated work** — if all test runs wrote similar scripts, bundle them:
   ```bash
   python3 scripts/extract_scripts.py \
     --transcripts ".skill-eval/runs/*/transcript.md" \
     --output-dir candidates/
   ```

Review eval feedback in grading.json (`eval_feedback.suggestions`) before improving — fixing the measurement is higher priority than tuning the skill.

## Regression Testing

Pin a known-good baseline, then compare future runs against it:

```bash
# Pin current run
python3 scripts/eval_workspace.py pin <skill-dir>

# After making changes, check for regressions
python3 scripts/eval_workspace.py regress <skill-dir>
```

The regression check compares pass/fail per expectation and flags any PASS→FAIL transitions prominently.

## Description Optimization

Optimize the skill's description for better triggering accuracy. Three approaches from cheapest to most thorough.

### Step 1: Generate trigger queries

Create 20 realistic queries — mix of should-trigger (8-10) and should-not-trigger (8-10). Save as JSON:
```json
[
  {"query": "realistic user prompt with detail", "should_trigger": true},
  {"query": "near-miss that shares keywords", "should_trigger": false}
]
```

Queries should be substantive (not "read this file"), include detail (file paths, context), and test the boundary (near-misses for negatives).

### Step 2: Review with user

Present queries using the HTML editor:
1. Read `assets/eval_review.html`
2. Replace `__EVAL_DATA_PLACEHOLDER__` with the JSON array
3. Replace `__SKILL_NAME_PLACEHOLDER__` and `__SKILL_DESCRIPTION_PLACEHOLDER__`
4. Write to temp file, open in browser
5. User edits and exports `eval_set.json`

### Step 3: Run optimization

Three modes — pick based on your environment and cost tolerance:

#### In-Session (zero external cost — preferred)

Run everything within the current conversation. No subprocess spawning, no API calls. Uses the host subscription with negligible overhead.

1. Generate trigger simulation prompt:
   ```bash
   python3 scripts/sim_trigger.py --prompt-only \
     --skill-path <skill-dir> --eval-set <eval_set.json>
   ```
2. Feed the prompt to a Haiku subagent (Claude Code: `Agent(model: haiku)`) or evaluate inline (Claude.ai)
3. Parse results:
   ```bash
   python3 scripts/sim_trigger.py --parse \
     --skill-name <name> --eval-set <eval_set.json> --response <response-file>
   ```
4. Analyze failures inline — identify which queries failed and why
5. Generate improvement prompt:
   ```bash
   python3 scripts/improve_description.py --prompt-only \
     --eval-results <results.json> --skill-path <skill-dir>
   ```
6. Improve the description yourself — you ARE the model, reason about it directly
7. Update SKILL.md frontmatter with the new description
8. Repeat steps 1-7 until convergence or max iterations

#### Economical (minimal subprocess calls)

```bash
python3 -m scripts.run_loop --eval-set <eval_set.json> \
  --skill-path <skill-dir> --economical
```

Uses simulated trigger testing (one batched Haiku call per iteration) and CLI-based improvement. ~5 lightweight `claude -p` calls per iteration instead of 60+. No API key needed.

#### Full Fidelity (for final validation)

```bash
python3 -m scripts.run_loop --eval-set <eval_set.json> \
  --skill-path <skill-dir> --model <model-id> --max-iterations 5
```

Real trigger testing via `claude -p` (N queries × 3 runs × N iterations). Use after in-session or economical optimization has converged. Optionally add `--use-api` for Anthropic API improvement with extended thinking.

### Step 4: Apply result

Take `best_description` from the output and update SKILL.md frontmatter.

## Advanced: Blind Comparison

For rigorous A/B comparison between skill versions:

1. **Run two versions in parallel** — each gets the same eval prompts
2. **Randomly assign as A/B** — prevents order bias
3. **Spawn comparator agent** with `references/agents/comparator.md` — generates task-specific rubric (content: correctness/completeness/accuracy + structure: organization/formatting/usability, 1-5 scale), scores both, picks winner → comparison.json
4. **Spawn analyzer agent** with `references/agents/analyzer.md` — reads both skills + transcripts + comparison, identifies winner strengths + loser weaknesses + prioritized improvements → analysis.json

This is optional and requires subagents. The human review loop is usually sufficient.

## Ship Pipeline

One-command quality gate + packaging:

1. **Validate** — `skills-ref validate` (or `quick_validate.py`)
2. **Eval** — Run full eval suite. All Tier 1 checks must pass, 80%+ Tier 2 assertions
3. **Quality gate:**
   - SKILL.md under 500 lines
   - No TODO markers in content
   - All referenced files exist
   - Token budget under threshold
4. **Package** — Generate `.skill` file via `package_skill.py`
5. **Summary card** — Report: skill name, version, pass rate, token budget, package size

## Reference Materials

Consult these based on your needs:

- **[references/schemas.md](references/schemas.md)** — All JSON schemas (eval, grading, benchmark, comparison, analysis, manifest)
- **[references/eval-methodology.md](references/eval-methodology.md)** — Philosophy, two-tier rationale, iteration guidance, multi-environment support, subagent patterns, extended thinking
- **[references/eval-format.md](references/eval-format.md)** — .eval.yaml specification, check types reference, category-specific recommendations
- **[references/agents/grader.md](references/agents/grader.md)** — Grader agent: 8-step process for assertions, claims, eval critique
- **[references/agents/comparator.md](references/agents/comparator.md)** — Blind A/B comparison with task-specific rubrics
- **[references/agents/analyzer.md](references/agents/analyzer.md)** — Post-hoc analysis + benchmark pattern surfacing
