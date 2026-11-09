# 04 · 工具协议：OpenAI Tools · MCP · 自定义 HTTP，谁在什么时候赢

## 当时业务痛点

同一个「查订单」能力，被接了三次：ChatGPT 自定义 Action、内部 Agent 的 function call JSON、第三个自动化平台的 webhook。字段名不一致，鉴权各写各的，文档全过期。Agent 一多，工具层变成**集成税中心**。

同时行业出现 **MCP（Model Context Protocol）** 叙事：工具/资源/提示以标准协议暴露给任意宿主。Java 侧 Spring AI 也在接 MCP 客户端/服务端。问题变成：

- 继续用厂商 Function Calling 够不够？
- 是否值得把内部能力封成 MCP Server？
- 哪些永远该留在自定义 HTTP / gRPC？

## 当时怎么看这个问题

工具协议解决的是 **「谁来发现能力、谁来鉴权、谁来传参与流式结果」**，不是让模型变聪明。选协议要看：宿主是否多样、工具是否要跨产品复用、是否要本地/远程一致体验、安全边界谁来守。

## 试过什么

1. **纯 OpenAI-compatible tools（JSON Schema function calling）**：与模型集成紧、例子多；换宿主或跨进程工具进程时，发现/生命周期要自管。
2. **每个 Agent 项目一份 tools.py**：最快；一年后出现五份「查订单」。
3. **企业内部 HTTP Tool 网关（OpenAPI）**：统一鉴权、限流、审计；Agent 侧仍要适配成 function schema。
4. **MCP Server 封装同一网关**：IDE / Agent 宿主 / 桌面侧可复用；协议与进程模型要学，生态仍在快速变。
5. **把高危写操作只暴露给 MCP、不设网关鉴权**：危险实验，见否决。

## 为什么否决

| 选项 | 原因 |
|------|------|
| **无网关的裸 MCP / 裸 Function** | 否决上生产写操作。协议 ≠ 授权。 |
| **为 MCP 而 MCP** | 否决。只有一个宿主、三个工具时，标准协议收益有限。 |
| **Agent 直接拿 DB 凭据** | 否决。工具必须是受控 API，而不是「模型 + 连接串」。 |
| **放弃厂商 tools 只留 MCP** | 现阶段否决「唯一」。许多推理 API 原生 tools 延迟与贴合度仍最好，可双轨。 |

## 最终怎么解

**能力下沉为稳定业务 API；适配层可多协议。**

```
[业务服务 / 只读与幂等写 API]
        ↑
[Tool Gateway：鉴权·限流·审计·幂等键]
        ↑
   ┌────┼────┐
OpenAI Tools  MCP Server  内部 SDK
（会话内调用） （跨宿主）  （Java Bean）
```

| 协议 | 优点 | 缺点 | 什么场景选谁 |
|------|------|------|--------------|
| **OpenAI-compatible Tools** | 与聊天 API 原生、延迟友好、生态熟 | 跨宿主发现弱、易项目内复制 | 单产品内 Agent、快速迭代 |
| **MCP** | 跨宿主复用、资源/工具/提示统一、适合桌面与多客户端 | 运维进程、版本与安全模型要认真做 | 同一工具要进 IDE + 多人 Agent + 本地助手 |
| **自定义 HTTP/OpenAPI 网关** | 企业鉴权、审计、SLA 成熟 | 每个 Agent 框架要写适配器 | **所有写操作与核心读的底层真相** |

Spring AI 场景：ChatClient tools / FunctionCallback 对接网关；MCP 客户端用来接入已有 Server；**不要**让模型直接碰数据源。细节姊妹仓：[spring-ai-lab](https://github.com/jianwen049-hub/spring-ai-lab)

CLI：`python3 -m stack_lab.cli compare protocols`

### 常见踩坑

1. **Schema 与真实校验不一致** → 模型以为参数合法，网关 400；要用同一份 JSON Schema / OpenAPI 生成。
2. **工具描述写成小说** → 模型乱调用；描述要短、边界要硬（「仅查询、不退款」）。
3. **超时与部分失败** → 必须幂等键；MCP / HTTP 都一样。
4. **把 prompt 当权限** → 「不要调用删除」不是安全控制。
5. **本地 MCP 默认信任** → 桌面场景仍要用户确认高危工具。

## 用到的具体 skill / 技巧清单

| Skill | 用法 |
|-------|------|
| **业务 API 为真相** | 协议只是适配 |
| **双轨适配** | 会话内 tools + 跨宿主 MCP |
| **网关统一鉴权** | OAuth/mTLS/服务账号，不进 prompt |
| **幂等键** | 所有写工具强制 |
| **精短 tool description** | 动词边界写清 |
| **Schema 单一来源** | OpenAPI → tools / MCP 生成 |

## 代码 / 表解析

### `matrix.py` → `protocols`

选项 `openai_tools` / `mcp` / `http_gateway` 的 pros/cons/best_for/watchouts。

### `recommend`

痛点含 `ide`/`cursor`/`跨应用` → 提高 MCP；含 `java`/`spring`/`网关` → 强调 HTTP gateway 为底层。

---

**一句话**：MCP 很重要，但**赢在复用与宿主边界**；写操作的胜负手永远是网关、鉴权与幂等。
