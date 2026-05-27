# Skill 7: meme-workflow-controller

## 定位

流程总控。不做业务判断。负责：按顺序调度 6 个 skill，管理 phase_state，处理错误恢复和超时。

## 触发方式

```bash
# 用户在 Telegram 发送
/sol <token_address>
/sol <token_address> --from wallet_roles   # 从某个阶段恢复
/sol status <token_address>                # 查看状态
/sol list                                  # 当前活跃的分析任务
```

## 输入

```json
{
  "command": "run | resume | status | list",
  "token_address": "<address>",
  "chain": "sol",
  "resume_from": null,
  "force_refresh": false
}
```

## 执行流程

```
START
│
├─ 1. 验证输入
│     ├─ 地址格式检查
│     ├─ 检查是否已有进行中的分析
│     └─ 如果 resume，加载 phase_state.json
│
├─ 2. 初始化目录
│     └─ data/runs/<token_address>/
│         ├─ phase_state.json
│         └─ ...
│
├─ 3. 执行 meme-candidate-entry
│     ├─ PASS → 继续
│     ├─ BLOCK → 写 blocker_report → 停止
│     └─ ERROR → 写 blocker_report → 停止
│
├─ 4. 执行 meme-token-panel
│     ├─ PASS → 继续
│     ├─ WARN → 记录 → 继续
│     ├─ BLOCK → 写 blocker_report → 停止
│     └─ ERROR → 写 blocker_report → 停止
│
├─ 5. 执行 meme-wallet-roles
│     ├─ PASS → 继续
│     ├─ WARN → 记录 → 继续
│     ├─ NEED_MORE_DATA → 降级记录 → 继续（可降级运行后续）
│     └─ ERROR → 写 blocker_report → 停止
│
├─ 6. 执行 meme-wallet-structure
│     ├─ PASS → 继续
│     ├─ WARN → 记录 → 继续
│     ├─ NEED_MORE_DATA → 降级记录 → 继续
│     └─ ERROR → 降级记录 → 继续（structure 不硬性要求）
│
├─ 7. 执行 meme-evidence-chain
│     ├─ PASS → 继续
│     ├─ WARN → 继续
│     ├─ NEED_MORE_DATA → 记录 → 继续到 gate
│     └─ ERROR → 写 blocker_report → 停止
│
├─ 8. 执行 meme-trade-gate
│     ├─ 输出 gate_decision
│     └─ 记录到 phase_state
│
├─ 9. 生成 workflow_summary.md
│
└─ 10. 输出结果到 Telegram
```

## Phase State 管理

### 写入时机

| 事件 | 写入内容 |
|------|---------|
| 开始新任务 | 创建 phase_state.json, current_phase = "candidate_entry" |
| 每个 skill 完成 | 更新 completed_phases, current_phase = 下一个 |
| skill 返回 BLOCK | blocked_at, blocker_phase, blocker_reasons |
| skill 返回 ERROR | blocked_at, blocker_phase, blocker_reasons |
| 全部完成 | current_phase = "COMPLETED", gate_decision |

### 恢复逻辑

```python
def resume_from_phase(token_address, resume_phase):
    state = load_phase_state(token_address)

    # 验证 resume_phase 之前的所有 phase 都已完成
    phase_order = [
        "candidate_entry", "token_panel", "wallet_roles",
        "wallet_structure", "evidence_chain", "trade_gate"
    ]
    resume_idx = phase_order.index(resume_phase)
    completed = [p["phase"] for p in state["completed_phases"]]

    for i in range(resume_idx):
        if phase_order[i] not in completed:
            # 缺少前置，需要从这里重跑
            return phase_order[i]

    return resume_phase
```

### 数据过期检查

```python
def check_data_freshness(token_address):
    """检查已有数据是否过期"""
    ttl_map = {
        "candidate_entry": 1800,    # 30 min
        "token_panel": 1800,        # 30 min
        "wallet_roles": 3600,       # 60 min
        "wallet_structure": 3600,   # 60 min
        "evidence_chain": 1800,     # 30 min
        "trade_gate": 900           # 15 min
    }
    stale = []
    for phase, ttl in ttl_map.items():
        output_file = f"data/runs/{token_address}/{phase}.json"
        if os.path.exists(output_file):
            age = time.time() - os.path.getmtime(output_file)
            if age > ttl:
                stale.append(phase)
    return stale
```

## Telegram 输出格式

### 进行中

```
🔄 Analyzing {symbol} ({token_address[:8]}...)
━━━━━━━━━━━━━━━━━━
✅ Candidate Entry: PASS
✅ Token Panel: PASS (2 warnings)
🔄 Wallet Roles: running...
⬜ Wallet Structure
⬜ Evidence Chain
⬜ Trade Gate
```

### 完成

```
📊 {symbol} Analysis Complete
━━━━━━━━━━━━━━━━━━
📋 Gate Decision: {gate_decision}
📈 Gate Score: {total_score}/100
🎯 Confidence: {confidence_score}

🔑 Key Findings:
• {narrative.one_line}
• SM: {sm_count} wallets, {sm_direction}
• Structure Risk: {structure_risk_level}
• Security: {overall_risk}

⚠️ Risk Factors:
{risk_factors list}

✅ Positive Signals:
{positive_signals list}

📎 Full report: workflow_summary.md
Next: {next_action}
```

### BLOCK

```
🚫 {symbol} BLOCKED
━━━━━━━━━━━━━━━━━━
Blocked at: {blocker_phase}
Reason: {blocker_reasons}

{blocker_report excerpt}
```

## workflow_summary.md 模板

```markdown
# Workflow Summary: {symbol}

**Token:** {token_address}
**Chain:** SOL
**Analyzed at:** {timestamp}
**Gate Decision:** {gate_decision}
**Gate Score:** {total_score}/100
**Confidence:** {confidence_score}

---

## Token Panel Summary
{token_panel.md 的精简版}

## Wallet Roles Summary
- Smart Money: {count}, {direction}
- Dev: {status}
- Top 5 Key Wallets: {table}

## Structure Summary
- Same-source groups: {count}
- Coordinated buys: {count}
- Concentration: {level}
- Structure Risk: {level}

## Evidence Chain
**Dominant Behavior:** {dominant_behavior}
**Narrative:** {paragraph}

### Evidence
{evidence list}

### Counter Evidence
{counter_evidence list}

### Risk Factors
{risk_factors list}

## Gate Decision
**Decision:** {gate_decision}
**Score Breakdown:**
- Security: {security_score}/30
- Smart Money: {smart_money_score}/30
- Structure: {structure_score}/20
- Behavior: {behavior_score}/20

### Triggered Rules
{decision_reasons table}

### Next Review Conditions
{next_review_conditions list}

---

## Warnings & Downgrades
{all downgrade_reasons from all skills}

## Missing Data
{all missing_fields from all skills}
```

## 错误处理

| 错误类型 | 处理 |
|----------|------|
| GMGN API 超时 | 重试 1 次，再失败则 NEED_MORE_DATA |
| GMGN API 返回空 | 记录 missing_field，降级继续 |
| JSON 解析失败 | ERROR + blocker_report |
| 前置 skill 文件不存在 | 从缺失处重跑 |
| 磁盘写入失败 | ERROR + blocker_report |

## 并发控制

Phase 1 不支持并发。同一时间只能分析一个 token。
active_runs.json 记录当前进行中的任务，新请求排队或拒绝。

## 禁止事项

```
禁止：controller 做业务判断
禁止：controller 修改 skill 输出
禁止：跳过 phase 执行
禁止：在 BLOCK 状态继续执行下游 skill
禁止：调用任何交易 API
```
