# PART 2: L2 Structure Candidate — 2次计算字节组合

> 定义：N 个 L1 feature + canonical bytes 组合 → 一个结构状态判断
> 边界：只描述「市场可能处于什么状态」，不输出 buy/sell/action/decision_ticket

---

## L2-A：累积型结构 (Accumulation Structures)

### L2-A1：SMART_MONEY_CONVICTION_ACCUMULATION

```yaml
structure_candidate:
  name: SMART_MONEY_CONVICTION_ACCUMULATION
  meaning: "聪明钱正在有信念地积累仓位"

  required_conditions:
    all_of:
      - sm_direction_signal.sm_buy_ratio > 0.6          # 多数 SM 在买
      - sm_exit_ratio < 0.2                              # 极少数 SM 在清仓
      - sm_penetration > 0.01                            # SM 有一定参与
      - volume_momentum > 1.0                            # 成交量至少不低于均线

  supporting_signals:
    - volume_weighted_sm_conviction > 0                  # 大仓 SM 也在买
    - volume_per_swap > 50                               # 有一定大单 ($50+)
    - insider_activity_composite < 0.3                   # 操纵交易占比低

  warning_signals:
    - fresh_wallet_ratio > 0.6 AND sm_buy_ratio < 0.7    # 大量新钱包但 SM 买盘不足
    - is_wash_trading == true                             # 刷量直接降级

  possible_meaning:
    - "聪明钱在早期或回调中积累"
    - "市场存在未被零售发现的买入机会"
    - "可能是趋势启动前兆"

  not_meaning:
    - "不是立即买入信号"
    - "不是价格一定上涨的保证"
    - "不是 strategy_approved"

  quality_gate:
    - smart_degen_count >= 3     # SM 样本至少 3 个
    - token_age > 5 min          # 排除刚创建的噪声
    - is_wash_trading == false   # 排除刷量

  risk:
    - "SM 可能累积后不拉升（项目失败）"
    - "SM 可能是在摊平成本而非主动买入"
    - "零售可能在 SM 之后才注意到，追高风险"
```

### L2-A2：KOL_SM_RESONANCE_ACCUMULATION

```yaml
structure_candidate:
  name: KOL_SM_RESONANCE_ACCUMULATION
  meaning: "聪明钱和 KOL 同时共振买入——最强累积信号"

  required_conditions:
    all_of:
      - sm_direction_signal.sm_buy_ratio > 0.6
      - kol_direction_signal.kol_buy_ratio > 0.6
      - kol_quality_flag > 0.3                              # KOL 有实质持仓

  supporting_signals:
    - sm_profit_status.sm_avg_unrealized_pnl < 1.0          # SM 还没有大幅盈利
    - volume_momentum > 1.5                                 # 量在放大
    - buy_dominance > 0.55                                  # 买入主导

  warning_signals:
    - sm_profit_status.sm_in_profit_ratio > 0.8             # SM 已经大幅盈利
    - kol_quality_flag < 0.2                                # KOL 实质持仓极小
    - price_to_ath_ratio > 0.8                              # 价格接近 ATH

  possible_meaning:
    - "SM 和 KOL 同时看好，可能有催化剂"
    - "机构 + 零售共识，趋势可能持续"

  not_meaning:
    - "不是无限上涨"
    - "KOL 可能因付费推广而买入"

  risk:
    - "KOL 共振可能是 FOMO 末期"
    - "需要区分 SM 先买 KOL 后买（健康）vs 同时买（FOMO）"
    - "KOL 买入后可能快速卖出"
```

### L2-A3：ORGANIC_STEALTH_ACCUMULATION

```yaml
structure_candidate:
  name: ORGANIC_STEALTH_ACCUMULATION
  meaning: "低调控量积累——量不大但结构健康，SM 安静进场"

  required_conditions:
    all_of:
      - sm_direction_signal.sm_buy_ratio > 0.5
      - volume_momentum < 1.5                                # 量没有爆发（低调）
      - fresh_wallet_ratio < 0.5                             # 没有大量新人涌入
      - insider_activity_composite < 0.2                     # 无操纵嫌疑

  supporting_signals:
    - top_holder_velocity > 0.3                              # 大仓在动（但不明显）
    - dev_risk_score < 0.3                                   # Dev 风险低
    - social_completeness > 0.5                              # 项目有一定包装

  possible_meaning:
    - "SM 在不被零售注意的情况下积累"
    - "可能是长期项目而非短期 pump"

  risk:
    - "低量也可能只是因为没人关注"
    - "需要更长时间验证"
```

---

## L2-B：分销/出货型结构 (Distribution / Exit Structures)

### L2-B1：SMART_MONEY_DISTRIBUTION

```yaml
structure_candidate:
  name: SMART_MONEY_DISTRIBUTION
  meaning: "聪明钱正在系统性出货"

  required_conditions:
    all_of:
      - sm_direction_signal.sm_buy_ratio < 0.4                # 多数 SM 在卖
      - sm_exit_ratio > 0.3                                   # 至少 30% SM 已清仓过八成
      - volume_momentum > 0.8                                 # 还有量支撑出货

  supporting_signals:
    - sm_profit_status.sm_in_profit_ratio > 0.6               # SM 在盈利中出货
    - kol_direction_signal.kol_buy_ratio > 0.5                # KOL 可能在接盘
    - fresh_wallet_ratio > 0.5                                # 新人在接

  warning_signals:
    - volume_decay_ratio < 0.5                                # 量在快速衰减
    - top_holder_velocity < 0.3                               # 大仓不动了（已出完）

  possible_meaning:
    - "SM 正在把货倒给 KOL 和新人"
    - "价格可能仍在上行但结构在恶化"

  not_meaning:
    - "不是立即崩盘（SM 分批出货可能持续一段时间）"

  risk:
    - "SM 出货后价格可能快速崩塌"
    - "SM 可能只部分止盈，不完全离场"
```

### L2-B2：DEV_DUMP_IN_PROGRESS

```yaml
structure_candidate:
  name: DEV_DUMP_IN_PROGRESS
  meaning: "开发者正在或准备大规模卖出"

  required_conditions:
    any_of:
      - creator_token_status == "creator_hold" AND dev_team_hold_rate > 0.05
      - liquidity_decay_flag < 0.5 AND creator_token_status == "creator_hold"

  supporting_signals:
    - dex_marketing_intensity >= 2                         # dev 在积极营销（可能是出货前造势）
    - fresh_wallet_ratio > 0.5                             # 在拉新人进场
    - buy_dominance > 0.5 AND sm_direction_signal.sm_buy_ratio < 0.4  # 零售在买 SM 在卖

  warning_signals:
    - dev_risk_score > 0.5
    - creator_open_count == 0                              # 首次发币 → rug 概率高
    - twitter_name_change_history not empty                # 有改名历史 → 可疑

  possible_meaning:
    - "Dev 可能在利用营销吸引零售，准备出货"
    - "如果是社区接管 (CTO) 则不同"

  risk:
    - "Dev dump 可能导致价格归零"
    - "Dev 可能在多个钱包中分散持仓，难以完全追踪"
```

