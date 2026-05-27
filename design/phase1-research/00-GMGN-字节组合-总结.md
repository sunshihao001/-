# GMGN 字节组合反向推理 — 完整交付总结

> 产出时间：2026-05-25
> 项目：`/root/sikk-gmgn/` Solana Meme Workflow OS
> Phase：Phase 1 Research Pipeline
> 边界：safe-mode research only，不输出 buy/sell/swap/signing/broadcast

---

## 一句话

从 GMGN 230 个 API 字段出发，用 VWAP 方法论模板，
系统性地推导出 37 个 L1 派生指标 + 16 个 L2 结构状态判断 +
一套可复用的推理方法。

---

## 交付文件

| 文件 | 内容 | 路径 |
|------|------|------|
| **01 字段清单** | GMGN 230 raw fields 完整罗列（用户提供） | `01-GMGN字段原始清单.txt` |
| **02 字节分解** | Part 0-6：Canonical(120) → L1(37) → L2(16) → Quality Gate → VWAP映射 → Gap | `design/phase1-research/gmgn-byte-decomposition-v0.1.md` |
| **03 推理链** | Part 1-7：37 L1 + 16 L2 逐条推理+字节+功能 + 方法论 | `design/phase1-research/gmgn-byte-combination-reasoning-v0.1.md` |

---

## 核心架构

```
GMGN API (230 raw fields)
        │
        ▼
┌──────────────────────────┐
│ PART 0: Canonical Bytes  │  120 字段直接可用，不需计算
│ (价格/量/持有/安全/Dev)  │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ PART 1: L1 Features      │  37 个 1次计算 = 2+ raw bytes → 1 派生指标
│                          │
│ A.买卖压力 (6)  B.动量 (5)  C.深度质量 (5)
│ D.钱包智能 (7)  E.Dev风险 (6)  F.生命周期 (5)  G.社交 (3)
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ PART 2: L2 Candidates    │  16 个 2次计算 = N 个 L1 → 1 结构判断
│                          │
│ A.累积 (3)   B.分销 (3)   C.操纵 (3)
│ D.生命周期 (3)  E.特殊事件 (3)  F.健康 (1)
└──────────┬───────────────┘
           │
           ▼
     Gate: BLOCK / WATCH / PAPER
```

---

## L1 Features 速查（37 条）

| ID | 名称 | 核心公式 | 功能 |
|----|------|---------|------|
| A1 | buy_dominance | buy_1h/(buy+sell) | 买方资金占比 |
| A2 | buy_sell_count_ratio | buy笔数/(buy+sell)笔数 | 配合A1区分大单vs散单 |
| A3 | net_flow_intensity | (buy-sell)/liquidity | 净流向对池子压力 |
| A4 | sm_direction_signal | SM netflow聚合 | 聪明钱净买卖方向 |
| A5 | kol_direction_signal | KOL netflow聚合 | 与SM对比判断共振/分歧 |
| A6 | volume_weighted_sm_conviction | sign(netflow)×仓位% | 大仓SM的加权方向 |
| B1 | volume_intensity | vol_1h/liquidity | 流动性周转速度 |
| B2 | volume_momentum | vol_1h/(vol_24h/24) | 相对近24h平均的倍数 |
| B3 | swap_per_holder | swaps_1h/holders | 人均交易活跃度 |
| B4 | volume_per_swap | vol_1h/swaps_1h | 每笔平均金额 |
| B5 | volume_decay_ratio | vol_now/vol_prev | 量加速or衰减 |
| C1 | mcap_to_liquidity_ratio | mcap/liquidity | 市场薄度 |
| C2 | price_to_ath_ratio | price/ath | 相对历史高点位置 |
| C3 | top_holder_velocity | 1h内活跃大仓/10 | 大仓是否在动 |
| C4 | liquidity_decay_flag | liq/initial_liq | 流动性保留率 |
| C5 | spread_quality_proxy | quote_res/(base+quote) | 价差代理（无L1订单簿） |
| D1 | sm_penetration | sm_count/holders | SM渗透深度 |
| D2 | sm_exit_ratio | 已清仓SM/SM总数 | SM离场比例 |
| D3 | sm_profit_status | SM盈亏聚合 | SM处于盈利or亏损 |
| D4 | kol_quality_flag | 实质持仓KOL/KOL总数 | KOL参与真实性 |
| D5 | fresh_wallet_ratio | fresh/holders | 新钱包比例 |
| D6 | wallet_source_convergence | 资金来源多样性 | 同源钱包检测 |
| D7 | sniper_retention | sniper持有比 | 狙击手是否还在 |
| E1 | dev_risk_score | 6因子加权 | Dev综合风险 |
| E2 | dev_track_record_score | ath_mc/100k | Dev历史发币质量 |
| E3 | dex_marketing_intensity | 4个营销flag计数 | Dev营销投入 |
| E4 | insider_activity_composite | rat+bundler+entrap | 操纵交易总占比 |
| E5 | fee_burden_total | buy_tax+sell_tax | 买卖总税费 |
| E6 | cto_quality_check | CTO后复苏质量 | 仅在CTO时计算 |
| F1 | token_age_minutes | (now-created)/60 | Token年龄 |
| F2 | bonding_curve_progress_rate | Δprogress/Δtime | 毕业进度速度 |
| F3 | time_since_open | (now-open)/60 | 开盘时长 |
| F4 | pool_age_hours | (now-pool_created)/3600 | 池子年龄 |
| F5 | holder_growth_rate | Δholders/Δtime | 持有人增速 |
| G1 | social_completeness | 社交覆盖/4 | 包装完整度 |
| G2 | follower_to_mcap_ratio | followers/(mcap/1k) | 社交热度相对市值 |
| G3 | description_quality_hint | len(description) | 描述认真程度 |

