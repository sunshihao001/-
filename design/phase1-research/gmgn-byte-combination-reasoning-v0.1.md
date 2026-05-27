# GMGN 字节组合推理链：L1 Feature + L2 Structure Candidate 逐条展开

> 格式：每条 = 推理链 → 输入字节 → 功能
> 状态：RESEARCH_IN_PROGRESS
> 前提：Phase 1 read-only，不输出 buy/sell

---

## L1-A：买卖压力特征（6 条）

---

### L1-A1：buy_dominance

**推理链**
```
市场中每一笔 swap 都有方向（买或卖）。
如果只看总交易量 volume，无法区分是买入驱动还是卖出驱动。
GMGN 已经把 1h 窗口内的 buy_volume 和 sell_volume 分开给了。

但「买入 $50k + 卖出 $50k」和「买入 $90k + 卖出 $10k」
总交易量都是 $100k，市场含义完全不同。

因此需要计算 buy_dominance = buy_1h / (buy_1h + sell_1h)。
这个值在 [0,1] 之间，0.5 是均衡线。
>0.6 说明买方主导，<0.4 说明卖方主导。

但 buy_dominance 不够——高 buy_dominance 可能是
鲸鱼一单大买（有意义）或散户 FOMO 追高（危险）。
所以需要配合 L1-A2（笔数比）来区分。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `buy_volume_1h` | token info (price.buy_volume_1h) | USD string |
| `sell_volume_1h` | token info (price.sell_volume_1h) | USD string |

**功能**
```
回答：过去 1 小时内，买入资金占总交易资金的比例是多少？
下游消费：L2-A1（SM 积累）、L2-B1（SM 出货）、L2-E2（炒作高潮）
不可单独作为信号：高 buy_dominance 可能是 FOMO 陷阱
```

---

### L1-A2：buy_sell_count_ratio

**推理链**
```
L1-A1 只看了「钱的方向」，没看「人的方向」。
同样 $50k 买入量，可能是：
- 1 笔大单 $50k（鲸鱼进场）
- 500 笔 $100（散户 FOMO）

这两种情况的含义截然不同。
GMGN 给了 buys_1h（买入笔数）和 sells_1h（卖出笔数）。

计算 buy_sell_count_ratio = buys_1h / (buys_1h + sells_1h)。

和 L1-A1 配对使用，形成 2×2 矩阵：
- buy_dominance 高 + count_ratio 低 → 少数大单买入 → 鲸鱼/SM 行为
- buy_dominance 高 + count_ratio 高 → 多数小单买入 → FOMO
- buy_dominance 低 + count_ratio 低 → 少数大单卖出 → 大户离场
- buy_dominance 低 + count_ratio 高 → 多数小单卖出 → 恐慌
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `buys_1h` | token info (price.buys_1h) | integer |
| `sells_1h` | token info (price.sells_1h) | integer |

**功能**
```
回答：过去 1 小时内，买入笔数占总交易笔数的比例是多少？
必须与 L1-A1 配对使用：区分「少数大单」vs「多数小单」
下游消费：L2-D1（早期突破，区分真实买盘 vs Bot 刷量）
```

---

### L1-A3：net_flow_intensity

**推理链**
```
net_flow = buy_volume - sell_volume 告诉你净方向。
但 $10k 净买入对一个 $1M 流动性的池子和一个 $10k 流动性的池子
冲击完全不同。

因此要把 net_flow 除以 liquidity，得到「净流向相对池子深度的压力强度」。

例如：
- net_flow = $5k, liquidity = $10k → intensity = 0.5（半个池子被净买入，冲击大）
- net_flow = $5k, liquidity = $500k → intensity = 0.01（微不足道）

这个比值告诉你当前买卖失衡对价格的实际推动力。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `buy_volume_1h` | token info | USD string |
| `sell_volume_1h` | token info | USD string |
| `liquidity` | token info / trending | USD float |

**功能**
```
回答：净买卖压力相对池子深度的强度有多大？
绝对值大 = 当前流向可能推动显著价格变化
绝对值小 = 虽有方向但力量不足
下游消费：判断价格变动是被真实资金驱动还是薄流动性放大
```

---

### L1-A4：sm_direction_signal

**推理链**
```
GMGN 标记了 smart_degen 钱包（历史高胜率交易者）。
如果只看 token 级别的 buy_volume，不知道是谁在买。
但如果能单独看 SM 群体的行为方向，信息量完全不同。

SM 是经过 GMGN 算法筛选的「聪明钱」。
他们对单个 token 的买入/卖出行为是重要的参考信号。

推理步骤：
1. 调用 token traders --tag smart_degen 获取 SM 群体数据
2. 对每个 SM 看 netflow_usd（GMGN 已算好的净 USD 流）
3. 聚合：sum(netflow_usd) 得到 SM 整体净方向
4. 计算 sm_buy_ratio = count(SM netflow>0) / count(SM)

如果多数 SM 在净买入 → 专业交易者看好
如果多数 SM 在净卖出 → 专业交易者在离场
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `netflow_usd` | token traders (per SM) | USD float |
| `buy_volume_cur` | token traders (per SM) | USD float |
| `sell_volume_cur` | token traders (per SM) | USD float |
| `tags` | token traders (per SM) | array (filter: smart_degen) |

**功能**
```
回答：聪明钱群体在这个 token 上当前是净买入还是净卖出？
这是最核心的「聪明钱方向」信号。
下游消费：L2-A1（SM 积累）、L2-B1（SM 出货）的直接输入
不可独立使用：SM 可能在摊平亏损而非看好
```

---

### L1-A5：kol_direction_signal

**推理链**
```
KOL（renowned）钱包是 GMGN 标记的知名钱包。
和 SM 不同，KOL 的行为可能包含：真实看好、付费推广、滞后跟风。

因此 KOL 方向不能独立看，必须和 SM 方向对比：
- SM 买 + KOL 买 → SM 和 KOL 共振，强信号
- SM 买 + KOL 不买 → SM 在独自积累，KOL 还没注意到
- SM 卖 + KOL 买 → SM 在出货给 KOL 的粉丝，危险信号
- SM 不买 + KOL 买 → 可能是付费推广，无 SM 背书

这就是为什么需要同时算 SM 和 KOL 两个方向。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `netflow_usd` | token traders (per KOL) | USD float |
| `buy_volume_cur` | token traders (per KOL) | USD float |
| `sell_volume_cur` | token traders (per KOL) | USD float |
| `tags` | token traders (per KOL) | array (filter: renowned) |

**功能**
```
回答：KOL 群体当前是净买入还是净卖出？与 SM 方向对比。
SM + KOL 共振 = 最强累积信号
SM 卖 + KOL 买 = SM 可能在把货倒给 KOL 粉丝
```

---

### L1-A6：volume_weighted_sm_conviction

**推理链**
```
L1-A4 只看 SM 的「净方向」，但没考虑「仓位大小」。
两个 SM 都净买入 $1000：
- SM-A 持有总供应的 5%（大户重仓买入）
- SM-B 持有总供应的 0.01%（试探性小额买入）

这两种行为的「信念强度」完全不同。

因此需要仓位加权：
conviction_i = sign(netflow_usd_i) × amount_percentage_i

amount_percentage 越大 → 这个 SM 的买入/卖出越有分量。
不只看方向，还看「用仓位投票的力度」。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `netflow_usd` | token holders (per SM) | USD float |
| `amount_percentage` | token holders (per SM) | float (0-1) |
| `tags` | token holders | array (filter: smart_degen) |

