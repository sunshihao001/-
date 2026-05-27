# 16｜Gate 决策框架理论基石：从 L2 结构观察到 Gate 决策干预的五原则

## 这一篇要解决的问题

前面 14 篇已经回答了「字段怎么读、L2 怎么组、阈值大致放哪里」。但还没有回答一个更前置的问题：

**Gate 到底是什么？是结构属性（看到什么），还是决策属性（决定做什么）？**

如果不先把这个问题拍死，Gate 规则会和 L2 规则混在一起，未来很难做反事实分析、命中率校准和规则迭代。

这一篇通过 Spark 模式（塔勒布 + Pearl + 泰特洛克）对 5 个底层判定逐一拍板，沉淀成「Gate 决策框架五原则」，作为 14（门控阈值）之上的认知论基石。

不涉及具体阈值，不涉及代码。只确立框架。

---

## 一、5 个底层判定

### 判定 1：Gate 是结构属性还是决策属性？

**结论：决策属性。**

| 专家 | 核心立场 |
|---|---|
| 塔勒布 | 结构是世界的，Gate 是你对世界的回应。把 Gate 写成结构属性等于假装客观，掩盖了你在押注。BLOCK 不是「它坏」，是「我不接」。 |
| Pearl | L2 触发是 `P(token \| features)`，Gate 是 `do(action \| L2)`。结构属性无法支持反事实推理——你无法回答「如果当时没 BLOCK 会怎样」。 |
| 泰特洛克 | 结构属性无法被证伪；决策属性可以累积命中率。Gate 必须留下「我当时为什么这样判」的痕迹，否则没法迭代。 |

**工程后果**：L2 检测和 Gate 决策必须是两层分离的函数，不允许合并。L2 输出「看到什么」，Gate 输出「做什么」。

---

### 判定 2：单 L2 触发 vs 组合 L2 触发？

**结论：组合 L2，且需满足三个约束。**

| 专家 | 核心立场 |
|---|---|
| 塔勒布 | 单 L2 触发是脆弱的——一个字段被操纵就全盘崩。组合触发让攻击成本指数上升。反脆弱的 Gate 要求多源证据。 |
| Pearl | 组合要做因果独立性检查。两个 L2 如果共享同一个上游因（如都受「大户拉盘」驱动），组合不增加信息量。 |
| 泰特洛克 | 组合 L2 是「狐狸式」（多视角加权），单 L2 是「刺猬式」（一锤定音）。狐狸式预测在长期校准上显著更好。但权重不等。 |

**三个约束**：

1. **因果独立性**：每个 L2_Pattern 显式声明组成的 L1 集合 + 独立性声明
2. **权重不等**：Phase 1 不学权重，但要标注 L1 的判定强度（STRONG / MEDIUM / WEAK）
3. **攻击成本递增**：组合越多，操纵者要同时伪造的字段越多

**因果独立性示例**：

| L1 对 | 共享上游？ | 是否独立 |
|---|---|---|
| liquidity_low + holders_few | 都来自「早期阶段」 | 否（不独立） |
| top10_high + freshwallet_high | 不同行为路径 | 是 |
| dev_holding_high + holder_growth_slow | 弱共因 | 部分独立（降权使用） |

---

### 判定 3：确定性触发 vs 权重塌缩？

**结论：BLOCK 用确定性硬规则；WATCH / PAPER 用规则式；Phase 1 全部规则式。**

| 专家 | 核心立场 |
|---|---|
| 塔勒布 | BLOCK 是不对称的——错杀一个 token 损失有限（机会成本），放过一个毒 token 损失无限（资金毁灭）。BLOCK 必须是硬规则。 |
| Pearl | BLOCK 应该是确定性 intervention，因为它要支持反事实分析。WATCH→PAPER 可以是概率性，但要可解释。 |
| 泰特洛克 | 权重塌缩在小样本下不可校准——你没几千次决策，权重学不出来。早期阶段所有 Gate 都该是「如果 A 且 B 且非 C」式规则。 |

**Phase 推进路线**：

