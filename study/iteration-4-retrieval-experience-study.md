# 迭代 4 学习笔记：检索能力建设（Retrieval Experience）

> **面向读者**：有大型分布式系统和软件开发管理经验，但对 AI/ML 技术了解有限的读者。
>
> **目标**：读完本文，你能清晰理解"给代码仓库加上语义搜索"这件事在技术上是怎么做的，以及每个组件承担什么职责。

---

## 一、这次迭代做了什么？

### 1.1 背景：前三次迭代做了什么

| 迭代 | 产出 |
|------|------|
| 迭代 1 | 项目骨架，目录结构，基础配置 |
| 迭代 2 | 扫描仓库，把文件分成"文档切块"和"代码切块"，类似把书拆成章节 |
| 迭代 3 | 提取代码的符号清单（函数名、类名、调用关系），类似给书建索引 |
| **迭代 4** | **在切块和索引的基础上，实现"用自然语言提问、找到相关内容"的检索能力** |

### 1.2 交付的四个核心能力

```
用自然语言问 "仓库怎么扫描文件的？"
       │
       ▼
[文档语义搜索]  → 返回最相关的文档切块 + 来源路径 + 相关性分数

用自然语言问 "哪里有处理符号提取的代码？"
       │
       ▼
[代码语义搜索]  → 返回最相关的代码切块 + 函数名 + 所在文件行号

输入符号名 "build_scan_preview"
       │
       ▼
[符号精确查找]  → 不用语义，直接按名字精确/模糊匹配，返回定义位置

对任何搜索加上条件 --filter-path "app/repo/*"
       │
       ▼
[元数据过滤]    → 结果只保留路径匹配的文件
```

### 1.3 新增的 CLI 命令

```bash
# 先把仓库索引进向量数据库（一次性或重新索引）
python -m app.main --index .

# 按语义搜索文档
python -m app.main --search-docs "how is the repository scanned"

# 按语义搜索代码
python -m app.main --search-code "extract symbols from source files"

# 按名字查找符号（函数/类）
python -m app.main --lookup-symbol "build_scan_preview"

# 加上路径过滤
python -m app.main --search-code "scan" --filter-path "app/repo/*"

# 加上符号类型过滤
python -m app.main --search-code "class" --filter-symbol-kind "class"
```

---

## 二、涉及了哪些技术？

这次迭代的核心是 **RAG（Retrieval-Augmented Generation）流程中的检索层**。即使现在还没有生成（Generation）部分，检索层是一切 AI 问答能力的基础。

### 2.1 核心技术概念地图

```
原始内容（代码/文档）
        │
        ▼
  [Embedding 向量化]     ← 把文字变成一串数字（高维向量），语义相近的文字在空间上距离近
        │
        ▼
  [向量数据库存储]        ← 专门为"找最近邻向量"设计的数据库（Qdrant）
        │
  ┌─────┴──────┐
  │ 查询时：    │
  │ 用户输入    │
  │ 同样向量化  │
  │     │      │
  │     ▼      │
  │ [相似度搜索]│  ← 在向量空间里找距离最近的 K 个点
  │     │      │
  │     ▼      │
  │ [排序/过滤] │  ← 结合元数据权重调整排名
  └─────┬──────┘
        │
        ▼
   返回结果列表
```

### 2.2 Embedding（向量嵌入）——把语义变成数字

这是整个检索能力的核心假设，也是 AI 检索与传统关键词检索最本质的区别。

**传统关键词搜索的问题：**
- 搜索"扫描文件" → 只能找到包含"扫描文件"这几个字的文档
- 搜索"scan repository" → 找不到写着"read directory"的代码，即使语义完全相同

**Embedding 解决了什么：**

```
"扫描仓库文件"  →  [0.12, -0.87, 0.34, 0.95, ...]  (1536 维向量)
"scan repository files" → [0.11, -0.85, 0.36, 0.93, ...]  (几乎相同的向量)
"读取目录内容"  →  [0.10, -0.83, 0.35, 0.91, ...]  (向量也很接近)
"数据库连接配置" → [0.89,  0.23, -0.67, -0.12, ...]  (向量完全不同)
```