**功能**
```
回答：SM 群体用仓位投票的加权方向强度。
大仓 SM 的买入远重于小仓 SM 的试探。
正值大 = 大仓 SM 在积极加仓
负值大 = 大仓 SM 在积极减仓
```

---

## L1-B：成交量/动量特征（5 条）

---

### L1-B1：volume_intensity

**推理链**
```
liquidity 是池子深度——一次可以交易的量。
volume_1h 是 1 小时内的实际交易量。

volume_intensity = volume_1h / liquidity

这个比值告诉你流动性被「翻动」了多少次。
如果 liquidity = $100k，volume_1h = $300k → intensity = 3
意味着池子被交易了 3 遍。

正常市场：0.1-1.0（池子部分被交易）
活跃市场：1.0-2.0
极端市场：>3.0（可能是 pump/dump 或 Bot 刷量）

但这个值本身不区分「谁在交易」。
需要配合 L1-E4（insider_activity_composite）判断是否真实交易。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `volume_1h` | token info / trenches | USD float |
| `liquidity` | token info / trending | USD float |

**功能**
```
回答：流动性在 1 小时内被翻动了多少遍？
>3.0 = 极高换手，可能是 pump/dump/刷量
<0.1 = 几乎无交易，可能是死 token
下游消费：L2-C2（Bot 刷量）、L2-D2（死 token）
```

---

### L1-B2：volume_momentum

**推理链**
```
volume_1h 给的是绝对量。但 $50k 交易量对于不同 token 含义不同：
- 平时每小时 $10k → $50k 是爆发
- 平时每小时 $200k → $50k 是萎缩

因此需要相对基准：volume_momentum = volume_1h / (volume_24h / 24)

24h 均分到每小时 = 平均小时交易量，作为基准线。

>3.0 = 爆发式放量（相对于近期正常水平翻 3 倍以上）
1.0-1.5 = 正常
<0.5 = 显著缩量

爆发式放量 → 可能有催化剂或操纵
缩量 → 兴趣在消退
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `volume_1h` | token info / trenches | USD float |
| `volume_24h` | trenches | USD float |

**功能**
```
回答：当前 1h 交易量相对于近 24h 平均水平的倍数。
>3x = 异常放量 → 检查是否伴随 SM 动作
<0.5x = 缩量 → 市场兴趣消退
下游消费：几乎所有 L2 candidates 的 supporting signal
```

---

### L1-B3：swap_per_holder

**推理链**
```
swaps_1h 是总交易笔数，holder_count 是持有人数。
比值 = 平均每个持有人做了多少笔交易。

如果 100 个持有人，swaps = 50 → swap/holder = 0.5 → 一半人交易了一次
如果 100 个持有人，swaps = 500 → swap/holder = 5 → 平均每人交易 5 次

高 swap/holder 有两种可能：
1. 真实高频参与（市场极度活跃）
2. Bot 刷量（少数钱包反复对倒）

需要配合 L1-B4（volume_per_swap）和 L1-E4（insider_activity）
来区分真实活跃和 Bot 刷量。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `swaps_1h` | token info (price.swaps_1h) | integer |
| `holder_count` | token info | integer |

**功能**
```
回答：每个持有人平均参与了多少笔交易？
>3.0 → 需要警惕：是真实高度活跃还是 Bot 刷量？
<0.1 → 大部分持有者不交易，可能是死仓
配 L1-B4 + L1-E4 判断真实性
```

---

### L1-B4：volume_per_swap

**推理链**
```
volume_1h / swaps_1h = 每笔 swap 的平均金额。

这个值区分「大单市场」和「散单市场」：
- $500+/swap → 大单主导 → 可能是鲸鱼/SM/机构
- $50-$500/swap → 混合
- <$50/swap → 散户主导

和 L1-A2（笔数比）配对：
- 高 volume_per_swap + 低 count_ratio → 少数大单，有意义
- 低 volume_per_swap + 高 count_ratio → 多数小单，FOMO/恐慌
- 低 volume_per_swap + 笔数极多 → Bot 对倒（L2-C2）
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `volume_1h` | token info | USD float |
| `swaps_1h` | token info (price.swaps_1h) | integer |

**功能**
```
回答：每笔交易平均金额是多少？
大单 + 少量 = SM/鲸鱼行为 → L2-A1
小单 + 大量 = 散户 FOMO → L2-E2
极小单 + 极多量 = Bot 对倒 → L2-C2
```

---

### L1-B5：volume_decay_ratio

**推理链**
```
volume_momentum 告诉你当前相比 24h 平均如何。
但 24h 平均可能被 23 小时前的旧数据平滑掉。
更敏感的指标是：最近 1h vs 前面 1h。

volume_decay_ratio = volume_1h / volume_previous_1h

这个值直接检测「量的加速或衰减」：
>1.5 → 量在加速（关注度上升）
<0.5 → 量在快速衰减（兴趣在消失）

这是最短期的动量变化检测。需要两段连续的 kline 数据。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `volume` (kline, current 1h) | market kline | USD |
| `volume` (kline, previous 1h) | market kline | USD |

**功能**
```
回答：最近 1h 交易量相比前 1h 是在加速还是衰减？
>1.5 = 加速放量 → 关注窗口
<0.5 = 快速萎缩 → 可能是 pump 后的冷却
下游消费：L2-D1（早期突破）、L2-D2（死亡确认）
```

---

## L1-C：市场深度/质量特征（5 条）

---

### L1-C1：mcap_to_liquidity_ratio

**推理链**
```
market_cap 是「名义总价值」——所有 token × 当前价格。
liquidity 是「实际可交易的资金」——池子里有多少钱可以接你的卖单。

这两个值在 Solana Meme 市场经常极度不匹配：
- mcap = $10M，liquidity = $50k → ratio = 200
  意味着你卖出的金额超过 $500（流动性的 1%）就会产生显著滑点。
  账面市值 $10M 只是纸面富贵，无法兑现。

- mcap = $100k，liquidity = $50k → ratio = 2
  流动性深度好，可以支撑真实交易。

这个比值是 GMGN 环境下最接近「市场薄度」的度量。
VWAP 文档中的 spread 在 GMGN 中只能用这个近似。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `market_cap` | trending | USD float |
| `liquidity` | token info / trending | USD float |

**功能**
```
回答：名义市值是实际流动性的多少倍？
>50 = 极薄 → 任何稍大的卖出都会砸穿 → L2-C3（流动性陷阱）
<10 = 合理 → 可以支撑有意义的仓位
这是 GMGN 环境下最重要的「价格可信度」指标
```

---

### L1-C2：price_to_ath_ratio

**推理链**
```
ath_price 是这个 token 历史上达到的最高价。
price / ath_price 告诉你当前价格相对历史高点的位置。

这个值的意义取决于 token 的生命周期：
- 刚开盘 5min，ATH 就是开盘价 → ratio near 1.0，无信息量
- 已经 2 小时，ATH 是 $0.01，现在 $0.002 → ratio = 0.2

ratio 低于 0.3 = 深度回调。此时需要看：
- SM 是否在回调中买入？（L1-A4） → 可能是积累
- SM 是否在回调中继续卖？（L1-D2） → 可能是归零

ratio 高于 0.9 = 接近新高。此时需要看：
- SM 是在追高还是在出货？→ L2-E2 炒作高潮
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `price` | token info / trending | USD float |
| `ath_price` | token info | USD float |

**功能**
```
回答：当前价格在历史高点的什么位置？
<0.3 + SM 在买 → L2-E3（超跌反弹候选）
<0.3 + SM 在卖 → 归零风险
>0.9 + SM 在卖 → L2-E2（炒作高潮）
新 token（<5min）的 ATH 无参考意义
```

---

### L1-C3：top_holder_velocity

**推理链**
```
top_10_holder_rate 告诉你「大仓拿了多少货」，但是静态的。
你不知道这些大仓是「死仓」（创建后从未动过）还是「活跃仓」（在操作）。

