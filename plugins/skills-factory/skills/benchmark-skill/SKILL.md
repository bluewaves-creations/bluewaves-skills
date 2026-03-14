---
name: benchmark-skill
description: Aggregate benchmark results from skill evaluation runs into statistics. Use when comparing evaluation runs or analyzing skill performance trends.
allowed-tools: Bash, Read
license: MIT
compatibility: Python 3.8+. claude CLI required for evaluation runs.
---
Aggregate benchmark statistics from skill evaluation runs.

$ARGUMENTS

If `$ARGUMENTS` is provided, use it as the skill path. Otherwise, ask the user which skill to benchmark.

## Steps

1. **Locate the skill directory** and its `.skill-eval/` workspace. Resolve `$ARGUMENTS` to an absolute path if provided.

2. **Find the latest benchmark run** directory inside `.skill-eval/`.

3. **Run aggregate_benchmark.py:**
   ```bash
   python3 ${SKILL_ROOT}/../skill-shaper/scripts/aggregate_benchmark.py <benchmark-dir> --skill-name <name>
   ```

4. **Display the generated `benchmark.md` summary.**

5. **Report pass rate deltas** between with-skill and without-skill configurations.
