# Agent Skills Repo Notes

## Repo shape

- This repo is a **skill library**, not an app or package workspace. There is no `package.json`, lockfile, CI workflow, Makefile, or general build/test/lint pipeline at the repo root.
- Each skill should live in a **top-level folder** with `SKILL.md` as the entry point. `references/`, `samples/`, and `scripts/` are optional support folders.
- Treat local runtime state as noise, not source: `.omx/`, `.sisyphus/`, `.gitnexus/`, and `.claude/settings.local.json` are ignored/local artifacts.

## Highest-value files

- `README.md` / `docs/README.zh-CN.md` — repo purpose and the intended top-level skill layout.
- `llm-wiki/SKILL.md` — canonical workflow for the main published skill in this repo.
- `llm-wiki/references/wiki-schema.md` — the durable page schema and language/provenance rules behind `llm-wiki`.
- `llm-wiki/scripts/install_skill.py` — the real install behavior for `codex`, `claude-code`, and `generic-agent` targets.
- `llm-wiki/scripts/validate_skill.py` — the closest thing this repo has to a focused verification command.
- `.claude/skills/gitnexus/*/SKILL.md` — local guidance for GitNexus-backed exploration, impact analysis, debugging, refactoring, and CLI usage.

## llm-wiki rules that are easy to miss

- `raw/` is **immutable source evidence**. Never edit, move, delete, or generate files under it.
- Do not write `wiki/` pages until the target wiki language is explicit in the request or already remembered in `wiki/config.md`.
- For large ingests, `wiki/manifest.json` is required. `llm-wiki` treats **more than 30 raw files** as batch mode, with **20 files per batch** by default.
- Source-page generation and concept synthesis are intentionally separated in `llm-wiki/SKILL.md`; do not collapse them into one undifferentiated pass.
- `wiki/index.md` is a compact navigation page, not the full provenance inventory. Full raw coverage belongs in `wiki/manifest.json`.

## Commands agents are likely to guess wrong

- Install the published skill via npm wrapper: `npx skills@latest add inkpark/skills/llm-wiki`
- Preview a local install without writing: `python3 llm-wiki/scripts/install_skill.py --dry-run --platform codex`
- Real local install requires an explicit confirmation flag: `python3 llm-wiki/scripts/install_skill.py --platform claude-code --confirm`
- `generic-agent` installs need `--target` or `LLM_WIKI_SKILL_TARGET` / `AI_AGENT_SKILL_TARGET`; there is no default generic skill path.
- For `llm-wiki` changes, run the focused validator: `python3 llm-wiki/scripts/validate_skill.py --repo-root /home/inkparker/workspace/skills`

## GitNexus usage in this repo

- If GitNexus reports a stale index, refresh it with `npx gitnexus analyze` before trusting graph results.
- Before editing a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and surface HIGH/CRITICAL risk before proceeding.
- Before committing, run `gitnexus_detect_changes()` to confirm the change scope matches expectations.
- Use `gitnexus_rename` for symbol renames; do not do graph-blind find/replace.
- For unfamiliar code, prefer `gitnexus_query` / `gitnexus_context` over blind grep when the index is fresh.

## Practical verification expectations

- There is no repo-wide build/test command to run after every change.
- Verify the smallest relevant surface instead: for `llm-wiki`, use `validate_skill.py`; for instruction-only edits, verify by rereading the touched files against the cited source files.