top_holder_velocity 检查 Top 10 持有者的 last_active_timestamp。
如果在最近 1h 内活跃 → 这个大仓是「活的」，可能在操作。
如果很久没动 → 可能是死仓或长期持有。

高 velocity = 大仓在动 → 可能发生重大变化
低 velocity = 大仓不动 → 当前价格波动可能是散户主导
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `amount_percentage` | token holders (top 10) | float |
| `last_active_timestamp` | token holders (top 10) | unix seconds |

**功能**
```
回答：Top 10 大仓中有多少个在最近 1h 内有活动？
>0.7 = 大仓活跃 → 可能正在发生持仓变化
<0.3 = 大仓不动 → 价格波动可能来自散户
下游消费：L2-B1（SM 出货确认）、L2-D2（死 token 确认）
```

---

### L1-C4：liquidity_decay_flag

**推理链**
```
liquidity 是当前的池子深度。
initial_liquidity 是池子创建时的初始深度（GMGN 给了这个字段）。

liquidity / initial_liquidity = 流动性保留率。

如果初始 $100k，现在 $30k → ratio = 0.3（流失了 70%）
如果初始 $100k，现在 $120k → ratio = 1.2（增长了）

大幅流失 → 可能是 LP 撤出 → dev 可能在跑路
但这个解释需要配合 creator_token_status：
- liquidity 流失 + creator_token_status = hold → dev 还没卖但在准备
- liquidity 流失 + creator_token_status = close → dev 已清仓，池子自然萎缩
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `liquidity` | token info | USD float |
| `initial_liquidity` | trending | USD float |

**功能**
```
回答：流动性相比初始时保留了多少？
<0.3 = 流失超过 70% → 检查是否是 LP rug
配合 creator_token_status 判断：
  dev hold + 流动性流失 → L2-B2（Dev 准备 dump）
  dev close + 流动性流失 → 可能是正常萎缩或 L2-D2
```

---

### L1-C5：spread_quality_proxy

**推理链**
```
在 CEX 环境里，spread = (ask - bid) / mid_price。
但 GMGN 不给订单簿数据——你拿不到 bid/ask。

替代方案：用池子储备比率来近似价差质量。
在 AMM 池中，quote_reserve / base_reserve 决定了当前隐含价格。
两个储备越均衡，隐含价差越小。
极端失衡 → 一根 token 有大量 quote 支撑或反过来 → 价差大。

这只是一个近似，精度远不如真实 L1 spread。
但对于 GMGN 环境，这是唯一可行的「价差代理」。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `pool.quote_reserve_value` | token info | USD float |
| `pool.base_reserve_value` | token info | USD float |
| `pool.fee_ratio` | token info | float |

**功能**
```
回答：池子储备结构是否健康？（价差代理）
均衡 ≈ 正常价差
严重失衡 ≈ 价差可能很大 → 交易成本高
仅在已毕业 token（launchpad_status=2）可用
```

---

## L1-D：钱包智能特征（7 条）

---

### L1-D1：sm_penetration

**推理链**
```
有 SM 参与 ≠ SM 深度参与。
如果 1 个 SM 在 10000 个持有人中 → 0.01%，SM 只是「路过」
如果 50 个 SM 在 1000 个持有人中 → 5%，SM 在「深耕」

sm_penetration = smart_degen_count / holder_count
这个比值反映了 SM 在这个 token 上的「渗透深度」。

高渗透率意味着：
- SM 群体对这个 token 的共识较强
- 但不代表 SM 看涨——也可能 SM 在看跌做空（但 Meme 币一般不做空）

需要配合 L1-A4（SM 方向）来确认渗透 + 方向。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `smart_degen_count` | wallet_tags_stat / trending | integer |
| `holder_count` | token info | integer |

**功能**
```
回答：SM 占总持有人的比例是多少？
>0.05 = SM 深度参与 → 重点关注
<0.01 = SM 只是路过 → 弱信号
下游消费：L2-A1（SM 积累的前置条件）、L2-C1（无 SM=操纵信号）
```

---

### L1-D2：sm_exit_ratio

**推理链**
```
SM 可以「还在持有」但已经开始减持。
sell_amount_percentage 是 GMGN 给出的已卖出比例。
1.0 = 全清了，0.5 = 卖了一半，0 = 还全仓在。

sm_exit_ratio = count(SM 中 sell_amount_percentage > 0.8) / smart_degen_count

如果 10 个 SM 中有 6 个已清仓超过 80% → exit_ratio = 0.6
这是一个强烈的离场信号。

但 sell_amount_percentage 只反映「已发生」，不反映「意图」。
SM 可能清仓后重新入场。所以需要结合 L1-A4 当前的 SM 方向。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `sell_amount_percentage` | token holders (per SM) | float (0-1) |
| `tags` | token holders | array (filter: smart_degen) |
| `smart_degen_count` | wallet_tags_stat | integer |

**功能**
```
回答：SM 群体中有多少已经清仓超过 80%？
>0.5 = 半数 SM 已离场 → L2-B1（SM 系统性出货）
<0.2 = SM 基本还在 → 尚未到出货阶段
下游消费：L2-A1（积累确认：exit_ratio 必须低）、L2-B1（出货核心条件）
```

---

### L1-D3：sm_profit_status

**推理链**
```
SM 在盈利中卖出和 SM 在亏损中卖出，含义完全不同。
- SM 盈利 + 开始卖 → 获利了结，健康的止盈
- SM 亏损 + 还在买 → 摊平成本，可能有内幕信心
- SM 亏损 + 开始卖 → 认赔出局，极空信号

sm_profit_status 输出两个值：
1. sm_in_profit_ratio：SM 中 unrealized_profit > 0 的比例
2. sm_avg_unrealized_pnl：SM 平均未实现盈亏比

如果 80% SM 在盈利 + 平均 PnL > 2.0 → SM 大幅盈利
→ 获利了结动机强 → 配合 L1-D2 看是否在卖
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `unrealized_profit` | token holders (per SM) | USD float |
| `unrealized_pnl` | token holders (per SM) | float |
| `tags` | token holders | array (filter: smart_degen) |

**功能**
```
回答：SM 当前处于盈利还是亏损状态？盈利程度有多大？
SM 大幅盈利 + 开始卖 → 获利了结，预期内
SM 亏损 + 还在买 → 可能是抄底信心或摊平
SM 亏损 + 开始卖 → 认赔，极空信号
```

---

### L1-D4：kol_quality_flag

**推理链**
```
renowned_count 告诉你 KOL 数量，但不告诉你 KOL 参与深度。
一个 KOL 持有 0.0001% 供应（几乎可以忽略）和
一个 KOL 持有 0.5% 供应（实质参与），完全不同。

kol_quality_flag = count(KOL 中 amount_percentage > 0.001) / renowned_count

>0.5 = 多数 KOL 有实质持仓 → 不是走过场
<0.2 = KOL 持仓极小 → 可能只是路过式参与或付费推广

