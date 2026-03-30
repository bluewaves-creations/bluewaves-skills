#!/usr/bin/env python3
"""Simulated trigger testing — prompt-based, zero subprocess cost.

Generates a prompt that simulates Claude's skill-routing decision:
"Given these skill descriptions, which would you invoke for each query?"

Modes:
  --prompt-only   Output the simulation prompt (for in-session use)
  --parse         Parse raw LLM response into run_eval-compatible results
  --execute       Run via claude -p --model haiku (fallback for unattended use)

Usage:
    sim_trigger.py --prompt-only --skill-name <name> --description "<desc>" --eval-set <json>
    sim_trigger.py --parse --skill-name <name> --eval-set <json> --response <file>
    sim_trigger.py --execute --skill-name <name> --skill-path <dir> --eval-set <json>
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import parse_skill_md


# Decoy skills provide realistic competition for the routing decision.
# Without decoys, the model just answers "yes/no" which doesn't test selectivity.
DEFAULT_DECOYS = [
    {
        "name": "pdf-reader",
        "description": (
            "Read and extract text, tables, and metadata from PDF files. "
            "Use when the user wants to read a PDF, extract content from a "
            "PDF, parse a PDF document, or convert PDF to text."
        ),
    },
    {
        "name": "code-review",
        "description": (
            "Review code for quality, security vulnerabilities, and best "
            "practices. Use when the user asks for a code review, wants "
            "feedback on their code, or asks about code quality."
        ),
    },
    {
        "name": "data-analysis",
        "description": (
            "Analyze datasets, generate statistical summaries, and create "
            "visualizations. Use when the user mentions data analysis, CSV "
            "processing, statistics, or data visualization."
        ),
    },
]


def build_sim_prompt(skill_name: str, description: str,
                     queries: list, decoy_skills: list = None) -> str:
    """Build a prompt that simulates Claude's skill-routing decision.

    Args:
        skill_name: Name of the skill being tested
        description: Description to test
        queries: List of dicts with 'query' and 'should_trigger' keys
        decoy_skills: Optional list of dicts with 'name' and 'description'

    Returns:
        Prompt string for the simulation
    """
    decoys = decoy_skills or DEFAULT_DECOYS

    skills_block = f"- {skill_name}: {description}"
    for d in decoys:
        skills_block += f"\n- {d['name']}: {d['description']}"

    queries_block = ""
    for i, item in enumerate(queries, 1):
        q = item["query"] if isinstance(item, dict) else item
        queries_block += f'{i}. "{q}"\n'

    return f"""You are Claude Code's skill router. When a user sends a message, you decide whether to invoke a skill based on available skill names and descriptions. You see ONLY the information below — not the skill contents or any other context.

Available skills:
{skills_block}

For each user query below, decide which skill (if any) you would invoke. Consider:
- Does the query match the skill's described purpose and trigger contexts?
- Is there a better-matching skill among the alternatives?
- Would you handle this query without any skill?

