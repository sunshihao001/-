# PROMPT 7: 全流程一键执行

## 直接发给 GPT 的 Prompt（一次跑完 6 步）

```
## 任务

对一个 Solana token 执行完整的 6 步研究流水线，从地址验证到门控判断。

## Token

地址：{在这里填 CA}
来源：{manual_ca / gmgn_trending / telegram}
原因：{为什么要看}

## 流水线

按以下顺序严格执行，每步必须先输出 GMGN 采集命令，等我粘贴数据后才能继续下一步。任何一步 BLOCK 则立即停止。

### Step 1/6: Candidate Entry
- 输出命令：`gmgn-cli token info --chain sol --address {CA} --raw`
- 我粘贴数据后，验证地址有效性、token 存在、有池子、有流动性
- 输出 candidate_entry.json 摘要
- PASS → 继续；BLOCK → 停止并输出原因

### Step 2/6: Token Panel
- 输出命令：token info + token security + token pool + market kline
- 我粘贴数据后，生成 basic_info, security, risk_score_card
- 输出 token_panel.json 摘要 + risk_score_card 表格
- BLOCK → 停止；PASS/WARN → 继续

### Step 3/6: Wallet Roles
- 输出命令：holders (top50 + smart_degen + renowned + sniper + bundler + rat_trader + fresh_wallet) + traders + dev created-tokens + dev stats
- 我粘贴数据后，分类角色、计算 SM 行为方向、评估 dev 信誉
- 输出 wallet_roles.json 摘要

### Step 4/6: Wallet Structure
- 基于 Step 3 的 key_wallets 数据，分析同源资金、协调买入、卖出模式、集中度
- 如果 native_transfer_from 数据不足，输出补充查询命令
- 输出 wallet_structure.json 摘要

### Step 5/6: Evidence Chain
- 汇总 Step 2-4 所有证据
- 推断 dominant_behavior
- 计算 confidence_score
- 输出叙事（one_line + paragraph）

### Step 6/6: Trade Gate
- 执行一票否决检查
- 执行观察规则检查
- 计算 gate_score
- 输出 gate_decision: BLOCK / WATCH / PAPER_ONLY / NEED_MORE_DATA

## 最终输出格式

完成全部 6 步后，输出一份完整的中文报告：

```markdown
# {symbol} 研究报告

## 基础信息
Price | Market Cap | Liquidity | Holders | Age

## 安全评分
{risk_score_card}

## 关键钱包
| 角色 | 数量 | 合计持仓 |
| Smart Money | x | x% |
| KOL | x | x% |
| Dev | x | x% |
...

## SM 行为
方向：{accumulating/distributing/neutral}

## 钱包结构
- 同源组：{count}，合计 {pct}%
- 协调买入：{count}
- 集中度：{level}

## 证据链
**主导行为：{dominant_behavior}**
**置信度：{confidence_score}**

{paragraph narrative}

## 风险因素
{risk_factors}

## 正面信号
{positive_signals}

## 门控判断
**Decision: {gate_decision}**
**Score: {total_score}/100**

| 维度 | 得分 |
| Security | {x}/30 |
| Smart Money | {x}/30 |
| Structure | {x}/20 |
| Behavior | {x}/20 |

触发的规则：{list}
下次重评条件：{list}
```

## 工作方式

1. 你每步先输出需要的 gmgn-cli 命令
2. 我把命令结果粘贴给你
3. 你处理数据、执行判断、输出该步摘要
4. 继续下一步或停止（如果 BLOCK）
5. 全部完成后输出完整报告

## 全程禁止

- 不编造任何数据
- 不说"确定"、"一定"、"应该买/卖"
- 缺数据用 NEED_MORE_DATA，不猜测
- Phase 1 最高只到 PAPER_ONLY
- 不输出任何交易执行指令
```
