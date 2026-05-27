# Skill 5: meme-evidence-chain

## 定位

证据链生成。对标 Arkham。负责回答：前面所有分析汇总成什么判断，证据是什么，反证是什么，置信度多少。

## 输入

```json
{
  "token_address": "<address>",
  "chain": "sol",
  "token_panel": "<token_panel.json 路径>",
  "wallet_roles": "<wallet_roles.json 路径>",
  "wallet_structure": "<wallet_structure.json 路径>"
}
```

## GMGN 命令映射

本 skill 不直接调用 GMGN API。它读取前三个 skill 的输出，做汇总推断。

## 核心分析逻辑

### 行为推断引擎

从已有数据推断当前 token 的主导行为：

```python
def infer_behavior(token_panel, wallet_roles, wallet_structure):
    signals = []

    # Signal 1: SM 方向
    sm = wallet_roles.smart_money_behavior
    if sm.sm_net_direction == "accumulating":
        signals.append(("ACCUMULATION", "high", "Smart money accumulating"))
    elif sm.sm_net_direction == "distributing":
        signals.append(("DISTRIBUTION", "high", "Smart money distributing"))

    # Signal 2: 结构风险
    struct = wallet_structure.structure_risk
    if struct.has_same_source_groups and struct.same_source_combined_pct > 0.2:
        signals.append(("CONTROLLED", "medium", f"Same-source groups hold {struct.same_source_combined_pct:.0%}"))

    # Signal 3: Dev 状态
    dev = wallet_roles.dev_profile
    if dev.creator_token_status == "creator_hold" and dev.creator_balance_rate > 0.05:
        signals.append(("DEV_RISK", "medium", "Dev holding significant position"))
    elif dev.creator_token_status == "creator_close":
        signals.append(("DEV_EXITED", "low", "Dev has exited"))

    # Signal 4: Wash trading
    if token_panel.security.is_wash_trading:
        signals.append(("WASH_TRADING", "high", "Wash trading detected"))

    # Signal 5: 价格趋势 vs 钱包行为
    if token_panel.kline_summary.trend == "up" and sm.sm_net_direction == "distributing":
        signals.append(("DIVERGENCE", "high", "Price up but SM distributing"))

    # Signal 6: Fresh wallet 占比
    if wallet_roles.wallet_summary.fresh_wallet_count / max(wallet_roles.wallet_summary.total_holders_sampled, 1) > 0.5:
        signals.append(("ARTIFICIAL", "medium", "Majority fresh wallets"))

    return signals
```

### 置信度计算

```python
def calculate_confidence(signals, downgrade_count, missing_count):
    base = 0.8
    # 每个 high weight signal +0.05, medium +0.03
    for behavior, weight, reason in signals:
        if weight == "high": base += 0.05
        elif weight == "medium": base += 0.03
    # 每个 downgrade -0.1
    base -= downgrade_count * 0.1
    # 每个 missing field -0.05
    base -= missing_count * 0.05
    return max(0.1, min(1.0, base))
```

### 行为分类

| 行为 | 条件组合 |
|------|---------|
| ACCUMULATION | SM accumulating + no distribution pattern + low structure risk |
| DISTRIBUTION | SM distributing 或 distribution_groups 非空 |
| WASH | is_wash_trading = true |
| CONTROLLED | same_source combined > 20% 或 suspected_controller 存在 |
| EXIT | dev exited + SM distributing + volume declining |
| EARLY_STAGE | token age < 1h + smart_money_count >= 1 + no distribution |
| UNKNOWN | 信号冲突或数据不足 |

## 输出

```json
{
  "schema_version": "1.0",
  "skill_name": "meme-evidence-chain",
  "task_id": "<token_address>_<timestamp>",
  "token_address": "<address>",
  "chain": "sol",
  "timestamp": "<ISO 8601>",
  "status": "PASS | WARN | NEED_MORE_DATA",

  "dominant_behavior": "ACCUMULATION | DISTRIBUTION | WASH | CONTROLLED | EXIT | EARLY_STAGE | UNKNOWN",

  "behavior_signals": [
    {
      "behavior": "<behavior type>",
      "weight": "high | medium | low",
      "reason": "<具体原因>",
      "source_skill": "token_panel | wallet_roles | wallet_structure",
      "source_field": "<具体字段>"
    }
  ],

  "narrative": {
    "one_line": "<一句话总结>",
    "paragraph": "<2-3 句证据叙事>"
  },

  "evidence_summary": {
    "total_evidence_count": 0,
    "high_weight_count": 0,
    "medium_weight_count": 0,
    "low_weight_count": 0,
    "counter_evidence_count": 0
  },

  "risk_factors": [
    {
      "factor": "<风险因素>",
      "severity": "critical | high | medium | low",
      "source": "<来源>"
    }
  ],

  "positive_signals": [
    {
      "signal": "<积极信号>",
      "strength": "strong | moderate | weak",
      "source": "<来源>"
    }
  ],

  "evidence": [],
  "counter_evidence": [],
  "confidence_score": 0.0,
  "downgrade_reasons": [],
  "blocker_reasons": [],
  "missing_fields": [],
  "valid_until": "<30min>",
  "next_action": "meme-trade-gate",
  "handoff_to": "meme-trade-gate"
}
```

## 叙事生成规则

### one_line 模板

```
"{symbol}: {dominant_behavior}. SM {sm_direction}, structure risk {level}, dev {status}. Confidence {score}."
```

示例：

```
"PEPE: ACCUMULATION. SM accumulating (5 wallets), structure risk low, dev exited. Confidence 0.82."
"DOGE: DISTRIBUTION. SM distributing, same-source group holds 25%, dev holding. Confidence 0.65."
"SCAM: WASH. Wash trading detected, bundler dominated, no SM. Confidence 0.91."
```

### paragraph 模板

```
"{symbol} 当前主导行为判断为 {dominant_behavior}。
证据：{top 3 behavior_signals, each with reason}。
反面证据：{top counter_evidences}。
风险因素：{risk_factors}。
置信度 {confidence_score}，降级原因：{downgrade_reasons 或 '无'}。"
```

## 判断规则

| 条件 | status |
|------|--------|
| dominant_behavior 可判定 + confidence >= 0.6 | PASS |
| dominant_behavior 可判定 + confidence 0.4-0.6 | WARN |
| dominant_behavior = UNKNOWN 或 confidence < 0.4 | NEED_MORE_DATA |

## 降级规则

| 条件 | 降级动作 |
|------|---------|
| wallet_structure 缺 same_source 数据 | downgrade: "No funding source data for structure"; confidence -0.15 |
| wallet_roles 缺 SM 数据 | downgrade: "No smart money data"; confidence -0.10 |
| token_panel 缺 kline | downgrade: "No price trend data"; confidence -0.05 |
| 信号相互冲突（例如 SM accumulating 但 structure risk critical） | downgrade: "Conflicting signals"; confidence -0.10 |

## 阻塞规则

| 条件 | 阻塞动作 |
|------|---------|
| token_panel.status = BLOCK | 继承 BLOCK，不执行 |
| wallet_roles.json 不存在 | ERROR + blocker_report |
| wallet_structure.json 不存在 | ERROR + blocker_report（但可降级运行，仅用 token_panel + wallet_roles） |

## 禁止输出

```
禁止：确定庄家 / 确定内幕 / 一定会涨 / 一定会跌
禁止：买入建议 / 卖出建议
禁止：直接交易决策
```

所有输出必须保留：
```
疑似 / 候选 / 证据等级 / 置信度 / 降级原因
```
