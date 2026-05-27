# SOL 工作流项目梳理 — ai-pro-dev-workflow 控制面

日期：2026-05-26
项目根目录：`/root/sikk-gmgn/`
状态口径：PM/Docs 梳理，不宣称 HUMAN_ACCEPTED / PRODUCTION_READY / LIVE_READY。

## 1. 当前项目定位

当前项目不是自动交易系统，而是：

> GMGN-entry + wallet-intel + Hermes-stateful 的 Solana meme 研究 / 交易决策审计工作流。

Phase 1 边界：research pipeline / paper-only gate；禁止 live trading、swap、private key、signing、broadcast、auto deploy。

## 2. 已固定的控制面

已存在并读取确认：

- `AGENTS.md`：角色边界、3-terminal 准备模式、No task card no coding、安全禁区。
- `CONTEXT.md`：只做 glossary，不承载进度或验收。
- `docs/specs.md`：Phase 1 scope、runtime layout、standard skill output contract、phase order、AI development requirements。
- `docs/acceptance.md`：global gates、skill contract gates、test gates、safety gates、human acceptance gate。
- `docs/freeze_record.md`：`sol-ai-pro-dev-workflow-freeze-20260525-001`，状态为 `FROZEN_FOR_TASK_CARD_EXECUTION`。
- `tasks/task_tree.md`：当前任务树和 blocked CR 分支。
- `reports/review.md`：PM review 已记录 INTERNAL_PASS 批次。
- `reports/final_acceptance.md`：仍为 `HUMAN_ACCEPTANCE_PENDING`。

## 3. 当前实现链路

冻结文档定义的 Phase Order：

```text
meme-candidate-entry
→ meme-token-panel
→ meme-wallet-roles
→ meme-wallet-structure
→ meme-evidence-chain
→ meme-trade-gate
```

`meme-workflow-controller` 负责 orchestration 和 phase state。

标准 skill output contract 必须包含：

```text
schema_version
skill_name
task_id
token_address
chain
timestamp
status
evidence
counter_evidence
confidence_score
downgrade_reasons
blocker_reasons
missing_fields
valid_until
next_action
handoff_to
```

## 4. 当前任务状态快照

从 `tasks/**.md` 扫描到：

### READY 类卡片

- `TASK-BE-001` 到 `TASK-BE-005`
- `TASK-CI-001`
- `TASK-CONTRACT-001`
- `TASK-DATA-001`
- `TASK-DOC-001`
- `TASK-FIXTURE-001`
- `TASK-FIXTURE-002`
- `TASK-QA-001`
- `TASK-QA-002`
- `TASK-RULE-001` 到 `TASK-RULE-004`
- `TASK-SCHEMA-001`
- `TASK-SCHEMA-002`
- `TASK-STATE-001`

这些已有多个 result report，并在 review 中形成 INTERNAL_PASS 记录。

### BLOCKED 类卡片

Five-Forces Entry / CR-2026-05-25-002 分支仍阻塞，等待人类批准：

- `TASK-DOC-002`
- `TASK-RULE-005`
- `TASK-SCHEMA-003`
- `TASK-BE-006`
- `TASK-BE-007`
- `TASK-FIXTURE-003`
- `TASK-QA-003`

因此不能把 Five-Forces Gate 当作已实现主链路能力。

## 5. 验证结果

本轮在 `/root/sikk-gmgn/` 执行：

```bash
pytest -q
```

结果：

```text
Pytest: 34 passed
```

这说明当前已纳入测试的 Phase 1 基线是绿的；但不能等同于 HUMAN_ACCEPTED，也不能等同于 live / production readiness。

## 6. 当前最重要的系统判断

当前已经不再是纯设计阶段，已经进入：

```text
冻结文档
→ task cards
→ backend/fixture/rule/schema/state patches
→ pytest green
→ PM INTERNAL_PASS
→ HUMAN_ACCEPTANCE_PENDING
```

也就是说，项目当前是：

> Phase 1 controlled implementation baseline green, PM internal pass recorded, human final acceptance pending, CR-2026-05-25-002 blocked.

## 7. 下一轮梳理重点

不建议直接扩大到 Phase 2 / paper trading。下一轮应该先处理两个方向之一：

### A. 验收闭环方向

目标：把当前 Phase 1 green baseline 整理成可交付验收包。

输出：

- 更新 `reports/final_acceptance.md` 的验收清单，但保持 `HUMAN_ACCEPTANCE_PENDING`。
- 补一份 `reports/phase1_internal_acceptance_packet.md`。
- 汇总：scope、completed tasks、test evidence、safety evidence、known blocked CR、human decision required。

### B. CR-2026-05-25-002 解锁方向

目标：如果人类明确批准 Five-Forces Entry，则创建 freeze record 002，然后开放 blocked task cards。

顺序必须是：

```text
human approval
→ TASK-DOC-002
→ new freeze record 002
→ TASK-RULE-005 / TASK-SCHEMA-003
→ TASK-BE-006 / TASK-BE-007
→ TASK-FIXTURE-003 / TASK-QA-003
→ pytest
→ PM review
```

未批准前，不执行这些 blocked cards。

## 8. 当前禁止事项

仍然禁止：

- live trading
- swap
- private key access
- wallet signing
- transaction broadcast
- `gmgn-cli swap`
- `gmgn-cli multi-swap`
- `gmgn-cli cooking create`
- auto deploy
- 宣称 `HUMAN_ACCEPTED`
- 宣称 `PRODUCTION_READY`
- 宣称 `LIVE_TRADING_READY`
- 把 GMGN candidate 当买入信号
- 把 PAPER_ONLY 当真实执行许可

## 9. 推荐下一步

推荐下一步走 A：先产出 Phase 1 internal acceptance packet。

原因：

- 当前 pytest 已 green。
- PM review 已有 INTERNAL_PASS。
- final acceptance 仍 pending。
- blocked CR 分支未获人类批准，不应绕过。

最小下一步任务：

```text
创建 reports/phase1_internal_acceptance_packet.md
内容包括：scope、evidence、task batch、test result、safety review、blocked items、human decision checklist。
```

验收口径：

```text
INTERNAL_ACCEPTANCE_PACKET_READY
HUMAN_ACCEPTANCE_PENDING
NO_LIVE_EXECUTION_AUTHORIZED
```
