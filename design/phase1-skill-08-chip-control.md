# Skill 8: meme-chip-control

## 定位

筹码控制权状态层（层 4）。回答：结构控制权是否仍然有效，处于什么状态，状态是否足够新鲜可靠可供下游使用。

## 上游输入

### 层 2 (meme-entity-clustering)

```json
wallet_entity_groups.json
same_source_groups.json
wallet_classification.json
entity_merge_completeness
```

### 层 3 (meme-structure-evidence)

```json
structure_evidence.json
  - structure_evidence_status
  - early_wallet_remaining_ratio
  - same_source_group_remaining_ratio
  - full_exit_count / partial_exit_count
  - distribution_receiver_count
  - backflow_address_count
  - wash_trading_level
  - evidence_completeness
```

### 层 1 (meme-data-standardizer)

```text
standardized_wallet_snapshot.json
standardized_kline_volume.json
completeness_report
snapshot_time
```

## Precondition

- `entity_merge_completeness > 0`
- `evidence_completeness > 0`
- `structure_evidence_status != INVALIDATED`
- 输入时间戳对齐

## Postcondition

- 输出 `chip_control_status.json`
- 包含 `chip_control_status`、`status_confidence`、`state_probabilities`
- 包含 `control_stock_score` + `per_entity_control_weight[]`
- 包含 `valid_until` / `ooda_status` / `unknown_reason`
- UNKNOWN 必须带 `unknown_reason`

## Invariant

- 已清仓实体权重恒 0
- CEX / pool / system / burn 地址不贡献控制权重
- normalized weights 之和为 1（当 `control_stock_score > floor`）
- 数据过期时不输出高置信度具体状态
- 不输出最终交易动作

## 设计守则

1. 周期位置守则（Howard Marks）
2. 模块边界守则（David Parnas）
3. 数据时效性守则（Nancy Leveson）
4. 概率判断守则（Michael Mauboussin）
5. 伪精度防护守则（Charlie Munger）

## 输出

### chip_control_status

```text
ESTABLISHING | ESTABLISHED | MAINTAINED | LOOSENING | TRANSFERRING | COLLAPSED | UNKNOWN
```

主状态带 `maintenance_type`:

```text
maintenance_type: ACTIVE | PASSIVE | UNKNOWN | null
```

### 公式总线

执行顺序：

```text
Step 0  输入对齐检查
Step 1  OODA 时效硬门禁
Step 2  控制库存硬门槛
Step 3  主通道计算
Step 4  实体权重计算
Step 5  信噪比修正
Step 6  贝叶斯状态更新
Step 7  状态机合法性检查
Step 8  输出接口
```

#### Step 1: OODA 硬门禁

```python
if remaining_validity_sec <= 0 or ooda_status == "EXPIRED":
    chip_control_status = "UNKNOWN"
    unknown_reason = "STALE_OODA_LOOP"
    refresh_required = true
    stop
```

#### Step 2: 控制库存硬门槛

```python
control_stock_score = sum(raw_entity_control_weight)

if control_stock_score < MIN_CONTROL_STOCK_FLOOR:
    if evidence complete and no inflow and no backflow:
        chip_control_status = "COLLAPSED"
    else:
        chip_control_status = "UNKNOWN"
        unknown_reason = "NO_VALID_ACTIVE_CONTROL_ENTITY"
    stop
```

#### Step 3: 主通道

```python
net_control_flow_score = control_inflow_score - control_outflow_score
control_raw = control_stock_score * net_control_flow_score
```

#### Step 4: 实体权重

```python
raw_entity_control_weight = (
    base_holding_weight
    * source_cohesion_multiplier
    * timing_role_multiplier
    * flow_behavior_multiplier
    * reflexive_confidence_modifier
    * ooda_validity_modifier
)
```

#### Step 5: 信噪比修正

```python
noise_factor = combine(
    reflexive_disguise_risk,
    camouflage_cost_score,
    data_quality_penalty,
)
control_effective = control_raw * (1 - noise_factor)
```

#### Step 6: 贝叶斯更新

```python
state_probabilities[t] = normalize(
    state_probabilities[t-1]
    * likelihood(control_effective, stock, flow, backflow, state)
    * base_rate_adjustment
)
```

#### Step 7: 状态机合法性

```python
if best_state violates allowed_transition:
    fallback_status = next_legal_candidate or "UNKNOWN"
    unknown_reason = "ILLEGAL_STATE_TRANSITION"
```

#### Step 8: 输出

```json
{
  "chip_control_status": "LOOSENING",
  "status_confidence": 0.68,
  "state_probabilities": {},
  "scores": {
    "control_stock_score": 0.63,
    "chip_control_retention_score": 0.72,
    "structure_exit_intensity_score": 0.58,
    "counterparty_pressure_score": 0.44,
    "distribution_progress_score": 0.37,
    "control_invalidation_risk": 0.52
  },
  "ooda": {
    "ooda_status": "AGING",
    "remaining_validity_sec": 72,
    "refresh_required": false
  },
  "unknown_reason": null,
  "recommended_downstream": "DEGRADE"
}
```

