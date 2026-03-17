# 第二次迭代学习笔记：Repository Scanning & Chunking

## 文档目的

这份文档面向有大型分布式软件经验、也有研发管理经验，但对 AI 技术体系还不熟的读者。

目标不是讲“怎么写这段 Python 代码”，而是讲清楚三件事：

1. 这次迭代到底交付了什么功能。
2. 这些功能在一个 AI Agent 系统里处于什么位置。
3. 这次实现用到了哪些技术和库，它们分别解决什么问题。

---

## 1. 这次迭代具体做了什么功能

### 1.1 一句话总结

这次迭代为 DevFlow Agent 建立了“仓库内容进入 AI 系统之前的入口层”。

更准确地说，它做了三件事情：

1. 扫描代码仓库，找出哪些文件应该进入后续 AI 处理流程。
2. 过滤掉不该进入流程的内容，比如二进制文件、媒体文件、缓存目录、构建产物。
3. 把纳入范围的文本文件切成两类基础数据：
   - 文档切块 `DocumentChunk`
   - 代码切块 `CodeChunk`

### 1.2 这在 AI Agent 系统里意味着什么

如果把整个 DevFlow Agent 看成一个“能理解代码仓库、再回答问题或生成计划”的系统，那么这次迭代做的是最前面的 `Ingestion` 阶段。

可以把它类比成分布式系统里的“数据接入层”：

- 上游是代码仓库本身
- 中间是扫描、过滤、归类、切块
- 下游才是向量索引、检索、推理、规划、patch 生成

也就是说，这次迭代还没有进入：

- embedding
- 向量数据库
- LLM 推理
- RAG 检索
- agent graph orchestration

但它已经把这些后续能力最依赖的输入契约建立起来了。

### 1.3 本次实际落地的功能模块

这次实现里，核心逻辑分成了几层：

#### A. 扫描候选项生成

对应代码：

- [app/repo/scanner.py](app/repo/scanner.py)

它负责遍历仓库，把文件先变成 `ScanCandidate`。

你可以把 `ScanCandidate` 理解为：

- “这个文件我发现了”
- “它可能是什么内容类型”
- “它看起来是不是文本文件”

这一步还没有真正接入 AI，只是在做“候选输入识别”。

#### B. 作用域过滤

对应代码：

- [app/repo/path_rules.py](app/repo/path_rules.py)
- [app/repo/content_types.py](app/repo/content_types.py)
- [app/repo/scan_records.py](app/repo/scan_records.py)

这里定义了两个核心判断：

1. 路径上是否应该排除
2. 文件类型上是否应该排除

例如：

- `.git/`
- `node_modules/`
- `dist/`
- `build/`
- 图片、音频、视频、压缩包、编译产物

都会被挡在系统外面。

这是一个很关键的工程判断：AI 系统不是“把所有文件都喂进去”，而是要先做输入治理。

#### C. 扫描记录生成

对应代码：

- [app/repo/scan_records.py](app/repo/scan_records.py)

通过过滤后，候选项会被转换为 `ScanRecord`。

`ScanRecord` 是这次迭代特别重要的设计点。

它的意义是：

- 扫描和切块之间不直接耦合
- 中间先形成一个可审查、可解释、可调试的中间产物

对于有分布式系统经验的人，这很像：

- ingestion pipeline 里的 normalized event
- ETL 流程里的 staging record
- 数据平台里的 canonical intermediate representation

这一步让系统从“直接处理文件”升级为“先产生规范化中间对象，再进入后续处理”。

#### D. 切块

对应代码：

- [app/codeintel/document_chunker.py](app/codeintel/document_chunker.py)
- [app/codeintel/code_chunker.py](app/codeintel/code_chunker.py)

这次切块不是为了最终用户直接看到，而是为了后续：

- 做 embedding
- 做向量检索
- 做 rerank
- 做基于上下文的 LLM 推理

这里最重要的不是“切多少字符”，而是先建立两个概念：

1. 文档和代码必须分开建模
2. 每个 chunk 必须携带来源上下文 metadata

这两个约束对后续 AI 效果影响很大。

### 1.4 为什么要把文档和代码分开

