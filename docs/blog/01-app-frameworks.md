# 01 · 应用框架选型：LangChain / LangGraph · LlamaIndex · Spring AI · 裸 SDK

## 当时业务痛点

团队要在**已有 Java 微服务**上挂 RAG + 工具调用：客服知识问答、工单摘要、内部审批助手。产品经理要「两周能演示」，架构师要「别引入无法审计的黑盒」，运维要「能进现有 CI / 配置中心 / 链路追踪」。Python 同学推 LangChain 全家桶；Java 同学问有没有 Spring 生态；还有人说「直接调 OpenAI SDK 不就完了」。

真实痛点不是「哪个名字更火」，而是：

1. **集成面**：鉴权、配置、日志、线程池、事务边界能不能复用现有基建。
2. **可演进**：从「单次问答」长到「多步 Agent / 图编排」时，要不要整仓重写。
3. **可观测与可控**：prompt、工具调用、检索片段能不能打点、回放、做回归。
4. **团队技能栈**：写业务的人是 Java 还是 Python，决定维护成本。

## 当时怎么看这个问题

我一度把框架理解成「多包一层 LLM 调用」——觉得薄包装就够。现场打脸的是：一旦出现 **检索编排 + 工具循环 + 失败重试 + 会话记忆**，裸 SDK 会迅速长出一套私有「准框架」；而重框架若抽象不对，调试成本比裸调更高。正确问题是：**抽象层是否贴合我们的变更频率与排障路径**。

## 试过什么

1. **裸 OpenAI / 厂商 SDK**：demo 最快，三天能出接口；一周后出现手写 retry、手写 tool loop、手写 message trim。
2. **LangChain LCEL 链式拼装**：组件多、文档例子多；复杂分支后 chain 变成难读的管道，图状态难表达。
3. **LangGraph**：显式状态机 / 图，适合多步与人机回环；学习曲线与调试工具链要单独投入。
4. **LlamaIndex**：索引与查询管线强，文档问答上手快；偏「数据进、答案出」，重业务工作流时要外挂编排。
5. **Spring AI（及同类 Java AI 抽象）**：ChatClient / Advisor / ToolCallback 贴 Spring Boot；适合已有 Java 服务嵌入；生态比 Python 侧新，要自己补一些胶水。

## 为什么否决

| 选项 | 否决或降级原因 |
|------|----------------|
| **永远裸 SDK** | 否决作为唯一长期形态。短期可行，中期必然长出无法文档化的私有框架。 |
| **LangChain 一把梭所有层** | 否决「用 chain 表达一切」。复杂控制流应上图（LangGraph）或自研状态机，而不是嵌套 Runnable。 |
| **LlamaIndex 当通用 Agent 平台** | 降级：它擅长索引与检索编排，不是企业工作流中枢。 |
| **为追新全部迁 Python** | 否决。Java 存量与合规链路不是「换语言」能一笔勾销的；应用层可用 Spring AI，实验层可用 Python。 |
| **Spring AI 替代检索专用栈** | 降级：Spring AI 是应用集成层；向量检索仍要独立设计（见 03）。 |

## 最终怎么解

分层而不是选教派：

| 层 | 倾向 | 理由 |
|----|------|------|
| 生产业务 API（Java 为主） | **Spring AI + 裸 SDK 兜底** | 配置、Bean、观测、安全过滤器复用；关键路径可直调 SDK |
| 复杂多步 Agent | **LangGraph 或自研图 / 状态机** | 显式节点、边、checkpoint，可测可回放 |
| 文档/知识库索引实验 | **LlamaIndex 或自研检索流水线** | 快速验证 chunk / 索引策略 |
| 协议与工具 | **MCP + 内部 HTTP Tool**（见 04） | 框架可换，工具契约尽量稳 |
| 对照表 | 本仓 `lab` CLI `compare frameworks` | 把取舍固化成可打印矩阵 |

原则：**框架服务变更频率**——变更在检索就强检索框架；变更在编排就强图；变更在企业集成就强 Spring。

### 对比表（摘要）

| 维度 | LangChain / LangGraph | LlamaIndex | Spring AI | 裸 SDK |
|------|----------------------|------------|-----------|--------|
| 主语言生态 | Python（JS 亦有） | Python | Java / Kotlin | 各语言 |
| 强项 | 组件生态；Graph 控流 | 索引 / 查询 / RAG 管线 | Spring 集成、Advisor | 最小依赖、最大控制 |
| 弱项 | 抽象过厚时难排障 | Agent/工作流非主场 | 生态较新、样板较少 | 易长出私有框架 |
| 适合 | 实验→产品的 Python 服务；复杂图 | 知识库 / 文档 QA | 已有 Spring 微服务嵌入 AI | 边界清晰的单次调用、POC |
| 不适合 | 强约束 Java-only 合规栈硬套 | 重审批流 / 多系统编排中枢 | 纯研究向 notebook 迭代 | 多工具循环 + 记忆 + 评测一体 |

跑：`python3 -m stack_lab.cli compare frameworks`

## 用到的具体 skill / 技巧清单

| Skill | 用法 |
|-------|------|
| **按变更频率选抽象** | 哪一层改得最勤，哪一层配最强框架 |
| **双栈策略** | Java 生产 + Python 实验，契约用 OpenAPI / MCP 对齐 |
| **Advisor / 中间件思维** | 日志、限流、RAG 注入、Token 预算做成可插拔链，而不是写死在业务里 |
| **图优于深层 chain** | 分支、重试、人机审批用显式状态 |
| **保留逃生舱** | 关键路径允许直调 SDK，避免框架版本锁死 |
| **决策矩阵入库** | `matrix.py` 把优缺点写成数据，博客与 CLI 同源 |

## 代码 / 表解析（按文件路径）

### `lab/src/stack_lab/matrix.py`

`LAYERS["frameworks"]["options"]` 存各框架的 `pros` / `cons` / `best_for` / `watchouts`。CLI 与博客表格同一数据源，避免文档漂移。

### `lab/src/stack_lab/compare.py`

`format_table(layer_key)` 用纯 stdlib 拼 Markdown 风格宽表，无第三方依赖。

### `lab/src/stack_lab/cli.py`

`compare frameworks` / `recommend "..."`：推荐逻辑是关键词启发（如出现 `java`/`spring` → 提高 Spring AI 分），**不是**模型调用——保证离线可复现。

### `lab/scripts/smoke_check.py`

断言 frameworks 层至少含 LangChain、LlamaIndex、Spring AI、raw SDK 四类选项，且 `compare all` 退出码为 0。

---

**一句话**：框架不是信仰，是**对集成面、控流复杂度、团队语言**的显式下注；用决策矩阵写下来，比争论「谁更火」有用。