### 四投影分数

| 分数 | 公式简写 | 定位 |
|---|---|---|
| retention_score | 0.45*stock + 0.25*same_source + 0.15*concentration + 0.10*OODA + 0.05*(1-disguise) | 控制权保留 |
| exit_intensity | 0.35*outflow + 0.25*sell_pressure + 0.15*sync_exit + 0.15*exit_done + 0.10*(1-backflow) | 结构侧撤退 |
| counterparty_pressure | 0.30*new_holder + 0.25*new_whale + 0.20*receiver_dispersion + 0.15*external_flow + 0.10*price_impact | 对手盘压力 |
| distribution_progress | 0.30*sold_ratio + 0.20*receiver_dispersion + 0.20*remaining_decline + 0.15*profit_recycle + 0.15*exit_continuity | 派发进度 |

### 多实体权重

必须同时输出：

```text
control_stock_score = sum(raw_entity_control_weight)
per_entity_control_weight_i = raw_i / control_stock_score
```

归一化前排除：dust / POOL / CEX / SYSTEM / BURN。

### Veto

```text
FULL_EXIT           → raw_weight = 0
STALE_ENTITY_DATA   → ooda_modifier 降低
REFLEXIVE_DISGUISE  → reflexive_modifier 降低
CLUSTER_CONFLICT    → source_multiplier 降低
DOWNSTREAM_UNSAFE   → recommended_downstream = PAUSE
```

输出名为 `entity_control_veto_evidence[]`，不叫 `final_veto`。

### 状态机

```text
UNKNOWN → 任意状态
ESTABLISHING → ESTABLISHED / MAINTAINED / COLLAPSED / UNKNOWN
ESTABLISHED → MAINTAINED / LOOSENING / TRANSFERRING / COLLAPSED / UNKNOWN
MAINTAINED → ESTABLISHED / LOOSENING / TRANSFERRING / COLLAPSED / UNKNOWN
LOOSENING → MAINTAINED / TRANSFERRING / COLLAPSED / UNKNOWN
TRANSFERRING → MAINTAINED / LOOSENING / COLLAPSED / UNKNOWN
COLLAPSED → UNKNOWN / ESTABLISHING（有新结构证据合法）
```

### UNKNOWN 原因

```text
EVIDENCE_INSUFFICIENT
CONFLICTING_SIGNALS
STALE_INPUT
STALE_OODA_LOOP
REFLEXIVE_DISGUISE_RISK
ENTITY_CLUSTER_UNVERIFIED
MISSING_CRITICAL_BYTES
DOWNSTREAM_WINDOW_TOO_SHORT
ILLEGAL_STATE_TRANSITION
INPUT_NOT_ALIGNED
NO_VALID_ACTIVE_CONTROL_ENTITY
```

## 下游接口

### 给层 5 (meme-lifecycle-classifier)

可读：

```text
chip_control_status
status_confidence
state_probabilities
retention_score / exit_intensity / counterparty_pressure / distribution_progress
flow_direction
maintenance_type
valid_until
unknown_reason
```

不可读：

```text
per_entity_control_weight
raw_entity_control_weight
内部 multiplier
veto 明细
```

### 给层 7 (meme-final-gate)

可读：

```text
chip_control_status
status_confidence
control_invalidation_risk
distribution_progress_score
exit_intensity / counterparty_pressure
valid_until
recommended_downstream
unknown_reason
entity_control_veto_evidence[]
transition_result
```

## recommended_downstream

```text
CONTINUE | DEGRADE | PAUSE | REFRESH_REQUIRED | REVIEW_REQUIRED
```

禁止输出：

```text
BUY / SELL / BLOCK / PAPER_READY / AUTO_READY
```

## 降级规则

| 条件 | 降级动作 |
|---|---|
| OODA AGING | time_decay_confidence_modifier 降低 |
| OODA STALE | 最高只能 UNKNOWN |
| evidence_completeness < threshold | unknown_reason = EVIDENCE_INSUFFICIENT |
| reflexive_disguise_risk 高 | state_ambiguity 上升，confidence 降低 |
| entity_cluster_confidence 低 | weight_confidence 降低，可保留为 UNVERIFIED |
| 分数冲突 | score_conflicts 记录，进入贝叶斯但 confidence 降低 |

## 阻塞规则

| 条件 | 阻塞动作 |
|---|---|
| OODA EXPIRED | UNKNOWN + 停止后续计算 |
| remaining_validity_sec <= 0 | UNKNOWN + refresh_required |
| 输入时间戳不对齐 | UNKNOWN + INPUT_NOT_ALIGNED |
| 关键 bytes 缺失 | UNKNOWN + MISSING_CRITICAL_BYTES |
| 状态转移非法 | UNKNOWN + ILLEGAL_STATE_TRANSITION |

## 禁止输出

```text
- BUY / SELL / BLOCK / PAPER_READY / AUTO_READY
- 确定控盘 / 确定庄家 / 一定会涨 / 一定会跌
- final_veto
```