### L2-B3：SNIPER_MASS_EXIT

```yaml
structure_candidate:
  name: SNIPER_MASS_EXIT
  meaning: "开盘狙击手集体离场"

  required_conditions:
    all_of:
      - sniper_retention < 0.3                             # 少于 30% 狙击手仍在持有
      - sniper_wallets > 5                                 # 狙击手数量足够
      - time_since_open < 60 min                           # 开盘 1 小时内

  supporting_signals:
    - sell_volume dominance (via buy_dominance < 0.4)
    - price_to_ath_ratio < 0.5                             # 价格已从开盘高点回落

  possible_meaning:
    - "开盘狙击手已获利离场"
    - "价格可能从开盘高点回落后企稳或继续下跌"

  risk:
    - "Sniper 离场后如果 SM 进场接盘，可能是反转信号"
    - "Sniper 离场 + 无 SM 接盘 → 可能归零"
```

---

## L2-C：操纵/风险型结构 (Manipulation / Risk Structures)

### L2-C1：INSIDER_MANIPULATION_DOMINATED

```yaml
structure_candidate:
  name: INSIDER_MANIPULATION_DOMINATED
  meaning: "交易量主要由内部人/捆绑/刷量主导——真实参与极少"

  required_conditions:
    all_of:
      - insider_activity_composite > 0.5                   # 操纵交易占比 > 50%
      - sm_penetration < 0.005                             # SM 几乎不参与
      - smart_degen_count <= 1                              # 至多 1 个 SM

  supporting_signals:
    - is_wash_trading == true                              # 明确刷量
    - wallet_source_convergence > 0.7                      # 钱包同源
    - top_10_holder_rate > 0.5                             # 持仓高度集中
    - dev_risk_score > 0.4                                 # Dev 风险偏高

  possible_meaning:
    - "价格和交易量是人为制造的"
    - "真实参与者极少"
    - "进入后可能无法以合理价格退出"

  not_meaning:
    - "不是一定会 rug（但概率极高）"

  risk:
    - "**高概率亏损**"
    - "操纵者可以在任何时候停止支撑价格"
    - "流动性可能瞬间消失"

  gate_implication: "此结构候选通常应触发 BLOCK 或极端 WATCH"
```

### L2-C2：BOT_WASH_FESTIVAL

```yaml
structure_candidate:
  name: BOT_WASH_FESTIVAL
  meaning: "Bot 刷量活跃但无真实人类参与"

  required_conditions:
    all_of:
      - is_wash_trading == true
      - bot_degen_count > 5 OR bot_degen_rate > 0.3
      - volume_intensity > 3.0                             # 极高换手
      - swap_per_holder > 3.0                             # 每人大量交易

  supporting_signals:
    - buy_sell_count_ratio near 0.5                        # 买卖笔数几乎相等（对倒特征）
    - volume_per_swap < 20                                 # 小单刷量
    - sm_penetration < 0.005

  possible_meaning:
    - "纯 Bot 制造的假活跃"
    - "GMGN trending 排名可能是刷出来的"

  risk:
    - "进入后可能被 Bot 的卖出墙卡住"
```

### L2-C3：LIQUIDITY_TRAP

```yaml
structure_candidate:
  name: LIQUIDITY_TRAP
  meaning: "市场极薄，持仓集中——名义市值虚高，无法支撑真实卖出"

  required_conditions:
    all_of:
      - mcap_to_liquidity_ratio > 50                       # 市值是流动性的 50 倍以上
      - top_10_holder_rate > 0.3                           # Top 10 持仓超 30%
      - liquidity < 50000                                  # 流动性 < $50k

  supporting_signals:
    - top_holder_velocity < 0.3                            # 大仓不活跃
    - liquidity_decay_flag < 0.5                           # 流动性已流失过半

  possible_meaning:
    - "即使价格看起来不错，任何稍大的卖出都会砸穿"
    - "账面利润可能无法兑现"

  risk:
    - "卖出时滑点可能超过 20%"
    - "适合极小额交易，不适合任何规模仓位"

  gate_implication: "此结构候选应触发 WATCH 或 BLOCK（取决于 liquidity 绝对值）"
```

---

## L2-D：生命周期型结构 (Lifecycle Structures)

### L2-D1：EARLY_BREAKOUT_ZONE

```yaml
structure_candidate:
  name: EARLY_BREAKOUT_ZONE
  meaning: "新创建或刚开盘的 token，出现 SM 开始进场的早期信号"

  required_conditions:
    all_of:
      - token_age_minutes < 60                              # 不到 1 小时
      - smart_degen_count >= 1                              # 至少 1 个 SM 在关注
      - volume_momentum > 1.5                               # 量在放大
      - sm_exit_ratio < 0.1                                 # SM 还没有在卖

  supporting_signals:
    - sm_direction_signal.sm_buy_ratio > 0.5
    - insider_activity_composite < 0.5                      # 操纵不过分
    - buy_dominance > 0.5

  warning_signals:
    - dev_risk_score > 0.5                                  # Dev 高风险 → 可能 SM 也被骗
    - sniper_wallets > 20                                   # 大量狙击手 → 开盘抛压
    - is_wash_trading == true

  possible_meaning:
    - "Token 处于关键观察窗口"
    - "SM 正在评估并试探性进场"
    - "可能是十倍机会，也可能是零"

  not_meaning:
    - "不是确认的买入信号"
    - "不是 trend established"

  risk:
    - "极早期数据极不稳定"
    - "SM 可能在几分钟后全部撤出"
    - "rug_ratio 可能在初期不准确"

  gate_implication: "此结构候选应为 WATCH（数据不足以做任何判断）"
```

### L2-D2：DEAD_OR_DYING

```yaml
structure_candidate:
  name: DEAD_OR_DYING
  meaning: "Token 活跃度极低，可能已经死亡或在死亡过程中"

  required_conditions:
    all_of:
      - volume_intensity < 0.05                             # 几乎没有交易
      - volume_decay_ratio < 0.3                            # 量在持续衰减
      - holder_growth_rate <= 0                             # 持有者在减少或不变
      - top_holder_velocity < 0.2                           # 大仓不动

  supporting_signals:
    - liquidity_decay_flag < 0.3                            # 流动性已流失
    - swaps_1h < 5                                          # 一小时不到 5 笔交易

  possible_meaning:
    - "项目已失去市场兴趣"
    - "继续关注的价值极低"
    - "除非出现 CTO 或重大催化剂"

  gate_implication: "此结构候选应触发 BLOCK（浪费研究资源）"
```

