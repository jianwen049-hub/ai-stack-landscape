# 03 · 检索栈:稀疏 / 稠密 / 混合,pgvector vs Qdrant vs Chroma,重排与 GraphRAG

> 对应矩阵层:`retrieval`(`python3 -m stack_lab.cli compare retrieval`)。选项 id:`sparse` / `dense` / `hybrid` / `contextual_chunks` / `graph_rag` / `store_faiss` / `store_chroma` / `store_pgvector` / `store_qdrant` / `store_managed` / `reranker`。姊妹仓:[hybrid-retrieval](https://github.com/jianwen049-hub/hybrid-retrieval) · [context-engineering](https://github.com/jianwen049-hub/context-engineering) · [ai-eval-lab](https://github.com/jianwen049-hub/ai-eval-lab)。

## 当时业务痛点

知识库上线两周,客服反馈两极:有的问题「秒准」,有的「答得像相关其实完全不是」。典型翻车:

- 用户甩 **订单号 / 政策编号**,向量检索漂到语义相近的旧政策。
- 用户问「退款多久到账」,同义表达很多,纯关键词又漏召回。
- top-5 里混进权限不该看的文档,答案一本正经泄密风险。
- 换了「更大 embedding 模型」账单涨了,差评率几乎不动。
- 用户问「对比一下 A 政策和 B 政策对所有华东代理商的要求」——多跳聚合题,向量检索把 A、B 两个文档片段各捞一条,答案开始编造中间的「对比」。

痛点本质:**召回目标混杂(精确 ID vs 语义意图 vs 多跳关系)**,却只用一路检索;**排序目标与生成目标脱节**(相关 ≠ 可引用、可授权);**切块丢失上下文**(代词指向前一页的定义)。

### 具体翻车现场(不是段子)

- **HNSW + 过滤塌方**:pgvector 上加了 `tenant_id = X` 前置过滤,召回率从 0.9 掉到 0.4——过滤后的候选集太小,HNSW 图导航直接失灵。教训:**过滤后的候选规模要压测,不是「能跑」就算过**。
- **向量库选型回炉**:小团队用 Chroma 起步,数据到千万级后内存与重建索引时间爆炸,被迫迁 pgvector/Qdrant,迁移期间双写对账。教训:**第一天就把「迁移成本」当选项字段**。
- **上下文增强救了 11 个点**:政策文档切块后满是「该条款」这种代词,稠密检索全靠猜;给每块加一句 LLM 生成的「本块在讲什么」的上下文头,Recall@10 直接抬升(矩阵 `contextual_chunks`)。教训:**切块质量是地基,先修地基再换更大的模型**。

## 当时怎么看这个问题

向量库营销话术容易让人以为「embedding 搞定搜索」。信息检索几十年经验是:稀疏与稠密互补,重排吃的是候选质量,生成吃的是重排后的可引用片段。工程上要分开优化 **Recall@k(候选)** 与 **Faithfulness / 引用正确率(生成)**。

2025–2026 的两条新争论线:

1. **pgvector vs Qdrant vs Chroma**:pgvector 的卖点是「与业务库一体」;Qdrant 的卖点是「过滤+ANN 是一等公民」;Chroma 的卖点是「今天就能跑」。选型其实是问:**你的查询里过滤占比多高、规模多大、谁值夜班**。
2. **GraphRAG 什么时候值**:知识图谱增强不是更高级的 RAG,是**另一条腿**——专答多跳与聚合问题;点查场景它又贵又慢。

## 试过什么

1. **只用稠密 + FAISS/Chroma**:语义题尚可;ID / 型号 / 错误拼写惨。
2. **只用 BM25 / 倒排**:专有名词强;同义改写弱。
3. **线性加权稀疏分 + 稠密分**:量纲不同,调参玄学。
4. **RRF(倒数排名融合)再交叉编码器重排**(`hybrid` + `reranker`):更稳;重排模型贵、要控候选宽度。
5. **上下文增强切块**(`contextual_chunks`):索引期给每块生成一句「上下文摘要」头;索引期多一遍 LLM 成本,换查询期两路召回同时受益。
6. **GraphRAG**(`graph_rag`):实体/关系抽取建图,多跳聚合题答得出;抽取管线要维护,实体漂移要监控;点查不如向量。
7. **托管向量库一把梭**:运维省心;索引策略、混合检索、权限过滤仍要自己设计。
8. **pgvector 塞进业务 Postgres**:事务与备份统一;超大规模 ANN 与隔离要评估。
9. **Qdrant 独立部署**:过滤性能与量化选项强;多一个要值夜班的数据存储,与业务库的一致性自己管。

## 为什么否决

| 选项 | 原因 |
|------|------|
| **稠密替代稀疏** | 否决。精确匹配场景不可丢。 |
| **分数直接相加当融合** | 否决默认做法。不同路分量纲与分布差一个数量级。 |
| **重排吃全库** | 否决。交叉编码器只能吃小候选集(如 50~200)。 |
| **「换更大向量模型」当银弹** | 否决。先修切块、元数据过滤、混合与评测集。 |
| **无权限过滤的统一索引** | 否决上生产。检索层必须能按租户/角色裁剪。 |
| **GraphRAG 替代向量** | 否决。图谱是补充腿,点查仍靠混合检索;两条腿都要评测集。 |
| **Chroma 直接上生产** | 否决用于有合规与规模预期的场景;它最好的角色是原型与单机实验。 |

## 最终怎么解

推荐默认管道(可按规模裁剪):

```
查询理解(改写/纠错,可选)
  → 并行:稀疏召回 ‖ 稠密召回(各路带元数据过滤)
  → 融合(优先 RRF)→ 去重
  → 重排(交叉编码器或业务规则)
  → 上下文组装(引用、长度预算)→ 生成
```

切块策略:标题路径 + 滑窗重叠;代词密集的语料加**上下文增强头**(`contextual_chunks`);关系密集的语料(组织结构、法规映射)在混合检索旁边挂 **GraphRAG 腿**(`graph_rag`)。

### 向量存储对比(摘要)

| 选项 | 优点 | 缺点 | 什么场景选 |
|------|------|------|------------|
| **FAISS(本地)**(`store_faiss`) | 快、可控、实验友好 | 自管持久化/复制 | 单机实验、批建索引 |
| **Chroma(嵌入式)**(`store_chroma`) | 上手快、零额外基建 | 生产韧性与治理要自补 | Proto / 小团队 |
| **pgvector**(`store_pgvector`) | 与业务库一体、SQL 过滤强、备份/HA 一套故事 | 极大规模 ANN、写吞吐与索引调参 | 中小规模、强过滤、已有 Postgres 运维 |
| **Qdrant**(`store_qdrant`) | 过滤+ANN 一等公民、量化选项、可自托管 | 多一个存储要值夜班;跨库一致性自理 | 向量重负载、pgvector 调参救不回来时 |
| **托管向量库**(`store_managed`) | 省运维、常带混合检索 | 成本、锁商、合规出境 | 要快速生产、团队小 |

**pgvector vs Qdrant 的实战判据**(被问最多的问题):

- 查询里 `WHERE tenant_id = ? AND type = ?` 这类**前置过滤占比 > 60%**,规模 < 千万块 → 先 pgvector,压测过滤后召回;不达标再上 Qdrant。
- 需要和业务表 **join**(检索结果直接关联订单/客户行)→ pgvector,除非规模说明不行。
- 团队没有 Postgres 深夜值班能力,但愿意养一个专用引擎 → Qdrant(自托管或云)。
- 谁都不想值夜班 → 托管,但把 ACL 与混合查询设计攥在自己手里。

### 检索范式

| 范式 | 优点 | 缺点 | 场景 |
|------|------|------|------|
| 稀疏 BM25(`sparse`) | 精确、可解释 | 同义弱 | ID、型号、法规条款号 |
| 稠密 embedding(`dense`) | 语义、多语言 | 精确弱、要语料匹配 | 自然语言意图 |
| 混合 + RRF(`hybrid`) | 互补稳 | 管道复杂 | **默认生产** |
| 上下文增强切块(`contextual_chunks`) | 修代词/歧义,两路召回都受益 | 索引期 LLM 成本 | 政策/长文档等切块敏感语料 |
| GraphRAG(`graph_rag`) | 多跳与聚合题 | 抽取维护成本、点查不占优 | 关系密集语料、本体明确 |
| 重排(`reranker`) | 提精准 | 贵、增延迟 | 候选≥20 且质量敏感 |

CLI:`python3 -m stack_lab.cli compare retrieval`

姊妹仓:[hybrid-retrieval](https://github.com/jianwen049-hub/hybrid-retrieval) · [context-engineering](https://github.com/jianwen049-hub/context-engineering)

## 用到的具体 skill / 技巧清单

| Skill | 用法 |
|-------|------|
| **先元数据过滤再 ANN** | 租户/时间/类型裁剪,缩小污染;**过滤后召回要压测** |
| **RRF 优于裸分数相加** | 用排名融合避开量纲 |
| **切块服务引用** | 块太大难定位,太碎丢上下文;代词密集就上上下文增强头 |
| **黄金集分意图** | ID 类 / 语义类 / 多跳类分开算召回 |
| **重排宽度与延迟预算** | k_retrieve 与 rerank 模型级联选型 |
| **权限在检索层执行** | 不靠模型「不要泄露」 |
| **图谱腿独立评测** | 多跳题集单独算 GraphRAG 的胜率,别混进普通题 |
| **第一天写迁移脚本** | 向量库选型把「将来换家」的成本当作字段 |

## 代码 / 表解析

### `matrix.py` → `retrieval`

含 `sparse` / `dense` / `hybrid` / `contextual_chunks` / `graph_rag` / `store_faiss` / `store_chroma` / `store_pgvector` / `store_qdrant` / `store_managed` / `reranker` 行;`store_qdrant` 的 watchouts 直接写着「业务真相留在 SQL」,提醒架构边界。

### `recommend.py`

痛点串里 `pgvector`/`postgres` → pgvector,`qdrant` → Qdrant,`多跳`/`图谱` → GraphRAG 腿,`切块` → 上下文增强;向量库三家争论因此在推荐输出里同时可见。

### 评测怎么挂

离线:固定 query 集算 Recall@k / nDCG,**分意图切片**(ID 类 / 语义类 / 多跳类);在线:引用点击、人工抽检、答案与片段重合——见 05 与 [ai-eval-lab](https://github.com/jianwen049-hub/ai-eval-lab)。组装进上下文的预算与裁剪策略见 [context-engineering](https://github.com/jianwen049-hub/context-engineering)。

---

**一句话**:检索是 **多路召回 + 融合 + 重排 + 权限** 的系统,不是「一个向量库 API」;向量库选型答的是**过滤占比、规模与值班表**,GraphRAG 是给多跳题加的一条腿,不是替代品。