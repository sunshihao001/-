# PROMPT 4: Wallet Structure — 钱包结构分析

## 直接发给 GPT 的 Prompt

```
## 任务

执行 meme-wallet-structure：分析钱包之间的关联结构（同源资金、协调买入、集中度、疑似控盘）。

## 输入

Token 地址：{CA}
前置 wallet_roles.json：{粘贴完整 JSON 或关键字段}

需要用到的字段：
- key_wallets 数组中每个钱包的：address, native_transfer_from, start_holding_at, amount_percentage, sell_amount_percentage, role

## 你要做的事

### Step 1: 同源资金检测

从 key_wallets 中提取所有 native_transfer_from 字段，找出：
- 同一个地址给 >= 2 个钱包打款 = 一个同源组
- 计算每个同源组的 combined_holding_pct 和 combined_usd_value
- 判断 group_type：
  - 如果 funder 是已知 CEX 地址 → "same_cex"
  - 否则 → "same_funder"

### Step 2: 买入时间窗口聚类

- 以 5 分钟为窗口，对所有 start_holding_at 聚类
- 同一窗口内 >= 3 个钱包买入 = 疑似协调买入
- 记录窗口时间范围、涉及钱包、combined_holding_pct

### Step 3: 卖出模式聚类

- 找 sell_amount_percentage 相近的钱包（差值 < 0.1）
- 如果 >= 3 个钱包卖出比例高度一致 → 可能同一操作者

### Step 4: 持仓集中度

- top5_holder_pct = 前 5 大持仓合计
- top10_holder_pct = 前 10 大合计
- top20_holder_pct = 前 20 大合计
- 排除池子地址和已知 CEX 地址
- concentration_level：< 20% = low, 20-40% = medium, 40-60% = high, > 60% = extreme

### Step 5: 疑似控盘钱包

| 条件 | evidence_strength |
|------|------------------|
| 是 >= 3 个钱包的 funding source 且自身持仓 > 5% | strong |
| 是 >= 2 个钱包的 funding source | moderate |
| 最早买入 + 最大持仓 + 未卖出 | moderate |
| 仅 coordinated buy 中出现 | weak |

### Step 6: 结构风险评分

| 条件 | overall_structure_risk |
|------|----------------------|
| 无同源组 + 无协调买入 + concentration low | low |
| 1 个同源组 combined < 10% 或 1 次协调买入 | medium |
| 同源组 combined > 20% 或 多次协调买入 或 concentration high | high |
| 同源组 combined > 40% 或 suspected_controller > 30% | critical |

### Step 7: 如果 wallet_roles 中 native_transfer_from 数据不全

可补充查询：
```bash
gmgn-cli portfolio activity --chain sol --wallet {addr} --type buy --limit 5 --raw
gmgn-cli portfolio stats --chain sol --wallet {addr1} --wallet {addr2} --period 7d --raw
```

### Step 8: 输出 JSON

```json
{
  "schema_version": "1.0",
  "skill_name": "meme-wallet-structure",
  "task_id": "{CA}_{时间戳}",
  "token_address": "{CA}",
  "chain": "sol",
  "timestamp": "{ISO 8601}",
  "status": "PASS/WARN/BLOCK/NEED_MORE_DATA",
  "same_source_groups": [
    {
      "funding_source": "{funder address}",
      "wallets": ["{addr1}", "{addr2}"],
      "wallet_count": 2,
      "combined_holding_pct": 0.0,
      "combined_usd_value": 0.0,
      "group_type": "same_funder/same_cex/unknown"
    }
  ],
  "coordinated_buy_groups": [
    {
      "time_window_start": "{ISO 8601}",
      "time_window_end": "{ISO 8601}",
      "wallets": [],
      "wallet_count": 0,
      "combined_holding_pct": 0.0
    }
  ],
  "distribution_groups": [
    {
      "pattern": "similar_sell_ratio/sequential_sell/transfer_chain",
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
    "concentration_level": "low/medium/high/extreme"
  },
  "suspected_controller_wallets": [
    {
      "address": "",
      "reason": "",
      "evidence_strength": "strong/moderate/weak",
      "holding_pct": 0.0
    }
  ],
  "structure_risk": {
    "has_same_source_groups": false,
    "same_source_combined_pct": 0.0,
    "has_coordinated_buys": false,
    "coordinated_buy_combined_pct": 0.0,
    "has_distribution_pattern": false,
    "concentration_level": "",
    "overall_structure_risk": "low/medium/high/critical"
  },
  "evidence": [],
  "counter_evidence": [],
  "confidence_score": 0.0,
  "downgrade_reasons": [],
  "blocker_reasons": [],
  "missing_fields": [],
  "valid_until": "{60分钟后}",
  "next_action": "meme-evidence-chain",
  "handoff_to": "meme-evidence-chain"
}
```

### 降级条件

- native_transfer_from 全部为空 → downgrade + same_source_groups 设 []
- key_wallets < 10 个 → downgrade: "Too few wallets"
- start_holding_at 全部为 0 → downgrade + coordinated_buy_groups 设 []

## 禁止

- 不说"确定庄家"、"确定控盘"
- 用"疑似同源组"、"疑似协调买入"、"候选控盘钱包"
- 不编造资金关系
- funding source 数据缺失时不猜测
```
