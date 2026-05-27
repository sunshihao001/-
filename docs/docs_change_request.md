# Docs Change Requests

---

## CR-2026-05-25-002 — GMGN 字段组合五力模型 落地到 S01 候选入口

change_id: CR-2026-05-25-002
status: DRAFT
proposed_by: PM/Docs
proposed_at: 2026-05-25T08:55:00Z

## Requested Change

把 `learning/GMGN字段组合五力模型理论总结.txt` 中的研究结论，正式落地到 `meme-candidate-entry` (S01) 的入口契约里。

需要修改的 frozen docs：

- `docs/specs.md`
  - 在 `Standard Skill Output Contract` 之后新增一节 `S01 Candidate Entry Five-Forces Gate Contract`。
  - 在 `Engineering Requirements` 中追加一条：S01 必须输出 `five_forces`、`basic_gate`、`gmgn_risk_density`、`entry_aux_decision` 五个新字段，且 `basis` 字段值固定为 `gmgn_field_combination_hint`。
  - 在 `Excluded` 中明确：`SKIP / FILTERED_OUT / CAUTION` 仅为入口辅助，不替代 S06 的 `BLOCK / WATCH / PAPER_ONLY / NEED_MORE_DATA`。
- `docs/acceptance.md`
  - 在 `Skill Contract Gates` 中追加 S01 五力字段验收项。
  - 在 `Test Gates` 中追加：fixtures 至少覆盖 `PASS / CAUTION / SKIP / FILTERED_OUT / UNKNOWN` 五种入口决策。
- `CONTEXT.md`
  - 在 `Skill Terms` 增加术语：`Five-Forces Gate`、`Absorption Power`、`Diffusion Power`、`Control Power`、`Camouflage Power`、`Exit Power`、`Entry Aux Decision`、`GMGN Risk Density`。

## Reason

1. 当前 S01 仅做地址校验和最小 token info 解析，无法把研究中已经收敛的「五力 + 三段筛选」用作入口辅助。
2. 真实 trending 批量结果显示 7/10 决策为 `NEED_MORE_DATA`，说明完整工作流被「不值得深筛」的候选稀释。
3. 用户原文要求：「现在的话，需要把字段组合的理论知识从研究走向 sol 工作流中的应用场景需要的准备来。使用 ai-pro-dev-workflow。」
4. 把研究产物固化进 spec，才能进入 task card 执行环节，避免「从聊天里写代码」。

## Impacted Frozen Docs

- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`

## Out of Scope (本次变更不动)

- `data/runs/` 历史产物
- `meme-trade-gate` 决策枚举
- `meme-workflow-controller` 阶段顺序
- 任何 live trading / swap / signing / broadcast 能力
- `SEMI_AUTO_READY` / `AUTO_READY` 升级

## Approval

- [ ] PM/review approve
- [ ] Human approve (required before new freeze record)

待人类批准后，PM/Docs 会写入 `docs/freeze_record.md` 的下一条记录 `sol-ai-pro-dev-workflow-freeze-20260525-002`。

---
