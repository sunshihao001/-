# SIKK-GMGN 统一结构设计 v2.0

文件路径：`/root/sikk-gmgn/docs/trading_system_stage_layer_design_v2.md`

前置文档：`/root/sikk-gmgn/docs/trading_system_stage_layer_design.md`（v1 阶段设计，保留为历史参考）

---

## 1. Summary

以 **8 层否定门禁**为主骨架，**12 阶段**降级为每层内部的实例轨迹，**7 个 Skill**映射为各层的数据管道实现，**16 篇学习理论**按层归属挂载。

系统核心操作从"抽象过滤 / 场景分类"转为"否定优先"：先排除不可做，再讨论可做。

---

## 2. Motivation

v1 存在四套独立体系（12 阶段、9 层抽象、7 Skill、16 理论），彼此没有统一映射，导致每次新建 Skill 或补一篇理论都飘在四套体系之间。

Meme 市场存在极端不对称：**错过机会 < 踩中毒 token。** 因此优先用否定门禁（同源组清仓、结构侧崩塌、高位接盘），将 Type II 误差方向从"错过机会"移向"避免损失"。

否定条件比"场景分类"更耐时间——新场景出现时不需要推翻已有分类，只需要新增否定条件。

---

## 3. Non-Goals

- 不重写 7 个 Skill 代码
- 不改 Gate 规则 JSON 逻辑
- 不修改 AGENTS.md 安全边界
- 不定义具体数学阈值（属于后续 sample calibration）
- 不改变 paper-only 安全级别

---

## 4.  层否定门禁主骨架

### 4.0 层 0：系统宪法层

**职责**：定义系统能说什么、不能说什么、输出什么、禁止输出什么。

**Precondition**：交易 `tx` 是合法 Solana 字节串，签名可验证。调用者（外部触发：用户/控制器）对本层的调用必须在系统安全边界以内。

**Postcondition**：交易类型在宪法枚举内。输出宪法合规标记 `CONSTITUTIONAL / UNCONSTITUTIONAL`。

**Invariant**（即使退化也绝不违反）：无软分叉口。宪法规则修改必须走显式版本升级流程。

**输入**：外部触发（用户输入 token 地址、GMGN trending 推送、控制器调度）。

**输出**：
- `constitution_status: CONSTITUTIONAL | UNCONSTITUTIONAL`
- `safety_boundary: PAPER_ONLY`
- `language_constraint: FORBIDDEN_TERMS[]`（禁止称庄家、禁止绝对定性）
- `evidence_language_requirement: MUST_USE_PROBABLE_LANGUAGE`

**Completeness Indicator**：本层不依赖数据，完整性恒为 1.0。

**Accountability Chain**：无上游依赖。本层失效 = 系统配置错误。

**一票否决条件**：无。本层只做声明，不否决 token。

**退化路径**：不适用。宪法层无数据依赖。

**阶段轨迹**：阶段 0（系统边界定义）。

**挂载 Skill**：所有 Skill 执行前必须通过本层检查。

**挂载理论**：学习理论 00（系统总图）、SIKK 结构地址体系第 0 层。

**数据归属**：宪法规则常量、禁止术语表。

---

### 4.1 层 1：数据标准化层

**职责**：接收 GMGN / Solana RPC / K 线 / 成交量 / 换手率 / 历史地址库的原始字段，标准化为全系统统一的 Schema，并输出完整性指标。

**Precondition**：传入原始字段非空、类型匹配宪法层定义的 Schema。至少包含 token 地址和时间戳。

**Postcondition**：输出规范化结构（小数点对齐、时间戳归一化到 ISO8601、字段名统一）。不丢弃字段——不可得的字段显式填 null 并标记 `missing`。每条输出携带 `completeness_ratio`。

**Invariant**（即使退化也绝不违反）：不截断字段。不把 null 伪装成零值。字段来源可追溯。

**输入**：
- GMGN raw JSON（token info / security / pool / kline / holders / traders / trending / signal）
- Solana RPC 补查（资金来源、转账路径、token transfer）
- 历史地址库
- 多时间快照（开盘快照、候选发现快照、当前快照）

**输出**：
```text
standardized_token_context.json
standardized_wallet_snapshot.json
standardized_kline_volume.json
standardized_liquidity.json
standardized_history.json
+ completeness_report（包含以下指标）
  - completeness_ratio: 0.0-1.0
  - confidence_score: 0.0-1.0
  - time_window_coverage_pct: 0.0-1.0
  - missing_fields: []
  - degradation_level: FULL | PARTIAL | MINIMAL | CRITICAL
```

**Completeness Indicator**：由 `completeness_report` 承载，显式传递给所有上层。

**Accountability Chain**：本层输出完整性不足 → 责任在本层数据源接入逻辑。Schema 不符 → 责任在调用者未提供合法字段。

