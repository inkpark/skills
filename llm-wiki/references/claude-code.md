# Claude Code Reference for the LLM Wiki Skill

Use this reference when invoking the canonical `llm-wiki` workflow from Claude Code.
For agents that are not Claude Code, prefer `references/ai-agent-integration.md` unless a dedicated verified reference exists.

## Canonical source of truth

The canonical skill lives in the knowledge repository:

```text
<knowledge-repo>/skills/llm-wiki/
```

Claude-specific files are configuration pointers only. Do not fork the workflow into a separate Claude-only source package.

## Claude Code environment notes

Claude Code is a terminal-based coding assistant. Official Claude Code docs describe project/user configuration through `CLAUDE.md` and `.claude/settings.json`; settings can be user-level or project-level. When integrating a skill, keep the LLM Wiki rules in the canonical `SKILL.md` and use Claude files only to point Claude Code at that canonical source.

Reference links for re-checking:

- Claude Code overview: <https://docs.anthropic.com/en/docs/claude-code/overview>
- Claude Code setup: <https://docs.anthropic.com/en/docs/claude-code/getting-started>
- Claude Code settings: <https://docs.anthropic.com/en/docs/claude-code/settings>

## Configuration pointer

Preferred configuration:

1. Keep `skills/llm-wiki/` under the knowledge repository as the audited source.
2. Add a short `CLAUDE.md` pointer instructing Claude to read `skills/llm-wiki/SKILL.md` for wiki-maintenance tasks. Do not paste the full workflow body into `CLAUDE.md` because that creates drift.

## Invocation behavior

Claude Code should apply `llm-wiki` when the user asks to maintain or query the knowledge repository's LLM Wiki:

- ingest selected raw notes into reviewable wiki pages;
- update indexes, logs, source summaries, concept pages, or workflow pages;
- lint for stale summaries, missing provenance, duplicate concepts, contradictions, or over-fragmentation;
- update cross-links, source summaries, concept pages, or workflow pages.

For page shape, read `references/wiki-schema.md` first.

## Claude-specific guardrails

- Claude Code may have broad local file access depending on settings. Still treat `raw/` as immutable by policy.
- If using `.claude/settings.json`, prefer deny rules for secrets and generated/cache folders. Do not hide `skills/llm-wiki/` or `wiki/` from normal workflow operation.
- Keep `CLAUDE.md` content short and pointer-based to avoid a second copy of the skill.

Example pointer fallback:

```markdown
# LLM Wiki Skill

For tasks about ingesting, maintaining, querying, or linting the knowledge repository's LLM Wiki, read `skills/llm-wiki/SKILL.md` and follow it as the canonical workflow. Do not edit `raw/`. Do not install packages unless explicitly requested.
```

## Pointer sanity check

Verify the pointer still references the canonical package:

```bash
grep -q 'skills/llm-wiki/SKILL.md' CLAUDE.md
```
