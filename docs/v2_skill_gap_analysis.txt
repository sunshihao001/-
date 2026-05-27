# 7 Skill → v2 8 层 缺口分析

> 对比基准：`trading_system_stage_layer_design_v2.md`
> 分析对象：`design/phase1-skill-01~07.md`
> 评价体系：Meyer 契约完整度 + Leveson 完整性指标 + Parnas 数据归属

---

## 1. 总览：7 个 Skill 对 8 层的覆盖率

```
v2 层              当前 Skill 覆盖度    状态
──────────────────────────────────────────────
层 0 系统宪法          ❌ 无           严重缺失
层 1 数据标准化         ⚠️ 部分         结构缺失
层 2 地址实体归并        ✅ 基本覆盖      细节不足
层 3 结构地址证据        ✅ 基本覆盖      缺少刷量 B0-B4
层 4 筹码控制权          ❌ 几乎无        严重缺失
层 5 生命周期 14 场景    ❌ 仅 7 行为      严重缺失
层 6 行为动机假设        ❌ 无结构化输出   严重缺失
层 7 否定门禁            ⚠️ 仅 6/14 否决   严重缺失
──────────────────────────────────────────────
Gate 决策枢纽 (5 Gate)  ❌ 仅 1 个 flat gate  严重缺失
传递性失效链             ❌ 无            缺失
冲突裁决 6 规则          ❌ 无            缺失
完整性指标体系            ⚠️ 部分         缺失
可归责性标注             ❌ 无            缺失
```

---

## 2. 逐层详细缺口

### 2.1 层 0 系统宪法层 — ❌ 完全缺失

**v2 要求**：所有 Skill 执行前通过宪法检查，输出：
- `constitution_status: CONSTITUTIONAL | UNCONSTITUTIONAL`
- `safety_boundary: PAPER_ONLY`
- `language_constraint: FORBIDDEN_TERMS[]`
- `evidence_language_requirement: MUST_USE_PROBABLE_LANGUAGE`

**现状**：
- Skill 5 底部有"禁止输出"列表，但只是备注文字，不是可执行的检查
- 没有 Skill 在执行前做宪法合规验证
- AGENTS.md 有安全边界声明，但没有被任何 Skill 程序化读入

**建议**：新增 Skill 0 `meme-constitution-gate`，嵌入所有 Skill 执行前。

---

### 2.2 层 1 数据标准化层 — ⚠️ 结构缺失

**v2 要求**：统一输出标准化文件 + 完整性报告：
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

**现状**：
- Skill 1 和 Skill 2 分别拉数据，各自输出自有格式
- Skill 2 直接输出 `token_panel.json`，不是标准化格式
- 三个关键指标缺失：`time_window_coverage_pct`、`degradation_level`、`completeness_ratio`
- 多时间快照（开盘快照 / 候选发现快照 / 当前快照）完全没有支持

**Parnas 违规**：Skill 2、3、4 都直接调用 GMGN API 读原始字段，没有统一的层 1 接口。GMGN 改字段名 = 3 个 Skill 同时改。

**建议**：合并 Skill 1+2 的数据采集部分为一个统一的 `meme-data-standardizer`，只在这个 Skill 里调 GMGN API。其他 Skill 只读标准化输出。

---

### 2.3 层 2 地址实体归并层 — ✅ 细节不足

**v2 要求**：输出 `entity_merge_completeness` 指标 + 角色分类

**现状**：
- Skill 3 做角色分类 ✅
- Skill 4 做同源检测 + 协调买入 ✅
- 缺少：`entity_merge_completeness`（成功归并数 / 总输入地址数）
- 缺少：`wallet_entity_groups.json`（地址→实体簇ID映射）
- 缺少：entity cluster ID 概念——当前用 `same_source_groups`，不是 entity cluster

**建议**：补充 entity cluster ID 概念和 `entity_merge_completeness` 指标。

---

