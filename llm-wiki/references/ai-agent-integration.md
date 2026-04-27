# AI Agent Integration Reference for the LLM Wiki Skill

Use this reference when adapting the canonical `llm-wiki` workflow to an AI agent beyond the dedicated Claude Code notes.

## Portability contract

The skill is portable when the target agent can:

- read a local Markdown instruction file or skill folder;
- inspect and edit the knowledge repository filesystem within the requested scope;
- preserve the safety contract from `SKILL.md`, especially `raw/` immutability;
- avoid package installs and model/API calls unless explicitly requested.

If the user does not explicitly specify a knowledge repository path, the agent should use its current session working directory as the knowledge repository root. Do not derive the root from the installed skill location.

Do not fork the workflow for each agent. Keep `skills/llm-wiki/SKILL.md` as the canonical source and use agent-specific files only as short pointers.

## Integration patterns

Prefer the first supported pattern:

1. **Project instruction pointer**: add a short pointer in the agent's project instruction file that tells it to read `skills/llm-wiki/SKILL.md` for LLM Wiki tasks.
2. **Session prompt pointer**: when no persistent configuration is available, include the same short pointer in the task prompt.

Before writing an agent-specific config file, check that agent's current documentation or local help. Agent conventions change; do not assume a path is stable just because another agent uses a similar file name.

## Pointer fallback template

Use a short pointer rather than copying the full skill body:

```markdown
# LLM Wiki Skill

For tasks about ingesting, maintaining, querying, or linting the knowledge repository's LLM Wiki, read `skills/llm-wiki/SKILL.md` and follow it as the canonical workflow. Do not edit `raw/`. Do not install packages or call models/APIs unless explicitly requested.
```

## Agent adaptation checklist

- Keep `SKILL.md` and `references/` together when pointing an agent at the workflow.
- Add agent-specific details to a small new reference file only when the details are verified and materially useful.
- If the agent has memory, rules, or hooks, store only a pointer there; do not duplicate the full workflow.