**一票否决条件**：无。

**暂停条件**：`degradation_level = CRITICAL` 时（如 token 地址无法解析、全字段为空），暂停后续分析。

**退化路径**：
- 字段缺失 → 填 null + 标记 `missing`
- 时间快照不完整 → `time_window_coverage_pct` 降低
- GMGN 接口不可用 → `completeness_ratio` 降低，上层必须读取此指标

**阶段轨迹**：阶段 1（新代币发现）、阶段 4 的数据部分。

**挂载 Skill**：`meme-candidate-entry`（数据采集部分）、`meme-token-panel`（数据采集部分）。

**挂载理论**：学习理论 02（GMGN 入口与候选代币池）、03（对标研究与字段体系）、05-08（GMGN 字段与价格发现学习模块）。

**数据归属**：GMGN 字段标准化 Schema、历史地址库结构、多快照时间轴定义。

---

### 4.2 层 2：地址实体归并层

**职责**：把单个钱包地址归并为实体组（同源组/分发组/回流组），识别钱包角色，输出实体簇 ID 而非孤立地址。

**Precondition**：输入地址为合法 Base58，校验和通过。标准化钱包数据由层 1 提供，`completeness_ratio > 0`。

**Postcondition**：返回实体簇 ID，同源地址归入同一簇。每个地址有角色分类标签。

**Invariant**（即使退化也绝不违反）：一个地址永不归属两个实体簇。

**输入**：层 1 输出的标准化钱包快照（买入时间、买入金额、资金来源、卖出时间、剩余持仓）。

**输出**：
- `wallet_entity_groups.json`（地址→实体簇 ID 映射）
- `same_source_groups.json`（同源组列表 + 成员 + 置信度）
- `wallet_classification.json`（地址角色标签：疑似新钱包狙击/疑似临时执行钱包/疑似同源执行组/疑似结构持仓钱包/疑似分发接收钱包/疑似派发钱包/疑似利润回收钱包/疑似对手盘鲸鱼）
- `distribution_path_graph.json`（Token 分发路径）
- `funding_source_graph.json`（资金来源路径）

**Completeness Indicator**：`entity_merge_completeness`（成功归并地址数 / 总输入地址数）。

**Accountability Chain**：地址格式非法 → 层 1 未履行标准化。实体簇 ID 重复 → 本层归并逻辑错误。

**一票否决条件**：无（本层只做归并，不否决）。

**退化路径**：GMGN 钱包标签不可靠时，角色分类置信度降低，`wallet_classification.json` 中标记 `confidence: LOW / UNVERIFIED`。

**阶段轨迹**：阶段 5（早期钱包与资金来源分析）的归并部分。

**挂载 Skill**：`meme-wallet-roles`（角色分类部分）、`meme-wallet-structure`（结构计算的本层前置）。

**挂载理论**：学习理论 10（钱包行为分析）、11（资金溯源与同源检测）、12（Sybil/Wash Trading/协调买入）。

**数据归属**：实体簇 ID 生成算法、同源组阈值配置、分发路径图结构。

---

### 4.3 层 3：结构地址证据层

**职责**：判断钱包行为是否真的构成结构性控制。不输出"结构存在/不存在"的二元结论，而是输出证据强度分级。

**Precondition**：实体簇 ID 存在、对应持仓数据可解析、层 2 输出的 `entity_merge_completeness > 0`。

**Postcondition**：输出带时间戳的证据链（持仓、换手、刷量指标、同源行为、派发路径），证据等级分为强/中/弱/伪阳性/失效/冲突。

**Invariant**（即使退化也绝不违反）：证据链非空（如果没有证据，输出 `EVIDENCE_INSUFFICIENT`，不输出空链）。

**输入**：层 2 的实体簇 + 层 1 的标准化钱包快照 + 历史地址库。

**输出**：
- `structure_evidence.json`
  - `structure_evidence_status: STRONG | MEDIUM | WEAK | FALSE_POSITIVE | INVALIDATED | CONFLICTING`
  - `early_wallet_remaining_ratio`（早期钱包剩余比例）
  - `same_source_group_remaining_ratio`（同源组剩余比例）
  - `full_exit_count / partial_exit_count`
  - `distribution_receiver_count`
  - `backflow_address_count`
  - `historical_reappearance_count`
  - `supporting_evidence[]`
  - `counter_evidence[]`
  - `alternative_explanations[]`

**刷量识别（B0-B4）由本层输出，不是层 1 或层 2**：刷量依赖钱包买入时序、交易密度、单笔金额——这些是层 1+2 提供的事实，但刷量判断本身是证据推断，属于本层职责。

**Completeness Indicator**：`evidence_completeness`（产生有效证据的实体簇数 / 总实体簇数）。

