#!/usr/bin/env python3
"""Generate interactive HTML eval viewer from workspace results.

Self-contained HTML with two tabs: Outputs (per-eval with prompt,
output, grades, feedback) and Benchmark (stats comparison).

Modes:
  Default:   Write temp HTML and open in browser
  --static:  Write static HTML to path
  --serve:   Start HTTP server with live feedback auto-save

Usage:
    generate_review.py <workspace> --skill-name <name> \
        [--benchmark <json>] [--previous-workspace <dir>] \
        [--static <path>] [--auto-refresh]
    generate_review.py <workspace> --serve [--port 3117] --skill-name <name>
"""

import argparse
import atexit
import base64
import json
import mimetypes
import os
import signal
import subprocess
import sys
import tempfile
import time
import webbrowser
from functools import partial
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# Extensions rendered as inline text
TEXT_EXTENSIONS = {
    ".txt", ".md", ".json", ".csv", ".py", ".js", ".ts", ".tsx", ".jsx",
    ".yaml", ".yml", ".xml", ".html", ".css", ".sh", ".rb", ".go", ".rs",
    ".java", ".c", ".cpp", ".h", ".hpp", ".sql", ".r", ".toml",
}

# Extensions rendered as inline images
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}

# MIME overrides
MIME_OVERRIDES = {
    ".svg": "image/svg+xml",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}

# Files to skip in output listings
METADATA_FILES = {"transcript.md", "user_notes.md", "metrics.json"}


