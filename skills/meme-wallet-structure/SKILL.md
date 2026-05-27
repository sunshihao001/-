---
name: meme-wallet-structure
description: |
  Skill 04 — Solana meme token 持有人结构分析。基于 GMGN holders 数据，剔除
  pool / 交易所地址后，计算 top10 / top50 集中度、同源钱包组、可疑分布模式，
  输出 structure_risk（low/medium/high/critical）。受 acceptance gate 约束：
  必须排除 pool/exchange 地址再算集中度。
  Trigger: wallet-roles 已完成；需要知道持仓是否过度集中；workflow controller
  的第四步。
---

# meme-wallet-structure

## 作用

把 GMGN holders 列表转化为「结构风险评级」。下游 evidence-chain 和 trade-gate
依赖此评级判断 token 是否有派发 / 庄控 / 同源钱包风险。

## 触发场景

- wallet-roles 已完成
- workflow controller 第四步自动调度
- 单独想看持仓集中度和同源关系

## 输入

- `token_address: str`
- `chain: str = "sol"`
- 上游：`wallet_roles.json`（可选，用于剔除已识别地址）

## 处理流程

1. 调用 GMGN holders / wallet stats
2. `_is_system_wallet` 剔除 pool、交易所、known system 地址
3. `_analysis_wallets` 计算 top10 / top50 集中度、Gini 等
4. `_same_source_groups` 识别同资金来源的钱包组
5. 综合判定 `structure_risk.overall_structure_risk`（low/medium/high/critical）
6. 落盘 `wallet_structure.json` + `wallet_structure.md`

## 输出

- 文件：`data/runs/<token>/wallet_structure.json` + `wallet_structure.md`
- 关键字段：`structure_risk`、`concentration`、`same_source_groups`、`holders_count`、
  `missing_fields`
- 返回 dict

## 依赖

- `common.gmgn_client.GmgnClient`
- `common.file_io` / `common.validators`
- 上游：`wallet_roles.json`（可选）

## 不做什么

- **不**把 pool / 交易所地址算进集中度（acceptance gate 强制约束）
- 不做钱包角色识别（Skill 03）
- 不做证据链合成（Skill 05）
- 不做最终交易裁决（Skill 06）
- 不声称「确定派发」「确定庄家」
- 不在骨架模式下被真实调用

## 使用方式

```bash
python3 skills/meme-wallet-structure/scripts/run.py <token_address>

# 推荐：由 controller 调度
python3 skills/meme-workflow-controller/scripts/run.py run <token_address>
```

## 安全边界

Phase 1 paper-only。只读链上 holders 数据，不做任何交易动作。
