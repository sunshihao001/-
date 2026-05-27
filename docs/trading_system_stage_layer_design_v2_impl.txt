# SIKK-GMGN v2 实施版：10 Skill × 8 层 × 5 Gate

> 理论基础：`trading_system_stage_layer_design_v2.md`（8 层否定门禁 + Meyer/Leveson/Parnas 三层深化）
> 缺口分析：`v2_skill_gap_analysis.md`（7 Skill 的 15 类缺口）
> 本文件：实施版。将 7 Skill 拆为 10 Skill，建立 Parnas 数据边界，定义 5 Gate 顺序。

---

## 1. 拆分总览

```
原 7 Skill                         →  实施版 10 Skill
───────────────────────────────────────────────────────────
meme-candidate-entry               →  meme-candidate-entry         入口验证层
meme-token-panel                   →  meme-data-standardizer       层 1
(合并 candidate-entry 数据部分)

meme-wallet-roles                  →  meme-entity-clustering        层 2
meme-wallet-structure              →  meme-structure-evidence       层 3

meme-evidence-chain  ──拆分──→       meme-chip-control              层 4
                           →       meme-lifecycle-classifier       层 5
                           →       meme-behavioral-hypothesis      层 6

meme-trade-gate                    →  meme-final-gate               层 7
meme-workflow-controller           →  meme-workflow-controller      调度层
```

---

## 2. 10 Skill 逐一定义

### Skill 0：meme-candidate-entry

**职责**：验证入口合法性。回答"这个 token 能不能进流水线"。

**覆盖 v2 层**：入口层（非 8 层之一）

**输入**：用户提供的 token 地址 + 来源 + 原因

**输出**：
```text
candidate_entry.json
  - status: PASS | BLOCK | ERROR
  - token_address, chain, entry_source, entry_reason
  - initial_validation（地址格式 / token 存在 / 有池子 / 有流动性 / 未在 bonding curve）
  - confidence_score, missing_fields
  - handoff_to: meme-data-standardizer
```

**判断规则**：地址格式 base58 / token 存在 / 有交易池 / liquidity > 0

**数据归属**：不调 GMGN 除 token info 以外的 API。只做入口验证。

---

### Skill 1：meme-data-standardizer

**职责**：**层 1 的唯一 GMGN 调用入口**。拉取所有原始数据，标准化为统一 Schema，输出完整性报告。在此 Skill 之后，任何 Skill 不再直接调用 GMGN API。

**覆盖 v2 层**：层 1（数据标准化层）

**GMGN 命令（所有原始数据调用集中在此）**：
```bash
gmgn-cli token info / security / pool / kline
gmgn-cli token holders / traders（所有 tag）
gmgn-cli portfolio created-tokens / stats
gmgn-cli portfolio activity
```

**输出（标准化文件）**：
```text
standardized_token_context.json
standardized_wallet_snapshot.json
standardized_kline_volume.json
standardized_liquidity.json
standardized_history.json

+ completeness_report:
  - completeness_ratio: 0.0-1.0
  - confidence_score: 0.0-1.0
  - time_window_coverage_pct: 0.0-1.0
  - missing_fields: []
  - degradation_level: FULL | PARTIAL | MINIMAL | CRITICAL
```

**Parnas 边界**：此 Skill 是 GMGN 原始字段的**唯一消费者**。层 2+ 只读标准化文件，不读 GMGN raw JSON。

**退化**：
- GMGN 接口不可用 → `completeness_ratio` 降低，上层读此指标
- 字段缺失 → 填 null + 标记 `missing`
- `degradation_level = CRITICAL` → 暂停后续分析

---

### Skill 2：meme-entity-clustering

**职责**：地址归并为实体簇，识别钱包角色。输出 entity cluster ID，不是孤立地址列表。

**覆盖 v2 层**：层 2（地址实体归并层）

**输入**：只读层 1 的标准化文件（`standardized_wallet_snapshot.json` + `standardized_token_context.json`）

**输出**：
```text
wallet_entity_groups.json        ← 地址 → entity_cluster_id 映射
same_source_groups.json          ← 同源组 + 成员 + 置信度
wallet_classification.json       ← 角色标签
distribution_path_graph.json     ← Token 分发路径
funding_source_graph.json        ← 资金来源路径

+ entity_merge_completeness: 成功归并数 / 总输入地址数
```

**Invariant**：一个地址永不归属两个实体簇。

**Parnas 边界**：不调 GMGN API。只读层 1 输出。如果层 1 `completeness_ratio < 0.7`，本层角色分类置信度降低。

---

### Skill 3：meme-structure-evidence

**职责**：判断钱包行为是否构成结构性控制。输出证据强度分级 + 刷量 B0-B4 评分。

