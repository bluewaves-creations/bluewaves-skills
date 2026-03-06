#!/usr/bin/env python3
"""Manage .skill-eval/ workspace for skill evaluation runs.

Commands:
    init <skill-path>           Create workspace with manifest.json
    run <skill-path>            Create next run directory with skill snapshot
    compare [N] [M]             Compare two runs (defaults: latest vs previous)
    clean --keep-last N         Prune old runs
    pin [run_id]                Pin a run as regression baseline
    regress <skill-path>        Compare current against pinned baseline

Usage:
    eval_workspace.py init <skill-path>
    eval_workspace.py run <skill-path>
    eval_workspace.py compare <skill-path> [--run-a N] [--run-b M]
    eval_workspace.py clean <skill-path> --keep-last N
    eval_workspace.py pin <skill-path> [run_id]
    eval_workspace.py regress <skill-path>
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import find_skill_eval_dir, get_next_run_id, hash_file, parse_skill_md


def cmd_init(skill_path: Path) -> int:
    """Create .skill-eval/ workspace with manifest.json."""
    skill_path = Path(skill_path).resolve()
    eval_dir = find_skill_eval_dir(skill_path)

    if (eval_dir / "manifest.json").exists():
        print(f"Workspace already exists: {eval_dir}")
        return 0

    eval_dir.mkdir(parents=True, exist_ok=True)
    (eval_dir / "runs").mkdir(exist_ok=True)
    (eval_dir / "evals").mkdir(exist_ok=True)

    name, _, _ = parse_skill_md(skill_path)

    manifest = {
        "skill_name": name,
        "created": datetime.now(timezone.utc).isoformat(),
        "runs": [],
        "pinned_baseline": None,
    }

    (eval_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Initialized workspace: {eval_dir}")
    print(f"  manifest.json created for skill '{name}'")
    print(f"  evals/ directory ready for .eval.yaml files")
    return 0


def cmd_run(skill_path: Path) -> int:
    """Create next sequential run directory with skill snapshot."""
    skill_path = Path(skill_path).resolve()
    eval_dir = find_skill_eval_dir(skill_path)

    if not (eval_dir / "manifest.json").exists():
        print("Workspace not initialized. Run 'init' first.")
        return 1

    run_id = get_next_run_id(eval_dir)
    run_dir = eval_dir / "runs" / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "outputs").mkdir()

    # Snapshot current SKILL.md
    skill_md = skill_path / "SKILL.md"
    snapshot = run_dir / "skill-snapshot.md"
    snapshot.write_text(skill_md.read_text())

    skill_hash = hash_file(skill_md)

    # Update manifest
    manifest_path = eval_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["runs"].append(
        {
            "id": run_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "skill_hash": skill_hash,
            "summary": None,
        }
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"Created run {run_id}: {run_dir}")
    print(f"  Skill snapshot saved (hash: {skill_hash})")
    print(f"  Ready for eval execution")
    return 0


def cmd_compare(skill_path: Path, run_a: str = None, run_b: str = None) -> int:
    """Compare two runs (defaults: latest vs previous)."""
    skill_path = Path(skill_path).resolve()
    eval_dir = find_skill_eval_dir(skill_path)
    runs_dir = eval_dir / "runs"

    if not runs_dir.exists():
        print("No runs found.")
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

    print(f"Comparing run {run_a} vs {run_b}")
    print()

    # Compare skill snapshots
    snap_a = dir_a / "skill-snapshot.md"
    snap_b = dir_b / "skill-snapshot.md"
    if snap_a.exists() and snap_b.exists():
        if snap_a.read_text() == snap_b.read_text():
            print("  SKILL.md: unchanged")
        else:
            print("  SKILL.md: modified between runs")

    # Compare grading results
    for run_id, run_dir in [(run_a, dir_a), (run_b, dir_b)]:
        grading_path = run_dir / "grading.json"
        if grading_path.exists():
            grading = json.loads(grading_path.read_text())
            summary = grading.get("summary", {})
            print(
                f"  Run {run_id}: {summary.get('passed', '?')}/{summary.get('total', '?')} passed "
                f"({summary.get('pass_rate', 0):.0%})"
            )
        else:
            print(f"  Run {run_id}: no grading.json")

    return 0


def cmd_clean(skill_path: Path, keep_last: int) -> int:
    """Prune old runs, keeping the last N."""
    skill_path = Path(skill_path).resolve()
    eval_dir = find_skill_eval_dir(skill_path)
    runs_dir = eval_dir / "runs"

    if not runs_dir.exists():
        print("No runs to clean.")
        return 0

    existing = sorted([d for d in runs_dir.iterdir() if d.is_dir() and d.name.isdigit()])
    if len(existing) <= keep_last:
        print(f"Only {len(existing)} runs exist, nothing to clean (keeping {keep_last}).")
        return 0

    # Check pinned baseline
    manifest_path = eval_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    pinned = manifest.get("pinned_baseline")

    to_remove = existing[: len(existing) - keep_last]
    removed = 0
    for run_dir in to_remove:
        if pinned and run_dir.name == pinned:
            print(f"  Skipping pinned baseline: {run_dir.name}")
            continue
        import shutil

        shutil.rmtree(run_dir)
        manifest["runs"] = [r for r in manifest["runs"] if r["id"] != run_dir.name]
        removed += 1

    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Removed {removed} runs, kept {len(existing) - removed}.")
    return 0


def cmd_pin(skill_path: Path, run_id: str = None) -> int:
    """Pin a run as regression baseline."""
    skill_path = Path(skill_path).resolve()
    eval_dir = find_skill_eval_dir(skill_path)
    manifest_path = eval_dir / "manifest.json"

    if not manifest_path.exists():
        print("Workspace not initialized.")
        return 1

    manifest = json.loads(manifest_path.read_text())

    if not run_id:
        runs = sorted(
            [d.name for d in (eval_dir / "runs").iterdir() if d.is_dir() and d.name.isdigit()]
        )
        if not runs:
            print("No runs to pin.")
            return 1
        run_id = runs[-1]

    run_dir = eval_dir / "runs" / run_id
    if not run_dir.exists():
        print(f"Run {run_id} not found.")
        return 1

    manifest["pinned_baseline"] = run_id
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Pinned run {run_id} as regression baseline.")
    return 0


def cmd_regress(skill_path: Path) -> int:
    """Compare current state against pinned baseline."""
    skill_path = Path(skill_path).resolve()
    eval_dir = find_skill_eval_dir(skill_path)
    manifest_path = eval_dir / "manifest.json"

    if not manifest_path.exists():
        print("Workspace not initialized.")
        return 1

    manifest = json.loads(manifest_path.read_text())
    pinned = manifest.get("pinned_baseline")
    if not pinned:
        print("No pinned baseline. Run 'pin' first.")
        return 1

    runs = sorted(
        [d.name for d in (eval_dir / "runs").iterdir() if d.is_dir() and d.name.isdigit()]
    )
    if not runs:
        print("No runs to compare.")
        return 1

    latest = runs[-1]
    if latest == pinned:
        print("Latest run IS the pinned baseline. Run new evals first.")
        return 1

    print(f"Regression check: run {latest} vs pinned baseline {pinned}")
    return cmd_compare(skill_path, run_a=pinned, run_b=latest)


def main():
    parser = argparse.ArgumentParser(description="Skill eval workspace manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_init = subparsers.add_parser("init", help="Initialize workspace")
    p_init.add_argument("skill_path", help="Path to skill directory")

    p_run = subparsers.add_parser("run", help="Create next run directory")
    p_run.add_argument("skill_path", help="Path to skill directory")

    p_compare = subparsers.add_parser("compare", help="Compare two runs")
    p_compare.add_argument("skill_path", help="Path to skill directory")
    p_compare.add_argument("--run-a", help="First run ID")
    p_compare.add_argument("--run-b", help="Second run ID")

    p_clean = subparsers.add_parser("clean", help="Prune old runs")
    p_clean.add_argument("skill_path", help="Path to skill directory")
    p_clean.add_argument("--keep-last", type=int, required=True, help="Number of runs to keep")

    p_pin = subparsers.add_parser("pin", help="Pin a run as baseline")
    p_pin.add_argument("skill_path", help="Path to skill directory")
    p_pin.add_argument("run_id", nargs="?", help="Run ID to pin (default: latest)")

    p_regress = subparsers.add_parser("regress", help="Check regression against baseline")
    p_regress.add_argument("skill_path", help="Path to skill directory")

    args = parser.parse_args()

    if args.command == "init":
        return cmd_init(args.skill_path)
    elif args.command == "run":
        return cmd_run(args.skill_path)
    elif args.command == "compare":
        return cmd_compare(args.skill_path, args.run_a, args.run_b)
    elif args.command == "clean":
        return cmd_clean(args.skill_path, args.keep_last)
    elif args.command == "pin":
        return cmd_pin(args.skill_path, getattr(args, "run_id", None))
    elif args.command == "regress":
        return cmd_regress(args.skill_path)


if __name__ == "__main__":
    sys.exit(main() or 0)
