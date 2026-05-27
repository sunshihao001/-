---
name: meme-workflow-controller
description: |
  Skill 07 — Solana meme workflow 总控。按顺序调度 Skill 01-06（candidate-entry →
  token-panel → wallet-roles → wallet-structure → evidence-chain → trade-gate），
  管理 phase_state 状态机，处理 BLOCK/ERROR 短路，写 workflow_summary.json/md，
  维护 active_runs / completed_runs 索引。支持单 token 全流程、断点续跑、状态
  查询、批量筛选、Walking Skeleton mock 模式。
  Trigger: 给定 SOL token 地址，需要跑完整 7-step 研究流水线；批量筛选 GMGN
  候选池；查询某 token 当前状态；骨架模式端到端冒烟。
---

# meme-workflow-controller

## 作用

7-step 研究流水线的总控。它**不做任何业务判断**，只负责：
- 按固定顺序调度 6 个业务 skill
- 维护 phase_state（每 token 一份）
- BLOCK/ERROR 时短路停止，不污染下游
- 聚合 6 个 skill 的输出成 workflow_summary
- 维护 active / completed 索引

## 触发场景

- 单 token 全流程：`run <token>`
- 断点续跑：`run <token> --from <phase>`
- 状态查询：`status <token>`
- 批量筛选：`screen --source trending --limit 10`
- 列出 active/completed：`list`
- 骨架冒烟：`run <token> --skeleton`（freeze 003 路径）

## 子命令

| 命令 | 用途 |
|---|---|
| `run <token>` | 跑完整 7-step 工作流 |
| `run <token> --from <phase>` | 从指定 phase 续跑 |
| `run <token> --force-refresh` | 重置 phase_state 重跑 |
| `run <token> --skeleton` | Walking Skeleton mock 模式（产物隔离在 `_skeleton_/`） |
| `status <token>` | 看某 token 当前 phase / stale / 详情 |
| `screen --source <s>` | 批量调度 GMGN 候选池 |
| `list` | 列出 active_runs / completed_runs |

## 阶段顺序

```
candidate_entry → token_panel → wallet_roles → wallet_structure
                                                   ↓
                              trade_gate ← evidence_chain
```

任意 phase 返回 status=BLOCK 或 ERROR → 停止并写 blocker_report。

## 输出

- 文件：`data/runs/<token>/workflow_summary.json` + `workflow_summary.md`
  （骨架模式下在 `data/runs/_skeleton_/<token>/`）
- BLOCK/ERROR 时额外：`blocker_report.md`
- `state/active_runs.json` / `state/completed_runs.json` 索引
- 关键字段：`workflow_status`（COMPLETED/BLOCKED/ERROR）、`gate_decision`、
  `gate_score`、`confidence_score`、`key_findings`、`risk_factors`、
  `positive_signals`、`next_action`、`forbidden`

## 依赖

- 6 个业务 skill 的 `scripts/run.py`（动态加载，每次清理 `rules` / `schema` 模块避免串包）
- `common.file_io` / `common.validators` / `common.phase_state`

## 不做什么

- **不**做任何业务判断（只编排）
- **不**调用 GMGN（业务 skill 自己调）
- **不**修改 6 个业务 skill 的输出
- 不发起实盘交易 / 签名 / 广播 / swap（freeze 003 强制约束）
- 不预留 entry/exit/size 字段
- 不在骨架模式下调用真实 skill（短路到 `_run_phase_skeleton`）

## 安全边界

Phase 1 paper-only。所有 workflow_summary 必带 `forbidden:
["live_trading","swap","private_key","signing","broadcast"]` 字段。
