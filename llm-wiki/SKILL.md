---
name: llm-wiki
description: Maintain a reviewable LLM Wiki from immutable raw notes, including ingest planning, querying, linting, and guarded Graphify graph refreshes for AI coding agents and assistants such as Codex, Claude Code, or any agent that can read local Markdown instructions.
---

# LLM Wiki

Use this skill from any capable AI agent when the user asks to ingest notes into an LLM Wiki, maintain or query the wiki, lint wiki consistency, update wiki indexes/logs/cross-links, or refresh/consult a Graphify graph for the wiki.

## Safety contract

- Treat `raw/` as immutable source evidence: never edit, move, delete, normalize, or write generated files under it.
- Treat `wiki/` as the reviewable compiled Markdown layer.
- Treat `graphify-out/` as generated, reproducible graph output; never cite it as canonical source content.
- Do not install `graphifyy`, run `graphify`, call models/APIs, or generate a full wiki unless the user explicitly requests that execution step.
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
2. Read selected `raw/*.md` files as evidence only; do not alter them.
3. Map each raw source to at least one `wiki/sources/*.md` page and at most a small justified set of concept/workflow pages.
4. Draft source pages with provenance in frontmatter and concise claim summaries.
5. Draft concept/workflow pages only when they synthesize multiple sources or encode reusable procedure.
6. Update `wiki/index.md` and append an entry to `wiki/log.md` for accepted writes.
7. Stop before full wiki generation unless execution scope explicitly allows it.

## Workflow: query

1. Prefer `wiki/index.md`, relevant `wiki/**/*.md` pages, and `graphify-out/wiki/GRAPH_REPORT.md` when present.
2. Cite wiki pages and their raw provenance; do not cite Graphify output as source of truth.
3. After answering, decide whether the result contains durable knowledge: a reusable synthesis, comparison, decision, source map, or workflow clarification that future queries should find.
4. If durable knowledge was produced, do not leave it only in chat history:
   - for ordinary query prompts, offer a scoped wiki update with a proposed page title/path and the provenance that would be filed;
   - when the user requested wiki maintenance, compounding, or autonomous execution, perform the scoped update instead of merely offering it.
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
3. Default mode is wiki-only: read `wiki/`, write `graphify-out/wiki/`.
4. Raw-audit mode is explicit and isolated: read `raw/`, write `graphify-out/raw-audit/`.
5. Never use a mixed/root graph by default. It requires a validated ignore policy and explicit confirmation.
6. After an approved refresh, summarize `GRAPH_REPORT.md` for navigation and append the refresh to `wiki/log.md`.

## Optional helpers

- `scripts/install_skill.py --help` and `--dry-run` show Codex, Claude Code, or generic agent install targets without writing.
- `scripts/install_skill.py --dry-run --platform generic-agent --target <agent-skill-dir>` previews a copy/symlink install for other agents.
- `scripts/run_graphify.py --help` and `--dry-run --mode wiki-only` validate intended paths without running Graphify; run it from the knowledge repository root or pass `--repo-root <knowledge-repo>` when the skill is installed elsewhere.
