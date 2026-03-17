# Repository Ingestion Example

## Example / 示例

Run `python3 -m app.main` to preview the current repository ingestion result.

运行 `python3 -m app.main` 可以预览当前仓库的扫描与切块结果摘要。

## Expected Output Shape / 预期输出结构

- `accepted_scan_records`: count of accepted text-based files
- `excluded_paths`: count of excluded files or paths
- `document_chunks`: count of generated document chunks
- `code_chunks`: count of generated code chunks

- `accepted_scan_records`：纳入范围的文本型文件数量
- `excluded_paths`：被排除的文件或路径数量
- `document_chunks`：生成的文档切块数量
- `code_chunks`：生成的代码切块数量
