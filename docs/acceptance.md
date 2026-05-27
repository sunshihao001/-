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

---

## v2 认知升级验收条款（V2-FREEZE-001 freeze）

依据：`docs/acceptance.freeze_candidate.md`，PM/review INTERNAL_PASS

### 验收范围

本组验收：v2 总体结构、10 个业务 Skill 边界、workflow-controller 边界、artifact/evidence/gate/state 规则、legacy 前置层对齐、安全边界。
本组不验收：代码实现、真实 API 接入、真实交易、私钥/签名/swap/broadcast、生产可用性。

### A. Architecture

- [ ] A1. v2 declares exactly 10 business skills and 1 workflow-controller.
- [ ] A2. workflow-controller is not counted as a business skill.
- [ ] A3. each business skill has a unique responsibility.
- [ ] A4. each business skill has upstream inputs and downstream consumers.
- [ ] A5. v2 declares paper-only research as the current boundary.
- [ ] A6. v2 declares PAPER_ONLY as the current highest allowed state.

### B. Business Skill Boundary

For each business skill:
- [ ] B1. one-sentence responsibility exists.
- [ ] B2. upstream inputs are listed.
- [ ] B3. stable outputs are listed.
- [ ] B4. failure modes are listed.
- [ ] B5. downstream consumers are listed.
- [ ] B6. forbidden outputs/actions are listed.
- [ ] B7. raw data access policy is listed.
- [ ] B8. judgment permission is listed.
- [ ] B9. gate permission is listed.
- [ ] B10. minimum handoff fields are listed.

### C. Artifact

- [ ] C1. each artifact has a producer skill.
- [ ] C2. each artifact has at least one consumer or archive purpose.
- [ ] C3. each artifact has status.
- [ ] C4. each artifact has missing_fields or equivalent.
- [ ] C5. each artifact has downgrade_reasons or equivalent.
- [ ] C6. each artifact has valid_until or explicit no-expiry rationale.
- [ ] C7. controller may validate artifact presence and shape.
- [ ] C8. controller must not modify business artifact content.

### D. Evidence

- [ ] D1. supporting_evidence is preserved where a claim exists.
- [ ] D2. counter_evidence is preserved where a claim exists.
- [ ] D3. missing_fields are preserved and never replaced by default values.
- [ ] D4. downgrade_reasons are preserved.
- [ ] D5. source_artifacts or evidence_refs are preserved.
- [ ] D6. GMGN labels are treated as hints, not final classification.
- [ ] D7. deterministic accusation language is forbidden.
- [ ] D8. evidence-chain keeps alternatives and conflicts when unresolved.

### E. Gate

- [ ] E1. candidate-entry owns entry gate only.
- [ ] E2. trade-gate owns positive gate only.
- [ ] E3. negative-gate owns negative gate / veto only.
- [ ] E4. negative-gate may downgrade or block but cannot upgrade.
- [ ] E5. controller must not override negative-gate final_state.
- [ ] E6. trade-gate output must pass through negative-gate before final_state.
- [ ] E7. PAPER_ONLY is not live trading permission.
- [ ] E8. BLOCK must include blocker_reasons or veto_rules_hit.

### F. Controller

- [ ] F1. controller orchestrates skill order.
- [ ] F2. controller records phase_state.
- [ ] F3. controller records gate_sequence.
- [ ] F4. controller records artifact_manifest or equivalent.
- [ ] F5. controller supports resume_point.
- [ ] F6. controller writes blocker_report when blocked.
- [ ] F7. controller writes workflow_summary.
- [ ] F8. controller does not read GMGN raw or chain raw.
- [ ] F9. controller does not produce business conclusions.
- [ ] F10. controller does not patch missing business fields.

### G. Legacy / Front-Layer Alignment

- [ ] G1. candidate-entry, token-panel, and wallet-roles may be treated as natural v1/v2 front-layer alignment points.
- [ ] G2. old front-layer artifacts may be recognized as legacy-compatible.
- [ ] G3. legacy-compatible does not mean v2 schema-compliant.
- [ ] G4. incomplete old downstream designs must not create fake migration debt.
- [ ] G5. structure-evidence, chip-control, evidence-chain, lifecycle-classifier, trade-gate, negative-gate, and paper-validation should be designed directly as v2 components.

### H. Safety

- [ ] H1. live trading is forbidden.
- [ ] H2. private key access is forbidden.
- [ ] H3. wallet signing is forbidden.
- [ ] H4. transaction broadcast is forbidden.
- [ ] H5. gmgn swap / multi-swap / cooking is forbidden.
- [ ] H6. auto deploy is forbidden.
- [ ] H7. production readiness claims are forbidden.
- [ ] H8. "确定庄家", "确定内幕", and "一定会涨" style claims are forbidden.
- [ ] H9. future human acceptance is required before any non-paper boundary change.

### Required Review Questions

1. Does every skill have a clear producer/consumer relationship?
2. Does any skill duplicate another skill's judgment?
3. Does controller accidentally become a business skill?
4. Can final_state be traced through gate_sequence?
5. Can every BLOCK be traced to blocker or veto evidence?
6. Can every NEED_MORE_DATA be traced to missing_fields?
7. Are legacy artifacts clearly separated from v2 standard artifacts?
8. Are all safety prohibitions visible in the candidate docs?

### Acceptance Decision Labels

- `INTERNAL_PASS`: 候选文档达到内部一致性，可交给用户最终确认。
- `PATCH_REQUIRED`: 需要补丁后再评审。
- `BLOCKED`: 关键边界不清，不能 freeze。
- `OUT_OF_SCOPE`: 请求已经越过 paper-only / theory boundary。

Human labels: `HUMAN_ACCEPTED`, `HUMAN_REJECTED`

### 待冻结问题

1. Architecture 是否采用 08.md 的 A1-A6，还是 04.md 的 A1-A7？
2. Artifact 是否采用 08.md 的 C1-C8，还是 04.md 的 C1-C10？
3. Controller 是否采用 08.md 的 F1-F10，还是 04.md 的 F1-F12？
4. acceptance 文档最终语言风格是否继续中文解释 + English terms？