这 1536 个数字不是人为定义的特征，而是 OpenAI 的神经网络模型（`text-embedding-3-small`）从数百亿文本中学习出来的"语义坐标系"。语义相近的内容，在这个坐标系中的距离就近。

> **类比给有分布式经验的读者**：这相当于一致性哈希里的"哈希空间"，只不过这个哈希函数不是为了均匀分布，而是为了把语义相近的内容映射到相近的位置。

### 2.3 向量数据库（Qdrant）——为"找相邻点"而生

普通数据库（MySQL、PostgreSQL）擅长的是：
- `WHERE id = 123`（精确匹配）
- `WHERE price < 100`（范围过滤）
- `LIKE '%keyword%'`（字符串匹配）

**向量数据库擅长的是完全不同的查询：**

```
给我找 1000 万个向量中，
与 [0.12, -0.87, 0.34, 0.95, ...] 这个点
距离最近的前 10 个
```

这个问题如果暴力计算需要对比 1000 万次，向量数据库用 HNSW（层级图导航算法）等索引结构把它降到 O(log N)。

**Qdrant 还额外支持"带过滤条件的近邻搜索"：**

```
找最相近的 10 个向量，但只在 source_path 以 "app/repo/" 开头的点里找
```

这正是迭代 4 的元数据过滤功能所依赖的能力。

> **类比**：Qdrant 相当于 Elasticsearch，只不过 ES 的核心是倒排索引（词频统计），Qdrant 的核心是向量近邻索引。两者都支持附加元数据过滤。

### 2.4 两个集合（Collection）的设计决策

迭代 4 建了两个独立的 Qdrant 集合，而不是一个：

```
documents 集合                    code 集合
─────────────────────────────    ─────────────────────────────────────
chunk_id                          chunk_id
source_path (文件路径)            source_path (文件路径)
repository_context (顶层目录)    repository_context (顶层目录)
chunk_text (全文)                 chunk_text (全文)
line_start / line_end             line_start / line_end
                                  symbol_name (函数名/类名)
                                  symbol_kind (function/class/method)
                                  structural_role (顶层/嵌套/容器)
```

分开存的原因：
- 文档搜索和代码搜索是不同的查询路径
- 代码切块有额外的符号元数据字段（来自迭代 3），文档切块不需要
- 避免混合查询时必须每次都加 `content_type = "code"` 过滤条件

### 2.5 符号查找为什么不用 Embedding

符号名（`build_scan_preview`、`IngestionService`）是**标识符**，不是自然语言。

- Embedding 把 `"build_scan_preview"` 和 `"build_chunk_preview"` 映射到非常接近的向量（因为它们字面相似）
- 但用户想要精确匹配，不是"语义上差不多的"
- 精确/模糊名字匹配直接遍历迭代 3 的符号清单，时间复杂度 O(N)，对单仓库完全够用

这是一个"不要为了用技术而用技术"的设计判断：**语义搜索不适合所有场景**。

---

## 三、使用了哪些库，怎么用的？

### 3.1 `qdrant-client`（向量数据库 Python 客户端）

**角色**：与本地 Qdrant 实例通信的 Python SDK

#### 3.1.1 建集合（`ensure_collections`）

```python
from qdrant_client import QdrantClient
from qdrant_client.http import models

client = QdrantClient(host="localhost", port=6333)

client.recreate_collection(
    collection_name="documents",
    vectors_config=models.VectorParams(
        size=1536,                        # 向量维度，必须与 Embedding 模型一致
        distance=models.Distance.COSINE,  # 相似度计算方式：余弦相似度
    ),
)
```

`recreate_collection` 的语义是"如果存在就删掉重建"，这保证了重新索引的幂等性。

#### 3.1.2 写入向量（`upsert`）

```python
from qdrant_client.http import models

points = [
    models.PointStruct(
        id=0,                              # 唯一 ID（整数）
        vector=[0.12, -0.87, 0.34, ...],  # 1536 维 Embedding 向量
        payload={                          # 可附加任意 JSON 元数据
            "chunk_id": "app/main.py:code:1",
            "source_path": "app/main.py",
            "symbol_name": "create_app",
            "symbol_kind": "function",
            "chunk_text": "def create_app() -> dict:...",
            "line_start": 1,
            "line_end": 20,
        },
    ),
    # ... 更多 points
]

client.upsert(collection_name="code", points=points)
```