### L2-D3：BONDING_CURVE_GRADUATION_WINDOW

```yaml
structure_candidate:
  name: BONDING_CURVE_GRADUATION_WINDOW
  meaning: "Token 即将从 bonding curve 毕业进入 DEX——关键观察窗口"

  required_conditions:
    all_of:
      - is_on_curve == true OR launchpad_status == 1
      - launchpad_progress > 0.7                             # 进度 > 70%
      - bonding_curve_progress_rate > 0.01                   # 有意义的填充速度

  supporting_signals:
    - volume_momentum > 1.5                                  # 买盘加速
    - buy_dominance > 0.55                                   # 买入主导

  possible_meaning:
    - "毕业时可能有流动性事件"
    - "狙击手可能在毕业瞬间介入"
    - "SM 可能在毕业前后评估"

  risk:
    - "毕业不保证上涨，大量 token 毕业后归零"
    - "毕业时可能出现剧烈波动"
```

---

## L2-E：特殊事件型结构 (Special Event Structures)

### L2-E1：COMMUNITY_TAKEOVER_REVIVAL

```yaml
structure_candidate:
  name: COMMUNITY_TAKEOVER_REVIVAL
  meaning: "Dev 已放弃，社区接管后出现复苏迹象"

  required_conditions:
    all_of:
      - cto_flag == 1
      - creator_token_status == "creator_close"              # 原 dev 已清仓
      - cto_quality_check > 0.5                              # CTO 质量好

  supporting_signals:
    - sm_direction_signal.sm_buy_ratio > 0.5
    - volume_momentum > 1.0
    - sm_penetration > 0.01

  warning_signals:
    - insider_activity_composite > 0.4                       # CTO 后仍有操纵
    - dex_marketing_intensity == 0                           # 无营销支撑

  possible_meaning:
    - "CTO 是真实的社区自救"
    - "SM 认可 CTO 后重新入场"
    - "可能是被低估的底部"

  not_meaning:
    - "不是所有 CTO 都会成功"
    - "CTO 不等于只涨不跌"

  risk:
    - "CTO 团伙可能也是 rug 的另一种形式"
    - "没有原 dev 的技术支持，项目可能停滞"
```

### L2-E2：HYPE_CYCLE_PEAK

```yaml
structure_candidate:
  name: HYPE_CYCLE_PEAK
  meaning: "Token 处于炒作周期的高潮——量价齐升但结构可能已恶化"

  required_conditions:
    all_of:
      - price_change_percent1h > 50                          # 1h 涨超 50%
      - volume_momentum > 3.0                                # 量暴增 3 倍以上
      - fresh_wallet_ratio > 0.6                             # 大量新钱包涌入

  supporting_signals:
    - sm_exit_ratio > 0.3                                    # SM 在出货
    - sm_direction_signal.sm_buy_ratio < 0.4                 # SM 偏卖
    - social_completeness > 0.5                              # 有社交炒作

  warning_signals:
    - price_to_ath_ratio near 1.0                            # 接近或突破 ATH
    - sm_profit_status.sm_in_profit_ratio > 0.8              # SM 大幅盈利

  possible_meaning:
    - "当前处于 FOMO 阶段"
    - "SM 可能在利用零售热情出货"
    - "追高风险极高"

  not_meaning:
    - "不是一定会崩（但概率高）"
    - "不是一定不能突破（但风险收益比差）"

  risk:
    - "追高可能在几分钟内亏损 50%+"
    - "SM 卖完后的自由落体可能极快"

  gate_implication: "此结构候选应触发 WATCH 或 PAPER_ONLY（远离真实入场）"
```

### L2-E3：OVERSOLD_BOUNCE_CANDIDATE

```yaml
structure_candidate:
  name: OVERSOLD_BOUNCE_CANDIDATE
  meaning: "价格深度回调后，SM 开始重新关注——可能的反弹结构"

  required_conditions:
    all_of:
      - price_to_ath_ratio < 0.3                             # 价格从 ATH 跌超 70%
      - buy_dominance > 0.5                                  # 买盘开始出现
      - volume_momentum > 1.0                                # 有一定量

  supporting_signals:
    - sm_direction_signal.sm_buy_ratio > 0.5                 # SM 在买
    - sm_profit_status.sm_avg_unrealized_pnl < -0.5          # SM 在亏损（成本区附近）
    - volume_decay_ratio > 1.2                               # 量在回升

  warning_signals:
    - liquidity_decay_flag < 0.2                             # 流动性已极度流失
    - holder_count declining                                 # 持有人仍在减少
    - is_wash_trading == true

  possible_meaning:
    - "超跌后有技术性反弹可能"
    - "SM 在抄底"
    - "但可能是死猫反弹"

  not_meaning:
    - "不是趋势反转确认"
    - "不是底部确认"

  risk:
    - "极度超跌的 token 大概率是 dead，反弹后继续跌"
    - "流动性不足时反弹无法兑现"
```

---

## L2-F：结构健康型 (Healthy Structure)

### L2-F1：HEALTHY_ORGANIC_MARKET

```yaml
structure_candidate:
  name: HEALTHY_ORGANIC_MARKET
  meaning: "市场结构整体健康——有真实参与、无显著操纵、流动性合理"

  required_conditions:
    all_of:
      - sm_penetration > 0.01                                # 有一定 SM 参与
      - insider_activity_composite < 0.2                     # 操纵占比低
      - mcap_to_liquidity_ratio < 30                         # 市场不太薄
      - is_wash_trading == false                             # 无刷量
      - dev_risk_score < 0.3                                 # Dev 风险低

  supporting_signals:
    - top_holder_velocity > 0.3                              # 大仓有活动
    - wallet_source_convergence < 0.5                        # 资金来源分散
    - holder_growth_rate > 0                                 # 持有人稳定或增长

  possible_meaning:
    - "这个 token 的基本市场结构是健康的"
    - "可以作为进一步研究的候选"
    - "在此基础上，再判断方向（累积/分销）"

  not_meaning:
    - "不是买入信号（只说明结构健康，不说明方向）"
    - "不保证不会 rug（dev 可能随时变卦）"

  gate_implication: "此结构候选通常是 WATCH 的准入条件"
```

---

## L2 Structure Candidate 总表