def _get_mime(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in MIME_OVERRIDES:
        return MIME_OVERRIDES[ext]
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


def _embed_file(path: Path) -> dict:
    """Read a file and return an embedded representation."""
    ext = path.suffix.lower()
    mime = _get_mime(path)

    if ext in TEXT_EXTENSIONS:
        try:
            content = path.read_text(errors="replace")
        except OSError:
            content = "(Error reading file)"
        return {"name": path.name, "type": "text", "content": content}

    # Binary (images, PDFs, etc.) — base64
    try:
        raw = path.read_bytes()
        b64 = base64.b64encode(raw).decode("ascii")
    except OSError:
        return {"name": path.name, "type": "error", "content": "(Error reading file)"}

    if ext in IMAGE_EXTENSIONS:
        return {"name": path.name, "type": "image", "mime": mime, "data_uri": f"data:{mime};base64,{b64}"}
    if ext == ".pdf":
        return {"name": path.name, "type": "pdf", "data_uri": f"data:{mime};base64,{b64}"}
    return {"name": path.name, "type": "binary", "mime": mime, "data_uri": f"data:{mime};base64,{b64}"}


def collect_eval_data(workspace: Path) -> list:
    """Collect eval results from workspace runs."""
    evals = []
    runs_dir = workspace / "runs"

    if not runs_dir.exists():
        return evals

    for run_dir in sorted(runs_dir.iterdir()):
        if not run_dir.is_dir():
            continue

        grading_path = run_dir / "grading.json"
        snapshot_path = run_dir / "skill-snapshot.md"
        timing_path = run_dir / "timing.json"

        entry = {
            "run_id": run_dir.name,
            "grading": json.loads(grading_path.read_text()) if grading_path.exists() else None,
            "timing": json.loads(timing_path.read_text()) if timing_path.exists() else None,
            "has_snapshot": snapshot_path.exists(),
        }

        # Collect and embed output files
        outputs_dir = run_dir / "outputs"
        if outputs_dir.exists():
            files = []
            embedded = []
            for f in sorted(outputs_dir.rglob("*")):
                if f.is_file() and f.name not in METADATA_FILES:
                    files.append(str(f.relative_to(outputs_dir)))
                    embedded.append(_embed_file(f))
            entry["output_files"] = files
            entry["embedded_outputs"] = embedded

        evals.append(entry)

    return evals


def build_html(skill_name: str, evals: list, benchmark: dict = None,
               previous_evals: list = None, auto_refresh: bool = False,
               feedback_path: str = None, serve_mode: bool = False) -> str:
    """Build self-contained interactive HTML.

    Tries the full viewer.html template first. Falls back to minimal HTML
    only if the template file doesn't exist.
    """
    template_path = Path(__file__).parent.parent / "assets" / "viewer.html"

    if template_path.exists():
        html = template_path.read_text()
        html = html.replace("__SKILL_NAME__", _escape_html(skill_name))
        html = html.replace("__EVAL_DATA__", json.dumps(evals))
        html = html.replace("__BENCHMARK_DATA__", json.dumps(benchmark or {}))
        html = html.replace("__PREVIOUS_DATA__", json.dumps(previous_evals or []))

        if auto_refresh:
            html = html.replace("<head>", '<head>\n<meta http-equiv="refresh" content="10">')

        if serve_mode:
            # Inject auto-save JS that POSTs to /api/feedback on change
            autosave_js = """
<script>
(function() {
    const _origSaveFeedback = window.saveFeedback || function(){};
    let _saveTimer = null;
    function autoSaveFeedback() {
        clearTimeout(_saveTimer);
        _saveTimer = setTimeout(function() {
            const reviews = Object.entries(feedback || {}).map(function(e) {
                return {run_id: e[0], feedback: e[1], timestamp: new Date().toISOString()};
            });
            if (reviews.length === 0) return;
            fetch('/api/feedback', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({reviews: reviews, status: 'in_progress'})
            }).catch(function(){});
        }, 1000);
    }
    window.saveFeedback = function(id, text) {
        _origSaveFeedback(id, text);
        autoSaveFeedback();
    };
})();
</script>
"""
            html = html.replace("</body>", autosave_js + "</body>")

        if feedback_path and not serve_mode:
            html = html.replace(
                "a.download = 'feedback.json';",
                f"a.download = 'feedback.json';\n    // Feedback also saved to: {feedback_path}",
            )

        return html

    # Fallback: generate minimal HTML
    return _generate_minimal_html(skill_name, evals, benchmark, previous_evals,
                                  auto_refresh, serve_mode)


def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _generate_minimal_html(skill_name: str, evals: list, benchmark: dict = None,
                           previous_evals: list = None, auto_refresh: bool = False,
                           serve_mode: bool = False) -> str:
    """Generate minimal self-contained HTML viewer."""
    refresh_tag = '<meta http-equiv="refresh" content="10">' if auto_refresh else ""

    # Auto-save snippet for serve mode
    autosave_fn = ""
    if serve_mode:
        autosave_fn = """
let _saveTimer = null;
function autoSaveFeedback() {
    clearTimeout(_saveTimer);
    _saveTimer = setTimeout(function() {
        const reviews = Object.entries(feedback).map(([id, text]) => ({
            run_id: id, feedback: text, timestamp: new Date().toISOString()
        }));
        if (reviews.length === 0) return;
        fetch('/api/feedback', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({reviews, status: 'in_progress'})
        }).catch(() => {});
    }, 1000);
}
"""

    autosave_call = "\n    autoSaveFeedback();" if serve_mode else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{refresh_tag}
<title>Eval Review: {_escape_html(skill_name)}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; background: #0a0a0a; color: #e0e0e0; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
h1 {{ font-size: 24px; margin-bottom: 16px; color: #fff; }}
.tabs {{ display: flex; gap: 4px; margin-bottom: 24px; border-bottom: 1px solid #333; }}
.tab {{ padding: 8px 16px; cursor: pointer; border: none; background: transparent; color: #888; font-size: 14px; }}
.tab.active {{ color: #fff; border-bottom: 2px solid #3b82f6; }}
.panel {{ display: none; }} .panel.active {{ display: block; }}
.eval-card {{ background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 16px; margin-bottom: 16px; }}
.eval-card h3 {{ color: #fff; margin-bottom: 8px; }}
.pass {{ color: #22c55e; }} .fail {{ color: #ef4444; }} .skip {{ color: #888; }}
.grade {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }}
.grade.pass {{ background: #052e16; }} .grade.fail {{ background: #450a0a; }}
.feedback {{ width: 100%; min-height: 60px; background: #111; border: 1px solid #333; border-radius: 4px; color: #e0e0e0; padding: 8px; margin-top: 8px; resize: vertical; }}
.nav {{ display: flex; gap: 8px; margin-bottom: 16px; }}
.nav button {{ padding: 6px 12px; background: #333; border: none; color: #fff; border-radius: 4px; cursor: pointer; }}
.nav button:hover {{ background: #444; }}
.submit {{ padding: 8px 24px; background: #3b82f6; border: none; color: #fff; border-radius: 4px; cursor: pointer; margin-top: 16px; }}
.submit:hover {{ background: #2563eb; }}
.embedded-text {{ font-family: monospace; font-size: 12px; white-space: pre-wrap; background: #111; padding: 12px; border-radius: 4px; max-height: 300px; overflow-y: auto; margin: 8px 0; color: #ccc; }}
.embedded-img {{ max-width: 100%; border-radius: 4px; margin: 8px 0; }}
table {{ width: 100%; border-collapse: collapse; }} th, td {{ padding: 8px 12px; text-align: left; border-bottom: 1px solid #333; }}
th {{ color: #888; font-size: 12px; text-transform: uppercase; }}
.stat {{ font-variant-numeric: tabular-nums; }}
</style>
</head>
<body>
<div class="container">
<h1>Eval Review: {_escape_html(skill_name)}</h1>
<div class="tabs">
  <button class="tab active" onclick="showTab('outputs')">Outputs</button>
  <button class="tab" onclick="showTab('benchmark')">Benchmark</button>
</div>

<div id="outputs" class="panel active"></div>
<div id="benchmark" class="panel"></div>

<button class="submit" onclick="submitReviews()">Submit All Reviews</button>
</div>

<script>
const evalData = {json.dumps(evals)};
const benchmarkData = {json.dumps(benchmark or {})};
const previousData = {json.dumps(previous_evals or [])};
const feedback = {{}};
let currentIdx = 0;
{autosave_fn}

function showTab(name) {{
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById(name).classList.add('active');
}}

function renderOutputs() {{
  const panel = document.getElementById('outputs');
  if (!evalData.length) {{ panel.innerHTML = '<p>No eval results found.</p>'; return; }}

  let html = '<div class="nav">';
  html += '<button onclick="navigate(-1)">&larr; Prev</button>';
  html += '<span id="nav-label"></span>';
  html += '<button onclick="navigate(1)">Next &rarr;</button>';
  html += '</div><div id="eval-content"></div>';
  panel.innerHTML = html;
  renderEval(0);
}}

function renderEval(idx) {{
  if (idx < 0 || idx >= evalData.length) return;
  currentIdx = idx;
  const e = evalData[idx];
  document.getElementById('nav-label').textContent = `${{idx + 1}} / ${{evalData.length}}`;

  let html = `<div class="eval-card"><h3>Run: ${{e.run_id}}</h3>`;

  if (e.grading) {{
    const s = e.grading.summary || {{}};
    html += `<p>Pass rate: <span class="${{s.pass_rate >= 0.8 ? 'pass' : 'fail'}}">${{(s.pass_rate * 100).toFixed(0)}}%</span> (${{s.passed}}/${{s.total}})</p>`;

    if (e.grading.expectations) {{
      html += '<div style="margin-top:12px">';
      for (const exp of e.grading.expectations) {{
        const cls = exp.passed === null ? 'skip' : (exp.passed ? 'pass' : 'fail');
        const label = exp.passed === null ? 'PENDING' : (exp.passed ? 'PASS' : 'FAIL');
        const tier = exp.tier ? ` [T${{exp.tier}}]` : '';
        html += `<div style="margin:4px 0"><span class="grade ${{cls}}">${{label}}</span> ${{exp.text}}${{tier}}</div>`;
        if (exp.evidence) html += `<div style="margin-left:60px;color:#888;font-size:12px">${{exp.evidence}}</div>`;
      }}
      html += '</div>';
    }}
  }}

  // Render embedded outputs
  if (e.embedded_outputs && e.embedded_outputs.length) {{
    html += '<div style="margin-top:12px">';
    for (const f of e.embedded_outputs) {{
      html += `<p style="color:#888;font-size:12px;margin-top:8px"><strong>${{f.name}}</strong></p>`;
      if (f.type === 'text') {{
        html += `<div class="embedded-text">${{f.content.replace(/</g,'&lt;').replace(/>/g,'&gt;')}}</div>`;
      }} else if (f.type === 'image') {{
        html += `<img class="embedded-img" src="${{f.data_uri}}" alt="${{f.name}}">`;
      }} else if (f.type === 'pdf') {{
        html += `<iframe src="${{f.data_uri}}" style="width:100%;height:400px;border:1px solid #333;border-radius:4px;margin:8px 0"></iframe>`;
      }} else if (f.data_uri) {{
        html += `<a href="${{f.data_uri}}" download="${{f.name}}" style="color:#3b82f6">Download ${{f.name}}</a>`;
      }}
    }}
    html += '</div>';
  }} else if (e.output_files && e.output_files.length) {{
    html += '<p style="margin-top:12px;color:#888">Output files: ' + e.output_files.join(', ') + '</p>';
  }}

  if (e.timing) {{
    html += `<p style="color:#888">Tokens: ${{(e.timing.total_tokens || 0).toLocaleString()}} | Duration: ${{(e.timing.total_duration_seconds || 0).toFixed(1)}}s</p>`;
  }}

  html += `<textarea class="feedback" placeholder="Your feedback..." oninput="saveFeedback('${{e.run_id}}', this.value)">${{feedback[e.run_id] || ''}}</textarea>`;
  html += '</div>';

  document.getElementById('eval-content').innerHTML = html;
}}

function navigate(delta) {{ renderEval(currentIdx + delta); }}
function saveFeedback(id, text) {{ feedback[id] = text;{autosave_call} }}

function renderBenchmark() {{
  const panel = document.getElementById('benchmark');
  if (!benchmarkData.run_summary) {{ panel.innerHTML = '<p>No benchmark data.</p>'; return; }}

  let html = '<table><tr><th>Config</th><th>Pass Rate</th><th>Time</th><th>Tokens</th></tr>';
  for (const [config, data] of Object.entries(benchmarkData.run_summary)) {{
    if (config === 'delta') continue;
    html += `<tr><td>${{config}}</td><td class="stat">${{(data.pass_rate.mean * 100).toFixed(0)}}% &plusmn; ${{(data.pass_rate.stddev * 100).toFixed(0)}}%</td><td class="stat">${{data.time_seconds.mean.toFixed(1)}}s</td><td class="stat">${{data.tokens.mean.toFixed(0)}}</td></tr>`;
  }}
  html += '</table>';
  panel.innerHTML = html;
}}

function submitReviews() {{
  const reviews = Object.entries(feedback).map(([id, text]) => ({{
    run_id: id, feedback: text, timestamp: new Date().toISOString()
  }}));
  const payload = JSON.stringify({{reviews, status: 'complete'}}, null, 2);
  {'fetch("/api/feedback", {method:"POST", headers:{"Content-Type":"application/json"}, body: payload}).then(() => alert("Feedback saved!")).catch(e => alert("Save failed: " + e));' if serve_mode else "const blob = new Blob([payload], {type: 'application/json'}); const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'feedback.json'; a.click();"}
}}

document.addEventListener('keydown', e => {{
  if (e.target.tagName === 'TEXTAREA') return;
  if (e.key === 'ArrowLeft') navigate(-1);
  if (e.key === 'ArrowRight') navigate(1);
}});

renderOutputs();
renderBenchmark();
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# HTTP server for --serve mode
# ---------------------------------------------------------------------------

def _kill_port(port: int) -> None:
    """Kill any process listening on the given port."""
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True, text=True, timeout=5,
        )
        for pid_str in result.stdout.strip().split("\n"):
            if pid_str.strip():
                try:
                    os.kill(int(pid_str.strip()), signal.SIGTERM)
                except (ProcessLookupError, ValueError):
                    pass
        if result.stdout.strip():
            time.sleep(0.5)
    except subprocess.TimeoutExpired:
        pass
    except FileNotFoundError:
        pass


class ReviewHandler(BaseHTTPRequestHandler):
    """Serves the review HTML and handles feedback saves.

    Regenerates HTML on each GET / so refreshing picks up new outputs.
    """

    def __init__(self, workspace, skill_name, feedback_path, benchmark_path,
                 previous_workspace, *args, **kwargs):
        self.workspace = workspace
        self.skill_name = skill_name
        self.feedback_path = feedback_path
        self.benchmark_path = benchmark_path
        self.previous_workspace = previous_workspace
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            evals = collect_eval_data(self.workspace)
            benchmark = None
            if self.benchmark_path and self.benchmark_path.exists():
                try:
                    benchmark = json.loads(self.benchmark_path.read_text())
                except (json.JSONDecodeError, OSError):
                    pass
            previous = collect_eval_data(self.previous_workspace) if self.previous_workspace else None
            html = build_html(self.skill_name, evals, benchmark, previous,
                              serve_mode=True)
            content = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/api/feedback":
            data = b"{}"
            if self.feedback_path.exists():
                data = self.feedback_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/feedback":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                if not isinstance(data, dict) or "reviews" not in data:
                    raise ValueError("Expected JSON with 'reviews' key")
                self.feedback_path.write_text(json.dumps(data, indent=2) + "\n")
                resp = b'{"ok":true}'
                self.send_response(200)
            except (json.JSONDecodeError, OSError, ValueError) as e:
                resp = json.dumps({"error": str(e)}).encode()
                self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
        else:
            self.send_error(404)

    def log_message(self, fmt, *args):
        pass  # suppress request logging


def main():
    parser = argparse.ArgumentParser(description="Generate interactive HTML eval viewer")
    parser.add_argument("workspace", help="Path to .skill-eval/ workspace")
    parser.add_argument("--skill-name", default="skill", help="Skill name for display")
    parser.add_argument("--benchmark", help="Path to benchmark.json")
    parser.add_argument("--previous-workspace", help="Previous iteration workspace for comparison")
    parser.add_argument("--static", help="Write static HTML to path instead of serving")
    parser.add_argument("--auto-refresh", action="store_true", help="Add auto-refresh meta tag")
    parser.add_argument("-o", "--output", help="Alias for --static")
    parser.add_argument("--serve", action="store_true", help="Start HTTP server with live feedback auto-save")
    parser.add_argument("--port", type=int, default=3117, help="Server port for --serve mode (default: 3117)")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    evals = collect_eval_data(workspace)
    benchmark = json.loads(Path(args.benchmark).read_text()) if args.benchmark else None
    previous_evals = collect_eval_data(Path(args.previous_workspace)) if args.previous_workspace else None

    # --serve mode: HTTP server with feedback auto-save
    if args.serve:
        feedback_path = workspace / "feedback.json"
        benchmark_path = Path(args.benchmark).resolve() if args.benchmark else None
        previous_ws = Path(args.previous_workspace).resolve() if args.previous_workspace else None

        _kill_port(args.port)
        handler = partial(ReviewHandler, workspace.resolve(), args.skill_name,
                          feedback_path, benchmark_path, previous_ws)
        try:
            server = HTTPServer(("127.0.0.1", args.port), handler)
            port = args.port
        except OSError:
            server = HTTPServer(("127.0.0.1", 0), handler)
            port = server.server_address[1]

        url = f"http://localhost:{port}"
        print(f"\n  Eval Viewer (server mode)")
        print(f"  {'─' * 35}")
        print(f"  URL:       {url}")
        print(f"  Workspace: {workspace}")
        print(f"  Feedback:  {feedback_path}")
        print(f"\n  Press Ctrl+C to stop.\n")

        webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
            server.server_close()
        return 0

    # Static / temp file modes
    static_path = args.static or args.output
    feedback_path = str(workspace / "feedback.json") if not static_path else None

    html = build_html(
        args.skill_name, evals, benchmark, previous_evals,
        auto_refresh=args.auto_refresh,
        feedback_path=feedback_path,
    )

    if static_path:
        Path(static_path).write_text(html)
        print(f"Static HTML written to {static_path}")
        return 0

    # Write to temp file and open in browser
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, dir="/tmp")
    tmp.write(html)
    tmp.close()

    atexit.register(lambda: os.unlink(tmp.name) if os.path.exists(tmp.name) else None)

    webbrowser.open(f"file://{tmp.name}")
    print(f"Opened eval viewer in browser: {tmp.name}")
    print("Press Ctrl+C when done reviewing.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