**Accountability Chain**：实体簇 ID 不存在 → 层 2 未履行归并。证据链空 → 本层推断逻辑不足。

**一票否决条件**：无（本层只提供证据，不做最终否决。否决权在层 7）。

**退化路径**：
- `completeness_ratio < 0.7` → 自动切换为严格模式——只输出通过置信度检验的断言，其余标记 `EVIDENCE_INSUFFICIENT`
- 钱包数据严重缺失 → `structure_evidence_status = INVALIDATED`，传递 `EVIDENCE_INSUFFICIENT` 给层 4

**阶段轨迹**：阶段 4（早期结构识别）、阶段 5（钱包与资金分析）、阶段 6（控盘箱体识别）的证据采集部分。

**挂载 Skill**：`meme-wallet-structure`（集中度/同源关系/可疑模式部分）、`meme-evidence-chain`（证据合成部分）。

**挂载理论**：学习理论 13（多信号融合与置信度）、15（GMGN 字段组合地基）、16（Gate 决策框架理论基石）。

**数据归属**：同源组阈值、刷量识别算法（B0-B4 评分模型）、证据强度分级的判断规则。

---

### 4.4 层 4：筹码控制权状态层

**职责**：判断"筹码控制权是否仍然在结构侧"——不是问"庄家有没有货"，而是问控制权处于什么状态。

**Precondition**：证据链包含活动实体、`evidence_completeness > 0`、证据链未处于 `INVALIDATED` 状态。

**Postcondition**：返回每个活动实体的筹码权重和控制权状态，总权重归一化到 [0,1]。

**Invariant**（即使退化也绝不违反）：已清仓实体的控制权权重恒 0。总权重 = 1.0。

**输入**：层 3 的结构证据链 + 层 2 的实体簇。

**输出**：
- `chip_control_status.json`
  - `chip_control_status: ESTABLISHING | ESTABLISHED | MAINTAINED | LOOSENING | TRANSFERRING | COLLAPSED | UNKNOWN`
  - `chip_control_retention_score`（控制权保留分）
  - `structure_exit_intensity_score`（结构侧撤退分）
  - `counterparty_pressure_score`（对手盘压力分）
  - `distribution_progress_score`（派发进度分）
  - `control_invalidation_risk`（控制权失效风险）
  - `per_entity_control_weight[]`
  - `per_entity_veto_count`

**Completeness Indicator**：`control_assessment_completeness`（有效参与控制权评估的实体数 / 应评估实体数）。

**Accountability Chain**：证据链空 → 层 3 未履行。权重计算错误 → 本层。

**一票否决条件**：无（本层判断控制权状态，不做否决）。

**退化路径**：
- 层 3 输出标记 `EVIDENCE_INSUFFICIENT` → 本层控制权状态标记 `UNKNOWN`，`confidence_score` 降级
- 传递性失效：层 3 证据不完整 → 本层控制权断言置信度自动降级为 `LOW`

**阶段轨迹**：阶段 7（筹码状态与派发进度判断）。

**挂载 Skill**：`meme-evidence-chain`（筹码控制权计算部分）。

**挂载理论**：学习理论 14（门控阈值与 Downgrade）、SIKK 结构地址体系第 4 层（筹码控制权状态层）。

**数据归属**：控制权状态的定义与过渡规则、筹码权重计算模型。

---

### 4.5 层 5：主导侧生命周期层

**职责**：判断当前代币处于什么生命周期阶段，输出场景标签和场景置信度。

**Precondition**：筹码控制权状态已确定、`chip_control_status != UNKNOWN`、总权重归一化、否决票数 ≥0。

**Postcondition**：输出主导场景 `primary_scene` + 可选次要场景 `secondary_scenes[]` + `scene_confidence`。

**Invariant**（即使退化也绝不违反）：已清仓实体的场景参与权重恒 0。

**输入**：层 4 的控制权状态 + 层 3 的证据链 + 层 1 的 K 线/成交量/换手率/市值标准化数据。

**输出**：
- `lifecycle_classification.json`
  - `primary_scene`（从下面场景表中取值）
  - `secondary_scenes[]`
  - `scene_confidence`
  - `lifecycle_stage`

**生命周期场景表**：

