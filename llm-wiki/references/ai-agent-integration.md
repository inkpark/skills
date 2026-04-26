# AI Agent Integration Reference for the LLM Wiki Skill

Use this reference when adapting the canonical `llm-wiki` skill to an AI agent beyond the dedicated Codex and Claude Code notes.

## Portability contract

The skill is portable when the target agent can:

- read a local Markdown instruction file or skill folder;
- inspect and edit the knowledge repository filesystem within the requested scope;
- preserve the safety contract from `SKILL.md`, especially `raw/` immutability;
- avoid package installs and model/API calls unless explicitly requested.

Do not fork the workflow for each agent. Keep `skills/llm-wiki/SKILL.md` as the canonical source and use agent-specific files only as short pointers or install targets.

## Integration patterns

Prefer the first supported pattern:

1. **Native skill directory**: copy or symlink the whole `llm-wiki/` folder into the agent's documented skill/tool directory.
2. **Project instruction pointer**: add a short pointer in the agent's project instruction file that tells it to read `skills/llm-wiki/SKILL.md` for LLM Wiki tasks.
3. **Session prompt pointer**: when no persistent configuration is available, include the same short pointer in the task prompt.

Before writing an agent-specific config file, check that agent's current documentation or local help. Agent conventions change; do not assume a path is stable just because another agent uses a similar file name.

## Generic install helper

For native skill-directory agents with a known destination:

```bash
python3 skills/llm-wiki/scripts/install_skill.py --dry-run \
  --platform generic-agent \
  --target /path/to/agent/skills/llm-wiki
```

After reviewing the dry-run, a real install requires `--confirm`. Use `--method symlink` only when the target agent can safely follow symlinks and should track the canonical source directly.

If the destination should come from environment instead of the command line, set one of:

```bash
LLM_WIKI_SKILL_TARGET=/path/to/agent/skills/llm-wiki
AI_AGENT_SKILL_TARGET=/path/to/agent/skills/llm-wiki
```

## Pointer fallback template

Use a short pointer rather than copying the full skill body:

```markdown
# LLM Wiki Skill

For tasks about ingesting, maintaining, querying, or linting the knowledge repository's LLM Wiki, read `skills/llm-wiki/SKILL.md` and follow it as the canonical workflow. Do not edit `raw/`. Do not install packages or call models/APIs unless explicitly requested.
```

## Agent adaptation checklist

- Keep `SKILL.md` and `references/` together; do not install only the frontmatter.
- Keep `scripts/` executable when the target agent is expected to run dry-run helpers.
- Prefer a symlink for personal/local agent setups where drift is worse than coupling.
- Prefer a copy for shared/project setups where the agent must not depend on the original checkout path.
- Add agent-specific details to a small new reference file only when the details are verified and materially useful.
- If the agent has memory, rules, or hooks, store only a pointer there; do not duplicate the full workflow.