因为它们服务的检索和推理目标不同。

文档通常回答：

- 这个模块是干什么的
- 配置应该怎么写
- 使用方式是什么

代码通常回答：

- 逻辑实现在哪
- 调用链怎么走
- 哪些文件需要改

如果把它们混成一种 chunk，后续检索很容易出现：

- 文档问题命中一堆代码
- 代码问题命中一堆 README
- rerank 难以判断真实语义相关性

所以这次迭代的价值，不只是“把文件切开”，而是建立“AI 检索对象的语义边界”。

---

## 2. 此功能涉及了什么技术？这次迭代运用了什么技术？

### 2.1 从 AI 系统角度看，涉及哪些技术主题

虽然这次没有直接调用 LLM，也没有上向量库，但它已经涉及了 AI 工程里的几个基础主题。

#### 1. Ingestion

这是 AI 系统最容易被忽略、但实际上最关键的一层。

很多人会把注意力放在模型、prompt、agent graph 上，但真实工程里，模型质量很大程度取决于输入治理是否扎实。

这次迭代做的就是 ingestion 的前半部分：

- 文件发现
- 文件分类
- 输入过滤
- 中间表示生成
- chunk 准备

#### 2. Knowledge Representation

这次不是直接把仓库当“文件集合”，而是把它重构成一组结构化对象：

- `ScanCandidate`
- `ScanRecord`
- `DocumentChunk`
- `CodeChunk`
- `ChunkContextMetadata`

这属于知识表示的基础设计。

在 AI 系统里，好的知识表示会显著影响：

- 可解释性
- 可测试性
- 检索准确率
- 后续 schema 演进能力

#### 3. Retrieval Preparation

这次还没有做 retrieval，但已经在为 retrieval 预制数据形态。

后续做向量检索时，最常见的问题不是“embedding 模型不好”，而是：

- chunk 太粗
- chunk 太细
- 文档和代码混在一起
- metadata 不足
- 来源不可追踪

这次迭代做的其实就是 retrieval preparation。

#### 4. Human-in-the-loop / Reviewable AI

这次明确引入了 `ScanRecord` 和 `ScanPreview` 这种“可审查中间结果”。

这很符合企业级 AI 系统的设计风格：

- 不追求黑盒自动化
- 先让过程可解释
- 先让输入输出可审查
- 再逐步增加自动推理能力

这对生产系统尤其重要，因为很多 AI 失败并不是模型推错，而是输入内容本身就不可信。

### 2.2 从软件工程角度看，这次具体用了哪些技术

#### 1. Python 3.11+

本次实现语言是 Python。

选择 Python 的原因不是“因为 AI 都用 Python”，而是因为它在这里同时适合三类工作：

- 文件系统遍历
- 文本处理
- 后续接入 AI 生态

Python 在这个阶段的优势主要是：

- 标准库足够强
- 数据建模成本低
- 与后续 FastAPI、LangGraph、Qdrant、Tree-sitter 等生态兼容

#### 2. `dataclass` + `StrEnum`

对应代码：

- [app/schemas/repository_ingestion.py](app/schemas/repository_ingestion.py)

这是这次实现最核心的建模手段。

为什么不用裸 `dict`？

因为这里做的不是脚本，而是“面向未来 AI 系统的数据契约层”。

使用 `dataclass` 的意义：

- 结构清晰
- 字段稳定
- 便于阅读
- 便于测试
- 便于后续演进到 Pydantic、API schema、持久化 schema

使用 `StrEnum` 的意义：

- 枚举值既有约束，又方便序列化
- 更适合后续写入向量库 metadata 或 API 输出

#### 3. 文件系统遍历与启发式分类

对应代码：

- [app/repo/scanner.py](app/repo/scanner.py)
- [app/repo/content_types.py](app/repo/content_types.py)

这次没有引入复杂解析器，而是先使用：

- 路径规则
- 扩展名规则
- 文件名规则
- 字节采样规则

例如：

- 通过扩展名识别源码、文档、媒体、二进制
- 通过读取前 2KB 内容判断是不是文本
- 通过是否包含 `\x00` 字节排除非文本

这是一种很典型的“先用低成本启发式建立 80% 能力”的方法。

