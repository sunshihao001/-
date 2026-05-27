# Grill Session: 用 GMGN 全字节反推策略 / 2次字节组合

- 日期：2026-05-26
- 项目：Solana Meme Workflow (`/root/sikk-gmgn/`)
- 阶段：Phase 1 研究 — 字节研究 / 反向推理
- 工具：`grill-with-docs`（原版）
- 状态：READY_FOR_REVIEW（研究产出，未进入实施）
- 边界：不 live、不 paper、不 swap、不 sign；研究产出只到 WATCH / WATCH→PAPER gate

---

## 0. 起点问题

用户原句：

> 现在在 sol 工作流里我现在研究其 gmgn 的全部初始字节来反向推理反推其需要的策略的 2 次需要计算字节组合

第一轮 grill 校准后，问题被规范化为：

- 「初始字节」= GMGN API 返回的全部约 230 个 raw fields（10 大类）
- 「2 次计算字节组合」= 层次定义：Layer 0（canonical raw / GMGN 已算）→ Layer 1（1 次组合 = feature）→ Layer 2（2 次组合 = structure candidate）
- 「反向推理」= 不先套既有策略框架，而是先看字节组合本身能暴露出哪些结构、行为、阶段、策略类型，再回到策略层做选择
- 「需要的策略」= GMGN 字段能支持哪些策略类型；它不能支持哪些策略类型

---

## 1. Grill 路径回顾（拷问链）

1. 把「2 次」从"二阶派生 vs 类别"歧义拷问为"层次定义"
2. 把「初始字节」从"个别字段"拷问为"GMGN 全部 230+ raw fields"
3. 把「反推策略」从"做信号"拷问为"先暴露结构再选择策略类型"
4. 把「让字节自己说话」从口号拷问为可操作的方法论
5. 把「套框架 vs 生框架」拷问出用户真实立场（A、B、C → C：两者都有，但希望更多生）
6. 把「同一组字节多种结论」拷问到根本原因（A：数据中性，框架是活的）
7. 用维特根斯坦 / 奥派 / 反理性建构主义把"字节会说话"这种拟人化表述拆掉
8. 给出"价格信号"作为任何新框架的最终回路验证标准

---

## 2. 字节三层架构（这次研究的核心成果）

```text
Layer 0 — Canonical Raw（GMGN 已算）
  • 约 120 个字段
  • token info / token security / token pool / token holders / token traders
  • market trending / market trenches / market kline / market signal
  • 这一层不是 raw bytes，是 GMGN 替我们做完一次聚合后的"准 raw"

Layer 1 — Feature（1 次组合）
  • 37 个 feature，7 类
  • A 买卖压力 6 | B 动量 5 | C 深度质量 5 | D 钱包智能 7
  • E Dev 风险 6 | F 生命周期 5 | G 社交 3
  • 由 2+ Layer 0 字段组合而成

Layer 2 — Structure Candidate（2 次组合）
  • 16 个候选结构，6 类
  • A 累积型 | B 分销型 | C 操纵型 | D 生命周期 | E 特殊事件 | F 结构健康
  • 由多个 Layer 1 feature 组合而成
  • 输出到 Gate：BLOCK / WATCH / WATCH→PAPER
```

详见：

- `gmgn-byte-decomposition-v0.1.md` — 完整技术规格 6 Parts
- `gmgn-byte-combination-reasoning-v0.1.md` — 每条 L1/L2 的推理链 + Part 7「五问题引擎」方法论
- `00-GMGN-字节组合-总结.md` — 速查总览
- `00b-GMGN-Canonical-Bytes.txt` — Canonical 字段子类清单
- `00c-GMGN-思维模型提炼.txt` — 8 思维模型 / 5 推理模式 / 5 GMGN 特有认知修正 / 7 可迁移方法
- `00d-GMGN-多维度推理扩展.txt` — 钱包 / 微结构 / 庄家生命周期 / 策略类型 4 个新维度
- `00e-字节反推框架-突破认知局限.txt` — 6 个从字节生发新框架的方法

---

## 3. GMGN 字段的硬限制

