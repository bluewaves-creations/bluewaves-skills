#!/usr/bin/env python3
"""Trigger evaluation via claude -p subprocess.

Tests skill triggering by creating temp command files with unique IDs and
running claude -p with streaming output. Detects triggering via stream events
with skill identity verification (not just any tool use).

Usage:
    run_eval.py --eval-set <json> --skill-path <dir> \
        [--num-workers 10] [--timeout 30] [--runs-per-query 3] [--model <id>]
"""

import argparse
import json
import os
import select
import subprocess
import sys
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import parse_skill_md


def find_project_root() -> Path:
    """Find project root by walking up from cwd looking for .claude/ directory."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".claude").is_dir():
            return parent
    return current


def run_single_query(query: str, skill_name: str, skill_description: str,
                     timeout: int, project_root: str, model: str = None) -> dict:
    """Run a single query through claude -p and detect triggering.

    Creates a unique command file in .claude/commands/ so it appears in
    Claude's available_skills list. Uses --include-partial-messages to
    detect triggering early from stream events rather than waiting for
    full tool execution.

    Returns dict with: query, triggered, duration_ms, total_tokens, error
    """
    unique_id = uuid.uuid4().hex[:8]
    clean_name = f"{skill_name}-skill-{unique_id}"
    # Match patterns: temp command name OR real skill name (with optional plugin prefix)
    match_names = {clean_name, skill_name, f":{skill_name}"}
    project_root = Path(project_root)
    commands_dir = project_root / ".claude" / "commands"
    command_file = commands_dir / f"{clean_name}.md"

    try:
        commands_dir.mkdir(parents=True, exist_ok=True)
        # Use YAML block scalar to avoid breaking on quotes in description
        indented_desc = "\n  ".join(skill_description.split("\n"))
        command_content = (
            f"---\n"
            f"description: |\n"
            f"  {indented_desc}\n"
            f"---\n\n"
            f"# {skill_name}\n\n"
            f"This skill handles: {skill_description}\n"
        )
        command_file.write_text(command_content)

        cmd = [
            "claude", "-p", query,
            "--output-format", "stream-json",
            "--verbose",
            "--include-partial-messages",
        ]
        if model:
            cmd.extend(["--model", model])

        # Remove CLAUDECODE env var to allow nesting claude -p
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

        start_time = time.time()
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=str(project_root),
            env=env,
        )

        triggered = False
        total_tokens = 0
        buffer = ""
        pending_tool_name = None
        accumulated_json = ""

        try:
            while time.time() - start_time < timeout:
                if process.poll() is not None:
                    remaining = process.stdout.read()
                    if remaining:
                        buffer += remaining.decode("utf-8", errors="replace")
                    break

                ready, _, _ = select.select([process.stdout], [], [], 1.0)
                if not ready:
                    continue

                chunk = os.read(process.stdout.fileno(), 8192)
                if not chunk:
                    break
                buffer += chunk.decode("utf-8", errors="replace")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    event_type = event.get("type", "")

                    # Stream event detection (from --include-partial-messages)
                    if event_type == "stream_event":
                        se = event.get("event", {})
                        se_type = se.get("type", "")

                        if se_type == "content_block_start":
                            cb = se.get("content_block", {})
                            if cb.get("type") == "tool_use":
                                tool_name = cb.get("name", "")
                                if tool_name in ("Skill", "Read"):
                                    pending_tool_name = tool_name
                                    accumulated_json = ""
                                elif tool_name == "ToolSearch":
                                    # ToolSearch loads deferred tools (e.g. Skill)
                                    # — don't early-exit, wait for next tool call
                                    pending_tool_name = None
                                    accumulated_json = ""
                                else:
                                    # Wrong tool — not our skill, early exit
                                    duration_ms = int((time.time() - start_time) * 1000)
                                    return {
                                        "query": query, "triggered": False,
                                        "duration_ms": duration_ms, "total_tokens": 0,
                                    }

                        elif se_type == "content_block_delta" and pending_tool_name:
                            delta = se.get("delta", {})
                            if delta.get("type") == "input_json_delta":
                                accumulated_json += delta.get("partial_json", "")
                                if any(n in accumulated_json for n in match_names):
                                    duration_ms = int((time.time() - start_time) * 1000)
                                    return {
                                        "query": query, "triggered": True,
                                        "duration_ms": duration_ms, "total_tokens": 0,
                                    }

                        elif se_type in ("content_block_stop", "message_stop"):
                            if pending_tool_name:
                                triggered = any(n in accumulated_json for n in match_names)
                                duration_ms = int((time.time() - start_time) * 1000)
                                return {
                                    "query": query, "triggered": triggered,
                                    "duration_ms": duration_ms, "total_tokens": 0,
                                }
                            if se_type == "message_stop":
                                duration_ms = int((time.time() - start_time) * 1000)
                                return {
                                    "query": query, "triggered": False,
                                    "duration_ms": duration_ms, "total_tokens": 0,
                                }

                    # Fallback: full assistant message (non-streaming)
                    elif event_type == "assistant":
                        message = event.get("message", {})
                        only_toolsearch = True
                        for content_item in message.get("content", []):
                            if content_item.get("type") != "tool_use":
                                continue
                            tool_name = content_item.get("name", "")
                            tool_input = content_item.get("input", {})
                            if tool_name == "Skill" and any(n in tool_input.get("skill", "") for n in match_names):
                                triggered = True
                                only_toolsearch = False
                            elif tool_name == "Read" and any(n in tool_input.get("file_path", "") for n in match_names):
                                triggered = True
                                only_toolsearch = False
                            elif tool_name == "ToolSearch":
                                pass  # Intermediate step, keep waiting
                            else:
                                only_toolsearch = False
                        if not only_toolsearch:
                            duration_ms = int((time.time() - start_time) * 1000)
                            return {
                                "query": query, "triggered": triggered,
                                "duration_ms": duration_ms, "total_tokens": 0,
                            }

                    # Usage data
                    elif event_type == "message_delta":
                        usage = event.get("usage", {})
                        total_tokens = usage.get("output_tokens", total_tokens)

                    elif event_type == "result":
                        duration_ms = int((time.time() - start_time) * 1000)
                        return {
                            "query": query, "triggered": triggered,
                            "duration_ms": duration_ms, "total_tokens": total_tokens,
                        }

            # Timeout reached
            duration_ms = int((time.time() - start_time) * 1000)
            return {"query": query, "triggered": False, "duration_ms": duration_ms, "error": "timeout"}

        finally:
            if process.poll() is None:
                process.kill()
                process.wait()

    except FileNotFoundError:
        return {"query": query, "triggered": False, "error": "claude CLI not found"}
    finally:
        if command_file.exists():
            command_file.unlink()


def evaluate_queries(eval_set: list, skill_name: str, description: str,
                     project_root: Path, num_workers: int = 10,
                     timeout: int = 30, runs_per_query: int = 3,
                     trigger_threshold: float = 0.5,
                     model: str = None) -> dict:
    """Run all eval queries and compute trigger rates."""
    results = []

    total_runs = len(eval_set) * runs_per_query
    completed = 0

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {}
        for item in eval_set:
            query = item["query"] if isinstance(item, dict) else item
            should_trigger = item.get("should_trigger", True) if isinstance(item, dict) else True

            for run in range(runs_per_query):
                future = executor.submit(
                    run_single_query, query, skill_name, description,
                    timeout, str(project_root), model,
                )
                futures[future] = {"query": query, "should_trigger": should_trigger, "run": run}

        for future in as_completed(futures):
            meta = futures[future]
            try:
                result = future.result()
            except Exception as e:
                result = {"query": meta["query"], "triggered": False, "error": str(e)}

            result["should_trigger"] = meta["should_trigger"]
            result["run"] = meta["run"]
            results.append(result)

            completed += 1
            print(f"  [{completed}/{total_runs}] {meta['query'][:50]}... -> "
                  f"{'triggered' if result.get('triggered') else 'not triggered'}")

    # Aggregate per-query
    query_results = {}
    for r in results:
        q = r["query"]
        if q not in query_results:
            query_results[q] = {
                "query": q,
                "should_trigger": r["should_trigger"],
                "triggers": 0,
                "runs": 0,
            }
        query_results[q]["runs"] += 1
        if r.get("triggered"):
            query_results[q]["triggers"] += 1

    # Compute metrics
    for qr in query_results.values():
        qr["trigger_rate"] = qr["triggers"] / qr["runs"] if qr["runs"] > 0 else 0
        if qr["should_trigger"]:
            qr["pass"] = qr["trigger_rate"] >= trigger_threshold
        else:
            qr["pass"] = qr["trigger_rate"] < trigger_threshold

    passed = sum(1 for qr in query_results.values() if qr["pass"])
    total_queries = len(query_results)

    return {
        "skill_name": skill_name,
        "description": description,
        "results": list(query_results.values()),
        "summary": {
            "total": total_queries,
            "passed": passed,
            "failed": total_queries - passed,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Skill trigger evaluation via claude -p")
    parser.add_argument("--eval-set", required=True, help="JSON file with eval queries")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override description to test")
    parser.add_argument("--num-workers", type=int, default=10, help="Parallel workers")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per query (seconds)")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Runs per query for reliability")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    parser.add_argument("--model", help="Model ID to use")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()

    skill_path = Path(args.skill_path)
    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    eval_set = json.loads(Path(args.eval_set).read_text())
    if isinstance(eval_set, dict):
        eval_set = eval_set.get("evals", eval_set.get("queries", []))

    name, original_description, content = parse_skill_md(skill_path)
    description = args.description or original_description
    project_root = find_project_root()

    print(f"Running trigger evaluation: {len(eval_set)} queries x {args.runs_per_query} runs")
    print(f"Skill: {name}")
    print(f"Project root: {project_root}")
    print()

    results = evaluate_queries(
        eval_set, name, description, project_root,
        num_workers=args.num_workers,
        timeout=args.timeout,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        model=args.model,
    )

    # Print summary
    summary = results["summary"]
    print(f"\n{'=' * 50}")
    print(f"Results: {summary['passed']}/{summary['total']} queries passed")
    print()

    for qr in results["results"]:
        status = "PASS" if qr["pass"] else "FAIL"
        expected = "should trigger" if qr["should_trigger"] else "should NOT trigger"
        color = "\033[92m" if qr["pass"] else "\033[91m"
        print(f"  {color}{status}\033[0m {qr['query'][:60]}...")
        print(f"       {expected}, triggered {qr['triggers']}/{qr['runs']} ({qr['trigger_rate']:.0%})")

    # Write output
    output_path = Path(args.skill_path) / ".skill-eval" / "trigger_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2) + "\n")
    print(f"\nResults saved to {output_path}")

    # Also write to stdout as JSON for piping
    if args.verbose:
        print(json.dumps(results, indent=2))

    pass_rate = summary["passed"] / summary["total"] if summary["total"] > 0 else 0
    return 0 if pass_rate >= 0.8 else 1


if __name__ == "__main__":
    sys.exit(main())
