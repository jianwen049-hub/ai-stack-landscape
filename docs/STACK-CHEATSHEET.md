# AI Engineering Stack Cheatsheet（一页速查）

> 与 `lab/src/stack_lab/matrix.py` 同步维护：本页的层名、选项名、选项 id 与矩阵一一对应（改名请同时改这里和矩阵）。打印用：A4 单页。离线对照:`cd lab && export PYTHONPATH=src && python3 -m stack_lab.cli compare all`。

## 1 · 应用框架 `frameworks`

| 选项 (id) | 一句话 | 别忘 |
|---|---|---|
| LangChain / LangGraph (`langchain_langgraph`) | 组件最多;复杂控流上图,别嵌套 chain | 锁版本,留 raw SDK 逃生舱 |
| PydanticAI 式薄框架 (`pydantic_ai`) | 类型化工具/输出,薄而可读 | 电池少:评测/检索自建 |
| LlamaIndex (`llamaindex`) | 索引与查询管线强 | 副作用工作流要外挂编排 |
| Spring AI (`spring_ai`) | Java 微服务内嵌 AI 首选 | 检索设计独立(见 §3) |
| Vercel AI SDK / Mastra (`ts_edge_sdk`) | TS 流式直出前端 | serverless 超时;工具仍走网关 |
| 裸 SDK (`raw_sdk`) | POC/单次调用 | 早早抽出公共 client/retry |

**默认**:按团队语言与变更频率选;prompt 资产、工具契约、trace 映射、评测集四件不绑死框架。

## 2 · Agent 编排 `agents`

| 选项 (id) | 一句话 | 别忘 |
|---|---|---|
| 单 Agent ReAct (`react`) | 只读问答 | 步数/费用硬顶 |
| Plan-and-Execute (`plan_execute`) | 步骤可见 | 计划可失效重规划 |
| 图工作流 (`graph`) | 副作用/审批/回放默认态 | 终止写边不写散文 |
| 多 Agent (`multi_agent`) | 真实角色冲突才上 | 黑板>塞 prompt |
| CrewAI / AutoGen (`crewai_autogen`) | 角色对话,十分钟 demo | 不碰钱;预算外置 |
| handoff SDK (`openai_agents_sdk`) | 轻循环+移交 | trace 导自家 OTel |

**默认**:复杂度梯子——单次→单工具→有限步 ReAct→图→多 Agent。写工具必带幂等键。

## 3 · 检索 `retrieval`

| 选项 (id) | 一句话 | 别忘 |
|---|---|---|
| BM25 (`sparse`) | ID/型号/条款号 | 向量来了也别退 |
| 稠密 (`dense`) | 语义改写 | 大模型救不了坏切块 |
| 混合+RRF+重排 (`hybrid` + `reranker`) | **生产默认** | RRF 不裸加分;重排只吃小候选 |
| 上下文增强切块 (`contextual_chunks`) | 修代词歧义 | 索引期成本,离线批处理 |
| GraphRAG (`graph_rag`) | 多跳/聚合题 | 补充腿,非替代 |
| FAISS (`store_faiss`) / Chroma (`store_chroma`) | 实验/原型 | 上生产前重估 |
| pgvector (`store_pgvector`) | 有 Postgres+强过滤 | HNSW 过滤塌方要压测 |
| Qdrant (`store_qdrant`) | 过滤+ANN 一等公民 | 业务真相留 SQL |
| 托管 (`store_managed`) | 小团队快上 | ACL/混合仍自己设计 |

**默认**:先元数据过滤再 ANN;黄金集分意图(ID/语义/多跳)切片评测。

## 4 · 协议与工具 `protocols`

| 选项 (id) | 一句话 | 别忘 |
|---|---|---|
| OpenAI Tools (`openai_tools`) | 单产品内低仪式 | 写操作仍走网关 |
| MCP (`mcp`) | 跨宿主复用(IDE+Agent+桌面) | 协议≠授权;第三方 Server 先审后装 |
| A2A (`a2a`) | 跨组织 Agent 委托 | 按任务短期凭据+全量审计 |
| HTTP/OpenAPI 网关 (`http_gateway`) | **写操作与核心读的真相层** | schema 单一来源生成 |

