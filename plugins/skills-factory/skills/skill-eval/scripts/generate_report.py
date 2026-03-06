#!/usr/bin/env python3
"""HTML report for description optimization progress.

Generates a per-query grid: iterations x queries with pass/fail indicators,
train vs test distinction, polarity coloring, best-row highlighting,
and score badges.

Usage:
    generate_report.py <json-input> -o <output.html> [--skill-name NAME] [--light]
"""

import argparse
import json
import sys
from html import escape
from pathlib import Path


def build_report_html(data: dict, auto_refresh: bool = False,
                      light: bool = False) -> str:
    """Build HTML report from loop results.

    Produces a per-query grid showing pass/fail for every query across
    every iteration, with train/test column distinction and polarity
    coloring (should-trigger vs should-not-trigger).
    """
    skill_name = escape(data.get("skill_name", "skill"))
    original = escape(data.get("original_description", ""))
    best = escape(data.get("best_description", ""))
    best_score = data.get("best_score", "N/A")
    iterations = data.get("iterations_run", 0)
    train_size = data.get("train_size", 0)
    test_size = data.get("test_size", 0)
    history = data.get("history", [])

    # Collect ordered query lists from first iteration
    train_queries: list[dict] = []
    test_queries: list[dict] = []
    if history:
        first = history[0]
        for r in first.get("train_results", first.get("results", [])):
            train_queries.append({
                "query": r["query"],
                "should_trigger": r.get("should_trigger", True),
            })
        for r in first.get("test_results", []):
            test_queries.append({
                "query": r["query"],
                "should_trigger": r.get("should_trigger", True),
            })

    refresh_tag = '    <meta http-equiv="refresh" content="5">\n' if auto_refresh else ""

    # Theme
    if light:
        bg = "#faf9f5"; fg = "#141413"; card_bg = "white"; border = "#e8e6dc"
        th_bg = "#141413"; th_fg = "#faf9f5"; test_th_bg = "#6a9bcc"
        test_cell_bg = "#f0f6fc"; hover_bg = "#faf9f5"; best_bg = "#f5f8f2"
        pass_color = "#788c5d"; fail_color = "#c44"; muted = "#b0aea5"
        score_good_bg = "#eef2e8"; score_good_fg = "#788c5d"
        score_ok_bg = "#fef3c7"; score_ok_fg = "#d97706"
        score_bad_bg = "#fceaea"; score_bad_fg = "#c44"
        desc_bg = "#f5f5f5"
    else:
        bg = "#0a0a0a"; fg = "#e0e0e0"; card_bg = "#1a1a1a"; border = "#333"
        th_bg = "#222"; th_fg = "#e0e0e0"; test_th_bg = "#1a3a5c"
        test_cell_bg = "#0d1a2a"; hover_bg = "#1e1e1e"; best_bg = "#1a2e1a"
        pass_color = "#22c55e"; fail_color = "#ef4444"; muted = "#888"
        score_good_bg = "#052e16"; score_good_fg = "#22c55e"
        score_ok_bg = "#422006"; score_ok_fg = "#f59e0b"
        score_bad_bg = "#450a0a"; score_bad_fg = "#ef4444"
        desc_bg = "#111"

    # Find best iteration
    best_iter = None
    if history:
        if test_queries:
            best_iter = max(history, key=lambda h: h.get("test_passed", 0) or 0).get("iteration")
        else:
            best_iter = max(history, key=lambda h: h.get("train_passed", 0)).get("iteration")

    # --- Build HTML ---
    parts = []
    parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{refresh_tag}<title>{skill_name} — Description Optimization</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; background: {bg}; color: {fg}; padding: 24px; }}
h1 {{ font-size: 22px; margin-bottom: 4px; }}
.subtitle {{ color: {muted}; margin-bottom: 20px; font-size: 14px; }}
.summary {{ background: {card_bg}; border: 1px solid {border}; border-radius: 8px; padding: 16px; margin-bottom: 16px; }}
.summary p {{ margin: 4px 0; font-size: 14px; }}
.summary .best {{ color: {pass_color}; font-weight: 600; }}
.desc-block {{ font-family: monospace; font-size: 12px; white-space: pre-wrap; background: {desc_bg}; padding: 10px; border-radius: 4px; margin: 4px 0 8px 0; max-height: 100px; overflow-y: auto; }}
.legend {{ display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 12px; font-size: 13px; align-items: center; }}
.legend-item {{ display: flex; align-items: center; gap: 6px; }}
.swatch {{ width: 16px; height: 16px; border-radius: 3px; display: inline-block; }}
.swatch-pos {{ background: {th_bg}; border-bottom: 3px solid {pass_color}; }}
.swatch-neg {{ background: {th_bg}; border-bottom: 3px solid {fail_color}; }}
.swatch-train {{ background: {th_bg}; }}
.swatch-test {{ background: {test_th_bg}; }}
.table-wrap {{ overflow-x: auto; width: 100%; }}
table {{ border-collapse: collapse; background: {card_bg}; border: 1px solid {border}; border-radius: 6px; font-size: 12px; min-width: 100%; }}
th, td {{ padding: 8px; text-align: left; border: 1px solid {border}; white-space: normal; word-wrap: break-word; }}
th {{ background: {th_bg}; color: {th_fg}; font-weight: 500; }}
th.test-col {{ background: {test_th_bg}; }}
th.query-col {{ min-width: 200px; }}
th.pos {{ border-bottom: 3px solid {pass_color}; }}
th.neg {{ border-bottom: 3px solid {fail_color}; }}
td.desc {{ font-family: monospace; font-size: 11px; max-width: 400px; word-wrap: break-word; }}
td.result {{ text-align: center; font-size: 16px; min-width: 40px; }}
td.test-result {{ background: {test_cell_bg}; }}
.pass {{ color: {pass_color}; }}
.fail {{ color: {fail_color}; }}
.rate {{ font-size: 9px; color: {muted}; display: block; }}
tr:hover {{ background: {hover_bg}; }}
.best-row {{ background: {best_bg}; }}
.score {{ display: inline-block; padding: 2px 6px; border-radius: 4px; font-weight: 600; font-size: 11px; }}
.score-good {{ background: {score_good_bg}; color: {score_good_fg}; }}
.score-ok {{ background: {score_ok_bg}; color: {score_ok_fg}; }}
.score-bad {{ background: {score_bad_bg}; color: {score_bad_fg}; }}
</style>
</head>
<body>
<h1>{skill_name} — Description Optimization</h1>
<p class="subtitle">Train: {train_size} queries | Test: {test_size} queries | {iterations} iteration(s){' (auto-refreshing)' if auto_refresh else ''}</p>
""")

    # Summary
    parts.append(f"""<div class="summary">