| ID | 名称 | 大类 | 核心判断 | 关键 L1 Feature | Gate 建议 |
|----|------|------|---------|----------------|----------|
| A1 | SMART_MONEY_CONVICTION_ACCUMULATION | 累积 | SM 在积累 | sm_direction, sm_exit, sm_penetration, vol_momentum | WATCH → PAPER |
| A2 | KOL_SM_RESONANCE_ACCUMULATION | 累积 | SM+KOL 共振买 | sm_direction, kol_direction, kol_quality | WATCH → PAPER |
| A3 | ORGANIC_STEALTH_ACCUMULATION | 累积 | 低调积累 | sm_direction, vol_momentum, fresh_wallet | WATCH |
| B1 | SMART_MONEY_DISTRIBUTION | 分销 | SM 在出货 | sm_direction, sm_exit, sm_profit | WATCH (远离入场) |
| B2 | DEV_DUMP_IN_PROGRESS | 分销 | Dev 准备/正在砸盘 | creator_status, dex_marketing, dev_risk | BLOCK |
| B3 | SNIPER_MASS_EXIT | 分销 | 狙击手集体离场 | sniper_retention, time_since_open | WATCH |
| C1 | INSIDER_MANIPULATION_DOMINATED | 操纵 | 内部人主导 | insider_composite, sm_penetration, wallet_convergence | BLOCK |
| C2 | BOT_WASH_FESTIVAL | 操纵 | Bot 刷量 | is_wash_trading, bot_degen, volume_intensity | BLOCK |
| C3 | LIQUIDITY_TRAP | 操纵 | 无法退出 | mcap/liq ratio, top10, liquidity | BLOCK |
| D1 | EARLY_BREAKOUT_ZONE | 生命周期 | 早期观察窗口 | token_age, sm_count, vol_momentum | WATCH |
| D2 | DEAD_OR_DYING | 生命周期 | 已死/将死 | volume_intensity, vol_decay, holder_growth | BLOCK |
| D3 | BONDING_CURVE_GRADUATION_WINDOW | 生命周期 | 即将毕业 | is_on_curve, progress, progress_rate | WATCH |
| E1 | COMMUNITY_TAKEOVER_REVIVAL | 特殊事件 | CTO 复苏 | cto_flag, cto_quality, sm_direction | WATCH |
| E2 | HYPE_CYCLE_PEAK | 特殊事件 | 炒作高潮 | price_change_1h, vol_momentum, fresh_wallet | WATCH (远离) |
| E3 | OVERSOLD_BOUNCE_CANDIDATE | 特殊事件 | 超跌反弹候选 | price/ath, buy_dominance, sm_direction | WATCH |
| F1 | HEALTHY_ORGANIC_MARKET | 结构健康 | 整体健康 | sm_penetration, insider, mcap/liq, dev_risk | WATCH 准入 |

**L2 Structure Candidate 总计：16 个，覆盖 6 个大类。**

---

## L2 的 Gate 映射

```
L2 Structure Candidate → Gate Decision 建议：

BLOCK:
  - INSIDER_MANIPULATION_DOMINATED (C1)
  - BOT_WASH_FESTIVAL (C2)
  - LIQUIDITY_TRAP (C3) [当 liquidity < $10k]
  - DEV_DUMP_IN_PROGRESS (B2)
  - DEAD_OR_DYING (D2)

WATCH:
  - EARLY_BREAKOUT_ZONE (D1)
  - BONDING_CURVE_GRADUATION_WINDOW (D3)
  - SNIPER_MASS_EXIT (B3)
  - ORGANIC_STEALTH_ACCUMULATION (A3)
  - OVERSOLD_BOUNCE_CANDIDATE (E3)
  - HEALTHY_ORGANIC_MARKET (F1)

WATCH → PAPER (需要更多证据):
  - SMART_MONEY_CONVICTION_ACCUMULATION (A1)
  - KOL_SM_RESONANCE_ACCUMULATION (A2)
  - SMART_MONEY_DISTRIBUTION (B1) [PAPER: 验证做空假设]
  - COMMUNITY_TAKEOVER_REVIVAL (E1)
  - HYPE_CYCLE_PEAK (E2) [PAPER: 验证做空/回避假设]
```

---

## 完整架构图

```
GMGN API (230 raw fields)
        │
        ▼
┌──────────────────────────┐
│ PART 0: Canonical Bytes  │  120 直接可用字段
│ (0.1~0.12, 12子类)       │
└──────────┬───────────────┘
           │ 提供输入
           ▼
┌──────────────────────────┐
│ PART 1: L1 Features      │  37 派生指标
│ (A-G, 7类, 含公式)       │  1次计算 = 2+ canonical → 1 feature
└──────────┬───────────────┘
           │ 提供输入
           ▼
┌──────────────────────────┐
│ PART 2: L2 Structure     │  16 结构候选
│ Candidates               │  2次计算 = N features + canonicals → 1 structure
│ (A-F, 6类, 条件组合)     │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Gate Decision            │
│ BLOCK / WATCH / PAPER    │  → meme-trade-gate
└──────────────────────────┘
```

---

---

# PART 3: VWAP 7-Role Framework → GMGN 映射

> 来源：`你的 SIKK 体系里 VWAP 应该被用在市场的哪些位置.md`
> 目的：将 VWAP 方法论中的「7 条深化研究主线」映射到 GMGN 数据环境中
> 关键差异：GMGN 无 L1 bid/ask → 无精确 VWAP → 用 kline/池子数据做近似替代

---

## 3.0 GMGN 环境下的 VWAP 等效物

```yaml
gmgn_vwap_equivalent:
  precise_vwap: "不存在（无 trade-level price × volume）"
  
  closest_approximations:
    kline_vwap_proxy:
      formula: "对于每根 kline: (high + low + close) / 3 作为近似价, amount 作为近似量"
      source: "market kline"
      precision: "粗（依赖 kline resolution）"
      
    pool_implied_cost:
      formula: "pool.base_reserve_value / pool.base_reserve → 近似平均成交价"
      source: "token info / token pool"
      precision: "只反映池子当前状态，不反映窗口内成交"
      
    trending_price:
      formula: "直接使用 GMGN 给的 price + price_change_percent 序列"
      source: "trending / trenches"
      precision: "GMGN 已聚合，无法做窗口化 VWAP"
    
  conclusion: >
    在 GMGN 环境下，无法精确计算 VWAP。
    但 VWAP 的 7 个方法论角色可以映射到 GMGN 的替代指标上。
    「VWAP」在 GMGN 上下文中应理解为「成交成本锚点方法论框架」，
    而非「VWAP 公式的精确计算结果」。
```

---

## 3.1 角色 1：成交成本锚点 → GMGN 映射

