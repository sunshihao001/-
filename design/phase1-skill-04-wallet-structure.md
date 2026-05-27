# Skill 4: meme-wallet-structure

## 定位

钱包结构分析。对标 Bubblemaps。负责回答：这些钱包之间有没有关系，有没有团伙结构。

## 输入

```json
{
  "token_address": "<address>",
  "chain": "sol",
  "wallet_roles": "<wallet_roles.json 路径>"
}
```

## GMGN 命令映射

本 skill 主要基于 wallet_roles 的已有数据做二次分析。额外查询：

| 用途 | 命令 |
|------|------|
| 补充钱包资金来源 | `gmgn-cli portfolio activity --chain sol --wallet <addr> --type buy --limit 5 --raw` |
| 补充钱包统计 | `gmgn-cli portfolio stats --chain sol --wallet <addr1> --wallet <addr2> --period 7d --raw` |
| 钱包间 token 余额确认 | `gmgn-cli portfolio token-balance --chain sol --wallet <addr> --token <token_addr> --raw` |

## 核心分析逻辑

### 同源资金检测

从 wallet_roles.key_wallets 提取所有 `native_transfer_from` 字段：

```python
# 伪代码
funding_groups = {}
for wallet in key_wallets:
    funder = wallet.native_transfer_from
    if funder:
        funding_groups.setdefault(funder, []).append(wallet.address)

# funding_groups 中 len(wallets) >= 2 的就是同源组
same_source_groups = {
    funder: wallets
    for funder, wallets in funding_groups.items()
    if len(wallets) >= 2
}
```

### 买入时间窗口聚类

```python
# 伪代码
from collections import defaultdict
time_clusters = defaultdict(list)
for wallet in key_wallets:
    bucket = wallet.start_holding_at // 300  # 5 分钟窗口
    time_clusters[bucket].append(wallet.address)

# 同一 5 分钟窗口内 >= 3 个钱包买入 = 疑似协调买入
coordinated_buys = {
    bucket: wallets
    for bucket, wallets in time_clusters.items()
    if len(wallets) >= 3
}
```

### 卖出模式聚类

```python
# 伪代码
# sell_amount_percentage 相似（差值 < 0.1）的钱包可能是同一操作者
distribution_groups = []
wallets_by_sell_pct = sorted(key_wallets, key=lambda w: w.sell_amount_percentage)
# 滑动窗口聚类
```

### 持仓集中度分析

```python
# 伪代码
top5_pct = sum(w.amount_percentage for w in sorted(key_wallets, key=lambda w: -w.amount_percentage)[:5])
top10_pct = sum(w.amount_percentage for w in sorted(key_wallets, key=lambda w: -w.amount_percentage)[:10])
top20_pct = sum(w.amount_percentage for w in sorted(key_wallets, key=lambda w: -w.amount_percentage)[:20])
```

## 输出

```json
{
  "schema_version": "1.0",
  "skill_name": "meme-wallet-structure",
  "task_id": "<token_address>_<timestamp>",
  "token_address": "<address>",
  "chain": "sol",
  "timestamp": "<ISO 8601>",
  "status": "PASS | WARN | BLOCK | NEED_MORE_DATA",

  "same_source_groups": [
    {
      "funding_source": "<funder address>",
      "wallets": ["<addr1>", "<addr2>"],
      "wallet_count": 2,
      "combined_holding_pct": 0.0,
      "combined_usd_value": 0.0,
      "group_type": "same_funder | same_cex | unknown"
    }
  ],

  "coordinated_buy_groups": [
    {
      "time_window_start": "<ISO 8601>",
      "time_window_end": "<ISO 8601>",
      "wallets": ["<addr1>", "<addr2>", "<addr3>"],
      "wallet_count": 3,
      "combined_holding_pct": 0.0
    }
  ],

  "distribution_groups": [
    {
      "pattern": "similar_sell_ratio | sequential_sell | transfer_chain",
      "wallets": [],
      "sell_ratio_range": [0.0, 0.0],
      "combined_sold_pct": 0.0
    }
  ],

  "concentration": {
    "top5_holder_pct": 0.0,
    "top10_holder_pct": 0.0,
    "top20_holder_pct": 0.0,
    "excluding_pools_and_cex": true,
    "concentration_level": "low | medium | high | extreme"
  },

  "suspected_controller_wallets": [
    {
      "address": "<wallet>",
      "reason": "funding_source_of_multiple | largest_holder_and_early | coordinated_buy_leader",
      "evidence_strength": "strong | moderate | weak",
      "holding_pct": 0.0
    }
  ],

  "structure_risk": {
    "has_same_source_groups": false,
    "same_source_combined_pct": 0.0,
    "has_coordinated_buys": false,
    "coordinated_buy_combined_pct": 0.0,
    "has_distribution_pattern": false,
    "concentration_level": "low | medium | high | extreme",
    "overall_structure_risk": "low | medium | high | critical"
  },

  "evidence": [],
  "counter_evidence": [],
  "confidence_score": 0.0,
  "downgrade_reasons": [],
  "blocker_reasons": [],
  "missing_fields": [],
  "valid_until": "<60min>",
  "next_action": "meme-evidence-chain",
  "handoff_to": "meme-evidence-chain"
}
```

## 判断规则

### 结构风险评分

| 条件 | overall_structure_risk |
|------|----------------------|
| 无同源组 + 无协调买入 + concentration low | low |
| 1 个同源组 combined < 10% 或 1 次协调买入 | medium |
| 同源组 combined > 20% 或 多次协调买入 或 concentration high | high |
| 同源组 combined > 40% 或 suspected_controller > 30% | critical |

### suspected_controller_wallets 判定

| 条件 | evidence_strength |
|------|------------------|
| 是 >= 3 个钱包的 funding source + 自身持仓 > 5% | strong |
| 是 >= 2 个钱包的 funding source | moderate |
| 最早买入 + 最大持仓 + 未卖出 | moderate |
| 仅 coordinated buy 中出现 | weak |

## 降级规则

| 条件 | 降级动作 |
|------|---------|
| key_wallets 中 native_transfer_from 全部为空 | downgrade: "No funding source data"; same_source_groups 设为 [] |
| key_wallets < 10 个 | downgrade: "Too few wallets for structure analysis" |
| 所有 start_holding_at = 0 | downgrade: "No holding timestamp data"; coordinated_buy_groups 设为 [] |

## 阻塞规则

| 条件 | 阻塞动作 |
|------|---------|
| wallet_roles.json 不存在或解析失败 | ERROR + blocker_report |
| wallet_roles.status = BLOCK | 继承 BLOCK，不执行本 skill |
