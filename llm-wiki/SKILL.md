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
- For many raw sources, use `wiki/manifest.json` for incremental batching instead of trying to generate the whole wiki in one pass. Default large-source threshold: more than 30 raw files. Default batch size: 20 raw files unless the user specifies another batch size.
- Prefer small, reviewable wiki updates and record meaningful changes in `wiki/log.md`.
- Keep `wiki/index.md` as a compact navigation catalog, not an ever-growing provenance dump. Do not append every raw file into an index `Sources` field/list. Store complete raw coverage in `wiki/manifest.json`, keep raw provenance on the relevant source/concept pages, and rebuild index source links from current `wiki/sources/*.md` pages with deduplication.
- Source generation: generate or refresh source pages with sub-agents or equivalent isolated context workers whenever the agent environment supports them. Each worker should receive only a bounded raw-file slice plus the page schema and return source-page drafts/summaries; the main context should coordinate, review, and integrate rather than ingesting the entire raw corpus.
- After generating or refreshing source pages, always run a bounded Concept synthesis pass. Use sub-agents or equivalent isolated context workers for this pass whenever the agent environment supports them, so the main context handles only plans, source-page summaries, proposed concepts, and final integration rather than every raw/source detail.

## Reference map

Read only the references needed for the current request:

- `references/wiki-schema.md` — directory layout, frontmatter, page types, index/log/config rules, page-plan guardrails.
- `references/ai-agent-integration.md` — portable setup patterns for agents beyond the named Claude Code reference.
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
5. Create or update `wiki/manifest.json` with raw file paths, content hashes, target source pages, language, and status.
6. If the selected raw set is larger than 30 files, or the pending changed/new set is larger than the batch size, enter batch mode and process only the next batch of pending raw files.
7. Generate or update source pages with sub-agents/equivalent isolated workers, keeping the first pass small and reviewable unless the user explicitly requested full generation:
   - give each worker a bounded raw-file slice, target source-page paths, language, and source-page schema;
   - require clickable raw provenance links and concise evidence-bound summaries;
   - have workers return changed page paths, short page summaries, and any uncertainty/blockers for main-agent integration.
8. After the source-page pass, run a Concept synthesis pass using sub-agents/equivalent isolated workers:
   - give each worker a bounded set of source pages or source-page summaries, not the whole raw corpus;
   - ask for reusable cross-source concepts, merge candidates, and evidence links;
   - integrate only accepted concepts into `wiki/concepts/*.md`, avoiding duplicate or over-fragmented pages.
9. Update `wiki/index.md`, `wiki/manifest.json`, and append `wiki/log.md` with the language, changed pages, raw coverage, concept synthesis status, batch status, and verification.
   - Keep the index compact: summarize raw coverage counts and link to `wiki/manifest.json` or a dedicated source catalog when needed instead of expanding an unbounded raw-source list.

## Workflow: ingest plan

1. Identify the requested source set. For new or large sets, list proposed wiki pages before writing.
2. Determine the target wiki language before any wiki write. If it is not explicit, first reuse `wiki/config.md`; if no remembered language exists, ask: "请选择或指定本次 wiki 使用的语种（例如 zh-CN、en、bilingual 或其他）" and do not proceed with wiki writes until the user answers.
3. Read selected `raw/*.md` files as evidence only; do not alter them.
4. Update `wiki/manifest.json` before writing pages. Mark raw files as `new`, `changed`, `unchanged`, `missing-page`, `done`, or `skipped`.
5. If there are more than 30 raw files or more pending files than the batch size, process only one batch at a time. Default batch size is 20; respect explicit user input such as "batch size 50".
6. Map each raw source in the current batch to at least one `wiki/sources/*.md` page and at most a small justified set of concept/workflow pages.
7. Draft source pages in the chosen wiki language through sub-agents/equivalent isolated workers, with provenance and `language` in frontmatter, concise claim summaries, and explicit Markdown links to the corresponding raw file(s). The main agent should pass bounded raw slices to workers and integrate their drafts, not read every raw source into one context.
8. After source pages are drafted, run Concept synthesis with sub-agents/equivalent isolated context workers before the final index/log update. Each worker should inspect only a bounded slice of source pages plus existing concept titles/summaries, then return candidate concepts with evidence links.
9. Draft concept/workflow pages in the chosen wiki language when they synthesize multiple sources, merge repeated ideas, or encode reusable procedure; concept pages must link to the relevant source pages and raw file(s). If no new concept qualifies, record that the Concept pass found no durable synthesis.
10. Update `wiki/index.md`, `wiki/manifest.json`, and append an entry to `wiki/log.md` for accepted writes.
   - Rebuild the index deterministically from maintained pages; do not append duplicate or historical `Sources` entries.
11. Stop before full wiki generation unless execution scope explicitly allows it.

## Workflow: large raw sets

Use this workflow whenever `raw/` contains more than 30 Markdown files, or when the changed/new pending set is larger than the configured batch size.

1. Build or refresh `wiki/manifest.json` by hashing every `raw/**/*.md` file. Prefer SHA-256 when local tooling is available.
2. Compare each raw file with the manifest:
   - `new`: raw file not in manifest;
   - `changed`: hash differs from manifest;
   - `unchanged`: hash matches and target source page exists;
   - `missing-page`: hash matches but target source page is missing;
   - `done`: processed and verified in the current language;
   - `skipped`: intentionally not ingested, with a reason.
3. Select the next batch in this priority order: `changed`, `missing-page`, `new`.
4. Process at most the batch size. Default: 20 raw files. User override examples: `batch size 50`, `每批 10 个`.
5. Generate source pages first with sub-agents/equivalent isolated workers over bounded raw-file slices. Do not load all raw files into the main context for source-page drafting.
6. After each source batch, run a bounded Concept synthesis pass with sub-agents/equivalent isolated workers over the completed source pages for that batch plus concise summaries of existing concepts. Do not load all raw files into the main context for concept discovery.
7. After every batch, update `wiki/manifest.json`, `wiki/index.md`, and `wiki/log.md` before continuing.
   - For large sets, `wiki/index.md` should show counts, batch status, and links to source pages or grouped source catalogs; the exhaustive raw-file inventory belongs in `wiki/manifest.json`.
8. If work remains after a batch, report the remaining counts and next batch recommendation instead of silently attempting an unbounded full generation.

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
- stale or missing `wiki/manifest.json` entries, including raw hashes that no longer match source pages.

Report proposed fixes before large rewrites.
