# 02 · Agent 编排:单兵、多 Agent、ReAct、Plan-Execute、图工作流、CrewAI/AutoGen

> 对应矩阵层:`agents`(`python3 -m stack_lab.cli compare agents`)。选项 id:`react` / `plan_execute` / `graph` / `multi_agent` / `crewai_autogen` / `openai_agents_sdk`。姊妹仓:[multi-agent-orchestration](https://github.com/jianwen049-hub/multi-agent-orchestration) · [agent-observability](https://github.com/jianwen049-hub/agent-observability) · [rag-agent-lab](https://github.com/jianwen049-hub/rag-agent-lab)。

## 当时业务痛点

客服助手从「检索答一句」长成「查订单 → 判断能否退 → 调退款工具 → 写回访摘要」。产品要自动化;风控要人工确认;研发发现:一个巨大 System Prompt + while tool_call 循环,在异常订单上会**死循环烧钱**,或者在半失败状态留下脏写。

痛点拆开是:

1. **控制流不透明**:模型下一步干什么,日志里只能猜。
2. **责任边界不清**:检索、决策、写操作、质检混在一个 Agent 里,权限难收。
3. **失败不可恢复**:工具超时后重试策略与业务幂等没设计。
4. **协作成本**:多人改同一个巨型 prompt,冲突不断。

### 具体翻车现场(不是段子)

- **死循环账单**:ReAct 循环在「订单不存在」分支反复调用同一查询工具 47 次,因为观察结果里没有任何「此路不通」的硬信号,模型只能继续猜。一晚上烧掉平时三周的 token 费。教训:**步数与费用硬顶必须在循环外面,不在 prompt 里面**。
- **半失败脏写**:退款工具超时,Agent 重试,结果前一笔其实已成功——用户被退了两次。教训:**写工具必须带幂等键,重试语义由键决定**。
- **CrewAI 剧场感**:五个角色的对话记录读了 30 页,「质检官」夸了「写作官」三遍,然后一起跑题。质量没有提升,token 费先翻三倍。教训:**没有真实职责冲突时,多角色对话是戏剧不是工程**。
- **计划腐烂**:Plan-and-Execute 在第 2 步发现库存数据变了,后面的计划仍在执行旧世界假设。教训:**计划必须可失效,工具结果改变世界时要重规划**。

## 当时怎么看这个问题

早期流行叙事是「Agent = LLM + Tools + Memory」,好像加工具就会自己变聪明。2025 年行业叙事又摆到另一头:「多 Agent 编排框架(CrewAI / AutoGen / 各家 Agents SDK)开箱即用」。工程上更准确的说法始终是:**Agent = 带策略的控制回路**。策略可以是 ReAct 逐步想、可以是先规划再执行、可以是显式图、可以是多角色分工。选错策略的代价是延迟、费用和事故,不是「不够智能」这种空话。

判断「CrewAI/AutoGen 式角色对话框架」与「LangGraph 式显式图」的关键:**控制流写在聊天记录里,还是写在可测试的边里**。前者 demo 快、审计难;后者前期贵、回放易。一旦有写操作与真钱,答案几乎总是后者。

## 试过什么

1. **单 Agent + ReAct(Thought/Action/Observation 循环)**(`react`):实现简单;工具一多就迷路,且难插入「必须人工点头」的硬门禁。
2. **单 Agent + Plan-and-Execute**(`plan_execute`):先出计划再逐步执行;计划过时(世界状态变了)时要重规划,否则假执行。
3. **多 Agent 分工(研究员 / 执行者 / 批评者)**(`multi_agent`):质量有时更好;消息总线、终止条件、成本爆炸是新问题。
4. **CrewAI / AutoGen 式角色对话框架**(`crewai_autogen`):十分钟配好「团队」;控制流埋在会话历史里,预算与终止常常是隐式的,账单先到、质量后到。
5. **OpenAI Agents SDK 式宿主循环 + handoff**(`openai_agents_sdk`):几行代码得到「循环 + 移交」原语,自带 trace 控制台;handoff 图一复杂,可测试性下降,观测还锁在厂商控制台。
6. **LangGraph / 自研状态图**(`graph`):节点=技能,边=转移条件,checkpoint=可恢复;样板代码多,但事故可回放。
7. **把一切塞进一条 chain**:否决候选,见下。

## 为什么否决

| 选项 | 原因 |
|------|------|
| **永远单 Agent 无限 ReAct** | 否决作为写操作默认态。无上限循环 + 副作用工具 = 事故温床。 |
| **多 Agent 默认上** | 否决「一上来就五六个角色」。通信与评测成本常高于收益;先证明单图节点不够再用多 Agent。 |
| **CrewAI/AutoGen 用于带钱的流程** | 否决。角色对话框架适合探索与创作管线;控制流埋在会话里,审计与幂等没有着力点。 |
| **宿主 Agents SDK 唯一化** | 否决「只用它」。handoff 仍是控制流,需要同样的预算与门禁;且观测导出要尽早切到自家 OTel 后端(见 05)。 |
| **纯 Plan 一次生成永不修订** | 否决。工具结果会改变世界,计划必须可失效、可重规划。 |
| **用更大模型代替编排** | 否决。模型能力 ≠ 工作流正确性;权限、幂等、审计仍要结构保证。 |

## 最终怎么解

用「复杂度梯子」升级,而不是跳级:

```
单次补全 → 单工具调用 → 单 Agent 有限步 ReAct
   → 显式图(分支/重试/人工门) → 多 Agent(仅当角色冲突真实存在)
```

| 模式 | 优点 | 缺点 | 什么场景选 |
|------|------|------|------------|
| **单 Agent ReAct** | 实现快、灵活 | 易循环、难审计硬门禁 | 只读检索、低风险问答 |
| **Plan-Execute** | 步骤可见、易向人展示 | 计划过时;规划本身耗 token | 步骤稳定的批处理分析 |
| **图工作流** | 状态显式、可测、可 checkpoint | upfront 设计成本 | 有副作用、要审批、要回放 |
| **多 Agent(显式角色+共享状态)** | 角色隔离、可并行专项 | 总线/终止/费用复杂 | 调研+写作+质检等真实分工 |
| **CrewAI/AutoGen 角色对话** | 十分钟出 demo、叙事直观 | 控制流在聊天里,难测难审 | 无副作用的探索/创作管线 |
| **宿主 Agents SDK + handoff** | 循环/移交原语开箱即用、trace 方便 | handoff 图缠起来后不可读;厂商锁定 | 单厂商产品快速结构化 |

配套硬约束(与模型无关):

- **步数 / 费用预算**硬顶,挂在循环外面;
- **写工具**必须幂等键 + 人工或规则门禁;
- **终止条件**写进图边,不写进「请你自己判断是否结束」的散文里;
- 批评者(critic)可以否决,但要规定否决后的边:重试 / 升级人工 / 降级回答。

### 决策表:什么时候上多 Agent

| 问题 | 若否 | 若是 |
|------|------|------|
| 两个角色的 prompt 是否在互相打架(一个要快、一个要全)? | 单 Agent 分阶段就够 | 考虑显式角色,共享黑板 |
| 是否需要**并行**跑互不依赖的子任务(如同时查三个数据源)? | 串行图节点即可 | 值得多 Agent/并行分支 |
| 某角色是否需要**不同权限**(质检只读、执行可写)? | 同一 Agent 换 prompt 即可 | 按权限拆角色,写权限单独网关 |
| 单步上下文是否塞不下(研究员 50 页笔记,写作只需结论)? | 长上下文/摘要即可 | 拆角色 + 结构化中间产物 |

四个「若否」都命中 → 你需要的不是多 Agent,是更好的图。

本仓 CLI:`python3 -m stack_lab.cli compare agents`

姊妹仓实践:[multi-agent-orchestration](https://github.com/jianwen049-hub/multi-agent-orchestration)

## 用到的具体 skill / 技巧清单

| Skill | 用法 |
|-------|------|
| **复杂度梯子** | 能用单节点绝不上多 Agent |
| **副作用隔离** | 读工具松、写工具严;写节点单独鉴权 |
| **显式终止** | max_steps、预算、成功/失败终态 |
| **Checkpoint** | 长任务可恢复,避免整段重跑 |
| **Critic 有边** | 否决不是结束,是否决后的转移 |
| **黑板 / 共享状态** | 多 Agent 别只靠塞进 prompt 的聊天记录 |
| **幂等键** | 一切写工具的第一参数 |
| **对话≠审计** | 角色对话框架里,预算与终止必须外置 |

## 代码 / 表解析

### `lab/src/stack_lab/matrix.py` → `agents`

选项含 `react` / `plan_execute` / `graph` / `multi_agent` / `crewai_autogen` / `openai_agents_sdk`,字段含 `pros`/`cons`/`best_for`/`watchouts`。`crewai_autogen` 与 `openai_agents_sdk` 是 2025–2026 争论的直接沉淀:前者「会话即编排」,后者「轻循环+移交」。

### `lab/src/stack_lab/recommend.py`

痛点串含「审批」「退款」「写库」→ 提高 `graph` 分;含「调研」「写作」「质检」→ 才考虑 `multi_agent`;含 `crewai`/`autogen`/`handoff` → 命中新框架行。测试 `test_recommend_rules_reference_real_options` 保证这些规则引用的 id 永远真实存在。

### 与观测的衔接

没有 trace 的多步 Agent 等于盲飞——见 05 与 [agent-observability](https://github.com/jianwen049-hub/agent-observability)。多 Agent 的 trace 尤其要带**角色与成本归集字段**,否则「哪个角色烧的钱」都答不上来。端到端 Agent + RAG 组合的实验方法在 [rag-agent-lab](https://github.com/jianwen049-hub/rag-agent-lab)。

---

**一句话**:编排的本质是**把不可控的模型下一步,收成可控的状态转移**;图是手段,预算与幂等是底线,角色对话框架只配给不碰钱的流程。