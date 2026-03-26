# DevFlow Agent

## Overview / 概览

DevFlow Agent is an AI-assisted project focused on repository understanding, requirement
analysis, implementation planning, and patch draft generation for software engineering
workflows.

DevFlow Agent 是一个面向软件工程流程的 AI 辅助项目，重点支持代码仓库理解、需求分析、
实现规划和 patch 草案生成。

## Project Focus / 项目重点

This repository is organized around repository understanding, requirement analysis,
implementation planning, and patch draft generation for software engineering workflows.

本仓库围绕代码仓库理解、需求分析、实现规划和 patch 草案生成等软件工程流程能力进行组织。

## Repository Layout / 仓库布局

- `app/`: future application code, including API, agent, tools, retrieval, repository, and
  code-intelligence modules
- `tests/`: future automated tests
- `examples/`: future demos and usage examples
- `doc/`: project-level plans and iteration roadmap
- `specs/`: feature-level specifications, plans, and task breakdowns

- `app/`：后续应用代码，包括 API、agent、tools、retrieval、repository 与 code-intelligence 模块
- `tests/`：后续自动化测试
- `examples/`：后续演示示例与使用样例
- `doc/`：项目级规划与迭代路线图
- `specs/`：feature 级规格、计划与任务拆解

## Planned Root Files / 根级基础文件

- `pyproject.toml`: project metadata and Python baseline
- `.env.example`: example environment variables
- `docker-compose.yml`: baseline local service composition
- `Makefile`: common project commands

- `pyproject.toml`：项目元数据与 Python 基线配置
- `.env.example`：环境变量示例
- `docker-compose.yml`：本地服务组合基线文件
- `Makefile`：常用项目命令入口

## Development Environment / 开发环境

Create and activate the local virtual environment before running development commands:

在运行开发命令前，请先创建并激活本地虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

- `make run` uses the project virtual environment Python.
- `make test` runs the repository test suite through the virtual environment.
- `make lint` performs a lightweight compile check for `app/` and `tests/`.

- `make run` 会使用项目虚拟环境中的 Python。
- `make test` 会通过虚拟环境运行仓库测试。
- `make lint` 会对 `app/` 与 `tests/` 做轻量编译检查。

## Related Documents / 关联文档

- `doc/devflow_agent_project_plan.md`: master project vision and technical context
- `doc/devflow_agent_iteration_plan.md`: seven-iteration roadmap
- `doc/git_commit_message_conventions.md`: git commit message format conventions

- `doc/devflow_agent_project_plan.md`：总体项目愿景与技术上下文
- `doc/devflow_agent_iteration_plan.md`：7 次迭代路线图
- `doc/git_commit_message_conventions.md`：git 提交信息格式约定

## Iteration 4 Status / 第四次迭代状态

The repository now includes Iteration 4 retrieval capabilities: semantic document search,
code search enriched with symbol metadata, exact/partial symbol lookup, and metadata-aware
filtering and ranking. All retrieval logic lives under `app/rag/`, backed by a local Qdrant
vector database instance.

仓库当前已具备迭代 4 的检索能力：语义文档检索、富含符号元数据的代码检索、精确/部分符号查找，
以及基于元数据的过滤与排序。所有检索逻辑位于 `app/rag/` 下，由本地 Qdrant 向量数据库支撑。

### Prerequisites / 前置条件

1. Start a local Qdrant instance (default port 6333):
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```
2. Set an OpenAI-compatible API key:
   ```bash
   export OPENAI_API_KEY=your-key-here
   ```
3. Install dependencies:
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -e ".[dev]"
   ```

1. 启动本地 Qdrant 实例（默认端口 6333）：
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```
2. 设置 OpenAI 兼容的 API 密钥：
   ```bash
   export OPENAI_API_KEY=your-key-here
   ```

### CLI Commands / 命令行接口

| Command | Description |
|---------|-------------|
| `python -m app.main --index .` | Index the repository into Qdrant |
| `python -m app.main --search-docs "QUERY"` | Search document chunks by meaning |
| `python -m app.main --search-code "QUERY"` | Search code chunks by intent |
| `python -m app.main --lookup-symbol "NAME"` | Look up symbol by name |
| `--filter-path "app/repo/*"` | Filter results by file path prefix |
| `--filter-symbol-kind "function"` | Filter results by symbol kind |
| `--max-results N` | Limit result count (default 10) |

### Previous Iterations / 前序迭代

- **Iteration 2**: Repository scanning and chunking (`app/repo/`, `app/codeintel/`)
- **Iteration 3**: Code intelligence extraction — symbol inventory and structural relationships

- 运行 `python3 -m app.main` 可以预览纳入范围的扫描记录、排除路径数量与切块数量。
- 仓库扫描逻辑位于 `app/repo/`。
- 切块逻辑位于 `app/codeintel/`。
