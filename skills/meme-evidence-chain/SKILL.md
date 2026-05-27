---
name: meme-evidence-chain
description: |
  Skill 05 — Solana meme token 证据链合成。聚合 token-panel + wallet-roles +
  wallet-structure 三方输出，做行为推断（infer_behavior），生成带权重的 signals、
  positive/risk factors、narrative 单行叙述、置信度评分。受 acceptance gate
  约束：必须保留冲突证据，不得过度声称。
  Trigger: token-panel + wallet-roles + wallet-structure 全部完成；workflow
  controller 的第五步；需要给一个 token 出一份「证据链报告」。
---

# meme-evidence-chain

## 作用

整条 workflow 的「证据合成层」。它本身不调用 GMGN，只读前 3 个 skill 的输出，
做行为推断和置信度计算，产出下游 trade-gate 直接消费的标准证据 + 叙事。

## 触发场景

- token-panel + wallet-roles + wallet-structure 都已写出 JSON
- workflow controller 第五步自动调度
- 单独想看某 token 的证据链合成结果

## 输入

- `token_address: str`
- `chain: str = "sol"`
- 上游必读：
  - `data/runs/<token>/token_panel.json`
  - `data/runs/<token>/wallet_roles.json`
  - `data/runs/<token>/wallet_structure.json`

## 处理流程

1. 从 run 目录读 3 个上游 JSON
2. `infer_behavior(token_panel, wallet_roles, wallet_structure)` 做跨源行为推断
3. 用 `sig(behavior, weight, reason, source_skill, source_field)` 生成带溯源的 signal
4. `calculate_confidence(signals, downgrade_count, missing_count)` 计算置信度
5. 区分 `positive_signals` 与 `risk_factors`
6. 生成 `narrative.one_line` 单行叙事
7. 保留 `counter_evidence` 冲突证据
8. 落盘 `evidence_chain.json` + `evidence_chain.md`

## 输出

- 文件：`data/runs/<token>/evidence_chain.json` + `evidence_chain.md`
- 关键字段：`signals`、`positive_signals`、`risk_factors`、`counter_evidence`、
  `narrative`、`confidence_score`、`missing_fields`、`downgrade_reasons`
- 返回 dict

## 依赖

- `common.file_io` / `common.validators`
- **不**直接调用 GMGN（只读上游 JSON）
- 上游强依赖：token_panel / wallet_roles / wallet_structure 三方 JSON 必须存在

## 不做什么

- **不**抛弃冲突证据（acceptance gate 强制约束：必须保留 counter_evidence）
- **不**过度声称（不能输出「确定」「一定」「庄家」「内幕」类语言）
- 不做最终交易裁决（Skill 06）
- 不调用 GMGN
- 不在骨架模式下被真实调用

## 使用方式

```bash
python3 skills/meme-evidence-chain/scripts/run.py <token_address>

# 推荐：由 controller 调度（确保上游 JSON 已生成）
python3 skills/meme-workflow-controller/scripts/run.py run <token_address>
```

## 安全边界

Phase 1 paper-only。本 skill 不接外部数据源，不做交易动作。
