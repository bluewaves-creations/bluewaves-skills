#!/usr/bin/env python3
"""Auto-generate .eval.yaml files from skill metadata.

Parses SKILL.md description to extract trigger scenarios and generates
starter eval files with category-appropriate Tier 1 checks. Can use
claude CLI for higher-quality query generation.

Usage:
    eval_scaffold.py --skill-path <dir> [--queries <json>] [--use-claude]
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
from utils import find_skill_eval_dir, parse_skill_md


# Category detection heuristics based on description keywords
CATEGORY_PATTERNS = {
    "document-creation": [
        r"generat\w+\s+(pdf|document|epub|docx|report)",
        r"creat\w+\s+(pdf|document|epub|docx|file)",
        r"render\w*\s+(pdf|document|markdown)",
        r"convert\w*\s+\w+\s+to\s+(pdf|docx|epub)",
    ],
    "workflow": [
        r"automat\w+",
        r"pipeline",
        r"process\w*\s+(data|files|images)",
        r"workflow",
        r"deploy",
        r"build\s+and",
    ],
    "mcp-enhancement": [
        r"mcp",
        r"model\s+context\s+protocol",
        r"external\s+(api|service|tool)",
        r"integrat\w+\s+with",
    ],
}

# Category-specific default checks
CATEGORY_CHECKS = {
    "document-creation": [
        {"type": "file_exists", "target": "output.*", "comment": "Verify output file was created"},
    ],
    "workflow": [
        {"type": "exit_code", "expected": 0, "comment": "Verify workflow completed successfully"},
    ],
    "mcp-enhancement": [
        {"type": "contains", "target": "transcript.md", "expected": "Tool:", "comment": "Verify tool was called"},
    ],
}


def detect_category(description: str) -> str:
    """Detect skill category from description text."""
    desc_lower = description.lower()
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, desc_lower):
                return category
    return "generic"


def extract_trigger_phrases(description: str, skill_name: str) -> list:
    """Extract potential trigger phrases from a skill description using verb phrase extraction."""
    triggers = []

    # Extract verb phrases (imperative form: "Generate PDFs", "Create websites", etc.)
    verb_phrases = re.findall(
        r"(?:^|\.\s+|,\s+|;\s+|when\s+(?:the\s+)?user\s+)([A-Z][a-z]+(?:\s+\w+){1,6})",
        description,
    )
    for phrase in verb_phrases:
        # Make it a user query
        query = f"I need to {phrase.lower().rstrip('.')}"
        if 20 < len(query) < 200:
            triggers.append(query)

    # Extract "Use when..." / "Use this skill when..." clauses
    when_clauses = re.findall(
        r"(?:use\s+(?:this\s+skill\s+)?when|trigger\s+when|use\s+for)\s+(.+?)(?:\.|$)",
        description, re.IGNORECASE,
    )
    for clause in when_clauses:
        clause = clause.strip()
        if 10 < len(clause) < 200:
            triggers.append(clause)

    # Extract quoted examples or specific keywords
    keywords = re.findall(r'"([^"]{10,80})"', description)
    triggers.extend(keywords)

    # Deduplicate and limit
    seen = set()
    unique = []
    for t in triggers:
        normalized = t.lower().strip()
        if normalized not in seen:
            seen.add(normalized)
            unique.append(t)

    return unique[:8]


def generate_queries_via_claude(skill_name: str, description: str, content: str) -> list:
    """Use claude -p to generate high-quality trigger queries."""
    if not shutil.which("claude"):
        return []

    prompt = f"""Generate trigger test queries for a Claude Code skill.

Skill name: {skill_name}
Description: {description}

Skill content (first 80 lines):
{chr(10).join(content.split(chr(10))[:80])}

Generate exactly 10 should-trigger queries and 10 should-NOT-trigger queries.

Rules:
- Should-trigger queries: realistic user prompts that would benefit from this skill. Include detail (file paths, context, specifics). Vary the phrasing.
- Should-NOT-trigger queries: near-miss queries that share some keywords but are clearly outside scope. Include queries for adjacent/competing skills.
- All queries should be substantive (not just "read this file" or "help me").
- Each query should be 1-2 sentences.

