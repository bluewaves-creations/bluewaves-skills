#!/usr/bin/env python3
"""Two-tier grading pipeline for skill evaluations.

Tier 1 (programmatic, 0 tokens): file_exists, regex, json_valid, yaml_valid,
    exit_code, contains, not_contains, line_count_range, file_size_range
Tier 2 (agent-graded): Only invoked if ALL Tier 1 checks pass.
    Spawns grader via claude -p with references/agents/grader.md as system prompt.

Usage:
    eval_grader.py --eval-file <.eval.yaml> --outputs-dir <dir> \
        [--transcript <file>] [--metrics <file>] [--timing <file>] \
        [--grading-output <file>] [--skip-tier2]
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import load_yaml


# --- Tier 1 Check Implementations ---


def check_file_exists(outputs_dir: Path, target: str, **_) -> dict:
    """Check that a file matching the target pattern exists."""
    import fnmatch

    matches = [f for f in outputs_dir.rglob("*") if fnmatch.fnmatch(f.name, target)]
    passed = len(matches) > 0
    evidence = f"Found: {[str(m.relative_to(outputs_dir)) for m in matches]}" if passed else f"No file matching '{target}'"
    return {"type": "file_exists", "target": target, "passed": passed, "evidence": evidence}


def check_regex(outputs_dir: Path, target: str, pattern: str, **_) -> dict:
    """Check that file contents match a regex pattern."""
    target_path = outputs_dir / target
    if not target_path.exists():
        return {"type": "regex", "target": target, "pattern": pattern, "passed": False, "evidence": f"File not found: {target}"}
    content = target_path.read_text(errors="replace")
    match = re.search(pattern, content)
    passed = match is not None
    evidence = f"Matched: '{match.group()}'" if passed else f"Pattern '{pattern}' not found"
    return {"type": "regex", "target": target, "pattern": pattern, "passed": passed, "evidence": evidence}


def check_json_valid(outputs_dir: Path, target: str, **_) -> dict:
    """Check that a file contains valid JSON."""
    target_path = outputs_dir / target
    if not target_path.exists():
        return {"type": "json_valid", "target": target, "passed": False, "evidence": f"File not found: {target}"}
    try:
        json.loads(target_path.read_text())
        return {"type": "json_valid", "target": target, "passed": True, "evidence": "Valid JSON"}
    except json.JSONDecodeError as e:
        return {"type": "json_valid", "target": target, "passed": False, "evidence": f"Invalid JSON: {e}"}


def check_yaml_valid(outputs_dir: Path, target: str, **_) -> dict:
    """Check that a file contains valid YAML."""
    target_path = outputs_dir / target
    if not target_path.exists():
        return {"type": "yaml_valid", "target": target, "passed": False, "evidence": f"File not found: {target}"}
    try:
        import yaml
        yaml.safe_load(target_path.read_text())
        return {"type": "yaml_valid", "target": target, "passed": True, "evidence": "Valid YAML"}
    except Exception as e:
        return {"type": "yaml_valid", "target": target, "passed": False, "evidence": f"Invalid YAML: {e}"}


def check_exit_code(outputs_dir: Path, expected: int = 0, **_) -> dict:
    """Check exit code from a stored result."""
    ec_path = outputs_dir / "exit_code"
    if not ec_path.exists():
        return {"type": "exit_code", "expected": expected, "passed": False, "evidence": "No exit_code file found"}
    actual = int(ec_path.read_text().strip())
    passed = actual == expected
    evidence = f"Exit code: {actual}" + ("" if passed else f" (expected {expected})")
    return {"type": "exit_code", "expected": expected, "passed": passed, "evidence": evidence}


def check_contains(outputs_dir: Path, target: str, expected: str, **_) -> dict:
    """Check that a file contains expected text."""
    target_path = outputs_dir / target
    if not target_path.exists():
        return {"type": "contains", "target": target, "expected": expected, "passed": False, "evidence": f"File not found: {target}"}
    content = target_path.read_text(errors="replace")
    passed = expected in content
    evidence = f"Found '{expected}'" if passed else f"'{expected}' not found in {target}"
    return {"type": "contains", "target": target, "expected": expected, "passed": passed, "evidence": evidence}


def check_not_contains(outputs_dir: Path, target: str, expected: str, **_) -> dict:
    """Check that a file does NOT contain specified text."""
    target_path = outputs_dir / target
    if not target_path.exists():
        return {"type": "not_contains", "target": target, "expected": expected, "passed": True, "evidence": f"File not found (vacuously true)"}
    content = target_path.read_text(errors="replace")
    passed = expected not in content
    evidence = f"'{expected}' correctly absent" if passed else f"Found unwanted '{expected}' in {target}"
    return {"type": "not_contains", "target": target, "expected": expected, "passed": passed, "evidence": evidence}


def check_line_count_range(outputs_dir: Path, target: str, min: int = 0, max: int = 999999, **_) -> dict:
    """Check that a file's line count is within a range."""
    target_path = outputs_dir / target
    if not target_path.exists():
        return {"type": "line_count_range", "target": target, "passed": False, "evidence": f"File not found: {target}"}
    lines = len(target_path.read_text().splitlines())
    passed = min <= lines <= max
    evidence = f"{lines} lines" + ("" if passed else f" (expected {min}-{max})")
    return {"type": "line_count_range", "target": target, "min": min, "max": max, "passed": passed, "evidence": evidence}


