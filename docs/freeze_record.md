# Freeze Record

freeze_id: sol-ai-pro-dev-workflow-freeze-20260525-001
frozen_at: 2026-05-25T05:53:33.555877+00:00
status: FROZEN_FOR_TASK_CARD_EXECUTION
scope: Phase 1 research pipeline + AI pro development workflow control plane preparation

## Frozen Inputs
- `CONTEXT.md`
- `docs/specs.md`
- `docs/acceptance.md`

## Source Materials Used
- `design/README.md`
- `design/phase0-workflow-contract.md`
- `design/phase1-skill-01-candidate-entry.md`
- `design/phase1-skill-02-token-panel.md`
- `design/phase1-skill-03-wallet-roles.md`
- `design/phase1-skill-04-wallet-structure.md`
- `design/phase1-skill-05-evidence-chain.md`
- `design/phase1-skill-06-trade-gate.md`
- `design/phase1-skill-07-workflow-controller.md`
- `design/工程完善计划书.md`

## Change Rule
After this record, no execution terminal may directly modify:
- `CONTEXT.md`
- `docs/specs.md`
- `docs/acceptance.md`

Changes require PM/review approval and a new freeze record.

## Safety Boundary
This freeze does not authorize live trading, wallet signing, transaction broadcast, auto deploy, or production-ready claims.

---

# Freeze Record

freeze_id: sol-ai-pro-dev-workflow-freeze-20260525-002
frozen_at: 2026-05-26T03:45:32Z
status: FROZEN_FOR_TASK_CARD_EXECUTION
scope: CR-2026-05-25-002 — GMGN Five-Forces Gate landing on S01

## Frozen Inputs

- `CONTEXT.md`
- `docs/specs.md`
- `docs/acceptance.md`

## Change Origin

- `docs/docs_change_request.md` → CR-2026-05-25-002
- Telegram human approval in current session: user explicitly requested `TASK-DOC-002 → 更新 docs/specs.md / docs/acceptance.md / CONTEXT.md → 写 freeze record 002 → 写 reports/TASK-DOC-002/result.md → 然后才能解锁 TASK-RULE-005 / TASK-SCHEMA-003 / TASK-BE-006...`

## Source Materials

- `learning/GMGN字段组合五力模型理论总结.txt`
- `learning/15-GMGN字段组合地基.md`
- `design/phase1-research/00-GMGN-字节组合-总结.md`
- `design/phase1-research/gmgn-byte-combination-reasoning-v0.1.md`
- `design/phase1-research/00b-GMGN-Canonical-Bytes.txt`
- `design/phase1-research/00b-GMGN-Canonical-Bytes.md`
- `reports/cr_20260525_002_canonical_bytes_evidence_addendum.md`

## Safety Boundary

Phase 1 safe-mode unchanged. No live trading / signing / broadcast / swap / auto deploy.


---

# Freeze Record

freeze_id: sol-ai-pro-dev-workflow-freeze-20260526-003
frozen_at: 2026-05-26T09:33:00Z
status: WALKING_SKELETON_FROZEN
scope: Phase 1 系统目标重定义为 Walking Skeleton

## 触发来源

- Telegram 用户在 grill-with-docs 流程中明确选择 grill 问题 1 选项 ③（Walking Skeleton 路线）
- 用户上传文档：`定义清楚才能做好系统.md`，确立 V1→V4 分层目标模型
- 用户三件事确认：freeze 003=是 / 目录隔离=是 / mock 策略=c（controller `--skeleton`）

## 冻结内容

### 当前系统目标

Phase 1 系统目标 = **Walking Skeleton**：
- 输出：能从入口到报告端到端自动跑通的 mock 流水线
- 验收：mock 数据跑通 7 个 phase + 状态机正确落盘 + 容错正常 + 断点续跑

### 当前阶段非目标（禁止讨论 / 禁止实装）

- 真实判断逻辑准确性
- entry/exit/size/take-profit/stop-loss 字段
- 真实交易动作 / 签名 / 广播
- auto-execution / semi-auto 接口预留
- 「能不能赚钱」「胜率多少」类问题
- 实盘 / live trading / production-ready 任何形式的声明

### 已存在的 Five-Forces 任务处理

以下任务**暂停（PAUSE），不删除**，等 Walking Skeleton 阶段验收通过后再决定是否继续：
- `TASK-SCHEMA-003` — Five-Forces Gate schema 扩展
- `TASK-BE-006` — Five-Forces Gate 逻辑实装
- `TASK-BE-007` — controller 处理 `basic_gate=FILTERED_OUT` / `entry_aux_decision=SKIP`
- `TASK-FIXTURE-003` — entry decisions fixtures
- `TASK-QA-003` — Five-Forces Gate + controller skip pytest

理由：这些任务属于「真实判断层」，不属于「骨架层」。在骨架未稳定前实装会导致两个方向同时跑，互相污染。

### 工程改造（本次落地）