| 场景标签 | 中文 | 动作方向 |
|---|---|---|
| `SCENE_ACCUMULATION` | 疑似吸筹 | WATCH |
| `SCENE_MARKUP_VALID` | 真实拉升扩张 | HIGH_PRIORITY_WATCH / PAPER_READY |
| `SCENE_SECOND_LEG_EXPANSION` | 二段扩张候选 | PAPER_READY / WAIT_CONFIRMATION |
| `SCENE_HIGH_DISTRIBUTION` | 高位派发 | BLOCK / EXIT_MONITOR |
| `SCENE_DOWNTREND_REDISTRIBUTION` | 下跌再派发 | BLOCK |
| `SCENE_BULL_TRAP_REBOUND` | 诱多反抽 | BLOCK / EXIT_MONITOR |
| `SCENE_EXIT_LIQUIDITY_TRAP` | 退出流动性陷阱 | BLOCK |
| `SCENE_FAKE_BASE_AFTER_DISTRIBUTION` | 派发后假横盘 | PAUSE / BLOCK |
| `SCENE_REACCUMULATION_CONFIRMED` | 再吸筹确认 | HIGH_PRIORITY_WATCH / PAPER_READY |
| `SCENE_FINAL_EXIT_PUMP` | 末端拉盘派发 | BLOCK / EXIT_MONITOR |
| `SCENE_LONG_ACCUMULATION_REACTIVATION` | 长横盘再激活 | WATCH / PAPER_READY |
| `SCENE_DEEP_WASH_REVERSAL` | 深洗反转 | HIGH_PRIORITY_WATCH |
| `SCENE_CONTROL_BOX_BREAKOUT_RETEST` | 控盘箱体突破回踩 | PAPER_READY |
| `SCENE_DEAD` | 死亡盘 | IGNORE |

**刷量过滤规则**：`fake_volume_risk >= B3` 时，放量突破不能判定为 `REAL_BREAKOUT`，成交量放大不能作为强势信号。B3/B4 级刷量下只允许 WATCH 或 BLOCK。

**Completeness Indicator**：`lifecycle_coverage`（有足够数据做出场景判断的时间窗口占比）。

**Accountability Chain**：控制权状态未知 → 层 4 未履行。场景与生命周期明显不匹配 → 本层推断错误。

**一票否决条件**：无（本层只做分类，否决在层 7）。

**退化路径**：
- 层 4 标记 `UNKNOWN` → 本层场景标记 `PHASE_UNVERIFIED`，仅给出候选场景
- 层 1 时间快照不完整（`time_window_coverage_pct < 50%`）→ 本层不能判定吸筹阶段，只能给 `POSSIBLE_ACCUMULATION` 而不是 `SCENE_ACCUMULATION`

**阶段轨迹**：阶段 8（主导侧生命周期与行为意图判断）、阶段 9（K 线转强与策略适配）。

**挂载 Skill**：`meme-evidence-chain`（生命周期推断部分）、`meme-trade-gate`（策略适配预处理）。

**挂载理论**：学习理论 04（链上本质思维工具箱）、SIKK 多模型场景识别体系 v1.0（第 6 层生命周期识别层）、下跌派发与反抽流动性陷阱模型（P0-P7 阶段映射）、2 段交易策略部分（条件 3-5）。

**数据归属**：生命周期场景→动作映射表、洗盘/诱多反抽/末端拉盘判断的硬条件规则。

---

### 4.6 层 6：行为动机假设层

**职责**：推断主导侧的行为动机，但不声称知道意图。每条假设必须带置信度和反证。

**Precondition**：实体存活状态和生命周期阶段已确定。场景分类完成。

**Postcondition**：输出每实体假设违规概率（基于换手率突变、结构侧崩塌、高位接盘鲸鱼增加），每条假设必须带 `confidence`、`supporting_evidence`、`counter_evidence`。

**Invariant**（即使退化也绝不违反）：所有概率在 [0,1] 区间。不能声称知道"意图"，只能输出"假设"。

**输入**：层 5 的场景分类 + 层 4 的控制权状态 + 层 3 的证据链。

**输出**：
- `behavioral_hypothesis.json`
  - `dominant_side_intent_hypothesis`（合法表达：疑似主导侧仍在保留筹码 / 正在制造流动性 / 存在二次扩张动机 / 进入主动派发 / 正在通过反抽吸引接盘）
  - `intent_confidence`
  - `supporting_evidence[]`
  - `counter_evidence[]`
  - `alternative_explanations[]`（替代解释）
  - `invalidation_conditions[]`（失效条件）
  - `next_observation_points[]`

**禁止输出**：庄家一定要拉 / 庄家肯定会出货 / 庄家在想什么。

**Completeness Indicator**：`intent_coverage`（能生成假设的实体数 / 总活动实体数）。

**Accountability Chain**：场景未分类 → 层 5 未履行。假设概率超出 [0,1] → 本层计算错误。

**退化路径**：层 5 仅给候选场景 → 本层只输出多假设并列，不做单一假设推定。

**阶段轨迹**：阶段 8（行为意图判断部分）。

**挂载 Skill**：`meme-evidence-chain`（行为推断部分）。

**挂载理论**：SIKK 结构地址体系第 6 层（行为动机假设层）、2 段交易策略部分（认知升级 2：拉升对结构方的经济意义）。

