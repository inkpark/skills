#!/usr/bin/env python3
"""Validate the portable llm-wiki skill package without side effects.

This checker is intentionally stdlib-only and dry-run-only. It never installs
packages and never writes outside temporary directories created for validation.
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
    "ai-agent-integration.md",
    "claude-code.md",
}
EXPECTED_RAW_TO_SOURCE_PAGE = {
    "raw/example-source-a.md": "wiki/sources/example-source-a.md",
    "raw/example-source-b.md": "wiki/sources/example-source-b.md",
}
BANNED_SKILL_CORE_SNIPPETS = (
    "~/.claude",
    ".claude/skills",
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
    return Path(__file__).resolve().parents[1]


def resolve_validation_paths(candidate: Path) -> tuple[Path, Path]:
    root = candidate.expanduser().resolve(strict=False)
    skill_root = root / "skills" / SKILL_NAME
    if (skill_root / "SKILL.md").is_file():
        return root, skill_root
    direct_skill_root = root / SKILL_NAME
    if (direct_skill_root / "SKILL.md").is_file():
        return root, direct_skill_root
    if root.name == SKILL_NAME and (root / "SKILL.md").is_file():
        return root.parent, root
    raise ValidationError(
        "--repo-root must point to a repository root containing llm-wiki (directly or under skills/) or to the llm-wiki skill directory itself"
    )


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


def check_skill_frontmatter(root: Path, skill_root: Path) -> None:
    text = read(skill_root / "SKILL.md")
    meta = parse_frontmatter(text)
    if meta.get("name") != SKILL_NAME:
        raise ValidationError(f"frontmatter name must be {SKILL_NAME!r}")
    description = meta.get("description", "")
    if len(description) < 40:
        raise ValidationError("frontmatter description must be descriptive enough for discovery")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", meta["name"]):
        raise ValidationError("frontmatter name must be lowercase hyphenated")


def check_portable_core(root: Path, skill_root: Path) -> None:
    text = read(skill_root / "SKILL.md")
    banned = [snippet for snippet in BANNED_SKILL_CORE_SNIPPETS if snippet in text]
    if banned:
        raise ValidationError(f"SKILL.md core contains platform-specific implementation snippets: {banned}")
    assert_contains(
        text,
        [
            "raw/",
            "wiki/",
            "session working directory",
            "wiki language",
            "raw file",
            "references/wiki-schema.md",
            "Source generation",
            "Concept synthesis",
            "sub-agents",
        ],
        "SKILL.md portable core",
    )


def check_references(root: Path, skill_root: Path) -> None:
    refs_dir = skill_root / "references"
    missing = sorted(name for name in REQUIRED_REFS if not (refs_dir / name).is_file())
    if missing:
        raise ValidationError(f"missing required references: {missing}")
    agent_text = read(refs_dir / "ai-agent-integration.md")
    assert_contains(
        agent_text,
        ["Portability contract", "Integration patterns", "Pointer fallback"],
        "references/ai-agent-integration.md",
    )
    schema_text = read(refs_dir / "wiki-schema.md")
    assert_contains(
        schema_text,
        [
            "language:",
            "Repository root resolution",
            "session working directory",
            "Language policy",
            "wiki/config.md",
            "wiki/manifest.json",
            "batch_size",
            "type: config",
            "clickable raw file links",
            "请选择或指定本次 wiki 使用的语种",
            "Source generation",
            "Concept synthesis",
            "sub-agents",
        ],
        "references/wiki-schema.md",
    )


def check_no_project_specific_content(root: Path, skill_root: Path) -> None:
    offenders: list[str] = []
    for path in sorted(skill_root.rglob("*")):
        if not path.is_file() or path.name == "validate_skill.py" or path.suffix == ".pyc":
            continue
        text = read(path)
        for snippet in BANNED_PROJECT_SPECIFIC_SNIPPETS:
            if snippet in text:
                offenders.append(f"{rel(path, root)} contains {snippet!r}")
    if offenders:
        raise ValidationError("project-specific content remains: " + "; ".join(offenders))


def check_first_pass_page_plan(root: Path, skill_root: Path) -> None:
    raw_dir = root / "raw"
    raw_files = sorted(rel(path, root) for path in raw_dir.glob("*.md")) if raw_dir.exists() else []
    expected_raw = sorted(EXPECTED_RAW_TO_SOURCE_PAGE)
    if raw_files and raw_files != expected_raw:
        raise ValidationError(f"raw source set changed; update page plan. expected={expected_raw}, actual={raw_files}")

    plan = read(skill_root / "references" / "first-pass-page-plan.md")
    assert_contains(
        plan,
        [
            "Wiki language",
            "wiki/config.md",
            "wiki/manifest.json",
            "batch size",
            "language:",
            "](../../raw/",
            "Source generation",
            "Concept synthesis",
            "sub-agents",
        ],
        "first-pass page plan",
    )
    for raw_path, page_path in EXPECTED_RAW_TO_SOURCE_PAGE.items():
        assert_contains(plan, [raw_path, page_path], "first-pass page plan")

    concept_pages = sorted(set(re.findall(r"wiki/concepts/[a-z0-9-]+\.md", plan)))
    if len(concept_pages) > 4:
        raise ValidationError(f"first-pass concept set is too broad: {concept_pages}")


def check_samples(root: Path, skill_root: Path) -> None:
    samples_dir = skill_root / "samples"
    for name, expected_type in (("source-page.md", "source"), ("concept-page.md", "concept")):
        text = read(samples_dir / name)
        if not text.startswith("---\n"):
            raise ValidationError(f"sample {name} lacks frontmatter")
        assert_contains(text, [f"type: {expected_type}", "status: draft", "language:", "raw/", "](../../raw/", "updated:"], f"sample {name}")


def check_no_generated_outputs(root: Path, skill_root: Path) -> None:
    generated_roots = [root / "wiki"]
    offenders: list[str] = []
    for output_root in generated_roots:
        if output_root.exists():
            offenders.extend(rel(path, root) for path in output_root.rglob("*") if path.is_file())
    if offenders:
        raise ValidationError(f"repository contains generated knowledge output files: {sorted(offenders)}")


def run_command(command: list[str], root: Path) -> str:
    completed = subprocess.run(command, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    return completed.stdout.strip()


def check_install_copy_filter(root: Path, skill_root: Path) -> None:
    install_script = skill_root / "scripts" / "install_skill.py"
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / SKILL_NAME
        run_command(
            [
                sys.executable,
                str(install_script),
                "--platform",
                "generic-agent",
                "--target",
                str(target),
                "--confirm",
            ],
            skill_root,
        )
        offenders = sorted(
            rel(path, target)
            for path in target.rglob("*")
            if path.is_file() and (
                path.name in {".DS_Store", "settings.local.json"}
                or path.suffix == ".pyc"
                or ".omx" in path.parts
                or "__pycache__" in path.parts
            )
        )
    if offenders:
        raise ValidationError(f"install copy leaked filtered local artifacts: {offenders}")


def run_all(root: Path) -> tuple[list[str], Path]:
    workspace_root, skill_root = resolve_validation_paths(root)
    checks = [
        check_skill_frontmatter,
        check_portable_core,
        check_references,
        check_no_project_specific_content,
        check_first_pass_page_plan,
        check_samples,
        check_no_generated_outputs,
        check_install_copy_filter,
    ]
    passed: list[str] = []
    for check in checks:
        check(workspace_root, skill_root)
        passed.append(check.__name__)
    return passed, skill_root


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=repo_root(), help="Repository root or llm-wiki skill directory to validate")
    args = parser.parse_args()
    root = args.repo_root.expanduser().resolve(strict=False)
    try:
        passed, skill_root = run_all(root)
    except ValidationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    for check in passed:
        print(f"PASS: {check}")
    print(f"PASS: validated {SKILL_NAME} skill package at {skill_root}")


if __name__ == "__main__":
    main()
