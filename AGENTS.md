# devflow-agent Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-17

## Active Technologies
- Qdrant for vector search in later iterations; Markdown files for curren (001-init-task-docs)
- Python 3.11 for the planned backend; Markdown for planning and + FastAPI, LangGraph, Qdrant, Tree-sitter, pluggable LLM providers (002-repo-skeleton-setup)
- Repository files in git for this iteration; Qdrant remains a planned later (002-repo-skeleton-setup)
- Python 3.11 for repository scanning and chunk preparation logic; + Standard-library file traversal utilities for Iteration 2; (003-repo-scanning-chunking)
- Repository files in git as scan inputs and scan/chunk outputs; no external (003-repo-scanning-chunking)

- Python 3.11 (planned project implementation language); Markdown for + LangGraph, FastAPI, Qdrant, Tree-sitter, pluggable LLM providers (001-init-task-docs)

## Project Structure

```text
backend/
frontend/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.11 (planned project implementation language); Markdown for: Follow standard conventions

## Recent Changes
- 003-repo-scanning-chunking: Added Python 3.11 for repository scanning and chunk preparation logic; + Standard-library file traversal utilities for Iteration 2;
- 002-repo-skeleton-setup: Added Python 3.11 for the planned backend; Markdown for planning and + FastAPI, LangGraph, Qdrant, Tree-sitter, pluggable LLM providers
- 001-init-task-docs: Added Python 3.11 (planned project implementation language); Markdown for + LangGraph, FastAPI, Qdrant, Tree-sitter, pluggable LLM providers


<!-- MANUAL ADDITIONS START -->
- Use Conventional Commit subjects (`feat|fix|docs|test|refactor|chore: <short summary>`) and follow `doc/git_commit_message_conventions.md` before creating commits.
<!-- MANUAL ADDITIONS END -->