### 2.4 层 3 结构地址证据层 — ✅ 缺少刷量分级

**v2 要求**：
- `structure_evidence_status: STRONG | MEDIUM | WEAK | FALSE_POSITIVE | INVALIDATED | CONFLICTING`
- 刷量 B0-B4 识别
- `evidence_completeness` 指标
- 退化：`completeness_ratio < 0.7` → 严格模式（只输出通过置信度检验的断言，其余标记 EVIDENCE_INSUFFICIENT）

**现状**：
- Skill 4 输出 `structure_risk` ✅ 但用 `low | medium | high | critical`，不是 v2 的 6 级证据状态
- Skill 2 输出 `is_wash_trading: boolean` —— 是/否，没有 B0-B4 分级
- 没有 `evidence_completeness`
- 没有严格模式退化

**建议**：
- 升级 Skill 2 的 `is_wash_trading` → B0-B4 分级
- Skill 4 增加 evidence_status 6 级

---

### 2.5 层 4 筹码控制权状态层 — ❌ 严重缺失

**v2 要求**：
```text
chip_control_status: ESTABLISHING | ESTABLISHED | MAINTAINED |
                     LOOSENING | TRANSFERRING | COLLAPSED | UNKNOWN
chip_control_retention_score
structure_exit_intensity_score
counterparty_pressure_score
distribution_progress_score
control_invalidation_risk
per_entity_control_weight[]
per_entity_veto_count
```

**现状**：Skill 5 完全没有这些字段。当前只输出 `dominant_behavior`（如 ACCUMULATION），没有任何控制权状态的语义。

**建议**：这是 v2 的核心判断层，**必须有独立 Skill**（建议从 Skill 5 拆出 `meme-chip-control`）。

---

### 2.6 层 5 生命周期 14 场景 — ❌ 仅 7 个行为标签

**v2 定义 14 场景**：
```
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

**Skill 5 只定义了 7 个行为**：
```
ACCUMULATION, DISTRIBUTION, WASH, CONTROLLED, EXIT, EARLY_STAGE, UNKNOWN
```

缺失 10 个场景。且 v2 的场景标签带了动作方向（WATCH / PAPER_READY / BLOCK），当前 Skill 没有这个映射。

**建议**：14 场景 + 动作映射需要完整实现在生命周期 Skill 中。

---

### 2.7 层 6 行为动机假设层 — ❌ 无结构化输出

**v2 要求**：
```text
dominant_side_intent_hypothesis（合法表达模板）
intent_confidence
supporting_evidence[]
counter_evidence[]
alternative_explanations[]
invalidation_conditions[]
next_observation_points[]
```

**现状**：Skill 5 有 `narrative.one_line` 和 `narrative.paragraph`，是文本摘要，不是结构化假设。缺失：替代解释、失效条件、下次观察点、per-entity 假设。

**Parnas 视角**：行为假设依赖层 5 场景 + 层 4 控制权 + 层 3 证据，但当前 Skill 5 直接读 Skill 2-4 的原始输出，没有层间契约。

**建议**：从 Skill 5 拆分 `meme-behavioral-hypothesis` 作为独立 Skill。

---

### 2.8 层 7 否定门禁 — ⚠️ 仅 6/14 否决 + 缺 4 个模块

**v2 定义 14 个一票否决条件**，Skill 6 只覆盖了 **6 个**：

| v2 否决条件 | Skill 6 |
|---|---|
| 同源组同步清仓 | ❌ |
| 结构侧剩余持仓大幅下降 | ❌ |
| 利润回收钱包集中出现 | ❌ |
| 高位接盘鲸鱼快速增加 | ❌ |
| Top Holder 集中度异常下降 | ❌ |
| 拉升后成交量放大但结构侧持续卖出 | ❌ |
| 反抽期间结构侧继续派发 | ❌ |
| 市值已从发现时大幅扩张且无重新吸筹证据 | ❌ |

**缺失模块**：
- 冲突裁决 6 规则 → ❌ 完全缺失
- 刷量 B0-B4 降级映射 → ❌ 只有 boolean
- 传递性失效链 → ❌ 缺失
- 最终状态 12 种 → ⚠️ Skill 6 只有 4 个 decision，v2 有 12 个 final_state

---

## 3. 架构层面缺口

### 3.0 grill-with-docs 验证层 — ❌ 挂载点缺失

v2 §11 定义了 `grill-with-docs` 的两个挂载点：

**挂载点 A：设计冻结前**
- 术语一致性挑战（v2 术语 vs CONTEXT.md Glossary）
- 契约可检查性挑战（每个 precondition 有代码？postcondition 有字段？）
- 模糊语言消除（"大幅下降"→量化）

**挂载点 B：Pipeline 执行后**
- 层间契约符合性挑战（Parnas 违规检测）
- 术语漂移检测（FORBIDDEN_TERMS 触发检查）
- 完整性指标审计（每层 completeness_ratio 存在？）
- 场景→动作映射一致性检查

**现状**：两个挂载点都不存在。目前没有：
- PM/review 终端在工作流中调用 grill-with-docs
- 设计变更时自动触发术语对照
- Pipeline 完成后自动触发契约符合性审计
- ADR 生成流程

**建议**：在 workflow-controller 中增加 grill-with-docs 触发点，PM/review 角色在以下时机必须调用：
1. v2 设计文档修改后
2. 每次完整 Pipeline 执行后
3. 新增/修改 Skill 后
4. CONTEXT.md 发现术语冲突时

### 3.1 Parnas 数据归属违规

当前数据流：
```
GMGN API → Skill 2 (token-panel)      ← 读原始字段
GMGN API → Skill 3 (wallet-roles)     ← 读原始字段
GMGN API → Skill 4 (wallet-structure) ← 读原始字段
```

v2 要求：
```
GMGN API → 层 1 (统一标准化) → 层 2 → 层 3 → 层 4 → 层 5 → 层 6 → 层 7
                                  ↑       ↑       ↑        ↑      ↑      ↑
                                只读层1 只读层1+2 只读层1+2+3 ……