- **Phase 1**：BLOCK / WATCH / WATCH→PAPER 全部 if-then 硬规则
- **Phase 2+**：在 PAPER 升级层考虑权重塌缩；BLOCK 永远不上权重

---

### 判定 4：TTL / 状态时间属性？

**结论：双 TTL 设计（证据 TTL + 决策 TTL）。**

| 专家 | 核心立场 |
|---|---|
| 塔勒布 | meme 市场的信号衰减是指数级的。10 分钟前的「高活跃」现在可能是死盘。没有 TTL 的 Gate 等于在用过期证据决策。 |
| Pearl | 时间是 confounder。`L2_t` 触发 ≠ `L2_{t+Δ}` 仍成立。Gate 决策必须绑定证据时间戳，且决策本身也有 TTL。 |
| 泰特洛克 | 可校准性要求时间一致性。每个 Gate 必须有「证据时窗」和「决策有效期」两个 TTL，否则校准乱套。 |

**双 TTL 设计**：

- **证据 TTL（evidence_ttl）**：L2 触发所依据的字段数据的有效期
- **决策 TTL（decision_ttl）**：Gate 输出（BLOCK / WATCH / PAPER）的有效期

**证据 TTL 分类（建议值，具体由 06、09 后续学习课题确认）**：

| 字段类别 | 示例 | 建议 TTL |
|---|---|---|
| 实时市场态 | price, liquidity, volume_5m | 1–3 分钟 |
| 持仓结构 | top10_ratio, holder_count | 5–10 分钟 |
| 链上行为 | dev_sold, fresh_wallet_count | 10–30 分钟 |
| 标签/黑箱 | gmgn_risk_tags | 30 分钟–1 小时（且仅作 hint） |

**决策 TTL 分类**：

| Action | decision_ttl | 到期处理 |
|---|---|---|
| BLOCK | 30 分钟 | 重新评估；但 BLOCK 通常更稳定 |
| WATCH | 5–10 分钟 | 强制重检 |
| WATCH→PAPER | 5 分钟 | 强制重检 |
| PASS | 5 分钟 | 重新评估 |

**时间一致性约束**：任一证据过期 → Gate 决策自动失效，进入重评估队列。

---

### 判定 5：缺数据策略？

**结论：默认 BLOCK + 记录 missing_fields + 校准命中率。**

| 专家 | 核心立场 |
|---|---|
| 塔勒布 | 缺数据 = BLOCK。凸性保护是不对称的——你不知道的东西不能假设是好的。「missing → safe default」是赌博。在 meme 市场，黑箱通常对应骗局。 |
| Pearl | 分情况。MCAR（完全随机缺失）可以填补，MNAR（缺失本身有信息）必须当作信号。meme 市场的「holder 数据查不到」大概率是 MNAR——这本身就是 BLOCK 的证据。 |
| 泰特洛克 | 缺数据策略本身要被记录和校准。如果「缺数据 → BLOCK」规则在历史上 95% 都是对的，那继续。如果只有 50%，那是迷信。Phase 1 默认 BLOCK，但要校准。 |

**三态分类**：

```
field_status ∈ {present, missing_MCAR, missing_MNAR}
```

Phase 1 简化：**所有 missing 默认按 MNAR 处理**。

**触发规则**：

```
critical_fields_missing ≥ 1   →   BLOCK
non_critical_missing ≥ N      →   降级为 WATCH（不进 PAPER）
```

**critical_fields 候选清单**（待 06、09 后续学习课题确认）：

- holder 分布字段（top10_ratio, holder_count）
- 流动性字段（liquidity_usd, lp_locked）
- dev 字段（dev_holding, dev_sold）

**记录义务**：不允许把 missing 当作「=0」或「=默认值」填充。所有 missing 必须显式记录到 `decision.missing_fields`，用于 Phase 2 校准命中率。

---

## 二、Gate 的形式化定义

### 对象层级