def check_file_size_range(outputs_dir: Path, target: str, min: int = 0, max: int = 999999999, **_) -> dict:
    """Check that a file's size is within a range (bytes)."""
    target_path = outputs_dir / target
    if not target_path.exists():
        return {"type": "file_size_range", "target": target, "passed": False, "evidence": f"File not found: {target}"}
    size = target_path.stat().st_size
    passed = min <= size <= max
    evidence = f"{size} bytes" + ("" if passed else f" (expected {min}-{max})")
    return {"type": "file_size_range", "target": target, "min": min, "max": max, "passed": passed, "evidence": evidence}


CHECK_DISPATCH = {
    "file_exists": check_file_exists,
    "regex": check_regex,
    "json_valid": check_json_valid,
    "yaml_valid": check_yaml_valid,
    "exit_code": check_exit_code,
    "contains": check_contains,
    "not_contains": check_not_contains,
    "line_count_range": check_line_count_range,
    "file_size_range": check_file_size_range,
}


def run_tier1(checks: list, outputs_dir: Path) -> list:
    """Run all Tier 1 programmatic checks."""
    results = []
    for check in checks:
        check_type = check.get("type")
        if check_type not in CHECK_DISPATCH:
            results.append(
                {"type": check_type, "passed": False, "evidence": f"Unknown check type: {check_type}"}
            )
            continue

        params = {k: v for k, v in check.items() if k not in ("type", "comment")}
        result = CHECK_DISPATCH[check_type](outputs_dir, **params)
        results.append(result)

    return results


