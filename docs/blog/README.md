# 技术博客（中文深拆）

写法统一：**当时业务痛点 → 当时怎么看 → 试过什么 → 为什么否决 → 最终怎么解 → skill 清单 → 代码/表解析**。每篇开头标注对应矩阵层与选项 id（如 `obs/otel_genai`），并交叉链接姊妹仓。

| # | 标题 | 覆盖分层 | 代码锚点 |
|---|------|----------|----------|
| [01](./01-app-frameworks.md) | 应用框架选型：LangChain / LangGraph · PydanticAI · LlamaIndex · Spring AI · Vercel AI SDK · 裸 SDK | 框架 | `matrix.py` frameworks |
| [02](./02-agent-orchestration.md) | Agent 编排：单兵、多 Agent、ReAct、Plan-Execute、图工作流、CrewAI/AutoGen、handoff | 编排 | `matrix.py` agents |
| [03](./03-retrieval-stack.md) | 检索栈：稀疏 / 稠密 / 混合，pgvector vs Qdrant vs Chroma，重排、上下文增强与 GraphRAG | 检索 | `matrix.py` retrieval |
| [04](./04-protocols-mcp-tools.md) | 工具协议：OpenAI Tools · MCP · A2A · 自定义 HTTP，谁在什么时候赢 | 协议 | `matrix.py` protocols |
| [05](./05-serving-obs-cost-safety.md) | 服务、观测、成本与安全：LLM 网关、OTel GenAI、评测、prompt/语义缓存、Guardrail | 服务·观测·成本安全 | `matrix.py` serving/obs/cost |

一页速查：[`docs/STACK-CHEATSHEET.md`](../STACK-CHEATSHEET.md)

姊妹仓：[spring-ai-lab](https://github.com/jianwen049-hub/spring-ai-lab) · [hybrid-retrieval](https://github.com/jianwen049-hub/hybrid-retrieval) · [multi-agent-orchestration](https://github.com/jianwen049-hub/multi-agent-orchestration) · [agent-observability](https://github.com/jianwen049-hub/agent-observability) · [llm-cost-latency](https://github.com/jianwen049-hub/llm-cost-latency) · [context-engineering](https://github.com/jianwen049-hub/context-engineering) · [ai-eval-lab](https://github.com/jianwen049-hub/ai-eval-lab) · [mcp-lab](https://github.com/jianwen049-hub/mcp-lab) · [rag-agent-lab](https://github.com/jianwen049-hub/rag-agent-lab)