配合 L1-A5 的 KOL 方向：
- KOL 实质持仓 + KOL 在买 → 真实看好
- KOL 极小持仓 + KOL 在买 → 可能是付费推广
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `amount_percentage` | token holders (per KOL) | float (0-1) |
| `tags` | token holders | array (filter: renowned) |
| `renowned_count` | wallet_tags_stat | integer |

**功能**
```
回答：KOL 的持仓是实质性的还是路过式的？
>0.5 = 多数 KOL 有真金白银在里面
<0.2 = KOL 只是做样子 → 弱信号
配合 L1-A5 判断 KOL 参与的真实性
```

---

### L1-D5：fresh_wallet_ratio

**推理链**
```
fresh_wallets 是新创建的钱包（无历史交易记录）。
这些钱包涌入 token 可能是：
1. 真实新用户 → 项目在出圈
2. 项目方/庄家创建的新钱包 → 分散持仓、制造热度假象
3. Bot 钱包 → 刷量

区分方法：
- fresh_wallet_ratio 高 + SM 在买 → 可能是真实热度扩散
- fresh_wallet_ratio 高 + SM 在卖 → 新人接盘，SM 在出货
- fresh_wallet_ratio 高 + is_wash_trading = true → Bot 钱包

GMGN 直接给了 fresh_wallets 数量（wallet_tags_stat.fresh_wallets），
所以这个 L1 实际上不需要复杂计算。
但它的「解释」必须配合其他特征。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `fresh_wallets` | wallet_tags_stat | integer |
| `holder_count` | token info | integer |

**功能**
```
回答：新钱包占总持有人的比例？
配合 SM 方向判断：新人是来接盘的还是真实新用户？
下游消费：L2-E2（炒作高潮——大量新人涌入 + SM 在卖）
```

---

### L1-D6：wallet_source_convergence

**推理链**
```
GMGN 在 token holders 中给了 native_transfer.address——
这个钱包的第一笔 SOL/ETH 是从哪个地址转来的。

如果 Top 20 持有者的资金来源都是同一个地址 →
这些「不同钱包」实际上是同一个人/实体控制的。
这是链上 Sybil 检测的核心方法。

convergence 高 = 资金来源高度集中 → 同源钱包 → 可能是庄家
convergence 低 = 资金来源分散 → 独立参与者 → 更健康

但有时交易所热钱包也会造成假集中。需要排除 addr_type = 2 的地址。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `native_transfer.address` | token holders (top 20) | string |
| `addr_type` | token holders (top 20) | integer |

**功能**
```
回答：Top 持有者的资金来源是否集中在少数地址？
（Shannon 多样性 → 同源检测）
>0.7 = 高度同源 → 可能是单个实体多钱包 → 庄家控盘
<0.3 = 来源分散 → 独立参与者
下游消费：L2-C1（内部人操纵——同源+集中+无SM）
```

---

### L1-D7：sniper_retention

**推理链**
```
sniper 是 token 开盘瞬间买入的狙击手。
他们通常有最快的执行速度，目的是开盘买入→拉升出货。

如果 sniper 大部分已经清仓（sell_amount_percentage > 0.5），
说明早期参与者不看好后续。
如果 sniper 大部分还在持有，说明他们觉得还有空间。

但 sniper 也可能是 dev 自己的钱包——用来开盘拉盘。
所以 sniper retention 高不一定好（可能是 dev 在撑着）。
需要配合 D6（同源检测）来看 sniper 是否和 dev 同源。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `sell_amount_percentage` | token holders (per sniper) | float (0-1) |
| `tags` | token holders | array (filter: sniper) |
| `sniper_wallets` | wallet_tags_stat | integer |

**功能**
```
回答：开盘狙击手中有多少仍在持有？
>0.7 = 多数 sniper 还在 → 他们看好后续或就是 dev
<0.3 = 多数 sniper 已离场 → L2-B3（Sniper 集体离场）
配合 L1-D6 判断 sniper 是否和 dev 同源
```

---

## L1-E：Dev/Creator 风险特征（6 条）

---

### L1-E1：dev_risk_score

**推理链**
```
Dev 风险不是单一维度，而是多因子叠加：
1. creator_token_status = hold → dev 仍在持有 → 存在卖压（+0.3）
2. top_10_holder_rate > 0.3 → 持仓高度集中 → 容易被操纵（+0.2）
3. dev_team_hold_rate > 0.1 → 团队持仓高 → 集体卖压（+0.15）
4. creator_open_count = 0 → 首次发币 → 无历史可追溯（+0.15）
5. twitter 有改名历史 → 可能跑路过 → 可疑（+0.1）
6. 有删推记录 → 可能删过 rug 证据（+0.1）

每一项都是独立的危险信号，叠加后形成综合评分。
0-0.2 = 低风险（dev 已清仓且历史干净）
0.2-0.5 = 中等风险
>0.5 = 高风险

权重是初始值，需要后续回测校准。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `creator_token_status` | token security | string |
| `top_10_holder_rate` | token security | float |
| `dev_team_hold_rate` | token security | float |
| `creator_open_count` | token info (dev) | integer |
| `twitter_name_change_history` | token info (dev) | array |
| `twitter_del_post_token_count` | token info (dev) | integer |

**功能**
```
回答：开发者/创建者的综合风险评分（多因子加权）
>0.5 = 高风险 dev → 下游触发警告
配合 L1-E2（历史记录）和 L1-E3（营销投入）判断 dev 意图
下游消费：L2-B2（Dev dump）、L2-C1（内部人操纵）
```

---

### L1-E2：dev_track_record_score

**推理链**
```
一个发过 20 个 token、其中有一个冲到 $500k 市值的 dev，
和一个首次发币的 dev，可信度完全不同。

dev.ath_token_info.ath_mc 告诉你这个 dev 历史上最好的 token
曾经达到过多少市值。

score = min(ath_mc / 100000, 1.0)
$100k = 0.1，$1M = 1.0（满分），首次发币 = 0

但要警惕：历史好不代表这次不会 rug。
有些 dev 的策略是：先出几个好项目建立声誉，然后 rug 一个大的。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `dev.ath_token_info.ath_mc` | token info | USD string |
| `creator_open_count` | token info (dev) | integer |

**功能**
```
回答：开发者历史上最好的 token 达到过多少市值？
>0.5 = dev 有成功经验
=0 = 首次发币或历史无亮点 → 无 track record
配合 L1-E1：track record 好 ≠ 这次不会 rug
```

---

### L1-E3：dex_marketing_intensity

**推理链**
```
GMGN 给了 dev 在 DexScreener 上的 4 个营销行为标志：
dexscr_ad（是否投广告）、dexscr_update_link（更新链接）、
dexscr_trending_bar（是否上 trending bar）、dexscr_boost_fee（Boost 投入）

计数 = 0-4 分。

高营销投入可能是：
1. 认真做项目的 dev（好）
2. Pump and dump 的前期造势（坏）

区分方法：配合 L1-E1（dev 风险）和 L1-A4（SM 方向）
- 高营销 + dev 风险低 + SM 在买 → 可能是好项目
- 高营销 + dev 风险高 + SM 在卖 → 典型的 pump and dump
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `dev.dexscr_ad` | token info | integer |
| `dev.dexscr_update_link` | token info | integer |
| `dev.dexscr_trending_bar` | token info | integer |
| `dev.dexscr_boost_fee` | token info | integer |

**功能**
```
回答：Dev 在 DexScreener 上的营销投入程度（0-4 分）
3-4 = 高营销 → 需要判断是真的在推项目还是在造势出货
0 = 零营销 → 可能是 rug 或纯草根项目
```

