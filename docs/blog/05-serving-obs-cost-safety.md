# 05 · 服务、观测、成本与安全:网关、OTel GenAI、评测、缓存与 Guardrail

> 对应矩阵层:`serving` / `obs` / `cost`(`python3 -m stack_lab.cli compare all`)。选项 id:`closed_api` / `open_weights` / `llm_gateway` / `batch_api` / `routing_mix` / `streaming_structured` / `traces` / `otel_genai` / `golden_offline` / `llm_judge` / `online_eval` / `routing` / `prompt_cache` / `semantic_cache` / `guardrails` / `pii`。姊妹仓:[agent-observability](https://github.com/jianwen049-hub/agent-observability) · [llm-cost-latency](https://github.com/jianwen049-hub/llm-cost-latency) · [ai-eval-lab](https://github.com/jianwen049-hub/ai-eval-lab)。

## 当时业务痛点

演示很惊艳,一进生产就三连崩:

1. **延迟**:首 token 慢,用户以为卡死;全量 JSON 又等太久。
2. **账单**:周末一次 Agent 死循环,工具日志刷爆,早会财务报表先到。
3. **事故**:模型把工单里的手机号原样回给无关坐席;或一本正经幻觉政策。
4. **不会改**:没有 trace,不知道坏在检索、工具还是提示词;没有黄金集,改 prompt 只能靠感觉。

这是同一类问题:**把模型当系统,却没按系统去服务、观测、计费和设防。**

### 具体翻车现场(不是段子)

- **观测断链**:三家厂商各自一套 trace 控制台,同一条请求的检索 span 在 A 家、模型 span 在 B 家,根本对不起来。迁到 OTel GenAI 语义约定后,一条 trace 从入口贯到工具调用,排障从「猜」变成「看」。教训:**观测格式要厂商中立**(矩阵 `obs/otel_genai`)。
- **语义缓存投毒事故**:语义缓存把「如何注销账号?」命中到「如何冻结账号?」的旧答案,阈值 0.87 的相似度看起来很高,用户照着错误答案操作。教训:**语义缓存必须 TTL + 命中抽样 QA + 高危主题白名单旁路**(矩阵 `cost/semantic_cache`)。
- **缓存命中率没人看**:上了 provider prompt cache,月账单没降;查了才发现系统 prompt 前面拼了时间戳,前缀永远不同,天天 miss。教训:**可缓存前缀放头、动态内容放尾,命中率当一等指标**(矩阵 `cost/prompt_cache`)。
- **judge 偏长**:LLM-as-judge 上线后,所有更啰嗦的回答得分都更高;校准集一跑,长度偏差肉眼可见。教训:**judge 要先对 100 条人工标注校准,且永远不能单独发版门禁**(矩阵 `obs/llm_judge`)。

## 当时怎么看这个问题

服务层要回答:模型从哪来、流式怎么切、结构化怎么约束。观测层要回答:一次请求的因果链。评估层要回答:改动是变好还是变差。成本与安全是横切——路由、缓存、护栏、PII——它们不是上线前的检查表,而是**运行时架构**。

2025–2026 的三个新默认:

1. **统一 LLM 网关**(`serving/llm_gateway`):多供应商的团队把「换模型」从改代码变成改配置,预算、限流、failover 收进一个入口。代价是多一跳、多一个要 HA 的组件。
2. **OpenTelemetry GenAI 语义约定**(`obs/otel_genai`):prompt/completion/tool 的 span 字段标准化,trace 后端可换,观测不再是厂商锁定的粘合剂。
3. **缓存拆成两种**:`prompt_cache`(provider 前缀缓存,零正确性风险)与 `semantic_cache`(语义命中,有错答风险)——同一个词「缓存」,风险差一个量级,必须分开设计、分开评测。

## 试过什么

### 模型服务

1. **只接一家闭源 API**(`closed_api`):质量稳、功能全;出境、单价、限流、停服风险要预案。
2. **自宿开源权重**(`open_weights`):数据可控、可微调;要吃 GPU、工程与安全补丁。
3. **LiteLLM / OpenRouter 式统一网关**(`llm_gateway`):鉴权、预算、failover 一处收口;厂商特有功能会漏过最小公倍数接口,要按路由测试。
4. **离线 batch API**(`batch_api`):批量回填与夜间评测便宜一个量级;接口细节与 chat API 有微妙差异,要共享校验器。
5. **结构化输出**:JSON mode / schema;仍要服务端校验,不信模型一次成型。
6. **流式 SSE 到前端**:体验好;取消、半截工具调用、网关缓冲要设计。

### 观测与评估

1. **只打应用日志**:缺 span 关联,Agent 多步对不上。
2. **厂商控制台 trace**:各家格式不同,跨厂商断链;导出到自家 OTel 后端才连贯。
3. **OTel GenAI 语义约定 span**(`otel_genai`):厂商中立、与既有微服务 trace 同一条链;prompt 内容捕获策略要先定(合规!),不是装完再想。
4. **LLM-as-judge**(`llm_judge`):评分可扩展;有长度偏差、位置偏差,要人工校准集钉住。
5. **离线黄金集 + 在线抽样 + trace**:可管,但要维护成本。

### 成本 / 延迟 / 安全

1. **一律最强模型**:贵且慢。
2. **prompt cache**(`prompt_cache`):稳赚;注意前缀结构与命中率监控。
3. **semantic cache**(`semantic_cache`):FAQ 流量省钱;错答风险要 TTL、抽样 QA、旁路清单三件套。
4. **靠 prompt 防泄露**:不够。
5. **出口正则脱敏 + 工具 ACL + 路由小模型 + guardrail 抽检**(`guardrails` / `pii`):有效,需持续调;guardrail 自身的精确率/召回率也要在标注集上评,否则误拦太多会被悄悄关掉。

## 为什么否决

| 选项 | 原因 |
|------|------|
| **无双供的单一闭源依赖** | 否决作为唯一生产通路(至少要有降级或只读缓存预案)。 |
| **无 schema 校验的「模型保证 JSON」** | 否决。 |
| **无 trace 的多步 Agent 上生产** | 否决。 |
| **只靠在线用户反馈当评测** | 否决作为唯一质量信号。 |
| **judge 单独当发版门禁** | 否决。judge 与指标 + 抽检三方绑定,防长度/位置偏差悄悄放水。 |
| **最大模型打天下** | 否决默认路由。 |
| **semantic cache 无旁路清单** | 否决。账号/支付/权限类查询永远直连。 |
| **Prompt-only 安全** | 否决。要网关 ACL、PII 过滤、输出检查。 |

## 最终怎么解

### 1) Serving & models

| 选项 | 优点 | 缺点 | 场景 |
|------|------|------|------|
| 闭源 API(`closed_api`) | 质量/功能/运维省 | 数据出境与议价、限流 | 默认智能、工具调用密集 |
| 开源自宿(`open_weights`) | 可控、可私有化 | GPU 与工程成本 | 敏感数据、稳定高 QPS 模板任务 |
| 统一 LLM 网关(`llm_gateway`) | 换供应商=改配置;预算/限流/failover 收口 | 多一跳要 HA;厂商特性漏过统一接口 | 多供应商车队、组织级成本管控 |
| 离线 batch(`batch_api`) | 大折扣、免限流陪跑 | 小时级延迟 | 回填、文档增强、夜间评测 |
| 混合路由(`routing_mix`) | 成本与质量平衡 | 路由策略要评测 | **推荐默认**:简单→小/本地,难→大 |

流式:UI 走 token 流;工具调用边界要「缓冲到合法帧」再执行(`streaming_structured`)。结构化:schema 生成 + 服务端校验 + 失败重试一次严格模式。

### 2) Observability & eval

| 手段 | 用途 |
|------|------|
| **Trace / Span**(请求→检索→工具→模型) | 排障、归因、费用归集 |
| **OTel GenAI 语义约定**(`otel_genai`) | 厂商中立 span,后端可换,与业务 trace 同链 |
| **黄金集离线评**(`golden_offline`) | 改 prompt/检索不盲飞 |
| **LLM-as-judge**(`llm_judge`) | 长答案、成对比较、RAG 忠实度规模化评分;必须先校准 |
| **在线抽样 + 用户信号**(`online_eval`) | 分布漂移 |
| **回归门禁** | CI 里跑关键集,坏了不发版 |

姊妹仓:[agent-observability](https://github.com/jianwen049-hub/agent-observability) · [ai-eval-lab](https://github.com/jianwen049-hub/ai-eval-lab)

### 3) Cost / latency / safety

| 杠杆 | 做法 |
|------|------|
| **路由**(`routing`) | 分类器/规则:FAQ 走小模型或缓存;复杂推理走大模型 |
| **prompt cache**(`prompt_cache`) | 稳定 system prompt + 长 tool schema 放前缀;命中率一等指标 |
| **semantic cache**(`semantic_cache`) | 高频低风险 FAQ;TTL + 命中抽样 QA + 账号/支付类旁路 |
| **预算** | 每请求 token / 费用硬顶,Agent 步数硬顶(见 02) |
| **Guardrail**(`guardrails`) | 输入注入检测、输出政策、工具 ACL;guardrail 自身也要评测 |
| **PII**(`pii`) | 入模前脱敏、出模后扫描、日志落盘分级 |

姊妹仓:[llm-cost-latency](https://github.com/jianwen049-hub/llm-cost-latency)

CLI:

```bash
python3 -m stack_lab.cli compare serving
python3 -m stack_lab.cli compare obs
python3 -m stack_lab.cli compare cost
python3 -m stack_lab.cli compare all
```

### 缓存决策表(prompt cache vs semantic cache)

| 问题 | prompt cache | semantic cache |
|------|--------------|----------------|
| 命中条件 | 前缀逐字节相同 | 语义相似度过阈值 |
| 错答风险 | **零**(同前缀只是省钱) | **有**(近似命中=近错答案) |
| 运维件套 | 命中率监控 | TTL + 抽样 QA + 旁路清单 + 阈值回归 |
| 先上哪个 | **先上这个** | FAQ 流量大且能容忍近错时再上 |

## 用到的具体 skill / 技巧清单

| Skill | 用法 |
|-------|------|
| **双供与降级** | 主模型挂了只读缓存或小模型致歉 |
| **网关收口** | 预算/限流/failover 一处管;网关自身要 HA,留 raw-SDK 旁路 |
| **流式与工具分相** | 展示可流,执行要完整帧 |
| **Schema + 校验** | 结构化输出两道闸 |
| **Trace 必打费用** | 成本和质量同一条因果链 |
| **OTel GenAI 约定** | 观测厂商中立;prompt 捕获策略先定 |
| **judge 先校准** | 100 条人工标注,季度复检;不单独门禁 |
| **离线门禁** | 黄金集不过不发版 |
| **路由省钱** | 不是损质量,是把简单题分流 |
| **缓存二分** | prompt cache 稳赚;semantic cache 三件套 |
| **PII 分层** | 训练/日志/回答/工具参数各有策略 |
| **guardrail 也要评** | 精确率/召回率不达标 = 会被悄悄关掉 |

## 代码 / 表解析

### `matrix.py` → `serving` / `obs` / `cost`

三张表分别沉淀模型来源、观测评估、成本安全选项。本轮扩充:`serving` 加 `llm_gateway` 与 `batch_api`;`obs` 加 `otel_genai` 与 `llm_judge`;`cost` 把单一 `caching` 拆成 `prompt_cache` 与 `semantic_cache` 两个风险等级不同的行,并加 `guardrails` 的评测 watchout。

### `lab/src/stack_lab/cli.py` → `recommend`

痛点含 `pii`/`合规`/`延迟`/`账单`/`语义缓存`/`otel` 等关键词时,打印对应层的优先选项与 watchouts。

### `smoke_check.py`

确保七层 key 齐全:`frameworks, agents, retrieval, protocols, serving, obs, cost`,且每层至少 3 个 options,新增行(`llm_gateway` / `otel_genai` / `prompt_cache` 等)在位;`recommend` 对新旧关键词串都返回 0。

---

**一句话**:上线不是接好 API,而是 **可服务、可看见、可测量、可限费、可设防**;网关与 OTel 让这些变成架构而不是纪律,缓存按风险二分,评测永远比 vibes 有说服力——对比表是地图,CI 与网关才是方向盘。