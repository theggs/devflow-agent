# Git Commit Message Conventions / Git 提交信息约定

## Purpose / 目的

This document defines the preferred git commit message format for this repository.

本文档定义本仓库推荐使用的 git 提交信息格式。

The goal is to keep history easy to scan, easy to search, and easy to understand during
review.

目标是让提交历史在代码审查、问题定位和项目回顾时更易浏览、更易检索、更易理解。

## Required Format / 必须格式

Use the following subject-line format:

提交标题统一使用如下格式：

```text
<type>: <short summary>
```

Examples:

示例：

```text
feat: implement repository scanning and chunking foundation
docs: add iteration 2 study notes
fix: handle binary-file detection in ingestion pipeline
chore: allow env example in gitignore
test: add chunk pipeline coverage
refactor: split scan record creation from scanner
```

## Allowed Types / 允许的类型

- `feat`: new user-facing or system-facing functionality
- `fix`: bug fix or correctness fix
- `docs`: documentation-only change
- `test`: add or update tests
- `refactor`: internal restructuring without intended behavior change
- `chore`: repository maintenance, tooling, or housekeeping

- `feat`：新增功能
- `fix`：缺陷修复或正确性修复
- `docs`：纯文档变更
- `test`：新增或更新测试
- `refactor`：不改变预期行为的内部重构
- `chore`：工具、配置、仓库维护类工作

## Style Rules / 风格规则

- Use lowercase for `type`
- Keep the summary concise and specific
- Prefer imperative phrasing such as `add`, `implement`, `update`, `fix`
- Do not end the summary with a period
- Avoid vague messages such as `update files`, `fix stuff`, or `misc changes`

- `type` 使用小写
- 标题保持简洁、具体
- 优先使用祈使式动词，例如 `add`、`implement`、`update`、`fix`
- 标题结尾不要加句号
- 避免使用 `update files`、`fix stuff`、`misc changes` 这类模糊表述

## Scope Guidance / 适用范围建议

Use one commit for one coherent logical change whenever practical.

在可行的情况下，一个 commit 应只表达一个清晰、连贯的逻辑变更。

Good examples:

较好的例子：

- `feat: implement repository scanning and chunking foundation`
- `docs: add iteration 2 study notes`
- `test: add ingestion service coverage`

Less desirable examples:

不推荐的例子：

- `feat: implement feature and update docs and cleanup config`
- `chore: many changes`

## How This Applies To Codex / 这条规则如何约束 Codex

Codex is more likely to follow this convention consistently when the rule appears in:

当以下位置同时存在这条规则时，Codex 更容易稳定遵循：

1. This repository document
2. `AGENTS.md` repository instructions
3. The user request in the same conversation when asking for a commit

1. 本文档
2. `AGENTS.md` 仓库级指令
3. 你在当前对话里提出提交请求时的明确说明

## Optional Stronger Enforcement / 可选的更强约束

If stricter enforcement is needed later, consider adding one of the following:

如果未来需要更强约束，可以继续增加下面任一机制：

- a git commit template
- a local `commit-msg` hook
- a CI check for commit subject format

- git commit template
- 本地 `commit-msg` hook
- CI 中的 commit message 格式检查
