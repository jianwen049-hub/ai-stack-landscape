# ai-stack-landscape — AI Engineering Stack Map & Trade-offs

> Open lab that **maps today's AI engineering stacks** and **compares them with real trade-offs** — frameworks, agents, retrieval, protocols (incl. MCP), serving, observability, cost/latency/safety. Offline stdlib decision-matrix CLI. No buzzword dump.

**Author:** 马健文 / Evans Owen ([jianwen049-hub](https://github.com/jianwen049-hub))

| | |
|---|---|
| **Lab** | [`lab/`](./lab/) — decision matrix CLI · layers · smoke |
| **Blog** | [`docs/blog/`](./docs/blog/) — long Chinese deep-dives |
| **Cheatsheet** | [`docs/STACK-CHEATSHEET.md`](./docs/STACK-CHEATSHEET.md) — one-page printable |
| **Bio** | [`PROFILE.md`](./PROFILE.md) |

## Stack at a glance

每层的**默认选法**、**什么时候偏离**、深挖入口。矩阵键可被 `python3 -m stack_lab.cli compare <layer>` 直接打印;完整优缺点见 CLI 输出与对应博客。

| Layer (matrix key) | 默认选法 | 什么时候偏离 | 深挖入口 |
|--------------------|----------|----------------|----------|
| 应用框架 `frameworks` | 按团队语言：Python → LangGraph（复杂流）/ PydanticAI（薄服务）；Java → Spring AI + raw SDK 兜底 | TS-first 产品 UI 且流式直出前端 → Vercel AI SDK / Mastra，但工具调用仍走后端网关 | [blog 01](./docs/blog/01-app-frameworks.md) · [spring-ai-lab](https://github.com/jianwen049-hub/spring-ai-lab) |
| Agent 编排 `agents` | 只读问答 → 有限步 ReAct；有副作用/审批 → 显式图 `graph` | 角色职责真实冲突、需并行/分权限才上 `multi_agent`；无副作用创作管线可用 CrewAI/AutoGen `crewai_autogen`；单厂商快速结构化可用 handoff SDK `openai_agents_sdk` | [blog 02](./docs/blog/02-agent-orchestration.md) · [multi-agent-orchestration](https://github.com/jianwen049-hub/multi-agent-orchestration) |
| 检索 `retrieval` | 混合 BM25+向量 + RRF + 小候选重排 `hybrid`；过滤多、有 Postgres → pgvector；过滤重负载 → Qdrant | 切块代词密集 → 上下文增强 `contextual_chunks`；多跳/聚合题 → GraphRAG 腿 `graph_rag`；原型期 → Chroma | [blog 03](./docs/blog/03-retrieval-stack.md) · [hybrid-retrieval](https://github.com/jianwen049-hub/hybrid-retrieval) |
| 协议与工具 `protocols` | 一切写操作/核心读走 OpenAPI 网关 `http_gateway`；跨宿主复用（IDE+Agent）加 MCP | 跨组织 Agent 委托才考虑 A2A `a2a`；单产品内快速迭代可只用 OpenAI Tools `openai_tools` | [blog 04](./docs/blog/04-protocols-mcp-tools.md) · [mcp-lab](https://github.com/jianwen049-hub/mcp-lab) |
| 模型服务 `serving` | 多供应商 → 统一 LLM 网关 `llm_gateway` + 混合路由 `routing_mix` | 数据出境受限/稳定高 QPS → 自宿开源权重 `open_weights`；回填与夜间评测 → batch API `batch_api` | [blog 05](./docs/blog/05-serving-obs-cost-safety.md) · [llm-cost-latency](https://github.com/jianwen049-hub/llm-cost-latency) |
| 观测与评估 `obs` | Trace 全链 + OTel GenAI 语义约定 `otel_genai` + 黄金集 CI 门禁 `golden_offline` | 长答案/RAG 忠实度规模化评分 → LLM-as-judge `llm_judge`（先校准，不单独门禁）；漂移监控 → 在线抽样 `online_eval` | [blog 05](./docs/blog/05-serving-obs-cost-safety.md) · [agent-observability](https://github.com/jianwen049-hub/agent-observability) · [ai-eval-lab](https://github.com/jianwen049-hub/ai-eval-lab) |
| 成本·延迟·安全 `cost` | 分级路由 `routing` + prompt cache `prompt_cache` + guardrails/工具 ACL `guardrails` | 高频低风险 FAQ 且容忍近错 → 语义缓存 `semantic_cache`（TTL+QA+旁路）；工单/CRM文本 → PII 分层 `pii` | [blog 05](./docs/blog/05-serving-obs-cost-safety.md) · [llm-cost-latency](https://github.com/jianwen049-hub/llm-cost-latency) |

## 中文速览

做 AI 产品时最贵的往往不是模型费，而是**选错栈之后的返工**：框架锁死、检索一路打天下、工具协议各写一套、上线后不会评不会观测。本仓把当前主流技术栈按分层摊开，用对比表 + 业务现场叙事讲清「什么场景选谁、常见坑在哪」。配套 `stack_lab` CLI 离线打印决策矩阵，方便对照博客。

**覆盖分层（每层含 2025–2026 真实争论点）：**

1. 应用框架：LangChain / LangGraph · PydanticAI · LlamaIndex · Spring AI · Vercel AI SDK / Mastra · 裸 SDK
2. Agent 编排：ReAct · Plan-Execute · 图工作流 · 多 Agent · CrewAI/AutoGen · handoff SDK
3. 检索：稀疏 / 稠密 / 混合+RRF · 上下文增强切块 · GraphRAG · FAISS / Chroma / pgvector / Qdrant / 托管 · 重排
4. 协议与工具：OpenAI Tools · MCP · A2A · 自定义 HTTP 网关
5. 模型服务：闭源 API · 开源权重 · LLM 网关 · batch API · 混合路由 · 流式+结构化
6. 观测与评估：Traces · OTel GenAI 语义约定 · 黄金集 · LLM-as-judge · 在线评估
7. 成本 / 延迟 / 安全：分级路由 · prompt cache / 语义缓存 · Guardrails+ACL · PII

## Reading guide (EN)

```bash
cd lab
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # empty / stdlib only
export PYTHONPATH=src
python3 scripts/smoke_check.py
python3 -m stack_lab.cli layers
python3 -m stack_lab.cli compare frameworks
python3 -m stack_lab.cli recommend "java spring enterprise rag"
python3 -m unittest discover -s tests -v
```

### CLI cheat sheet

| Command | What it prints |
|---------|----------------|
| `layers` | Seven engineering layers + one-line purpose |
| `compare <layer>` | Trade-off table for one layer |
| `compare all` | All layer tables |
| `recommend "<pain>"` | Heuristic picks from keywords in the pain string |
| `decide` | Interactive-ish checklist (stdin defaults offline) |

## Sibling labs

Related deep-dives on the same profile: [spring-ai-lab](https://github.com/jianwen049-hub/spring-ai-lab) · [hybrid-retrieval](https://github.com/jianwen049-hub/hybrid-retrieval) · [multi-agent-orchestration](https://github.com/jianwen049-hub/multi-agent-orchestration) · [agent-observability](https://github.com/jianwen049-hub/agent-observability) · [llm-cost-latency](https://github.com/jianwen049-hub/llm-cost-latency) · [context-engineering](https://github.com/jianwen049-hub/context-engineering) · [ai-eval-lab](https://github.com/jianwen049-hub/ai-eval-lab) · [mcp-lab](https://github.com/jianwen049-hub/mcp-lab) · [rag-agent-lab](https://github.com/jianwen049-hub/rag-agent-lab)

## License

MIT — see [`LICENSE`](./LICENSE).