**数据归属**：行为假设的合法表达模板、假设→置信度的计算规则。

---

### 4.7 层 7：否定门禁与状态输出层

**职责**：综合所有上游层的输出，执行一票否决、冲突裁决、刷量降级，输出最终状态和推荐动作。这是系统的最终决策层。

**Precondition**：假设概率已计算。所有上游层输出就绪。

**Postcondition**：构造否定凭证，任一票否决条件触发则锁定交易。输出 `recommended_action` + `final_state` + 完整证据摘要。

**Invariant**（即使退化也绝不违反）：否决后不可撤销（同一快照周期内）。任何成交量信号必须经过刷量过滤后才能作为有效放量信号。

**输入**：层 0-6 的全部输出。

**输出**：
- `scene_classification.json`（见下方 Schema）
- `recommended_action.json`
- `invalidation_conditions.json`
- `counter_evidence.json`
- `workflow_summary.md`（人类可读）

**JSON Schema（核心部分）**：

```json
{
  "token_address": "string",
  "token_symbol": "string",
  "snapshot_time": "ISO8601",
  "primary_scene": "SCENE_BULL_TRAP_REBOUND",
  "secondary_scenes": ["SCENE_DOWNTREND_REDISTRIBUTION"],
  "scene_confidence": 0.82,
  "recommended_action": "BLOCK",
  "scores": {
    "security_risk_score": 0.0,
    "structure_evidence_score": 0.0,
    "chip_control_score": 0.0,
    "distribution_risk_score": 0.0,
    "trap_risk_score": 0.0,
    "fake_volume_risk_score": 0.0,
    "market_structure_score": 0.0,
    "liquidity_quality_score": 0.0,
    "strategy_fit_score": 0.0,
    "historical_recurrence_score": 0.0
  },
  "supporting_evidence": [],
  "counter_evidence": [],
  "invalidation_conditions": [],
  "next_observation_points": []
}
```

**最终状态定义**：

| 状态 | 含义 |
|---|---|
| `IGNORE` | 不关注 |
| `DISCOVERED` | 已发现 |
| `WATCH` | 观察 |
| `HIGH_PRIORITY_WATCH` | 重点观察 |
| `WALLET_SUPPORT` | 钱包结构支持继续观察 |
| `WALLET_PAUSE` | 钱包结构矛盾，暂停 |
| `WALLET_BLOCK` | 钱包结构明显风险，阻断 |
| `PAPER_READY` | 允许纸面交易 |
| `PAUSE` | 暂停等待确认 |
| `BLOCK` | 阻断 |
| `EXIT_MONITOR` | 退出监控 |
| `REVIEW_REQUIRED` | 数据冲突或不足，需要复查 |

**一票否决条件**（任意一条成立 → `BLOCK`）：

```text
- 同源组同步清仓（same_source_group_full_exit = true）
- 结构侧剩余持仓大幅下降（early_wallet_remaining_ratio < 阈值 且下降速度 > 阈值）
- 利润回收钱包集中出现
- 高位接盘鲸鱼快速增加（trapped_whale_growth_rate > 阈值）
- Top Holder 集中度异常下降
- 拉升后成交量放大但结构侧持续卖出（sell_while_pumping_ratio > 阈值）
- 反抽期间结构侧继续派发
- 市值已从发现时大幅扩张且无重新吸筹证据
- paper-only 边界：任何真实交易、swap、private key access → `BLOCK`
```

**暂停条件**（满足 → `PAUSE`）：

```text
- 结构侧部分卖出但仍保留筹码
- 长横盘但未放量确认
- 二段扩张证据不足
- 数据快照不足（completeness_ratio < 阈值）
- K 线结构和钱包结构冲突
- 成交量可能刷量但未确认（B2）
- Top Holder 变化异常但未形成派发路径
```

**冲突裁决规则**：

```text
规则 1：SECURITY_BLOCK 优先级最高。如果安全硬风险存在，所有买入模型失效。
规则 2：fake_volume_risk >= B3 → REAL_BREAKOUT 不能成立 → 降级为 FAKE_VOLUME_BREAKOUT。
规则 3：反抽期间早期钱包/分发钱包卖出 → SECOND_LEG_EXPANSION 无效 → 转为 BULL_TRAP_REBOUND。
规则 4：横盘无新结构钱包进入 → REACCUMULATION 不能成立 → 标记 FAKE_BASE / PAUSE。
规则 5：暴力拉升期间旧结构钱包卖出 → MARKUP_VALID 转为 FINAL_EXIT_PUMP。
规则 6：K 线强势但钱包派发强 → PAPER_READY 降级为 BLOCK 或 EXIT_MONITOR。
```

**刷量 B0-B4 降级规则**：