```
Token         := 被评估的代币（mint 地址）
Field         := GMGN/链上单字段（如 liquidity_usd, top10_holder_ratio）
L1_Signal     := 单字段触发（field op threshold），结构观察层
L2_Pattern    := 多 L1 组合（field 组合 + 因果独立），结构判断层
Evidence      := L2 触发时的字段快照 + 时间戳
Gate          := 基于 Evidence 的决策动作
Action        := {BLOCK, WATCH, WATCH→PAPER, PASS}
```

**关键区分**：

- L2 是结构观察（看到什么）
- Gate 是决策干预（决定做什么）

### Gate 的形式化签名

```
Gate: Evidence × Context × Time → Decision

Decision = {
  action:        BLOCK | WATCH | WATCH→PAPER | PASS,
  triggered_by:  [L2_Pattern, ...],          # 哪些 L2 触发
  evidence_ts:   timestamp,                   # 证据时间戳
  evidence_ttl:  duration,                    # 证据有效期
  decision_ttl:  duration,                    # 决策有效期
  missing_fields: [Field, ...],               # 缺数据清单
  rationale:     string,                      # 可校准的判断理由
  confidence:    "rule" | "weighted",         # Phase 1 全部为 rule
}
```

### Gate 状态机

```
        ┌─────────────────────────────────┐
        │  Token 进入评估                  │
        └───────────────┬─────────────────┘
                        ▼
                ┌───────────────┐
                │  L2 检测层     │
                └───────┬───────┘
                        ▼
        ┌───────────────────────────────┐
        │  BLOCK 规则集（硬规则）         │  ← 任一触发即 BLOCK
        │  - L2_blockset_1 → BLOCK      │
        │  - L2_blockset_2 → BLOCK      │
        └───────┬───────────────────────┘
                ▼ (无 BLOCK)
        ┌───────────────────────────────┐
        │  WATCH 规则集                   │
        │  - L2_watchset_1 → WATCH      │
        └───────┬───────────────────────┘
                ▼
        ┌───────────────────────────────┐
        │  PAPER 升级条件                 │
        │  WATCH AND L2_promoteset       │
        │  → WATCH→PAPER                 │
        └───────┬───────────────────────┘
                ▼
              PASS
```

**优先级**：`BLOCK > WATCH→PAPER > WATCH > PASS`。任一上层触发，下层不再评估。

---

## 三、Gate 决策框架五原则（拍板）

| # | 原则 | 一句话表达 | 来源 |
|---|---|---|---|
| 1 | **干预非观察** | Gate 是 `do(action)`，不是 `P(token)` | Pearl |
| 2 | **组合非单点** | L2 由因果独立的 L1 组合而成，权重不等 | Pearl + 泰特洛克 + 塔勒布 |
| 3 | **硬规则非权重** | Phase 1 全规则式，BLOCK 永远确定性 | 塔勒布 + 泰特洛克 |
| 4 | **双 TTL 非永恒** | 证据 TTL + 决策 TTL，过期自动失效 | Pearl + 塔勒布 |
| 5 | **缺数据 = BLOCK** | 凸性保护 + MNAR 假设 + 显式记录 | 塔勒布 + Pearl |

---

## 四、与其他学习篇的关系

- **14（门控阈值）**：本篇是 14 的认知论基石。14 回答「阈值放哪里」，本篇回答「为什么 Gate 是这样工作的」。
- **06（数据源机制）**：本篇要求的「critical_fields 清单」依赖 06 对 trending / trenches / signal 三源的字段可得性分析。
- **09（LP / 流动性深度）**：本篇要求的「证据 TTL 分类」依赖 09 对流动性字段衰减速度的分析。
- **13（多信号融合）**：本篇的「因果独立性约束」由 13 的 Evidence Chain 设计具体落实。

---

## 五、Phase 1 边界提醒

- 本篇是 **paper-only 研究**，不涉及任何真实交易、签名、广播
- Gate 决策的输出只用于「是否进入 paper trade 跟踪」，不直接驱动资金
- 所有「BLOCK」「WATCH」语言都是研究判断，不构成投资建议
- 严禁出现「确定庄家」「一定会涨」「确定内幕」等语言
