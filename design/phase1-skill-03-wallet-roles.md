# Skill 3: meme-wallet-roles

## 定位

钱包角色识别。对标 Nansen。负责回答：这个 token 里有哪些关键钱包，它们是什么角色。

## 输入

```json
{
  "token_address": "<address>",
  "chain": "sol",
  "token_panel": "<token_panel.json 路径>"
}
```

## GMGN 命令映射

| 用途 | 命令 |
|------|------|
| Top 持有人（按持仓比例） | `gmgn-cli token holders --chain sol --address <addr> --limit 50 --order-by amount_percentage --direction desc --raw` |
| Smart Money 持有人 | `gmgn-cli token holders --chain sol --address <addr> --limit 50 --tag smart_degen --order-by amount_percentage --raw` |
| KOL 持有人 | `gmgn-cli token holders --chain sol --address <addr> --limit 20 --tag renowned --order-by profit --direction desc --raw` |
| Sniper 钱包 | `gmgn-cli token holders --chain sol --address <addr> --limit 20 --tag sniper --order-by amount_percentage --raw` |
| Bundler 钱包 | `gmgn-cli token holders --chain sol --address <addr> --limit 20 --tag bundler --order-by amount_percentage --raw` |
| Rat Trader 钱包 | `gmgn-cli token holders --chain sol --address <addr> --limit 20 --tag rat_trader --order-by amount_percentage --raw` |
| Fresh Wallet | `gmgn-cli token holders --chain sol --address <addr> --limit 20 --tag fresh_wallet --order-by amount_percentage --raw` |
| Dev 钱包 | `gmgn-cli token holders --chain sol --address <addr> --limit 10 --tag dev --raw` |
| Top 交易者（按利润） | `gmgn-cli token traders --chain sol --address <addr> --limit 50 --tag smart_degen --order-by profit --direction desc --raw` |
| SM 正在卖出的 | `gmgn-cli token traders --chain sol --address <addr> --tag smart_degen --order-by sell_volume_cur --direction desc --limit 20 --raw` |
| Dev 历史发币 | `gmgn-cli portfolio created-tokens --chain sol --wallet <creator_address> --order-by token_ath_mc --direction desc --raw` |
| Dev 交易统计 | `gmgn-cli portfolio stats --chain sol --wallet <creator_address> --period 30d --raw` |

## 输出

```json
{
  "schema_version": "1.0",
  "skill_name": "meme-wallet-roles",
  "task_id": "<token_address>_<timestamp>",
  "token_address": "<address>",
  "chain": "sol",
  "timestamp": "<ISO 8601>",
  "status": "PASS | WARN | BLOCK | NEED_MORE_DATA",

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

  "key_wallets": [
    {
      "address": "<wallet>",
      "role": "smart_money | kol | sniper | bundler | rat_trader | dev | whale | early_buyer | fresh_wallet",
      "tags": [],
      "maker_token_tags": [],
      "amount_percentage": 0.0,
      "usd_value": 0.0,
      "avg_cost": 0.0,
      "realized_profit": 0.0,
      "unrealized_profit": 0.0,
      "buy_volume_cur": 0.0,
      "sell_volume_cur": 0.0,
      "sell_amount_percentage": 0.0,
      "buy_tx_count": 0,
      "sell_tx_count": 0,
      "start_holding_at": 0,
      "is_selling": false,
      "native_transfer_from": "<funding source address>",
      "twitter_username": "",
      "name": ""
    }
  ],

  "dev_profile": {
    "creator_address": "",
    "creator_token_status": "",
    "total_tokens_created": 0,
    "graduated_count": 0,
    "graduation_ratio": 0.0,
    "best_token_ath_mc": 0.0,
    "best_token_symbol": "",
    "dev_30d_winrate": 0.0,
    "dev_30d_pnl": 0.0,
    "fund_from_address": ""
  },

  "smart_money_behavior": {
    "sm_buying": false,
    "sm_selling": false,
    "sm_net_direction": "accumulating | distributing | neutral | no_sm",
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
  "valid_until": "<60min>",
  "next_action": "meme-wallet-structure",
  "handoff_to": "meme-wallet-structure"
}
```

## 判断规则

### 角色分类规则

| 条件 | 角色标记 |
|------|---------|
| tags 包含 "smart_degen" | smart_money |
| tags 包含 "kol" 或 "renowned" | kol |
| tags 包含 "sniper" | sniper |
| tags 包含 "bundler" | bundler |
| tags 包含 "rat_trader" | rat_trader |
| tags 包含 "dev" | dev |
| amount_percentage > 0.02 且无其他标签 | whale |
| start_holding_at 在 token 创建后 5 分钟内 且 无 sniper 标签 | early_buyer |
| is_new = true 或 tags 包含 "fresh_wallet" | fresh_wallet |

### SM 行为判断

| 条件 | sm_net_direction |
|------|-----------------|
| smart_money_count = 0 | no_sm |
| SM 平均 sell_amount_percentage < 0.2 | accumulating |
| SM 平均 sell_amount_percentage > 0.7 | distributing |
| 其他 | neutral |

### Dev 信誉判断

| 条件 | 判断 |
|------|------|
| graduation_ratio > 0.3 且 best_token_ath_mc > 100000 | dev 有成功记录 |
| graduation_ratio < 0.1 | dev 大量失败，降级 |
| total_tokens_created > 50 且 graduation_ratio < 0.05 | dev 疑似批量发垃圾币，高风险 |

## 降级规则

| 条件 | 降级动作 |
|------|---------|
| holders API 返回 < 10 条 | downgrade: "Too few holders to analyze" |
| smart_degen tag 返回 0 条 | downgrade: "No smart money data" |
| dev 历史查询失败 | downgrade: "Dev history unavailable"; dev_profile 部分设 null |
| portfolio stats 查询失败 | downgrade: "Dev stats unavailable" |
| fresh_wallet_count / total_holders_sampled > 0.5 | downgrade: "High fresh wallet ratio" |

## 阻塞规则

| 条件 | 阻塞动作 |
|------|---------|
| holders API 全部返回错误 | ERROR + blocker_report |
| rat_trader_count > bundler_count + smart_money_count | WARN: "Rat traders dominate" |
| bundler_count > smart_money_count + kol_count 且 bundler_total_pct > 0.3 | WARN: "Bundler dominated token" |
