"""Heuristic stack recommendations from a free-text pain description.

Offline keyword scoring — no model calls. Deterministic for smoke tests.
"""
from __future__ import annotations

from dataclasses import dataclass

from stack_lab.matrix import LAYERS


@dataclass
class Scored:
    layer: str
    option_id: str
    label: str
    score: int
    reasons: list[str]


# keyword -> list of (layer, option_id, weight, reason)
RULES: list[tuple[str, str, str, int, str]] = [
    ("java", "frameworks", "spring_ai", 5, "Java/Spring mentioned → Spring AI fits existing services"),
    ("spring", "frameworks", "spring_ai", 5, "Spring ecosystem → Spring AI + Advisors"),
    ("python", "frameworks", "langchain_langgraph", 4, "Python-centric → LangChain/LangGraph"),
    ("langgraph", "frameworks", "langchain_langgraph", 5, "Explicit graph need"),
    ("llamaindex", "frameworks", "llamaindex", 5, "Named LlamaIndex"),
    ("pydanticai", "frameworks", "pydantic_ai", 5, "Named PydanticAI-style typed stack"),
    ("pydantic", "frameworks", "pydantic_ai", 3, "Typed tool contracts lean → thin typed framework"),
    ("vercel", "frameworks", "ts_edge_sdk", 5, "Vercel/TS edge → Vercel AI SDK family"),
    ("mastra", "frameworks", "ts_edge_sdk", 5, "Named Mastra"),
    ("typescript", "frameworks", "ts_edge_sdk", 4, "TS-first team → edge AI SDK"),
    ("知识库", "frameworks", "llamaindex", 3, "Knowledge base → index-strong stack"),
    ("rag", "retrieval", "hybrid", 5, "RAG → hybrid+RRF default"),
    ("检索", "retrieval", "hybrid", 4, "Retrieval → hybrid"),
    ("订单号", "retrieval", "sparse", 4, "Exact IDs need sparse"),
    ("sku", "retrieval", "sparse", 4, "SKU/exact tokens"),
    ("向量", "retrieval", "dense", 2, "Vectors alone are not enough — still prefer hybrid overall"),
    ("pgvector", "retrieval", "store_pgvector", 5, "Named pgvector"),
    ("postgres", "retrieval", "store_pgvector", 4, "Postgres → pgvector candidate"),
    ("faiss", "retrieval", "store_faiss", 5, "Named FAISS"),
    ("qdrant", "retrieval", "store_qdrant", 5, "Named Qdrant"),
    ("托管", "retrieval", "store_managed", 3, "Managed vector DB"),
    ("chroma", "retrieval", "store_chroma", 5, "Named Chroma"),
    ("重排", "retrieval", "reranker", 4, "Rerank mentioned"),
    ("rerank", "retrieval", "reranker", 4, "Rerank mentioned"),
    ("图谱", "retrieval", "graph_rag", 4, "Relationship questions → GraphRAG leg"),
    ("graph rag", "retrieval", "graph_rag", 4, "Named GraphRAG"),
    ("多跳", "retrieval", "graph_rag", 4, "Multi-hop questions → graph-augmented retrieval"),
    ("切块", "retrieval", "contextual_chunks", 3, "Chunking pain → contextual retrieval"),
    ("审批", "agents", "graph", 5, "Approval gates → graph workflow"),
    ("退款", "agents", "graph", 4, "Side-effect write → graph + idempotency"),
    ("写库", "agents", "graph", 5, "DB writes → explicit graph"),
    ("多agent", "agents", "multi_agent", 4, "Multi-agent named"),
    ("多 agent", "agents", "multi_agent", 4, "Multi-agent named"),
    ("调研", "agents", "multi_agent", 3, "Research/write/critique pattern"),
    ("质检", "agents", "multi_agent", 3, "Critique role pattern"),
    ("react", "agents", "react", 3, "ReAct named — keep for read-only"),
    ("crewai", "agents", "crewai_autogen", 5, "Named CrewAI-style role framework"),
    ("autogen", "agents", "crewai_autogen", 5, "Named AutoGen-style framework"),
    ("agents sdk", "agents", "openai_agents_sdk", 5, "Hosted agent SDK + handoffs named"),
    ("handoff", "agents", "openai_agents_sdk", 4, "Handoff pattern → keep budgets on edges"),
    ("mcp", "protocols", "mcp", 5, "MCP named"),
    ("ide", "protocols", "mcp", 4, "IDE/host reuse → MCP"),
    ("cursor", "protocols", "mcp", 4, "IDE host → MCP"),
    ("跨应用", "protocols", "mcp", 4, "Cross-app tools → MCP"),
    ("a2a", "protocols", "a2a", 4, "Agent-to-agent delegation → A2A-style, gate it hard"),
    ("网关", "protocols", "http_gateway", 5, "Gateway → HTTP/OpenAPI truth"),
    ("openapi", "protocols", "http_gateway", 4, "OpenAPI gateway"),
    ("function call", "protocols", "openai_tools", 3, "Function calling in-session"),
    ("tools", "protocols", "openai_tools", 2, "Generic tools — still gateway underneath"),
    ("流式", "serving", "streaming_structured", 4, "Streaming UX"),
    ("streaming", "serving", "streaming_structured", 4, "Streaming UX"),
    ("json", "serving", "streaming_structured", 3, "Structured outputs"),
    ("私有化", "serving", "open_weights", 5, "On-prem / privacy → open weights"),
    ("开源", "serving", "open_weights", 3, "Open weights interest"),
    ("闭源", "serving", "closed_api", 3, "Closed API interest"),
    ("litellm", "serving", "llm_gateway", 5, "Named LiteLLM-style gateway"),
    ("openrouter", "serving", "llm_gateway", 4, "OpenRouter → unified gateway"),
    ("多供应商", "serving", "llm_gateway", 4, "Multi-provider → gateway with failover"),
    ("batch", "serving", "batch_api", 4, "Batch/backfill → offline batch API"),
    ("回填", "serving", "batch_api", 4, "Backfill workload → batch API"),
    ("路由", "serving", "routing_mix", 4, "Model routing"),
    ("账单", "cost", "routing", 4, "Bill pain → tiered routing"),
    ("成本", "cost", "routing", 4, "Cost → routing/cache"),
    ("延迟", "cost", "prompt_cache", 4, "Latency → prompt cache + routing"),
    ("缓存", "cost", "prompt_cache", 4, "Caching → prompt cache is the safe first lever"),
    ("prompt cache", "cost", "prompt_cache", 5, "Prompt caching named"),
    ("语义缓存", "cost", "semantic_cache", 5, "Semantic cache named — TTL + hit QA required"),
    ("semantic cache", "cost", "semantic_cache", 5, "Semantic cache named — TTL + hit QA required"),
    ("pii", "cost", "pii", 5, "PII"),
    ("脱敏", "cost", "pii", 5, "Redaction / PII"),
    ("合规", "cost", "guardrails", 4, "Compliance → guardrails + ACL"),
    ("安全", "cost", "guardrails", 3, "Safety → guardrails"),
    ("护栏", "cost", "guardrails", 5, "Guardrails named"),
    ("guardrail", "cost", "guardrails", 5, "Guardrails named"),
    ("trace", "obs", "traces", 5, "Tracing"),
    ("观测", "obs", "traces", 4, "Observability"),
    ("otel", "obs", "otel_genai", 5, "OpenTelemetry → GenAI semconv spans"),
    ("opentelemetry", "obs", "otel_genai", 5, "OpenTelemetry → GenAI semconv spans"),
    ("黄金", "obs", "golden_offline", 5, "Golden set"),
    ("评测", "obs", "golden_offline", 4, "Eval"),
    ("回归", "obs", "golden_offline", 4, "Regression gate"),
    ("judge", "obs", "llm_judge", 4, "LLM-as-judge named"),
    ("裁判", "obs", "llm_judge", 4, "Judge-style scoring"),
    ("enterprise", "frameworks", "spring_ai", 3, "Enterprise Java lean"),
    ("enterprise", "protocols", "http_gateway", 3, "Enterprise → gateway"),
]


