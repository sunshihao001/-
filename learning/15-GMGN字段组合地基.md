# 15｜GMGN 字段组合地基：从入口数据推理二段筛选思想

## 这一篇要解决的问题

GMGN 不是只提供单个字段。更有价值的地方在于：它把市场、钱包、风险、社交、流动性、热度放在同一个入口里。我们要做的不是相信某个标签，而是把这些字段组合成可解释的候选筛选思想。

核心目标：把 GMGN 字段从「看板信息」变成「候选入口的地基」。

---

## 一、源头：字段组合不是字段堆叠

单字段只能回答一个局部问题。

例如：

- `liquidity`：现在池子有多少承接能力。
- `market_cap`：市场给了多大估值。
- `volume`：一段时间内有多少交易活动。
- `holder_count`：有多少地址持有。
- `top_10_holder_rate`：头部集中度有多高。
- `smart_degen_count`：GMGN 认为有多少聪明钱包参与。
- `is_show_alert`：GMGN 前端是否提示风险。
- `renounced_mint` / `renounced_freeze_account`：权限是否放弃。
- `rug_ratio`：GMGN 推导出的风险比例。
- `bundler_rate`：疑似打包/集中买入痕迹。

单独看，每个字段都容易误导。

组合起来，就能形成问题：

> 这个代币是否已经具备足够市场承载力，值得进入第二段深度筛选？

这就是候选入口的意义。

---

## 二、第一层组合：二段筛选资格

二段筛选不是所有币都值得跑。

进入二段筛选至少需要满足：

1. 有一定流动性。
2. 市值不能太低。
3. 有真实交易活动。
4. 有足够持有人或交易者。
5. 风险提示不能过密。

这可以形成一个入口判断：

```text
二段候选资格 = 流动性承接 × 市值规模 × 交易活跃 × 持有人基础 × 风险密度
```

建议字段：

```text
liquidity
market_cap
volume
swaps / buys / sells
holder_count
top_10_holder_rate
is_show_alert
rug_ratio
bundler_rate
renounced_mint
renounced_freeze_account
```

### 入口思想

```text
流动性太低 → 一点买卖就严重滑点，完整工作流价值低。
市值太低 → 还处于噪声区，容易被单钱包行为主导。
交易太少 → 无法判断市场结构。
持有人太少 → 分布没有形成，钱包结构分析不稳定。
风险太密 → 先降级或跳过，避免浪费深度分析资源。
```

当前工程里已经加了第一版：

```text
min_liquidity = 50000
min_market_cap = 50000
```

后续可以继续扩展为完整二段资格门。

---

## 三、第二层组合：流动性与市值的关系

单看流动性和市值都不够。

关键是二者比例。

```text
流动性市值比 = liquidity / market_cap
```

这个比例很重要。

### 情况 A：市值高，流动性低

```text
market_cap 高
liquidity 低
```

含义：

- 看起来估值高。
- 实际承接弱。
- 少量卖出就可能砸穿。
- 适合标记为「估值虚胖」。

### 情况 B：市值低，流动性高

```text
market_cap 低
liquidity 高
```

含义：

- 可能是早期但池子不差。
- 也可能是刚加池子、交易未扩散。
- 值得观察成交和钱包结构。

### 情况 C：市值和流动性同步抬升

```text
market_cap 上升
liquidity 足够
volume 增加
holder_count 增加
```

含义：

- 具备进入二段筛选的基础。
- 需要继续看钱包质量和风险密度。

### 可生成字段

```json
{
  "liquidity_marketcap_ratio": 0.42,
  "liquidity_quality_hint": "healthy | thin | overstuffed | unknown",
  "valuation_liquidity_relation": "matched | inflated | early_pool | unknown"
}
```

---

## 四、第三层组合：热度与承接力

热度字段容易被制造。

但热度和承接力组合后，可以看出更有意思的东西。

建议组合：

```text
volume / liquidity
volume / market_cap
swaps / holder_count
buy_sell_ratio
price_change_percent1h / liquidity
```

### 思想 1：热度能不能被池子承接

```text
volume 很高
liquidity 很低
```

这类币可能很热，但冲击成本高。容易出现剧烈插针。

### 思想 2：交易活跃是不是来自少数地址

```text
swaps 很高
holder_count 很低
```

可能是机器人刷量，或者少数地址反复交易。

### 思想 3：上涨是否过度压缩后续空间

```text
price_change_percent1h 很高
market_cap 已高
liquidity 不同步增加
```

说明追高风险增加。

可生成字段：

```json
{
  "heat_absorption_hint": "absorbed | overheated | thin_pump | unknown",
  "activity_distribution_hint": "broad | concentrated | bot_like | unknown",
  "chase_risk_hint": "low | medium | high | unknown"
}
```

---

## 五、第四层组合：风险密度

GMGN 前端提示风险过多，本质上是风险密度问题。

单个风险提示不一定致命。

多个风险同时出现时，入口层就应该先过滤。

建议组合：

```text
is_show_alert
rug_ratio
bundler_rate
renounced_mint
renounced_freeze_account
top_10_holder_rate
creator_token_status
creator_close
is_wash_trading
```

### 风险密度思想

```text
权限风险 + 集中度风险 + 刷量风险 + 打包风险
```

如果同时出现，就不需要进入完整二段。

可生成字段：

```json
{
  "gmgn_risk_density_score": 0.72,
  "gmgn_risk_density_level": "low | medium | high | extreme",
  "gmgn_risk_hint_reasons": [
    "freeze_not_renounced",
    "high_bundler_rate",
    "top10_holder_concentration"
  ],
  "entry_aux_decision": "PASS | CAUTION | SKIP | UNKNOWN"
}
```

