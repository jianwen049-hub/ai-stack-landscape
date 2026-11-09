# 04 · 工具协议:OpenAI Tools · MCP · A2A · 自定义 HTTP,谁在什么时候赢

> 对应矩阵层:`protocols`(`python3 -m stack_lab.cli compare protocols`)。选项 id:`openai_tools` / `mcp` / `a2a` / `http_gateway`。姊妹仓:[mcp-lab](https://github.com/jianwen049-hub/mcp-lab) · [spring-ai-lab](https://github.com/jianwen049-hub/spring-ai-lab)。

## 当时业务痛点

同一个「查订单」能力,被接了三次:ChatGPT 自定义 Action、内部 Agent 的 function call JSON、第三个自动化平台的 webhook。字段名不一致,鉴权各写各的,文档全过期。Agent 一多,工具层变成**集成税中心**。

同时行业出现 **MCP(Model Context Protocol)** 叙事:工具/资源/提示以标准协议暴露给任意宿主。Java 侧 Spring AI 也在接 MCP 客户端/服务端。随后又冒出 **A2A(Agent-to-Agent)** 一类跨组织 Agent 互操作的叙事。问题变成:

- 继续用厂商 Function Calling 够不够?
- 是否值得把内部能力封成 MCP Server?
- A2A 这种 Agent 间协议要不要跟?
- 哪些永远该留在自定义 HTTP / gRPC?

### 具体翻车现场(不是段子)

- **五份「查订单」**:一年后仓库里躺着五个 repo,各自实现了字段名不同的查订单工具;某天下游改了限流策略,只改了三份。教训:**工具描述也要有单一来源**。
- **MCP Server 供应链**:从社区装了一个「数据库查询」MCP Server,它默认读整库;幸好演练环境先跑,否则生产凭据就交出去了。教训:**第三方 MCP Server 当第三方依赖审,不当配置项抄**。
- **Schema 撒谎**:工具 schema 写 `status: enum[paid, shipped]`,真实 API 还有 `partially_refunded`;模型永远选不到这个值,客服排障排了两天才发现是 schema 过期。教训:**schema 从 OpenAPI 生成,手写必漂**。
- **把 prompt 当权限**:「你只能查询,不要修改」写在 system prompt 里;一次注入攻击让模型调了 `updateOrderStatus`。教训:**prompt 是说明书,不是门禁;门禁在网关 ACL**。

## 当时怎么看这个问题

工具协议解决的是 **「谁来发现能力、谁来鉴权、谁来传参与流式结果」**,不是让模型变聪明。选协议要看:宿主是否多样、工具是否要跨产品复用、是否要本地/远程一致体验、安全边界谁来守。

MCP 的真实价值在**复用与宿主边界**:同一个「查订单」写一次,IDE、桌面助手、内部 Agent 都能用。A2A 的价值在**跨边界委托**:把我做不了的任务连同能力声明一起交给你的 Agent。两者的共同陷阱:都**不是授权模型**——协议管「怎么找到、怎么调用」,不管「该不该让你调」。

## 试过什么

1. **纯 OpenAI-compatible tools(JSON Schema function calling)**(`openai_tools`):与模型集成紧、例子多;换宿主或跨进程工具进程时,发现/生命周期要自管。
2. **每个 Agent 项目一份 tools.py**:最快;一年后出现五份「查订单」。
3. **企业内部 HTTP Tool 网关(OpenAPI)**(`http_gateway`):统一鉴权、限流、审计;Agent 侧仍要适配成 function schema。
4. **MCP Server 封装同一网关**(`mcp`):IDE / Agent 宿主 / 桌面侧可复用;协议与进程模型要学,生态仍在快速变。
5. **A2A 式跨组织委托**(`a2a`):agent capability cards + 任务委托的叙事很顺;规范年轻、落地案例少,安全模型完全自理。
6. **把高危写操作只暴露给 MCP、不设网关鉴权**:危险实验,见否决。

## 为什么否决

| 选项 | 原因 |
|------|------|
| **无网关的裸 MCP / 裸 Function** | 否决上生产写操作。协议 ≠ 授权。 |
| **为 MCP 而 MCP** | 否决。只有一个宿主、三个工具时,标准协议收益有限。 |
| **未经审计的第三方 MCP Server** | 否决直连生产。MCP Server 是依赖,要过供应链审查:读它的源、限它的凭据、看它的出网。 |
| **A2A 用于单团队内部** | 否决。内部单团队流程用 MCP/HTTP 足够;多养一个协议就是多养一套运维与安全面。 |
| **Agent 直接拿 DB 凭据** | 否决。工具必须是受控 API,而不是「模型 + 连接串」。 |
| **放弃厂商 tools 只留 MCP** | 现阶段否决「唯一」。许多推理 API 原生 tools 延迟与贴合度仍最好,可双轨。 |

## 最终怎么解

**能力下沉为稳定业务 API;适配层可多协议。**

```
[业务服务 / 只读与幂等写 API]
        ↑
[Tool Gateway:鉴权·限流·审计·幂等键]
        ↑
   ┌────┼────┐
OpenAI Tools  MCP Server  内部 SDK
(会话内调用) (跨宿主)  (Java Bean)

跨组织(A2A)→ 仍走上述网关,凭据短期化,按任务授权
```

| 协议 | 优点 | 缺点 | 什么场景选谁 |
|------|------|------|--------------|
| **OpenAI-compatible Tools**(`openai_tools`) | 与聊天 API 原生、延迟友好、生态熟 | 跨宿主发现弱、易项目内复制 | 单产品内 Agent、快速迭代 |
| **MCP**(`mcp`) | 跨宿主复用、资源/工具/提示统一、适合桌面与多客户端 | 运维进程、版本与安全模型要认真做;**Server 质量参差** | 同一工具要进 IDE + 多人 Agent + 本地助手 |
| **A2A 式**(`a2a`) | 跨组织发现与任务委托、能力卡片契约 | 规范年轻、双协议运维成本 | 联邦场景:跨团队/跨厂商 Agent 委托 |
| **自定义 HTTP/OpenAPI 网关**(`http_gateway`) | 企业鉴权、审计、SLA 成熟 | 每个 Agent 框架要写适配器 | **所有写操作与核心读的底层真相** |

Spring AI 场景:ChatClient tools / FunctionCallback 对接网关;MCP 客户端用来接入已有 Server;**不要**让模型直接碰数据源。细节姊妹仓:[spring-ai-lab](https://github.com/jianwen049-hub/spring-ai-lab)。MCP Server 的封装与调试实验在 [mcp-lab](https://github.com/jianwen049-hub/mcp-lab)。

CLI:`python3 -m stack_lab.cli compare protocols`

### 常见踩坑

1. **Schema 与真实校验不一致** → 模型以为参数合法,网关 400;要用同一份 JSON Schema / OpenAPI 生成。
2. **工具描述写成小说** → 模型乱调用;描述要短、边界要硬(「仅查询、不退款」)。
3. **超时与部分失败** → 必须幂等键;MCP / HTTP 都一样。
4. **把 prompt 当权限** → 「不要调用删除」不是安全控制。
5. **本地 MCP 默认信任** → 桌面场景仍要用户确认高危工具。
6. **MCP Server 当配置抄** → 社区 Server 先审后装:读源码、限凭据、看出网、灰度接入。
7. **A2A 当内部 RPC** → 跨组织委托每个任务都要独立授权与限流,别复用长期凭据。

### 工具暴露分级表

| 工具类型 | 暴露方式 | 门禁 |
|----------|----------|------|
| 只读查询 | 网关 + OpenAI Tools / MCP | 限流 + 租户过滤 |
| 幂等写(可重试) | 网关 + MCP / 内部 SDK | 幂等键 + 预算 |
| 危险写(退款/删除) | 网关 + 人工门 | 幂等键 + 审批边(见 02 图编排) |
| 跨组织委托 | A2A 式 + 短期凭据 | 按任务授权 + 全量审计 |

## 用到的具体 skill / 技巧清单

| Skill | 用法 |
|-------|------|
| **业务 API 为真相** | 协议只是适配 |
| **双轨适配** | 会话内 tools + 跨宿主 MCP |
| **网关统一鉴权** | OAuth/mTLS/服务账号,不进 prompt |
| **幂等键** | 所有写工具强制 |
| **精短 tool description** | 动词边界写清 |
| **Schema 单一来源** | OpenAPI → tools / MCP 生成 |
| **MCP 供应链审查** | 审源码、限凭据、看出网、灰度 |
| **协议≠授权** | A2A/MCP 只管发现与调用,「该不该」永远在网关 |

## 代码 / 表解析

### `matrix.py` → `protocols`

选项 `openai_tools` / `mcp` / `a2a` / `http_gateway` 的 pros/cons/best_for/watchouts;`a2a` 行的 watchouts 明确写着「远程 Agent 当不受信 API 对待」,这是这一层最重要的安全默认。

### `recommend`

痛点含 `ide`/`cursor`/`跨应用` → 提高 MCP;含 `java`/`spring`/`网关` → 强调 HTTP gateway 为底层;含 `a2a` → 命中跨组织协议行并附带门禁提醒。

---

**一句话**:MCP 很重要,但**赢在复用与宿主边界**;A2A 管跨组织委托,更早的问题是「凭据给不给」;写操作的胜负手永远是网关、鉴权与幂等。