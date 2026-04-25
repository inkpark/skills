#!/usr/bin/env python3
"""Install or preview installing the canonical llm-wiki skill for AI agents.

The canonical source remains this repository's ``skills/llm-wiki`` folder. By

default this helper only reports the source and destination; real writes require
``--confirm``. Existing targets are never replaced unless ``--replace-existing``
is also supplied.

Use ``--platform generic-agent --target <agent-skill-dir>`` for assistants that
can read a copied or symlinked Markdown skill folder but do not have a dedicated
platform default here.
"""
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

SKILL_NAME = "llm-wiki"
PLATFORMS = ("codex", "claude-code", "generic-agent")


def skill_root() -> Path:
    """Return the canonical skill directory in the knowledge repository."""
    return Path(__file__).resolve().parents[1]


def default_target(platform: str) -> Path:
    """Return the conventional per-assistant install target."""
    if platform == "codex":
        return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "skills" / SKILL_NAME
    if platform == "claude-code":
        return Path(os.environ.get("CLAUDE_HOME", Path.home() / ".claude")) / "skills" / SKILL_NAME
    if platform == "generic-agent":
        target = os.environ.get("LLM_WIKI_SKILL_TARGET") or os.environ.get("AI_AGENT_SKILL_TARGET")
        if target:
            return Path(target)
        raise SystemExit(
            "generic-agent requires --target or LLM_WIKI_SKILL_TARGET/AI_AGENT_SKILL_TARGET "
            "because agent skill directories are not standardized."
        )
    raise ValueError(f"unsupported platform: {platform}")


def resolve_target(platform: str, target: str | None) -> Path:
    return Path(target).expanduser().resolve() if target else default_target(platform).expanduser().resolve()


def refuse_self_install(src: Path, dst: Path) -> None:
    """Avoid deleting or nesting the canonical skill during installation."""
    src_resolved = src.resolve()
    dst_resolved = dst.resolve() if dst.exists() else dst
    if dst_resolved == src_resolved:
        raise SystemExit("Refusing to install onto the canonical source directory.")
    try:
        dst_resolved.relative_to(src_resolved)
    except ValueError:
        return
    raise SystemExit("Refusing to install inside the canonical source directory.")


def remove_existing(dst: Path) -> None:
    if dst.is_dir() and not dst.is_symlink():
        shutil.rmtree(dst)
    elif dst.exists() or dst.is_symlink():
        dst.unlink()


def copy_tree(src: Path, dst: Path) -> None:
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def print_plan(platform: str, method: str, src: Path, dst: Path, dry_run: bool) -> None:
    print(f"platform: {platform}")
    print(f"canonical_source: {src}")
    print(f"target: {dst}")
    print(f"method: {method}")
    print(f"strategy: {'create symlink to canonical source' if method == 'symlink' else 'copy canonical skill tree'}")
    print(f"target_exists: {dst.exists() or dst.is_symlink()}")
    print(f"dry_run: {str(dry_run).lower()}")


def install(platform: str, method: str, dry_run: bool, confirm: bool, replace_existing: bool, target: str | None) -> None:
    src = skill_root().resolve()
    dst = resolve_target(platform, target)
    refuse_self_install(src, dst)
    print_plan(platform, method, src, dst, dry_run)

    if dry_run:
        print("result: no files written")
        return
    if not confirm:
        raise SystemExit("Refusing to write without --confirm. Re-run with --dry-run first, then --confirm.")
    if (dst.exists() or dst.is_symlink()) and not replace_existing:
        raise SystemExit("Refusing to replace existing target without --replace-existing.")

    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        remove_existing(dst)

    if method == "copy":
        copy_tree(src, dst)
    elif method == "symlink":
        dst.symlink_to(src, target_is_directory=True)
    else:  # pragma: no cover - argparse prevents this
        raise ValueError(method)
    print("result: installed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=PLATFORMS, required=True)
    parser.add_argument("--method", choices=["copy", "symlink"], default="copy")
    parser.add_argument("--target", help="Optional explicit target directory; defaults to the selected platform's skill path")
    parser.add_argument("--dry-run", action="store_true", help="Print source, target, and strategy without writing")
    parser.add_argument("--confirm", action="store_true", help="Allow a real install after review")
    parser.add_argument("--replace-existing", action="store_true", help="Allow replacing an existing target during a confirmed install")
    args = parser.parse_args()
    install(args.platform, args.method, args.dry_run, args.confirm, args.replace_existing, args.target)


if __name__ == "__main__":
    main()
