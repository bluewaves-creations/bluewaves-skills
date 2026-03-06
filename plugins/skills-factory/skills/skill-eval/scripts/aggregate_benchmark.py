#!/usr/bin/env python3
"""Aggregate benchmark results from grading.json files into statistics.

Reads grading.json files from the workspace run layout and computes
mean, stddev, min, max for pass_rate, time_seconds, and tokens per
configuration. Computes delta between configurations.

Usage:
    aggregate_benchmark.py <benchmark_dir> --skill-name <name>
"""

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path


def mean(values: list) -> float:
    """Compute arithmetic mean."""
    return sum(values) / len(values) if values else 0


def stddev(values: list) -> float:
    """Compute sample standard deviation."""
    if len(values) < 2:
        return 0
    m = mean(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))


def stats(values: list) -> dict:
    """Compute full statistics for a list of values."""
    if not values:
        return {"mean": 0, "stddev": 0, "min": 0, "max": 0}
    return {
        "mean": round(mean(values), 2),
        "stddev": round(stddev(values), 2),
        "min": round(min(values), 2),
        "max": round(max(values), 2),
    }


def collect_runs(benchmark_dir: Path) -> list:
    """Collect grading.json results from benchmark directory layout.

    Supports two layouts:
    1. Flat: runs/NNN/grading.json
    2. Nested: eval-E/{with_skill,without_skill}/run-R/grading.json
    """
    runs = []

    # Try nested layout first
    for eval_dir in sorted(benchmark_dir.glob("eval-*")):
        eval_name = eval_dir.name
        for config_dir in sorted(eval_dir.iterdir()):
            if not config_dir.is_dir():
                continue
            configuration = config_dir.name  # with_skill or without_skill
            for run_dir in sorted(config_dir.glob("run-*")):
                grading_path = run_dir / "grading.json"
                timing_path = run_dir / "timing.json"
                if grading_path.exists():
                    grading = json.loads(grading_path.read_text())
                    timing = json.loads(timing_path.read_text()) if timing_path.exists() else {}

                    summary = grading.get("summary", {})
                    run_number = int(run_dir.name.split("-")[-1]) if "-" in run_dir.name else 1

                    runs.append({
                        "eval_name": eval_name,
                        "configuration": configuration,
                        "run_number": run_number,
                        "result": {
                            "pass_rate": summary.get("pass_rate", 0),
                            "passed": summary.get("passed", 0),
                            "failed": summary.get("failed", 0),
                            "total": summary.get("total", 0),
                            "time_seconds": timing.get("total_duration_seconds", 0),
                            "tokens": timing.get("total_tokens", 0),
                            "tool_calls": grading.get("execution_metrics", {}).get("total_tool_calls", 0),
                            "errors": grading.get("execution_metrics", {}).get("errors_encountered", 0),
                        },
                        "expectations": grading.get("expectations", []),
                    })

    # Try flat layout if nested yielded nothing
    if not runs:
        runs_dir = benchmark_dir / "runs" if (benchmark_dir / "runs").exists() else benchmark_dir
        for run_dir in sorted(runs_dir.glob("*")):
            if not run_dir.is_dir():
                continue
            grading_path = run_dir / "grading.json"
            timing_path = run_dir / "timing.json"
            if grading_path.exists():
                grading = json.loads(grading_path.read_text())
                timing = json.loads(timing_path.read_text()) if timing_path.exists() else {}
                summary = grading.get("summary", {})
                runs.append({
                    "eval_name": run_dir.name,
                    "configuration": "with_skill",
                    "run_number": 1,
                    "result": {
                        "pass_rate": summary.get("pass_rate", 0),
                        "passed": summary.get("passed", 0),
                        "failed": summary.get("failed", 0),
                        "total": summary.get("total", 0),
                        "time_seconds": timing.get("total_duration_seconds", 0),
                        "tokens": timing.get("total_tokens", 0),
                    },
                    "expectations": grading.get("expectations", []),
                })

    return runs