Queries:
{queries_block}
Respond with ONLY a JSON array — no explanation, no markdown fences:
[{{"query": "the query text", "invoke": "skill-name-or-none"}}, ...]"""


def parse_sim_results(response_text: str, queries: list,
                      skill_name: str) -> dict:
    """Parse LLM response into run_eval-compatible results format.

    Args:
        response_text: Raw LLM response (should be JSON array)
        queries: Original eval set for should_trigger metadata
        skill_name: Name of the skill being tested

    Returns:
        Dict matching run_eval.evaluate_queries() output format
    """
    # Extract JSON from response (handle markdown fences)
    text = response_text.strip()
    json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if json_match:
        text = json_match.group(1)

    try:
        decisions = json.loads(text)
    except json.JSONDecodeError:
        # Try to find array in the text
        arr_match = re.search(r"\[.*\]", text, re.DOTALL)
        if arr_match:
            decisions = json.loads(arr_match.group(0))
        else:
            return {
                "skill_name": skill_name,
                "description": "",
                "results": [],
                "summary": {"total": 0, "passed": 0, "failed": 0},
                "error": f"Could not parse response as JSON: {text[:200]}",
            }

    # Build query lookup for should_trigger metadata
    query_meta = {}
    for item in queries:
        q = item["query"] if isinstance(item, dict) else item
        should = item.get("should_trigger", True) if isinstance(item, dict) else True
        query_meta[q] = should

    # Map decisions to run_eval-compatible results
    results = []
    for d in decisions:
        query = d.get("query", "")
        invoked_skill = d.get("invoke", "none")
        triggered = invoked_skill == skill_name
        should_trigger = query_meta.get(query, True)

        # Pass/fail logic matches run_eval
        if should_trigger:
            passed = triggered
        else:
            passed = not triggered

        results.append({
            "query": query,
            "should_trigger": should_trigger,
            "trigger_rate": 1.0 if triggered else 0.0,
            "triggers": 1 if triggered else 0,
            "runs": 1,
            "pass": passed,
            "invoked": invoked_skill,
        })

    passed_count = sum(1 for r in results if r["pass"])
    total = len(results)

    return {
        "skill_name": skill_name,
        "results": results,
        "summary": {
            "total": total,
            "passed": passed_count,
            "failed": total - passed_count,
        },
    }


def sim_evaluate_queries(eval_set: list, skill_name: str, description: str,
                         project_root: Path = None, model: str = None,
                         decoy_skills: list = None, **kwargs) -> dict:
    """Drop-in replacement for run_eval.evaluate_queries() using simulation.

    Same interface, same output format. Uses one claude -p call with Haiku
    instead of N*M separate sessions.
    """
    prompt = build_sim_prompt(skill_name, description, eval_set, decoy_skills)
    model = model or "haiku"

    cmd = ["claude", "-p", prompt, "--output-format", "text"]
    if model:
        cmd.extend(["--model", model])

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60, env=env,
            cwd=str(project_root) if project_root else None,
        )
        if result.returncode != 0:
            return {
                "skill_name": skill_name,
                "description": description,
                "results": [],
                "summary": {"total": 0, "passed": 0, "failed": 0},
                "error": f"claude -p failed: {result.stderr[:200]}",
            }

        results = parse_sim_results(result.stdout, eval_set, skill_name)
        results["description"] = description
        return results

    except FileNotFoundError:
        return {
            "skill_name": skill_name, "description": description,
            "results": [], "summary": {"total": 0, "passed": 0, "failed": 0},
            "error": "claude CLI not found",
        }
    except subprocess.TimeoutExpired:
        return {
            "skill_name": skill_name, "description": description,
            "results": [], "summary": {"total": 0, "passed": 0, "failed": 0},
            "error": "claude -p timed out",
        }


def main():
    parser = argparse.ArgumentParser(
        description="Simulated trigger testing — prompt-based, zero subprocess cost"
    )
    parser.add_argument("--skill-name", help="Skill name")
    parser.add_argument("--skill-path", help="Path to skill directory (reads name/description)")
    parser.add_argument("--description", help="Override description to test")
    parser.add_argument("--eval-set", help="JSON file with eval queries")
    parser.add_argument("--decoys", help="JSON file with decoy skill descriptions")
    parser.add_argument("--model", default="haiku", help="Model for --execute mode (default: haiku)")

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prompt-only", action="store_true",
                       help="Output simulation prompt and exit")
    mode.add_argument("--parse", action="store_true",
                       help="Parse LLM response into results")
    mode.add_argument("--execute", action="store_true",
                       help="Run via claude -p (fallback for unattended use)")
    parser.add_argument("--response", help="File with LLM response (for --parse mode)")

    args = parser.parse_args()

    # Resolve skill name and description
    skill_name = args.skill_name
    description = args.description
    if args.skill_path:
        name, desc, _ = parse_skill_md(Path(args.skill_path))
        skill_name = skill_name or name
        description = description or desc

    if not skill_name:
        print("Error: --skill-name or --skill-path required", file=sys.stderr)
        sys.exit(1)

    # Load eval set
    eval_set = []
    if args.eval_set:
        data = json.loads(Path(args.eval_set).read_text())
        if isinstance(data, list):
            eval_set = data
        elif isinstance(data, dict):
            eval_set = data.get("evals", data.get("queries", []))

    # Load optional decoys
    decoys = None
    if args.decoys:
        decoys = json.loads(Path(args.decoys).read_text())

    if args.prompt_only:
        if not description:
            print("Error: --description or --skill-path required", file=sys.stderr)
            sys.exit(1)
        print(build_sim_prompt(skill_name, description, eval_set, decoys))

    elif args.parse:
        if args.response:
            response_text = Path(args.response).read_text()
        else:
            response_text = sys.stdin.read()
        results = parse_sim_results(response_text, eval_set, skill_name)
        print(json.dumps(results, indent=2))

    elif args.execute:
        if not description:
            print("Error: --description or --skill-path required", file=sys.stderr)
            sys.exit(1)
        results = sim_evaluate_queries(
            eval_set, skill_name, description, model=args.model, decoy_skills=decoys,
        )
        print(json.dumps(results, indent=2))

        summary = results.get("summary", {})
        passed = summary.get("passed", 0)
        total = summary.get("total", 0)
        print(f"\nResults: {passed}/{total} queries passed", file=sys.stderr)
        for r in results.get("results", []):
            status = "PASS" if r["pass"] else "FAIL"
            expected = "should trigger" if r["should_trigger"] else "should NOT trigger"
            print(f"  [{status}] {r['query'][:60]}... ({expected}, invoked: {r.get('invoked', '?')})",
                  file=sys.stderr)

        sys.exit(0 if passed / total >= 0.8 else 1 if total > 0 else 1)


if __name__ == "__main__":
    main()
