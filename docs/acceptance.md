# Acceptance Criteria — Solana Meme Workflow OS

## Global Acceptance Gates
- [ ] `AGENTS.md` defines role boundaries and safety rules.
- [ ] `docs/ai_dev_workflow.md` defines the development workflow protocol.
- [ ] `CONTEXT.md` is glossary-only.
- [ ] `docs/specs.md` and `docs/acceptance.md` exist before execution tasks.
- [ ] `docs/freeze_record.md` records frozen inputs.
- [ ] `tasks/task_tree.md` and task cards exist before Backend/QA coding.
- [ ] Every execution task writes `reports/<task_id>/result.md`.

## Skill Contract Gates
- [ ] Each skill emits standard handoff fields: schema_version, skill_name, task_id, token_address, chain, timestamp, status, evidence, counter_evidence, confidence_score, downgrade_reasons, blocker_reasons, missing_fields, valid_until, next_action, handoff_to.
- [ ] `meme-token-panel` emits token/security/risk fields required by downstream skills.
- [ ] `meme-wallet-roles` does not treat GMGN labels as final role classification without behavior-rule basis.
- [ ] `meme-wallet-structure` excludes pool/exchange addresses from holder concentration when applicable.
- [ ] `meme-evidence-chain` preserves conflicting evidence and does not overclaim.
- [ ] `meme-trade-gate` emits `gate_decision` and respects Phase 1 allowed decisions.
- [ ] `meme-workflow-controller` supports run/status/list with phase-state persistence.

- [ ] `meme-candidate-entry` emits `entry_stage`, `basis`, `basic_gate`, `five_forces`, `gmgn_risk_density`, `entry_aux_decision`, and `next_action` fields per the Five-Forces Gate Contract.
- [ ] `meme-candidate-entry.basis` 字段值固定为 `gmgn_field_combination_hint`。
- [ ] `meme-candidate-entry` loads thresholds from `rules/entry_five_forces_rules_v1.json`.
- [ ] `meme-workflow-controller` honors `basic_gate.decision == FILTERED_OUT` by skipping S02-S06 in batch mode and recording the skipped count.

## Test Gates
- [ ] `pytest -q` passes, or every failure has an explicit task card and attribution.
- [ ] Fixtures cover BLOCK / WATCH / PAPER_ONLY / NEED_MORE_DATA.
- [ ] At least one fixture covers downgrade behavior.
- [ ] At least one fixture covers missing fields.
- [ ] Tests do not require live trading or wallet operations.

- [ ] Fixtures 至少覆盖五种入口决策：`PASS` / `CAUTION` / `SKIP` / `FILTERED_OUT` / `UNKNOWN`。
- [ ] Fixture 至少覆盖：缺 `liquidity` 字段、缺 `market_cap` 字段、`is_wash_trading=true`、`bundler_rate` 过高、`top_10_holder_rate` 过高、权限未放弃六种场景。
- [ ] Test 覆盖：单 token `run` 与批量 `screen` 在 `entry_aux_decision == SKIP` 时的差异行为。

## Safety Gates
- [ ] No task invokes real order placement.
- [ ] No task accesses private keys.
- [ ] No task signs transactions.
- [ ] No task broadcasts transactions.
- [ ] No task calls `gmgn-cli swap`, `gmgn-cli multi-swap`, or `gmgn-cli cooking create`.
- [ ] No output claims certainty about insider activity or guaranteed price movement.

## Human Acceptance Gate
- [ ] PM/review may mark `INTERNAL_PASS` only.
- [ ] Final status remains `HUMAN_ACCEPTANCE_PENDING` until the human explicitly accepts or rejects.

## Walking Skeleton Acceptance Gates
依据：`docs/freeze_record.md` freeze 003（Walking Skeleton freeze，grill 问题 3 → 选项 B 鲁棒骨架完成）。
所有 10 条必须同时通过，缺一不可。任意一条未通过不得宣称骨架完成，不得进入真实数据接入阶段，不得解锁已暂停的 Five-Forces 任务。

### Happy Path
- [ ] WS-1 `--skeleton` 端到端 7 phase → `workflow_status=COMPLETED`
- [ ] WS-2 `--from <phase> --skeleton` 从任意 phase 续跑能到 COMPLETED；phase_state.json 的 `completed_phases` 链条正确
- [ ] WS-3 状态机 6 状态（PASS / BLOCK / ERROR / COMPLETED / BLOCKED / SKIPPED）在 phase_state.json 至少各被写入一次
- [ ] WS-4 骨架产物全部落在 `data/runs/_skeleton_/<token>/`；骨架测试期间 `data/runs/<token>/` 零新增
- [ ] WS-5 `pytest skills/ -q` 全绿，无 SKIP / XFAIL 掩盖

### 容错矩阵
- [ ] WS-6 任意 phase 抛异常 → controller 捕获 → `workflow_status=ERROR` + `blocked_at` + `blocker_reasons` 包含异常信息；下游 phase 不执行；下游 JSON 不写入
- [ ] WS-7 任意 phase 输出 schema 不合规 → BLOCK + `missing_fields` / `schema_violations`；状态机停在该 phase
- [ ] WS-8 模拟 phase 超时 → TIMEOUT 状态正确写入 phase_state.json，与 ERROR / BLOCK 可区分
- [ ] WS-9 `screen --skeleton`（或等价命令）能用骨架 mock 跑 ≥ 5 个 token；批次报告正确生成在 `data/runs/_skeleton_/batches/<batch_id>/`
- [ ] WS-10 跑到一半人工 kill controller → 重启 `--skeleton --from <next_phase>` 能续跑完成；已完成 phase 不重复执行

### 验收交付物
- [ ] `reports/walking_skeleton_acceptance/result.md` 按 WS-1~WS-10 逐条出据（命令 + 输出片段 + 文件路径 + pass/fail）
- [ ] PM/review 才能标 `INTERNAL_PASS`；人类显式批准后才能解锁 Five-Forces 任务和真实数据接入

### 明确不验收
- 任何 mock 数据的真实性或业务合理性
- 任何 phase 输出的判断准确性
- 跨 skill 真实字段依赖关系
- Five-Forces Gate 逻辑
- 真实 GMGN 接口调用
