#!/usr/bin/env python3
"""Description optimization with extended thinking via Anthropic API.

Calls the Anthropic Python SDK to generate improved skill descriptions
based on eval results (failed triggers, false positives, previous attempts).
Falls back to claude CLI if SDK is not installed.

Usage:
    improve_description.py --eval-results <json> --skill-path <dir> \
        [--model <id>] [--history <json>] [--test-results <json>] \
        [--log-dir <dir>] [--iteration <n>]
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

MAX_DESCRIPTION_CHARS = 1024


def build_improvement_prompt(skill_name: str, current_description: str,
                             eval_results: dict, skill_content: str,
                             previous_attempts: list = None,
                             test_results: dict = None) -> str:
    """Build the prompt for description improvement."""
    failed_triggers = []
    false_positives = []

    for r in eval_results.get("results", []):
        if not r.get("pass", r.get("passed")):
            if r.get("should_trigger") and r.get("trigger_rate", 0) < 0.5:
                failed_triggers.append(r)
            elif not r.get("should_trigger") and r.get("trigger_rate", 0) >= 0.5:
                false_positives.append(r)

    # Build scores summary
    summary = eval_results.get("summary", {})
    train_score = f"{summary.get('passed', 0)}/{summary.get('total', 0)}"
    if test_results:
        ts = test_results.get("summary", {})
        test_score = f"{ts.get('passed', 0)}/{ts.get('total', 0)}"
        scores_summary = f"Train: {train_score}, Test: {test_score}"
    else:
        scores_summary = f"Score: {train_score}"

    prompt = f"""You are optimizing a skill description for a Claude Code skill called "{skill_name}". A "skill" is sort of like a prompt, but with progressive disclosure -- there's a title and description that Claude sees when deciding whether to use the skill, and then if it does use the skill, it reads the .md file which has lots more details and potentially links to other resources in the skill folder like helper files and scripts and additional documentation or examples.

The description appears in Claude's "available_skills" list. When a user sends a query, Claude decides whether to invoke the skill based solely on the title and on this description. Your goal is to write a description that triggers for relevant queries, and doesn't trigger for irrelevant ones.

Here's the current description:
<current_description>
"{current_description}"
</current_description>

Current scores ({scores_summary}):
<scores_summary>
"""

    if failed_triggers:
        prompt += "FAILED TO TRIGGER (should have triggered but didn't):\n"
        for r in failed_triggers:
            triggers = r.get("triggers", r.get("trigger_count", 0))
            runs = r.get("runs", r.get("total_runs", 0))
            prompt += f'  - "{r["query"]}" (triggered {triggers}/{runs} times)\n'
        prompt += "\n"

    if false_positives:
        prompt += "FALSE TRIGGERS (triggered but shouldn't have):\n"
        for r in false_positives:
            triggers = r.get("triggers", r.get("trigger_count", 0))
            runs = r.get("runs", r.get("total_runs", 0))
            prompt += f'  - "{r["query"]}" (triggered {triggers}/{runs} times)\n'
        prompt += "\n"

    if previous_attempts:
        prompt += "PREVIOUS ATTEMPTS (do NOT repeat these -- try something structurally different):\n\n"
        for h in previous_attempts[-5:]:
            train_s = f"{h.get('train_passed', h.get('passed', 0))}/{h.get('train_total', h.get('total', 0))}"
            test_s = None
            if h.get("test_passed") is not None:
                test_s = f"{h.get('test_passed')}/{h.get('test_total', '?')}"
            score_str = f"train={train_s}" + (f", test={test_s}" if test_s else "")
            prompt += f'<attempt {score_str}>\n'
            prompt += f'Description: "{h.get("description", "")}"\n'
            if "results" in h:
                prompt += "Train results:\n"
                for r in h["results"]:
                    status = "PASS" if r.get("pass") else "FAIL"
                    triggers = r.get("triggers", 0)
                    runs = r.get("runs", 0)
                    prompt += f'  [{status}] "{r["query"][:80]}" (triggered {triggers}/{runs})\n'
            if h.get("note"):
                prompt += f'Note: {h["note"]}\n'
            prompt += "</attempt>\n\n"

    prompt += f"""</scores_summary>

