---
name: llm-wiki
description: Maintain a reviewable LLM Wiki from immutable raw notes, including language-aware ingest planning, querying, linting, and durable wiki updates.
---

# LLM Wiki

Use this skill from any capable AI agent when the user asks to ingest notes into an LLM Wiki, maintain or query the wiki, lint wiki consistency, or update wiki indexes/logs/cross-links.

When the user invokes only `llm-wiki` or otherwise provides no additional task details, do not show a workflow menu. Treat the bare invocation as the default bootstrap/refresh pipeline: resolve the wiki language, then generate or update the wiki directly from `raw/`.

If the user does not explicitly specify a working directory or knowledge repository path, operate on the current session working directory. Resolve `raw/`, `wiki/`, and all relative links from that directory.

## Safety contract

- Treat `raw/` as immutable source evidence: never edit, move, delete, normalize, or write generated files under it.
- Treat `wiki/` as the reviewable compiled Markdown layer.
- Treat the session working directory as the knowledge repository root unless the user explicitly provides another directory.
- Every generated or updated wiki page that is derived from raw material must link to its corresponding `raw/` file(s), not only list them in frontmatter.
- Do not install packages, call models/APIs, or generate a full wiki unless the user explicitly requests that execution step.
- Before creating or updating `wiki/` pages, determine the target wiki language. If the user did not explicitly specify it in the current request or accepted page plan, open a short choice/input dialog when the agent UI supports it, or ask in chat, and wait for the user to choose or specify the language.
- Remember the selected wiki language in `wiki/config.md` using `language: <value>`, and reuse it on later invocations unless the user overrides it.
- Prefer small, reviewable wiki updates and record meaningful changes in `wiki/log.md`.

## Reference map

Read only the references needed for the current request:

- `references/wiki-schema.md` — directory layout, frontmatter, page types, index/log/config rules, page-plan guardrails.
- `references/ai-agent-integration.md` — portable setup patterns for agents beyond the named Codex/Claude Code references.
- `references/codex.md` — Codex installation and usage notes.
- `references/claude-code.md` — Claude Code installation and usage notes.
- `references/first-pass-page-plan.md` — initial page plan and sample style for the current `<knowledge-repo>` raw sources.

## Workflow: bare invocation

Use this workflow when the user invokes the skill without any other instruction, for example just `llm-wiki`.

1. Resolve the target wiki language:
   - if the user specified a language in the current request, use it;
   - otherwise read the remembered language from `wiki/config.md` when present;
   - otherwise, if `wiki/index.md` or existing maintained pages have a consistent `language` value, reuse it and write it to `wiki/config.md`;
   - otherwise ask: "请选择或指定本次 wiki 使用的语种（例如 zh-CN、en、bilingual 或其他）" and wait for the answer.
2. If the user selected a language and `wiki/config.md` is absent or stale, create/update it before other wiki writes.
3. Use the user-specified working directory when provided; otherwise use the current session working directory as the knowledge repository root.
4. Inventory `raw/*.md` and existing `wiki/**/*.md` coverage without altering `raw/`.
5. Generate or update the wiki directly from `raw/`, keeping the first pass small and reviewable unless the user explicitly requested full generation.
6. Update `wiki/index.md` and append `wiki/log.md` with the language, changed pages, raw coverage, and verification.

## Workflow: ingest plan

1. Identify the requested source set. For new or large sets, list proposed wiki pages before writing.
2. Determine the target wiki language before any wiki write. If it is not explicit, first reuse `wiki/config.md`; if no remembered language exists, ask: "请选择或指定本次 wiki 使用的语种（例如 zh-CN、en、bilingual 或其他）" and do not proceed with wiki writes until the user answers.
3. Read selected `raw/*.md` files as evidence only; do not alter them.
4. Map each raw source to at least one `wiki/sources/*.md` page and at most a small justified set of concept/workflow pages.
5. Draft source pages in the chosen wiki language, with provenance and `language` in frontmatter, concise claim summaries, and explicit Markdown links to the corresponding raw file(s).
6. Draft concept/workflow pages in the chosen wiki language only when they synthesize multiple sources or encode reusable procedure; concept pages must link to the relevant source pages and raw file(s).
7. Update `wiki/index.md` and append an entry to `wiki/log.md` for accepted writes.
8. Stop before full wiki generation unless execution scope explicitly allows it.

## Workflow: query

1. Prefer `wiki/index.md` and relevant `wiki/**/*.md` pages for answered/cited knowledge.
2. Cite wiki pages and their raw provenance.
3. After answering, decide whether the result contains durable knowledge: a reusable synthesis, comparison, decision, source map, or workflow clarification that future queries should find.
4. If durable knowledge was produced, do not leave it only in chat history:
   - for ordinary query prompts, offer a scoped wiki update with a proposed page title/path and the provenance that would be filed;
   - when the user requested wiki maintenance, compounding, or autonomous execution, perform the scoped update instead of merely offering it, but first apply the wiki-language gate if the target language was not explicit.
5. For accepted or performed durable updates, write the synthesis into the smallest suitable `wiki/` page, update `wiki/index.md` when navigation changes, and append a `wiki/log.md` entry.

## Workflow: lint

Check for:

- source pages missing raw provenance;
- raw sources not represented in `wiki/sources/`;
- orphan or duplicate concept pages;
- over-fragmented pages that should be merged;
- stale `wiki/index.md` entries;
- missing `wiki/log.md` entries for wiki maintenance;
- contradictions between summaries and raw provenance;
- missing or inconsistent `language` values across maintained pages.

Report proposed fixes before large rewrites.

## Optional helpers

- `scripts/install_skill.py --help` and `--dry-run` show Codex, Claude Code, or generic agent install targets without writing.
- `scripts/install_skill.py --dry-run --platform generic-agent --target <agent-skill-dir>` previews a copy/symlink install for other agents.
