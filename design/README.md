# Solana Meme Workflow OS — Design Index

## 系统一句话

> GMGN 数据 → Hermes skill 流水线 → 证据级钱包研究 → 门控判断 → 纸面验证 → 半自动交易

在 Hermes 上运行，不复制传统量化体系。轻量、可中断、可恢复、可审计。

## Phase 路线图

| Phase | 名称 | 状态 | 范围 |
|-------|------|------|------|
| **0** | Workflow Contract | ✅ 设计完成 | 目录/Schema/状态/规则/禁止事项 |
| **1** | Research Pipeline | ✅ 设计完成 | 6 Skills + Controller |
| 2 | Paper Trading | 未开始 | 纸面交易模拟 + 复盘 |
| 3 | Auto Candidate | 未开始 | 自动候选 + 信号订阅 |
| 4 | Semi-Auto | 未开始 | 人工确认交易 |
| 5 | Auto Execution | 未开始 | 全自动交易 |

## Phase 1 设计文件

| # | 文件 | Skill | 定位 |
|---|------|-------|------|
| 0 | [phase0-workflow-contract.md](phase0-workflow-contract.md) | — | 工作流契约 |
| 1 | [phase1-skill-01-candidate-entry.md](phase1-skill-01-candidate-entry.md) | meme-candidate-entry | 候选入口 (≈ 手动输入 CA) |
| 2 | [phase1-skill-02-token-panel.md](phase1-skill-02-token-panel.md) | meme-token-panel | Token 数据面板 (≈ DexScreener) |
| 3 | [phase1-skill-03-wallet-roles.md](phase1-skill-03-wallet-roles.md) | meme-wallet-roles | 钱包角色识别 (≈ Nansen) |
| 4 | [phase1-skill-04-wallet-structure.md](phase1-skill-04-wallet-structure.md) | meme-wallet-structure | 钱包结构分析 (≈ Bubblemaps) |
| 5 | [phase1-skill-05-evidence-chain.md](phase1-skill-05-evidence-chain.md) | meme-evidence-chain | 证据链汇总 (≈ Arkham) |
| 6 | [phase1-skill-06-trade-gate.md](phase1-skill-06-trade-gate.md) | meme-trade-gate | 门控判断 |
| 7 | [phase1-skill-07-workflow-controller.md](phase1-skill-07-workflow-controller.md) | meme-workflow-controller | 流程总控 |

## Skill 执行流

```
/sol <CA>
  │
  ▼
┌─────────────────────┐
│ meme-candidate-entry │  验证 token 地址有效
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  meme-token-panel   │  基础数据 + 安全审计
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  meme-wallet-roles  │  SM / KOL / Sniper / Dev 角色
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ meme-wallet-structure│  同源 / 协调买入 / 集中度
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ meme-evidence-chain │  汇总推断 + 叙事
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│   meme-trade-gate   │  门控 → BLOCK / WATCH / PAPER
└──────────┬──────────┘
           ▼
      workflow_summary.md
      → Telegram 输出
```

## Hermes 特性利用

| Hermes 能力 | 本系统用法 |
|-------------|-----------|
| Skill 系统 | 每个分析模块 = 一个 skill，可独立更新 |
| Phase State | JSON 文件状态机，可中断恢复 |
| Telegram Gateway | `/sol <CA>` 直接触发分析 |
| Cron Jobs | Phase 3: 定时扫描 GMGN trending |
| Memory | 记住用户偏好、历史分析结论 |
| Safe Mode | Phase 1 不允许交易，只有 BLOCK/WATCH/PAPER |
| Evidence Pipeline | 每步输出 evidence + counter_evidence |
| Delegation | Phase 3+: 并行分析多个 token |

## GMGN CLI 命令索引

| 类别 | 命令 | 用于 Skill |
|------|------|-----------|
| Token 信息 | `gmgn-cli token info` | candidate-entry, token-panel |
| Token 安全 | `gmgn-cli token security` | token-panel |
| Token 池 | `gmgn-cli token pool` | token-panel |
| K 线 | `gmgn-cli market kline` | token-panel |
| 持有人 | `gmgn-cli token holders` | wallet-roles |
| 交易者 | `gmgn-cli token traders` | wallet-roles |
| 钱包统计 | `gmgn-cli portfolio stats` | wallet-roles |
| 创建代币 | `gmgn-cli portfolio created-tokens` | wallet-roles |
| 钱包活动 | `gmgn-cli portfolio activity` | wallet-structure |
| Token 余额 | `gmgn-cli portfolio token-balance` | wallet-structure |
| 趋势 | `gmgn-cli market trending` | candidate-entry (Phase 3) |
| 新币 | `gmgn-cli market trenches` | candidate-entry (Phase 3) |
| 信号 | `gmgn-cli market signal` | candidate-entry (Phase 3) |
