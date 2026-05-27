# Skill 1: meme-candidate-entry

## 定位

候选发现入口。负责回答：这次分析哪些 token，为什么。

## 输入

### 手动模式（Phase 1 默认）

```json
{
  "mode": "manual",
  "token_address": "<base58 solana address>",
  "chain": "sol",
  "entry_source": "manual_ca | gmgn_trending | gmgn_trenches | gmgn_signal | smartmoney_cluster | telegram",
  "entry_reason": "<为什么要看这个 token>"
}
```

### 自动模式（Phase 3 GMGN 候选池）

```json
{
  "mode": "auto",
  "chain": "sol",
  "source_commands": [
    "gmgn-cli market trending --chain sol --interval 1h --order-by volume --limit 50 --raw",
    "gmgn-cli market trenches --chain sol --type completed --filter-preset strict --sort-by smart_degen_count --raw",
    "gmgn-cli market signal --chain sol --signal-type 12 --raw"
  ]
}
```

## GMGN 命令映射

| 用途 | 命令 |
|------|------|
| 热门 token | `gmgn-cli market trending --chain sol --interval 1h --order-by volume --limit 50 --raw` |
| 新币（已毕业） | `gmgn-cli market trenches --chain sol --type completed --filter-preset strict --sort-by smart_degen_count --raw` |
| Smart money 买入信号 | `gmgn-cli market signal --chain sol --signal-type 12 --raw` |
| 验证 token 地址有效 | `gmgn-cli token info --chain sol --address <addr> --raw` |

## 输出

```json
{
  "schema_version": "1.0",
  "skill_name": "meme-candidate-entry",
  "task_id": "<token_address>_<timestamp>",
  "token_address": "<address>",
  "chain": "sol",
  "timestamp": "<ISO 8601>",
  "status": "PASS | BLOCK | ERROR",
  "entry_source": "<来源>",
  "entry_reason": "<原因>",
  "token_symbol": "<从 token info 获取>",
  "token_name": "<从 token info 获取>",
  "creation_timestamp": "<token 创建时间>",
  "launchpad": "<launchpad 平台>",
  "initial_validation": {
    "address_valid": true,
    "token_exists": true,
    "has_pool": true,
    "has_liquidity": true,
    "is_on_curve": false
  },
  "evidence": [],
  "counter_evidence": [],
  "confidence_score": 1.0,
  "downgrade_reasons": [],
  "blocker_reasons": [],
  "missing_fields": [],
  "valid_until": "<30min>",
  "next_action": "meme-token-panel",
  "handoff_to": "meme-token-panel"
}
```

## 判断规则

| 检查项 | 通过条件 | 不通过动作 |
|--------|---------|-----------|
| 地址格式 | base58, 32-44 字符 | BLOCK: "Invalid address format" |
| token 存在 | token info 返回数据 | BLOCK: "Token not found" |
| 有交易池 | biggest_pool_address 非空 | BLOCK: "No pool found" |
| 有流动性 | liquidity > 0 | BLOCK: "Zero liquidity" |
| 未在 bonding curve 上 | launchpad_status = 2 或无 launchpad | WARN: "Still on bonding curve" |

## 降级规则

| 条件 | 降级动作 |
|------|---------|
| token 创建时间 < 10 分钟 | downgrade: "Extremely new token, < 10min" |
| 无社交链接 | downgrade: "No social links" |
| holder_count < 50 | downgrade: "Very few holders" |

## 阻塞规则

| 条件 | 阻塞动作 |
|------|---------|
| 地址无效 | BLOCK + 停止 |
| token 不存在 | BLOCK + 停止 |
| 无交易池 | BLOCK + 停止 |
| 零流动性 | BLOCK + 停止 |

## Phase 1 行为

- 默认手动模式：用户提供 token CA
- 调用 `token info` 验证 token 存在且有效
- 记录来源和原因
- 写入 `data/runs/<token_address>/candidate_entry.json`
- 更新 `phase_state.json`
