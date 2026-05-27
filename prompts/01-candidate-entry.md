# PROMPT 1: Candidate Entry — 候选入口验证

## 直接发给 GPT 的 Prompt

```
## 任务

执行 meme-candidate-entry：验证一个 Solana token 地址是否可以进入分析流水线。

## 输入

Token 地址：{在这里填 CA}
来源：{manual_ca / gmgn_trending / gmgn_trenches / telegram}
原因：{为什么要看这个 token}

## 你要做的事

### Step 1: 生成数据采集命令

输出以下命令（我会把结果粘回来给你）：

```bash
gmgn-cli token info --chain sol --address {CA} --raw
```

### Step 2: 收到数据后，检查以下条件

| 检查项 | 通过条件 | 不通过 |
|--------|---------|--------|
| 地址格式 | base58, 32-44 字符 | BLOCK: "Invalid address format" |
| token 存在 | token info 返回数据 | BLOCK: "Token not found" |
| 有交易池 | biggest_pool_address 非空 | BLOCK: "No pool found" |
| 有流动性 | liquidity > 0 | BLOCK: "Zero liquidity" |
| 未在 bonding curve | launchpad_status = 2 或无 launchpad | WARN: "Still on bonding curve" |

### 降级条件（不阻塞但记录）

- token 创建时间 < 10 分钟 → downgrade: "Extremely new token"
- 无社交链接 → downgrade: "No social links"
- holder_count < 50 → downgrade: "Very few holders"

### Step 3: 输出严格按以下 JSON

```json
{
  "schema_version": "1.0",
  "skill_name": "meme-candidate-entry",
  "task_id": "{CA}_{当前时间戳}",
  "token_address": "{CA}",
  "chain": "sol",
  "timestamp": "{ISO 8601}",
  "status": "PASS 或 BLOCK 或 ERROR",
  "entry_source": "{来源}",
  "entry_reason": "{原因}",
  "token_symbol": "{从数据提取}",
  "token_name": "{从数据提取}",
  "creation_timestamp": "{token 创建时间}",
  "launchpad": "{launchpad 名}",
  "initial_validation": {
    "address_valid": true/false,
    "token_exists": true/false,
    "has_pool": true/false,
    "has_liquidity": true/false,
    "is_on_curve": true/false
  },
  "evidence": [
    {"claim": "检查通过的项", "source": "gmgn-cli token info", "value": "具体值", "weight": "high"}
  ],
  "counter_evidence": [],
  "confidence_score": 1.0,
  "downgrade_reasons": [],
  "blocker_reasons": [],
  "missing_fields": [],
  "valid_until": "{30分钟后}",
  "next_action": "meme-token-panel",
  "handoff_to": "meme-token-panel"
}
```

## 禁止

- 不要编造任何数据字段
- 不要给出买卖建议
- 不要跳过任何检查项
- 如果 token info 返回错误，直接输出 status: "ERROR"
```
