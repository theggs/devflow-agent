# 第三次迭代学习说明：Code Intelligence Extraction / 代码结构提取

## 1. 这次迭代做了什么

这次迭代完成的不是“让 AI 直接回答问题”，而是让系统第一次具备了“理解代码结构”的基础能力。

如果第二次迭代解决的是：

- 哪些文件应该进入系统
- 这些文件如何变成 scan record 和 chunk

那么第三次迭代解决的是：

- 一个代码文件里有哪些结构化元素
- 这些结构化元素如何被表示成 AI 可消费的对象
- 文件、符号、符号之间的关系如何保留下来

从功能上看，这次迭代新增了 4 类核心产物：

1. `SourceFileStructure`
   表示一个源码文件的结构化视图。
2. `SymbolInventoryEntry`
   表示从文件中提取出来的符号条目，例如 class、function、method。
3. `StructuralRelationship`
   表示文件到符号、符号到符号之间的关系。
4. `CodeIntelligenceSnapshot`
   表示一次结构提取运行后的汇总快照。

这意味着系统现在已经不只是“知道有这个文件”，而是开始“知道这个文件里有什么结构、这些结构怎么互相关联”。

---

## 2. 这一轮功能的工程意义

对于一个面向代码仓库的 AI Agent 来说，真正有价值的并不是“把整个文件全文塞给模型”，而是把仓库内容转换成更适合推理和检索的中间表示。

这次迭代的意义可以理解为给系统补上了“代码理解层”的第一版：

1. 从文件级理解升级为符号级理解
2. 从平面文本升级为结构化对象
3. 从“有内容”升级为“有上下文、有关系”

它直接为后续几个能力做准备：

- 检索：后面就可以按 symbol 检索，而不是只能按文件检索
- 规划：后面分析一个需求时，可以定位到函数、类，而不是只能定位到文件
- 解释：后面可以回答“这个文件里有哪些主要结构”“某个函数属于哪个类”
- patch draft：后面生成修改建议时，可以更精准地定位修改范围

如果用大型分布式系统熟悉的语言来类比：

- 第二次迭代更像是做数据接入和标准化
- 第三次迭代更像是做面向上层查询和调度的语义索引层

也就是说，这一轮做的是“AI 系统的代码知识建模”。

---

## 3. 这次迭代具体实现了哪些功能

### 3.1 结构提取入口

主入口在：

- [structure_pipeline.py](../app/codeintel/structure_pipeline.py)

它的核心流程是：

1. 从第二次迭代的 `ScanRecord` 中挑出代码类输入
2. 读取源码文本
3. 提取 symbol inventory
4. 生成 source file structure
5. 生成 structural relationships
6. 汇总成 preview/snapshot

这是一条非常典型的 AI 工程流水线：

- 输入是上游标准化对象
- 中间是结构化抽取
- 输出是下游可复用的知识对象

这比把逻辑写成一坨黑盒函数更重要，因为后续检索、规划、评审、测试都能沿着这条链路复用。

### 3.2 符号提取

主要逻辑在：

- [symbol_inventory.py](../app/codeintel/symbol_inventory.py)

这里用了两种策略：

1. 对 Python 文件，优先用 `ast` 做结构化解析
2. 对非 Python 文件，退化为启发式解析

这是一个很实用的工程取舍。

原因是：

- Python 的 AST 是标准库内置、稳定且低成本的
- 但当前仓库未来会支持多语言，不能因为还没接 Tree-sitter 就完全没有结构提取能力

所以这次实现采用了“高可信优先 + 通用兜底”的模式：

- Python：准确性更高
- JS/TS/C 类风格文件：先用轻量 heuristic 提供基础能力

### 3.3 关系建模

关系逻辑在：

- [relationship_metadata.py](../app/codeintel/relationship_metadata.py)

这次显式保留了三类关系：

1. `file-contains-symbol`
2. `symbol-defined-in`
3. `symbol-contains-symbol`

这三类关系非常关键，因为它们共同定义了一个最小但可用的代码图谱：

- 文件里有什么符号
- 某个符号来自哪个文件
- 某个符号是不是另一个符号的子结构

对于后续 AI 系统而言，这种关系信息比单独的文本片段更有价值。

原因是模型在做推理时往往最依赖“上下文组织结构”，而不是孤立片段。

### 3.4 可审查预览

入口在：

- [app/main.py](../app/main.py)
- [ingestion_service.py](../app/repo/ingestion_service.py)

这一轮没有直接接入数据库或 API，而是先把结果做成可本地预览的形态。

运行：

```bash
.venv/bin/python -m app.main
```

当前会返回类似：

- accepted scan records 数量
- document chunk 数量
- code chunk 数量
- structured files 数量
- symbol inventory 数量
- relationships 数量
- sample symbols

这个设计很像分布式系统里常见的“可观测中间态”理念。

也就是：