def aggregate(benchmark_dir: Path, skill_name: str) -> dict:
    """Aggregate all benchmark runs into statistics."""
    runs = collect_runs(benchmark_dir)

    if not runs:
        print("No grading.json files found.")
        return {}

    # Group by configuration
    configs = {}
    for run in runs:
        config = run["configuration"]
        if config not in configs:
            configs[config] = {"pass_rates": [], "times": [], "tokens": []}
        configs[config]["pass_rates"].append(run["result"]["pass_rate"])
        configs[config]["times"].append(run["result"].get("time_seconds", 0))
        configs[config]["tokens"].append(run["result"].get("tokens", 0))

    run_summary = {}
    for config, data in configs.items():
        run_summary[config] = {
            "pass_rate": stats(data["pass_rates"]),
            "time_seconds": stats(data["times"]),
            "tokens": stats(data["tokens"]),
        }

    # Compute delta if both configs exist
    delta = {}
    if "with_skill" in run_summary and "without_skill" in run_summary:
        ws = run_summary["with_skill"]
        wos = run_summary["without_skill"]
        delta = {
            "pass_rate": f"{ws['pass_rate']['mean'] - wos['pass_rate']['mean']:+.2f}",
            "time_seconds": f"{ws['time_seconds']['mean'] - wos['time_seconds']['mean']:+.1f}",
            "tokens": f"{ws['tokens']['mean'] - wos['tokens']['mean']:+.0f}",
        }

    benchmark = {
        "metadata": {
            "skill_name": skill_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "evals_run": sorted(set(r["eval_name"] for r in runs)),
            "total_runs": len(runs),
        },
        "runs": runs,
        "run_summary": run_summary,
    }

    if delta:
        benchmark["run_summary"]["delta"] = delta

    # Generate notes
    notes = []
    for run in runs:
        for exp in run.get("expectations", []):
            text = exp.get("text", "")
            passed = exp.get("passed")
            # Check for non-discriminating assertions (always pass)
            if all(
                any(e.get("text") == text and e.get("passed") for e in r.get("expectations", []))
                for r in runs
            ):
                note = f"Assertion '{text[:60]}' passes in all runs - may not differentiate skill value"
                if note not in notes:
                    notes.append(note)
                    break

    benchmark["notes"] = notes

    return benchmark


def main():
    parser = argparse.ArgumentParser(description="Aggregate benchmark results")
    parser.add_argument("benchmark_dir", help="Directory with benchmark results")
    parser.add_argument("--skill-name", required=True, help="Skill name for metadata")
    args = parser.parse_args()

    benchmark_dir = Path(args.benchmark_dir).resolve()
    benchmark = aggregate(benchmark_dir, args.skill_name)

    if not benchmark:
        return 1

    # Write benchmark.json
    output_path = benchmark_dir / "benchmark.json"
    output_path.write_text(json.dumps(benchmark, indent=2) + "\n")
    print(f"Benchmark saved to {output_path}")

    # Write benchmark.md summary
    md_path = benchmark_dir / "benchmark.md"
    md_lines = [f"# Benchmark: {args.skill_name}", ""]

    for config, data in benchmark["run_summary"].items():
        if config == "delta":
            continue
        md_lines.append(f"## {config}")
        md_lines.append(f"- Pass rate: {data['pass_rate']['mean']:.0%} (stddev: {data['pass_rate']['stddev']:.2f})")
        md_lines.append(f"- Time: {data['time_seconds']['mean']:.1f}s (stddev: {data['time_seconds']['stddev']:.1f})")
        md_lines.append(f"- Tokens: {data['tokens']['mean']:.0f} (stddev: {data['tokens']['stddev']:.0f})")
        md_lines.append("")

    if "delta" in benchmark.get("run_summary", {}):
        delta = benchmark["run_summary"]["delta"]
        md_lines.append("## Delta (with_skill - without_skill)")
        md_lines.append(f"- Pass rate: {delta['pass_rate']}")
        md_lines.append(f"- Time: {delta['time_seconds']}s")
        md_lines.append(f"- Tokens: {delta['tokens']}")
        md_lines.append("")

    if benchmark.get("notes"):
        md_lines.append("## Notes")
        for note in benchmark["notes"]:
            md_lines.append(f"- {note}")

    md_path.write_text("\n".join(md_lines) + "\n")
    print(f"Summary saved to {md_path}")

    # Print summary
    print(f"\nResults: {benchmark['metadata']['total_runs']} runs across {len(benchmark['metadata']['evals_run'])} evals")
    for config, data in benchmark["run_summary"].items():
        if config == "delta":
            continue
        print(f"  {config}: {data['pass_rate']['mean']:.0%} pass rate")

    return 0


if __name__ == "__main__":
    sys.exit(main())