**覆盖 v2 层**：层 3（结构地址证据层）

**输入**：层 2 的 entity clusters + 层 1 的标准化快照 + 历史地址库

**输出**：
```text
structure_evidence.json
  - structure_evidence_status: STRONG | MEDIUM | WEAK |
                               FALSE_POSITIVE | INVALIDATED | CONFLICTING
  - early_wallet_remaining_ratio
  - same_source_group_remaining_ratio
  - full_exit_count / partial_exit_count
  - distribution_receiver_count
  - backflow_address_count
  - historical_reappearance_count
  - wash_trading_level: B0 | B1 | B2 | B3 | B4  ← 取代 is_wash_trading boolean
  - supporting_evidence[]
  - counter_evidence[]
  - alternative_explanations[]

+ evidence_completeness: 产生有效证据的实体簇数 / 总实体簇数
```

**退化**：
- `completeness_ratio < 0.7` → 严格模式：只输出通过置信度检验的断言，其余 `EVIDENCE_INSUFFICIENT`
- 数据严重缺失 → `structure_evidence_status = INVALIDATED`

**Parnas 归属**：同源组阈值、刷量算法 B0-B4 的判定逻辑属于本层。

---

### Skill 4：meme-chip-control

**职责**：判断筹码控制权状态——不是"有没有货"，而是"控制权处于什么状态"。

**覆盖 v2 层**：层 4（筹码控制权状态层）

**输入**：层 3 的证据链 + 层 2 的实体簇

**输出**：
```text
chip_control_status.json
  - chip_control_status: ESTABLISHING | ESTABLISHED | MAINTAINED |
                         LOOSENING | TRANSFERRING | COLLAPSED | UNKNOWN
  - chip_control_retention_score       ← 控制权保留分
  - structure_exit_intensity_score     ← 结构侧撤退分
  - counterparty_pressure_score        ← 对手盘压力分
  - distribution_progress_score        ← 派发进度分
  - control_invalidation_risk          ← 控制权失效风险
  - per_entity_control_weight[]        ← 每个实体的筹码权重
  - per_entity_veto_count              ← 否决票数

+ control_assessment_completeness
```

**Invariant**：已清仓实体的控制权权重恒 0。总权重归一化到 [0,1]。

**退化**：层 3 输出 `EVIDENCE_INSUFFICIENT` → 本层 `chip_control_status = UNKNOWN`，`confidence_score` 降级。

---

### Skill 5：meme-lifecycle-classifier

**职责**：场景分类。判断当前 token 处于什么生命周期阶段，输出场景标签和动作方向。

**覆盖 v2 层**：层 5（主导侧生命周期层）

**输入**：层 4 的控制权状态 + 层 3 的证据链 + 层 1 的 K 线/成交量/市值标准化数据

**输出**：
```text
lifecycle_classification.json
  - primary_scene            ← 从 14 场景表中取值
  - secondary_scenes[]
  - scene_confidence
  - lifecycle_stage

+ lifecycle_coverage（有足够数据做场景判断的时间窗口占比）
```

**14 场景 × 动作映射表**：

```text
SCENE_ACCUMULATION              → WATCH
SCENE_MARKUP_VALID              → HIGH_PRIORITY_WATCH / PAPER_READY
SCENE_SECOND_LEG_EXPANSION      → PAPER_READY / WAIT_CONFIRMATION
SCENE_HIGH_DISTRIBUTION         → BLOCK / EXIT_MONITOR
SCENE_DOWNTREND_REDISTRIBUTION  → BLOCK
SCENE_BULL_TRAP_REBOUND         → BLOCK / EXIT_MONITOR
SCENE_EXIT_LIQUIDITY_TRAP       → BLOCK
SCENE_FAKE_BASE_AFTER_DIST      → PAUSE / BLOCK
SCENE_REACCUMULATION_CONFIRMED  → HIGH_PRIORITY_WATCH / PAPER_READY
SCENE_FINAL_EXIT_PUMP           → BLOCK / EXIT_MONITOR
SCENE_LONG_ACCUM_REACTIVATION   → WATCH / PAPER_READY
SCENE_DEEP_WASH_REVERSAL        → HIGH_PRIORITY_WATCH
SCENE_CONTROL_BOX_BREAKOUT      → PAPER_READY
SCENE_DEAD                      → IGNORE
```

**刷量过滤**：`wash_trading_level >= B3` → 放量突破不能判定为有效突破，只允许 WATCH/BLOCK。

**退化**：层 4 `UNKNOWN` → 场景标记 `PHASE_UNVERIFIED`；时间快照覆盖 < 50% → 不能判定吸筹，只能用 `POSSIBLE_` 前缀。

