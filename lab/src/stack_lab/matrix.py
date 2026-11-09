"""Decision-matrix data for AI engineering stacks.

Each layer has options with: label, pros, cons, best_for, watchouts.
Blog posts and CLI share this module as the single source of truth.

Option ids are stable API: recommend.py rules, tests, smoke_check and the
blog posts reference them (e.g. `retrieval/store_qdrant`, `obs/otel_genai`).
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
                "pros": [
                    "Huge component ecosystem",
                    "LangGraph explicit control flow",
                    "Fast Python iteration",
                ],
                "cons": [
                    "Thick abstractions hard to debug",
                    "Version churn",
                    "Java shops pay dual-stack cost",
                ],
                "best_for": ["Python services", "Complex graphs / human-in-the-loop"],
                "watchouts": [
                    "Do not express every branch as nested chains",
                    "Pin versions; keep escape hatches to raw SDK",
                ],
            },
            {
                "id": "pydantic_ai",
                "label": "PydanticAI-style typed thin frameworks",
                "pros": [
                    "Type-checked tools & structured outputs",
                    "Small dependency surface, easy to read end-to-end",
                    "Framework-agnostic: swap models without rewriting logic",
                ],
                "cons": [
                    "Fewer batteries: retrieval/tooling often hand-rolled",
                    "You re-solve problems LangChain already ships",
                    "Less copy-paste material for exotic flows",
                ],
                "best_for": [
                    "Small dedicated teams that hate thick abstractions",
                    "Services where typed I/O contracts matter more than components",
                ],
                "watchouts": [
                    "Still need your own eval/telemetry plan",
                    "Fine choice for the app layer; do not use as an excuse to skip orchestration design",
                ],
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
                "pros": [
                    "Native Spring Boot integration",
                    "Advisors/tools fit enterprise Java",
                    "Config/observability reuse",
                ],
                "cons": ["Younger ecosystem than Python", "Fewer copy-paste samples"],
                "best_for": ["Existing Java microservices embedding AI", "Compliance-friendly JVM stacks"],
                "watchouts": ["Keep retrieval design separate", "Reserve raw SDK path for critical calls"],
            },
            {
                "id": "ts_edge_sdk",
                "label": "Vercel AI SDK / Mastra (TS edge)",
                "pros": [
                    "First-class streaming UX primitives",
                    "Colocates with frontend/edge runtimes",
                    "TS type inference on tool schemas",
                ],
                "cons": [
                    "Python-land research lands late or never",
                    "Serverless limits long-running agent loops",
                ],
                "best_for": ["Product UIs where tokens stream straight to React", "Full-stack TS teams"],
                "watchouts": [
                    "Agent state/checkpoints in serverless need external stores",
                    "Do not rebuild heavy retrieval logic client-side",
                ],
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
                "label": "Multi-agent (explicit roles on shared state)",
                "pros": ["Role isolation", "Parallel specialties"],
                "cons": ["Bus/termination/cost complexity"],
                "best_for": ["Real division e.g. research + write + critique"],
                "watchouts": ["Climb the complexity ladder first; shared blackboard > prompt stuffing"],
            },
            {
                "id": "crewai_autogen",
                "label": "CrewAI / AutoGen-style role-conversation frameworks",
                "pros": [
                    "Fast to demo multi-role narratives",
                    "Conversation-as-orchestration is intuitive for non-engineers",
                    "Bundled role/memory abstractions",
                ],
                "cons": [
                    "Control flow lives in chat history — hard to test edges",
                    "Budget/termination often implicit until it bills you",
                    "Debugging = reading long transcripts",
                ],
                "best_for": ["Exploration, demos, non-side-effect creative pipelines"],
                "watchouts": [
                    "Prefer LangGraph-style explicit graphs once writes/money enter",
                    "Pin conversation budgets; conversation != audit trail",
                ],
            },
            {
                "id": "openai_agents_sdk",
                "label": "Hosted agent SDKs with handoffs (OpenAI Agents SDK style)",
                "pros": [
                    "Lightweight loop + handoff primitive in a few lines",
                    "Built-in tracing hooks in the vendor console",
                    "Low ceremony for single-vendor shops",
                ],
                "cons": [
                    "Handoff graphs get tangled without external design",
                    "Vendor-locked observability & tool format",
                ],
                "best_for": ["All-in-one-vendor products wanting agent structure fast"],
                "watchouts": [
                    "Export traces to your own OTel backend before it matters",
                    "Handoffs are still control flow: budget & gate them like edges",
                ],
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
                "watchouts": ["Bigger embedding != fix bad chunking"],
            },
            {
                "id": "hybrid",
                "label": "Hybrid BM25 + vector (+ rerank)",
                "pros": ["Complementary recall", "Production default"],
                "cons": ["Pipeline complexity", "Rerank latency/cost"],
                "best_for": ["Most production RAG"],
                "watchouts": ["Prefer RRF over raw score add; filter ACL before ANN"],
            },
            {
                "id": "contextual_chunks",
                "label": "Contextual retrieval / enriched chunks",
                "pros": [
                    "Chunk-level context blurbs fix 'it/this' ambiguity",
                    "Lifts both sparse and dense legs",
                    "Works with existing stores",
                ],
                "cons": [
                    "One extra LLM pass per chunk at index time",
                    "Enrichment prompts need eval too",
                ],
                "best_for": ["Chunky policy/doc corpora with pronoun-heavy fragments"],
                "watchouts": [
                    "Batch enrichment offline; never enrich in the query path",
                    "Version chunk metadata with the enrichment model",
                ],
            },
            {
                "id": "graph_rag",
                "label": "GraphRAG / KG-augmented retrieval",
                "pros": [
                    "Multi-hop & aggregate questions ('summarize all policies about X')",
                    "Explicit entities/relations are auditable",
                ],
                "cons": [
                    "Extraction & graph maintenance cost",
                    "Quality bounded by extraction accuracy",
                    "Overkill for point lookups",
                ],
                "best_for": ["Relationship-heavy corpora: org structures, regulation maps, ontologies"],
                "watchouts": [
                    "Keep vector/hybrid as the default leg; graph for the questions it uniquely answers",
                    "Budget extraction runs; drift detection on entity counts",
                ],
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
                "label": "Chroma (embedded)",
                "pros": ["Quick start", "Zero extra infra for prototypes"],
                "cons": ["Prod governance DIY", "Scale/HA on you"],
                "best_for": ["Proto / small teams"],
                "watchouts": ["Revisit before regulated prod"],
            },
            {
                "id": "store_pgvector",
                "label": "pgvector",
                "pros": ["SQL filters + biz DB unity", "One backup/HA story", "Joins with business tables"],
                "cons": ["Huge-scale ANN tradeoffs", "Vector index vs write throughput tuning"],
                "best_for": ["Mid scale with strong metadata filters"],
                "watchouts": ["Index & vacuum ops matter; benchmark HNSW vs IVFFlat per workload"],
            },
            {
                "id": "store_qdrant",
                "label": "Qdrant (dedicated vector engine)",
                "pros": [
                    "Purpose-built filtering + ANN performance",
                    "Payload filters feel first-class, not bolted on",
                    "Self-host or cloud; quantization options",
                ],
                "cons": [
                    "Another datastore to operate & back up",
                    "Cross-store consistency with business DB is yours",
                ],
                "best_for": ["Vector-heavy workloads where pgvector index tuning hurts", "Teams wanting managed vector without full vendor DB"],
                "watchouts": [
                    "Keep biz truth in SQL; replicate IDs, not authority",
                    "Load-test filtered queries — ANN + filter can degrade badly",
                ],
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
                "pros": ["Cross-host reuse", "Tools/resources/prompts unified", "Growing server ecosystem"],
                "cons": ["Process/ops & evolving security model", "Server quality varies wildly"],
                "best_for": ["Same capability in IDE + agents + local hosts"],
                "watchouts": [
                    "Protocol != authorization; confirm dangerous tools",
                    "Audit third-party MCP servers before granting them credentials",
                ],
            },
            {
                "id": "a2a",
                "label": "Agent-to-Agent protocols (A2A-style)",
                "pros": [
                    "Cross-org agent discovery & task delegation story",
                    "Clean agent capability cards (skills, auth) as contracts",
                ],
                "cons": [
                    "Early/evolving spec; interop still settles",
                    "Adds a second protocol to operate alongside MCP",
                ],
                "best_for": ["Federated setups: agents across teams/vendors delegating work"],
                "watchouts": [
                    "Treat remote agents like untrusted APIs: authz per task, rate limits, audit",
                    "Do not adopt for internal single-team flows; MCP/HTTP suffice",
                ],
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
                "pros": ["Control & privacy", "Tunable", "Steady-state unit economics at high QPS"],
                "cons": ["GPU & patch burden", "Serving-stack security is on you"],
                "best_for": ["Sensitive data, steady high-QPS templates"],
                "watchouts": ["Secure the serving stack like any prod service"],
            },
            {
                "id": "llm_gateway",
                "label": "Unified LLM gateway (LiteLLM / OpenRouter-style)",
                "pros": [
                    "One egress: auth, budgets, rate limits, failover in one place",
                    "Provider swap = config, not code",
                    "Central logging for cost attribution",
                ],
                "cons": [
                    "Yet another hop & proxy to operate",
                    "Vendor-specific features leak through lowest-common-denominator APIs",
                ],
                "best_for": ["Multi-provider fleets, org-wide cost control, fast failover"],
                "watchouts": [
                    "Gateway outage = full outage: HA it, keep a raw-SDK bypass path",
                    "Test provider-quirk features (tool call formats) per route",
                ],
            },
            {
                "id": "batch_api",
                "label": "Offline batch APIs",
                "pros": ["Large discounts vs interactive", "No rate-limit babysitting"],
                "cons": ["Hours of latency", "Not for interactive UX"],
                "best_for": ["Backfills, doc enrichment, nightly eval runs"],
                "watchouts": ["Batch input schemas differ subtly from chat APIs; keep a shared validator"],
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
                "id": "otel_genai",
                "label": "OpenTelemetry GenAI semantic-convention spans",
                "pros": [
                    "Vendor-neutral span names/attrs for prompts, completions, tools",
                    "Swap tracing backends without re-instrumenting",
                    "Pairs with existing microservice traces (one trace = one request)",
                ],
                "cons": [
                    "Conventions still versioning (semconv incubating)",
                    "Some vendor SDKs emit vendor formats first",
                ],
                "best_for": ["Multi-vendor stacks and orgs with an OTel collector already"],
                "watchouts": [
                    "Decide prompt-content capture policy before enabling, not after",
                    "Keep gen_ai spans correlated with business request ids",
                ],
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
                "id": "llm_judge",
                "label": "LLM-as-judge offline scoring",
                "pros": [
                    "Scales grading beyond hand-labeling",
                    "Consistent rubric across candidates",
                ],
                "cons": [
                    "Judge has its own failure modes: position bias, verbosity bias",
                    "Calibration cost against human labels",
                ],
                "best_for": ["Grading long-form answers, pairwise model comparison, RAG faithfulness"],
                "watchouts": [
                    "Calibrate on ~100 human-labeled pairs first; re-check quarterly",
                    "Never let a judge alone gate a release; pair with metric + spot checks",
                ],
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
                "id": "prompt_cache",
                "label": "Prompt caching / KV reuse (provider-side)",
                "pros": [
                    "Big discounts on repeated system prompts & few-shot blocks",
                    "Latency drops with zero correctness risk",
                ],
                "cons": [
                    "Cache-hit rules differ per provider (prefix, TTL)",
                    "Cache misses silently at budget time",
                ],
                "best_for": ["Stable system prompts + long tool schemas on every call"],
                "watchouts": [
                    "Structure prompts: cacheable prefix first, dynamic tail last",
                    "Track cache-hit rate as a first-class metric",
                ],
            },
            {
                "id": "semantic_cache",
                "label": "Semantic cache (embedding-similarity responses)",
                "pros": ["Hits on paraphrases exact cache misses", "Cuts cost on FAQ-like traffic"],
                "cons": [
                    "Wrong hit = confidently wrong answer served to user",
                    "Threshold tuning; embedding drift; invalidation hard",
                ],
                "best_for": ["High-volume, low-stakes Q&A where a near-miss is tolerable"],
                "watchouts": [
                    "TTL + hit-rate QA + bypass for auth/transactional queries",
                    "Log every semantic hit for sampling; never cache side-effect answers",
                ],
            },
            {
                "id": "guardrails",
                "label": "Guardrails + tool ACL",
                "pros": ["Policy enforcement beyond prompts"],
                "cons": ["False positives / ops"],
                "best_for": ["Any tool with side effects"],
                "watchouts": [
                    "Prompt-only safety is not enough",
                    "Measure guardrail precision/recall on a labeled abuse set; a noisy guardrail gets switched off",
                ],
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


def find_option(layer_key: str, option_id: str) -> dict[str, Any]:
    layer = get_layer(layer_key)
    for opt in layer["options"]:
        if opt["id"] == option_id:
            return opt
    raise KeyError(f"unknown option {option_id!r} in layer {layer_key!r}")