```yaml
role_1_cost_anchor:
  vwap_concept: "当前价格相对近期成交成本的位置"
  
  gmgn_equivalents:
    - feature: price_to_ath_ratio (L1-C2)
      role: "价格相对历史最高成交成本的位置"
      
    - feature: price_change_percent1h (canonical)
      role: "短期内的成本偏移方向"
      
    - feature: kline_close_vs_vwap_proxy (需要新增)
      role: "用 kline 近似 VWAP 计算后，比较当前收盘价"
      formula: "close / sum((high+low+close)/3 * amount) / sum(amount)"
      note: "K 线分辨率至少 1m 才有意义"

    - feature: pool_quote_reserve_value / pool.base_reserve_value (canonical)
      role: "池子当前隐含的平均成交价作为成本参考"
      
  gap: >
    缺少精确的 trade-by-trade VWAP。kline 近似只在 1m resolution 下勉强可用。
    GMGN trending 的 price_change 序列可作为方向性替代，但无法做窗口化成本锚定。
```

---

## 3.2 角色 2：市场结构识别 → GMGN 映射

```yaml
role_2_market_structure:
  vwap_concept: "VWAP 在趋势/回归/均衡/不可靠四种结构中承担不同角色"
  
  gmgn_equivalents:
    trend_continuation:
      gmgn_signals:
        - buy_dominance > 0.55 (L1-A1)
        - volume_momentum > 1.5 (L1-B2)
        - sm_direction_signal.sm_buy_ratio > 0.5 (L1-A4)
        - price_change_percent1h > 0 (canonical)
      meaning: "价格方向 + 量 + SM 共振 → 趋势延续候选"
      
    mean_reversion_pressure:
      gmgn_signals:
        - price_to_ath_ratio < 0.3 (L1-C2)
        - buy_dominance > 0.5 (buying after drop) (L1-A1)
        - sm_direction_signal.sm_buy_ratio > 0.5 (L1-A4)
      meaning: "深度回调 + 买盘出现 → 回归压力候选"
      
    balance_zone:
      gmgn_signals:
        - buy_sell_count_ratio near 0.5 (L1-A2)
        - volume_momentum < 1.0 (L1-B2)
        - abs(price_change_percent1h) < 5 (canonical)
      meaning: "买卖均衡 + 低量 → 均衡区"
      
    unreliable_price:
      gmgn_signals:
        - mcap_to_liquidity_ratio > 50 (L1-C1)
        - is_wash_trading == true (canonical)
        - insider_activity_composite > 0.5 (L1-E4)
      meaning: "薄市场/刷量/操纵 → 价格不可靠"
      
  already_mapped:
    - L2-A1: SMART_MONEY_CONVICTION_ACCUMULATION → trend_continuation
    - L2-E3: OVERSOLD_BOUNCE_CANDIDATE → mean_reversion
    - L2-F1: HEALTHY_ORGANIC_MARKET → balance_zone (需确认方向)
    - L2-C1/C2/C3 → unreliable_price
```

---

## 3.3 角色 3：流动性与价格可信度过滤器 → GMGN 映射

```yaml
role_3_liquidity_quality:
  vwap_concept: "VWAP 状态只有在流动性健康时才可信"
  
  gmgn_equivalents:
    spread_proxy:
      - L1-C5: spread_quality_proxy
      - pool.fee_ratio (canonical): 费率越高 → 隐含价差越大
      gap: "无真实 L1 spread，只能用池子储备比率和费率近似"
      
    volume_sufficiency:
      - L1-B1: volume_intensity
      - L1-B2: volume_momentum
      - swaps_1h (canonical)
      
    trade_count_sufficiency:
      - swaps_1h (canonical)
      - L1-B3: swap_per_holder
      
    freshness:
      - L1-F1: token_age_minutes
      - L1-F3: time_since_open
      gap: "无 quote timestamp，无法检测 stale quote"
      
    outlier_detection:
      - L1-E4: insider_activity_composite → 异常交易占比
      - is_wash_trading (canonical) → 刷量标记
      
  current_l2_mapping:
    HEALTHY_VWAP_STATE → HEALTHY_ORGANIC_MARKET (L2-F1)
    DEGRADED_VWAP_STATE → EARLY_BREAKOUT_ZONE (L2-D1, 数据不足)
    INVALID_VWAP_STATE → INSIDER_MANIPULATION_DOMINATED (L2-C1), BOT_WASH_FESTIVAL (L2-C2)
```

---

## 3.4 角色 4：成交参与度与盘口压力 → GMGN 映射

```yaml
role_4_participation_pressure:
  vwap_concept: "价格偏离成本时，买卖压力是否支持这个偏离"
  
  gmgn_equivalents:
    above_cost_with_buy_pressure:
      condition:
        - buy_dominance > 0.55 (L1-A1)
        - sm_direction_signal.sm_buy_ratio > 0.5 (L1-A4)
        - volume_momentum > 1.0 (L1-B2)
      mapped_to: L2-A1 (SMART_MONEY_CONVICTION_ACCUMULATION)
      
    above_cost_with_sell_pressure:
      condition:
        - buy_dominance < 0.45 (L1-A1)
        - sm_direction_signal.sm_buy_ratio < 0.4 (L1-A4)
        - sm_exit_ratio > 0.2 (L1-D2)
      mapped_to: L2-B1 (SMART_MONEY_DISTRIBUTION)
      
    below_cost_with_sell_pressure:
      condition:
        - buy_dominance < 0.45 (L1-A1)
        - sm_exit_ratio > 0.3 (L1-D2)
        - volume_momentum > 1.0 (L1-B2, 放量下跌)
      mapped_to: L2-E2 (HYPE_CYCLE_PEAK, 崩盘侧)
      
    below_cost_with_buy_pressure:
      condition:
        - buy_dominance > 0.5 (L1-A1)
        - sm_direction_signal.sm_buy_ratio > 0.5 (L1-A4)
        - price_to_ath_ratio < 0.3 (L1-C2)
      mapped_to: L2-E3 (OVERSOLD_BOUNCE_CANDIDATE)
      
  gap: >
    VWAP 文档中的 bid_ask_imbalance 是 L1 订单簿概念。
    GMGN 无 L1 订单簿。最佳替代是 buy_dominance + volume_per_swap
    来近似"大单方向"。但这是已成交数据，不是挂单数据，性质不同。
```

---

## 3.5 角色 5：Regime / 市场状态解释 → GMGN 映射