| 刷量等级 | 对策略的影响 |
|---|---|
| B0 无明显刷量 | 正常判断 |
| B1 轻微异常 | 正常判断，标记刷量备注 |
| B2 中度疑似 | 放量信号降权，不单独作为突破确认 |
| B3 高度疑似 | 禁止把放量突破当作有效突破，只允许 WATCH/BLOCK |
| B4 极高风险 | 高成交量信号失效，优先判定 BLOCK |

**传递性失效规则**（Leveson 原则 3 的实现）：

```text
层 3 证据不完整
→ 层 4 控制权断言置信度降级
→ 层 5 生命周期标记 PHASE_UNVERIFIED
→ 层 6 行为假设只输出多假设并列
→ 层 7 recommended_action 强制降级（PAPER_READY → WATCH，WATCH → PAUSE）
```

**阶段轨迹**：阶段 10（状态输出与后续监控）。

**挂载 Skill**：`meme-trade-gate`（门控判断核心逻辑部分）、`meme-workflow-controller`（状态机维护和流程调度）。

**挂载理论**：学习理论 16（Gate 决策框架理论基石）、SIKK 结构地址体系第 7 层（否定门禁层）、SIKK 多模型场景识别 v1.0 第 8 层（冲突裁决与动作映射）。

**数据归属**：一票否决条件阈值、冲突裁决规则引擎、刷量降级映射表、最终状态机定义。

---

## 5. 多模型场景识别挂载（层 5-7 详参）

已确认的场景识别体系（来自 SIKK 多模型场景识别 v1.0）按以下方式挂载：

**层 5 负责**：场景分类。输入来自层 3+4，输出场景标签和置信度。

**层 6 负责**：行为假设。输入来自层 5，输出动机假设和反证。

**层 7 负责**：冲突裁决 + 动作映射。输入来自层 5+6，输出推荐动作。

### 模型库 → 层映射

| 模型类别 | 挂载层 |
|---|---|
| 生命周期模型（吸筹/拉升/派发/再派发/再吸筹） | 层 5 |
| 陷阱模型（诱多反抽/退出流动性/死猫反弹/假横盘/末端拉盘/接盘鲸鱼） | 层 5+6 |
| 盘面成交模型（放量突破/刷量假突破/放量滞涨/缩量回踩/成交效率/换手过热） | 层 3+5 |
| 钱包结构模型（早期结构/同源组/分发接收/利润回流/历史复现） | 层 2+3 |
| 策略执行模型（二段扩张/长横盘再激活/深洗反转/控盘箱体突破/高位禁买） | 层 7 |
| 验证与风控模型（策略回测/纸面归因/交易成本/滑点风险/误判复盘） | 层 7 + 复盘层 |

---

## 6. 原 v1 9 层抽象 → v2 8 层映射表

| v1 层 | v2 层 | 变化 |
|---|---|---|
| 1 数据层 | 1 数据标准化层 | 职责更明确：标准化 + 完整性指标 |
| 2 安全过滤层 | 并入层 7 否定门禁 | 安全 BLOCK 是一票否决条件之一，不再独立成层 |
| 3 市场过滤层 | 并入层 7 否定门禁 | 市场硬风险是暂停/阻断条件之一 |
| 4 钱包事实层 | 2+3 地址实体归并层 + 结构地址证据层 | 原来一层承担了归并和证据两个职责 |
| 5 结构证据层 | 3 结构地址证据层 | 职责不变，但明确刷量识别归属本层 |
| 6 行为推断层 | 5+6 生命周期层 + 行为假设层 | 原来一层承担了分类和假设两个职责 |
| 7 盘面策略层 | 5 生命周期层（策略适配） | 不再独立，并入生命周期判断 |
| 8 状态机决策层 | 7 否定门禁与状态输出层 | 职责明确为最终裁决 |
| 9 解释与复盘层 | 层 7 的输出部分 + 后续闭环 | 复盘回灌到各层的规则更新 |

---

## 7.  映射矩阵

### 7.1 阶段 × 层矩阵

```text
          层0 层1 层2 层3 层4 层5 层6 层7
阶段 0     ●
阶段 1          ●
阶段 2                                      ●（安全过滤）
阶段 3                                      ●（市场过滤）
阶段 4          ●   ●   ●
阶段 5              ●   ●
阶段 6                  ●   ●   ●
阶段 7                  ●   ●
阶段 8                          ●   ●
阶段 9                          ●
阶段 10                                     ●
阶段 11                         （复盘回灌到各层规则）
```

### 7.2 Skill × 层矩阵

