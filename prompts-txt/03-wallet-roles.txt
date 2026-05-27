# PROMPT 3: Wallet Roles — 钱包角色识别

## 直接发给 GPT 的 Prompt

```
## 任务

执行 meme-wallet-roles：识别一个 Solana token 中所有关键钱包的角色、持仓、行为。

## 输入

Token 地址：{CA}
前置 token_panel.json status：{PASS/WARN}

## 你要做的事

### Step 1: 生成数据采集命令

依次输出以下命令（我会把结果粘回来）：

```bash
# Top 持有人
gmgn-cli token holders --chain sol --address {CA} --limit 50 --order-by amount_percentage --direction desc --raw

# Smart Money
gmgn-cli token holders --chain sol --address {CA} --limit 50 --tag smart_degen --order-by amount_percentage --raw

# KOL
gmgn-cli token holders --chain sol --address {CA} --limit 20 --tag renowned --order-by profit --direction desc --raw

# Sniper
gmgn-cli token holders --chain sol --address {CA} --limit 20 --tag sniper --order-by amount_percentage --raw

# Bundler
gmgn-cli token holders --chain sol --address {CA} --limit 20 --tag bundler --order-by amount_percentage --raw

# Rat Trader
gmgn-cli token holders --chain sol --address {CA} --limit 20 --tag rat_trader --order-by amount_percentage --raw

# Fresh Wallet
gmgn-cli token holders --chain sol --address {CA} --limit 20 --tag fresh_wallet --order-by amount_percentage --raw

# Top 交易者（利润排序）
gmgn-cli token traders --chain sol --address {CA} --limit 50 --tag smart_degen --order-by profit --direction desc --raw

# Dev 历史发币
gmgn-cli portfolio created-tokens --chain sol --wallet {creator_address} --order-by token_ath_mc --direction desc --raw

# Dev 交易统计
gmgn-cli portfolio stats --chain sol --wallet {creator_address} --period 30d --raw
```

### Step 2: 角色分类规则

对每个钱包，按以下优先级分配角色：

| 条件 | 角色 |
|------|------|
| tags 含 "smart_degen" | smart_money |
| tags 含 "kol" 或 "renowned" | kol |
| tags 含 "sniper" | sniper |
| tags 含 "bundler" | bundler |
| tags 含 "rat_trader" | rat_trader |
| tags 含 "dev" | dev |
| amount_percentage > 2% 且无其他标签 | whale |
| 在 token 创建后 5 分钟内买入 且非 sniper | early_buyer |
| is_new = true 或 tags 含 "fresh_wallet" | fresh_wallet |

### Step 3: 填充 key_wallets

对每个关键钱包提取：
- address, role, tags, maker_token_tags
- amount_percentage, usd_value, avg_cost
- realized_profit, unrealized_profit
- buy_volume_cur, sell_volume_cur, sell_amount_percentage
- buy_tx_count, sell_tx_count
- start_holding_at
- is_selling（sell_amount_percentage > 0.5 视为正在卖出）
- native_transfer_from（资金来源地址）
- twitter_username, name

### Step 4: SM 行为判断

| 条件 | sm_net_direction |
|------|-----------------|
| smart_money_count = 0 | no_sm |
| SM 平均 sell_amount_percentage < 0.2 | accumulating |
| SM 平均 sell_amount_percentage > 0.7 | distributing |
| 其他 | neutral |

### Step 5: Dev Profile

从 created-tokens 和 portfolio stats 提取：
- total_tokens_created, graduated_count, graduation_ratio
- best_token_ath_mc, best_token_symbol
- dev_30d_winrate, dev_30d_pnl

Dev 信誉判断：
- graduation_ratio > 0.3 且 best_ath_mc > $100k → "有成功记录"
- graduation_ratio < 0.1 → "大量失败"
- total > 50 且 ratio < 0.05 → "疑似批量垃圾币发行者"

### Step 6: 输出 JSON

```json
{
  "schema_version": "1.0",
  "skill_name": "meme-wallet-roles",
  "task_id": "{CA}_{时间戳}",
  "token_address": "{CA}",
  "chain": "sol",
  "timestamp": "{ISO 8601}",
  "status": "PASS/WARN/NEED_MORE_DATA",
  "wallet_summary": {
    "total_holders_sampled": 50,
    "smart_money_count": 0,
    "smart_money_total_pct": 0.0,
    "kol_count": 0,
    "kol_total_pct": 0.0,
    "sniper_count": 0,
    "bundler_count": 0,
    "rat_trader_count": 0,
    "fresh_wallet_count": 0,
    "dev_wallet_count": 0
  },
  "key_wallets": [ ... ],
  "dev_profile": { ... },
  "smart_money_behavior": {
    "sm_buying": true/false,
    "sm_selling": true/false,
    "sm_net_direction": "accumulating/distributing/neutral/no_sm",
    "sm_avg_unrealized_pnl": 0.0,
    "sm_with_profit_count": 0,
    "sm_with_loss_count": 0
  },
  "early_buyer_analysis": {
    "earliest_buyer_address": "",
    "earliest_buyer_tags": [],
    "earliest_buyer_still_holding": false,
    "earliest_buyer_profit": 0.0,
    "top5_early_buyers_funding_sources": []
  },
  "evidence": [],
  "counter_evidence": [],
  "confidence_score": 0.0,
  "downgrade_reasons": [],
  "blocker_reasons": [],
  "missing_fields": [],
  "valid_until": "{60分钟后}",
  "next_action": "meme-wallet-structure",
  "handoff_to": "meme-wallet-structure"
}
```

### 降级条件

- holders 返回 < 10 条 → downgrade: "Too few holders"
- smart_degen 返回 0 → downgrade: "No smart money data"
- dev 历史查询失败 → downgrade + dev_profile 设 null
- fresh_wallet 占比 > 50% → downgrade: "High fresh wallet ratio"

## 禁止

- 不编造没有返回的钱包数据
- 不说"确定庄家"、"确定内幕"
- 不给交易建议
- 缺失字段放 missing_fields，不填默认值
```