```yaml
role_5_regime_context:
  vwap_concept: "VWAP 在不同 regime 下含义完全不同"
  
  gmgn_regime_definitions:
    trend_regime:
      indicators:
        - price_change_percent1h consistently same sign
        - volume_momentum > 1.0 (sustained)
        - sm_direction_signal consistently biased one way
      gmgn_mapped_structure: L2-A1 (SM 积累), L2-B1 (SM 出货)
      
    range_regime:
      indicators:
        - abs(price_change_percent1h) < 10 (low volatility)
        - buy_sell_count_ratio near 0.5
        - volume_momentum near 1.0
      gmgn_mapped_structure: L2-A3 (静默积累), L2-F1 (健康市场)
      
    high_volatility_regime:
      indicators:
        - abs(price_change_percent5m or 1m) > 20 (large swings)
        - volume_intensity > 3.0
      gmgn_mapped_structure: L2-E2 (炒作高潮), L2-D1 (早期突破)
      
    low_liquidity_regime:
      indicators:
        - mcap_to_liquidity_ratio > 50
        - liquidity_decay_flag < 0.5
      gmgn_mapped_structure: L2-C3 (流动性陷阱), L2-D2 (已死)
      
    event_regime:
      indicators:
        - cto_flag == 1
        - launchpad_progress > 0.9 (即将毕业)
        - dex_marketing_intensity >= 3 (大营销)
      gmgn_mapped_structure: L2-E1 (CTO 复苏), L2-D3 (毕业窗口)
      
  gap: >
    regime 判定需要时间序列数据（多时间点的连续采样），GMGN 单次 API
    调用只给快照。需要 cron job 或多次采样来建立 regime 上下文。
```

---

## 3.6 角色 6：执行质量与归因基准 → GMGN 映射

```yaml
role_6_execution_attribution:
  vwap_concept: "entry/exit 相对 VWAP 的位置用于归因"
  
  gmgn_applicable_fields:
    attribution_candidates:
      entry_vs_pool_price_bps:
        meaning: "入场价相对池子当前隐含价的偏离"
        source: "pool implied price from canonical 0.8"
        
      entry_during_sm_distribution:
        meaning: "是否在 SM 出货阶段入场"
        source: L2-B1 detection at entry time
        
      exit_during_sm_accumulation:
        meaning: "是否在 SM 积累阶段离场"
        source: L2-A1 detection at exit time
        
      slippage_estimate:
        meaning: "预期卖出滑点"
        source: mcap_to_liquidity_ratio (L1-C1) × position_size
        
  gap: >
    GMGN 环境下的归因只能依赖 snapshot 对比，无法做精确的
    entry_vs_vwap_bps 计算。但可以用 SM 方向 + 池子状态 + 流动性
    作为替代归因维度。归因框架的整体设计应独立成后续文档。
  status: DEFERRED_TO_PHASE_2
```

---

## 3.7 角色 7：策略生命周期反馈闭环 → GMGN 映射

```yaml
role_7_lifecycle_feedback:
  vwap_concept: "VWAP 研究结果回流到 SIKK 闭环"
  
  gmgn_lifecycle_mapping:
    raw_evidence:
      gmgn_object: "gmgn-cli 原始 JSON 输出"
      path: "/root/sikk-gmgn/data/runs/<token_address>/raw/"
      
    canonical_observation:
      gmgn_object: "GMGN Canonical Bytes (Part 0)"
      path: "candidate_entry.json / token_panel.json (Phase 1 skills)"
      
    feature_snapshot:
      gmgn_object: "L1 Features (Part 1)"
      path: "token_panel.json extended with L1 computed fields"
      
    structure_candidate:
      gmgn_object: "L2 Structure Candidates (Part 2)"
      path: "evidence_chain.json"
      
    gate_decision:
      gmgn_object: "BLOCK / WATCH / PAPER"
      path: "trade_gate.json"
      
    validation_later (Phase 2):
      gmgn_object: "Paper trading simulation"
      path: "deferred"
      
    attribution_later (Phase 2):
      gmgn_object: "Attribution report"
      path: "deferred"
      
    upgrade_candidate_later (Phase 4+):
      gmgn_object: "Strategy upgrade proposal"
      path: "deferred"
      
  current_boundary: >
    Phase 1 只能到达 structure_candidate + gate_decision。
    validation / attribution / upgrade 全部延后。
```

---

# PART 4: Quality Gate 逐类细化

> 为每个 L1 Feature 类别定义 GMGN 环境下的 quality gate 规范

---

## 4.1 类别 A（买卖压力）Quality Gate

```yaml
qa_category_A:
  common_inputs:
    - buy_volume_1h, sell_volume_1h (canonical 0.2)
    - token holders/traders list (for A4/A5/A6)
    
  quality_status:
    VALID:
      - "volume_1h > 0"
      - "token holders/traders API 返回成功"
      - "sm_direction 至少 3 个 SM 样本 (仅 A4/A6)"
      
    DEGRADED:
      - "volume_1h < $100 (低量，buy_dominance 不稳定)"
      - "SM 样本 1-2 个 (低置信)"
      - "rate limit 导致部分 holder 数据过期"
      
    MISSING:
      - "volume_1h = 0 或 null"
      - "token holders API 返回空"
      - "smart_degen_count = 0 (A4/A6 无法计算)"
      
    INVALID:
      - "buy_volume + sell_volume != volume_1h (数据不一致)"
      - "buy_volume < 0"
      
    STALE:
      - "token info 数据 > 30 min (canonical 过期)"
      - "token holders 数据 > 60 min"
```

---

## 4.2 类别 B（动量）Quality Gate

```yaml
qa_category_B:
  common_formula_pattern: "分母不能为 0"
  
  specific_checks:
    B1_volume_intensity:
      missing: "liquidity = 0"
      degraded: "liquidity < $5000 (薄市场天然高换手)"
      
    B2_volume_momentum:
      missing: "volume_24h = 0"
      degraded: "token_age < 24h (24h 基准不可靠)"
      stale: "volume_24h 数据 > 60 min"
      
    B3_swap_per_holder:
      missing: "holder_count = 0"
      invalid: "swaps_1h > holder_count × 10 (极端异常)"
      
    B4_volume_per_swap:
      missing: "swaps_1h = 0"
      
    B5_volume_decay_ratio:
      missing: "need 2 consecutive hours of kline data"
      degraded: "kline data has gaps"
```

---

## 4.3 类别 C（深度/质量）Quality Gate

```yaml
qa_category_C:
  specific_checks:
    C1_mcap_to_liquidity_ratio:
      missing: "liquidity = 0"
      invalid: "market_cap < liquidity (逻辑异常)"
      
    C2_price_to_ath_ratio:
      missing: "ath_price = 0"
      degraded: "ath_price may be from first candle (新币 ATH 无意义)"
      invalid: "price > ath_price * 2 (数据错误)"
      
    C3_top_holder_velocity:
      missing: "holder_count < 10"
      stale: "holders data > 60 min"
      
    C4_liquidity_decay_flag:
      missing: "initial_liquidity = 0"
      
    C5_spread_quality_proxy:
      missing: "pool data not available (launchpad_status != 2)"
      note: "仅适用于已毕业 token"
```

