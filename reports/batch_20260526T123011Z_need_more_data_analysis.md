# Batch 20260526T123011Z NEED_MORE_DATA 分析报告

生成时间：2026-05-26
分析对象：`/root/sikk-gmgn/data/runs/batches/20260526T123011Z/`

---

## 1. 结论先行

这批 4 个 token 全部停在 `NEED_MORE_DATA`，**不是因为字段大量缺失**，而是因为：

1. `wallet_roles` 给出的 smart money 证据几乎为空（4 个 token 全部 `smart_money_count = 0`，`sm_net_direction = no_sm`）
2. `evidence_chain` 的主导行为全部是 `UNKNOWN`
3. `wallet_structure` 的结构风险都偏高，其中 1 个是 `critical`
4. `trade_gate` 因此拿不到足够的正向证据将门控推到 `PAPER_ONLY`
5. 门控分数集中在 `27~33/100`，置信度集中在 `0.5~0.6`

所以当前问题不是“跑不通”，而是**判断材料不够强，导致系统刻意保守**。

---

## 2. 本批次整体统计

- Batch ID: `20260526T123011Z`
- Source: `trending`
- Candidate Count: `4`
- Filtered Out Count: `1`
- Completed Count: `4`
- Final gate decisions: 全部 `NEED_MORE_DATA`

门控分数分布：

- `WorldCup`: `33`
- `Henrik`: `33`
- `CTR`: `27`
- `ISOR`: `30`

置信度分布：

- `WorldCup`: `0.60`
- `Henrik`: `0.60`
- `CTR`: `0.50`
- `ISOR`: `0.60`

---

## 3. 四个 token 的共同特征

### 3.1 Smart money 证据几乎为零

四个 token 全部：

- `smart_money_count = 0`
- `sm_direction = no_sm`

这意味着 `wallet_roles` 没有提供足够的“聪明钱介入”信号。

在当前门控逻辑里，smart money 是推动 `PAPER_ONLY` 的重要正向条件之一。没有它，系统会自然偏向：

- 观望
- 继续观察
- 要更多数据

### 3.2 主导行为全是 UNKNOWN

四个 token 的 `evidence_chain.dominant_behavior` 全部是 `UNKNOWN`。

这说明：

- 证据链没有形成足够一致的行为方向
- 没有“持续吸筹 / 明确派发 / 明确早期阶段”等可用主导行为
- trade-gate 无法得到高质量行为证据

### 3.3 结构风险偏高

- `WorldCup`: `high`
- `Henrik`: `high`
- `CTR`: `critical`
- `ISOR`: `high`

这直接压低 `gate_score`，尤其是 `CTR`。

### 3.4 不是“字段缺失”问题

本批次汇总里：

- `all_missing = []`

也就是说，这批 token 不是因为上游字段没填而被卡住。
真正的问题是：

> 字段都在，但字段组合给出的结构判断不够强。

---

## 4. 具体 token 观察

### 4.1 WorldCup

- `gate_decision = NEED_MORE_DATA`
- `gate_score = 33`
- `confidence = 0.60`
- `structure_risk = high`
- `smart_money_count = 0`
- `dominant_behavior = UNKNOWN`
- `creator_status = creator_close`
- `liquidity ≈ 172.7k`

解释：

- 流动性本身不差，但没有 smart money 参与的正向证据
- 主导行为不清晰
- 结构风险偏高
- 只有 `DEV_EXITED` 这种弱正向信号，不足以推入 `PAPER_ONLY`

---

### 4.2 Henrik

- `gate_decision = NEED_MORE_DATA`
- `gate_score = 33`
- `confidence = 0.60`
- `structure_risk = high`
- `smart_money_count = 0`
- `dominant_behavior = UNKNOWN`
- `creator_status = creator_close`
- `liquidity ≈ 158.5k`

解释：

- 和 WorldCup 很像
- 结构风险高，但没有足够证据表明“可以进入 paper 观察”
- 系统保持保守是合理的

---

### 4.3 CTR

- `gate_decision = NEED_MORE_DATA`
- `gate_score = 27`
- `confidence = 0.50`
- `structure_risk = critical`
- `smart_money_count = 0`
- `dominant_behavior = UNKNOWN`
- `creator_status = creator_close`
- `liquidity ≈ 97.3k`

解释：

- 这是本批次最弱的一个
- 结构风险已经到 `critical`
- 门控分数最低
- 比起前两个 token，更不接近 `PAPER_ONLY`

---

### 4.4 ISOR

- `gate_decision = NEED_MORE_DATA`
- `gate_score = 30`
- `confidence = 0.60`
- `structure_risk = high`
- `smart_money_count = 0`
- `dominant_behavior = UNKNOWN`
- `creator_status = creator_close`
- `liquidity ≈ 75.7k`

解释：

- 依旧没有 smart money 证据
- 结构风险高
- 置信度略高于 CTR，但不足以改变门控结论

---

## 5. 为什么全部停在 NEED_MORE_DATA

可以概括成一句话：

> 系统看到了 token，但没有看到足够强的“可持续结构证据”。

具体来说：

1. **没有 smart money 进入的正向支撑**
2. **没有清晰的 dominant behavior**
3. **结构风险偏高，甚至 critical**
4. **门控阈值偏保守，要求更强证据才能进入 PAPER_ONLY**

因此 `trade-gate` 没有把任何 token 送到 `PAPER_ONLY`。

---

## 6. 这说明了什么

### 6.1 系统已经不是“不能跑”

流水线已经跑通，说明工程链路没问题。

### 6.2 当前真正的瓶颈是“判断质量”

`NEED_MORE_DATA` 的集中爆发，意味着系统目前更像一个：

- 风险筛选器
- 结构观察器
- 证据不足时的保守门控器

而不是一个已经能稳定挑出 paper-ready 机会的系统。

### 6.3 下一步应做的不是加自动交易

而是：

- 校准 wallet_roles 的 smart money 识别质量
- 校准 evidence_chain 的行为归因规则
- 校准 trade_gate 的门控阈值
- 看看是不是“有数据但没被识别出来”，还是“样本本身就弱”

---

## 7. 建议的下一步动作

### 7.1 做一个 `NEED_MORE_DATA` 原因拆分表

建议把每个 token 的 `trade_gate` 里：

- `missing_fields`
- `downgrade_reasons`
- `decision_reasons`
- `risk_factors`
- `positive_signals`

拆成统一原因矩阵，方便看是：

- 数据缺失型
- 结构过弱型
- 行为不明型
- 风险过高型

### 7.2 抽样做“强样本 vs 弱样本”对比

应该找一批历史上更接近 `PAPER_ONLY` 的样本，对比：

- smart money 数量
- dominant behavior
- structure risk
- gate score
- confidence

这样才能知道当前阈值是太严，还是样本确实弱。

### 7.3 优先检查 `wallet_roles` 和 `evidence_chain`

因为这两个层级最容易决定是否进入 `PAPER_ONLY`：

- `wallet_roles` 给不出 smart money，后面很难抬分
- `evidence_chain` 如果一直 `UNKNOWN`，trade-gate 只能保守

---

## 8. 一句话总结

这批 token **不是跑不动，而是“证据不够强”**。

系统当前表现为：

> 能把垃圾盘和不清晰盘挡住，但还没有足够证据把 token 推到 paper-ready。

---

## 9. 安全边界

本报告只用于研究和门控分析，不构成交易建议。

- 不含 live trading
- 不含 swap
- 不含私钥
- 不含签名
- 不含广播
- 不含下单提示