| Skill | 主挂载层 | 说明 |
|---|---|---|
| meme-candidate-entry | 层 1（数据采集）+ 层 2（角色初筛） | 入口 Skill，跨两层 |
| meme-token-panel | 层 1（数据拉取）+ 层 7（安全过滤） | 数据拉取在层 1，安全判定最终在层 7 |
| meme-wallet-roles | 层 2（角色分类） | 核心归属 |
| meme-wallet-structure | 层 3（结构证据） | 核心归属 |
| meme-evidence-chain | 层 3（证据合成）+ 层 4（控制权）+ 层 5（生命周期）+ 层 6（行为假设） | 最跨层 Skill——必须只通过层接口读数据，不直接读原始字段 |
| meme-trade-gate | 层 7（门控判断） | 核心归属 |
| meme-workflow-controller | 层 7（状态机） | 核心归属 |

### 7.3 理论 × 层矩阵

| 理论学习模块 | 主挂载层 |
|---|---|
| 01 总图 | 层 0 |
| 02 GMGN 入口与候选代币池 | 层 1 |
| 03 对标研究与字段体系 | 层 1 |
| 04 链上本质思维工具箱 | 层 5-6 |
| 05-08 GMGN 数据与安全 | 层 1 |
| 09-10 池子生命周期 | 层 5 |
| 11 资金溯源与同源检测 | 层 2 |
| 12 Sybil/Wash Trading | 层 3 |
| 13 多信号融合与置信度 | 层 3 |
| 14 门控阈值与 Downgrade | 层 7 |
| 15 GMGN 字段组合地基 | 层 3 |
| 16 Gate 决策框架理论基石 | 层 7 |

---

## 8. Gate 决策枢纽

Gate 不再是一层，而是层 3-7 之间的多个决策节点：

```text
层 3（结构证据）→ Gate1：证据是否足够？
层 4（筹码控制权）→ Gate2：控制权是否仍在结构侧？
层 5（生命周期）→ Gate3：当前场景允许什么动作？
层 6（行为假设）→ Gate4：假设是否有足够置信度？
层 7（否定门禁）→ Final Gate：综合裁决 + 冲突裁决 + 刷量降级 + 一票否决
```

每个 Gate 的输出不是"通过/不通过"的布尔值，而是：

```text
{gate_name}_decision: {PASS | PAUSE | DEGRADE | BLOCK}
{gate_name}_confidence: 0.0-1.0
{gate_name}_degradation_reason: string
```

---

## 9. Growth Rules（层和否定条件如何生长）

定义三个生长规则，确保 v2 不是一次性的分类系统，而是可生长的系统：

### 规则 1：插入新子层

当某一层的内部逻辑复杂度超过单层承载能力时，允许在层内插入子层。条件：

- 子层有明确的输入/输出接口，与相邻子层不共享数据结构
- 子层的 precondition 由上层子层满足，postcondition 满足下层子层的 precondition
- 插入后不改变该层对外暴露的接口契约

### 规则 2：新增否定条件

允许在层 7 的一票否决条件中新增条目。条件：

- 新条件必须有对应的证据来源（明确来自哪一层的哪个输出字段）
- 新条件必须经过 3 个历史样本验证
- 新增后必须补写对应的失效条件（什么情况下该否定条件本身不再成立）

### 规则 3：新增生命周期场景

允许在层 5 的场景表中新增场景。条件：

- 新场景不与已有场景形成判定冲突
- 新场景必须有对应的动作映射（WATCH/PAPER_READY/BLOCK/PAUSE）
- 新场景必须有至少 5 个历史样本支撑判定规则

---

## 10. Graduation Criteria

### Alpha：v2 文档完成

- 8 层每层定义完整（含契约、退化路径、数据归属）
- 阶段 × 层矩阵、Skill × 层矩阵、理论 × 层矩阵完成
- Gate 决策枢纽定义完成

### Beta：3 个真实 token 验证

- 3 个不同类型 token（二段候选 / 诱多反抽 / 高位派发）走完整 8 层流程
- 验证每层接口契约在真实数据下是否成立
- 验证退化路径是否在实际数据缺失时被触发

### Mock：延迟注入测试（Dijkstra 建议）

- 构造场景：安全数据比钱包数据延迟 30 秒到达
- 构造场景：同源组清仓信号比 K 线信号延后 1 分钟
- 验证层 7 在信息不完整时选择 `PAUSE` 而不是直接 `PAPER_READY`

### GA：全部 Skill 和理论无遗漏

- 7 个 Skill 全部能在 v2 结构中找到主挂载层
- 16 篇理论学习模块全部能归属到至少一个层
- 所有一票否决条件有对应的证据来源层

---

## 11. grill-with-docs 验证层（Governance Layer）

### 11.1 定位

`grill-with-docs` 不是 8 层数据管道的一部分。它是横跨设计和实施的**治理验证层**，在 v2 体系中的两个挂载点工作：