---

### L1-E4：insider_activity_composite

**推理链**
```
GMGN 给了三个内部人/操纵交易比率：
1. rat_trader_amount_rate：内部人/老鼠仓交易量占比
2. bundler_trader_amount_rate：Bot 捆绑买入交易量占比
3. entrapment_ratio：诱捕交易占比

这三者都是「非正常交易」。
正常市场：三者加起来应该很低（<0.2）。
高操纵市场：三者加起来可能超过 0.5。

直接把三个加起来 = insider_activity_composite。

新币因为有 sniper bot 抢开盘，bundler_rate 天然偏高。
所以对于 token_age < 10min 的新币，这个值的解读要放宽。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `rat_trader_amount_rate` | token security | float (0-1) |
| `bundler_trader_amount_rate` | token security | float (0-1) |
| `entrapment_ratio` | trending | float (0-1) |

**功能**
```
回答：内部人/捆绑/诱捕交易的总占比
>0.5 = 操纵交易主导 → L2-C1（内部人操纵）
0.2-0.5 = 有一定嫌疑
<0.2 = 相对干净
新币 bundler 比例天然高，需要年龄修正
```

---

### L1-E5：fee_burden_total

**推理链**
```
buy_tax + sell_tax = 总税费。
这是每次买入+卖出的总摩擦成本。
10% 总税费意味着：买入 100，实际到账 90（买税），
卖出 90，实际到账 81（卖税）= 总摩擦 19%。

超过 10% 的税费意味着极其显著的负期望值。
但如果 token 价格在涨，高税费也可能被覆盖。
所以这个值不是独立的「危险信号」，而是「成本修正因子」。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `buy_tax` | token security | float |
| `sell_tax` | token security | float |

**功能**
```
回答：买卖总税费是多少？
>0.10 = 高税费 → 显著负期望值
用于计算实际交易成本，修正收益预期
```

---

### L1-E6：cto_quality_check

**推理链**
```
CTO（Community Takeover）= 原 dev 放弃项目，社区接管。
不是所有 CTO 都是好信号——很多 CTO 是另一个团队接盘继续 rug。

cto_quality_check 只在 cto_flag = 1 时计算，评估 CTO 质量：
1. creator_token_status = close → 原 dev 已走（+0.4，必要条件）
2. sm_penetration > 0.02 → SM 在参与新团队（+0.3）
3. volume_momentum > 1.5 → 量在复苏（+0.3）

三项都满足 = 1.0（满分 CTO）
原 dev 还在 + SM 不参与 = 低质量 CTO
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `cto_flag` | token info / trending | integer |
| `creator_token_status` | token security | string |
| `sm_penetration` | L1-D1 | float |
| `volume_momentum` | L1-B2 | float |

**功能**
```
回答：如果发生了 CTO，接管质量如何？
>0.6 = 高质量 CTO → L2-E1（CTO 复苏）
<0.3 = 低质量 CTO → 可能只是换皮
仅在 cto_flag=1 时计算
```

---

## L1-F：时间/生命周期特征（5 条）

---

### L1-F1：token_age_minutes

**推理链**
```
token 的年龄是解读所有其他指标的基础上下文。
一个 3 分钟大的 token 和有 3 天历史的 token，
同样的 volume、holder_count、price_change 含义完全不同。

age < 5 min：刚创建 → 几乎所有数据都不可靠
age 5-30 min：新生儿 → 狙击手活跃，波动极大
age 30-120 min：早期 → 初步数据可用
age > 120 min：相对成熟 → 数据开始有统计意义

这个值本身不是策略输入，而是所有其他 L1 feature 的「上下文修正因子」。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `creation_timestamp` | token info | unix seconds |

**功能**
```
回答：Token 被创建了多久（分钟）？
所有 L1/L2 判断的「年龄上下文」
<5 min → 几乎所有判断都不可靠
>120 min → 数据开始有统计意义
```

---

### L1-F2：bonding_curve_progress_rate

**推理链**
```
对于还在 bonding curve 上的 token（launchpad_status = 1），
progress 从 0 增长到 1 意味着 token 将被「毕业」到 DEX。

progress_rate = (progress_t2 - progress_t1) / (time_diff_in_minutes)

这告诉你填充速度。
高速填充 → 买盘强劲 → 即将毕业 → 关注窗口
低速 → 冷门 → 可能永远不会毕业

但这个值需要两次 API 采样。单次调用只能看当前 progress。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `launchpad_progress` | token info (两次采样) | float (0-1) |
| `is_on_curve` | token holders | boolean |

**功能**
```
回答：Bonding curve 填充速度（每分钟进度）
只在 is_on_curve = true 时可用
高速 → 即将毕业 → L2-D3（毕业窗口）
需要至少 2 次采样（间隔 > 2 min）
```

---

### L1-F3：time_since_open

**推理链**
```
open_timestamp 是 token 开始交易的时刻。
time_since_open = (now - open_timestamp) / 60 分钟。

开盘前 5 分钟：狙击手主导，价格波动极端
5-30 分钟：早期参与者在评估
>60 分钟：开盘影响消退

配合 L1-D7（sniper_retention）判断开盘后的 sniper 行为阶段。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `open_timestamp` | token info | unix seconds |

**功能**
```
回答：Token 开盘交易了多久（分钟）？
<5 min → 狙击手主导，极高波动
5-30 min → 早期评估窗口
>60 min → 开盘影响消退
配合 L1-D7 判断 sniper 阶段
```

---

### L1-F4：pool_age_hours

**推理链**
```
池子创建时间 → 池子已存在多久。
新池子（<1h）→ 流动性可能不稳定 → 数据参考价值低
老池子（>24h）→ 流动性相对稳定

配合 L1-C4（liquidity_decay_flag）判断流动性变化的背景。
老池子流动性大幅流失比新池子更值得警惕。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `pool.creation_timestamp` | token info | unix seconds |

**功能**
```
回答：池子创建了多久（小时）？
<1h → 池子不稳定，谨慎解读
>24h → 池子相对稳定
配合 L1-C4 判断流动性变化的严重性
```

---

### L1-F5：holder_growth_rate

**推理链**
```
holder_count 的静态值告诉你「现在有多少持有人」。
但更重要的信息是「持有人是在增长还是减少」。

growth_rate = (holders_t2 - holders_t1) / time_diff_in_minutes

正增长 → 新人在进场 → 热度在扩散
零增长 → 稳定
负增长 → 持有人在离场 → 市场萎缩

需要两次独立采样。
这个值的精度取决于采样间隔——间隔太短噪声大。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `holder_count` | token info (两次采样) | integer |

**功能**
```
回答：持有人数量在增长还是减少？
正增长 → 热度扩散 → 配合 SM 方向判断新人质量
负增长 → 离场信号 → L2-D2（死亡确认的辅助信号）
需要至少 5 分钟间隔的两次采样
```

---

## L1-G：社交/注意力特征（3 条）

---

### L1-G1：social_completeness