def run_tier2(assertions: list, outputs_dir: Path, transcript: Path = None) -> list:
    """Run Tier 2 agent grading via claude -p.

    Spawns a grader agent using references/agents/grader.md as system prompt.
    Returns list of expectation dicts with passed/evidence/tier.
    """
    if not shutil.which("claude"):
        print("WARNING: claude CLI not available, Tier 2 assertions marked as pending", file=sys.stderr)
        return [
            {
                "text": assertion,
                "passed": None,
                "evidence": "Pending: claude CLI not available for agent grading",
                "tier": 2,
            }
            for assertion in assertions
            if isinstance(assertion, str) and not assertion.startswith("TODO:")
        ]

    # Find grader prompt
    grader_path = Path(__file__).parent.parent / "references" / "agents" / "grader.md"
    if not grader_path.exists():
        print(f"WARNING: grader.md not found at {grader_path}, Tier 2 assertions marked as pending", file=sys.stderr)
        return [
            {
                "text": assertion,
                "passed": None,
                "evidence": "Pending: references/agents/grader.md not found",
                "tier": 2,
            }
            for assertion in assertions
            if isinstance(assertion, str) and not assertion.startswith("TODO:")
        ]

    grader_system = grader_path.read_text()

    # Build user prompt for the grader
    assertion_list = [a for a in assertions if isinstance(a, str) and not a.startswith("TODO:")]
    if not assertion_list:
        return []

    # List output files
    output_files = []
    if outputs_dir.exists():
        for f in sorted(outputs_dir.rglob("*")):
            if f.is_file():
                rel = str(f.relative_to(outputs_dir))
                size = f.stat().st_size
                output_files.append(f"  - {rel} ({size} bytes)")

    user_prompt_parts = [
        "Grade the following assertions based on the eval outputs.",
        "",
        "Assertions to evaluate:",
    ]
    for i, a in enumerate(assertion_list, 1):
        user_prompt_parts.append(f"  {i}. {a}")

    user_prompt_parts.extend(["", "Output files:"])
    user_prompt_parts.extend(output_files if output_files else ["  (no output files)"])

    if transcript and Path(transcript).exists():
        transcript_content = Path(transcript).read_text(errors="replace")
        # Truncate if very long
        if len(transcript_content) > 10000:
            transcript_content = transcript_content[:10000] + "\n... (truncated)"
        user_prompt_parts.extend([
            "",
            "Execution transcript:",
            "```",
            transcript_content,
            "```",
        ])

    # Read first 2000 chars of each output file for context
    for f in sorted(outputs_dir.rglob("*")) if outputs_dir.exists() else []:
        if f.is_file() and f.stat().st_size < 50000:
            try:
                content = f.read_text(errors="replace")[:2000]
                rel = str(f.relative_to(outputs_dir))
                user_prompt_parts.extend([
                    "",
                    f"Content of {rel}:",
                    "```",
                    content,
                    "```",
                ])
            except Exception:
                pass

    user_prompt_parts.extend([
        "",
        "Respond with a JSON object containing:",
        '  "assertions": [{"text": "...", "passed": true/false, "evidence": "..."}]',
        '  "claims": ["implicit claim 1", ...]',
        '  "user_notes_summary": {"uncertainties": [], "needs_review": [], "workarounds": []}',
        '  "eval_feedback": {"suggestions": [{"assertion": "...", "reason": "..."}], "overall": "..."}',
        "",
        "Output ONLY the JSON, nothing else.",
    ])

    user_prompt = "\n".join(user_prompt_parts)

    # Call claude -p with the grader system prompt
    cmd = [
        "claude", "-p", user_prompt,
        "--system-prompt", grader_system,
        "--output-format", "text",
    ]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)
        if result.returncode != 0:
            print(f"WARNING: Grader agent failed: {result.stderr[:200]}", file=sys.stderr)
            return [
                {
                    "text": a, "passed": None,
                    "evidence": f"Grader agent error: {result.stderr[:100]}",
                    "tier": 2,
                }
                for a in assertion_list
            ]

        # Parse grader JSON response
        response_text = result.stdout.strip()
        # Extract JSON from potential markdown code fence
        json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)

        grader_output = json.loads(response_text)
        grader_assertions = grader_output.get("assertions", [])

        # Map grader results to expectations
        expectations = []
        for i, a in enumerate(assertion_list):
            if i < len(grader_assertions):
                ga = grader_assertions[i]
                expectations.append({
                    "text": a,
                    "passed": bool(ga.get("passed")),
                    "evidence": ga.get("evidence", ""),
                    "tier": 2,
                })
            else:
                expectations.append({
                    "text": a, "passed": None,
                    "evidence": "Grader did not return result for this assertion",
                    "tier": 2,
                })

        return expectations, grader_output

    except json.JSONDecodeError as e:
        print(f"WARNING: Failed to parse grader response as JSON: {e}", file=sys.stderr)
        return [
            {"text": a, "passed": None, "evidence": f"Grader response not valid JSON: {e}", "tier": 2}
            for a in assertion_list
        ]
    except subprocess.TimeoutExpired:
        return [
            {"text": a, "passed": None, "evidence": "Grader agent timed out", "tier": 2}
            for a in assertion_list
        ]
    except FileNotFoundError:
        return [
            {"text": a, "passed": None, "evidence": "claude CLI not found", "tier": 2}
            for a in assertion_list
        ]


