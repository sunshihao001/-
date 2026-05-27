# PROMPT 5: Evidence Chain — 证据链汇总

## 直接发给 GPT 的 Prompt

```
## 任务

执行 meme-evidence-chain：汇总前三步（token_panel + wallet_roles + wallet_structure）的所有证据，推断当前 token 的主导行为，输出证据叙事和置信度。

## 输入

粘贴以下三个 JSON 的完整输出（或关键字段）：
1. token_panel.json
2. wallet_roles.json
3. wallet_structure.json

## 你要做的事

### Step 1: 行为信号提取

从三个输入中提取以下信号：

| 信号 | 条件 | 权重 | 来源 |
|------|------|------|------|
| ACCUMULATION | sm_net_direction = "accumulating" | high | wallet_roles |
| DISTRIBUTION | sm_net_direction = "distributing" | high | wallet_roles |
| CONTROLLED | same_source_combined_pct > 20% | medium | wallet_structure |
| DEV_RISK | creator_hold + creator_balance_rate > 5% | medium | token_panel |
| DEV_EXITED | creator_token_status = "creator_close" | low | token_panel |
| WASH_TRADING | is_wash_trading = true | high | token_panel |
| DIVERGENCE | 价格涨但 SM 在卖 | high | token_panel + wallet_roles |
| ARTIFICIAL | fresh_wallet 占比 > 50% | medium | wallet_roles |
| COORDINATED | 有协调买入组 | medium | wallet_structure |
| LOW_LIQUIDITY | liquidity < $50k | low | token_panel |

### Step 2: 主导行为判定

根据信号组合判定 dominant_behavior：

| 行为 | 条件组合 |
|------|---------|
| ACCUMULATION | SM accumulating + 无 distribution pattern + structure risk low/medium |
| DISTRIBUTION | SM distributing 或 有 distribution_groups |
| WASH | is_wash_trading = true |
| CONTROLLED | same_source combined > 20% 或 suspected_controller 存在 |
| EXIT | dev exited + SM distributing + volume declining |
| EARLY_STAGE | token age < 1h + smart_money >= 1 + 无 distribution |
| UNKNOWN | 信号冲突或数据不足 |

### Step 3: 置信度计算

base = 0.8
- 每个 high 权重信号 +0.05
- 每个 medium 权重信号 +0.03
- 每个 downgrade（从三个前置 skill 继承） -0.10
- 每个 missing_field -0.05
- 信号冲突 -0.10
- 最终值 clamp 到 [0.1, 1.0]

### Step 4: 叙事生成

**one_line 格式**：
"{symbol}: {dominant_behavior}. SM {direction} ({count} wallets), structure risk {level}, dev {status}. Confidence {score}."

**paragraph 格式**：
"{symbol} 当前主导行为判断为 {dominant_behavior}。
证据：{top 3 behavior_signals, each with reason}。
反面证据：{counter_evidences}。
风险因素：{risk_factors}。
置信度 {score}，降级原因：{downgrade_reasons 或 '无'}。"

### Step 5: 输出 JSON

```json
{
  "schema_version": "1.0",
  "skill_name": "meme-evidence-chain",
  "task_id": "{CA}_{时间戳}",
  "token_address": "{CA}",
  "chain": "sol",
  "timestamp": "{ISO 8601}",
  "status": "PASS/WARN/NEED_MORE_DATA",
  "dominant_behavior": "ACCUMULATION/DISTRIBUTION/WASH/CONTROLLED/EXIT/EARLY_STAGE/UNKNOWN",
  "behavior_signals": [
    {
      "behavior": "ACCUMULATION",
      "weight": "high",
      "reason": "5 smart money wallets accumulating, avg sell ratio 0.12",
      "source_skill": "wallet_roles",
      "source_field": "smart_money_behavior.sm_net_direction"
    }
  ],
  "narrative": {
    "one_line": "...",
    "paragraph": "..."
  },
  "evidence_summary": {
    "total_evidence_count": 0,
    "high_weight_count": 0,
    "medium_weight_count": 0,
    "low_weight_count": 0,
    "counter_evidence_count": 0
  },
  "risk_factors": [
    {"factor": "...", "severity": "critical/high/medium/low", "source": "..."}
  ],
  "positive_signals": [
    {"signal": "...", "strength": "strong/moderate/weak", "source": "..."}
  ],
  "evidence": [],
  "counter_evidence": [],
  "confidence_score": 0.0,
  "downgrade_reasons": [],
  "blocker_reasons": [],
  "missing_fields": [],
  "valid_until": "{30分钟后}",
  "next_action": "meme-trade-gate",
  "handoff_to": "meme-trade-gate"
}
```

### 同时输出 Markdown 报告

```markdown
# Evidence Chain: {symbol}

## 主导行为: {dominant_behavior}
置信度: {confidence_score}

## 一句话
{one_line}

## 详细叙事
{paragraph}

## 正面证据
{positive_signals 列表}

## 风险因素
{risk_factors 列表}

## 反面证据
{counter_evidence 列表}

## 降级记录
{downgrade_reasons}

## 数据缺失
{missing_fields}
```

### 判断 status

| 条件 | status |
|------|--------|
| dominant_behavior 可判定 + confidence >= 0.6 | PASS |
| dominant_behavior 可判定 + confidence 0.4-0.6 | WARN |
| UNKNOWN 或 confidence < 0.4 | NEED_MORE_DATA |

## 禁止

- 禁止说"确定庄家"、"确定内幕"、"一定会涨"、"一定会跌"
- 禁止给买入建议或卖出建议
- 禁止输出交易决策
- 所有判断保留"疑似/候选/证据等级/置信度"
- 如果证据冲突，dominant_behavior 必须设为 UNKNOWN 或降低 confidence
```