**推理链**
```
严肃项目和 rug 项目在社交资料上的差异往往很明显。
严肃项目会填：Twitter、Telegram、网站、详细描述。
rug 项目通常：只有 Twitter（或啥都没有）、无描述、无网站。

completeness = 填了 Twitter + TG + 网站 + 有描述（>10 字）/ 4

0.25 或更低 = 极度缺失 → 大概率是 rug
1.0 = 社交完整 → 至少包装到位

但这不判断「项目好坏」，只判断「包装程度」。
包装好的项目也可能是精心设计的 rug。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `link.twitter_username` | token info | string |
| `link.telegram` | token info | string |
| `link.website` | token info | string |
| `link.description` | token info | string |

**功能**
```
回答：社交资料的完整程度（0-1）
<0.25 = 极度缺失 → 高概率 rug
1.0 = 完整 → 至少包装到位
不判断项目质量，只判断包装
```

---

### L1-G2：follower_to_mcap_ratio

**推理链**
```
follower_to_mcap = x_user_follower / (market_cap / 1000)
即「每 $1k 市值对应多少粉丝」。

高比值 → 相对市值有很多关注者 → 可能被低估（或社交泡沫）
低比值 → 市值靠链上驱动，社交关注少 → 可能是纯交易标的

一个极端的例子：
- mcap = $10k, followers = 5000 → ratio = 500（每 $1k = 500 粉丝）
  社交远大于市值 → 可能是早期被低估或 rug
- mcap = $10M, followers = 100 → ratio = 0.01
  市值大但无人关注 → 可能是刷出来的市值
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `x_user_follower` | trenches | integer |
| `market_cap` | trending | USD float |

**功能**
```
回答：每 $1k 市值对应多少 X 粉丝？
高比值 = 社交热度领先市值 → 可能被低估或社交泡沫
低比值 = 纯链上驱动 → 无社交支撑
```

---

### L1-G3：description_quality_hint

**推理链**
```
link.description 是 token 创建者写的项目描述。
长度和内容反映创建者的认真程度。

>100 字 → 详细描述 → 至少花了时间写
<10 字或 null → 敷衍 → 可能随手发的 rug

但描述再好也不代表项目好。只是多一个判断维度。
```

**输入字节**
| 字节 | 来源 | 类型 |
|------|------|------|
| `link.description` | token info | string |

**功能**
```
回答：项目描述的长度（粗判认真程度）
>100 字 = 有内容
<10 字 = 敷衍 → 较大概率 rug
只判认真程度，不判项目质量
```

---

## L2 Structure Candidate — 推理链逐条展开

以下只展开每个 L2 的「为什么这些 L1 组合在一起能推断出这个结构状态」的推理链，不重复条件清单。

---

### L2-A1：SMART_MONEY_CONVICTION_ACCUMULATION

**推理链**
```
SM 积累的判断需要同时成立四个条件，缺一不可：

1. SM 方向偏买（L1-A4）：
   多数 SM 在 net buying。如果只是 1-2 个 SM 在买，可能是
   个体行为。需要 >60% 的 SM 方向一致。

2. SM 没有在出货（L1-D2）：
   极少 SM 已清仓（<20%）。如果 SM 一边买一边卖，
   说明 SM 内部有分歧，不是共识积累。

3. SM 有一定参与深度（L1-D1）：
   至少 >1% 的持有人是 SM。如果 SM 只占总持有人的 0.1%，
   他们的买入对市场影响极小。

4. 量不能萎缩（L1-B2）：
   volume_momentum > 1.0。如果在缩量中积累，
   可能是 SM 在小额试探而非真实建仓。但也不能太高
   （太高可能是 FOMO 而非积累）。

四个条件同时成立 → SM 正在「安静地、有共识地、有深度地」建仓。
但这不是买入信号。SM 可能建仓后等几小时甚至几天才拉升。
也可能永远不拉升（项目失败，SM 也认赔）。
```

---

### L2-B1：SMART_MONEY_DISTRIBUTION

**推理链**
```
SM 出货的判断核心是「SM 在系统性降低仓位」，但
价格可能还在涨，因为 SM 在把货倒给新来的人。

1. SM 偏卖（L1-A4）：多数 SM 在 net selling
2. SM 已清仓比例高（L1-D2）：>30% 的 SM 清仓 >80%
3. 还有量（L1-B2）：volume_momentum > 0.8 → 有足够的流动性让 SM 出货

辅助信号：
- SM 在盈利（L1-D3）：SM 在获利了结，不是恐慌性抛售
- KOL 在买（L1-A5）：KOL 可能在接 SM 的货
- 新人在涌入（L1-D5）：新鲜钱包是 SM 的对手盘

危险组合：SM 卖 + KOL 买 + 新人涌入 = SM 在给所有人倒货。
这就是「聪明钱先跑，把货留给后来者」的经典模式。
```

---

### L2-C3：LIQUIDITY_TRAP

**推理链**
```
流动性陷阱的判断核心是「账面市值无法兑现」。

1. mcap/liquidity > 50（L1-C1）：卖 $1k 就可能产生显著滑点
2. top_10 > 0.3（canonical）：筹码高度集中 → 大仓出货 = 崩
3. liquidity < $50k（canonical）：绝对深度不足

这三个条件意味着：
你看到的价格是少数几笔交易撑起来的。
任何稍大的卖出都会因为没有对手盘而砸穿。
这不是「波动大」的问题，而是「无法退出」的问题。

Solana Meme 市场里这种情况极其常见：
一个 token 市值几百万，但池子里只有几千块。
持有者账面都赚钱，但谁也卖不掉。
```

---

### L2-E2：HYPE_CYCLE_PEAK

**推理链**
```
炒作高潮的判断核心是「所有表象都很牛，但结构在恶化」。

1. 价格暴涨（price_change_percent1h > 50）：1h 涨 50%+
2. 量暴增（L1-B2 > 3.0）：交易量是平时的 3 倍以上
3. 新人涌入（L1-D5 > 0.6）：超过 60% 的持有人是新钱包

这些是「看起来很牛」的表象。但加上：
- SM 在卖（L1-A4 偏卖）
- SM 已清仓比例高（L1-D2 > 0.3）
- SM 大幅盈利（L1-D3）

这就是「SM 在利用 FOMO 出货」的经典炒作高潮。
SM 在拉盘时卖 → 零售接盘 → 零售 FOMO 继续拉 → SM 继续卖。
最后 SM 卖完 → 零售也买完 → 自由落体。
```

---

### L2-D1：EARLY_BREAKOUT_ZONE

**推理链**
```
早期突破的判断核心是「数据不足以做任何确定性判断，但值得关注」。

条件很简单：
- token 不到 1h 老（L1-F1）
- 至少有 1 个 SM 在关注（smart_degen_count >= 1）
- 量在放大（L1-B2 > 1.5）
- SM 还没卖（L1-D2 < 0.1）

这四个条件同时成立 → token 处于「可能爆发也可能归零」的十字路口。
此时任何判断都是猜测。
正确做法：标记为 WATCH，等待更多数据。
错误做法：看到 SM 在买就跟进去——SM 可能在 5 分钟后全部撤出。
```

---

### L2-E1：COMMUNITY_TAKEOVER_REVIVAL

**推理链**
```
CTO 复苏的判断核心是「原 dev 确实走了 + 新团队确实在做事」。

1. cto_flag = 1 → 社区接管已发生
2. creator_token_status = close → 原 dev 确实清仓了（必要条件）
3. cto_quality_check > 0.5 → SM 在参与 + 量在复苏

如果 cto_flag = 1 但 creator_token_status = hold，
说明原 dev 还没走 → 这不是真正的 CTO，可能是 dev 换马甲。
如果 CTO 质量低（SM 不参与 + 量萎缩），
说明社区接管只是换了个名字，实质没有变化。

只有「dev 真走了 + SM 认可 + 量在复苏」三个同时成立，
CTO 才是值得关注的事件。
```

