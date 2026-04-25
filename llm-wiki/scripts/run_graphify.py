#!/usr/bin/env python3
"""Validate or run guarded Graphify modes for the LLM Wiki.

Dry-runs validate paths and print the command plan without importing or running
Graphify. Real execution is deliberately gated by ``--execute`` plus
``--confirm-cost-network`` because Graphify may use dependencies, network, or
model/API-backed extraction depending on local configuration.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
from pathlib import Path

MODES = {
    "raw-map": {"input": "raw", "output": "graphify-out/raw-map"},
    "wiki-refresh": {"input": "wiki", "output": "graphify-out/wiki"},
    "raw-audit": {"input": "raw", "output": "graphify-out/raw-audit"},
}


def discover_repo_root(start: Path) -> Path | None:
    """Find the caller's knowledge repository by walking up from ``start``.

    Installed copies of this helper live under assistant skill directories such
    as ``~/.codex/skills/llm-wiki``. In that mode the helper path is not the
    knowledge repository, so discovery must be based on the caller's working
    directory (or an explicit override), not on ``__file__``.
    """
    start = start.expanduser().resolve()
    for candidate in (start, *start.parents):
        if (candidate / "wiki").is_dir() or (candidate / "raw").is_dir():
            return candidate
    return None


def repo_root(value: str | None = None) -> Path:
    """Return the knowledge repository root for this Graphify run.

    Precedence:
    1. explicit ``--repo-root`` argument;
    2. ``LLM_WIKI_REPO_ROOT`` environment variable;
    3. nearest parent of the current working directory containing ``wiki/`` or
       ``raw/``.
    """
    selected = value or os.environ.get("LLM_WIKI_REPO_ROOT")
    if selected:
        return Path(selected).expanduser().resolve()

    discovered = discover_repo_root(Path.cwd())
    if discovered:
        return discovered

    raise SystemExit(
        "Could not find a knowledge repository from the current working directory. "
        "Run from a repo containing wiki/ or raw/, or pass --repo-root /path/to/repo "
        "(or set LLM_WIKI_REPO_ROOT)."
    )


def contained(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def require_contained(root: Path, label: str, path: Path) -> None:
    if not contained(root, path):
        raise SystemExit(f"Refusing {label} outside repo root: {path}")


def nonempty_dir(path: Path) -> bool:
    return path.is_dir() and any(path.iterdir())


def graphify_help() -> str:
    exe = shutil.which("graphify")
    if not exe:
        raise SystemExit("graphify CLI not found. Install graphifyy only after explicit approval.")
    return subprocess.check_output([exe, "--help"], text=True, stderr=subprocess.STDOUT)


def output_flag(help_text: str) -> str:
    """Return the supported output flag, or fail safely when unconfirmed."""
    if re.search(r"(^|[\s,])--out([\s,=]|$)", help_text):
        return "--out"
    if re.search(r"(^|[\s,])--output([\s,=]|$)", help_text):
        return "--output"
    raise SystemExit("graphify help did not confirm --out/--output support; use the documented staging workflow manually")


def build_plan(mode: str, repo_root_arg: str | None = None) -> tuple[Path, Path, Path]:
    root = repo_root(repo_root_arg).resolve()
    spec = MODES[mode]
    input_path = (root / spec["input"]).resolve()
    output_path = (root / spec["output"]).resolve()

    require_contained(root, "input path", input_path)
    require_contained(root, "output path", output_path)
    if not input_path.is_dir():
        raise SystemExit(f"Input directory does not exist: {input_path}")
    return root, input_path, output_path


def run(args: argparse.Namespace) -> None:
    if args.mode == "raw-audit" and not args.allow_raw_audit:
        raise SystemExit("raw-audit mode requires --allow-raw-audit")

    root, input_path, output_path = build_plan(args.mode, args.repo_root)
    print(f"mode: {args.mode}")
    print(f"repo_root: {root}")
    print(f"input: {input_path}")
    print(f"output: {output_path}")
    print(f"execute: {str(args.execute).lower()}")

    if args.dry_run or not args.execute:
        print("result: dry-run only; graphify not executed")
        if not args.execute:
            print("next_step: pass --execute only after explicit approval")
        return

    if not args.confirm_cost_network:
        raise SystemExit("Real Graphify execution requires --confirm-cost-network")
    if nonempty_dir(output_path) and not args.replace_existing:
        raise SystemExit("Refusing to write into non-empty output directory without --replace-existing")

    help_text = graphify_help()
    flag = output_flag(help_text)
    output_path.mkdir(parents=True, exist_ok=True)
    command = ["graphify", str(input_path), flag, str(output_path)]
    print("command:", " ".join(command))
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=sorted(MODES), default="raw-map")
    parser.add_argument(
        "--repo-root",
        help=(
            "Knowledge repository root containing wiki/ and/or raw/. Defaults to "
            "LLM_WIKI_REPO_ROOT, then the nearest such parent of the current working directory."
        ),
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate paths and print the plan without running Graphify")
    parser.add_argument("--execute", action="store_true", help="Run Graphify after explicit user approval")
    parser.add_argument("--confirm-cost-network", action="store_true", help="Required with --execute to acknowledge dependency/network/model cost risk")
    parser.add_argument("--replace-existing", action="store_true", help="Allow writing into a non-empty output directory during a real run")
    parser.add_argument("--allow-raw-audit", action="store_true", help="Required with --mode raw-audit; raw-map is the normal raw-to-wiki planning graph mode")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
