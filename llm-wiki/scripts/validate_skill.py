#!/usr/bin/env python3
"""Validate the portable llm-wiki skill package without side effects.

This checker is intentionally stdlib-only and dry-run-only. It never imports or
runs Graphify, never installs packages, and never writes outside temporary
directories created for validation.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable

SKILL_NAME = "llm-wiki"
REQUIRED_REFS = {
    "wiki-schema.md",
    "graphify.md",
    "ai-agent-integration.md",
    "codex.md",
    "claude-code.md",
}
EXPECTED_RAW_TO_SOURCE_PAGE = {
    "raw/example-source-a.md": "wiki/sources/example-source-a.md",
    "raw/example-source-b.md": "wiki/sources/example-source-b.md",
}
GRAPHIFY_REQUIRED_TERMS = (
    "graphifyy",
    "graphify",
    "graph.html",
    "graph.json",
    "GRAPH_REPORT.md",
    "graphify-out/wiki",
    "graphify-out/raw-audit",
    "network/API/cost",
)
BANNED_SKILL_CORE_SNIPPETS = (
    "~/.codex",
    "~/.claude",
    ".codex/skills",
    ".claude/skills",
    "graphify codex install",
    "graphify claude install",
)
BANNED_PROJECT_SPECIFIC_SNIPPETS = (
    "/mnt/d/" + "notes",
    "Barret" + "_China",
    "chencheng" + "pro",
    "Matt " + "Pocock",
    "raw/" + "Post by " + "@",
    "notes " + "vau" + "lt",
    "this " + "vau" + "lt",
)


class ValidationError(AssertionError):
    """Raised when a validation check fails."""


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValidationError("SKILL.md must start with YAML frontmatter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValidationError("SKILL.md frontmatter is not closed")
    data: dict[str, str] = {}
    for line in parts[1].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValidationError(f"frontmatter line lacks ':' separator: {line!r}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def assert_contains(text: str, needles: Iterable[str], context: str) -> None:
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise ValidationError(f"{context} missing required terms: {missing}")


def check_skill_frontmatter(root: Path) -> None:
    text = read(root / "skills" / SKILL_NAME / "SKILL.md")
    meta = parse_frontmatter(text)
    if meta.get("name") != SKILL_NAME:
        raise ValidationError(f"frontmatter name must be {SKILL_NAME!r}")
    description = meta.get("description", "")
    if len(description) < 40:
        raise ValidationError("frontmatter description must be descriptive enough for discovery")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", meta["name"]):
        raise ValidationError("frontmatter name must be lowercase hyphenated")


def check_portable_core(root: Path) -> None:
    text = read(root / "skills" / SKILL_NAME / "SKILL.md")
    banned = [snippet for snippet in BANNED_SKILL_CORE_SNIPPETS if snippet in text]
    if banned:
        raise ValidationError(f"SKILL.md core contains platform-specific implementation snippets: {banned}")
    assert_contains(
        text,
        ["raw/", "wiki/", "graphify-out/", "references/wiki-schema.md", "references/graphify.md"],
        "SKILL.md portable core",
    )


def check_references(root: Path) -> None:
    refs_dir = root / "skills" / SKILL_NAME / "references"
    missing = sorted(name for name in REQUIRED_REFS if not (refs_dir / name).is_file())
    if missing:
        raise ValidationError(f"missing required references: {missing}")
    agent_text = read(refs_dir / "ai-agent-integration.md")
    assert_contains(
        agent_text,
        ["generic-agent", "LLM_WIKI_SKILL_TARGET", "AI_AGENT_SKILL_TARGET", "Pointer fallback"],
        "references/ai-agent-integration.md",
    )
    graphify_text = read(refs_dir / "graphify.md")
    assert_contains(graphify_text, GRAPHIFY_REQUIRED_TERMS, "references/graphify.md")
    if "raw/" not in read(refs_dir / "graphifyignore-proposal.md"):
        raise ValidationError("graphifyignore proposal must mention raw/ policy")


def check_no_project_specific_content(root: Path) -> None:
    skill_root = root / "skills" / SKILL_NAME
    offenders: list[str] = []
    for path in sorted(skill_root.rglob("*")):
        if not path.is_file() or path.name == "validate_skill.py":
            continue
        text = read(path)
        for snippet in BANNED_PROJECT_SPECIFIC_SNIPPETS:
            if snippet in text:
                offenders.append(f"{rel(path, root)} contains {snippet!r}")
    if offenders:
        raise ValidationError("project-specific content remains: " + "; ".join(offenders))


def check_first_pass_page_plan(root: Path) -> None:
    raw_dir = root / "raw"
    raw_files = sorted(rel(path, root) for path in raw_dir.glob("*.md")) if raw_dir.exists() else []
    expected_raw = sorted(EXPECTED_RAW_TO_SOURCE_PAGE)
    if raw_files and raw_files != expected_raw:
        raise ValidationError(f"raw source set changed; update page plan. expected={expected_raw}, actual={raw_files}")

    plan = read(root / "skills" / SKILL_NAME / "references" / "first-pass-page-plan.md")
    for raw_path, page_path in EXPECTED_RAW_TO_SOURCE_PAGE.items():
        assert_contains(plan, [raw_path, page_path], "first-pass page plan")

    concept_pages = sorted(set(re.findall(r"wiki/concepts/[a-z0-9-]+\.md", plan)))
    if len(concept_pages) > 4:
        raise ValidationError(f"first-pass concept set is too broad: {concept_pages}")


def check_samples(root: Path) -> None:
    samples_dir = root / "skills" / SKILL_NAME / "samples"
    for name, expected_type in (("source-page.md", "source"), ("concept-page.md", "concept")):
        text = read(samples_dir / name)
        if not text.startswith("---\n"):
            raise ValidationError(f"sample {name} lacks frontmatter")
        assert_contains(text, [f"type: {expected_type}", "status: draft", "raw/", "updated:"], f"sample {name}")


def check_graphify_out_empty(root: Path) -> None:
    output_root = root / "graphify-out"
    if output_root.exists():
        files = sorted(rel(path, root) for path in output_root.rglob("*") if path.is_file())
        if files:
            raise ValidationError(f"graphify-out contains files despite no approved real graph run: {files}")


def run_command(command: list[str], root: Path) -> str:
    completed = subprocess.run(command, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    return completed.stdout.strip()


def check_helper_dry_runs(root: Path) -> None:
    commands = [
        [sys.executable, "skills/llm-wiki/scripts/install_skill.py", "--help"],
        [sys.executable, "skills/llm-wiki/scripts/install_skill.py", "--dry-run", "--platform", "codex"],
        [sys.executable, "skills/llm-wiki/scripts/install_skill.py", "--dry-run", "--platform", "claude-code"],
        [
            sys.executable,
            "skills/llm-wiki/scripts/install_skill.py",
            "--dry-run",
            "--platform",
            "generic-agent",
            "--target",
            "/tmp/llm-wiki-generic-agent-skill",
        ],
        [sys.executable, "skills/llm-wiki/scripts/run_graphify.py", "--help"],
    ]
    if (root / "wiki").is_dir():
        commands.append([sys.executable, "skills/llm-wiki/scripts/run_graphify.py", "--dry-run", "--mode", "wiki-only"])
    if (root / "raw").is_dir():
        commands.append(
            [
                sys.executable,
                "skills/llm-wiki/scripts/run_graphify.py",
                "--dry-run",
                "--mode",
                "raw-audit",
                "--allow-raw-audit",
            ]
        )
    for command in commands:
        output = run_command(command, root)
        joined = " ".join(command)
        if "--help" in command:
            if "usage:" not in output:
                raise ValidationError(f"help command did not print usage: {joined}")
            continue
        if "install_skill.py" in joined:
            if "dry_run: true" not in output or "no files written" not in output:
                raise ValidationError(f"install dry-run did not prove no writes: {joined}")
            continue
        if "run_graphify.py" in joined and "graphify not executed" not in output:
            raise ValidationError(f"graphify dry-run did not prove no graph execution: {joined}")

    with tempfile.TemporaryDirectory(prefix="llm-wiki-graphify-helper-") as tmp:
        knowledge_root = Path(tmp).resolve()
        (knowledge_root / "wiki").mkdir()
        (knowledge_root / "raw").mkdir()
        (knowledge_root / "nested" / "cwd").mkdir(parents=True)
        (knowledge_root / "wiki" / "index.md").write_text("# Index\n", encoding="utf-8")
        (knowledge_root / "raw" / "source.md").write_text("# Source\n", encoding="utf-8")
        helper = root / "skills" / SKILL_NAME / "scripts" / "run_graphify.py"

        cwd_discovery = run_command(
            [sys.executable, str(helper), "--dry-run", "--mode", "wiki-only"],
            knowledge_root / "nested" / "cwd",
        )
        if f"repo_root: {knowledge_root}" not in cwd_discovery or "graphify not executed" not in cwd_discovery:
            raise ValidationError("graphify helper did not discover the caller's knowledge repository from cwd")

        explicit_root = run_command(
            [
                sys.executable,
                str(helper),
                "--repo-root",
                str(knowledge_root),
                "--dry-run",
                "--mode",
                "raw-audit",
                "--allow-raw-audit",
            ],
            root,
        )
        if f"repo_root: {knowledge_root}" not in explicit_root or "graphify not executed" not in explicit_root:
            raise ValidationError("graphify helper did not honor explicit --repo-root for installed-helper usage")


def check_no_pycache(root: Path) -> None:
    files = sorted(rel(path, root) for path in (root / "skills" / SKILL_NAME).rglob("*") if path.name == "__pycache__" or path.suffix == ".pyc")
    if files:
        raise ValidationError(f"skill package contains generated Python cache files: {files}")


def run_all(root: Path) -> list[str]:
    checks = [
        check_skill_frontmatter,
        check_portable_core,
        check_references,
        check_no_project_specific_content,
        check_first_pass_page_plan,
        check_samples,
        check_graphify_out_empty,
        check_helper_dry_runs,
        check_no_pycache,
    ]
    passed: list[str] = []
    for check in checks:
        check(root)
        passed.append(check.__name__)
    return passed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=repo_root(), help="Vault/repo root to validate")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    try:
        passed = run_all(root)
    except ValidationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    for check in passed:
        print(f"PASS: {check}")
    print(f"PASS: validated {SKILL_NAME} skill package at {root / 'skills' / SKILL_NAME}")


if __name__ == "__main__":
    main()