---

### Skill 6：meme-behavioral-hypothesis

**职责**：推断主导侧行为动机，但不声称知道意图。每条假设带置信度和反证。

**覆盖 v2 层**：层 6（行为动机假设层）

**输入**：层 5 的场景分类 + 层 4 的控制权状态 + 层 3 的证据链

**输出**：
```text
behavioral_hypothesis.json
  - dominant_side_intent_hypothesis   ← 合法表达模板
  - intent_confidence
  - supporting_evidence[]
  - counter_evidence[]
  - alternative_explanations[]        ← 替代解释（至少 1 条）
  - invalidation_conditions[]         ← 什么情况下本假设失效
  - next_observation_points[]

+ intent_coverage
```

**合法表达模板**（禁止声称知道意图）：
```text
✅ 疑似主导侧仍在保留筹码
✅ 疑似主导侧正在制造流动性
✅ 疑似主导侧存在二次扩张动机
✅ 疑似主导侧进入主动派发
✅ 疑似主导侧正在通过反抽吸引接盘

❌ 庄家一定要拉
❌ 庄家肯定会出货
❌ 庄家在想什么
```

**Invariant**：所有概率在 [0,1] 区间。

**退化**：层 5 仅给候选场景 → 本层只输出多假设并列。

---

### Skill 7：meme-final-gate

**职责**：综合所有上游输出，执行一票否决、冲突裁决、刷量降级，输出最终推荐动作。

**覆盖 v2 层**：层 7（否定门禁与状态输出层）

**输入**：层 0-6 的全部输出

**输出**：
```text
scene_classification.json
recommended_action.json
invalidation_conditions.json
counter_evidence.json
workflow_summary.md
```

**14 个一票否决条件**（任意一条 → BLOCK）：

```text
V01  同源组同步清仓（same_source_group_full_exit = true）
V02  结构侧剩余持仓大幅下降（early_wallet_remaining_ratio < 阈值 && 下降速度 > 阈值）
V03  利润回收钱包集中出现
V04  高位接盘鲸鱼快速增加（trapped_whale_growth_rate > 阈值）
V05  Top Holder 集中度异常下降
V06  拉升后成交量放大但结构侧持续卖出（sell_while_pumping_ratio > 阈值）
V07  反抽期间结构侧继续派发
V08  市值已从发现时大幅扩张且无重新吸筹证据
V09  Honeypot（G01）
V10  Extreme Rug（G02）
V11  Unrenounced mint + freeze（G03）
V12  High Tax > 10%（G04）
V13  Wash Trading B4（G05 升级）
V14  Critical Structure + confidence >= 0.7（G06）
```

**6 条冲突裁决规则**：

```text
R1  SECURITY_BLOCK 优先级最高 → 所有买入模型失效
R2  wash_trading_level >= B3 → REAL_BREAKOUT 不成立 → FAKE_VOLUME_BREAKOUT
R3  反抽期间早期钱包/分发钱包卖出 → SECOND_LEG_EXPANSION 无效 → BULL_TRAP_REBOUND
R4  横盘无新结构钱包进入 → REACCUMULATION 不成立 → FAKE_BASE / PAUSE
R5  暴力拉升期间旧结构钱包卖出 → MARKUP_VALID → FINAL_EXIT_PUMP
R6  K 线强势但钱包派发强 → PAPER_READY 降级为 BLOCK 或 EXIT_MONITOR
```

**刷量 B0-B4 降级映射**：

```text
B0  正常判断
B1  正常判断，标记备注
B2  放量信号降权，不单独作为突破确认
B3  禁止把放量突破当作有效突破，只允许 WATCH/BLOCK
B4  高成交量信号失效，优先判定 BLOCK
```

**12 种最终状态**：

```text
IGNORE / DISCOVERED / WATCH / HIGH_PRIORITY_WATCH /
WALLET_SUPPORT / WALLET_PAUSE / WALLET_BLOCK /
PAPER_READY / PAUSE / BLOCK / EXIT_MONITOR / REVIEW_REQUIRED
```

**传递性失效链**：

```text
层 3 EVIDENCE_INSUFFICIENT
→ 层 4 confidence LOW
→ 层 5 PHASE_UNVERIFIED
→ 层 6 多假设并列
→ 层 7 forced downgrade（PAPER_READY → WATCH，WATCH → PAUSE）
```

---

### Skill 8：meme-workflow-controller

**职责**：纯调度。不参与业务判断。按顺序调度 Skill 0→7，管理 phase_state，恢复/超时/错误处理。

**覆盖 v2 层**：调度层

**执行顺序**：

