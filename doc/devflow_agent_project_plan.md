# DevFlow Agent 项目计划

## Document Role / 文档角色

This document is the master project plan for DevFlow Agent. It defines the overall vision,
target capabilities, technical direction, architecture, and end-state goals.

本文档是 DevFlow Agent 的总体项目计划，定义项目整体愿景、目标能力、技术方向、系统架构与
最终目标。

## Related Documents / 关联文档

- `doc/devflow_agent_iteration_plan.md`: standalone seven-iteration roadmap / 独立的 7 次项目迭代路线图
- `specs/001-init-task-docs/plan.md`: initialization iteration plan / 初始化迭代的 feature 级实施计划

## Usage / 使用方式

- Read this document for the full project vision and technical context.
- Read `doc/devflow_agent_iteration_plan.md` for the project-level delivery sequence.
- Read feature-local planning files under `specs/` for execution details of a specific
  iteration.

- 阅读本文档以了解完整的项目愿景与技术上下文。
- 阅读 `doc/devflow_agent_iteration_plan.md` 以查看项目级交付顺序。
- 阅读 `specs/` 下的 feature 文档以查看某次具体迭代的执行细节。

## 项目定位

**DevFlow Agent：面向代码仓库的开发辅助 Agent**

总体目标：
- 在项目创建过程中深入 agent 技术及 agent开发技术，以利于求职
- 创建一个 agent 项目，用于展示对 agent 开发技术有切实实践，以利于求职

目标：构建一个贴近真实软件工程流程的 AI Agent
系统，用于帮助开发者理解代码仓库、分析需求、生成实现计划以及生成 patch
草案。

系统能力包括：

-   代码库理解
-   Issue / 需求分析
-   实现方案规划
-   检索相关代码与文档
-   生成修改建议或 patch 草案
-   输出可审核结果（Human-in-the-loop）

该项目重点体现：

-   Agent workflow
-   RAG
-   tool calling
-   代码理解
-   工程化 API 服务

------------------------------------------------------------------------

# 一、完整技术方案

## 1.1 项目目标

系统输入示例：

-   "帮我理解这个仓库的模块划分"
-   "这个 issue 应该改哪些文件"
-   "为这个需求生成实现计划"
-   "给出 patch 草案，但不要直接提交"
-   "解释这个函数和相关调用链"

系统输出结构：

-   相关文件
-   证据片段
-   修改计划
-   patch 草案
-   风险点
-   人工审核建议

------------------------------------------------------------------------

## 1.2 推荐技术栈

### Agent 编排

LangGraph（Python）

### API 层

FastAPI

### 向量数据库

Qdrant

### 代码解析

Tree-sitter

### 模型层

可插拔 LLM：

-   OpenAI API
-   Anthropic API
-   本地兼容 OpenAI API

------------------------------------------------------------------------

## 1.3 系统架构

系统分为六层：

### A. Ingestion / Indexing

负责把代码仓库转化为可检索知识：

-   扫描仓库文件
-   过滤无关目录（.git、node_modules、dist、build）
-   使用 Tree-sitter 提取函数、类、文件结构
-   提取 README、docs、配置文件
-   写入 Qdrant

索引粒度：

-   文件级 chunk
-   符号级 chunk（函数、类）
-   文档级 chunk

------------------------------------------------------------------------

### B. Retrieval

检索机制：

-   语义检索
-   元数据过滤
-   符号检索
-   LLM rerank

------------------------------------------------------------------------

### C. Planning

将用户请求转换为结构化任务。

例如：

输入：

"给登录接口加结构化日志"

输出：

-   定位入口 handler
-   找 service 调用链
-   找日志模式
-   生成 patch 草案

------------------------------------------------------------------------

### D. Tools

Agent 使用工具：

-   search_docs
-   search_code
-   read_file
-   list_symbols
-   write_patch_draft

------------------------------------------------------------------------

### E. Agent Graph

基本流程：

request → classify → retrieve → analyze → plan → patch → final_answer

------------------------------------------------------------------------

### F. Human-in-the-loop

输出必须包含：

-   证据文件
-   相关代码片段
-   风险提示
-   是否需要人工审核

------------------------------------------------------------------------

# 二、GitHub 项目结构

    devflow-agent/
    ├── README.md
    ├── pyproject.toml
    ├── .env.example
    ├── docker-compose.yml
    ├── Makefile
    ├── app/
    │   ├── main.py
    │   ├── config.py
    │   ├── schemas/
    │   ├── api/
    │   ├── agent/
    │   ├── tools/
    │   ├── rag/
    │   ├── repo/
    │   ├── codeintel/
    │   └── llm/
    ├── tests/
    └── examples/

------------------------------------------------------------------------

# 三、关键功能模块

## 代码仓库索引

-   扫描仓库
-   解析源码结构
-   生成 chunk
-   embedding
-   写入 Qdrant

------------------------------------------------------------------------

## RAG 检索

支持：

-   文档检索
-   代码检索
-   符号检索

------------------------------------------------------------------------

## Planner

把用户请求转化为实现步骤。

输出：

-   修改步骤
-   影响范围
-   风险提示

------------------------------------------------------------------------

## Patch Draft

生成 patch 草案：

-   diff 内容
-   修改说明
-   review_required 标记

------------------------------------------------------------------------

# 四、简历写法

项目名称：

**DevFlow Agent｜AI 工程项目**

描述：

面向软件工程流程的开发辅助 Agent
系统，支持代码仓库索引、代码理解、需求分析与 patch 草案生成。

核心能力：

-   代码仓库索引与语义检索
-   Issue → 实现计划生成
-   Patch Draft 自动生成
-   Human-in-the-loop 审核机制

技术栈：

-   LangGraph
-   FastAPI
-   Qdrant
-   Tree-sitter
-   Python

------------------------------------------------------------------------

# 五、7 天开发计划

说明：本节是 7 次项目迭代的来源草案；整理后的独立路线图见
`doc/devflow_agent_iteration_plan.md`。

Note: this section is the source outline for the seven project iterations; the normalized
standalone roadmap is available in `doc/devflow_agent_iteration_plan.md`.

## Day 1

目标：

-   建立 GitHub 仓库
-   搭建基础项目结构
-   配置 FastAPI / LangGraph / Qdrant
-   编写 README 初版

------------------------------------------------------------------------

## Day 2

目标：

-   实现仓库扫描
-   过滤无关目录
-   chunk 文档与代码
-   写入向量数据库

------------------------------------------------------------------------

## Day 3

目标：

-   集成 Tree-sitter
-   提取函数 / 类 / 文件结构
-   建立 symbol index

------------------------------------------------------------------------

## Day 4

目标：

-   实现 RAG 查询
-   实现 search_docs / search_code

------------------------------------------------------------------------

## Day 5

目标：

-   实现 planner
-   输出实现计划

------------------------------------------------------------------------

## Day 6

目标：

-   实现 patch draft
-   输出 diff 建议

------------------------------------------------------------------------

## Day 7

目标：

-   完善 README
-   增加演示示例
-   编写基础测试
-   准备简历描述

------------------------------------------------------------------------

# 项目最终目标

完成后应具备：

-   可运行 API
-   可索引代码仓库
-   支持代码理解问答
-   支持需求 → 实现计划
-   支持 patch 草案生成
