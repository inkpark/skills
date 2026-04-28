# First-pass page plan template

Use this as a generic planning and style calibration reference before creating or substantially expanding an LLM Wiki. Replace placeholder paths and titles with the user's actual repository/source set.

## Source selection

Start from the requested immutable source set, usually a small group of Markdown files under `raw/`:

- `raw/example-source-a.md`
- `raw/example-source-b.md`

For large repositories, sample first and propose a staged plan instead of generating the full wiki at once.

## Wiki language

`SKILL.md` is the canonical workflow source for the language gate and reuse of `wiki/config.md`. This template keeps only the page-plan fields you must fill in.

Target wiki language: `<ask the user if not explicit; examples: zh-CN, en, bilingual, or another user-specified language>`.

Do not begin writing `wiki/` pages until the user has explicitly specified or selected this value. Record the selected value in each new maintained page's frontmatter as `language: <value>`.

When the language is selected for the first time, add or update `wiki/config.md` so later bare `llm-wiki` invocations can reuse it without prompting again.

## Batch and manifest plan

Use `SKILL.md` as the canonical workflow source for batching, manifest lifecycle, Source generation, and Concept synthesis. This template records the decisions and outputs for the current first pass.

Default large-source threshold: more than 30 raw Markdown files.

Default batch size: 20 raw files, unless the user explicitly specifies another value.

Before generating source pages, create or refresh `wiki/manifest.json` with raw paths, hashes, target source pages, language, status, and batch metadata. For large raw sets, record which pending batch is being processed and whether Source generation / Concept synthesis will use sub-agents or equivalent isolated context workers.

## Proposed wiki pages

| Page | Type | Sources | Purpose |
|---|---|---|---|
| `wiki/config.md` | config | none | Remember wiki-level settings such as selected language. |
| `wiki/manifest.json` | manifest | raw source set | Track raw hashes, target pages, statuses, and batch progress. |
| `wiki/index.md` | index | maintained wiki pages | Compact navigation catalog with summaries, raw coverage counts, and links to manifest/source catalogs; not an exhaustive raw-source dump. |
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

## Raw source

- [raw/example-source-a.md](../../raw/example-source-a.md)

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

- Cite source pages and their raw provenance, including direct raw links such as [raw/example-source-a.md](../../raw/example-source-a.md).

## Related

- [Query Workflow](../workflows/query.md)
```
