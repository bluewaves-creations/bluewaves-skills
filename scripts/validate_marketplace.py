#!/usr/bin/env python3
"""Comprehensive marketplace validator.

Five validation layers:
  1. Skills          — shells out to skills-ref validate
  2. Plugin metadata — plugin.json per Anthropic manifest spec
  3. Marketplace     — marketplace.json structure & schema
  4. Cross-consistency — marketplace ↔ plugin.json agreement
  5. Skill quality   — skill-shaper best-practice checks (WARN only)

Exit 0 if no failures (warnings are OK). Exit 1 on any failure.
Python 3.8+, stdlib only.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ── constants ────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"
MARKETPLACE_PATH = REPO_ROOT / ".claude-plugin" / "marketplace.json"
SUBMODULE_SKILLS_REF = REPO_ROOT / "deps" / "agentskills" / "skills-ref"

KEBAB_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(-[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?$"
)
FIRST_SECOND_PERSON_RE = re.compile(
    r"(?:^|(?<=\.\s))\s*(?:I |You |We |My |Your )", re.MULTILINE
)
TRIGGER_CONTEXT_RE = re.compile(r"\b(?:whenever|when|use when|triggers?\s+(?:on|when))\b", re.IGNORECASE)
EXTRANEOUS_FILES = {"README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md"}

SEPARATOR = "=" * 60

# ── state ────────────────────────────────────────────────────────────────────

passed = 0
failed = 0
warned = 0
failure_details: list[str] = []
warning_details: list[str] = []


# ── helpers ──────────────────────────────────────────────────────────────────


def record_pass(label: str) -> None:
    global passed
    passed += 1
    print(f"  {'PASS':<8} {label}")


def record_fail(label: str, detail: str = "") -> None:
    global failed
    failed += 1
    print(f"  {'FAIL':<8} {label}")
    if detail:
        failure_details.append(f"--- {label} ---\n{detail}")


def record_warn(label: str, detail: str = "") -> None:
    global warned
    warned += 1
    print(f"  {'WARN':<8} {label}")
    if detail:
        warning_details.append(f"--- {label} ---\n{detail}")


def section(title: str) -> None:
    print()
    print(SEPARATOR)
    print(f"  {title}")
    print(SEPARATOR)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Return (frontmatter dict, body) from a SKILL.md string.

    Handles simple YAML scalars and folded/literal block scalars (> / |).
    """
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 4 :].lstrip("\n")
    fm: dict[str, str] = {}
    current_key = ""
    current_val_lines: list[str] = []
    is_block = False

    def _flush() -> None:
        if current_key:
            fm[current_key] = " ".join(
                l.strip() for l in current_val_lines if l.strip()
            )

    for line in raw.split("\n"):
        # top-level key
        m = re.match(r"^([a-z][\w-]*):\s*(.*)", line)
        if m and not (is_block and line.startswith(" ")):
            _flush()
            current_key = m.group(1)
            val = m.group(2).strip()
            is_block = val in (">", "|", ">-", "|-")
            current_val_lines = [] if is_block else [val]
        else:
            current_val_lines.append(line)
    _flush()
    return fm, body


def discover_skills() -> list[tuple[str, str, Path]]:
    """Return sorted list of (plugin_name, skill_name, skill_dir)."""
    results = []
    for skill_dir in sorted(PLUGINS_DIR.glob("*/skills/*/")):
        if (skill_dir / "SKILL.md").exists():
            plugin_name = skill_dir.parent.parent.name
            results.append((plugin_name, skill_dir.name, skill_dir))
    return results


def discover_plugins() -> list[tuple[str, Path]]:
    """Return sorted list of (plugin_name, plugin_dir)."""
    results = []
    for pdir in sorted(PLUGINS_DIR.iterdir()):
        if pdir.is_dir() and (pdir / ".claude-plugin" / "plugin.json").exists():
            results.append((pdir.name, pdir))
    return results


def find_skills_ref() -> str | None:
    """Locate the skills-ref CLI binary."""
    # 1. On PATH
    which = shutil.which("skills-ref")
    if which:
        return which
    # 2. In submodule venv
    venv_bin = SUBMODULE_SKILLS_REF / ".venv" / "bin" / "skills-ref"
    if venv_bin.exists():
        return str(venv_bin)
    return None