#### 3.1.3 语义搜索（`search`）

```python
# 带元数据过滤的语义搜索
results = client.search(
    collection_name="code",
    query_vector=[0.11, -0.85, 0.36, ...],  # 用户查询的 Embedding
    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="source_path",
                match=models.MatchText(text="app/repo/"),  # 前缀过滤
            )
        ]
    ),
    limit=11,  # 多取 1 个，用来判断是否还有更多结果
)

# results 是 ScoredPoint 列表，每个元素包含：
# result.score    → 相似度分数 (0~1，越高越相关)
# result.payload  → 存入时的元数据字典
```

### 3.2 `openai`（Embedding 生成客户端）

**角色**：调用 OpenAI（或 OpenAI 兼容接口）的 Embedding API，把文本转成向量

```python
from openai import OpenAI

client = OpenAI(api_key="sk-...")

response = client.embeddings.create(
    model="text-embedding-3-small",  # 1536 维，速度快、成本低
    input=[
        "def create_app() -> dict:",       # 可以批量传入
        "how is the repository scanned",
    ],
)

# response.data 是列表，每个元素对应一个输入文本的 Embedding
vectors = [item.embedding for item in response.data]
# vectors[0] → [0.12, -0.87, 0.34, ...]  (1536 个浮点数)
# vectors[1] → [0.08, -0.91, 0.29, ...]
```

> **成本参考**：`text-embedding-3-small` 每 100 万 token 约 $0.02。一个中型仓库（10,000 个切块）全量索引一次大约消耗 2-5 美元。

**可插拔设计**（`base_url` 参数）：

```python
# 切换到本地 Ollama 或其他 OpenAI 兼容服务
client = OpenAI(
    api_key="not-needed",
    base_url="http://localhost:11434/v1",  # 本地模型接口
)
```

这让整个检索系统在不改代码的情况下可以切换到任意兼容 OpenAI 协议的 Embedding 服务。

### 3.3 库的使用模式总结

| 操作 | 使用的库 | 调用位置 |
|------|---------|---------|
| 生成文本向量 | `openai` | `app/rag/embedding.py` |
| 创建/重建集合 | `qdrant-client` | `app/rag/indexing.py` |
| 写入向量+元数据 | `qdrant-client` | `app/rag/indexing.py` |
| 语义搜索 | `qdrant-client` | `app/rag/search_service.py` |
| 元数据过滤转换 | `qdrant-client` | `app/rag/search_service.py` |
| 符号名匹配 | 纯 Python（无需外部库） | `app/rag/symbol_search.py` |

---

## 四、数据流全景图