**默认**:能力下沉稳定 API;多协议适配层。幂等键是一切写工具第一参数。

## 5 · 模型服务 `serving`

| 选项 (id) | 一句话 | 别忘 |
|---|---|---|
| 闭源 API (`closed_api`) | 默认智能 | failover/降级预案 |
| 开源自宿 (`open_weights`) | 敏感数据/高 QPS | serving 栈按生产服务加固 |
| LLM 网关 (`llm_gateway`) | 多供应商收口 | 网关自己要 HA+旁路 |
| batch API (`batch_api`) | 回填/夜间评测便宜 | schema 与 chat 有微妙差异 |
| 混合路由 (`routing_mix`) | 简单→小,难→大 | 路由按模型评测 |
| 流式+结构化 (`streaming_structured`) | UX+机器契约 | 缓冲到合法工具帧;服务端校验 |

## 6 · 观测与评估 `obs`

| 选项 (id) | 一句话 | 别忘 |
|---|---|---|
| Traces (`traces`) | 多步 Agent 必打 | prompt 捕获先定合规策略 |
| OTel GenAI 约定 (`otel_genai`) | 厂商中立 span,后端可换 | 与业务 trace 同链 |
| 黄金集 (`golden_offline`) | CI 门禁,不过不发版 | 分意图维护 |
| LLM-as-judge (`llm_judge`) | 规模化评分 | 先 100 条人工校准;不单独门禁 |
| 在线评估 (`online_eval`) | 抓漂移 | 补充而非替代离线 |

## 7 · 成本·延迟·安全 `cost`

| 选项 (id) | 一句话 | 别忘 |
|---|---|---|
| 分级路由 (`routing`) | 简单题走小模型 | 路由当模型评 |
| prompt cache (`prompt_cache`) | 稳赚第一杠杆 | 可缓存前缀放头;命中率一等指标 |
| 语义缓存 (`semantic_cache`) | 近似命中省钱 | TTL+命中 QA+账号/支付旁路 |
| Guardrails+ACL (`guardrails`) | 超越 prompt 的强制 | guardrail 自身精度/召回也要评 |
| PII 分层 (`pii`) | 入模前/出模后/日志分级 | 过度脱敏会毁任务 |

**缓存口诀**:prompt cache 零正确性风险先上;semantic cache 是「近错答案贩卖机」,三件套缺一不上。

## decide 七问(离线检查表)

1. 哪层变更最勤?框架、检索、编排的最强抽象跟着它走。
2. 有副作用吗?有 → 图 + 网关 + 幂等,不是无界 ReAct。
3. 查询里有精确 ID?保留稀疏;默认混合+RRF。
4. 多宿主(IDE+服务)?MCP 叠在 HTTP 网关上。
5. 一个请求能端到端 trace?不能 → 先别扩 Agent。
6. 黄金集进 CI 了吗?没有 → 改 prompt 是赌博。
7. 预算硬顶(步数/token/¥)?没有 → 等着账单上头条。

---

深挖见 [docs/blog/](./blog/);速查来源 `python3 -m stack_lab.cli decide`。姊妹仓:[spring-ai-lab](https://github.com/jianwen049-hub/spring-ai-lab) · [hybrid-retrieval](https://github.com/jianwen049-hub/hybrid-retrieval) · [multi-agent-orchestration](https://github.com/jianwen049-hub/multi-agent-orchestration) · [agent-observability](https://github.com/jianwen049-hub/agent-observability) · [llm-cost-latency](https://github.com/jianwen049-hub/llm-cost-latency) · [context-engineering](https://github.com/jianwen049-hub/context-engineering) · [ai-eval-lab](https://github.com/jianwen049-hub/ai-eval-lab) · [mcp-lab](https://github.com/jianwen049-hub/mcp-lab) · [rag-agent-lab](https://github.com/jianwen049-hub/rag-agent-lab)