<p><strong>Original:</strong></p><div class="desc-block">{original}</div>
<p class="best"><strong>Best:</strong></p><div class="desc-block">{best}</div>
<p><strong>Best score:</strong> {best_score} (test) | <strong>Iterations:</strong> {iterations}</p>
</div>
""")

    # Legend (only if we have query columns)
    if train_queries or test_queries:
        parts.append("""<div class="legend">
<strong>Query columns:</strong>
<span class="legend-item"><span class="swatch swatch-pos"></span> Should trigger</span>
<span class="legend-item"><span class="swatch swatch-neg"></span> Should NOT trigger</span>
<span class="legend-item"><span class="swatch swatch-train"></span> Train</span>
<span class="legend-item"><span class="swatch swatch-test"></span> Test</span>
</div>
""")

    # Table header
    parts.append("""<div class="table-wrap">
<table>
<thead><tr>
<th>Iter</th><th>Train</th><th>Test</th><th class="query-col">Description</th>
""")

    for q in train_queries:
        pol = "pos" if q["should_trigger"] else "neg"
        parts.append(f'<th class="{pol}">{escape(q["query"])}</th>\n')

    for q in test_queries:
        pol = "pos" if q["should_trigger"] else "neg"
        parts.append(f'<th class="test-col {pol}">{escape(q["query"])}</th>\n')

    parts.append("</tr></thead>\n<tbody>\n")

    # Rows
    for h in history:
        iteration = h.get("iteration", "?")
        train_results = h.get("train_results", h.get("results", []))
        test_results = h.get("test_results", [])
        description = h.get("description", "")

        train_by_q = {r["query"]: r for r in train_results}
        test_by_q = {r["query"]: r for r in test_results} if test_results else {}

        # Aggregate correct/total runs
        def agg_runs(results):
            correct = total = 0
            for r in results:
                runs = r.get("runs", 0)
                triggers = r.get("triggers", 0)
                total += runs
                if r.get("should_trigger", True):
                    correct += triggers
                else:
                    correct += runs - triggers
            return correct, total

        train_correct, train_runs = agg_runs(train_results)
        test_correct, test_runs = agg_runs(test_results)

        def score_cls(correct, total):
            if total > 0:
                ratio = correct / total
                if ratio >= 0.8:
                    return "score-good"
                elif ratio >= 0.5:
                    return "score-ok"
            return "score-bad"

        row_cls = ' class="best-row"' if iteration == best_iter else ""

        parts.append(f'<tr{row_cls}>\n')
        parts.append(f'<td>{iteration}</td>\n')
        parts.append(f'<td><span class="score {score_cls(train_correct, train_runs)}">{train_correct}/{train_runs}</span></td>\n')
        parts.append(f'<td><span class="score {score_cls(test_correct, test_runs)}">{test_correct}/{test_runs}</span></td>\n')
        parts.append(f'<td class="desc">{escape(description)}</td>\n')

        # Train query cells
        for q in train_queries:
            r = train_by_q.get(q["query"], {})
            did_pass = r.get("pass", False)
            triggers = r.get("triggers", 0)
            runs = r.get("runs", 0)
            icon = "\u2713" if did_pass else "\u2717"
            css = "pass" if did_pass else "fail"
            parts.append(f'<td class="result {css}">{icon}<span class="rate">{triggers}/{runs}</span></td>\n')

        # Test query cells
        for q in test_queries:
            r = test_by_q.get(q["query"], {})
            did_pass = r.get("pass", False)
            triggers = r.get("triggers", 0)
            runs = r.get("runs", 0)
            icon = "\u2713" if did_pass else "\u2717"
            css = "pass" if did_pass else "fail"
            parts.append(f'<td class="result test-result {css}">{icon}<span class="rate">{triggers}/{runs}</span></td>\n')

        parts.append("</tr>\n")

    parts.append("</tbody>\n</table>\n</div>\n")
    parts.append("</body>\n</html>\n")

    return "".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Generate description optimization HTML report")
    parser.add_argument("input", help="JSON file with loop results (or - for stdin)")
    parser.add_argument("-o", "--output", default=None, help="Output HTML path (default: stdout)")
    parser.add_argument("--skill-name", default="", help="Skill name for title")
    parser.add_argument("--light", action="store_true", help="Use light theme")
    args = parser.parse_args()

    if args.input == "-":
        data = json.load(sys.stdin)
    else:
        data = json.loads(Path(args.input).read_text())

    if args.skill_name:
        data["skill_name"] = args.skill_name

    html = build_report_html(data, light=args.light)

    if args.output:
        Path(args.output).write_text(html)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(html)

    return 0


if __name__ == "__main__":
    sys.exit(main())
