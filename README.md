# ai-stack-landscape — AI Engineering Stack Map & Trade-offs

> Open lab that **maps today's AI engineering stacks** and **compares them with real trade-offs** — frameworks, agents, retrieval, protocols (incl. MCP), serving, observability, cost/latency/safety. Offline stdlib decision-matrix CLI. No buzzword dump.

**Author:** 马健文 / Evans Owen ([jianwen049-hub](https://github.com/jianwen049-hub))

| | |
|---|---|
| **Lab** | [`lab/`](./lab/) — decision matrix CLI · layers · smoke |
| **Blog** | [`docs/blog/`](./docs/blog/) — long Chinese deep-dives |
| **Bio** | [`PROFILE.md`](./PROFILE.md) |

## 中文速览

做 AI 产品时最贵的往往不是模型费，而是**选错栈之后的返工**：框架锁死、检索一路打天下、工具协议各写一套、上线后不会评不会观测。本仓把当前主流技术栈按分层摊开，用对比表 + 业务现场叙事讲清「什么场景选谁、常见坑在哪」。配套 `stack_lab` CLI 离线打印决策矩阵，方便对照博客。

**覆盖分层（最低限度）：**

1. 应用框架：LangChain / LangGraph · LlamaIndex · Spring AI · 裸 SDK
2. Agent 编排：单 Agent / 多 Agent；ReAct · Plan-Execute · 图工作流
3. 检索：稀疏 / 稠密 / 混合；FAISS · Chroma · pgvector · 托管；重排
4. 协议与工具：OpenAI Tools · MCP · 自定义 HTTP
5. 模型服务：闭源 API · 开源权重；流式；结构化输出
6. 观测与评估：Traces · Golden set · 在线 / 离线评测
7. 成本 / 延迟 / 安全：路由 · 缓存 · Guardrail · PII

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

Related deep-dives on the same profile: [spring-ai-lab](https://github.com/jianwen049-hub/spring-ai-lab) · [hybrid-retrieval](https://github.com/jianwen049-hub/hybrid-retrieval) · [multi-agent-orchestration](https://github.com/jianwen049-hub/multi-agent-orchestration) · [agent-observability](https://github.com/jianwen049-hub/agent-observability) · [llm-cost-latency](https://github.com/jianwen049-hub/llm-cost-latency) · [context-engineering](https://github.com/jianwen049-hub/context-engineering) · [ai-eval-lab](https://github.com/jianwen049-hub/ai-eval-lab)

## License

MIT — see [`LICENSE`](./LICENSE).