Skill content (for context on what the skill does):
<skill_content>
{skill_content}
</skill_content>

Based on the failures, write a new and improved description that is more likely to trigger correctly. When I say "based on the failures", it's a bit of a tricky line to walk because we don't want to overfit to the specific cases you're seeing. So what I DON'T want you to do is produce an ever-expanding list of specific queries that this skill should or shouldn't trigger for. Instead, try to generalize from the failures to broader categories of user intent and situations where this skill would be useful or not useful.

Concretely, your description should not be more than about 100-200 words, even if that comes at the cost of accuracy.

Tips for writing effective descriptions:
- Phrased in the imperative: "Use this skill for..." rather than "this skill does..."
- Focus on user intent, not implementation details
- Make it distinctive and competitive with other skills
- Be creative -- mix up the style in different iterations
- Generalize: cover the category, not just specific examples
- MUST be under {MAX_DESCRIPTION_CHARS} characters

Please respond with only the new description text in <new_description> tags, nothing else."""

    return prompt


def improve_via_api(prompt: str, model: str = None, log_dir: Path = None,
                    iteration: int = None) -> tuple:
    """Call Anthropic API with extended thinking. Returns (description, transcript)."""
    try:
        import anthropic
    except ImportError:
        return None, {"error": "anthropic SDK not installed"}

    client = anthropic.Anthropic()
    model = model or "claude-sonnet-4-20250514"

    response = client.messages.create(
        model=model,
        max_tokens=16000,
        thinking={"type": "enabled", "budget_tokens": 10000},
        messages=[{"role": "user", "content": prompt}],
    )

    thinking_text = ""
    text = ""
    for block in response.content:
        if block.type == "thinking":
            thinking_text = block.thinking
        elif block.type == "text":
            text = block.text

    # Parse <new_description> tags
    match = re.search(r"<new_description>(.*?)</new_description>", text, re.DOTALL)
    description = match.group(1).strip().strip('"') if match else text.strip().strip('"')

    transcript = {
        "iteration": iteration,
        "prompt": prompt,
        "thinking": thinking_text,
        "response": text,
        "parsed_description": description,
        "char_count": len(description),
        "over_limit": len(description) > MAX_DESCRIPTION_CHARS,
    }

    # Multi-turn shortening if over limit
    if len(description) > MAX_DESCRIPTION_CHARS:
        shorten_prompt = (
            f"Your description is {len(description)} characters, which exceeds the "
            f"hard {MAX_DESCRIPTION_CHARS} character limit. Please rewrite it to be under "
            f"{MAX_DESCRIPTION_CHARS} characters while preserving the most important trigger "
            f"words and intent coverage. Respond with only the new description in "
            f"<new_description> tags."
        )
        shorten_response = client.messages.create(
            model=model,
            max_tokens=16000,
            thinking={"type": "enabled", "budget_tokens": 10000},
            messages=[
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": text},
                {"role": "user", "content": shorten_prompt},
            ],
        )

        shorten_thinking = ""
        shorten_text = ""
        for block in shorten_response.content:
            if block.type == "thinking":
                shorten_thinking = block.thinking
            elif block.type == "text":
                shorten_text = block.text

        match = re.search(r"<new_description>(.*?)</new_description>", shorten_text, re.DOTALL)
        shortened = match.group(1).strip().strip('"') if match else shorten_text.strip().strip('"')

        transcript["rewrite_prompt"] = shorten_prompt
        transcript["rewrite_thinking"] = shorten_thinking
        transcript["rewrite_response"] = shorten_text
        transcript["rewrite_description"] = shortened
        transcript["rewrite_char_count"] = len(shortened)
        description = shortened

    transcript["final_description"] = description

    # Save transcript
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"improve_iter_{iteration or 'unknown'}.json"
        log_file.write_text(json.dumps(transcript, indent=2))

    return description, transcript


def improve_via_cli(prompt: str, model: str = None) -> tuple:
    """Fallback: call claude CLI. Returns (description, transcript)."""
    print("WARNING: anthropic SDK not available, falling back to claude CLI "
          "(no extended thinking, no multi-turn shortening)", file=sys.stderr)

    cmd = ["claude", "-p", prompt, "--output-format", "text"]
    if model:
        cmd.extend(["--model", model])

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)
        if result.returncode != 0:
            return "", {"error": f"CLI error: {result.stderr[:200]}"}

        text = result.stdout.strip()
        match = re.search(r"<new_description>(.*?)</new_description>", text, re.DOTALL)
        description = match.group(1).strip().strip('"') if match else text.strip().strip('"')

        if len(description) > MAX_DESCRIPTION_CHARS:
            description = description[:MAX_DESCRIPTION_CHARS - 3] + "..."

        return description, {"response": text, "final_description": description}
    except FileNotFoundError:
        return "", {"error": "claude CLI not found"}
    except subprocess.TimeoutExpired:
        return "", {"error": "claude CLI timed out"}


def improve(eval_results: dict, skill_path: str, model: str = None,
            previous_attempts: list = None, test_results: dict = None,
            log_dir: Path = None, iteration: int = None,
            use_api: bool = False) -> dict:
    """Run one improvement iteration. Returns dict with success, new_description, transcript.

    Args:
        use_api: If True, use Anthropic API with extended thinking.
                 If False (default), use claude CLI (subscription).
    """
    skill_path = Path(skill_path).resolve()
    name, current_desc, content = parse_skill_md(skill_path)

    prompt = build_improvement_prompt(
        name, current_desc, eval_results, content,
        previous_attempts=previous_attempts,
        test_results=test_results,
    )

    # CLI first (uses subscription), API only when explicitly requested
    if use_api:
        description, transcript = improve_via_api(prompt, model, log_dir, iteration)
        if description is None:
            description, transcript = improve_via_cli(prompt, model)
    else:
        description, transcript = improve_via_cli(prompt, model)

    if not description:
        return {"success": False, "error": transcript.get("error", "Failed to generate description"),
                "transcript": transcript}

    return {
        "success": True,
        "skill_name": name,
        "original_description": current_desc,
        "new_description": description,
        "char_count": len(description),
        "transcript": transcript,
    }


def main():
    parser = argparse.ArgumentParser(description="Improve skill description with extended thinking")
    parser.add_argument("--eval-results", required=True, help="JSON file with trigger eval results")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--model", help="Model ID to use")
    parser.add_argument("--history", help="JSON file with previous attempts")
    parser.add_argument("--test-results", help="JSON file with test set results (for blinded reporting)")
    parser.add_argument("--log-dir", help="Directory for transcript logs")
    parser.add_argument("--iteration", type=int, help="Current iteration number")
    parser.add_argument("--prompt-only", action="store_true",
                        help="Output the improvement prompt and exit (for in-session use)")
    parser.add_argument("--use-api", action="store_true",
                        help="Use Anthropic API with extended thinking (default: CLI)")
    args = parser.parse_args()

    eval_results = json.loads(Path(args.eval_results).read_text())
    history = json.loads(Path(args.history).read_text()) if args.history else None
    test_results = json.loads(Path(args.test_results).read_text()) if args.test_results else None

    # Prompt-only mode: output the prompt for in-session use, no execution
    if args.prompt_only:
        skill_path = Path(args.skill_path).resolve()
        name, current_desc, content = parse_skill_md(skill_path)
        prompt = build_improvement_prompt(
            name, current_desc, eval_results, content,
            previous_attempts=history, test_results=test_results,
        )
        print(prompt)
        sys.exit(0)

    log_dir = Path(args.log_dir) if args.log_dir else None

    result = improve(
        eval_results, args.skill_path, args.model,
        previous_attempts=history,
        test_results=test_results,
        log_dir=log_dir,
        iteration=args.iteration,
        use_api=args.use_api,
    )

    # Output without transcript for cleaner piping
    output = {k: v for k, v in result.items() if k != "transcript"}
    print(json.dumps(output, indent=2))

    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
