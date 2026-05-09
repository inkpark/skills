---
name: dev-flow
description: "Automates the commit-merge-push workflow: auto-commit, merge to target branch, push, return to working branch."
---

# Dev Flow

自动化开发工作流 — 将多步 git 操作整合为一条命令。通过子命令支持多种工作流。

## 触发方式

| 命令 | 行为 |
|------|------|
| `/dev-flow` | 执行默认的 `merge-test` 工作流 |
| `/dev-flow:merge-test` | 同上（显式指定工作流） |
| `/dev-flow:commit-push` | 执行 `commit-push` 工作流 |

未来可扩展 `/dev-flow:hotfix`、`/dev-flow:release` 等子命令。

当本技能被触发时，解析子命令（`:` 之后的部分），路由到对应工作流；无子命令则使用默认的 `merge-test`。

## 配置文件

首次运行自动创建 `.dev-flow/config.yaml`：

```yaml
target_branch: test
```

`target_branch` 是合并目标分支名，默认 `test`。绝大多数场景只需这一项。

每次运行前都确保 `.dev-flow/` 已写入 `.gitignore`（不存在则创建，存在则追加）；若 `.dev-flow/` 已被 `git` 跟踪，则先中止 `merge-test` 并询问用户：由我代为执行 `git rm --cached -r .dev-flow/`，还是由用户自行清理后再继续。

<details>
<summary>高级配置</summary>

```yaml
target_branch: test
add_mode: -A          # git add 模式
protected_branches: [] # 禁止操作的分支
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `add_mode` | `-A` | `-A`(全部改动) / `-u`(仅已跟踪) / `.`(不含删除) |
| `protected_branches` | `[]` | 在此列表中的分支上执行会直接拒绝，如 `["main", "master"]` |

</details>

## 工作流：merge-test

将当前分支改动提交 → 合并到目标分支 → 推送 → 切回原分支。

### 主流程

1. **读取配置** — 获取 `target_branch`、`add_mode`、`protected_branches`（不存在则自动创建）
2. **检查分支安全** — `git branch --show-current` 记录 `WORKING_BRANCH`；如果在 `protected_branches` 中则拒绝
3. **提交** — `git add <add_mode>` → `git diff --cached` → 分析 diff 生成 commit message → `git commit -m`；提交信息中不得包含 `Co-authored-by:` 或其他 AI 协作签名尾注。
4. **无改动时** — 询问用户是否跳过提交直接合并推送；用户拒绝则终止
5. **切换到目标分支** — 确保 `target_branch` 存在（本地检查 → 远程检查 → 新建）→ `git checkout` → `git pull`
6. **合并** — `git merge --no-ff <WORKING_BRANCH>`
7. **推送并返回** — `git push origin <target_branch>` → `git checkout <WORKING_BRANCH>` → `git push origin <WORKING_BRANCH>`（首次推送使用 `-u`）→ 提示检查 CI/CD

Commit message 语言规则：diff 或项目文件中包含中文（注释、字符串、文档）则用中文，否则用英文。

## 工作流：commit-push

先 `git add`、`git commit`，再 `git pull`，最后将当前分支推送到远程；不执行合并到其他分支的操作。

### 主流程

1. **检查分支安全** — `git branch --show-current` 记录 `WORKING_BRANCH`；如果在 `protected_branches` 中则拒绝
2. **暂存改动** — 执行 `git add <add_mode>`
3. **提交改动** — 执行 `git commit -m`，提交信息规则同 `merge-test`
4. **拉取远程更新** — 在当前分支执行 `git pull`
5. **推送当前分支** — 执行 `git push origin <WORKING_BRANCH>`（首次推送使用 `-u`）

### 异常处理

| 场景 | 行为 |
|------|------|
| 受保护分支 | 直接拒绝，报错终止 |
| 无改动 | 询问用户是否跳过提交继续 |
| 当前在目标分支上 | 跳过 checkout/merge，`pull` 后直接 push |
| 目标分支不存在 | 本地检查 → 远程 track → 本地新建 |
| 合并冲突 | 留在目标分支，报错终止，等待手动处理 |
| Push 被拒绝 | 报错终止，绝不 force push |

### 安全规则

- **绝不 force push** — 任何情况下不使用 `--force` 或 `--force-with-lease`
- **受保护分支不可操作** — 在 `protected_branches` 中的分支上拒绝执行
- **冲突立即停止** — 不推送、不切回、不自动解决
- **报错信息明确** — 每步失败说明原因、当前状态和下一步操作
- **远程固定为 `origin`** — 不可配置
- **`.dev-flow/` 永不入库** — `.dev-flow/` 及其子文件不得被 `git` 跟踪；若检测到已跟踪条目，`merge-test` 必须暂停并让用户选择由我执行 `git rm --cached -r .dev-flow/` 或由用户自行处理。
- **提交信息禁止 AI 协作署名** — `Co-authored-by:` 或其他 AI 协作/协同署名 trailer 不得出现在最终 commit message 中。

## 扩展子命令

添加新工作流时，在本文档新增 `## 工作流：<name>` 章节即可。用户通过 `/dev-flow:<name>` 调用。

当前已实现：`merge-test`（默认）、`commit-push`。