def grade(eval_file: Path, outputs_dir: Path, transcript: Path = None,
          metrics: Path = None, timing: Path = None, skip_tier2: bool = False) -> dict:
    """Run the full grading pipeline."""
    eval_data = load_yaml(eval_file)
    outputs_dir = Path(outputs_dir)

    checks = eval_data.get("checks", [])
    assertions = eval_data.get("assertions", [])

    # Tier 1: Programmatic checks
    tier1_results = run_tier1(checks, outputs_dir)
    tier1_passed = all(r["passed"] for r in tier1_results)
    tier1_count = len(tier1_results)

    # Build expectations from Tier 1
    expectations = []
    for r in tier1_results:
        expectations.append({
            "text": f"[Check] {r['type']}: {r.get('target', r.get('expected', ''))}",
            "passed": r["passed"],
            "evidence": r["evidence"],
            "tier": 1,
        })

    # Tier 2: Agent assertions
    tier2_note = None
    grader_extras = {}

    real_assertions = [a for a in assertions if isinstance(a, str) and not a.startswith("TODO:")]

    if real_assertions and not tier1_passed:
        tier2_note = "Tier 2 assertions skipped: Tier 1 checks failed"
        for assertion in real_assertions:
            expectations.append({
                "text": assertion,
                "passed": False,
                "evidence": "Skipped: Tier 1 checks failed",
                "tier": 2,
            })
    elif real_assertions and skip_tier2:
        tier2_note = "Tier 2 assertions skipped: --skip-tier2 flag"
        for assertion in real_assertions:
            expectations.append({
                "text": assertion,
                "passed": None,
                "evidence": "Skipped: --skip-tier2 flag",
                "tier": 2,
            })
    elif real_assertions:
        # Run Tier 2 agent grading
        tier2_result = run_tier2(real_assertions, outputs_dir, transcript)
        if isinstance(tier2_result, tuple):
            tier2_expectations, grader_extras = tier2_result
        else:
            tier2_expectations = tier2_result
        expectations.extend(tier2_expectations)

    # Summary
    graded = [e for e in expectations if e["passed"] is not None]
    passed = sum(1 for e in graded if e["passed"])
    failed = sum(1 for e in graded if not e["passed"])
    total = len(graded)
    pass_rate = passed / total if total > 0 else 0

    grading = {
        "expectations": expectations,
        "summary": {
            "passed": passed,
            "failed": failed,
            "total": total,
            "pass_rate": round(pass_rate, 2),
            "tier1_passed": tier1_passed,
            "tier1_count": tier1_count,
        },
    }

    if tier2_note:
        grading["summary"]["tier2_note"] = tier2_note

    # Include grader extras (claims, user_notes_summary, eval_feedback)
    if grader_extras.get("claims"):
        grading["claims"] = grader_extras["claims"]
    else:
        grading["claims"] = []

    if grader_extras.get("user_notes_summary"):
        grading["user_notes_summary"] = grader_extras["user_notes_summary"]
    else:
        grading["user_notes_summary"] = {"uncertainties": [], "needs_review": [], "workarounds": []}

    if grader_extras.get("eval_feedback"):
        grading["eval_feedback"] = grader_extras["eval_feedback"]
    else:
        grading["eval_feedback"] = {"suggestions": [], "overall": ""}

    # Include metrics if available
    if metrics and Path(metrics).exists():
        grading["execution_metrics"] = json.loads(Path(metrics).read_text())

    # Include timing if available
    if timing and Path(timing).exists():
        grading["timing"] = json.loads(Path(timing).read_text())

    return grading


def main():
    parser = argparse.ArgumentParser(description="Two-tier skill eval grader")
    parser.add_argument("--eval-file", required=True, help="Path to .eval.yaml file")
    parser.add_argument("--outputs-dir", required=True, help="Directory with output files")
    parser.add_argument("--transcript", help="Path to transcript file")
    parser.add_argument("--metrics", help="Path to metrics.json")
    parser.add_argument("--timing", help="Path to timing.json")
    parser.add_argument("--grading-output", help="Output path for grading.json")
    parser.add_argument("--skip-tier2", action="store_true", help="Skip Tier 2 agent grading")
    args = parser.parse_args()

    outputs_dir = Path(args.outputs_dir).resolve()
    eval_file = Path(args.eval_file).resolve()

    grading = grade(
        eval_file, outputs_dir,
        transcript=args.transcript,
        metrics=args.metrics,
        timing=args.timing,
        skip_tier2=args.skip_tier2,
    )

    output_path = Path(args.grading_output) if args.grading_output else outputs_dir.parent / "grading.json"
    output_path.write_text(json.dumps(grading, indent=2) + "\n")
    print(f"Grading saved to {output_path}")

    summary = grading["summary"]
    print(f"  Tier 1: {summary['tier1_count']} checks, all passed: {summary['tier1_passed']}")
    print(f"  Total: {summary['passed']}/{summary['total']} passed ({summary['pass_rate']:.0%})")

    return 0 if summary["pass_rate"] >= 0.8 else 1


if __name__ == "__main__":
    sys.exit(main())
