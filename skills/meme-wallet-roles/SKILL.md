---
name: meme-wallet-roles
description: |
  Skill 03 — Solana meme token 钱包角色识别。基于 GMGN top traders / smart money /
  dev 数据，对参与该 token 的钱包做角色归类（dev / smart_money / early_buyer /
  sniper / 普通），并产出 smart_money_behavior（净方向：买入/卖出/中性）。
  受 acceptance gate 约束：不能把 GMGN 标签当作最终角色定性，需有行为规则佐证。
  Trigger: token-panel 已完成；需要知道谁在这个 token 上交易；workflow controller
  的第三步。
---

# meme-wallet-roles

## 作用

把 GMGN 返回的「钱包列表」转化为「带角色 + 行为方向」的标准 wallet_roles 输出。
下游 wallet-structure 和 evidence-chain 都从这里读「这些钱包是什么角色、在做什么」。

## 触发场景

- token-panel 已完成
- workflow controller 第三步自动调度
- 单独想看某 token 上 dev / smart money / 早期买家的行为

## 输入

- `token_address: str`
- `chain: str = "sol"`
- 可选 `gmgn: GmgnClient`
- 上游：`data/runs/<token>/token_panel.json`（读取 creator 等信息）

## 处理流程

1. 调用 GMGN 取 top traders / smart money trades / dev info / wallet stats
2. `_merge_dev_data` 合并 dev 创建信息和持仓
3. `_build_early_buyer_analysis` 识别早期买家行为模式
4. 对每个钱包做角色归类（dev / smart_money / early_buyer / sniper / 普通）
5. 计算 `wallet_summary`（smart_money_count 等聚合指标）
6. 计算 `smart_money_behavior.sm_net_direction`（buy/sell/neutral）
7. 落盘 `wallet_roles.json` + `wallet_roles.md`

## 输出

- 文件：`data/runs/<token>/wallet_roles.json` + `wallet_roles.md`
- 关键字段：`wallet_summary`、`smart_money_behavior`、`dev_info`、`early_buyer_analysis`、
  `wallets`、`missing_fields`
- 返回 dict

## 依赖

- `common.gmgn_client.GmgnClient`
- `common.file_io` / `common.validators`
- 上游：`token_panel.json`

## 不做什么

- **不**把 GMGN 标签直接当作最终角色定性（acceptance gate 强制约束）
- 不做钱包结构集中度分析（Skill 04）
- 不做证据链合成（Skill 05）
- 不声称「这是庄家」「这是内幕」（freeze 002 边界）
- 不做跟单功能
- 不在骨架模式下被真实调用

## 使用方式

```bash
python3 skills/meme-wallet-roles/scripts/run.py <token_address>

# 推荐：由 controller 调度
python3 skills/meme-workflow-controller/scripts/run.py run <token_address>
```

## 安全边界

Phase 1 paper-only。只读 GMGN，不签名、不交易、不输出确定性人物指认。
