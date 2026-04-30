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

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **skills** (204 symbols, 264 relationships, 5 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/skills/context` | Codebase overview, check index freshness |
| `gitnexus://repo/skills/clusters` | All functional areas |
| `gitnexus://repo/skills/processes` | All execution flows |
| `gitnexus://repo/skills/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