对于第一版 ingestion，这是合理的工程选择。

#### 4. Pipeline 分层

这次虽然代码量不大，但结构上已经体现了 pipeline 设计：

1. `discover_scan_candidates`
2. `build_scan_record`
3. `build_chunks`

这意味着系统不是一段大函数，而是有明确阶段边界。

这会给后续带来几个好处：

- 每层都可以单测
- 每层都可以替换实现
- 每层都可以扩展策略

例如未来可以很自然地替换为：

- 更复杂的文件分类器
- Tree-sitter 驱动的代码切块器
- 更细粒度的文档分段器

#### 5. 本地可验证入口

对应代码：

- [app/main.py](app/main.py)

本次没有直接做 API，而是先提供一个本地 preview 命令：

```bash
python -m app.main
```

这个做法很像在服务化之前先准备一个：

- smoke-test entrypoint
- debug entrypoint
- pipeline preview command

对于早期 AI 系统，这是非常实用的做法。

---

## 3. 为了实现功能使用了哪些库？这些库所涉及的使用方式是什么？

### 3.1 本次迭代真正使用到的库

这次实现非常克制，真正参与功能实现的“库”并不多。

#### A. Python 标准库

这是本次最核心的依赖。

主要包括：

- `pathlib`
- `dataclasses`
- `enum`

##### `pathlib`

用途：

- 遍历目录
- 处理相对路径
- 读文件内容

使用方式：

- `Path.cwd()`
- `root.rglob("*")`
- `path.relative_to(root)`
- `path.read_text(...)`
- `path.read_bytes()`

为什么重要：

在 AI ingestion 里，路径语义是很关键的 metadata。`pathlib` 让路径处理更稳定，也比字符串拼接更不容易出错。

##### `dataclasses`

用途：

- 定义 schema 对象
- 让中间数据结构显式化

使用方式：

- `@dataclass(frozen=True)` 定义不可变的中间对象
- `field(default_factory=list)` 定义容器默认值

为什么重要：

这一步在工程上相当于“先定义数据契约，再写处理逻辑”，这对 AI 系统尤其重要。

##### `enum.StrEnum`

用途：

- 定义有限状态和分类值

使用方式：

- `ContentCategory`
- `ChunkStrategy`
- `ScopeDecision`
- `ReviewStatus`

为什么重要：

在后续 embedding、vector store、API response 中，这类枚举值会反复出现。提前规范，有利于避免术语漂移。

#### B. pytest

这次不是业务逻辑依赖，而是开发依赖。

对应配置：

- [pyproject.toml](pyproject.toml)

用途：

- 验证扫描逻辑
- 验证 chunk pipeline 的行为

当前测试文件：

- [tests/repo/test_ingestion_service.py](tests/repo/test_ingestion_service.py)
- [tests/codeintel/test_chunk_pipeline.py](tests/codeintel/test_chunk_pipeline.py)

使用方式：

- 通过 `.venv/bin/python -m pytest`
- 使用断言验证：
  - `README.md` 会进入 document chunk
  - `app/main.py` 会进入 code chunk
  - chunk strategy 会按预期分流

为什么重要：

AI 系统很容易把测试全推迟到“结果层”，但其实 ingestion 这种底层阶段更适合做确定性测试。

#### C. ruff

同样是开发依赖。

这次虽然还没有在实现流程里重点使用它，但已经放进了 `dev` 依赖组。

用途：

- 后续静态检查
- 保持 Python 代码风格一致

对管理者视角可以这样理解：

`ruff` 在这里不是“AI 技术的一部分”，而是“把 AI 原型尽快拉回到工程化轨道”的工具。

### 3.2 这次没有真正用上、但在计划里出现的技术

这部分很值得特别说明，因为它反映的是“路线图”和“当期交付”的区别。

#### 1. FastAPI

状态：

- 在项目计划里出现
- 本次未实际使用

它未来的角色更可能是：

- 暴露扫描、检索、规划等 API

但这次迭代还停留在本地 preview 和中间数据结构阶段。

#### 2. LangGraph

状态：

- 在项目计划里出现
- 本次未实际使用

它未来的角色是：

