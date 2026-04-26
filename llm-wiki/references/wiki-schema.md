# LLM Wiki schema

This schema defines the reviewable Markdown layer for the LLM Wiki. It is assistant-portable and does not require generated graph tooling.

## Layering

```text
raw/            immutable source evidence; read-only for this skill
wiki/           maintained Markdown wiki; human-reviewable source of compiled knowledge
skills/llm-wiki canonical skill package and workflow documentation
```

Never write into `raw/`.

## Repository root resolution

When the user does not explicitly provide a working directory or knowledge repository path, the current session working directory is the knowledge repository root.

Rules:

- Resolve `raw/`, `wiki/`, `wiki/config.md`, `wiki/index.md`, and `wiki/log.md` relative to the session working directory by default.
- If the user explicitly supplies another directory, use that directory as the knowledge repository root for the current task.
- Do not infer a different root from the installed skill location, user home directory, or parent folders unless the user asks for that.
- Raw provenance paths in frontmatter should remain relative to the selected knowledge repository root.

## Directory plan

```text
wiki/
  config.md                 # remembered wiki settings such as target language
  manifest.json             # raw file hashes, source-page mapping, and ingest status
  index.md                  # catalog of maintained wiki pages
  log.md                    # append-only maintenance log
  sources/                  # one page per raw source or tightly related source cluster
  concepts/                 # small synthesis pages across sources
  workflows/                # reusable procedures for ingest/query/lint/graph refresh
```

The first pass for the knowledge repository should remain small: source pages for every current `raw/*.md`, workflow pages for the repeated procedures, and only a few concept pages that synthesize multiple sources.

Generate or refresh source pages as a separate Source generation stage. For non-trivial source sets, delegate source-page drafting to sub-agents or equivalent isolated context workers so each worker reads only a bounded raw-file slice and returns source-page drafts, short summaries, evidence links, and blockers. The main agent should coordinate, review, and integrate drafts; it should not keep the whole raw corpus in context.

After source pages are generated or refreshed, run Concept synthesis as its own stage. For non-trivial source sets, delegate concept discovery to sub-agents or equivalent isolated context workers so each worker reads only a bounded set of source pages and returns compact candidate concepts with evidence links. The main agent should integrate and deduplicate candidates; it should not keep the whole source-page corpus in context.

## Frontmatter

All maintained wiki pages should start with YAML frontmatter:

```yaml
---
title: "Readable page title"
type: source | concept | workflow | index | log | config
status: draft | review | stable
language: zh-CN
sources:
  - "raw/example.md"
tags: [llm-wiki]
updated: YYYY-MM-DD
---
```

Rules:

- `title`, `type`, `status`, and `updated` are required except for legacy pages being linted.
- `language` is required for new maintained pages and records the user-selected wiki language, for example `zh-CN`, `en`, `ja`, or `bilingual`.
- `sources` is required for `source` and `concept` pages; it may be empty or omitted for generic workflow pages.
- Use paths relative to the knowledge repository root for raw provenance.
- Frontmatter provenance is not enough: the page body must include clickable Markdown links to each relevant raw file.
- Keep tags sparse and reusable.

## Language policy

The target wiki language is a user-facing content decision. Before creating or updating `wiki/` pages, the agent must confirm the language when it is not explicit in the user's request or an accepted page plan.

Suggested prompt:

```text
请选择或指定本次 wiki 使用的语种（例如 zh-CN、en、bilingual 或其他）。
```

Rules:

- Do not infer the wiki language solely from the raw source language, repository locale, or current chat language.
- Remember the selected language in `wiki/config.md` as `language: <value>` so later bare invocations can reuse it without asking again.
- If `wiki/config.md` is absent, an agent may reuse a consistent `language` value found in `wiki/index.md` or maintained wiki pages, then write that value back to `wiki/config.md`.
- If the agent UI supports a modal or choice dialog, use it; otherwise ask in chat and wait for the user's answer.
- Write new page titles, headings, summaries, and index/log prose in the selected language unless the user explicitly asks for bilingual or mixed-language output.
- Preserve original terms, quotes, names, code, and identifiers in their source language when needed for accuracy.
- Record the selected language in frontmatter as `language: <value>`.

## Config page

`wiki/config.md` remembers wiki-level settings and should be small and reviewable:

```yaml
---
title: "LLM Wiki Config"
type: config
status: stable
language: zh-CN
sources: []
tags: [llm-wiki]
updated: YYYY-MM-DD
---
```

Body:

```markdown
# LLM Wiki Config

## Settings

- Language: zh-CN
```

Agents may create or update this page when the user selects a wiki language. Do not store secrets, tokens, or raw source content in this file.

## Manifest

`wiki/manifest.json` enables incremental generation for large raw sets. It should be updated before and after each ingest batch.

Recommended shape:

```json
{
  "schema_version": 1,
  "language": "zh-CN",
  "batch_size": 20,
  "updated": "YYYY-MM-DD",
  "raw": {
    "raw/example-source.md": {
      "sha256": "<hex>",
      "status": "done",
      "source_page": "wiki/sources/example-source.md",
      "last_ingested": "YYYY-MM-DD",
      "notes": ""
    }
  }
}
```

Status values:

- `new`: raw file is not represented yet.
- `changed`: raw hash differs from the last recorded hash.
- `unchanged`: raw hash matches and the source page exists.
- `missing-page`: manifest entry exists but the source page is missing.
- `done`: raw file was processed and verified for the selected language.
- `skipped`: raw file is intentionally not ingested; `notes` should explain why.

Rules:

- Use paths relative to the selected knowledge repository root.
- Prefer SHA-256 hashes when local tooling is available.
- Do not store raw source text in the manifest.
- Treat the manifest as an index, not as source evidence.
- For large raw sets, process pending entries in batches and update the manifest after every batch.

## Page types

### `source`

Purpose: summarize one raw source without replacing it.

Generation rule: create or update source pages through sub-agents/equivalent isolated workers for large or multi-source batches. Each worker should receive a bounded raw-file slice and produce source-page drafts plus compact summaries for the main agent to integrate.

Required sections:

1. `# <title>`
2. `## Raw source`
3. `## Summary`
4. `## Key claims`
5. `## Useful details`
6. `## Links`

Guidelines:

- Keep summaries concise and evidence-bound.
- Preserve uncertainty or context when the raw source is fragmentary.
- In `## Raw source`, include a direct Markdown link to the corresponding raw file, for example `[raw/example.md](../../raw/example.md)` from `wiki/sources/example.md`.
- Link to concept/workflow pages with relative or Obsidian-style links that remain readable in Markdown.

### `concept`

Purpose: synthesize reusable ideas across source pages.

Generation rule: create or update concept pages after the relevant source pages exist. Use sub-agents/equivalent isolated workers for concept discovery on large or multi-source batches, then integrate only durable, deduplicated concepts.

Required sections:

1. `# <title>`
2. `## Definition`
3. `## Why it matters`
4. `## Evidence`
5. `## Related`

Guidelines:

- Create concept pages only when they reduce duplication across multiple source pages.
- Avoid one-page-per-term fragmentation.
- Keep raw provenance in frontmatter and cite source pages in the body.
- In `## Evidence`, include links to relevant source pages and direct Markdown links to the raw files that support the concept.

### `workflow`

Purpose: encode repeatable wiki maintenance procedures.

Required sections:

1. `# <title>`
2. `## When to use`
3. `## Steps`
4. `## Safety checks`

Guidelines:

- Workflows should describe agent behavior, not one-time project status.
- Include stop conditions for raw immutability, cost/network risk, and large rewrites.

### `index`

`wiki/index.md` is the wiki catalog. It should include:

- a short description of the wiki purpose;
- links grouped by Sources, Concepts, and Workflows;
- one-line summaries for each maintained page;
- a note that `raw/` is immutable provenance.

Index size and provenance rules:

- Treat `wiki/index.md` as navigation, not complete provenance storage.
- For index frontmatter, use `sources: []` or omit `sources`; do not copy every raw path into the index frontmatter.
- In the body, list maintained `wiki/sources/*.md` pages rather than every raw file when the raw set is large.
- Rebuild source links from current wiki pages with stable sorting and deduplication; never append historical entries blindly.
- Store the complete raw-file inventory, hashes, and processing status in `wiki/manifest.json`.
- Keep per-page raw provenance on source/concept pages, including clickable raw links in their body.
- If the maintained source-page list itself becomes too large, group it by directory/topic/date or move the exhaustive catalog to `wiki/sources/README.md`, keeping `wiki/index.md` as a summary plus link.

### `log`

`wiki/log.md` is append-only. Each entry should include:

```markdown
## YYYY-MM-DD — <action>

- Scope: <files or source set>
- Change: <what changed>
- Verification: <checks performed>
```

Do not rewrite old entries except to correct formatting mistakes.

### `config`

`wiki/config.md` stores durable wiki preferences such as the selected language. It is not source evidence and should not replace per-page provenance.

## Link conventions

- Prefer relative Markdown links such as `../concepts/agent-context-memory.md` when writing standard Markdown.
- Obsidian-style links are acceptable in human-facing notes when they stay understandable, for example `[[../concepts/agent-context-memory]]`.
- Keep links within `wiki/` for maintained wiki navigation.
- Link to raw files in source pages and evidence sections; never copy raw content into generated files as a substitute for linking.

## Ingest guardrails

Before writing wiki pages, prepare a page plan containing:

- target wiki language and whether it was explicitly provided or user-selected after prompting;
- whether the language was read from or written to `wiki/config.md`;
- selected raw sources;
- manifest status for selected raw sources (`new`, `changed`, `missing-page`, etc.);
- batch size and whether more raw files remain after the current batch;
- proposed source pages;
- proposed concept/workflow pages;
- expected index/log updates;
- whether the change is a small update or full generation.

Ask for or rely on explicit execution authorization before full wiki generation. In autonomous execution modes, keep the first pass to the approved scope and avoid broad rewrites.

## Lint checklist

A wiki lint should check:

- every `raw/*.md` source is represented by at least one planned or existing source page;
- no maintained page has missing required frontmatter;
- source/concept pages have raw provenance and clickable raw file links in the body;
- no page is orphaned from `wiki/index.md` unless intentionally draft-only;
- concept pages are not duplicative or over-fragmented;
- `wiki/log.md` records significant maintenance actions;
- `wiki/manifest.json` exists for large raw sets and accurately records raw hashes, source-page targets, status, language, and batch size;