注意：这仍然是 GMGN hint，不是最终链上结论。

---

## 六、第五层组合：钱包质量与市场阶段

GMGN 有一些钱包相关字段：

```text
smart_degen_count
renowned_count
bluechip_owner_percentage
rat_trader_amount_rate
sniper_count
bundler_rate
holder_count
top_10_holder_rate
```

这些字段不能直接当真，但可以做入口假设。

### 好的组合

```text
holder_count 增加
smart_degen_count 有一些
bundler_rate 不高
top_10_holder_rate 不极端
bluechip_owner_percentage 有一定比例
```

这说明：

```text
有扩散
有部分高质量钱包参与
没有明显集中控制
```

### 坏的组合

```text
holder_count 不低
但 top_10_holder_rate 高
bundler_rate 高
sniper_count 高
rat_trader_amount_rate 高
```

这说明：

```text
表面分散
实际可能由早期集中钱包或机器人主导
```

可生成字段：

```json
{
  "wallet_quality_hint": "healthy | mixed | suspicious | unknown",
  "distribution_quality_hint": "organic_like | controlled_like | bot_like | unknown"
}
```

---

## 七、第六层组合：社交与市场是否匹配

GMGN 字段里也有社交相关信息：

```text
twitter_username
website
telegram
twitter_change_flag
twitter_rename_count
twitter_del_post_token_count
twitter_create_token_count
image_dup
```

这些字段可以形成「叙事可信度」入口判断。

### 可信组合

```text
有网站
有 Telegram
有 Twitter
没有频繁改名
没有大量删帖
图片重复低
```

### 可疑组合

```text
热度很高
社交缺失
Twitter 改名多
图片重复高
短时间创建多个 token
```

含义：

```text
可能是快速包装出来的叙事壳。
```

可生成字段：

```json
{
  "social_integrity_hint": "complete | thin | recycled | suspicious | unknown",
  "narrative_shell_risk": "low | medium | high | unknown"
}
```

---

## 八、一个更有意思的总模型：五种基础力

GMGN 字段组合可以抽象成五种基础力。

### 1. 承接力

代表市场能不能接住买卖。

字段：

```text
liquidity
market_cap
volume
volume/liquidity
```

### 2. 扩散力

代表参与是否从少数地址扩展到更多地址。

字段：

```text
holder_count
swaps
buys
sells
holder_count growth if available
```

### 3. 控制力

代表是否被少数钱包、开发者、机器人控制。

字段：

```text
top_10_holder_rate
bundler_rate
sniper_count
creator_token_status
```

### 4. 伪装力

代表热度、社交、成交是否可能被制造。

字段：

```text
is_wash_trading
image_dup
twitter_change_flag
twitter_rename_count
rat_trader_amount_rate
```

### 5. 退出力

代表早期参与者是否有能力或动机退出砸盘。

字段：

```text
creator_close
creator_token_status
dev_token_burn_ratio
top_10_holder_rate
liquidity/market_cap
```

组合后形成：

```text
候选价值 = 承接力 × 扩散力 - 控制力 - 伪装力 - 退出力
```

这不是数学公式，而是思考框架。

工程上可以拆成多个 hint score。

---

## 九、候选入口可以变成三段式

### 第 1 段：基础资格

```text
流动性够不够
市值够不够
交易量够不够
持有人够不够
```

输出：

```text
PASS / FILTERED_OUT
```

### 第 2 段：GMGN 风险密度

```text
权限风险
集中风险
刷量风险
打包风险
开发者风险
```

输出：

```text
PASS / CAUTION / SKIP / UNKNOWN
```

### 第 3 段：完整工作流

```text
S02 token panel
S03 wallet roles
S04 wallet structure
S05 evidence chain
S06 trade gate
```

输出：

```text
BLOCK / WATCH / NEED_MORE_DATA / PAPER_ONLY
```

---

## 十、下一步最值得构建的字段组合

建议优先做 5 个。

### 1. 二段候选资格分

```text
liquidity + market_cap + volume + holder_count
```

用于决定是否值得进入完整工作流。

### 2. 流动性质量 hint

```text
liquidity / market_cap
volume / liquidity
```

用于识别虚胖、市值薄、过热。

### 3. 风险密度 hint

```text
is_show_alert + rug_ratio + bundler_rate + top_10_holder_rate + permission fields
```

用于过滤 GMGN 明显提示风险过多的代币。

### 4. 叙事壳风险 hint

```text
social fields + twitter rename/delete/create + image_dup
```

用于识别包装壳和复用壳。

### 5. 钱包扩散质量 hint

```text
holder_count + top_10_holder_rate + smart_degen_count + sniper_count + bundler_rate
```

用于区分真实扩散和控制扩散。

---

## 小结

1. GMGN 字段的价值不在单字段，而在组合关系。
2. 二段筛选需要先有流动性、市值、成交、持有人基础，否则完整工作流容易浪费资源。
3. 流动性和市值要成对看，`liquidity / market_cap` 是关键入口指标。
4. GMGN 风险标签适合做风险密度 hint，不能替代最终链上行为判断。
5. 可以把 GMGN 字段抽象成五种基础力：承接力、扩散力、控制力、伪装力、退出力。

## 下一步

下一步可以把这些思想落成一份入口规则设计：

```text
GMGN 字段组合规则 v1
```

包括：

- 字段来源
- 组合公式
- 阈值
- 输出字段
- PASS / CAUTION / SKIP / FILTERED_OUT 的边界
- 与 S02-S06 的关系

这样 S01 就不只是候选入口，而是完整工作流的「地基筛」。