- 不直接追求最终功能闭环
- 先让中间结果可看、可测、可验证

这对 AI 系统尤其重要，因为 AI 系统里最怕的是“结果好像不对，但不知道错在哪一层”。

---

## 4. 这次迭代涉及了哪些 AI 相关技术

虽然这轮没有调用大模型，但它本质上已经进入了 AI 系统的“知识表示与检索准备”阶段。

### 4.1 Code Intelligence

这是这轮最核心的主题。

Code Intelligence 可以理解为：

- 从源码中抽取结构信息
- 把源码转换成对工具和上层系统更友好的语义对象

典型包括：

- 文件结构
- 函数、类、方法
- 调用关系、包含关系、定义关系
- 符号位置信息

当前这轮实现的是其中最基础的一层：

- Symbol extraction
- Structural relationship preservation
- Reviewable snapshot

### 4.2 Intermediate Representation

这轮实际上做了 AI 系统中的中间表示设计。

也就是把“原始代码文件”转换成：

- `SourceFileStructure`
- `SymbolInventoryEntry`
- `StructuralRelationship`
- `CodeIntelligenceSnapshot`

这和编译器、搜索引擎、数据平台中常见的 IR 思路非常像。

好处是：

1. 上下游解耦
2. 便于测试和演化
3. 便于以后接向量检索或图检索

### 4.3 Retrieval Preparation

这轮还在为后续 Retrieval 做准备。

如果没有结构提取，后续检索只能做到：

- 找到某个文件

有了结构提取后，后续检索可以逐步升级为：

- 找到某个类
- 找到某个函数
- 找到某个方法
- 找到某个函数所属类或所属文件

这会显著提升后续 RAG、规划和修改建议的精度。

### 4.4 Heuristic Parsing

这轮采用了启发式解析作为多语言兜底方案。

这不是最终形态，但非常适合作为系统早期版本：

- 成本低
- 易理解
- 易调试
- 可逐步被更强解析器替换

你可以把它理解为：

- 当前先用轻量规则建立“基础能力”
- 未来再用 Tree-sitter 替换成更强、更稳定、更跨语言的解析方案

---

## 5. 这次迭代运用了什么技术

### 5.1 Python 标准库 AST

这是本轮最关键的技术点。

用于：

- 解析 Python 源文件
- 提取 class / function / method
- 保留嵌套结构
- 保留起止行号

使用方式大致是：

1. `ast.parse(content)` 生成 AST
2. 遍历 `body`
3. 识别 `ClassDef` / `FunctionDef` / `AsyncFunctionDef`
4. 递归进入嵌套节点
5. 记录父子关系与行号

对有架构经验的人来说，可以把它理解为一个轻量版 parser front-end。

### 5.2 启发式正则提取

用于非 Python 文件。

这里主要依赖：

- `re.match(...)`
- 花括号深度跟踪
- 简单的 parent stack

作用不是做到编译器级精度，而是做到“足够有用的结构抽取”。

这很符合 AI 工程里常见的策略：

- 先建立可用的结构信号
- 再逐步提高精度

### 5.3 Dataclass Schema 建模

本轮大量使用了 `dataclass` 做结构对象建模。

例如：

- `SourceFileStructure`
- `SymbolInventoryEntry`
- `StructuralRelationship`
- `CodeIntelligencePreview`

这样做的好处：

1. 数据结构清晰
2. 测试断言容易写
3. 未来序列化和持久化方便
4. 比直接传 dict 更稳定

### 5.4 分层流水线设计

本轮代码结构非常强调职责分层：

- `structure_extractor.py`：文件级结构输出
- `symbol_inventory.py`：符号提取
- `relationship_metadata.py`：关系建模
- `snapshot_builder.py`：汇总输出
- `structure_pipeline.py`：总编排

这是典型的“单一职责 + pipeline orchestration”设计。

对后续演进非常友好，因为以后你可以单独替换其中一层，而不是推倒重写。

---

## 6. 为了实现功能使用了哪些库

这次迭代有一个很重要的特点：

没有引入新的第三方 AI 库。

这是一个有意识的工程决策，不是“技术不够新”，而是“阶段性控制复杂度”。

### 6.1 实际使用的库/模块

#### Python 标准库

1. `ast`
   用于 Python 代码结构解析。

2. `re`
   用于非 Python 语言的启发式符号匹配。

3. `pathlib`
   用于路径处理、仓库文件访问、后缀判断。

4. `dataclasses`
   用于定义结构化 schema。

5. `enum.StrEnum`
   用于定义稳定、可比较、可序列化的分类枚举。

#### 开发与测试依赖

6. `pytest`
   用于验证结构提取、关系构建和仓库集成逻辑。

### 6.2 这些库的使用方式

#### `ast` 的使用方式

适合：

- 单语言高质量解析
- 需要结构和位置信息
- 不想引入额外依赖

