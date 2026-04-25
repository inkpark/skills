# Agent Skills

A collection of agent skills that extend capabilities across knowledge management, development workflows, and tooling.

中文说明见 [docs/README.zh-CN.md](docs/README.zh-CN.md)。

## Writing & Knowledge

These skills help agents capture, organize, query, and maintain reusable knowledge.

- llm-wiki — Maintain a reviewable Markdown LLM Wiki from immutable raw notes, using guarded raw Graphify maps to improve wiki generation.

  ```bash
  npx skills@latest add inkpark/skills/llm-wiki
  ```

  Local dry-run installer:

  ```bash
  python3 llm-wiki/scripts/install_skill.py --dry-run --platform codex
  ```

## Adding More Skills

This repository is meant to grow as a personal skill directory. Add each new skill as a top-level folder with a `SKILL.md` entry point, plus optional `references/`, `samples/`, and `scripts/` folders when the skill needs more context or helper tooling.

Suggested structure:

```text
<skill-name>/
  SKILL.md
  references/
  samples/
  scripts/
```

Keep each skill self-contained, safe by default, and easy for an agent to understand without reading the entire repository.

## About

My personal directory of portable AI-agent skills.

### Resources

- [Chinese README](docs/README.zh-CN.md)
- [llm-wiki skill](llm-wiki/)

### License

Apache License. See [LICENSE](LICENSE).