---

## L2 Structure Candidates 速查（16 条）

| ID | 名称 | 核心条件 | Gate |
|----|------|---------|------|
| A1 | SM积累 | SM偏买+未清仓+深度参与+有量 | W→PAPER |
| A2 | KOL+SM共振 | SM偏买+KOL偏买+KOL实质持仓 | W→PAPER |
| A3 | 低调积累 | SM偏买+低量+无新人+无操纵 | WATCH |
| B1 | SM出货 | SM偏卖+清仓比例高+还有量 | W→PAPER |
| B2 | Dev砸盘 | dev持货+营销+新人涌入 | BLOCK |
| B3 | Sniper离场 | sniper大量清仓+开盘1h内 | WATCH |
| C1 | 内部人操纵 | 操纵>50%+SM不参与+同源 | **BLOCK** |
| C2 | Bot刷量 | 刷量标记+bot主导+对倒特征 | **BLOCK** |
| C3 | 流动性陷阱 | 极薄+集中+低流动性 | **BLOCK** |
| D1 | 早期突破 | <1h+SM关注+放量+未清仓 | WATCH |
| D2 | 已死 | 无交易+量萎缩+持有人减少 | **BLOCK** |
| D3 | 毕业窗口 | bonding curve>70%+有填充速度 | WATCH |
| E1 | CTO复苏 | dev已走+SM认可+量复苏 | W→PAPER |
| E2 | 炒作高潮 | 暴涨+量暴增+新人涌入+SM卖 | WATCH |
| E3 | 超跌反弹 | 跌70%+买盘+有量+SM接 | W→PAPER |
| F1 | 健康市场 | SM参与+无操纵+不薄+无刷量+dev低风险 | WATCH |

---

## 推理方法论（可复用）

任何 GMGN 字节组合的推理，从五个问题开始：

```
Q1: 我想知道什么市场事实？
Q2: 这个事实在链上会留下什么痕迹？
Q3: GMGN 哪个字段能看到这个痕迹？
Q4: 单一字段够不够？不够的话和哪个配对？
Q5: 配对后的值在什么范围内代表什么含义？
```

L1 → L2 跨越用 **反证法**：
> 「如果这个结构不存在，数据长什么样？」→ 取反 → 就是条件。

---

## VWAP → GMGN 关键映射

| VWAP 角色 | GMGN 替代 | 差距 |
|-----------|----------|------|
| 成交成本锚点 | price_to_ath_ratio, price_change_percent | 无精确 VWAP，kline 近似可用 |
| 市场结构识别 | 16 个 L2 Candidates（已映射） | ✅ 已覆盖 |
| 流动性过滤器 | mcap_to_liquidity_ratio, spread_quality_proxy | ⚠️ 无真实 L1 spread |
| 成交参与压力 | buy_dominance + volume_per_swap | ⚠️ 已成交非挂单，性质不同 |
| Regime 解释 | 5 种 regime 映射（trend/range/vol/low_liq/event） | ⚠️ 需连续采样 |
| 执行归因 | SM方向+池子状态+流动性 | 🔜 延后至 Phase 2 |
| 生命周期闭环 | raw→canonical→feature→structure→gate | ✅ Phase 1 可完成前 5 步 |

---

## 下一步

1. **阈值校准** — L1/L2 所有 > / < 阈值需要历史数据回测
2. **Phase 1 Skill 映射** — 把 37 L1 + 16 L2 嵌入 meme-candidate-entry → meme-trade-gate
3. **新增 L1-B6** — kline VWAP proxy 实现
4. **Quality Gate 代码化** — Part 4 规范 → 可执行 validator
5. **Regime Classifier** — 延后 Phase 2+

---

> 全部文件位于 `/root/sikk-gmgn/design/phase1-research/`
> 状态：RESEARCH_IN_PROGRESS（五轮完成）