---

### L2-A2：KOL_SM_RESONANCE_ACCUMULATION

**推理链**
```
A1 只看了 SM 的共识。但如果 KOL 也在同方向，信号更强。

但这里有一个关键的时间顺序问题：
- SM 先买 → KOL 后买：健康。SM 提前布局，KOL 带来关注度
- SM 和 KOL 同时买：可能是付费推广（KOL 被付费喊单）
- KOL 先买 → SM 后买：罕见。KOL 很少比 SM 更快

所以共振的意义不在于「同时」，而在于「SM 打底 + KOL 叠加」。
如果 kol_quality_flag 高（KOL 有实质持仓而非路过），共振的
可信度更高。如果 KOL 持仓极小（<0.001%），那 KOL 只是喊单，
没有实际行动支撑。

共振 ≠ 必涨。SM+KOL 共振买入后也可能一起亏损清仓。
但它比单独 SM 买入的信号更强。
```

---

### L2-A3：ORGANIC_STEALTH_ACCUMULATION

**推理链**
```
不是所有好的积累都是轰轰烈烈的。有些最好的项目在「无人关注」阶段。

低调积累的特征：
- SM 在买，但量不大（volume_momentum < 1.5）→ 没有引爆市场
- 新人不多（fresh_wallet_ratio < 0.5）→ 还没出圈
- 无操纵（insider_activity < 0.2）→ 没有在刷量抬轿
- Dev 风险低 → 不那么像 rug

这种情况下 SM 在「安静地建仓」，不引人注目。
这种结构往往出现在：
- 项目早期（token 还不到 2h 但有 SM 在关注）
- CTO 后复苏初期（SM 重新评估）

但「无人关注」和「根本没人要」只在一线之间。
区别在于：有没有 SM 在建仓？有 = A3，没有 = 可能是 D2（已死）。
```

---

## L2-B2：DEV_DUMP_IN_PROGRESS

**推理链**
```
Dev dump 的判断不需要看 SM 方向——dev 自己的行为就够了。

核心矛盾：
1. dev 还在持有（creator_token_status = hold）
2. dev/团队持仓比例可观（> 5%）
3. dev 在积极营销（dex_marketing_intensity >= 2）
4. 新人在涌入（fresh_wallet_ratio > 0.5）

这个组合的推理：dev 在制造热度，吸引新人接盘，因为 dev 还有货要出。

但如果 dev 持仓但没在营销、新人也没涌入，
那 dev 可能只是长期持有者——不构成 dump 信号。

另一个危险变体：
creator_token_status = hold + liquidity_decay_flag < 0.5
→ dev 可能在抽流动性准备跑路。

B2 和 B1（SM 出货）的区别：
- B1：SM 在出货（专业交易者离场）
- B2：Dev 在出货（创建者在离场）→ 更危险

两者同时发生 = 极度危险（SM 和 dev 都在跑）。
```

---

### L2-B3：SNIPER_MASS_EXIT

**推理链**
```
Sniper 是 token 开盘瞬间进入的专业交易者/机器人。
他们通常有严格的时间窗口：买入→快速拉升→几分钟内出货。

B3 判断 sniper 是否在「集体离场」：
- sniper_retention < 0.3 → 超过 70% 狙击手已清仓过半
- time_since_open < 60min → 还在开盘窗口内
- sniper_wallets > 5 → 足够样本

sniper 离场本身不一定是坏事——他们本来就是短线。
关键在于 sniper 离场后「谁在接盘」：
- 接盘的是 SM → 可能反转（L2-A1 或 E3）
- 接盘的是新人 → 可能是 FOMO（L2-E2）
- 没人接盘 + sniper 都走了 → 归零

B3 是开盘后的第一个结构判断。判断 B3 后必须紧接着
看 SM 方向（L1-A4）来决定下一步走向。
```

---

## L2-C1：INSIDER_MANIPULATION_DOMINATED

**推理链**
```
内部人操纵的判断核心不是「有没有操纵」，而是「操纵是否主导了全部交易」。

三个条件：
1. insider_activity_composite > 0.5（L1-E4）
   → 超过 50% 的交易量来自老鼠仓/捆绑/诱捕
2. sm_penetration < 0.005（L1-D1）
   → SM 几乎不参与
3. smart_degen_count <= 1
   → 至多 1 个 SM

当这三个条件同时成立，市场上几乎只有操纵者和受害者。
SM 不参与 = 专业交易者看到了什么让他们远离的东西。

辅助确认：
- wallet_source_convergence > 0.7（L1-D6）→ 钱包同源
- top_10_holder_rate > 0.5 → 高度集中

C1 是最强的 BLOCK 信号——不是「风险高」，而是「根本没有真实市场」。
```

---

### L2-C2：BOT_WASH_FESTIVAL

**推理链**
```
C1 是「人在操纵」，C2 是「Bot 在刷量」。
两者的区别在于交易模式：

C2 的特征：
1. is_wash_trading = true → GMGN 明确标记为刷量
2. bot_degen 数量多（>5）或比例高（>0.3）
3. volume_intensity 极高（>3.0）→ 同笔钱反复交易
4. swap_per_holder 极高（>3.0）→ 每人大量交易
5. buy_sell_count_ratio 接近 0.5 → 对倒（买卖笔数几乎相等）
6. volume_per_swap 极小（<$20）→ 小额刷量

这是 Bot 制造虚假热度、刷 GMGN trending 排名的经典模式。
目的是让 token 出现在更多人面前，吸引真实买家接盘。

和 C1 一样，C2 也是强 BLOCK 信号。
```

---

## L2-D2：DEAD_OR_DYING

**推理链**
```
D2 的判断核心是「已经不值得花时间研究了」。

条件都是「极低」的排列：
1. volume_intensity < 0.05（L1-B1）→ 几乎没有成交
2. volume_decay_ratio < 0.3（L1-B5）→ 量在持续萎缩
3. holder_growth_rate <= 0（L1-F5）→ 持有人不再增长
4. top_holder_velocity < 0.2（L1-C3）→ 大仓也不动了
5. swaps_1h < 5 → 一小时不到 5 笔

这些条件同时成立意味着：这个 token 的故事已经讲完了。
没有新资金、没有新关注、没有新交易。

唯一的例外：CTO 复活（L2-E1）。
一个 D2 的 token 如果被社区接管，可能死而复生。
但在此之前，研究 D2 token 的时间成本远超潜在收益。
```

---

### L2-D3：BONDING_CURVE_GRADUATION_WINDOW

**推理链**
```
对于还在 bonding curve 上的 token，毕业是生命周期的关键节点。

D3 的条件：
1. is_on_curve = true（还在 bonding curve 上）
2. launchpad_progress > 0.7（进度超 70%）
3. bonding_curve_progress_rate > 0.01/min（有意义的填充速度）

毕业意味着什么：
- token 从 bonding curve 合约迁移到 DEX 池
- 流动性从 bonding curve 转移到 DEX（可能增加或减少）
- Sniper bot 通常在毕业瞬间入场（抢开盘）
- 毕业后的前 5-30 分钟是波动最大的时期

为什么这是「窗口」而不是「信号」：
- 毕业不一定涨——大量 token 毕业后归零
- 毕业时 sniper 入场后的抛压可能导致暴跌
- 但如果 SM 在毕业前后开始建仓，那可能是机会

D3 是「准备观察」信号，不是「准备交易」信号。
毕业后需要立即进入完整的 Phase 1 分析流程。
```

---