- `skills/common/file_io.py` — `get_run_dir` 在 `SIKK_SKELETON_MODE=1` 时写到 `data/runs/_skeleton_/<token>/`
- `skills/meme-workflow-controller/scripts/run.py` — 新增 `SKELETON_MOCKS` / `_run_phase_skeleton` / `is_skeleton_mode` / `--skeleton` CLI flag
- 不改任何 7 个 skill 的内部逻辑（保持已有冻结）
- 不改 `docs/specs.md` / `docs/acceptance.md` / `CONTEXT.md`

### 使用方式

骨架模式端到端运行：
```bash
python3 skills/meme-workflow-controller/scripts/run.py run <token_address> --skeleton
```

骨架产物隔离在 `data/runs/_skeleton_/<token>/`，与正式 runs 物理分离。

## 退出条件

Walking Skeleton 阶段验收通过的标准（grill 问题 3 → 选项 B：鲁棒骨架完成）。
**所有 10 条必须同时满足**，缺一不可。任意一条未通过不得宣称骨架完成，不得进入下一阶段（真实数据接入 / Five-Forces 解锁）。

### 第一层：Happy Path（5 条）

1. **端到端跑通**：`--skeleton` 端到端跑通 7 个 phase（candidate_entry → token_panel → wallet_roles → wallet_structure → evidence_chain → trade_gate → workflow_summary），`workflow_status = COMPLETED`
2. **断点续跑**：从任意 phase 用 `--from <phase> --skeleton` 续跑能跑到 COMPLETED，phase_state.json 中 `completed_phases` 链条正确
3. **状态机 6 状态全可写入**：PASS / BLOCK / ERROR / COMPLETED / BLOCKED / SKIPPED 在 phase_state.json 至少各被写入一次（可由测试 fixture 驱动）
4. **目录隔离**：所有骨架产物落在 `data/runs/_skeleton_/<token>/`，正式 `data/runs/<token>/` 在骨架测试期间零新增
5. **pytest 全绿**：`pytest skills/ -q` 全通过，无 SKIP / XFAIL 掩盖

### 第二层：容错矩阵（5 条）

6. **异常容错**：任意 phase 抛 Python 异常 → controller 捕获 → 写入 `workflow_status=ERROR` + `blocked_at=<phase>` + `blocker_reasons` 包含异常信息 → 下游 phase 不再执行 → 不污染下游 JSON 文件
7. **Schema 容错**：任意 phase 输出格式不符合 schema → controller 标记为 BLOCK + 写入 `missing_fields` 或 `schema_violations` → 状态机停在该 phase
8. **超时容错**：模拟某 phase 超时 → TIMEOUT 状态正确写入 phase_state.json，与 ERROR / BLOCK 可区分
9. **批量模式骨架可跑**：`screen --skeleton`（或等价命令）能用骨架 mock 跑 ≥ 5 个 token，批次报告（筛选结果.json + 筛选报告.md）正确生成在 `data/runs/_skeleton_/batches/<batch_id>/`
10. **崩溃恢复**：在某 phase 跑到一半人工 kill controller 进程 → 重启 `--skeleton --from <last_completed_phase + 1>` → 能从 phase_state 续跑完成，不重复执行已完成 phase

### 验收方式

- 每条退出条件必须有对应的 pytest 用例或可重放的脚本验证
- 在 `reports/walking_skeleton_acceptance/result.md` 中按 10 条逐条出据（命令 + 输出 + 文件路径）
- PM/review 才能标记 `INTERNAL_PASS`；人类显式批准后才能解锁下一阶段

### 不在本阶段验收范围（明确排除）

- 任何 mock 数据的「真实性」或「合理性」
- 任何 phase 输出的判断准确性
- 6 个 skill 之间的真实业务字段依赖关系
- Five-Forces Gate 的任何逻辑
- 真实 GMGN 接口调用

## Safety Boundary

Phase 1 safe-mode 不变。No live trading / signing / broadcast / swap / auto deploy.

---

# Freeze Record

freeze_id: sol-ai-pro-dev-workflow-freeze-20260527-004
frozen_at: 2026-05-27T00:00:00Z
status: FROZEN_FOR_COGNITION_UPGRADE
scope: v2 cognition upgrade freeze — CONTEXT.md + docs/acceptance.md v2 terms/checks

## Frozen Inputs

- `CONTEXT.md`
- `docs/acceptance.md`
- `docs/freeze_record.md`

## Source Materials

- `CONTEXT.freeze_candidate.md`
- `docs/acceptance.freeze_candidate.md`
- `design/v2工作流总纲.md`
- `design/v2迁移说明.md`
- `reports/V2-CONTENT-CANDIDATE-001/review.md`

## Changes Applied

- `CONTEXT.md`: appended v2 System/Skill/State/Gate/Evidence/Safety terms
- `docs/acceptance.md`: appended v2 Architecture/Skill Boundary/Artifact/Evidence/Gate/Controller/Legacy/Safety acceptance groups

## Safety Boundary

Phase 1 safe-mode unchanged. No live trading / signing / broadcast / swap / auto deploy. v2 cognition upgrade does not authorize production readiness.

