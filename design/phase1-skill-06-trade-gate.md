# Skill 6: meme-trade-gate

## 定位

门控判断。不是策略引擎。负责回答：这个 token 允许进入什么阶段。

## 输入

```json
{
  "token_address": "<address>",
  "chain": "sol",
  "token_panel": "<token_panel.json 路径>",
  "wallet_roles": "<wallet_roles.json 路径>",
  "wallet_structure": "<wallet_structure.json 路径>",
  "evidence_chain": "<evidence_chain.json 路径>"
}
```

## GMGN 命令映射

本 skill 不直接调用 GMGN API。它读取所有前置 skill 输出，做最终门控判断。

## 输出

```json
{
  "schema_version": "1.0",
  "skill_name": "meme-trade-gate",
  "task_id": "<token_address>_<timestamp>",
  "token_address": "<address>",
  "chain": "sol",
  "timestamp": "<ISO 8601>",
  "status": "PASS",

  "gate_decision": "BLOCK | WATCH | PAPER_ONLY | NEED_MORE_DATA",

  "decision_reasons": [
    {
      "rule_id": "G01",
      "rule_name": "<规则名>",
      "triggered": true,
      "input_value": "<触发值>",
      "threshold": "<阈值>",
      "contribution": "block | downgrade | positive"
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

  "next_review_conditions": [
    "<什么条件发生后应该重新评估>"
  ],

  "evidence": [],
  "counter_evidence": [],
  "confidence_score": 0.0,
  "downgrade_reasons": [],
  "blocker_reasons": [],
  "missing_fields": [],
  "valid_until": "<15min>",
  "next_action": "COMPLETED | paper_trading_runner",
  "handoff_to": "controller"
}
```

## 门控规则表

### 一票否决规则（→ BLOCK）

| Rule ID | 规则名 | 条件 | 来源 |
|---------|--------|------|------|
| G01 | Honeypot | token_panel.security.is_honeypot = "yes" | token_panel |
| G02 | Extreme Rug | token_panel.security.rug_ratio > 0.5 | token_panel |
| G03 | Unrenounced | renounced_mint = false AND renounced_freeze = false | token_panel |
| G04 | High Tax | buy_tax > 0.10 OR sell_tax > 0.10 | token_panel |
| G05 | Wash Trading | token_panel.security.is_wash_trading = true AND evidence_chain.dominant_behavior = WASH | token_panel + evidence |
| G06 | Critical Structure | wallet_structure.structure_risk.overall = "critical" AND confidence >= 0.7 | wallet_structure |

### 观察规则（→ WATCH）

| Rule ID | 规则名 | 条件 | 来源 |
|---------|--------|------|------|
| G10 | Dev Holding | creator_token_status = "creator_hold" AND creator_balance_rate > 0.05 | token_panel |
| G11 | High Concentration | top_10_holder_rate > 0.40 | token_panel |
| G12 | No Smart Money | smart_wallets = 0 AND smart_money_count = 0 | token_panel + wallet_roles |
| G13 | SM Distributing | sm_net_direction = "distributing" | wallet_roles |
| G14 | Low Liquidity | liquidity < 50000 | token_panel |
| G15 | High Rug Ratio | rug_ratio 0.3-0.5 | token_panel |
| G16 | Structure Risk High | overall_structure_risk = "high" | wallet_structure |
| G17 | Bundler Dominated | bundler_count > smart_money_count + kol_count | wallet_roles |
| G18 | Divergence | evidence_chain.dominant_behavior signals 包含 DIVERGENCE | evidence_chain |
| G19 | Low Confidence | evidence_chain.confidence_score < 0.5 | evidence_chain |

### PAPER_ONLY 条件

满足以下全部：
- 无 BLOCK 规则触发
- WATCH 规则触发 ≤ 2 个
- evidence_chain.confidence_score >= 0.5
- evidence_chain.dominant_behavior ∈ {ACCUMULATION, EARLY_STAGE}
- smart_money_count >= 1
- liquidity >= 10000
- rug_ratio < 0.3

### NEED_MORE_DATA 条件

- evidence_chain.status = NEED_MORE_DATA
- 或 evidence_chain.missing_fields 非空且包含关键字段
- 或 token_panel / wallet_roles / wallet_structure 任一 status = ERROR

## Gate Score 计算

```python
def calculate_gate_score(token_panel, wallet_roles, wallet_structure, evidence_chain):
    score = 0

    # Security (0-30)
    sec = token_panel.security
    if sec.renounced_mint and sec.renounced_freeze_account: score += 10
    if sec.rug_ratio < 0.1: score += 10
    elif sec.rug_ratio < 0.3: score += 5
    if sec.top_10_holder_rate < 0.2: score += 5
    elif sec.top_10_holder_rate < 0.4: score += 2
    if sec.creator_token_status == "creator_close": score += 5

    # Smart Money (0-30)
    sm = wallet_roles.smart_money_behavior
    sm_count = wallet_roles.wallet_summary.smart_money_count
    if sm_count >= 5: score += 15
    elif sm_count >= 3: score += 10
    elif sm_count >= 1: score += 5
    if sm.sm_net_direction == "accumulating": score += 10
    elif sm.sm_net_direction == "neutral": score += 5
    if sm.sm_avg_unrealized_pnl > 0: score += 5

    # Structure (0-20)
    struct = wallet_structure.structure_risk
    if struct.overall_structure_risk == "low": score += 20
    elif struct.overall_structure_risk == "medium": score += 10
    elif struct.overall_structure_risk == "high": score += 0

    # Behavior / Evidence (0-20)
    ev = evidence_chain
    if ev.dominant_behavior == "ACCUMULATION": score += 15
    elif ev.dominant_behavior == "EARLY_STAGE": score += 10
    elif ev.dominant_behavior == "DISTRIBUTION": score += 0
    if ev.confidence_score >= 0.8: score += 5
    elif ev.confidence_score >= 0.6: score += 3

    return min(score, 100)
```

### Score → Decision 映射

| Score Range | Decision |
|-------------|----------|
| 0-20 | BLOCK（除非无硬停规则，则 WATCH） |
| 21-45 | WATCH |
| 46-65 | WATCH（接近 PAPER，需 review） |
| 66-80 | PAPER_ONLY |
| 81-100 | PAPER_ONLY（Phase 1 最高只到 PAPER_ONLY） |

注意：Phase 1 不允许输出 SEMI_AUTO_READY 或 AUTO_READY。

## 降级规则

| 条件 | 降级动作 |
|------|---------|
| 前置 skill 任一有 downgrade | 继承 downgrade，gate_score 扣分 |
| evidence_chain.confidence < 0.6 | 最高只能 WATCH |
| wallet_structure 数据不全 | structure_score 最高给 10 |

## 阻塞规则

| 条件 | 阻塞动作 |
|------|---------|
| 任何 BLOCK 规则触发 | gate_decision = BLOCK |
| token_panel.status = BLOCK | 继承 BLOCK |
| evidence_chain 不存在 | gate_decision = NEED_MORE_DATA |

## next_review_conditions 生成

根据 gate_decision 和触发的 WATCH 规则自动生成：

| 触发规则 | next_review_condition |
|---------|----------------------|
| G10 Dev Holding | "Re-evaluate when creator_token_status changes to creator_close" |
| G12 No SM | "Re-evaluate when smart_degen_count >= 1" |
| G13 SM Distributing | "Re-evaluate when SM selling stops or new SM enters" |
| G14 Low Liquidity | "Re-evaluate when liquidity > $50k" |
| G19 Low Confidence | "Re-evaluate when more data available or structure analysis improves" |
