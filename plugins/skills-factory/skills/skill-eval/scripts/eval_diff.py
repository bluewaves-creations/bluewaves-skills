#!/usr/bin/env python3
"""Terminal-native iteration comparison between eval runs.

Compares skill snapshots, grading results, and token budgets between runs
with colored ANSI output for regression detection.

Usage:
    eval_diff.py --workspace <.skill-eval/> [--run-a N] [--run-b M]
"""

import argparse
import json
import sys
from pathlib import Path


# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def load_grading(run_dir: Path) -> dict:
    """Load grading.json from a run directory."""
    path = run_dir / "grading.json"
    if path.exists():
        return json.loads(path.read_text())
    # Also check nested results
    path = run_dir / "results.json"
    if path.exists():
        return json.loads(path.read_text())
    return None


def diff_snapshots(dir_a: Path, dir_b: Path) -> list:
    """Compare SKILL.md snapshots between runs."""
    snap_a = dir_a / "skill-snapshot.md"
    snap_b = dir_b / "skill-snapshot.md"

    if not snap_a.exists() or not snap_b.exists():
        return ["  Snapshots not available for comparison"]

    lines_a = snap_a.read_text().splitlines()
    lines_b = snap_b.read_text().splitlines()

    if lines_a == lines_b:
        return [f"  {DIM}SKILL.md unchanged{RESET}"]

    output = []
    output.append(f"  {BOLD}SKILL.md changes:{RESET}")
    output.append(f"    Lines: {len(lines_a)} -> {len(lines_b)}")

    # Show section-level diff (headings)
    headings_a = {l.strip() for l in lines_a if l.startswith("#")}
    headings_b = {l.strip() for l in lines_b if l.startswith("#")}

    added = headings_b - headings_a
    removed = headings_a - headings_b

    for h in sorted(added):
        output.append(f"    {GREEN}+ {h}{RESET}")
    for h in sorted(removed):
        output.append(f"    {RED}- {h}{RESET}")

    return output


def diff_grading(grading_a: dict, grading_b: dict) -> list:
    """Compare grading results between runs."""
    output = []

    if not grading_a or not grading_b:
        output.append("  Grading data incomplete for comparison")
        return output

    sum_a = grading_a.get("summary", {})
    sum_b = grading_b.get("summary", {})

    rate_a = sum_a.get("pass_rate", 0)
    rate_b = sum_b.get("pass_rate", 0)
    delta = rate_b - rate_a

    color = GREEN if delta > 0 else RED if delta < 0 else DIM
    arrow = "+" if delta > 0 else ""
    output.append(
        f"  Pass rate: {rate_a:.0%} -> {color}{rate_b:.0%} ({arrow}{delta:.0%}){RESET}"
    )

    # Per-expectation comparison
    exps_a = {e["text"]: e["passed"] for e in grading_a.get("expectations", [])}
    exps_b = {e["text"]: e["passed"] for e in grading_b.get("expectations", [])}

    regressions = []
    improvements = []

    for text, passed_b in exps_b.items():
        passed_a = exps_a.get(text)
        if passed_a is True and passed_b is False:
            regressions.append(text)
        elif passed_a is False and passed_b is True:
            improvements.append(text)

    if regressions:
        output.append(f"  {RED}{BOLD}REGRESSIONS ({len(regressions)}):{RESET}")
        for r in regressions:
            output.append(f"    {RED}PASS -> FAIL: {r}{RESET}")

    if improvements:
        output.append(f"  {GREEN}Improvements ({len(improvements)}):{RESET}")
        for imp in improvements:
            output.append(f"    {GREEN}FAIL -> PASS: {imp}{RESET}")

    return output


def diff_timing(dir_a: Path, dir_b: Path) -> list:
    """Compare timing data between runs."""
    output = []

    timing_a_path = dir_a / "timing.json"
    timing_b_path = dir_b / "timing.json"

    if not timing_a_path.exists() or not timing_b_path.exists():
        return []

    timing_a = json.loads(timing_a_path.read_text())
    timing_b = json.loads(timing_b_path.read_text())

    tokens_a = timing_a.get("total_tokens", 0)
    tokens_b = timing_b.get("total_tokens", 0)
    if tokens_a and tokens_b:
        delta = tokens_b - tokens_a
        color = GREEN if delta < 0 else RED if delta > 0 else DIM
        output.append(f"  Tokens: {tokens_a:,} -> {color}{tokens_b:,} ({delta:+,}){RESET}")

    dur_a = timing_a.get("total_duration_seconds", 0)
    dur_b = timing_b.get("total_duration_seconds", 0)
    if dur_a and dur_b:
        delta = dur_b - dur_a
        color = GREEN if delta < 0 else RED if delta > 0 else DIM
        output.append(f"  Duration: {dur_a:.1f}s -> {color}{dur_b:.1f}s ({delta:+.1f}s){RESET}")

    return output


def run_diff(workspace: Path, run_a: str = None, run_b: str = None) -> int:
    """Execute the diff comparison."""
    workspace = Path(workspace)
    runs_dir = workspace / "runs"

    if not runs_dir.exists():
        print("No runs directory found.")
        return 1

    existing = sorted([d.name for d in runs_dir.iterdir() if d.is_dir() and d.name.isdigit()])

    if len(existing) < 2 and not (run_a and run_b):
        print("Need at least 2 runs to compare.")
        return 1

    if not run_b:
        run_b = existing[-1]
    if not run_a:
        run_a = existing[-2]

    dir_a = runs_dir / run_a
    dir_b = runs_dir / run_b

    print(f"{BOLD}Eval Diff: Run {run_a} vs Run {run_b}{RESET}")
    print(f"{'=' * 50}")

    # Skill snapshot diff
    print(f"\n{CYAN}Skill Changes:{RESET}")
    for line in diff_snapshots(dir_a, dir_b):
        print(line)

    # Grading diff
    grading_a = load_grading(dir_a)
    grading_b = load_grading(dir_b)

    print(f"\n{CYAN}Grading Results:{RESET}")
    for line in diff_grading(grading_a, grading_b):
        print(line)

    # Timing diff
    timing_lines = diff_timing(dir_a, dir_b)
    if timing_lines:
        print(f"\n{CYAN}Performance:{RESET}")
        for line in timing_lines:
            print(line)

    print()
    return 0


def main():
    parser = argparse.ArgumentParser(description="Terminal-native eval diff")
    parser.add_argument("--workspace", required=True, help="Path to .skill-eval/ directory")
    parser.add_argument("--run-a", help="First run ID (default: second latest)")
    parser.add_argument("--run-b", help="Second run ID (default: latest)")
    args = parser.parse_args()

    return run_diff(args.workspace, args.run_a, args.run_b)


if __name__ == "__main__":
    sys.exit(main())