---

## 4.4 类别 D（钱包智能）Quality Gate

```yaml
qa_category_D:
  critical_dependency: "token holders/traders API (rate limit: weight=5)"
  
  minimum_sample_sizes:
    sm_features (D1/D2/D3): "smart_degen_count >= 3"
    kol_features (D4): "renowned_count >= 1"
    sniper_features (D7): "sniper_wallets >= 5"
    source_convergence (D6): "holder_count >= 10 (至少 10 个 holder 做同源分析)"
    
  quality_status:
    DEGRADED:
      - "SM 样本 1-2 (small sample)"
      - "部分 holder 的 native_transfer.address 为 null"
      
    MISSING:
      - "smart_degen_count = 0 (SM features unavailable)"
      - "token holders API 返回 429 (rate limited)"
      
    STALE:
      - "holders data > 60 min"
      - "rate limit ban 导致无法刷新"
      
  rate_limit_strategy:
    max_concurrent_holder_requests: 3  # token holders weight=5, capacity=10
    priority_order: "SM holders → top 20 → KOL → sniper"
    fallback: "use cached data if within validity window"
```

---

## 4.5 类别 E（Dev 风险）Quality Gate

```yaml
qa_category_E:
  specific_checks:
    E1_dev_risk_score:
      missing:
        - "creator_token_status = null (无 dev 数据)"
        - "twitter_name_change_history cannot be parsed"
      degraded:
        - "creator_open_count = 0 且无可查历史 (新 dev)"
        
    E2_dev_track_record_score:
      missing: "dev.ath_token_info.ath_mc = null (无历史记录)"
      degraded: "creator_open_count = 0 (首次发币，无 track record)"
      
    E3_dex_marketing_intensity:
      note: "4 个 flag 都是 GMGN 直接给的，不需要计算，只做 summation"
      missing: "dev object not available"
      
    E4_insider_activity_composite:
      note: "三个 canonical fields 直接相加"
      invalid: "rat_trader_amount_rate + bundler_rate > 2.0 (overlap)"
      
    E6_cto_quality_check:
      missing: "cto_flag = 0 (not CTO)"
      note: "仅在 cto_flag = 1 时计算，否则返回 NOT_APPLICABLE"
```

---

## 4.6 类别 F（生命周期）Quality Gate

```yaml
qa_category_F:
  specific_checks:
    F1_token_age_minutes:
      invalid: "creation_timestamp > now (未来时间)"
      stale: "需要当前时间戳准确"
      
    F2_bonding_curve_progress_rate:
      missing: "is_on_curve = false (已毕业，无 bonding curve)"
      degraded: "采样间隔 < 2 min (噪声大)"
      invalid: "progress_t2 < progress_t1 (倒退，数据异常)"
      
    F5_holder_growth_rate:
      missing: "只采集了一次 (需要两次采样)"
      degraded: "采样间隔 < 5 min"
      note: "需要 cron job 或两次独立 API 调用"
```

---

## 4.7 类别 G（社交）Quality Gate

```yaml
qa_category_G:
  specific_checks:
    G1_social_completeness:
      note: "纯计数，无计算风险"
      missing: "link object not available"
      
    G2_follower_to_mcap_ratio:
      missing: "market_cap = 0 or x_user_follower = null"
      degraded: "market_cap < $1000 (ratio unstable)"
      
    G3_description_quality_hint:
      note: "纯长度判断"
      missing: "link.description = null"
```

---

# PART 5: L2 Structure Candidate → Allowed / Forbidden Interpretation

> 为每个 L2 Candidate 补全 VWAP 文档风格的 allowed/forbidden 解释边界

---

## 5.1 累积型 (A1-A3)

```yaml
A1_SMART_MONEY_CONVICTION_ACCUMULATION:
  allowed:
    - "当前 SM 群体的买入意愿强于卖出意愿"
    - "SM 持仓尚未大规模清仓"
    - "可能是趋势积累阶段"
    - "需要配合 L2-F1（健康市场）确认结构基础"
  forbidden:
    - "SM 在买所以我也该买"
    - "这是买入信号"
    - "价格一定会上涨"
    - "可以直接进入 paper trading"

A2_KOL_SM_RESONANCE_ACCUMULATION:
  allowed:
    - "SM 和 KOL 同时偏买入"
    - "可能存在催化剂或信息优势"
    - "SM 先买 KOL 后买的顺序比同时买更健康"
  forbidden:
    - "SM + KOL 共振 = 必涨"
    - "KOL 买入 = 真实看好（可能是付费）"
    - "共振强度 = 仓位大小"

A3_ORGANIC_STEALTH_ACCUMULATION:
  allowed:
    - "SM 在低量、低关注度下积累"
    - "可能是长期项目特征"
    - "需要更长时间验证"
  forbidden:
    - "低量积累 = 一定会拉升"
    - "没有新人关注 = 被低估（也可能是无人问津）"
```

---

## 5.2 分销型 (B1-B3)

```yaml
B1_SMART_MONEY_DISTRIBUTION:
  allowed:
    - "SM 群体的卖出意愿强于买入意愿"
    - "SM 正在系统性降低仓位"
    - "KOL 在 SM 出货时买入 = 可能是接盘"
    - "价格可能仍在上涨但结构恶化"
  forbidden:
    - "SM 在卖所以应该立即做空"
    - "SM 卖出 = 崩盘（SM 可能只部分止盈）"
    - "SM 出货速度 = 崩盘时间"

B2_DEV_DUMP_IN_PROGRESS:
  allowed:
    - "Dev 仍在持有可能卖出的仓位"
    - "Dev 在积极营销可能是在造势出货"
    - "新钱包涌入 + Dev 持仓 = 出货对象"
  forbidden:
    - "Dev 一定会 dump"
    - "Dev 持仓 = 一定 rug（有些 dev 长期持有）"
    - "营销投入 = 真实项目（也可能是 pump and dump）"

B3_SNIPER_MASS_EXIT:
  allowed:
    - "开盘狙击手正在或已经大量离场"
    - "开盘初期的抛压正在释放"
    - "SM 是否接盘是下一步关键"
  forbidden:
    - "狙击手离场 = 可以抄底"
    - "狙击手离场完毕 = 底部确认"
```

---

## 5.3 操纵型 (C1-C3)