- 没有 L1 订单簿 → 没有真实 bid/ask spread
- 没有 trade-level price × volume → VWAP 只能用 kline `(high+low+close)/3 × amount` 近似
- 没有完整全部 holders → 只看 top 列表
- 没有跨 token 钱包成本基线 → 只能用 GMGN 给出的 avg_cost
- 没有真实意图，只有事后行为痕迹

代理方案：

- `mcap_to_liquidity_ratio` 替代 spread proxy
- kline mid-price × amount 近似 VWAP
- 池子储备比率近似深度
- wallet_tags_stat + holders/traders 的行为字段近似"庄家结构"

---

## 4. 「让字节自己说话」的维特根斯坦校准

误导性表述：

> "字节会自己说话"

精确表述：

> 用系统化字节组合 + 链上结果反馈，减少个人经验对解释框架的垄断；不是让字节产生真理，而是让字节组合产生更多被检验的假设。

四个边界条件：

1. **字节是中性的** — 同一组字节可以生成多个互相冲突的框架，框架决定结论而不是字节决定结论
2. **框架是活的** — 框架不是预设而是被字节组合 + 链上反馈逐步长出来的
3. **反理性建构主义** — 你不能先设计完美框架然后要求市场符合，市场是自发秩序，框架只能从市场痕迹里逐步长出来
4. **价格信号是最终裁判** — 任何新框架最终都要回到价格 / 流动性 / SM 盈亏 / 钱包离场 / 结构重复 5 个回路验证，否则就是空框架

---

## 5. 方法论结论：套框架 vs 生框架

- **套框架**：拿既有理论（VWAP、Wyckoff、SMC、订单流、行为金融）解释字节
  - 优点：解释快、可沟通、有先验
  - 缺点：被旧框架限制、看不到 GMGN 字段暴露的新结构

- **生框架**：从字节组合本身归纳出未被命名的结构
  - 优点：可能发现旧框架之外的市场行为
  - 缺点：噪声高、需要链上反馈反复校准、容易过拟合

- **当前选择**：两者都做，但研究阶段重点向"生框架"倾斜，目的是逼自己跳出经验局限

「生框架」可操作的 6 个方法（见 `00e-字节反推框架-突破认知局限.txt`）：

1. 穷举字节两两 / 三三组合
2. 异常驱动：找统计极端值 → 反推它代表什么结构
3. 聚类驱动：对 token / 钱包做无监督聚类 → 看簇内共性
4. 对立驱动：找"看起来该涨却没涨"和"看起来该跌却没跌"的样本 → 反推被遗漏的字节
5. 时间序列驱动：看同一 token 不同时间段字节模式变化 → 反推阶段转换
6. 反证驱动：拿一个流行框架，用 GMGN 字段去证伪它

---

## 6. 任何新框架的 5 个回路验证（grill 终点）

一个 GMGN 字节组合 + 框架假设要成立，必须能回答：

1. 后续价格有没有变化？（涨 / 跌 / 横盘 / 振幅）
2. 流动性有没有变化？（liquidity, base/quote reserve）
3. SM（smart_degen）有没有赚钱？（profit, realized_pnl, sell_amount_percentage）
4. 钱包有没有离场？（end_holding_at, transfer_out_count, sell_amount_percentage = 1.0）
5. 结构有没有重复？（同类字节模式在其他 token 上是否再次出现且后续走势一致）

5 个都答不出来 → 空框架。
能答出 1–2 个 → 弱假设，回到 WATCH。
能答出 3+ 个且链上重复出现 → 升级到 WATCH→PAPER。
任何阶段都不直接 BUY/SELL。

---

## 7. Grill 终点一句话

> 你不是在研究 GMGN 字段。  
> 你是在用 GMGN 字段训练自己摆脱旧框架。  
> 字节组合的价值，不是给你更多结论，而是逼你发明更好的问题。

---

## 8. 状态

- status：`READY_FOR_REVIEW`
- next：
  - 选 1 个「生框架」方法（建议从 #2 异常驱动或 #5 时间序列驱动开始）在真实 GMGN token 上试一次
  - 或继续 `03-阈值校准与回测设计` / `04-Phase1-Skill 映射`
- 边界：本次产出只到研究层，未触发任何 paper / live / swap / sign
