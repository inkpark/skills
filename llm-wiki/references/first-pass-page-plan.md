# First-pass page plan template

Use this as a generic planning and style calibration reference before creating or substantially expanding an LLM Wiki. Replace placeholder paths and titles with the user's actual repository/source set.

## Source selection

Start from the requested immutable source set, usually a small group of Markdown files under `raw/`:

- `raw/example-source-a.md`
- `raw/example-source-b.md`

For large repositories, sample first and propose a staged plan instead of generating the full wiki at once.

## Wiki language

Target wiki language: `<ask the user if not explicit; examples: zh-CN, en, bilingual, or another user-specified language>`.

Do not begin writing `wiki/` pages until the user has explicitly specified or selected this value. Record the selected value in each new maintained page's frontmatter as `language: <value>`.

When the language is selected for the first time, add or update `wiki/config.md` so later bare `llm-wiki` invocations can reuse it without prompting again.

## Proposed wiki pages

| Page | Type | Sources | Purpose |
|---|---|---|---|
| `wiki/config.md` | config | none | Remember wiki-level settings such as selected language. |
| `wiki/index.md` | index | selected source set | Catalog maintained wiki pages and summaries. |
| `wiki/log.md` | log | selected source set | Append-only record of ingests, queries, lints, and graph refreshes. |
| `wiki/workflows/ingest.md` | workflow | skill | Define how agents transform raw notes into wiki pages. |
| `wiki/workflows/query.md` | workflow | skill | Define query-first behavior against wiki pages and graph reports. |
| `wiki/workflows/lint.md` | workflow | skill | Define consistency and health checks. |
| `wiki/sources/example-source-a.md` | source | `raw/example-source-a.md` | Summarize one source without replacing it. |
| `wiki/sources/example-source-b.md` | source | `raw/example-source-b.md` | Summarize one source without replacing it. |
| `wiki/concepts/example-shared-concept.md` | concept | multiple source pages | Synthesize only when a reusable idea appears across sources. |

## Sample source page excerpt

```markdown
---
title: "Example Source Summary"
type: source
status: draft
language: en
sources:
  - "raw/example-source-a.md"
tags: [llm-wiki]
updated: YYYY-MM-DD
---

# Example Source Summary

## Summary

Summarize the source concisely and keep claims tied to the raw provenance.

## Key claims

- State the important claims or observations.
- Preserve uncertainty when the raw source is fragmentary.

## Useful details

Record reusable terms, examples, caveats, or implementation details that help future queries.

## Links

- [Example Shared Concept](../concepts/example-shared-concept.md)
- [Ingest Workflow](../workflows/ingest.md)
```

## Sample concept page excerpt

```markdown
---
title: "Example Shared Concept"
type: concept
status: draft
language: en
sources:
  - "raw/example-source-a.md"
  - "raw/example-source-b.md"
tags: [llm-wiki]
updated: YYYY-MM-DD
---

# Example Shared Concept

## Definition

Define the reusable idea in terms that future agents can apply across tasks.

## Why it matters

Explain why the concept helps the knowledge repository answer future questions or guide future maintenance.

## Evidence

- Cite source pages and their raw provenance rather than generated graph output.

## Related

- [Query Workflow](../workflows/query.md)
```