```yaml
C1_INSIDER_MANIPULATION_DOMINATED:
  allowed:
    - "交易量主要由操纵行为构成"
    - "真实参与度极低"
    - "SM 几乎不参与"
    - "高概率不适合任何真实仓位"
  forbidden:
    - "操纵 = 一定 rug"
    - "存在操纵 = 反向操作机会"

C2_BOT_WASH_FESTIVAL:
  allowed:
    - "交易活动主要是 Bot 刷量"
    - "GMGN trending 排名可能是虚假的"
    - "买卖笔数高度对称是对倒特征"
  forbidden:
    - "刷量 = 有人在维护价格（可能是陷阱）"
    - "刷量中仍可获利"

C3_LIQUIDITY_TRAP:
  allowed:
    - "当前流动性不支持有意义的卖出"
    - "任何超过流动性 1% 的卖出都可能产生显著滑点"
    - "账面利润可能无法兑现"
  forbidden:
    - "流动性低 = 可以小仓位试试"
    - "流动性低 = 价格会涨到流动性增加"
```

---

## 5.4 生命周期型 (D1-D3)

```yaml
D1_EARLY_BREAKOUT_ZONE:
  allowed:
    - "Token 处于非常早期的阶段"
    - "已有初步 SM 关注"
    - "数据不足以做出任何确定性判断"
  forbidden:
    - "SM 在关注 = 可以买"
    - "早期 = 十倍机会"
    - "早期数据 = 可靠信号"

D2_DEAD_OR_DYING:
  allowed:
    - "Token 几乎无交易活动"
    - "持有人正在减少"
    - "流动性已大幅流失"
    - "继续研究的时间成本 > 预期收益"
  forbidden:
    - "已死 = 绝对零价值（可能有 CTO 复活）"
    - "已死 = 可以抄底等复活"

D3_BONDING_CURVE_GRADUATION_WINDOW:
  allowed:
    - "Token 即将从 bonding curve 毕业"
    - "毕业瞬间可能有流动性冲击"
    - "毕业后的 5-30 min 是关键观察窗口"
  forbidden:
    - "毕业 = 会涨"
    - "毕业 = 可以提前埋伏"
    - "毕业后一定会被 sniper 砸"
```

---

## 5.5 特殊事件型 (E1-E3)

```yaml
E1_COMMUNITY_TAKEOVER_REVIVAL:
  allowed:
    - "Dev 已清仓离开"
    - "社区接管后出现复苏迹象"
    - "SM 认可 CTO 并重新入场"
    - "但 CTO 本身不保证成功"
  forbidden:
    - "CTO = 好项目"
    - "CTO 后一定会涨"
    - "CTO 团队 = 值得信任"

E2_HYPE_CYCLE_PEAK:
  allowed:
    - "Token 处于极端 FOMO 阶段"
    - "大量新钱包涌入，SM 可能在出货"
    - "追高风险极高"
    - "价格可能在几分钟内反转"
  forbidden:
    - "涨得快 = 还会涨"
    - "FOMO = 可以跟风赚钱"
    - "新钱包多 = 真实热度"

E3_OVERSOLD_BOUNCE_CANDIDATE:
  allowed:
    - "价格深度回调后出现买盘"
    - "SM 在超卖区开始关注"
    - "可能是反弹，也可能是死猫跳"
  forbidden:
    - "超跌 = 可以抄底"
    - "SM 在买 = 底部确认"
    - "反弹 = 趋势反转"
```

---

## 5.6 结构健康型 (F1)

```yaml
F1_HEALTHY_ORGANIC_MARKET:
  allowed:
    - "市场结构没有明显操纵或风险信号"
    - "有一定真实参与度"
    - "可以作为进一步研究的候选"
    - "但不说明方向"
  forbidden:
    - "健康 = 可以买"
    - "健康 = 不会 rug"
    - "健康 = 可以跳过 gate"
```

---

# PART 6: Gap Analysis — 当前缺失

```yaml
gaps:
  gap_001:
    name: "无精确 VWAP 计算能力"
    severity: high
    impact: "成交成本锚点只能靠 kline 近似"
    mitigation: "使用 1m kline 做 (high+low+close)/3 × amount 近似 VWAP"
    new_feature_needed: "L1-B6: kline_vwap_proxy"
    
  gap_002:
    name: "无真实 L1 spread/bid-ask"
    severity: medium
    impact: "无法精确判断当前价差质量"
    mitigation: "使用 pool 储备比率 + fee_ratio 做代理"
    existing: L1-C5
    
  gap_003:
    name: "无 quote freshness / stale detection"
    severity: medium
    impact: "无法判断数据是否过期"
    mitigation: "依赖 GMGN API 的 updated_at / 自己的采样时间戳比较"
    note: "GMGN 不暴露 timestamp 精度，只能信任 API 响应的时效性"
    
  gap_004:
    name: "缺少连续时间序列采样能力"
    severity: high
    impact: "regime 识别 / holder_growth_rate / volume_decay 等需要两次采样"
    mitigation: "Phase 3 引入 cron job 定时采样"
    
  gap_005:
    name: "阈值未校准"
    severity: high
    impact: "所有 L1/L2 的 > / < 阈值均为经验设定"
    mitigation: "需要历史数据回测，但 Phase 1 不要求精确阈值"
    
  gap_006:
    name: "token holders API rate limit"
    severity: medium
    impact: "A4/A5/A6/D2/D3/D4/D6/D7 等 8 个 L1 features 依赖此 API"
    mitigation: "缓存 + 优先级排序 + 限制并发"
    
  gap_007:
    name: "regime labeling 机制缺失"
    severity: medium
    impact: "无法自动判断当前属于 trend/range/volatile/low_liq/event 哪种 regime"
    mitigation: "Phase 2+ 设计 regime classifier"
```

---

## 下一步

1. **阈值校准**：L1 和 L2 中的阈值（如 `volume_momentum > 1.5`）需要历史数据回测校准 → `03-GMGN-阈值校准与回测设计.md`
2. **Phase 1 Skill 映射**：对已有 skills (meme-candidate-entry → meme-trade-gate) 逐 skill 映射 L1 feature 输入 / L2 structure 输出
3. **quality gate 代码化**：Part 4 的 quality gate 规范需要转为可执行的 validator
4. **kline VWAP proxy**：新增 L1-B6 feature 实现 kline 近似 VWAP
5. **采样间隔**：L1-F2/F5 需要两次采样，定义最小采样间隔
6. **regime classifier**：延后至 Phase 2+

---

> 本文档状态：RESEARCH_IN_PROGRESS（第三轮细化完成）
> 对应 Phase：Phase 1 Research Pipeline
> 后续文档：
>   - 03-GMGN-阈值校准与回测设计.md（待产出）
>   - 04-GMGN-Phase1-Skill映射.md（待产出）
