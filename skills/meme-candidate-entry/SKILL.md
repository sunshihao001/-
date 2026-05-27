---
name: meme-candidate-entry
description: |
  Skill 01 — Solana meme token 入口候选评估。给定 token 合约地址，调用 GMGN 获取
  token 基本信息 + 池子 + 流动性，做地址格式校验、token 存在性、池子/流动性检查、
  Five-Forces Gate 入口辅助判断，输出 candidate_entry.json，作为后续 6 个 skill
  的统一入口。
  Trigger: 给定 SOL meme token 地址，需要做入口准入判定；批量筛选 GMGN trending /
  trenches / signal 候选池；workflow controller 调度的第一步。
---

# meme-candidate-entry

## 作用

Solana meme workflow 7-step 管线的第一步。负责把「一个 token 地址」转成「带入口
裁决的标准 candidate_entry 记录」，是下游所有 skill 的数据起点。

## 触发场景

- 用户手动给一个 SOL meme token 合约地址要做研究
- workflow controller 自动调度（`meme-workflow-controller` 的第一个 phase）
- 批量候选池筛选（GMGN trending / trenches / signal / mixed）

## 输入

- `token_address: str` — Solana token 合约地址（base58）
- `chain: str = "sol"` — 链标识，本阶段固定 sol
- `entry_source: str` — 入口来源（`manual_ca` / `trending` / `trenches` / `signal`）
- `entry_reason: str` — 入口理由（自由文本，由调用方写入）
- 可选 `gmgn: GmgnClient` — 注入测试桩

## 处理流程

1. 地址格式校验（base58 + Solana 长度）
2. 调用 `gmgn-cli` 取 token info / pool / liquidity
3. 计算 `initial_validation`（address_valid / token_exists / has_pool / has_liquidity / is_on_curve）
4. 应用 `rules/entry_five_forces_rules_v1.json` 五力门 + 降级规则 + blocker 规则
5. 计算 confidence_score、降级原因、blocker 原因
6. 落盘 `data/runs/<token>/candidate_entry.json`（schema 校验）
7. 通过 `phase_state` 推进状态机

## 输出

- 文件：`data/runs/<token>/candidate_entry.json`
- 关键字段：`status`（PASS/BLOCK/ERROR）、`gate_decision`、`basic_gate`、
  `entry_aux_decision`、`five_forces`、`confidence_score`、`blocker_reasons`、
  `missing_fields`、`next_action`
- 返回 dict（同 JSON 内容）

## 依赖

- `common.gmgn_client.GmgnClient` — gmgn-cli subprocess 封装
- `common.file_io` / `common.validators` / `common.phase_state`
- `rules/entry_five_forces_rules_v1.json` — Five-Forces 阈值（受 freeze record 002 管控）
- 同目录下的 `schema.py` / `rules.py`

## 不做什么

- 不做交易动作（实盘 / 签名 / 广播 / swap）
- 不做价格预测
- 不做钱包结构分析（那是 Skill 03/04）
- 不做最终入场决策（那是 Skill 06 trade-gate）
- 不在骨架模式（`SIKK_SKELETON_MODE=1`）下被真实调用——由 controller 短路为 mock

## 使用方式

```bash
# 单 token
python3 skills/meme-candidate-entry/scripts/run.py <token_address>

# 由 controller 调度（推荐）
python3 skills/meme-workflow-controller/scripts/run.py run <token_address>

# 批量候选池
# 通过 controller 的 screen 子命令
python3 skills/meme-workflow-controller/scripts/run.py screen --source trending --limit 10
```

## 安全边界

Phase 1 paper-only。本 skill 永不发起交易动作。
