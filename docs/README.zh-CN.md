# Agent Skills

这是一个 AI Agent 技能集合，用来扩展 Agent 在知识管理、开发工作流和工具使用方面的能力。

English documentation: [README.md](../README.md)。

## 写作与知识管理

这些技能帮助 Agent 捕获、组织、查询和维护可复用知识。

- llm-wiki — 从不可变的原始笔记维护可审阅的 Markdown LLM Wiki，支持语种记忆、摄入、查询、lint 与持续沉淀。

  ```bash
  npx skills@latest add inkpark/skills/llm-wiki
  ```

  本地 dry-run 安装器：

  ```bash
  python3 llm-wiki/scripts/install_skill.py --dry-run --platform codex
  ```

## 添加更多技能

这个仓库会作为个人技能目录持续扩展。新增技能时，把每个技能作为顶层目录，并提供 `SKILL.md` 入口；如果技能需要更多上下文或辅助工具，可以增加 `references/`、`samples/`、`scripts/` 等目录。

推荐结构：

```text
<skill-name>/
  SKILL.md
  references/
  samples/
  scripts/
```

每个技能都应尽量自包含、默认安全，并让 Agent 不需要阅读整个仓库也能理解如何使用。

## 关于

我的个人可移植 AI Agent 技能目录。

### 资源

- [英文 README](../README.md)
- [llm-wiki 技能](../llm-wiki/)

### 许可证

Apache License. 见 [LICENSE](../LICENSE)。