```

### 3.2 Gate 决策枢纽 — 1 个 flat gate vs 5 个 sequential gate

**v2 要求 5 个 Gate**：
```
Gate1（层 3→层 4）证据是否足够？
Gate2（层 4→层 5）控制权是否仍在结构侧？
Gate3（层 5→层 6）当前场景允许什么动作？
Gate4（层 6→层 7）假设是否有足够置信度？
Final Gate（层 7）综合裁决 + 冲突裁决 + 刷量降级 + 一票否决
```

每个 Gate 输出：
```text
{gate_name}_decision: {PASS | PAUSE | DEGRADE | BLOCK}
{gate_name}_confidence: 0.0-1.0
{gate_name}_degradation_reason: string
```

**Skill 6 只有一个平铺的 gate**：读所有前置输出，一次性做 decision。

### 3.3 传递性失效链 — ❌ 缺失

```
v2 要求：
层 3 证据不完整
→ 层 4 控制权断言置信度降级
→ 层 5 生命周期标记 PHASE_UNVERIFIED
→ 层 6 行为假设只输出多假设并列
→ 层 7 recommended_action 强制降级 (PAPER_READY→WATCH, WATCH→PAUSE)
```

当前：每个 Skill 独立判断，没有层间传递。

### 3.4 Skill 5 (evidence-chain) 过载

一个 Skill 承担 4 层职责：层 3 证据合成 + 层 4 控制权 + 层 5 场景分类 + 层 6 行为假设。Parnas 原则指出"跨层读写原始字段是耦合"——Skill 5 不仅跨 4 层，还直接读 Skill 2-4 的原始 JSON，同时做业务逻辑。

### 3.5 Growth Rules — ❌ 无实现

v2 定义了 3 个 Growth Rules，但没有 Skill 支持（可延后到 GA）。

---

## 4. 建议方案

### 4.1 最小可行拆分（推荐：7 → 10 个 Skill + 1 个验证层）

```
原 Skill                          →  新 Skill                          覆盖层
──────────────────────────────────────────────────────────────────────────
(新增)                            →  meme-constitution-gate             层 0
meme-candidate-entry (数据部分)    →  meme-data-standardizer             层 1
meme-token-panel (数据部分)        →  (合并到上)                         层 1
meme-wallet-roles                  →  meme-entity-clustering             层 2
meme-wallet-structure              →  meme-structure-evidence            层 3
(从 evidence-chain 拆分)           →  meme-chip-control                  层 4
(从 evidence-chain 拆分)           →  meme-lifecycle-classifier          层 5
(从 evidence-chain 拆分)           →  meme-behavioral-hypothesis         层 6
meme-trade-gate (大幅扩展)         →  meme-final-gate                    层 7
meme-workflow-controller           →  meme-workflow-controller           调度层
meme-candidate-entry (入口验证)    →  meme-candidate-entry               入口层
(不新增 Skill，流程触发)           →  grill-with-docs                    Governance
                                        ├─ 挂载点 A：设计变更后触发
                                        └─ 挂载点 B：Pipeline 完成后触发
