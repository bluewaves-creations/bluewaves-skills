#!/usr/bin/env python3
"""Eval + improve loop with train/test split.

Combines run_eval + improve_description in an iterative loop.
Stratified train/test split (60/40) by should_trigger. Selects
best description by TEST score (prevents overfitting).
Blinds test results from the improvement model.

Usage:
    run_loop.py --eval-set <json> --skill-path <dir> \
        [--model <id>] [--max-iterations 5] [--holdout 0.4] [--verbose]
"""

import argparse
import json
import os
import random
import re
import sys
import tempfile
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import parse_skill_md
from run_eval import evaluate_queries, find_project_root
from improve_description import improve
from generate_report import build_report_html


def stratified_split(eval_set: list, holdout: float = 0.4, seed: int = 42) -> tuple:
    """Split eval set into train/test with stratification by should_trigger."""
    rng = random.Random(seed)

    positives = [e for e in eval_set if e.get("should_trigger", True)]
    negatives = [e for e in eval_set if not e.get("should_trigger", True)]

    rng.shuffle(positives)
    rng.shuffle(negatives)

    def split_list(items):
        n = max(1, int(len(items) * holdout))
        return items[n:], items[:n]  # train, test

    pos_train, pos_test = split_list(positives)
    neg_train, neg_test = split_list(negatives)

    train = pos_train + neg_train
    test = pos_test + neg_test
    rng.shuffle(train)
    rng.shuffle(test)

    return train, test


def compute_confusion(results: list) -> dict:
    """Compute precision/recall/accuracy from trigger results."""
    tp = fp = tn = fn = 0
    for r in results:
        triggered = r.get("trigger_rate", 0) >= 0.5
        should = r.get("should_trigger", True)
        if should and triggered:
            tp += 1
        elif should and not triggered:
            fn += 1
        elif not should and triggered:
            fp += 1
        else:
            tn += 1

    total = tp + fp + tn + fn
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    accuracy = (tp + tn) / total if total > 0 else 0

    return {
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "accuracy": round(accuracy, 3),
    }


def update_description(skill_path: str, new_description: str):
    """Update the description in SKILL.md frontmatter."""
    skill_md = Path(skill_path) / "SKILL.md"
    content = skill_md.read_text()

    pattern = r"(description:\s*>?\s*\n(?:\s+.*\n)*|description:\s*[^\n]+\n)"
    if re.search(pattern, content):
        new_desc_yaml = "description: >\n"
        words = new_description.split()
        lines = []
        current_line = ""
        for word in words:
            if current_line and len(current_line) + len(word) + 1 > 70:
                lines.append(f"  {current_line}")
                current_line = word
            else:
                current_line = f"{current_line} {word}".strip()
        if current_line:
            lines.append(f"  {current_line}")

        replacement = new_desc_yaml + "\n".join(lines) + "\n"
        new_content = re.sub(pattern, replacement, content, count=1)
    else:
        new_content = content

    skill_md.write_text(new_content)


def _build_loop_data(skill_name: str, original_desc: str, history: list,
                     train_size: int, test_size: int, holdout: float) -> dict:
    """Build the data dict consumed by generate_report.build_report_html()."""
    best_entry = max(history, key=lambda h: h.get("test_score", 0)) if history else {}
    return {
        "skill_name": skill_name,
        "original_description": original_desc,
        "best_description": best_entry.get("description", original_desc),
        "best_score": f"{best_entry.get('test_score', 0):.0%}" if best_entry else "N/A",
        "iterations_run": len(history),
        "holdout": holdout,
        "train_size": train_size,
        "test_size": test_size,
        "history": history,
    }