def ensure_skills_ref() -> str | None:
    """Find or auto-install skills-ref. Return path or None."""
    path = find_skills_ref()
    if path:
        return path
    # Try auto-install
    if SUBMODULE_SKILLS_REF.is_dir():
        print("  skills-ref not found — installing from submodule...")
        try:
            subprocess.run(
                ["uv", "pip", "install", "-e", str(SUBMODULE_SKILLS_REF)],
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
        return find_skills_ref()
    return None


# ── Layer 1: Skills (skills-ref validate) ────────────────────────────────────


def layer1_skills(skills: list[tuple[str, str, Path]]) -> None:
    section("Layer 1: Skills (skills-ref validate)")
    sr = ensure_skills_ref()
    if sr is None:
        record_fail(
            "skills-ref",
            "skills-ref CLI not found and could not be installed.\n"
            "Run: git submodule update --init && "
            "uv pip install -e deps/agentskills/skills-ref/",
        )
        return
    for plugin_name, skill_name, skill_dir in skills:
        label = f"{plugin_name}/{skill_name}"
        try:
            subprocess.run(
                [sr, "validate", str(skill_dir)],
                check=True,
                capture_output=True,
                text=True,
            )
            record_pass(label)
        except subprocess.CalledProcessError as exc:
            output = (exc.stdout or "") + (exc.stderr or "")
            record_fail(label, output.strip())


# ── Layer 2: Plugin metadata (plugin.json) ───────────────────────────────────


def layer2_plugins(plugins: list[tuple[str, Path]]) -> None:
    section("Layer 2: Plugin metadata (plugin.json)")
    for name, pdir in plugins:
        pj_path = pdir / ".claude-plugin" / "plugin.json"

        # exists
        if not pj_path.exists():
            record_fail(f"{name}: file exists", f"{pj_path} not found")
            continue
        record_pass(f"{name}: file exists")

        # valid JSON
        try:
            data = json.loads(pj_path.read_text())
        except json.JSONDecodeError as exc:
            record_fail(f"{name}: valid JSON", str(exc))
            continue
        record_pass(f"{name}: valid JSON")

        # required: name
        pj_name = data.get("name", "")
        if not pj_name:
            record_fail(f"{name}: required field 'name'", "name is missing")
        else:
            record_pass(f"{name}: required field 'name'")

        # kebab-case name
        if pj_name and not KEBAB_RE.match(pj_name):
            record_fail(
                f"{name}: name kebab-case",
                f"'{pj_name}' does not match {KEBAB_RE.pattern}",
            )
        elif pj_name:
            record_pass(f"{name}: name kebab-case")

        # name matches directory
        if pj_name and pj_name != name:
            record_fail(
                f"{name}: name matches dir",
                f"plugin.json name '{pj_name}' != directory '{name}'",
            )
        elif pj_name:
            record_pass(f"{name}: name matches dir")

        # semver version
        version = data.get("version", "")
        if not version:
            record_fail(f"{name}: version present", "version field is missing")
        elif not SEMVER_RE.match(version):
            record_fail(
                f"{name}: semver version",
                f"'{version}' is not valid semver",
            )
        else:
            record_pass(f"{name}: semver version")

        # description (WARN if outside 50-200 chars, not FAIL)
        desc = data.get("description", "")
        if not desc:
            record_fail(f"{name}: description present", "description is missing")
        else:
            dlen = len(desc)
            if dlen < 50 or dlen > 200:
                record_warn(
                    f"{name}: description length ({dlen} chars)",
                    f"Recommended 50-200 chars, got {dlen}",
                )
            else:
                record_pass(f"{name}: description length")

        # author
        author = data.get("author")
        if not author:
            record_fail(f"{name}: author present", "author field is missing")
        elif isinstance(author, dict) and not author.get("name"):
            record_fail(
                f"{name}: author.name present",
                "author object missing 'name'",
            )
        else:
            record_pass(f"{name}: author present")

        # component path checks
        for comp_field in ("commands", "hooks", "mcpServers", "agents"):
            comp = data.get(comp_field)
            if comp is None:
                continue
            # comp may be a string path or nested object with paths
            paths_to_check: list[str] = []
            if isinstance(comp, str):
                paths_to_check.append(comp)
            elif isinstance(comp, dict):
                for v in comp.values():
                    if isinstance(v, str):
                        paths_to_check.append(v)
                    elif isinstance(v, dict):
                        for vv in v.values():
                            if isinstance(vv, str) and (
                                vv.startswith("./") or "/" in vv
                            ):
                                paths_to_check.append(vv)
            for p in paths_to_check:
                if not p.startswith("./"):
                    record_fail(
                        f"{name}: {comp_field} path '{p}'",
                        "Component paths must start with './'",
                    )
                elif ".." in p:
                    record_fail(
                        f"{name}: {comp_field} path '{p}'",
                        "Component paths must not contain '..'",
                    )
                else:
                    resolved = pdir / p
                    if not resolved.exists():
                        record_fail(
                            f"{name}: {comp_field} path '{p}' exists",
                            f"{resolved} not found on disk",
                        )
                    else:
                        record_pass(f"{name}: {comp_field} path '{p}' exists")


# ── Layer 3: Marketplace registry (marketplace.json) ─────────────────────────


def layer3_marketplace(plugins_on_disk: list[tuple[str, Path]]) -> dict | None:
    section("Layer 3: Marketplace registry (marketplace.json)")

    if not MARKETPLACE_PATH.exists():
        record_fail("file exists", f"{MARKETPLACE_PATH} not found")
        return None
    record_pass("file exists")

    try:
        data = json.loads(MARKETPLACE_PATH.read_text())
    except json.JSONDecodeError as exc:
        record_fail("valid JSON", str(exc))
        return None
    record_pass("valid JSON")

    # required top-level fields
    for field in ("name", "owner", "plugins"):
        if field not in data:
            record_fail(f"field: {field}", f"'{field}' missing from marketplace.json")
        else:
            record_pass(f"field: {field}")

    meta = data.get("metadata", {})
    if not meta.get("version"):
        record_fail("field: metadata.version", "metadata.version missing")
    elif not SEMVER_RE.match(meta["version"]):
        record_fail(
            "field: metadata.version",
            f"'{meta['version']}' is not valid semver",
        )
    else:
        record_pass("field: metadata.version")

    if not meta.get("description"):
        record_fail("field: metadata.description", "metadata.description missing")
    else:
        record_pass("field: metadata.description")

    mp_plugins = data.get("plugins", [])
    if not isinstance(mp_plugins, list):
        record_fail("plugins is array", f"plugins is {type(mp_plugins).__name__}")
        return data

    # Per-entry checks
    disk_names = {name for name, _ in plugins_on_disk}
    mp_names: set[str] = set()

    for entry in mp_plugins:
        ename = entry.get("name", "<unnamed>")
        mp_names.add(ename)

        # name + source required
        if not entry.get("name"):
            record_fail(f"{ename}: name present", "missing 'name'")
        elif not KEBAB_RE.match(ename):
            record_fail(
                f"{ename}: name kebab-case",
                f"'{ename}' does not match kebab-case",
            )
        else:
            record_pass(f"{ename}: name kebab-case")

        if not entry.get("source"):
            record_fail(f"{ename}: source present", "missing 'source'")
        else:
            source_path = REPO_ROOT / entry["source"]
            if not source_path.is_dir():
                record_fail(
                    f"{ename}: source path exists",
                    f"{source_path} not found",
                )
            else:
                record_pass(f"{ename}: source path exists")

    # orphan check: disk plugins not in marketplace
    for dname in sorted(disk_names):
        if dname in mp_names:
            record_pass(f"{dname}: listed in marketplace")
        else:
            record_fail(
                f"{dname}: listed in marketplace",
                f"Plugin directory '{dname}' exists on disk but is not in marketplace.json",
            )

    return data


# ── Layer 4: Cross-consistency ────────────────────────────────────────────────


def layer4_cross(
    mp_data: dict | None,
    plugins: list[tuple[str, Path]],
    skills: list[tuple[str, str, Path]],
) -> None:
    section("Layer 4: Cross-consistency")
    if mp_data is None:
        record_fail("marketplace data", "Skipped — marketplace.json invalid")
        return

    mp_plugins = {e["name"]: e for e in mp_data.get("plugins", []) if "name" in e}
    plugin_json_cache: dict[str, dict] = {}

    for name, pdir in plugins:
        pj_path = pdir / ".claude-plugin" / "plugin.json"
        try:
            pj = json.loads(pj_path.read_text())
        except Exception:
            pj = {}
        plugin_json_cache[name] = pj

        mp_entry = mp_plugins.get(name)
        if mp_entry is None:
            # already reported in layer 3
            continue

        # name match
        pj_name = pj.get("name", "")
        if pj_name == mp_entry.get("name", ""):
            record_pass(f"{name}: name matches plugin.json")
        else:
            record_fail(
                f"{name}: name matches plugin.json",
                f"marketplace '{mp_entry.get('name')}' != plugin.json '{pj_name}'",
            )

        # version match
        pj_ver = pj.get("version", "")
        mp_ver = mp_entry.get("version", "")
        if pj_ver and mp_ver and pj_ver == mp_ver:
            record_pass(f"{name}: version matches plugin.json")
        elif pj_ver and mp_ver:
            record_fail(
                f"{name}: version matches plugin.json",
                f"marketplace '{mp_ver}' != plugin.json '{pj_ver}'",
            )
        else:
            record_warn(
                f"{name}: version comparison",
                "Version missing in one or both locations",
            )

    # skill reachability
    listed_plugins = set(mp_plugins.keys())
    for plugin_name, skill_name, _ in skills:
        label = f"{plugin_name}/{skill_name}"
        if plugin_name in listed_plugins:
            record_pass(f"{label}: reachable")
        else:
            record_fail(
                f"{label}: reachable",
                f"Skill belongs to plugin '{plugin_name}' which is not in marketplace",
            )


# ── Layer 5: Skill quality (skill-shaper best practices) ─────────────────────


def layer5_quality(skills: list[tuple[str, str, Path]]) -> None:
    section("Layer 5: Skill quality (skill-shaper best practices)")

    for plugin_name, skill_name, skill_dir in skills:
        label = f"{plugin_name}/{skill_name}"
        skill_path = skill_dir / "SKILL.md"
        text = skill_path.read_text()
        fm, body = parse_frontmatter(text)
        desc = fm.get("description", "")

        # description voice — no first/second person sentence starts
        if desc and FIRST_SECOND_PERSON_RE.search(desc):
            record_warn(
                f"{label}: description voice",
                "Description contains first/second person sentence start",
            )
        else:
            record_pass(f"{label}: description voice")

        # description trigger context — should contain "when" or "use when"
        if desc and TRIGGER_CONTEXT_RE.search(desc):
            record_pass(f"{label}: description trigger context")
        elif desc:
            record_warn(
                f"{label}: description trigger context",
                "Description lacks 'when'/'use when' trigger context",
            )
        else:
            record_warn(
                f"{label}: description trigger context",
                "No description found in frontmatter",
            )

        # body size — under 500 lines
        body_lines = body.count("\n") + (1 if body and not body.endswith("\n") else 0)
        if body_lines > 500:
            record_warn(
                f"{label}: body size ({body_lines} lines)",
                f"Exceeds 500-line recommended maximum",
            )
        else:
            record_pass(f"{label}: body size ({body_lines} lines)")

        # reference depth — files in references/ should not link to references/
        refs_dir = skill_dir / "references"
        if refs_dir.is_dir():
            nested = False
            for ref_file in sorted(refs_dir.glob("*.md")):
                content = ref_file.read_text()
                # Strip fenced code blocks to avoid matching example links
                stripped = re.sub(r"```[\s\S]*?```", "", content)
                if "](references/" in stripped:
                    nested = True
                    record_warn(
                        f"{label}: reference depth",
                        f"{ref_file.name} contains nested references/ links",
                    )
                    break
            if not nested:
                record_pass(f"{label}: reference depth")

        # no extraneous files
        found = EXTRANEOUS_FILES & {f.name for f in skill_dir.iterdir() if f.is_file()}
        if found:
            record_warn(
                f"{label}: no extraneous files",
                f"Found: {', '.join(sorted(found))}",
            )
        else:
            record_pass(f"{label}: no extraneous files")


# ── main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    skills = discover_skills()
    plugins = discover_plugins()

    layer1_skills(skills)
    layer2_plugins(plugins)
    mp_data = layer3_marketplace(plugins)
    layer4_cross(mp_data, plugins, skills)
    layer5_quality(skills)

    # summary
    print()
    print(SEPARATOR)
    print(f"  Results: {passed} passed, {failed} failed, {warned} warning(s)")
    print(SEPARATOR)

    if failure_details:
        print("\nFailures:\n")
        for d in failure_details:
            print(d)
            print()

    if warning_details:
        print("\nWarnings:\n")
        for d in warning_details:
            print(d)
            print()

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