### L2-E3：OVERSOLD_BOUNCE_CANDIDATE

**推理链**
```
超跌反弹的判断核心是「价格已经跌得很深了，而且有人在承接」。

条件：
1. price_to_ath_ratio < 0.3（L1-C2）→ 从高点跌了 70%+
2. buy_dominance > 0.5（L1-A1）→ 买盘开始出现
3. volume_momentum > 1.0（L1-B2）→ 有承接量

这三个条件说明「底部有人在买」。
但这里有一个关键区分：

是「真反弹」还是「死猫跳」？
- 承接的是 SM（L1-A4 偏买）→ 可能是真反弹
- 承接的是新人（L1-D5 高）+ SM 不动 → 可能是死猫跳
- SM 在亏损中还在买（L1-D3）→ 可能是 SM 在摊平成本（不好判断）

超跌反弹 + 流动性极差（L1-C1 高）= 反弹无法兑现 = 假反弹。
超跌反弹 + SM 在买 + 流动性健康 = 可能是机会。

但永远不是「底部确认」。Memecoin 可以从 -90% 再跌 -90%。
```

---

# PART 7：字节组合推理方法论

> 以上 37 条 L1 + 16 条 L2 的推理链不是随机产生的。
> 它们来自一套可复用的推理框架。以下是这个框架本身。

---

## 7.1 推理引擎：五个问题驱动字节组合

任何 GMGN 字节组合的推理都从五个问题开始：

```
问题 1 → 我想知道什么市场事实？
问题 2 → 这个事实在链上会留下什么痕迹？
问题 3 → GMGN 的哪个字段能看到这个痕迹？
问题 4 → 单一字段够不够？不够的话需要和哪个字段配对？
问题 5 → 配对后的值在什么范围内代表什么含义？
```

**示例：推导 L1-A1 buy_dominance**

```
问题 1：我想知道「买方还是卖方在主导当前市场」
问题 2：买方买入会产生 buy_volume，卖方卖出会产生 sell_volume
问题 3：GMGN 给了 buy_volume_1h 和 sell_volume_1h
问题 4：单独 buy_volume 不够——$100k 买入+$0 卖出 vs $50k+$50k 完全不同
        → 需要 buy_volume / (buy_volume + sell_volume) 得到比例
问题 5：>0.6 = 买方主导，<0.4 = 卖方主导，≈0.5 = 均衡
```

**示例：推导 L2-A1 SMART_MONEY_CONVICTION_ACCUMULATION**

```
问题 1：我想知道「SM 是否在有共识地积累仓位」
问题 2：SM 积累 = SM 在净买入 + SM 还没清仓 + SM 有一定参与深度 + 有量支撑
问题 3&4：四个痕迹分别需要不同的 L1：
  SM 方向 → L1-A4（sm_direction_signal）
  SM 未清仓 → L1-D2（sm_exit_ratio）
  SM 深度 → L1-D1（sm_penetration）
  有量 → L1-B2（volume_momentum）
问题 5：四个条件同时成立 → SM 积累。任一缺失 → 不成立。
```

---

## 7.2 三层推理结构

```
Layer 0: Canonical Bytes（GMGN 已算好）
   ↓  问题：这个 raw 值能直接回答问题吗？
   ↓  能 → 直接使用（如 rug_ratio、is_honeypot）
   ↓  不能 → 进入 L1

Layer 1: Feature（1次计算 = 2+ bytes 配对）
   ↓  推理方法：
   ↓    1. 确定被除数（要归一化的量）
   ↓    2. 确定除数（归一化基准）
   ↓    3. 确定方向（越高=什么，越低=什么）
   ↓    4. 外推：极端值意味着什么市场状态？
   ↓  产出 → L1 Feature

Layer 2: Structure Candidate（2次计算 = 3-5 features 条件组合）
   ↓  推理方法：
   ↓    1. 定义市场状态（想检测什么模式）
   ↓    2. 列必要条件（缺一不可）
   ↓    3. 列增强条件（有更好，没有也能判断）
   ↓    4. 列否定条件（任一出现就降级或推翻）
   ↓    5. 定义解释边界（allowed vs forbidden）
   ↓  产出 → L2 Structure Candidate
```

---

## 7.3 归一化基准的选择规则

大部分 L1 Feature 是 A / B 形式。B（分母）的选择决定了指标的含义：

| 分母 | 含义 | 用于 |
|------|------|------|
| `liquidity` | 相对池子深度 | net_flow_intensity, volume_intensity, mcap/liquidity |
| `volume_24h/24` | 相对近期平均水平 | volume_momentum |
| `holder_count` | 人均 | swap_per_holder, sm_penetration |
| `buy+sell` | 在买卖总和中占比 | buy_dominance, buy_sell_count_ratio |
| `swaps_1h` | 每笔 | volume_per_swap |
| `ath_price` | 相对历史 | price_to_ath_ratio |
| `initial_liquidity` | 相对初始 | liquidity_decay_flag |
| `market_cap` | 相对市值 | follower_to_mcap_ratio |

规则：**选分母 = 选你要把分子「放回什么上下文中解读」**。

---

## 7.4 结构候选的「条件层级」设计规则

每个 L2 Structure Candidate 的三层条件：

```
required_conditions（AND）  → 缺一条就不成立
supporting_signals（bonus）  → 有更好，强化判断
warning_signals（negate）    → 任一条出现 = 降级或推翻
```

设计规则：
1. **required** 挑「定义性」特征——没有它就不是这个结构
2. **supporting** 挑「增强信心」特征——可有可无
3. **warning** 挑「推翻逻辑」特征——例如 L2-A1（积累）中如果出现 is_wash_trading=true，直接推翻

---

## 7.5 跨类别组合的设计规则

不是任意 L1 都能组合。有效组合跨越以下「配对轴」：

```
价格方向 + 量确认  → A + B（方向 + 动量）
方向 + 参与者身份 → A + D（方向 + 谁在做）
方向 + 风险背景   → A + E（方向 + dev 是否在跑）
结构 + 生命阶段    → any + F（任何结构的年龄修正）
结构 + 社交背景    → any + G（炒作 vs 安静）
```

无效组合示例：
- 社交完整度 + 买卖笔数比 → 无因果关联 → 不产生有意义的 L2

---

## 7.6 从「看到了」到「推断出」的认知跨越

这是最关键的一步。L1 给你的是「SM 在买」「量在放大」等**事实**。
L2 给你的是「SM 在有共识地积累」这个**推断**。

跨越的方法：**反证法**。

对每个 L2 候选，问：「如果这个结构不存在，我能从数据里看到什么？」
然后取反。

```
例如 L2-A1：
如果 SM 没有在积累 → 我能看到：
- SM 方向分化（有的买有的卖）→ L1-A4 不会 >0.6
- SM 在一边买一边出货 → L1-D2 不会 <0.2
- SM 几乎不参与 → L1-D1 不会 >0.01
- 几乎没有交易量 → L1-B2 不会 >1.0

所以「SM 积累」的 L2 条件 = 这四个反面的否定。
```

任何一组 GMGN 字节，都可以用这个方法推导其 L2 含义。

---

> 状态：RESEARCH_IN_PROGRESS（第五轮完成：剩余 L2 + 推理方法论）
> 文件：`/root/sikk-gmgn/design/phase1-research/gmgn-byte-combination-reasoning-v0.1.md`
> 37 L1 ✓ | 16 L2 ✓ | 方法论 ✓
> 下一步候选：用这个方法论对新的 GMGN 字段子集做快速推理演示
