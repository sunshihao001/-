---
name: meme-token-panel
description: |
  Skill 02 — Solana meme token 全景面板。给定 token 地址，并行拉取 GMGN token info
  + security + pool + kline，组装统一的 token_panel（基本信息 / 安全评分 / 池子 /
  K 线），并产出 risk_score_card（low/medium/high/critical），是下游钱包结构、
  证据链、交易门的共同上下文。
  Trigger: 已通过 candidate-entry 的 token 需要完整面板；workflow controller 的
  第二步；手动看一个 token 的安全/池子全貌。
---

# meme-token-panel

## 作用

把 GMGN 的 4 个独立接口（token info / security / pool / kline）聚合成一份
机器可读的 `token_panel.json` + 人类可读的 `token_panel.md`。下游所有 skill
（wallet-roles / wallet-structure / evidence-chain / trade-gate）都从这份面板
读取「这个 token 本身的事实」。

## 触发场景

- candidate-entry 已 PASS，需要补齐 token 全面信息
- workflow controller 第二步自动调度
- 单独想看某 token 的安全/池子/K 线全貌

## 输入

- `token_address: str`
- `chain: str = "sol"`
- 可选 `gmgn: GmgnClient`

## 处理流程

1. 并行调用 GMGN：token info / security / pool / kline
2. `_build_basic_info` 组装 symbol/name/decimals/创建时间/launchpad
3. `_build_security` 组装权限放弃、honeypot、washing trading、bundler 等安全字段
4. `_build_pool` 组装流动性、市值、24h 交易量、买卖比
5. `_build_kline` 组装最近 K 线形态摘要
6. 计算 `risk_score_card.overall_risk`（low/medium/high/critical）
7. 落盘 `token_panel.json`（schema 校验）+ `token_panel.md`

## 输出

- 文件：`data/runs/<token>/token_panel.json` + `token_panel.md`
- 关键字段：`basic_info`、`security`、`pool`、`kline`、`risk_score_card`、`missing_fields`
- 返回 dict

## 依赖

- `common.gmgn_client.GmgnClient`
- `common.file_io` / `common.validators`
- 同目录 `schema.py`
- 上游：可选 `candidate_entry.json`（不强依赖）

## 不做什么

- 不做钱包/持有人分析（Skill 03/04）
- 不做证据链合成（Skill 05）
- 不做交易裁决（Skill 06）
- 不输出价格预测、不声称庄家/内幕
- 不在骨架模式下被真实调用

## 使用方式

```bash
python3 skills/meme-token-panel/scripts/run.py <token_address>

# 推荐：由 controller 调度
python3 skills/meme-workflow-controller/scripts/run.py run <token_address>
```

## 安全边界

Phase 1 paper-only。本 skill 只读 GMGN，永不发起交易。
