# 01 · 应用框架选型：LangChain / LangGraph · LlamaIndex · Spring AI · PydanticAI · 裸 SDK

> 对应矩阵层:`frameworks`(`python3 -m stack_lab.cli compare frameworks`)。选项 id:`langchain_langgraph` / `pydantic_ai` / `llamaindex` / `spring_ai` / `ts_edge_sdk` / `raw_sdk`。姊妹仓:[spring-ai-lab](https://github.com/jianwen049-hub/spring-ai-lab) · [context-engineering](https://github.com/jianwen049-hub/context-engineering)。

## 当时业务痛点

团队要在**已有 Java 微服务**上挂 RAG + 工具调用:客服知识问答、工单摘要、内部审批助手。产品经理要「两周能演示」,架构师要「别引入无法审计的黑盒」,运维要「能进现有 CI / 配置中心 / 链路追踪」。Python 同学推 LangChain 全家桶;Java 同学问有没有 Spring 生态;前端同学说「我们在 TS,想直接 Vercel AI SDK 流到 React」;还有人甩了一句「直接调 OpenAI SDK 不就完了」。

真实痛点不是「哪个名字更火」,而是:

1. **集成面**:鉴权、配置、日志、线程池、事务边界能不能复用现有基建。
2. **可演进**:从「单次问答」长到「多步 Agent / 图编排」时,要不要整仓重写。
3. **可观测与可控**:prompt、工具调用、检索片段能不能打点、回放、做回归。
4. **团队技能栈**:写业务的人是 Java 还是 Python,决定维护成本。
5. **抽象厚度**:框架给的每一层便利,都是排障时多一层「到底是谁改了我的 prompt」。

### 具体翻车现场(不是段子)

- **升级即崩**:LangChain minor 升级后 `RetrievalQA` 被废弃,CI 里三个 notebook 同时红,回滚花掉一下午。教训:**锁版本 + 留逃生舱**。
- **隐式 prompt**:框架在 system prompt 里塞了「You are a helpful agent」再拼检索片段,线上答非所问;翻了两小时才发现 prompt 是框架拼的。教训:**能显式打印最终 prompt 的框架才可调试**。
- **双栈漂移**:Java 侧和 Python 侧各写一份「查订单」工具描述,字段名 `orderId` vs `order_id`,Agent 调 Java 网关 400。教训:**契约靠 OpenAPI/MCP 单一来源,不靠两端各自抄**。

## 当时怎么看这个问题

我一度把框架理解成「多包一层 LLM 调用」——觉得薄包装就够。现场打脸的是:一旦出现 **检索编排 + 工具循环 + 失败重试 + 会话记忆**,裸 SDK 会迅速长出一套私有「准框架」;而重框架若抽象不对,调试成本比裸调更高。

2025–2026 圈内的新争论是「**厚框架 vs 类型化薄框架**」:LangChain 组件多但抽象厚,PydanticAI 这类用类型系统约束工具输入输出的薄框架被越来越多认真写服务的团队拿来替代。我的判断是:正确问题不是「谁薄谁厚」,而是——**抽象层是否贴合我们的变更频率与排障路径**:

- 变更最勤的层(通常是 prompt 与检索),要能**直接看 diff、直接回放**;
- 变更最少但风险最高的层(鉴权、预算、审计),要**显式到代码里**,不能藏在框架默认行为。

## 试过什么

1. **裸 OpenAI / 厂商 SDK**(`raw_sdk`):demo 最快,三天能出接口;一周后出现手写 retry、手写 tool loop、手写 message trim。
2. **LangChain LCEL 链式拼装**:组件多、文档例子多;复杂分支后 chain 变成难读的管道,图状态难表达。
3. **LangGraph**(`langchain_langgraph`):显式状态机 / 图,适合多步与人机回环;学习曲线与调试工具链要单独投入。
4. **PydanticAI 式类型化薄框架**(`pydantic_ai`):工具签名、结构化输出全是类型约束,代码可读性极好;但检索、记忆、评测这些「电池」要自己装。
5. **LlamaIndex**(`llamaindex`):索引与查询管线强,文档问答上手快;偏「数据进、答案出」,重业务工作流时要外挂编排。
6. **Spring AI**(及同类 Java AI 抽象,`spring_ai`):ChatClient / Advisor / ToolCallback 贴 Spring Boot;适合已有 Java 服务嵌入;生态比 Python 侧新,要自己补一些胶水。
7. **Vercel AI SDK / Mastra**(`ts_edge_sdk`):TS 团队前端直出流式体验最好;长任务 Agent 循环在 serverless 上会被超时切断,checkpoint 得外置。

## 为什么否决

| 选项 | 否决或降级原因 |
|------|----------------|
| **永远裸 SDK** | 否决作为唯一长期形态。短期可行,中期必然长出无法文档化的私有框架。 |
| **LangChain 一把梭所有层** | 否决「用 chain 表达一切」。复杂控制流应上图(LangGraph)或自研状态机,而不是嵌套 Runnable。 |
| **PydanticAI 承担所有层** | 否决「薄框架=全栈」。它解决的是应用层的类型契约;检索策略、评测门禁仍要独立建设。 |
| **LlamaIndex 当通用 Agent 平台** | 降级:它擅长索引与检索编排,不是企业工作流中枢。 |
| **为追新全部迁 Python** | 否决。Java 存量与合规链路不是「换语言」能一笔勾销的;应用层可用 Spring AI,实验层可用 Python。 |
| **Spring AI 替代检索专用栈** | 降级:Spring AI 是应用集成层;向量检索仍要独立设计(见 03)。 |
| **前端同学私接 edge SDK 绕过网关** | 否决。流式 UX 可以在前端,但**工具调用必须走后端网关**,否则鉴权与审计直接失守。 |

## 最终怎么解

分层而不是选教派:

| 层 | 倾向 | 理由 |
|----|------|------|
| 生产业务 API(Java 为主) | **Spring AI + 裸 SDK 兜底** | 配置、Bean、观测、安全过滤器复用;关键路径可直调 SDK |
| 复杂多步 Agent | **LangGraph 或自研图 / 状态机** | 显式节点、边、checkpoint,可测可回放 |
| 类型敏感的 Python 服务 | **PydanticAI 式薄框架** | 工具 I/O 契约进类型,review 时看得见 |
| 文档/知识库索引实验 | **LlamaIndex 或自研检索流水线** | 快速验证 chunk / 索引策略 |
| 流式产品 UI | **Vercel AI SDK / Mastra + 后端网关** | 体验层在前端,权限层绝不下放 |
| 协议与工具 | **MCP + 内部 HTTP Tool**(见 04) | 框架可换,工具契约尽量稳 |
| 对照表 | 本仓 `lab` CLI `compare frameworks` | 把取舍固化成可打印矩阵 |

原则:**框架服务变更频率**——变更在检索就强检索框架;变更在编排就强图;变更在企业集成就强 Spring;变更在产品交互就强 TS 流式层。

### 对比表(摘要)

| 维度 | LangChain / LangGraph | PydanticAI 式 | LlamaIndex | Spring AI | Vercel AI SDK / Mastra | 裸 SDK |
|------|----------------------|----------------|------------|-----------|------------------------|--------|
| 主语言生态 | Python(JS 亦有) | Python | Python | Java / Kotlin | TypeScript | 各语言 |
| 强项 | 组件生态;Graph 控流 | 类型化工具/输出;薄 | 索引 / 查询 / RAG 管线 | Spring 集成、Advisor | 流式 UX、edge 运行时 | 最小依赖、最大控制 |
| 弱项 | 抽象过厚时难排障 | 电池少,自建件多 | Agent/工作流非主场 | 生态较新、样板较少 | 长任务受 serverless 限制 | 易长出私有框架 |
| 适合 | 实验→产品的 Python 服务;复杂图 | 讨厌厚抽象的小团队 | 知识库 / 文档 QA | 已有 Spring 微服务嵌入 AI | React 直出 token 的产品 UI | 边界清晰的单次调用、POC |
| 不适合 | 强约束 Java-only 合规栈硬套 | 想要开箱全家的团队 | 重审批流 / 多系统编排中枢 | 纯研究向 notebook 迭代 | 重检索/重评测后端逻辑 | 多工具循环 + 记忆 + 评测一体 |

跑:`python3 -m stack_lab.cli compare frameworks`

### 换框架的「退出成本」检查表

换框架前问四个问题(矩阵之外、工程之内):

1. **prompt 资产**是否以文件/模板独立存放(不在代码字符串里散落)?
2. **工具契约**是否 OpenAPI / MCP 描述(而不是框架私有装饰器)?
3. **trace 字段**是否已映射到 OTel GenAI 语义约定(见 05,`obs/otel_genai`)?
4. **评测集**能否在新框架上原样跑(见 [ai-eval-lab](https://github.com/jianwen049-hub/ai-eval-lab))?

四个都是 yes,换框架是一周事;两个以上 no,先还技术债再谈「迁移」。

## 用到的具体 skill / 技巧清单

| Skill | 用法 |
|-------|------|
| **按变更频率选抽象** | 哪一层改得最勤,哪一层配最强框架 |
| **双栈策略** | Java 生产 + Python 实验,契约用 OpenAPI / MCP 对齐 |
| **Advisor / 中间件思维** | 日志、限流、RAG 注入、Token 预算做成可插拔链,而不是写死在业务里 |
| **图优于深层 chain** | 分支、重试、人机审批用显式状态 |
| **类型化工具签名** | Pydantic / Bean Validation 把工具参数错误拦在调用前 |
| **最终 prompt 可打印** | 框架必须能 dump 完整上下文,否则不可调试 |
| **保留逃生舱** | 关键路径允许直调 SDK,避免框架版本锁死 |
| **决策矩阵入库** | `matrix.py` 把优缺点写成数据,博客与 CLI 同源 |

## 代码 / 表解析(按文件路径)

### `lab/src/stack_lab/matrix.py`

`LAYERS["frameworks"]["options"]` 存各框架的 `pros` / `cons` / `best_for` / `watchouts`,新增 `pydantic_ai` 与 `ts_edge_sdk` 两行,对应「厚 vs 薄」与「TS edge」两条 2025–2026 的真实争论线。CLI 与博客表格同一数据源,避免文档漂移。

### `lab/src/stack_lab/compare.py`

`format_table(layer_key)` 用纯 stdlib 拼 Markdown 风格宽表,无第三方依赖。

### `lab/src/stack_lab/cli.py`

`compare frameworks` / `recommend "..."`:推荐逻辑是关键词启发(如出现 `java`/`spring` → 提高 Spring AI 分;出现 `pydanticai` → 提高 `pydantic_ai` 分),**不是**模型调用——保证离线可复现。

### `lab/src/stack_lab/recommend.py`

`RULES` 里每条规则是 `(关键词, 层, 选项 id, 权重, 理由)` 元组;`lab/tests/test_matrix.py::test_recommend_rules_reference_real_options` 保证每条规则引用的选项真实存在,防止矩阵改名后推荐静默失效。

### `lab/scripts/smoke_check.py`

断言 frameworks 层至少含 LangChain、LlamaIndex、Spring AI、raw SDK 四类选项,且新加的 `pydantic_ai` / `ts_edge_sdk` 在位,`compare all` 退出码为 0。

---

**一句话**:框架不是信仰,是**对集成面、控流复杂度、团队语言**的显式下注;用决策矩阵写下来,比争论「谁更火」有用。选错了不可怕,可怕的是 prompt、契约、评测都长在框架身上,想换时拔不出来。