```
┌─────────────────────────────────────────────────────────────────┐
│                        索引阶段（--index）                        │
│                                                                  │
│  仓库文件                                                         │
│     │                                                            │
│     ├─ [迭代 2] 扫描 → 文档切块 (DocumentChunk)                  │
│     │                  代码切块 (CodeChunk)                       │
│     │                                                            │
│     └─ [迭代 3] 提取 → 符号清单 (SymbolInventoryEntry)            │
│                                                                  │
│  文档切块 ──→ [OpenAI Embedding API] ──→ 1536维向量               │
│                                           │                      │
│                                    写入 Qdrant                   │
│                                    documents 集合                 │
│                                                                  │
│  代码切块 ──→ [OpenAI Embedding API] ──→ 1536维向量               │
│    +符号元数据（从符号清单匹配行号获得）      │                    │
│                                    写入 Qdrant                   │
│                                    code 集合                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      查询阶段（--search-docs / --search-code）    │
│                                                                  │
│  用户输入: "how is the repository scanned"                        │
│     │                                                            │
│     ▼                                                            │
│  [OpenAI Embedding API] → 1536维查询向量                          │
│     │                                                            │
│     ▼                                                            │
│  [Qdrant search()]                                               │
│   ├─ 向量相似度排名（余弦相似度）                                   │
│   └─ 可选：元数据过滤（路径前缀、符号类型）                          │
│     │                                                            │
│     ▼                                                            │
│  [排序增强] 相似度分数 + 元数据 boost 信号（±0.03~0.05 微调）       │
│     │                                                            │
│     ▼                                                            │
│  SearchResponse                                                  │
│   ├─ results: [SearchResult, ...]  (含 chunk_text, 路径, 行号)   │
│   └─ has_more: bool  (是否还有更多结果)                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  符号查找阶段（--lookup-symbol）                   │
│                                                                  │
│  用户输入: "build_scan_preview"                                   │
│     │                                                            │
│     ▼                                                            │
│  [纯内存匹配] 遍历迭代 3 的符号清单                                 │
│   ├─ 精确匹配 (match_quality = "exact")  → 排前面                │
│   └─ 子串匹配 (match_quality = "partial") → 排后面               │
│     │                                                            │
│     ▼                                                            │
│  [SymbolLookupResult, ...]  (含文件路径、行号、结构角色)            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 五、设计上值得关注的判断

### 5.1 幂等索引（Idempotent Indexing）

每次执行 `--index` 都会重建集合（`recreate_collection`），而不是增量更新。

- **好处**：实现极其简单，不需要处理"哪些切块是新的/修改的/删除的"这个复杂问题
- **代价**：每次全量重新 Embedding，有 API 调用成本
- **判断依据**：在迭代 4 阶段仓库规模有限，全量重建比增量同步的实现代价低得多

这是一个典型的"做够用的设计，不过度工程化"的判断。

### 5.2 has_more 字段的实现技巧

```python
# 请求 max_results + 1 个结果
fetch_limit = query.max_results + 1
hits = client.search(limit=fetch_limit)

# 如果拿到了 max_results+1 个，说明还有更多
has_more = len(hits) > query.max_results
hits = hits[:query.max_results]  # 返回时截断回 max_results 个
```

这是 API 设计中常用的"多取一个判断是否有下一页"技巧，避免了额外的 `COUNT` 查询。

### 5.3 Embedding 向量化的批处理

```python
# 不是一个一个调用，而是批量传入
vectors = embed_texts([chunk.content_excerpt for chunk in all_chunks])
```

OpenAI Embedding API 支持批量输入，一次 HTTP 请求处理多个文本，显著降低延迟和成本。

---

## 六、这次迭代在整体架构中的位置

```
┌───────────────────────────────────────────────────────────────┐
│                     DevFlow Agent 整体架构                     │
│                                                               │
│  app/repo/        ← 迭代 2：仓库扫描、切块                     │
│  app/codeintel/   ← 迭代 3：符号提取、结构关系                  │
│  app/rag/         ← 迭代 4：向量索引、语义搜索  ◄ 本次迭代      │
│  app/tools/       ← 迭代 5（规划中）：Agent 工具定义            │
│  app/agent/       ← 迭代 6（规划中）：规划引擎                  │
│  app/api/         ← 迭代 7（规划中）：对外 API                  │
└───────────────────────────────────────────────────────────────┘
```

迭代 4 是整个 AI 能力的**基础设施层**：没有准确的检索，后续迭代的 Agent 规划引擎就没有可靠的上下文可以使用。这和分布式系统里"服务发现和配置中心"的地位类似——它本身不是业务功能，但所有业务功能都依赖它。

---

## 七、关键词速查

| 术语 | 一句话解释 |
|------|-----------|
| Embedding | 把文本转换成高维数字向量，语义相近的文本向量距离近 |
| 向量数据库 | 专门为"找最相近的向量"优化的数据库，Qdrant 是其中一种 |
| RAG | 检索增强生成，先检索相关内容，再让 LLM 基于检索结果回答 |
| HNSW | 向量数据库内部用的近邻搜索算法，类似跳表，O(log N) 复杂度 |
| 余弦相似度 | 向量间夹角的余弦值，1 代表完全相同，0 代表完全不相关 |
| Collection | Qdrant 中的表，类似 MySQL 的 table 或 ES 的 index |
| Payload | Qdrant 中附加在向量点上的元数据（JSON），用于过滤和返回 |
| text-embedding-3-small | OpenAI 提供的 Embedding 模型，输出 1536 维向量 |
| 幂等索引 | 无论执行多少次，结果都相同；重建比增量更新简单 |
