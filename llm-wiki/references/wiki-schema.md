# LLM Wiki schema

This schema defines the reviewable Markdown layer for the LLM Wiki. It is assistant-portable and applies before any Graphify-generated layer exists.

## Layering

```text
raw/            immutable source evidence; read-only for this skill
wiki/           maintained Markdown wiki; human-reviewable source of compiled knowledge
graphify-out/   generated graph artifacts; reproducible and non-canonical
skills/llm-wiki canonical skill package and workflow documentation
```

Never write into `raw/`. Do not treat `graphify-out/` as authoritative content.

## Directory plan

```text
wiki/
  index.md                  # catalog of maintained wiki pages
  log.md                    # append-only maintenance log
  sources/                  # one page per raw source or tightly related source cluster
  concepts/                 # small synthesis pages across sources
  workflows/                # reusable procedures for ingest/query/lint/graph refresh
```

The first pass for the knowledge repository should remain small: source pages for every current `raw/*.md`, workflow pages for the repeated procedures, and only a few concept pages that synthesize multiple sources.

## Frontmatter

All maintained wiki pages should start with YAML frontmatter:

```yaml
---
title: "Readable page title"
type: source | concept | workflow | index | log
status: draft | review | stable
sources:
  - "raw/example.md"
tags: [llm-wiki]
updated: YYYY-MM-DD
---
```

Rules:

- `title`, `type`, `status`, and `updated` are required except for legacy pages being linted.
- `sources` is required for `source` and `concept` pages; it may be empty or omitted for generic workflow pages.
- Use paths relative to the knowledge repository root for raw provenance.
- Keep tags sparse and reusable.

## Page types

### `source`

Purpose: summarize one raw source without replacing it.

Required sections:

1. `# <title>`
2. `## Summary`
3. `## Key claims`
4. `## Useful details`
5. `## Links`

Guidelines:

- Keep summaries concise and evidence-bound.
- Preserve uncertainty or context when the raw source is fragmentary.
- Link to concept/workflow pages with relative or Obsidian-style links that remain readable in Markdown.

### `concept`

Purpose: synthesize reusable ideas across source pages.

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
- a note that `raw/` is immutable provenance and `graphify-out/` is generated.

### `log`

`wiki/log.md` is append-only. Each entry should include:

```markdown
## YYYY-MM-DD — <action>

- Scope: <files or source set>
- Change: <what changed>
- Verification: <checks performed>
```

Do not rewrite old entries except to correct formatting mistakes.

## Link conventions

- Prefer relative Markdown links such as `../concepts/agent-context-memory.md` when writing standard Markdown.
- Obsidian-style links are acceptable in human-facing notes when they stay understandable, for example `[[../concepts/agent-context-memory]]`.
- Keep links within `wiki/` for maintained wiki navigation.
- Refer to raw files in provenance lists and evidence sections, not as generated copies.

## Ingest guardrails

Before writing wiki pages, prepare a page plan containing:

- selected raw sources;
- proposed source pages;
- proposed concept/workflow pages;
- expected index/log updates;
- whether the change is a small update or full generation.

Ask for or rely on explicit execution authorization before full wiki generation. In autonomous execution modes, keep the first pass to the approved scope and avoid broad rewrites.

## Lint checklist

A wiki lint should check:

- every `raw/*.md` source is represented by at least one planned or existing source page;
- no maintained page has missing required frontmatter;
- source/concept pages have raw provenance;
- no page is orphaned from `wiki/index.md` unless intentionally draft-only;
- concept pages are not duplicative or over-fragmented;
- `wiki/log.md` records significant maintenance actions;
- Graphify reports, if present, are used only for navigation.