```

### 4.2 优先级

**P0（必须现在做，否则 v2 是纸上的设计）**：
1. 拆分 Skill 5
2. 补全 Skill 6 的 14 个否决条件
3. 实现 B0-B4 刷量分级（改 Skill 2 的 `is_wash_trading`）
4. 层 1 统一标准化接口

**P1（验证 MVP 前必须做）**：
5. Gate 决策枢纽 5 个 Gate
6. 冲突裁决 6 规则
7. 14 场景 + 动作映射
8. grill-with-docs 挂载点 A + B 接入 workflow-controller

**P2（可延后到 Beta）**：
9. 完整性指标体系（每个 Skill 补充 completeness_ratio 等）
10. 层 0 宪法检查
11. Growth Rules 实现

**P3（可延后到 GA）**：
12. 可归责性标注
13. 传递性失效链（硬编码逻辑）

### 4.3 不拆 Skill 5 的最低成本替代方案

保持 7 个 Skill 数量不变，在每个 Skill 内部增加字段：

| Skill | 需增加的字段/逻辑 |
|---|---|
| Skill 1 | `degradation_level`, `time_window_coverage_pct` |
| Skill 2 | `completeness_ratio`, B0-B4 `wash_level` (取代 `is_wash_trading`) |
| Skill 3 | `entity_merge_completeness`, entity cluster ID |
| Skill 4 | v2 的 6 级 `structure_evidence_status` |
| Skill 5 | 14 场景标签 + 控制权状态 + 行为假设结构化输出 + 替代解释 + 失效条件 |
| Skill 6 | 8 个缺失否决条件 + 冲突裁决 6 规则 + B0-B4 降级映射 + 12 最终状态 |
| Skill 7 | Gate 顺序化（不跳过 Gate 间传递性失效） |

**代价**：Skill 5 会膨胀到 400+ 行 JSON schema，Skill 6 同理。维护成本随时间指数增长。

---

## 5. 结论

**7 个 Skill 不够**。不是因为数字小，而是因为：

1. **Skill 5 一人扛 4 层**：证据合成 + 控制权 + 场景分类 + 行为假设 → 违反单一职责
2. **Skill 6 缺失 8 个否决条件 + 冲突裁决 + 刷量降级** → 否决层不完整
3. **缺少层 0 宪法检查** → 无语言约束强制执行
4. **缺少层 1 统一标准化** → 3 个 Skill 独立调 GMGN（Parnas 违规）
5. **数据归属混乱** → 任何两层共享原始字段引用

**建议最终 Skill 数：10-11 个**。不是加复杂度，是把隐含在多层的逻辑显式化为单一职责的 Skill。
