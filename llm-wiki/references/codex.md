# Codex Reference for the LLM Wiki Skill

Use this reference when installing, syncing, or invoking the canonical `llm-wiki` skill from OpenAI Codex.
For agents that are not Codex, prefer `references/ai-agent-integration.md` unless a dedicated verified reference exists.

## Canonical source of truth

The project-local canonical skill source is:

```text
<knowledge-repo>/skills/llm-wiki/
  SKILL.md
  references/
  scripts/        optional safe helpers
```

Do not maintain a divergent Codex-only skill. Codex install targets are copies or symlinks of this canonical folder.

## Skill package shape

Codex skills use a self-contained folder with a required `SKILL.md` file. `SKILL.md` frontmatter must include at least:

```yaml
---
name: llm-wiki
description: Maintain the LLM Wiki in <knowledge-repo> from immutable raw notes through reviewed wiki pages and optional Graphify graph outputs.
---
```

Keep platform-specific details in references like this file. Keep the main `SKILL.md` portable and concise.

Reference links for re-checking:

- OpenAI Help: <https://help.openai.com/articles/20001066-skills-in-chatgpt>
- Local Codex skill authoring guide, when present: `${CODEX_HOME:-~/.codex}/skills/.system/skill-creator/SKILL.md`

## Install targets

Preferred install modes:

1. **Project-local canonical source**: keep using `skills/llm-wiki/` directly when Codex is launched from the knowledge repository and has this skill path in context.
2. **User-level Codex install**: copy or symlink canonical source to:

   ```text
   ${CODEX_HOME:-~/.codex}/skills/llm-wiki/
   ```

3. **Project-level Codex install**, only when explicitly desired:

   ```text
   <knowledge-repo>/.codex/skills/llm-wiki/
   ```

The install helper, if used, must support `--dry-run` and print the resolved source and target before writing.

## Dry-run install checks

Expected safe checks:

```bash
python3 skills/llm-wiki/scripts/install_skill.py --help
python3 skills/llm-wiki/scripts/install_skill.py --dry-run --platform codex
```

A dry-run must not create `.codex/`, write user-level files, install packages, or run Graphify. It should print at least:

- canonical source path;
- target Codex skill path;
- copy vs symlink strategy;
- whether an existing target would be overwritten in a real run.

## Invocation behavior

Codex should use `llm-wiki` when a user asks to:

- ingest selected `raw/` notes into wiki pages;
- query or maintain `wiki/`;
- lint wiki consistency;
- update `wiki/index.md` or `wiki/log.md`;
- refresh or consult the Graphify output under `graphify-out/wiki/`.

When the task involves Graphify, read `references/graphify.md` before proposing or running commands.

When the task involves page structure, read `references/wiki-schema.md` before creating wiki files.

## Codex-specific guardrails

- Treat `<knowledge-repo>/raw/` as read-only even if filesystem permissions allow writes.
- Do not run package installs or real Graphify commands from an automatic skill trigger.
- For current-date or external command behavior, verify with local `--help` or official docs rather than relying on stale memory.
- Prefer local validation commands and dry-runs over network operations.
- Keep citations in answers tied to `wiki/` pages and raw provenance, not to generated Graphify summaries alone.

## Post-install sanity check

After a real install/sync, check:

```bash
test -f "${CODEX_HOME:-$HOME/.codex}/skills/llm-wiki/SKILL.md" || \
  test -f ".codex/skills/llm-wiki/SKILL.md"
```

Then inspect that the installed `SKILL.md` still points to the canonical references and does not contain a forked Codex-only workflow.
