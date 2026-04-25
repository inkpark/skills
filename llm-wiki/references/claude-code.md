# Claude Code Reference for the LLM Wiki Skill

Use this reference when installing, syncing, or invoking the canonical `llm-wiki` skill from Claude Code.
For agents that are not Claude Code, prefer `references/ai-agent-integration.md` unless a dedicated verified reference exists.

## Canonical source of truth

The canonical skill lives in the knowledge repository:

```text
<knowledge-repo>/skills/llm-wiki/
```

Claude-specific files are install targets or configuration helpers only. Do not fork the workflow into a separate Claude-only source package.

## Claude Code environment notes

Claude Code is a terminal-based coding assistant. Official Claude Code docs describe project/user configuration through `CLAUDE.md` and `.claude/settings.json`; settings can be user-level or project-level. When integrating a skill, keep the LLM Wiki rules in the canonical `SKILL.md` and use Claude files only to point Claude Code at that canonical source.

Reference links for re-checking:

- Claude Code overview: <https://docs.anthropic.com/en/docs/claude-code/overview>
- Claude Code setup: <https://docs.anthropic.com/en/docs/claude-code/getting-started>
- Claude Code settings: <https://docs.anthropic.com/en/docs/claude-code/settings>

## Install targets

Preferred install modes:

1. **Project-local canonical source**: keep `skills/llm-wiki/` under the knowledge repository as the audited source.
2. **User-level Claude skill target**, when the local Claude Code installation supports skills:

   ```text
   ~/.claude/skills/llm-wiki/
   ```

3. **Project-level Claude skill target**, when supported and explicitly desired:

   ```text
   <knowledge-repo>/.claude/skills/llm-wiki/
   ```

4. **CLAUDE.md pointer fallback**: if the Claude installation does not support a native `skills/` directory, add a short `CLAUDE.md` pointer instructing Claude to read `skills/llm-wiki/SKILL.md` for wiki-maintenance tasks. Do not paste the full skill body into `CLAUDE.md` because that creates drift.

The install helper, if used, must print the resolved target and strategy in `--dry-run` mode and must not write unless dry-run is disabled explicitly.

## Dry-run install checks

Expected safe checks:

```bash
python3 skills/llm-wiki/scripts/install_skill.py --help
python3 skills/llm-wiki/scripts/install_skill.py --dry-run --platform claude-code
```

Dry-run output should include:

- canonical source path;
- target path (`~/.claude/skills/llm-wiki/` or project-level target);
- copy/symlink strategy;
- whether a `CLAUDE.md` pointer would be suggested;
- whether an existing target would be overwritten in a real run.

A dry-run must not install Claude Code, edit `.claude/settings.json`, run Graphify, or create/update `graphify-out/`.

## Invocation behavior

Claude Code should apply `llm-wiki` when the user asks to maintain or query the knowledge repository's LLM Wiki:

- ingest selected raw notes into reviewable wiki pages;
- update indexes, logs, source summaries, concept pages, or workflow pages;
- lint for stale summaries, missing provenance, duplicate concepts, contradictions, or over-fragmentation;
- generate or consult a Graphify graph.

For Graphify tasks, read `references/graphify.md` first. For page shape, read `references/wiki-schema.md` first.

## Claude-specific guardrails

- Claude Code may have broad local file access depending on settings. Still treat `raw/` as immutable by policy.
- Do not add hooks that automatically run Graphify or read the full knowledge repository on every prompt. Graphify builds must remain explicit because they may use model/API resources and can expose note contents to configured providers.
- If using `.claude/settings.json`, prefer deny rules for secrets and generated/cache folders. Do not hide `skills/llm-wiki/` or `wiki/` from normal skill operation.
- Keep `CLAUDE.md` content short and pointer-based to avoid a second copy of the skill.

Example pointer fallback:

```markdown
# LLM Wiki Skill

For tasks about ingesting, maintaining, querying, linting, or graphing the knowledge repository's LLM Wiki, read `skills/llm-wiki/SKILL.md` and follow it as the canonical workflow. Do not edit `raw/`. Do not run Graphify or install packages unless explicitly requested.
```

## Post-install sanity check

After a real install/sync, verify the installed or linked target still matches the canonical package:

```bash
test -f "$HOME/.claude/skills/llm-wiki/SKILL.md" || \
  test -f ".claude/skills/llm-wiki/SKILL.md" || \
  grep -q 'skills/llm-wiki/SKILL.md' CLAUDE.md
```

If the target contains a copied `SKILL.md`, compare it against `skills/llm-wiki/SKILL.md` before trusting it.
