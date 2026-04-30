---
name: dev-flow
description: "Automates development workflows: auto-commit with AI-generated messages, merge to target branch, push, and checkout back. First command: /dev-flow:merge-test"
---

# Dev Flow

自动化开发工作流技能，将多步 git 操作整合为一条命令。当前支持：

| 命令 | 功能 |
|------|------|
| `/dev-flow:merge-test` | 自动 commit → 合并到目标分支 → 推送 → 切回 |

后续将扩展更多工作流命令。

## 前置条件

### 配置文件

在项目根目录创建 `.dev-flow/config.yaml`（该目录应加入 `.gitignore`）：

```yaml
target_branch: test
```

- `target_branch`：合并的目标分支名，默认 `test`
- 如果配置文件不存在，执行命令时自动创建并使用默认值
- 建议将 `.dev-flow/` 目录加入项目的 `.gitignore`

---

## /dev-flow:merge-test

### 功能

将当前工作分支的改动自动提交、合并到目标分支、推送、然后切回工作分支。

### 执行流程

1. 读取 `.dev-flow/config.yaml`，获取 `target_branch`（默认 `test`）
2. `git add -A` — 暂存所有改动
3. `git diff --cached` — 获取暂存区 diff 内容
4. 分析 diff 内容，生成有意义的 commit message（根据代码内容自动选择中文或英文）
5. `git commit -m "<生成的 message>"`
6. 如果没有内容可提交（nothing to commit）：
   - 使用 question 工具询问用户："当前没有可提交的改动，是否继续执行合并和推送？"
   - 选项：`是，继续合并推送` / `否，终止流程`
   - 如果用户选择"否"，终止流程，不再执行后续步骤
7. 记录当前分支名：`git branch --show-current`，记为 `WORKING_BRANCH`
8. 如果 `WORKING_BRANCH == target_branch`（当前已在目标分支上）：
   - 跳过步骤 9-12（checkout / pull / merge）
   - 直接执行步骤 13（push 目标分支）
   - 然后执行步骤 14（checkout 回工作分支 — 实际仍在目标分支，无需切换）
   - 步骤 15 中只 push 目标分支，跳过 push 工作分支（二者相同）
9. 确保 `target_branch` 存在：
   - 检查本地：`git show-ref --verify refs/heads/<target_branch>`
   - 如果本地不存在，检查远程：`git ls-remote --heads origin <target_branch>`
   - 如果远程存在 → `git checkout -b <target_branch> origin/<target_branch>`
   - 如果都不存在 → `git checkout -b <target_branch>`
10. `git checkout <target_branch>`
11. `git pull origin <target_branch>`
    - 如果 pull 失败（如网络问题、认证失败），报错并终止
12. `git merge <WORKING_BRANCH>`
    - 使用普通 merge，允许生成 merge commit
    - **如果发生冲突**：立即报错终止，不推送，不切回工作分支。告知用户：
      > 合并冲突！当前停留在 `<target_branch>` 分支。请手动解决冲突后重新执行合并。
13. `git push origin <target_branch>`
    - **绝不使用 `--force` 或 `--force-with-lease`**
    - 如果 push 被拒绝（non-fast-forward），报错终止：
      > 推送被拒绝！目标分支 `<target_branch>` 可能有新的远程提交。请手动 pull 后重试。
14. `git checkout <WORKING_BRANCH>`
15. `git push origin <WORKING_BRANCH>`
    - 如果是首次推送（没有设置 upstream），使用 `git push -u origin <WORKING_BRANCH>`
    - 推送失败则报错，但不回滚之前的操作

### 边界情况

| 场景 | 处理方式 |
|------|----------|
| 工作区无改动（nothing to commit） | 询问用户是否继续后续的合并和推送步骤 |
| 当前已在目标分支上 | 跳过 checkout、pull、merge 步骤，直接 commit 并 push 目标分支 |
| 目标分支不存在 | 先检查远程（origin），有则 track，无则基于当前 HEAD 本地新建 |
| 合并冲突 | 报错终止，不推送，不切回工作分支，等待用户手动处理 |
| Push 被拒绝（non-fast-forward） | 报错终止，绝不使用 force push |

### 安全规则

- **绝不 force push**：任何情况下都不使用 `--force` 或 `--force-with-lease`
- **冲突时立即停止**：合并冲突时不再继续执行后续步骤
- **报错信息明确**：每一步失败都要给出清晰的错误信息、失败原因和当前 git 状态
- **不自动解决冲突**：所有冲突由用户手动处理
- **远程仓库固定为 `origin`**：不可配置
