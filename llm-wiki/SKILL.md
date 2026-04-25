---
name: llm-wiki
description: Maintain a reviewable LLM Wiki from immutable raw notes, including ingest planning, querying, linting, and guarded raw Graphify maps that help agents generate better wiki pages.
---

# LLM Wiki

Use this skill from any capable AI agent when the user asks to ingest notes into an LLM Wiki, maintain or query the wiki, lint wiki consistency, update wiki indexes/logs/cross-links, or refresh/consult a Graphify graph for the wiki.

## Safety contract

- Treat `raw/` as immutable source evidence: never edit, move, delete, normalize, or write generated files under it.
- Treat `wiki/` as the reviewable compiled Markdown layer.
- Treat `graphify-out/` as generated, reproducible graph output; use it to navigate and synthesize raw notes, but never cite it as canonical source content.
- Do not install `graphifyy`, run `graphify`, call models/APIs, or generate a full wiki unless the user explicitly requests that execution step.
- Before creating or updating `wiki/` pages, determine the target wiki language. If the user did not explicitly specify it in the current request or accepted page plan, open a short choice/input dialog when the agent UI supports it, or ask in chat, and wait for the user to choose or specify the language.
- Prefer small, reviewable wiki updates and record meaningful changes in `wiki/log.md`.

## Reference map

Read only the references needed for the current request:

- `references/wiki-schema.md` — directory layout, frontmatter, page types, index/log rules, page-plan guardrails.
- `references/graphify.md` — Graphify package/CLI names, safe run modes, output lifecycle, cost/network warnings.
- `references/ai-agent-integration.md` — portable setup patterns for agents beyond the named Codex/Claude Code references.
- `references/codex.md` — Codex installation and usage notes.
- `references/claude-code.md` — Claude Code installation and usage notes.
- `references/first-pass-page-plan.md` — initial page plan and sample style for the current `<knowledge-repo>` raw sources.
- `references/graphifyignore-proposal.md` — documented ignore policy for any future root graph or audit mode.

## Workflow: ingest plan

1. Identify the requested source set. For new or large sets, list proposed wiki pages before writing.
2. Determine the target wiki language before any wiki write. If it is not explicit, ask: "请选择或指定本次 wiki 使用的语种（例如 zh-CN、en、bilingual 或其他）" and do not proceed with wiki writes until the user answers.
3. Read selected `raw/*.md` files as evidence only; do not alter them.
4. If an approved raw Graphify map exists under `graphify-out/raw-map/`, use it as a navigation and clustering aid before mapping raw sources; otherwise map directly from selected raw files.
5. Map each raw source to at least one `wiki/sources/*.md` page and at most a small justified set of concept/workflow pages.
6. Draft source pages in the chosen wiki language, with provenance and `language` in frontmatter plus concise claim summaries.
7. Draft concept/workflow pages in the chosen wiki language only when they synthesize multiple sources or encode reusable procedure.
8. Update `wiki/index.md` and append an entry to `wiki/log.md` for accepted writes.
9. Stop before full wiki generation unless execution scope explicitly allows it.

## Workflow: query

1. Prefer `wiki/index.md` and relevant `wiki/**/*.md` pages for answered/cited knowledge. Use `graphify-out/raw-map/GRAPH_REPORT.md` when present as a navigation and synthesis aid for raw-backed gaps; use `graphify-out/wiki/GRAPH_REPORT.md` only to navigate an existing wiki.
2. Cite wiki pages and their raw provenance; do not cite Graphify output as source of truth.
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
- contradictions between summaries and raw provenance.

Report proposed fixes before large rewrites.

## Workflow: Graphify refresh

1. Load `references/graphify.md` before any graph action.
2. Confirm Graphify availability with `graphify --help` only; do not install or run graph builds without explicit approval.
3. Default planning mode is raw-map: read `raw/`, write `graphify-out/raw-map/`, then use that generated graph to cluster sources and draft better `wiki/` pages.
4. Wiki-refresh mode is secondary: read `wiki/`, write `graphify-out/wiki/` when the maintained wiki already exists and needs navigation review.
5. Raw-audit mode is explicit and isolated: read `raw/`, write `graphify-out/raw-audit/` for source coverage or audit tasks beyond normal wiki generation.
6. Never use a mixed/root graph by default. It requires a validated ignore policy and explicit confirmation.
7. After an approved refresh, summarize `GRAPH_REPORT.md` as a non-canonical navigation aid and append the refresh to `wiki/log.md` when wiki logging is in scope.

## Optional helpers

- `scripts/install_skill.py --help` and `--dry-run` show Codex, Claude Code, or generic agent install targets without writing.
- `scripts/install_skill.py --dry-run --platform generic-agent --target <agent-skill-dir>` previews a copy/symlink install for other agents.
- `scripts/run_graphify.py --help` and `--dry-run --mode raw-map` validate intended raw-to-graph paths without running Graphify; run it from the knowledge repository root or pass `--repo-root <knowledge-repo>` when the skill is installed elsewhere.