Respond with ONLY a JSON array:
[
  {{"query": "...", "should_trigger": true}},
  {{"query": "...", "should_trigger": false}}
]"""

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "text"],
            capture_output=True, text=True, timeout=60, env=env,
        )
        if result.returncode != 0:
            return []

        text = result.stdout.strip()
        # Extract JSON array from response
        json_match = re.search(r"\[.*\]", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(text)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return []


def generate_negative_queries(skill_name: str, description: str) -> list:
    """Generate skill-specific negative queries (not just 'What's the weather?')."""
    negatives = []
    readable = skill_name.replace("-", " ")

    # Generic unrelated queries
    negatives.append({"query": "What's the weather like today?", "should_trigger": False})

    # Near-miss: mentions skill-adjacent concepts
    desc_lower = description.lower()
    if any(w in desc_lower for w in ["pdf", "document", "report"]):
        negatives.append({"query": f"Read my PDF file and summarize the contents", "should_trigger": False})
    if any(w in desc_lower for w in ["image", "photo", "video"]):
        negatives.append({"query": "Describe what's in this screenshot", "should_trigger": False})
    if any(w in desc_lower for w in ["code", "script", "function"]):
        negatives.append({"query": "Explain what this code does in plain English", "should_trigger": False})
    if any(w in desc_lower for w in ["website", "html", "web"]):
        negatives.append({"query": "Help me debug this CSS layout issue", "should_trigger": False})
    if any(w in desc_lower for w in ["skill", "eval", "test"]):
        negatives.append({"query": "Write unit tests for my Python module", "should_trigger": False})

    # Always include at least 2 negatives
    if len(negatives) < 2:
        negatives.append({"query": "Tell me a joke about programming", "should_trigger": False})

    return negatives[:5]


def generate_eval_yaml(name: str, query: str, should_trigger: bool, checks: list, assertions: list) -> str:
    """Generate a single .eval.yaml file content."""
    lines = [
        f"name: {name}",
        f'query: "{query}"',
        f"should_trigger: {str(should_trigger).lower()}",
    ]

    if checks:
        lines.append("checks:")
        for check in checks:
            comment = check.pop("comment", None)
            if comment:
                lines.append(f"  # {comment}")
            lines.append(f"  - type: {check['type']}")
            for k, v in check.items():
                if k != "type":
                    lines.append(f"    {k}: {json.dumps(v) if not isinstance(v, str) else v}")

    if assertions:
        lines.append("assertions:")
        for assertion in assertions:
            lines.append(f'  - "{assertion}"')

    return "\n".join(lines) + "\n"


def scaffold(skill_path: Path, queries_json: str = None, use_claude: bool = False) -> int:
    """Generate eval files for a skill."""
    skill_path = Path(skill_path).resolve()
    name, description, content = parse_skill_md(skill_path)

    eval_dir = find_skill_eval_dir(skill_path)
    evals_dir = eval_dir / "evals"
    evals_dir.mkdir(parents=True, exist_ok=True)

    category = detect_category(description)
    default_checks = CATEGORY_CHECKS.get(category, [])

    # Get trigger queries
    if queries_json:
        queries = json.loads(Path(queries_json).read_text() if Path(queries_json).exists() else queries_json)
    elif use_claude:
        print("Generating queries via claude CLI...")
        queries = generate_queries_via_claude(name, description, content)
        if not queries:
            print("  Claude generation failed, falling back to heuristic extraction")
            queries = []
    else:
        queries = []

    if not queries:
        # Heuristic: extract from description
        phrases = extract_trigger_phrases(description, name)
        queries = [{"query": q, "should_trigger": True} for q in phrases]

    if not queries:
        # Fallback: generate generic triggers from skill name
        readable_name = name.replace("-", " ")
        queries = [
            {"query": f"Help me {readable_name}", "should_trigger": True},
            {"query": f"I need to {readable_name} for my project", "should_trigger": True},
        ]

    # Add skill-specific negative evals
    negatives = generate_negative_queries(name, description)
    queries.extend(negatives)

    created = 0
    for i, q in enumerate(queries):
        query_text = q if isinstance(q, str) else q.get("query", "")
        should_trigger = True if isinstance(q, str) else q.get("should_trigger", True)

        # Generate eval name from query
        eval_name = re.sub(r"[^a-z0-9]+", "-", query_text.lower().strip())[:40].strip("-")
        if not eval_name:
            eval_name = f"eval-{i}"

        filename = f"{eval_name}.eval.yaml"
        filepath = evals_dir / filename

        if filepath.exists():
            continue

        checks = [dict(c) for c in default_checks] if should_trigger else []
        assertions = (
            [f"TODO: Add assertion for '{eval_name}' -- what should a good output contain?"]
            if should_trigger
            else []
        )

        eval_content = generate_eval_yaml(eval_name, query_text, should_trigger, checks, assertions)
        filepath.write_text(eval_content)
        created += 1

    pos_count = sum(1 for q in queries if (q.get("should_trigger", True) if isinstance(q, dict) else True))
    neg_count = sum(1 for q in queries if (not q.get("should_trigger", True) if isinstance(q, dict) else False))

    print(f"Scaffolded {created} eval files in {evals_dir}")
    print(f"  Category detected: {category}")
    print(f"  Positive evals: {pos_count}")
    print(f"  Negative evals: {neg_count}")
    print()
    print("Next: Review and customize the generated .eval.yaml files,")
    print("then run eval_workspace.py run to execute them.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Auto-scaffold eval files for a skill")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--queries", help="JSON file or string with trigger queries")
    parser.add_argument("--use-claude", action="store_true",
                        help="Use claude CLI to generate high-quality queries")
    args = parser.parse_args()

    return scaffold(args.skill_path, args.queries, args.use_claude)


if __name__ == "__main__":
    sys.exit(main() or 0)