def recommend(pain: str, top_k: int = 8) -> list[Scored]:
    text = (pain or "").lower()
    scores: dict[tuple[str, str], Scored] = {}
    for kw, layer, opt_id, weight, reason in RULES:
        if kw.lower() in text or kw in pain:
            key = (layer, opt_id)
            opt = next(o for o in LAYERS[layer]["options"] if o["id"] == opt_id)
            if key not in scores:
                scores[key] = Scored(layer, opt_id, opt["label"], 0, [])
            scores[key].score += weight
            if reason not in scores[key].reasons:
                scores[key].reasons.append(reason)
    # mild priors if nothing matched
    if not scores:
        for layer, opt_id, weight, reason in [
            ("retrieval", "hybrid", 2, "Default prior: hybrid retrieval"),
            ("agents", "graph", 1, "Default prior: prefer explicit graph when unsure"),
            ("protocols", "http_gateway", 2, "Default prior: business API gateway"),
            ("obs", "traces", 2, "Default prior: instrument traces"),
            ("cost", "routing", 1, "Default prior: tiered routing"),
        ]:
            opt = next(o for o in LAYERS[layer]["options"] if o["id"] == opt_id)
            scores[(layer, opt_id)] = Scored(layer, opt_id, opt["label"], weight, [reason])
    ranked = sorted(scores.values(), key=lambda s: (-s.score, s.layer, s.option_id))
    return ranked[:top_k]


def format_recommend(pain: str) -> str:
    ranked = recommend(pain)
    lines = [
        f"# Recommendation for pain: {pain!r}",
        "# Heuristic keyword scoring (offline, deterministic)",
        "",
        f"{'Score':>5} | {'Layer':<12} | {'Option':<36} | Why",
        f"{'-'*5}-+-{'-'*12}-+-{'-'*36}-+-{'-'*40}",
    ]
    for s in ranked:
        why = "; ".join(s.reasons)
        if len(why) > 60:
            why = why[:57] + "..."
        lines.append(f"{s.score:>5} | {s.layer:<12} | {s.label:<36} | {why}")
    lines.append("")
    lines.append("Next: `compare <layer>` for full pros/cons; read docs/blog/ for deep dives.")
    lines.append("")
    return "\n".join(lines)