- 组织 agent workflow
- 管理 request -> retrieve -> analyze -> plan -> patch 的状态流

但在没有稳定 ingestion 输入之前，用 LangGraph 其实意义不大。

#### 3. Qdrant

状态：

- 在项目计划里出现
- 本次未实际使用

它未来的角色是：

- 存储 embedding 后的 chunk
- 支持向量检索

这次迭代做的 chunking，本质上是在为 Qdrant 准备“写进去的对象”。

#### 4. Tree-sitter

状态：

- 在项目计划里出现
- 本次未实际使用

它未来的角色是：

- 做更精细的代码结构提取
- 从“按行切 code chunk”升级到“按函数/类/语法结构切 chunk”

所以可以把这次的实现看成：

- 当前：启发式文件分类 + 简化切块
- 下一步：结构化代码理解

### 3.3 这次库使用的总体风格

这次实现体现的是一种很工程化的节奏：

1. 先用标准库把流程边界搭起来
2. 先把 schema 建好
3. 先让 preview 和测试可运行
4. 再逐步引入更重的 AI 依赖

这比一开始就上：

- 向量库
- embedding 模型
- agent orchestration
- 复杂 parser

更稳健，也更适合演进式开发。

---

## 4. 你可以怎样理解这次迭代在整个项目中的位置

### 4.1 用传统系统架构语言来类比

如果把整个项目映射成一个更传统的软件系统：

- 第一次迭代：搭项目骨架
- 第二次迭代：搭数据接入与标准化层
- 第三次迭代：做结构化抽取
- 第四次迭代：做检索
- 第五次迭代：做规划
- 第六次迭代：做 patch draft
- 第七次迭代：做展示与验证

所以第二次迭代不是“小功能”，而是整个系统中最关键的输入基础设施。

### 4.2 如果这层没做好，后面会发生什么

如果扫描和切块层设计不好，后面会出现典型问题：

- 向量库里存进去一堆噪音
- 检索结果混乱
- LLM 上下文不稳定
- 规划输出引用错误文件
- patch draft 命中错误代码位置

换句话说：

后面的 AI 能力看起来像“智能问题”，但根因常常是这类输入层问题。

### 4.3 这次迭代的真正产出

从管理视角看，这次迭代的真正产出不是某个命令行输出，而是以下几个“未来能力的约束条件”已经被固定下来：

1. 什么内容允许进入 AI 系统
2. 什么内容必须被排除
3. 进入系统后，最小中间表示是什么
4. 后续检索对象至少要带哪些 metadata
5. 文档和代码是两个不同语义对象

这五点一旦建立，后续做向量索引、检索和 agent workflow 就有了工程边界。

---

## 5. 建议你继续学习的顺序

如果你想真正理解这个项目，建议按下面顺序看：

1. 先看 [app/schemas/repository_ingestion.py](app/schemas/repository_ingestion.py)
   先理解这次迭代的数据模型。
2. 再看 [app/repo/scanner.py](app/repo/scanner.py) 和 [app/repo/content_types.py](app/repo/content_types.py)
   理解“发现文件”和“判断类型”。
3. 再看 [app/repo/scan_records.py](app/repo/scan_records.py)
   理解为什么要有中间层。
4. 再看 [app/codeintel/chunk_pipeline.py](app/codeintel/chunk_pipeline.py)
   理解 chunk 是如何分流的。
5. 最后运行：

```bash
source .venv/bin/activate
python -m app.main
python -m pytest
```

这样你会同时看到：

- 运行结果
- 数据结构
- 自动化验证

---

## 6. 最后的总结

这次迭代的本质不是“做了一个扫描脚本”，而是：

为未来的 AI 检索和推理系统，建立了一个最小但清晰的输入治理层。

它的关键价值在于：

- 把仓库文件系统转换成 AI 可消费的数据对象
- 用显式 schema 替代隐式文件处理
- 用 reviewable preview 替代黑盒流程
- 为未来的 Qdrant、Tree-sitter、LangGraph 留出了清晰接入点

如果用一句更偏架构的话来概括：

这次迭代完成的是 DevFlow Agent 的 “AI-ready repository ingestion boundary”。
