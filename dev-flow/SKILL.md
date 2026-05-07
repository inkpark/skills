---
name: dev-flow
description: "Automates the commit-merge-push workflow through the /dev-flow slash command: auto-commit with AI-generated messages, merge to target branch, push, and return to the working branch."
---

# Dev Flow

自动化开发工作流技能，将多步 git 操作整合为一条命令。当前版本只有一个默认工作流：`merge-test`。

## 如何触发

直接输入：

```text
/dev-flow
```

当前 `/dev-flow` 会执行默认的 `merge-test` 工作流。

> `/dev-flow:merge-test` 不会被当前技能系统自动注册为可执行 slash command。当前运行时只会把本技能注册为 `/dev-flow`。

后续如果需要多个独立命令，应拆分为多个技能，或改造成插件 / commands 体系。

## 前置条件

### 配置文件

在项目根目录创建 `.dev-flow/config.yaml`。首次运行时如果不存在则自动创建，并同步更新 `.gitignore`：

```yaml
target_branch: test
add_mode: -A
protected_branches: []
```

- `target_branch`：合并的目标分支名，默认 `test`
- `add_mode`：`git add` 的模式，可选值：
  - `-A`（默认）：暂存所有改动（包括新增、修改、删除）
  - `-u`：仅暂存已跟踪文件的修改和删除，不包含新文件
  - `.`：暂存当前目录及子目录下的新增和修改，不包含删除
- `protected_branches`：受保护分支列表（如 `["main", "master"]`），在这些分支上执行 `/dev-flow` 时会直接拒绝
- 如果配置文件不存在，执行命令时自动创建：
  1. 创建 `.dev-flow/` 目录和 `config.yaml`（使用默认值）
  2. 检查项目根目录的 `.gitignore`，确保包含 `.dev-flow/` 条目；如果没有则追加
  3. 本次提交时会一并提交 `.gitignore` 的修改和 `.dev-flow/config.yaml`

## 默认工作流：merge-test

### 功能

将当前工作分支的改动自动提交、合并到目标分支、推送、然后切回工作分支。

### 执行流程

1. 读取配置：
   - 如果 `.dev-flow/config.yaml` 存在 → 直接读取配置项
   - 如果不存在 → 自动创建：
     a. 创建 `.dev-flow/` 目录和 `config.yaml`（写入默认配置）
     b. 检查项目根目录 `.gitignore` 是否包含 `.dev-flow/` 条目：
        - 如果 `.gitignore` 不存在 → 创建并写入 `.dev-flow/`
        - 如果存在但不含 `.dev-flow/` → 追加 `.dev-flow/` 条目
        - 如果已包含 → 跳过
     c. 记录：后续 `git add` 和提交时一并包含 `.gitignore` 和 `.dev-flow/config.yaml` 的修改
   - 配置项：`target_branch`（默认 `test`）、`add_mode`（默认 `-A`）、`protected_branches`（默认 `[]`）
2. 记录当前分支名：`git branch --show-current`，记为 `WORKING_BRANCH`
3. 检查 `WORKING_BRANCH` 是否在 `protected_branches` 中：
   - 如果在，立即报错终止：
     > 当前分支 `<WORKING_BRANCH>` 在受保护分支列表中，不允许通过 /dev-flow 操作。请手动处理。
4. `git add <add_mode>` — 暂存改动（模式由 `add_mode` 配置决定，默认 `-A`）
   - 如果步骤 1 中自动创建了文件，额外执行 `git add .dev-flow/config.yaml .gitignore` 确保这些文件被纳入本次提交
5. `git diff --cached` — 获取暂存区 diff 内容
6. 分析 diff 内容，生成有意义的 commit message。语言选择规则：如果 diff 或项目文件中包含中文注释、字符串、文档 → 使用中文；否则使用英文。
7. `git commit -m "<生成的 message>"`
8. 如果没有内容可提交（nothing to commit）：
   - 询问用户："当前没有可提交的改动，是否继续执行合并和推送？"
   - 选项：`是，继续合并推送` / `否，终止流程`
   - 如果用户选择"否"，终止流程，不再执行后续步骤
9. 如果 `WORKING_BRANCH == target_branch`（当前已在目标分支上）：
   - 执行 `git pull origin <target_branch>`（拉取远程最新代码，防止 push 被拒绝）
   - 如果 pull 失败（如网络问题、认证失败），报错并终止
   - 跳过步骤 10-13（ensure target / checkout / merge）
   - 直接执行步骤 14（push 目标分支）
   - 然后跳过步骤 15（checkout 回工作分支 — 实际仍在目标分支，无需切换）
   - 步骤 16 中只 push 目标分支，跳过 push 工作分支（二者相同）
10. 确保 `target_branch` 存在：
    - 检查本地：`git show-ref --verify refs/heads/<target_branch>`
    - 如果本地不存在，检查远程：`git ls-remote --heads origin <target_branch>`
    - 如果远程存在 → `git checkout -b <target_branch> origin/<target_branch>`
    - 如果都不存在 → `git checkout -b <target_branch>`
11. `git checkout <target_branch>`
12. `git pull origin <target_branch>`
    - 如果 pull 失败（如网络问题、认证失败），报错并终止
13. `git merge --no-ff <WORKING_BRANCH>`
    - 使用 `--no-ff` 确保总是生成 merge commit，保持分支历史清晰
    - **如果发生冲突**：立即报错终止，不推送，不切回工作分支。告知用户：
      > 合并冲突！当前停留在 `<target_branch>` 分支。请手动解决冲突后重新执行合并。
14. `git push origin <target_branch>`
    - **绝不使用 `--force` 或 `--force-with-lease`**
    - 如果 push 被拒绝（non-fast-forward），报错终止：
      > 推送被拒绝！目标分支 `<target_branch>` 可能有新的远程提交。请手动 pull 后重试。
15. `git checkout <WORKING_BRANCH>`
16. `git push origin <WORKING_BRANCH>`
    - 如果是首次推送（没有设置 upstream），使用 `git push -u origin <WORKING_BRANCH>`
    - 推送失败则报错，但不回滚之前的操作
17. （建议）提示用户检查 CI/CD 状态，确认远程仓库合并结果符合预期

### 边界情况

| 场景 | 处理方式 |
|------|----------|
| 当前在受保护分支上 | 直接拒绝执行，报错终止 |
| 工作区无改动（nothing to commit） | 询问用户是否继续后续的合并和推送步骤 |
| 当前已在目标分支上 | 拉取远程最新代码后直接 commit 并 push 目标分支 |
| 目标分支不存在 | 先检查远程（origin），有则 track，无则基于当前 HEAD 本地新建 |
| 合并冲突 | 报错终止，不推送，不切回工作分支，等待用户手动处理 |
| Push 被拒绝（non-fast-forward） | 报错终止，绝不使用 force push |

### 安全规则

- **绝不 force push**：任何情况下都不使用 `--force` 或 `--force-with-lease`
- **受保护分支不可操作**：在 `protected_branches` 中列出的分支上拒绝执行任何操作
- **冲突时立即停止**：合并冲突时不再继续执行后续步骤
- **报错信息明确**：每一步失败都要给出清晰的错误信息、失败原因和当前 git 状态
- **不自动解决冲突**：所有冲突由用户手动处理
- **远程仓库固定为 `origin`**：不可配置
