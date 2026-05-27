# Phase 0: Solana Meme Workflow Contract

## 系统定位

GMGN-entry + wallet-intel + Hermes-stateful Solana meme trading workflow OS。

## 目录结构

```
/root/sikk-gmgn/
├── design/                          # 设计文档
├── skills/                          # Hermes skills 源码
│   ├── meme-candidate-entry/
│   ├── meme-token-panel/
│   ├── meme-wallet-roles/
│   ├── meme-wallet-structure/
│   ├── meme-evidence-chain/
│   ├── meme-trade-gate/
│   └── meme-workflow-controller/
├── data/                            # 运行时数据
│   └── runs/
│       └── <token_address>/         # 每个 token 一个目录
│           ├── candidate_entry.json
│           ├── token_panel.json
│           ├── token_panel.md
│           ├── wallet_roles.json
│           ├── wallet_structure.json
│           ├── evidence_chain.json
│           ├── evidence_chain.md
│           ├── trade_gate.json
│           ├── phase_state.json
│           ├── blocker_report.md
│           └── workflow_summary.md
├── state/                           # 全局状态
│   ├── active_runs.json             # 当前进行中的 token 分析
│   └── completed_runs.json          # 已完成的分析索引
├── rules/                           # 门控规则（可版本化）
│   ├── gate_rules_v1.json
│   └── downgrade_rules_v1.json
└── library/                         # 经验库（Phase 2+）
    ├── failure_cases/
    └── signal_effectiveness/
```

## 标准 Handoff Schema

所有 skill 输出必须包含以下公共字段：

```json
{
  "schema_version": "1.0",
  "skill_name": "meme-xxx",
  "task_id": "<token_address>_<timestamp>",
  "token_address": "<base58 address>",
  "chain": "sol",
  "timestamp": "<ISO 8601>",
  "status": "PASS | WARN | BLOCK | ERROR | NEED_MORE_DATA",
  "evidence": [
    {
      "claim": "<判断内容>",
      "source": "<数据来源命令>",
      "value": "<具体值>",
      "weight": "high | medium | low"
    }
  ],
  "counter_evidence": [
    {
      "claim": "<反面证据>",
      "source": "<数据来源>",
      "value": "<具体值>"
    }
  ],
  "confidence_score": 0.0,
  "downgrade_reasons": [],
  "blocker_reasons": [],
  "missing_fields": [],
  "valid_until": "<ISO 8601, 默认 30 分钟>",
  "next_action": "<下一步 skill 名或 STOP>",
  "handoff_to": "<下一个 skill>"
}
```

## Phase State Schema

每个 token 分析任务的状态文件：

```json
{
  "task_id": "<token_address>_<timestamp>",
  "token_address": "<address>",
  "chain": "sol",
  "created_at": "<ISO 8601>",
  "updated_at": "<ISO 8601>",
  "current_phase": "candidate_entry | token_panel | wallet_roles | wallet_structure | evidence_chain | trade_gate | COMPLETED | BLOCKED | ERROR",
  "completed_phases": [
    {
      "phase": "candidate_entry",
      "status": "PASS",
      "completed_at": "<ISO 8601>",
      "output_file": "candidate_entry.json"
    }
  ],
  "blocked_at": null,
  "blocker_phase": null,
  "blocker_reasons": [],
  "gate_decision": null,
  "resume_from": null
}
```

## Status 枚举

| Status | 含义 | 后续动作 |
|--------|------|----------|
| `PASS` | 通过，进入下一步 | handoff_to 下一个 skill |
| `WARN` | 有警告但可继续 | 记录 downgrade_reasons，继续 |
| `BLOCK` | 阻塞，不允许继续 | 写 blocker_report，停止 |
| `ERROR` | 执行错误 | 写 blocker_report，可重试 |
| `NEED_MORE_DATA` | 数据不足 | 记录 missing_fields，降级或停止 |

## Gate Decision 枚举

| Decision | 含义 | 当前阶段允许 |
|----------|------|-------------|
| `BLOCK` | 禁止继续 | ✅ |
| `WATCH` | 观察，不操作 | ✅ |
| `PAPER_ONLY` | 仅允许纸面交易 | ✅ |
| `NEED_MORE_DATA` | 数据不足 | ✅ |
| `SEMI_AUTO_READY` | 半自动就绪 | ❌ Phase 4 |
| `AUTO_READY` | 全自动就绪 | ❌ Phase 5 |

## 禁止事项（Phase 1）

```
禁止：真实下单、私钥签名、交易广播
禁止：调用 gmgn-cli swap / multi-swap / cooking create
禁止：输出"确定庄家"、"确定内幕"、"一定会涨"
禁止：跳过 gate 直接进入 paper 或执行
禁止：在 research 阶段触发任何资金操作
```

## 数据过期规则

| 数据类型 | 默认有效期 | 过期后动作 |
|----------|-----------|-----------|
| token_panel | 30 分钟 | 重新采集 |
| wallet_roles | 60 分钟 | 重新采集 |
| wallet_structure | 60 分钟 | 重新采集 |
| evidence_chain | 30 分钟 | 重新生成 |
| trade_gate | 15 分钟 | 重新判断 |

## Skill 执行顺序

```
meme-candidate-entry
→ meme-token-panel
→ meme-wallet-roles
→ meme-wallet-structure
→ meme-evidence-chain
→ meme-trade-gate
```

由 `meme-workflow-controller` 负责串联和状态管理。