当前用法属于“只取我们需要的结构信息”，而不是完整语义分析。

也就是说它不是在做：

- 类型推断
- 调用解析
- 控制流图

而是在做：

- 定义级别的结构抽取

#### `re` 的使用方式

适合：

- 多语言过渡期
- 先支持基础结构抽取
- 作为正式 parser 的兜底补丁层

当前它和花括号深度跟踪结合，能够识别一部分 class/function/method 的层级关系。

#### `dataclass` 的使用方式

适合：

- 做中间表示对象
- 做 pipeline 边界契约
- 写清晰的测试

这在 AI 工程里非常重要，因为 AI 系统如果没有稳定的中间对象，后续非常容易演变成“全是 dict 和隐式约定”的不可维护状态。

#### `pytest` 的使用方式

本轮新增测试覆盖了：

- 空符号文件与部分可提取文件
- 重复符号名与嵌套符号
- explicit / inferred 关系
- 与 Iteration 2 ingestion 的集成

也就是说测试不是只测“函数能运行”，而是测“结构抽取契约是否成立”。

这对于 AI 工程很关键，因为很多问题不是 crash，而是“语义不准确”。

---

## 7. 为什么这次没有直接使用 Tree-sitter、向量库、LLM

这是很多 AI 项目里很容易误判的一点。

很多人会觉得：

- 做代码理解就该马上上 Tree-sitter
- 做 AI 就该马上接 LLM
- 做检索就该马上接向量库

但从系统演化角度看，当前这轮先不接这些重组件是合理的。

原因是：

1. 当前首先要验证中间表示是否合理
2. 先验证 file/symbol/relationship 这三个层级是否足够支撑后续能力
3. 先验证测试和人工 review 能否稳定识别问题

如果这些基础对象还没稳定，过早接入：

- Tree-sitter
- Qdrant
- LangGraph
- LLM API

只会把问题藏得更深。

所以这轮的技术路线其实很成熟：

- 先把模型无关层做好
- 再逐步接入模型相关能力

---

## 8. 从 AI 系统视角如何理解这次迭代

可以把整个 DevFlow Agent 的能力链路拆成下面几层：

1. Ingestion
   把仓库内容纳入系统
2. Structuring
   把文件变成结构化代码知识
3. Retrieval
   把知识检索出来
4. Planning
   把用户请求转换成变更计划
5. Patch Drafting
   生成修改草案

那么第三次迭代做的，就是第二层 Structuring。

它不是最终用户直接可见的 feature，但它决定了后面：

- 检索是不是精准
- 规划是不是基于正确结构
- patch 草案是不是能定位到合理边界

从系统价值看，这一层非常像：

- 搜索引擎中的索引构建层
- 编译器中的 AST / IR 层
- 数据平台中的语义建模层

---

## 9. 你应该重点理解的几个技术点

如果你是“有大型软件和管理经验，但 AI 背景较少”，我建议重点抓下面 5 个点：

### 9.1 AI 系统并不等于 LLM 调用

这次迭代几乎没用到大模型，但它依然是 AI 系统核心能力的一部分。

因为 AI 系统的效果，往往首先取决于：

- 输入治理
- 结构建模
- 上下文组织

### 9.2 中间表示比 prompt 更重要

如果没有稳定的 file/symbol/relationship 中间表示，后面 prompt 再花哨也很难稳定。

### 9.3 可审查性非常重要

当前实现强调：

- preview
- snapshot
- test
- contract

这些都是在让 AI 系统更可观测、更可审查。

### 9.4 先 heuristic，再 parser，是合理演进路线

系统早期不一定需要一开始就上最重的技术栈。

更好的方式通常是：

1. 先做能工作的最小版本
2. 确认数据模型和边界
3. 再逐步替换底层实现

### 9.5 这轮是后续 RAG/Agent 的前置条件

后续要做的检索、规划、patch 生成，都会依赖这轮产出的结构对象。

所以这轮本质上是后续 AI 能力的“地基层”。

---

## 10. 用一句话总结这次迭代

这次迭代把 DevFlow Agent 从“知道仓库里有哪些文件”推进到了“开始理解代码文件内部有哪些结构、这些结构如何相互关联”，为后续检索、规划和 AI 推理建立了可复用的代码知识表示层。

---

## 11. 如果你要对外讲这次迭代，可以这样说

> 第三次迭代我做的是 DevFlow Agent 的代码结构理解层。  
> 它建立在上一轮的仓库扫描基础上，把 accepted code scan records 转成结构化的文件视图、符号清单和关系元数据。  
> 这轮我优先用 Python AST 做高质量结构提取，同时对非 Python 文件提供启发式兜底，实现了一个可审查、可测试、可扩展的 code intelligence pipeline。  
> 它的核心价值不是直接接大模型，而是先把代码仓库变成 AI 可消费的知识对象，为后续 retrieval、planning 和 patch draft 提供基础。  