```
挂载点 A（设计冻结前）
  v2 设计草案 → grill-with-docs → 术语冲突报告 → CONTEXT.md 更新 → 设计修订 → 冻结

挂载点 B（每轮 Pipeline 执行后）
  8 层输出 → grill-with-docs → 契约符合性挑战 → 术语漂移检测 → ADR（如需要）
```

### 11.2 挂载点 A：设计冻结前（Design-Time Governance）

**触发时机**：v2 设计更新 / 新增层 / 新增否决条件 / 新增场景时

**grill-with-docs 执行**：

1. **术语一致性挑战**：扫描 v2 设计文档中所有术语，与 `CONTEXT.md` 的 Glossary 对照
   - 例：v2 用"筹码控制权"，CONTEXT.md 是否定义了这个术语？
   - 例：v2 用"否定门禁"，是否与 AGENTS.md 的安全边界措辞一致？

2. **契约可检查性挑战**：
   - 每个 precondition 是否有对应的检查代码（在 Skill 里）？
   - 每个 postcondition 是否有对应的输出字段？
   - 每个 invariant 是否在退化路径中被保护？

3. **模糊语言消除**：
   - "疑似"→ 要求定义置信度阈值
   - "大幅下降"→ 要求量化
   - "异常"→ 要求定义正常基线

**输出**：
- `CONTEXT.md` 更新（新增术语、修正冲突术语）
- `docs/specs.md` 冻结确认
- 需要 ADR 的决策点列表

### 11.3 挂载点 B：Pipeline 执行后（Run-Time Governance）

**触发时机**：每次 8 层 pipeline 完整执行后，PM/review 终端调用

**grill-with-docs 执行**：

1. **层间契约符合性挑战**：
   - 层 2 的输入是否只来自层 1 的标准化输出？（Parnas 违规检测）
   - 层 7 的否决条件是否都能追溯到具体的证据来源层？

2. **术语漂移检测**：
   - 层 5 输出用了"派发"，但 CONTEXT.md 定义的术语是"distribution/派发"——必须一致
   - 层 6 输出用了"庄家"→ 立即标记为违规（FORBIDDEN_TERMS 触发）

3. **完整性指标审计**：
   - 每层是否输出了 `completeness_ratio`？
   - 退化路径是否被实际触发？如果触发，上层是否正确响应？

4. **场景→动作映射一致性**：
   - `SCENE_HIGH_DISTRIBUTION` 是否始终映射到 `BLOCK`？
   - 有没有场景被映射到不该去的动作方向？

**输出**：
- `reports/grill_session_<timestamp>.md`（挑战发现 + 建议修正）
- `CONTEXT.md` 更新（如发现术语漂移）
- ADR（如发现需要重大设计调整）

### 11.4 与 Skill 体系的关系

```
                    ┌─────────────────────────┐
                    │  grill-with-docs        │ ← 治理验证层
                    │  (PM/review 终端调用)     │
                    └──────────┬──────────────┘
                               │ 挑战 + 审计
         ┌─────────────────────┼─────────────────────┐
         ↓                     ↓                     ↓
   ┌──────────┐    ┌──────────────┐    ┌──────────────┐
   │ v2 设计   │    │ 8 层 Pipeline │    │ CONTEXT.md   │
   │ 文档      │    │ (7-10 Skill)  │    │ specs.md     │
   └──────────┘    └──────────────┘    │ acceptance.md│
                                       └──────────────┘
```

**grill-with-docs 不替代 Skill**。它不拉数据、不计算、不输出 evidence。它只做一件事：**用文档（v2 设计 + CONTEXT.md）去拷问设计本身和实现输出的一致性**。

### 11.5 AGENTS.md 角色映射

在 sikk-gmgn 项目中，`grill-with-docs` 由 PM/review 角色调用：

```text
PM/review：
  1. 设计变更前 → grill-with-docs（挂载点 A）
  2. Pipeline 完成后 → grill-with-docs（挂载点 B）
  3. 术语冲突时 → 更新 CONTEXT.md
  4. 重大决策时 → 生成 ADR
```

### 11.6 与 Meyer / Leveson / Parnas 的对应

| 三位的方法论 | grill-with-docs 实现 |
|---|---|
| Meyer：契约必须可检查 | 逐层检查 precondition/postcondition 是否有对应实现 |
| Leveson：完整性指标 | 审计每层输出的 `completeness_ratio` 和退化路径 |
| Parnas：数据归属 | 检测任何 Skill 是否绕过层接口直接读原始字段 |

---

## 12. 版本历史

- v1.0：`/root/sikk-gmgn/docs/trading_system_stage_layer_design.md`（12 阶段 + 9 层，保留为历史参考）
- v2.0：本文件（8 层否定门禁主骨架，含契约/退化/归属的三层深化）
- v2.1：新增 §11 grill-with-docs 验证层（Governance Layer），包含设计冻结前和 Pipeline 执行后两个挂载点