```text
candidate-entry (入口验证)
    ↓ BLOCK? → 停止，输出 blocker_report
data-standardizer (层 1)
    ↓ CRITICAL degradation? → 暂停
entity-clustering (层 2)
    ↓
structure-evidence (层 3)
    ↓ Gate1: evidence_completeness > 0?
chip-control (层 4)
    ↓ Gate2: chip_control_status != UNKNOWN?
lifecycle-classifier (层 5)
    ↓ Gate3: scene_confidence >= threshold?
behavioral-hypothesis (层 6)
    ↓ Gate4: intent_coverage > 0?
final-gate (层 7)
    ↓ Final Gate: 一票否决 + 冲突裁决 + 刷量降级
workflow_summary.md 输出
```

**每个 Gate 输出**：

```text
{gate_name}_decision: PASS | PAUSE | DEGRADE | BLOCK
{gate_name}_confidence: 0.0-1.0
{gate_name}_degradation_reason: string
```

---

## 3. Parnas 数据边界（硬约束）

```text
┌──────────────────────────────────────────────────────────┐
│  GMGN API / Solana RPC                                    │
└────────────┬─────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────┐
│ meme-data-standardizer │  ← 唯一 GMGN 调用入口
│ 层 1                   │
│ 输出：标准化文件 ×5     │
│      + completeness    │
└───────┬────────────────┘
        │ 标准化 JSON（非 raw GMGN）
        ├──────────────┬──────────────┬──────────────┬──────────────┐
        ▼              ▼              ▼              ▼              ▼
   entity-        structure-      chip-         lifecycle-    behavioral-
   clustering     evidence        control       classifier    hypothesis
   层 2            层 3            层 4           层 5          层 6
        │              │              │              │              │
        └──────────────┴──────────────┴──────────────┴──────────────┘
                                        │
                                        ▼
                                  final-gate
                                  层 7

规则：任何 Skill（除 data-standardizer）不得直接读 GMGN raw JSON 或调 GMGN API。
     所有跨层通信通过上一层的结构化 JSON 文件。
     如果 GMGN 改字段名，只需改 data-standardizer，其他 8 个 Skill 不受影响。
```

---

## 4. 5 Gate 决策枢纽

```text
Gate1（层 3 → 层 4）
  问题：证据是否足够继续分析？
  输入：structure_evidence.json
  检查：evidence_completeness > threshold? 证据链非 EVIDENCE_INSUFFICIENT?

Gate2（层 4 → 层 5）
  问题：控制权是否仍在结构侧（或可判定）？
  输入：chip_control_status.json
  检查：chip_control_status != UNKNOWN?

Gate3（层 5 → 层 6）
  问题：当前场景允许什么动作方向？
  输入：lifecycle_classification.json
  检查：scene_confidence > threshold? primary_scene 非 PHASE_UNVERIFIED?

Gate4（层 6 → 层 7）
  问题：行为假设是否有足够置信度？
  输入：behavioral_hypothesis.json
  检查：intent_confidence > threshold? intent_coverage > 0?

Final Gate（层 7）
  问题：综合裁决——一票否决、冲突裁决、刷量降级、传递性失效降级
  输入：全部上游层输出
  输出：recommended_action + final_state
```

**Gate 失败的动作**：

```text
PASS     → 继续下一层
PAUSE    → 暂停，标记等待条件
DEGRADE  → 降低置信度继续，但记录降级原因
BLOCK    → 停止流水线，输出 blocker_report
```

---

## 5. grill-with-docs 验证层

**定位**：PM/review 终端的手动工具。不接入 pipeline 自动流程。

**触发时机（均由 PM 手动调用）**：
- v2 设计变更后 → 术语一致性挑战 + 契约可检查性挑战
- Pipeline 输出异常 → 契约符合性审计 + 术语漂移检测
- 重大决策点 → ADR 生成

**不在 workflow-controller 中触发。** 交接文件（workflow_summary.md）写清楚即可。PM 拿到觉得有问题，手动开 grill。

---

## 6. 完整性指标（每层输出必须携带）

```text
层 1：completeness_ratio + time_window_coverage_pct + degradation_level
层 2：entity_merge_completeness
层 3：evidence_completeness
层 4：control_assessment_completeness
层 5：lifecycle_coverage
层 6：intent_coverage
层 7：（汇聚所有上游指标 + recommended_action confidence）
```

---

## 7. 版本对照

```text
v1：12 阶段 + 9 层 + 7 Skill + 16 理论（四套体系，无统一映射）
v2：8 层否定门禁 + 7 Skill + 16 理论（统一映射，但 Skill 5 过载）
v2 实施版（本文件）：8 层 + 10 Skill + 5 Gate（Parnas 边界硬化，Meyer/Leveson 契约落地）
```
