---
name: meme-trade-gate
description: |
  Skill 06 — Solana meme token 交易门裁决。读取前 5 个 skill 的输出，按打分 +
  复合规则计算 gate_score、gate_decision（PAPER_ONLY / WATCH / BLOCK /
  NEED_MORE_DATA）、next_action。Phase 1 paper-only：不允许输出实盘动作。
  Trigger: evidence-chain 已完成；workflow controller 的第六步（也是最后一个
  判断步）；需要给一个 token 出最终的研究门控决策。
---

# meme-trade-gate

## 作用

整条 workflow 的「最终研究门控」。读取前 5 个 skill 的全部 JSON，输出 Phase 1
唯一允许的 4 种研究门决策：`PAPER_ONLY` / `WATCH` / `BLOCK` / `NEED_MORE_DATA`。
本 skill 的输出**不是交易指令**，是研究流水线的终态标签。

## 触发场景

- evidence-chain 已完成
- workflow controller 第六步自动调度
- 单独想给某 token 出一份门控裁决

## 输入

- `token_address: str`
- `chain: str = "sol"`
- 上游必读：`token_panel.json` / `wallet_roles.json` / `wallet_structure.json` /
  `evidence_chain.json`（candidate_entry 间接依赖）

## 处理流程

1. 从 run 目录读 4-5 个上游 JSON
2. `calculate_gate_score(tp, wr, ws, ev)` 按权重打分
3. `_apply_complex_rules` 应用复合规则（多因子联动触发）
4. `decide(triggered, score, ...)` 综合给出 `gate_decision`
5. 调用 `complete_phase(token, "trade_gate", status)` 推状态机
6. 调用 `set_gate_decision(token, decision)` 写回 phase_state
7. 落盘 `trade_gate.json` + `trade_gate.md`

## 输出

- 文件：`data/runs/<token>/trade_gate.json` + `trade_gate.md`
- 关键字段：`gate_score`、`gate_decision`（PAPER_ONLY/WATCH/BLOCK/NEED_MORE_DATA）、
  `triggered_rules`、`next_action`、`confidence_score`、`reasoning`
- 返回 dict

## 依赖

- `common.file_io` / `common.validators` / `common.phase_state`
- **不**直接调用 GMGN
- 上游强依赖：token_panel / wallet_roles / wallet_structure / evidence_chain

## 不做什么

- **不**输出实盘交易指令（acceptance gate 强制约束：Phase 1 paper-only）
- **不**输出 entry/exit/size/take-profit/stop-loss 字段（freeze 003 边界）
- **不**输出 BUY/SELL/HOLD 等交易动作
- 不调用 GMGN
- 不签名、不广播、不调用 gmgn-cli swap
- 不声称「胜率」「盈利预期」「一定会涨」
- 不在骨架模式下被真实调用

## 使用方式

```bash
python3 skills/meme-trade-gate/scripts/run.py <token_address>

# 推荐：由 controller 调度（确保 5 个上游 JSON 都已生成）
python3 skills/meme-workflow-controller/scripts/run.py run <token_address>
```

## 安全边界

Phase 1 paper-only。`gate_decision` 是研究流水线终态标签，**不是**交易决策。
任何把本 skill 输出当作下单依据的使用方式都违反 acceptance.md 安全门。
