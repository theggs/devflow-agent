# DevFlow Agent Iteration Plan / DevFlow Agent 项目迭代计划

## Document Role / 文档角色

This document is the normalized project-level delivery roadmap. It translates the Day 1-
Day 7 outline from `doc/devflow_agent_project_plan.md` into seven standalone iterations
with explicit goals and expected outputs.

本文档是规范化后的项目级交付路线图。它将
`doc/devflow_agent_project_plan.md` 中的 Day 1-Day 7 草案整理为 7 次独立迭代，并明确每次
迭代的目标与预期产出。

## Related Documents / 关联文档

- `doc/devflow_agent_project_plan.md`: master project vision and source plan / 总体项目愿景与来源计划
- `specs/001-init-task-docs/plan.md`: initialization iteration planning details / 初始化迭代的 planning 细节

## Overview / 概览

This document is the standalone project-level roadmap for the next seven iterations of
DevFlow Agent. It is derived from `doc/devflow_agent_project_plan.md` and keeps the
project-wide delivery sequence separate from feature-local planning files.

本文档是 DevFlow Agent 后续 7 次迭代的独立项目级路线图，来源于
`doc/devflow_agent_project_plan.md`，用于将项目整体推进顺序与 feature 级执行文档分离。

## Planning Principles / 规划原则

- The current initialization iteration is separate from the seven future iterations.
- Each future iteration maps directly to one day in the Day 1-Day 7 plan.
- The roadmap focuses on intended outcomes and reviewable outputs, not low-level task
  decomposition.
- Project-level planning documents remain under `doc/`.

- 当前初始化迭代不计入后续 7 次迭代。
- 每次后续迭代都与 Day 1-Day 7 计划中的一天一一对应。
- 本路线图聚焦目标与可审查交付物，而不是底层任务拆解。
- 项目级规划文档统一保存在 `doc/` 目录。

## Current Iteration / 当前迭代

### Initialization Planning / 初始化规划

- Reorganize the master project plan into spec, plan, research, contract, and review
  artifacts.
- Clarify what is in scope now and what is deferred.
- Prepare the project for follow-up execution planning.

- 将总体项目计划整理为 spec、plan、research、contract 和审阅产物。
- 明确当前范围与后续延后范围。
- 为后续执行规划做好准备。

## Future Iterations / 后续迭代

### Iteration 1 - Repository & Skeleton Setup / 仓库与骨架搭建

**Source Alignment**: Day 1  
**Goal**: Establish the repository baseline and the initial runnable project skeleton.
**Expected Outputs**: Repository skeleton, base configuration files, initial README draft.

- Create the base repository structure.
- Prepare core configuration files and initial README content.
- Align directory boundaries for `app/`, `tests/`, and `examples/`.

- 建立基础仓库结构。
- 准备核心配置文件与 README 初版内容。
- 明确 `app/`、`tests/` 和 `examples/` 的目录边界。

### Iteration 2 - Repository Scanning & Chunking / 仓库扫描与切块

**Source Alignment**: Day 2  
**Goal**: Build the foundation for repository ingestion and indexed document/code chunks.
**Expected Outputs**: Repository scanning flow, directory filtering rules, chunking output definitions.

- Implement repository scanning flow.
- Exclude irrelevant directories from processing.
- Produce chunked document and code inputs for indexing.

- 实现仓库扫描流程。
- 过滤无关目录。
- 产出用于索引的文档与代码切块基础。

Implementation notes / 实现说明:

- Current implementation scans repository files through a reviewable scan-record stage
  before chunk generation.
- The active Iteration 2 scope is limited to text-based content and explicitly excludes
  binary and media files.

- 当前实现会先生成可审查的扫描记录，再进入切块流程。
- 当前第二次迭代范围仅包含文本型内容，并明确排除二进制与媒体文件。

### Iteration 3 - Code Intelligence Extraction / 代码结构提取

**Source Alignment**: Day 3  
**Goal**: Add code-structure understanding for symbols and file relationships.
**Expected Outputs**: Structure extraction flow, symbol inventory, code-intelligence metadata.

- Integrate structure extraction for files, functions, and classes.
- Build symbol-level organization for later retrieval.
- Prepare code intelligence outputs for analysis workflows.

- 集成文件、函数和类的结构提取。
- 建立后续检索所需的符号级组织能力。
- 为分析流程准备代码理解结果。

### Iteration 4 - Retrieval Experience / 检索能力建设

**Source Alignment**: Day 4  
**Goal**: Deliver practical document and code retrieval for downstream reasoning.
**Expected Outputs**: Document search, code search, retrieval filtering and ranking behavior.

- Implement document search.
- Implement code search.
- Improve retrieval quality with metadata-aware filtering and ranking.

- 实现文档检索。
- 实现代码检索。
- 通过元数据过滤和排序提升检索质量。

### Iteration 5 - Planning Engine / 规划引擎

**Source Alignment**: Day 5  
**Goal**: Convert user requests into structured implementation plans.
**Expected Outputs**: Review-ready planning output format, scope analysis, risk hints.

- Produce step-by-step change plans.
- Describe impact scope and risks.
- Keep planner outputs review-ready for humans.

- 生成分步骤的修改计划。
- 描述影响范围与风险点。
- 保持规划结果对人工评审友好。

### Iteration 6 - Patch Drafting / Patch 草案生成

**Source Alignment**: Day 6  
**Goal**: Generate reviewable patch drafts from analyzed user requests.
**Expected Outputs**: Patch draft format, modification notes, human-review checkpoints.

- Produce diff-style modification proposals.
- Add explanation and review notes for proposed changes.
- Preserve human-in-the-loop approval before final action.

- 生成 diff 风格的修改建议。
- 为建议变更补充说明与评审提示。
- 在最终动作前保留人工审核环节。

### Iteration 7 - Documentation, Examples, and Validation / 文档、示例与验证

**Source Alignment**: Day 7  
**Goal**: Polish the project for demonstration, validation, and presentation.
**Expected Outputs**: Improved README, demo examples, foundational tests, project presentation summary.

- Improve README and supporting documentation.
- Add example scenarios and foundational tests.
- Prepare presentation material and resume-oriented project summary.

- 完善 README 与配套文档。
- 增加演示示例与基础测试。
- 准备展示材料与面向简历的项目总结。

## Review Use / 使用方式

- Read this document for the project-wide delivery order.
- Read `doc/devflow_agent_project_plan.md` for the full vision and technical context.
- Read `specs/001-init-task-docs/plan.md` for the feature-local planning details of the
  initialization iteration.
- Use the source-alignment lines in each iteration to verify one-to-one mapping back to
  Day 1-Day 7 in `doc/devflow_agent_project_plan.md`.
- Treat this document as the roadmap view, and treat `doc/devflow_agent_project_plan.md`
  as the vision-and-architecture view.

- 阅读本文档以了解项目级交付顺序。
- 阅读 `doc/devflow_agent_project_plan.md` 以查看完整愿景与技术上下文。
- 阅读 `specs/001-init-task-docs/plan.md` 以查看初始化迭代的 feature 级计划细节。
- 使用每个迭代下的 Source Alignment 字段，核对其与
  `doc/devflow_agent_project_plan.md` 中 Day 1-Day 7 的一一对应关系。
- 将本文档视为路线图视图，将 `doc/devflow_agent_project_plan.md` 视为愿景与架构视图。