def run_loop(eval_set_path: str, skill_path: str, model: str = None,
             max_iterations: int = 5, holdout: float = 0.4,
             verbose: bool = False) -> dict:
    """Run the full eval+improve loop."""
    skill_path = Path(skill_path).resolve()
    eval_set = json.loads(Path(eval_set_path).read_text())

    if isinstance(eval_set, dict):
        eval_set = eval_set.get("evals", eval_set.get("queries", []))

    name, original_desc, _ = parse_skill_md(skill_path)
    project_root = find_project_root()

    # Split train/test
    train, test = stratified_split(eval_set, holdout)
    print(f"Train: {len(train)} queries, Test: {len(test)} queries")

    # Live HTML report
    report_path = skill_path / ".skill-eval" / "loop_report.html"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    history = []
    best_description = original_desc
    best_test_score = 0
    improvement_history = []  # For passing to improve_description

    # Write initial live report and open browser
    init_data = _build_loop_data(name, original_desc, history, len(train), len(test), holdout)
    report_path.write_text(build_report_html(init_data, auto_refresh=True))
    try:
        webbrowser.open(f"file://{report_path}")
    except Exception:
        pass

    for iteration in range(1, max_iterations + 1):
        print(f"\n{'=' * 50}")
        print(f"Iteration {iteration}/{max_iterations}")
        print(f"{'=' * 50}")

        _, current_desc, _ = parse_skill_md(skill_path)

        # Single-batch evaluation: combine train+test, then split results
        combined = train + test
        train_queries = {q["query"] for q in train}

        print(f"\nEvaluating {len(combined)} queries (train+test combined)...")
        combined_results = evaluate_queries(
            combined, name, current_desc, project_root,
            num_workers=10, timeout=30, runs_per_query=3,
            model=model,
        )

        # Split results back into train/test
        train_result_list = [r for r in combined_results["results"] if r["query"] in train_queries]
        test_result_list = [r for r in combined_results["results"] if r["query"] not in train_queries]

        train_passed = sum(1 for r in train_result_list if r.get("pass"))
        train_total = len(train_result_list)
        test_passed = sum(1 for r in test_result_list if r.get("pass"))
        test_total = len(test_result_list)

        train_results = {
            "skill_name": name,
            "description": current_desc,
            "results": train_result_list,
            "summary": {"total": train_total, "passed": train_passed, "failed": train_total - train_passed},
        }
        test_results_data = {
            "skill_name": name,
            "description": current_desc,
            "results": test_result_list,
            "summary": {"total": test_total, "passed": test_passed, "failed": test_total - test_passed},
        }

        # Confusion matrix for train
        train_confusion = compute_confusion(train_result_list) if verbose else {}

        entry = {
            "iteration": iteration,
            "description": current_desc,
            "train_passed": train_passed,
            "train_total": train_total,
            "train_score": train_passed / train_total if train_total > 0 else 0,
            "train_results": train_result_list,
            "test_passed": test_passed,
            "test_total": test_total,
            "test_score": test_passed / test_total if test_total > 0 else 0,
            "test_results": test_result_list,
            "train_confusion": train_confusion,
            "is_best": False,
        }

        print(f"\n  Train: {train_passed}/{train_total} ({entry['train_score']:.0%})")
        print(f"  Test:  {test_passed}/{test_total} ({entry['test_score']:.0%})")
        if verbose and train_confusion:
            c = train_confusion
            print(f"  Stats: precision={c['precision']} recall={c['recall']} accuracy={c['accuracy']}")
            print(f"         tp={c['tp']} fp={c['fp']} tn={c['tn']} fn={c['fn']}")

        # Track best by TEST score
        if entry["test_score"] > best_test_score:
            best_test_score = entry["test_score"]
            best_description = current_desc
            entry["is_best"] = True
            print(f"  New best! (test score: {best_test_score:.0%})")

        history.append(entry)

        # Update live report
        live_data = _build_loop_data(name, original_desc, history, len(train), len(test), holdout)
        report_path.write_text(build_report_html(live_data, auto_refresh=True))

        # Perfect score — stop early
        if entry["train_score"] >= 1.0 and entry["test_score"] >= 1.0:
            print("\nPerfect score on both sets. Stopping.")
            break

        # Last iteration — don't improve
        if iteration == max_iterations:
            break

        # Build blinded history for improvement model (strip all test_* keys)
        blinded_entry = {
            "description": current_desc,
            "passed": train_passed,
            "total": train_total,
            "train_passed": train_passed,
            "train_total": train_total,
            "results": train_result_list,
        }
        improvement_history.append(blinded_entry)

        # Improve description via direct function call
        print(f"\nImproving description...")
        log_dir = skill_path / ".skill-eval" / "logs"
        result = improve(
            eval_results=train_results,
            skill_path=str(skill_path),
            model=model,
            previous_attempts=improvement_history,
            log_dir=log_dir,
            iteration=iteration,
        )

        if result.get("success"):
            new_desc = result["new_description"]
            update_description(str(skill_path), new_desc)
            print(f"  Updated description ({len(new_desc)} chars)")
        else:
            print(f"  Improvement failed: {result.get('error', 'unknown')}")

    # Select best by test score across all history
    best_entry = max(history, key=lambda h: h.get("test_score", 0))
    best_description = best_entry["description"]

    # Restore best description if needed
    if best_description != parse_skill_md(skill_path)[1]:
        update_description(str(skill_path), best_description)
        print(f"\nRestored best description (test score: {best_entry['test_score']:.0%})")

    output = {
        "original_description": original_desc,
        "best_description": best_description,
        "best_score": f"{best_entry['test_score']:.0%}",
        "iterations_run": len(history),
        "holdout": holdout,
        "train_size": len(train),
        "test_size": len(test),
        "history": history,
    }

    # Save output
    output_path = skill_path / ".skill-eval" / "loop_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2) + "\n")
    print(f"\nResults saved to {output_path}")

    # Write final HTML report (no auto-refresh)
    report_path.write_text(build_report_html(output, auto_refresh=False))
    print(f"Report: {report_path}")

    print(json.dumps(output, indent=2))
    return output


def main():
    parser = argparse.ArgumentParser(description="Eval + improve loop with train/test split")
    parser.add_argument("--eval-set", required=True, help="JSON file with eval queries")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--model", help="Model ID to use")
    parser.add_argument("--max-iterations", type=int, default=5, help="Max iterations")
    parser.add_argument("--holdout", type=float, default=0.4, help="Test set proportion")
    parser.add_argument("--verbose", action="store_true", help="Show confusion matrix stats")
    args = parser.parse_args()

    result = run_loop(args.eval_set, args.skill_path, args.model,
                      args.max_iterations, args.holdout, args.verbose)

    best_score = result.get("best_score", "0%")
    score_val = float(best_score.rstrip("%")) / 100
    return 0 if score_val >= 0.8 else 1


if __name__ == "__main__":
    sys.exit(main())
