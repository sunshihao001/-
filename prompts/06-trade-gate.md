# PROMPT 6: Trade Gate — 门控判断

## 直接发给 GPT 的 Prompt

```
## 任务

执行 meme-trade-gate：读取前面所有分析结果，做最终门控判断。这是流水线最后一步。

## 输入

粘贴以下四个 JSON 的完整输出（或关键字段）：
1. token_panel.json
2. wallet_roles.json
3. wallet_structure.json
4. evidence_chain.json

## 你要做的事

### Step 1: 一票否决检查（任意命中 → BLOCK）

| Rule ID | 名称 | 条件 |
|---------|------|------|
| G01 | Honeypot | is_honeypot = "yes" |
| G02 | Extreme Rug | rug_ratio > 0.5 |
| G03 | Unrenounced | renounced_mint = false AND renounced_freeze = false |
| G04 | High Tax | buy_tax > 10% OR sell_tax > 10% |
| G05 | Wash Trading | is_wash_trading = true AND dominant_behavior = WASH |
| G06 | Critical Structure | overall_structure_risk = "critical" AND confidence >= 0.7 |

### Step 2: 观察规则检查（命中 → 降级）

| Rule ID | 名称 | 条件 |
|---------|------|------|
| G10 | Dev Holding | creator_hold AND creator_balance_rate > 5% |
| G11 | High Concentration | top_10_holder_rate > 40% |
| G12 | No SM | smart_wallets = 0 AND smart_money_count = 0 |
| G13 | SM Distributing | sm_net_direction = "distributing" |
| G14 | Low Liquidity | liquidity < $50k |
| G15 | Rug Ratio | rug_ratio 0.3-0.5 |
| G16 | Structure Risk | overall_structure_risk = "high" |
| G17 | Bundler Dominated | bundler_count > smart_money_count + kol_count |
| G18 | Divergence | behavior_signals 含 DIVERGENCE |
| G19 | Low Confidence | confidence_score < 0.5 |

### Step 3: Gate Score 计算

**Security (0-30):**
- renounced_mint + renounced_freeze = +10
- rug_ratio < 0.1 = +10, < 0.3 = +5
- top_10_holder_rate < 0.2 = +5, < 0.4 = +2
- creator_close = +5

**Smart Money (0-30):**
- sm_count >= 5 = +15, >= 3 = +10, >= 1 = +5
- sm accumulating = +10, neutral = +5
- sm_avg_unrealized_pnl > 0 = +5

**Structure (0-20):**
- overall_structure_risk = "low" = +20, "medium" = +10

**Behavior (0-20):**
- ACCUMULATION = +15, EARLY_STAGE = +10
- confidence >= 0.8 = +5, >= 0.6 = +3

Total = min(所有加分, 100)

### Step 4: Score → Decision

| Score | Decision |
|-------|----------|
| 0-20 | BLOCK（无硬停则 WATCH） |
| 21-65 | WATCH |
| 66-100 | PAPER_ONLY |

**PAPER_ONLY 额外要求**（全部满足才能给 PAPER_ONLY）：
- 无 BLOCK 规则触发
- WATCH 规则 ≤ 2 个
- confidence >= 0.5
- dominant_behavior ∈ {ACCUMULATION, EARLY_STAGE}
- smart_money_count >= 1
- liquidity >= $10k
- rug_ratio < 0.3

**如果 confidence < 0.6：最高只能给 WATCH**

### Step 5: 输出 JSON

```json
{
  "schema_version": "1.0",
  "skill_name": "meme-trade-gate",
  "task_id": "{CA}_{时间戳}",
  "token_address": "{CA}",
  "chain": "sol",
  "timestamp": "{ISO 8601}",
  "status": "PASS",
  "gate_decision": "BLOCK/WATCH/PAPER_ONLY/NEED_MORE_DATA",
  "decision_reasons": [
    {
      "rule_id": "G01",
      "rule_name": "Honeypot",
      "triggered": false,
      "input_value": "no",
      "threshold": "is_honeypot != yes",
      "contribution": "positive"
    }
  ],
  "gate_score": {
    "security_score": 0,
    "smart_money_score": 0,
    "structure_score": 0,
    "behavior_score": 0,
    "total_score": 0,
    "max_possible": 100
  },
  "phase_permission": {
    "research_allowed": true,
    "paper_allowed": false,
    "semi_auto_allowed": false,
    "auto_allowed": false
  },
  "next_review_conditions": [],
  "evidence": [],
  "counter_evidence": [],
  "confidence_score": 0.0,
  "downgrade_reasons": [],
  "blocker_reasons": [],
  "missing_fields": [],
  "valid_until": "{15分钟后}",
  "next_action": "COMPLETED",
  "handoff_to": "controller"
}
```

### Step 6: 生成 next_review_conditions

根据触发的 WATCH 规则自动生成：

| 触发规则 | 建议 |
|---------|------|
| G10 Dev Holding | "当 dev 卖出（creator_close）后重新评估" |
| G12 No SM | "当 smart money 进入后重新评估" |
| G13 SM Distributing | "当 SM 停止卖出或新 SM 进入后重新评估" |
| G14 Low Liquidity | "当流动性 > $50k 后重新评估" |
| G19 Low Confidence | "当有更多数据后重新评估" |

### Step 7: 同时输出中文摘要

```
📊 Gate Decision: {gate_decision}
📈 Score: {total_score}/100 (Security {s}/30 | SM {sm}/30 | Structure {st}/20 | Behavior {b}/20)
🎯 Confidence: {confidence_score}

✅ PASS Rules: {count}
⚠️ WATCH Rules: {triggered list}
🚫 BLOCK Rules: {triggered list}

下次重评条件：
{next_review_conditions}
```

## 关键约束

- **Phase 1 最高只能输出 PAPER_ONLY**，禁止 SEMI_AUTO_READY 和 AUTO_READY
- semi_auto_allowed 和 auto_allowed 永远是 false
- 不给买卖建议
- 不说"应该买入"、"可以抄底"
- gate_decision 只是"允许进入什么研究阶段"，不是交易指令
```
