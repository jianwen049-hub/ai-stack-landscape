"""Decision-matrix data for AI engineering stacks.

Each layer has options with: label, pros, cons, best_for, watchouts.
Blog posts and CLI share this module as the single source of truth.
"""
from __future__ import annotations

from typing import Any

LAYERS: dict[str, dict[str, Any]] = {
    "frameworks": {
        "title": "Application frameworks",
        "title_zh": "应用框架",
        "purpose": "Integrate LLM calls, tools, and RAG into an application runtime.",
        "options": [
            {
                "id": "langchain_langgraph",
                "label": "LangChain / LangGraph",
                "pros": ["Huge component ecosystem", "LangGraph explicit control flow", "Fast Python iteration"],
                "cons": ["Thick abstractions hard to debug", "Version churn", "Java shops pay dual-stack cost"],
                "best_for": ["Python services", "Complex graphs / human-in-the-loop"],
                "watchouts": ["Do not express every branch as nested chains", "Pin versions; keep escape hatches to raw SDK"],
            },
            {
                "id": "llamaindex",
                "label": "LlamaIndex",
                "pros": ["Strong indexing & query pipelines", "Great for doc QA experiments"],
                "cons": ["Not a full enterprise workflow hub", "Agent features secondary"],
                "best_for": ["Knowledge base / RAG prototyping", "Index strategy experiments"],
                "watchouts": ["Pair with a real orchestrator for side-effect workflows"],
            },
            {
                "id": "spring_ai",
                "label": "Spring AI",
                "pros": ["Native Spring Boot integration", "Advisors/tools fit enterprise Java", "Config/observability reuse"],
                "cons": ["Younger ecosystem than Python", "Fewer copy-paste samples"],
                "best_for": ["Existing Java microservices embedding AI", "Compliance-friendly JVM stacks"],
                "watchouts": ["Keep retrieval design separate", "Reserve raw SDK path for critical calls"],
            },
            {
                "id": "raw_sdk",
                "label": "Raw vendor SDKs",
                "pros": ["Minimal deps", "Max control", "Best for tiny surfaces"],
                "cons": ["Homegrown mini-framework debt", "Easy to skip eval/telemetry"],
                "best_for": ["POC", "Single-shot completions with clear boundaries"],
                "watchouts": ["Extract shared client/retry/tool-loop early or migrate to a thin framework"],
            },
        ],
    },
    "agents": {
        "title": "Agent orchestration",
        "title_zh": "Agent 编排",
        "purpose": "Choose control strategies for multi-step LLM + tool workflows.",
        "options": [
            {
                "id": "react",
                "label": "Single-agent ReAct",
                "pros": ["Simple loop", "Flexible", "Good for read-only tasks"],
                "cons": ["Loop risk", "Hard hard-gates", "Opaque control"],
                "best_for": ["Low-risk Q&A / retrieval assistants"],
                "watchouts": ["Hard cap steps & spend", "No unbounded write tools"],
            },
            {
                "id": "plan_execute",
                "label": "Plan-and-Execute",
                "pros": ["Steps visible to humans", "Batch analysis friendly"],
                "cons": ["Stale plans", "Planning token cost"],
                "best_for": ["Stable multi-step analytics"],
                "watchouts": ["Invalidate & replan when tool results change the world"],
            },
            {
                "id": "graph",
                "label": "Graph / state-machine workflow",
                "pros": ["Explicit state", "Testable edges", "Checkpoints"],
                "cons": ["Upfront design cost"],
                "best_for": ["Side effects, approvals, replay"],
                "watchouts": ["Put termination on edges, not in prose prompts"],
            },
            {
                "id": "multi_agent",
                "label": "Multi-agent",
                "pros": ["Role isolation", "Parallel specialties"],
                "cons": ["Bus/termination/cost complexity"],
                "best_for": ["Real division e.g. research + write + critique"],
                "watchouts": ["Climb the complexity ladder first; shared blackboard > prompt stuffing"],
            },
        ],
    },
    "retrieval": {
        "title": "Retrieval stack",
        "title_zh": "检索",
        "purpose": "Recall, fuse, and rerank evidence before generation.",
        "options": [
            {
                "id": "sparse",
                "label": "Sparse / BM25",
                "pros": ["Exact IDs & rare tokens", "Interpretable"],
                "cons": ["Weak on paraphrase"],
                "best_for": ["Order IDs, SKUs, statute numbers"],
                "watchouts": ["Do not retire sparse after vectors land"],
            },
            {
                "id": "dense",
                "label": "Dense embeddings",
                "pros": ["Semantic recall", "Multilingual potential"],
                "cons": ["Weak exact match", "Corpus/model mismatch"],
                "best_for": ["Natural-language intents"],
                "watchouts": ["Bigger embedding ≠ fix bad chunking"],
            },
            {
                "id": "hybrid",
                "label": "Hybrid + RRF (+ rerank)",
                "pros": ["Complementary recall", "Production default"],
                "cons": ["Pipeline complexity", "Rerank latency/cost"],
                "best_for": ["Most production RAG"],
                "watchouts": ["Prefer RRF over raw score add; filter ACL before ANN"],
            },
            {
                "id": "store_faiss",
                "label": "FAISS (local)",
                "pros": ["Fast", "Controllable experiments"],
                "cons": ["You own durability/HA"],
                "best_for": ["Offline / single-node indexing"],
                "watchouts": ["Plan persistence & rebuild"],
            },
            {
                "id": "store_chroma",
                "label": "Chroma-like embedded stores",
                "pros": ["Quick start"],
                "cons": ["Prod governance DIY"],
                "best_for": ["Proto / small teams"],
                "watchouts": ["Revisit before regulated prod"],
            },
            {
                "id": "store_pgvector",
                "label": "pgvector",
                "pros": ["SQL filters + biz DB unity"],
                "cons": ["Huge-scale ANN tradeoffs"],
                "best_for": ["Mid scale with strong metadata filters"],
                "watchouts": ["Index & vacuum ops matter"],
            },
            {
                "id": "store_managed",
                "label": "Managed vector DB",
                "pros": ["Less ops", "Often hybrid features"],
                "cons": ["Cost, lock-in, residency"],
                "best_for": ["Small team shipping prod fast"],
                "watchouts": ["Design ACL & hybrid even if vendor hosts bytes"],
            },
            {
                "id": "reranker",
                "label": "Cross-encoder reranker",
                "pros": ["Precision lift on small candidate sets"],
                "cons": ["Latency & $"],
                "best_for": ["Quality-sensitive answers after hybrid recall"],
                "watchouts": ["Never rerank the whole corpus"],
            },
        ],
    },
    "protocols": {
        "title": "Protocols & tools",
        "title_zh": "协议与工具",
        "purpose": "How agents discover and invoke capabilities safely.",
        "options": [
            {
                "id": "openai_tools",
                "label": "OpenAI-compatible Tools / function calling",
                "pros": ["Native to chat APIs", "Mature examples", "Low ceremony in-session"],
                "cons": ["Weak cross-host discovery", "Easy to duplicate per project"],
                "best_for": ["Single-product agents iterating fast"],
                "watchouts": ["Still put writes behind a gateway"],
            },
            {
                "id": "mcp",
                "label": "MCP (Model Context Protocol)",
                "pros": ["Cross-host reuse", "Tools/resources/prompts unified"],
                "cons": ["Process/ops & evolving security model"],
                "best_for": ["Same capability in IDE + agents + local hosts"],
                "watchouts": ["Protocol ≠ authorization; confirm dangerous tools"],
            },
            {
                "id": "http_gateway",
                "label": "Custom HTTP / OpenAPI tool gateway",
                "pros": ["Enterprise auth, audit, SLA", "Single source of truth APIs"],
                "cons": ["Each agent framework needs an adapter"],
                "best_for": ["All writes & core reads in regulated systems"],
                "watchouts": ["Generate tool schemas from the same OpenAPI"],
            },
        ],
    },
    "serving": {
        "title": "Serving & models",
        "title_zh": "模型服务",
        "purpose": "Where tokens come from; streaming & structured outputs.",
        "options": [
            {
                "id": "closed_api",
                "label": "Closed model APIs",
                "pros": ["Strong quality/features", "Low ML ops"],
                "cons": ["Residency, price, rate limits, vendor risk"],
                "best_for": ["Default intelligence, tool-heavy flows"],
                "watchouts": ["Need failover / degrade plan"],
            },
            {
                "id": "open_weights",
                "label": "Open weights self-host",
                "pros": ["Control & privacy", "Tunable"],
                "cons": ["GPU & patch burden"],
                "best_for": ["Sensitive data, steady high-QPS templates"],
                "watchouts": ["Secure the serving stack like any prod service"],
            },
            {
                "id": "routing_mix",
                "label": "Hybrid model routing",
                "pros": ["Cost/quality balance"],
                "cons": ["Router needs evaluation"],
                "best_for": ["Production default fleets"],
                "watchouts": ["Measure per-route quality, not only $"],
            },
            {
                "id": "streaming_structured",
                "label": "Streaming + structured outputs",
                "pros": ["UX + machine-readable contracts"],
                "cons": ["Partial tool frames, schema failures"],
                "best_for": ["Interactive UIs + API automation"],
                "watchouts": ["Buffer to valid tool frames; validate JSON server-side"],
            },
        ],
    },
    "obs": {
        "title": "Observability & eval",
        "title_zh": "观测与评估",
        "purpose": "See causal chains; know if changes help.",
        "options": [
            {
                "id": "traces",
                "label": "Distributed traces / spans",
                "pros": ["Debug multi-step", "Attribute cost"],
                "cons": ["Instrumentation discipline"],
                "best_for": ["Any multi-step agent in prod"],
                "watchouts": ["Log prompts/tools carefully re PII"],
            },
            {
                "id": "golden_offline",
                "label": "Golden-set offline eval",
                "pros": ["Regression gates", "Comparable runs"],
                "cons": ["Set maintenance"],
                "best_for": ["CI quality gate before release"],
                "watchouts": ["Split intents (ID vs semantic) in the set"],
            },
            {
                "id": "online_eval",
                "label": "Online sampling / user signals",
                "pros": ["Catches drift"],
                "cons": ["Noisy, lagged"],
                "best_for": ["Complement—not replace—offline gates"],
                "watchouts": ["Do not ship on vibes alone"],
            },
        ],
    },
    "cost": {
        "title": "Cost / latency / safety",
        "title_zh": "成本 · 延迟 · 安全",
        "purpose": "Runtime controls for spend, speed, and harm reduction.",
        "options": [
            {
                "id": "routing",
                "label": "Tiered routing",
                "pros": ["Cut spend on easy tasks"],
                "cons": ["Mis-route hurts quality"],
                "best_for": ["Mixed FAQ + hard reasoning traffic"],
                "watchouts": ["Evaluate router like a model"],
            },
            {
                "id": "caching",
                "label": "Caching (exact / careful semantic)",
                "pros": ["Latency & $ wins"],
                "cons": ["Stale or wrong semantic hits"],
                "best_for": ["Hot exact prompts, retrieval keys"],
                "watchouts": ["Prefer exact caches; semantic needs TTL & monitoring"],
            },
            {
                "id": "guardrails",
                "label": "Guardrails + tool ACL",
                "pros": ["Policy enforcement beyond prompts"],
                "cons": ["False positives / ops"],
                "best_for": ["Any tool with side effects"],
                "watchouts": ["Prompt-only safety is not enough"],
            },
            {
                "id": "pii",
                "label": "PII minimization",
                "pros": ["Reduce leak blast radius"],
                "cons": ["Can break tasks if over-redacted"],
                "best_for": ["Tickets, CRM, medical/finance adjacent text"],
                "watchouts": ["Separate policies for logs vs model input vs answers"],
            },
        ],
    },
}

LAYER_ORDER = [
    "frameworks",
    "agents",
    "retrieval",
    "protocols",
    "serving",
    "obs",
    "cost",
]


def get_layer(key: str) -> dict[str, Any]:
    if key not in LAYERS:
        raise KeyError(f"unknown layer: {key}; choose from {LAYER_ORDER}")
    return LAYERS[key]


def all_layer_keys() -> list[str]:
    return list(LAYER_ORDER)
