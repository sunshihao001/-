# PROMPT 2: Token Panel — 代币数据面板

## 直接发给 GPT 的 Prompt

```
## 任务

执行 meme-token-panel：对一个已验证的 Solana token 生成完整的基础数据面板和安全审计。

## 输入

Token 地址：{CA}
前置 candidate_entry.json：{粘贴或说明 PASS}

## 你要做的事

### Step 1: 生成数据采集命令

依次输出以下命令（我会把结果粘回来）：

```bash
# 基础信息 + 价格
gmgn-cli token info --chain sol --address {CA} --raw

# 安全审计
gmgn-cli token security --chain sol --address {CA} --raw

# 流动性池
gmgn-cli token pool --chain sol --address {CA} --raw

# 最近1小时K线
gmgn-cli market kline --chain sol --address {CA} --resolution 5m --from {1小时前时间戳} --to {当前时间戳} --raw
```

### Step 2: 收到数据后，提取并填充以下字段

**basic_info**: symbol, name, price, market_cap, liquidity, holder_count, total_supply, pair_age_seconds, launchpad, pool_address, pool_exchange, ath_price

**security**: 从 token security 返回提取所有安全字段：is_honeypot, renounced_mint, renounced_freeze_account, buy_tax, sell_tax, rug_ratio, top_10_holder_rate, creator_token_status, creator_balance_rate, dev_team_hold_rate, suspected_insider_hold_rate, is_wash_trading, rat_trader_amount_rate, bundler_trader_amount_rate, sniper_count, burn_status

**wallet_tags_stat**: smart_wallets, renowned_wallets, sniper_wallets, rat_trader_wallets, bundler_wallets, whale_wallets, fresh_wallets

**dev_info**: creator_address, creator_token_balance, creator_open_count, fund_from, cto_flag, dexscr_ad, dexscr_update_link

**social**: twitter_username, website, telegram

**kline_summary**: 从K线数据计算 open, close, high, low, total_volume_usd, trend（up/down/sideways/volatile）

### Step 3: 生成 risk_score_card

| 字段 | safe 条件 | danger 条件 |
|------|----------|------------|
| honeypot | is_honeypot != "yes" | is_honeypot = "yes" |
| mint_authority | renounced_mint = true | false |
| freeze_authority | renounced_freeze_account = true | false |
| rug_ratio_level | < 0.10 = low, 0.10-0.30 = medium | > 0.30 = high |
| concentration_level | < 0.20 = low, 0.20-0.50 = medium | > 0.50 = high |
| dev_status | creator_close = safe | creator_hold = risk |
| wash_trading | false = clean | true = detected |
| overall_risk | 0 danger + ≤1 medium = low; 2+ medium = medium | 任何 danger = high; honeypot = critical |

### Step 4: 判断 status

**BLOCK（立即停止）：**
- is_honeypot = "yes"
- rug_ratio > 0.5
- renounced_mint = false AND renounced_freeze_account = false
- buy_tax > 0.10 OR sell_tax > 0.10

**WARN（继续但记录）：**
- rug_ratio 0.3-0.5
- top_10_holder_rate > 0.50
- creator_token_status = "creator_hold"
- sniper_count > 20
- is_wash_trading = true
- smart_wallets = 0
- liquidity < 10000

**PASS：** 无 BLOCK 触发 + renounced_mint = true + renounced_freeze = true + rug_ratio < 0.3 + liquidity >= 10000

### 降级条件

- K线数据不足 → downgrade + kline_summary 设 null
- 社交全空 → downgrade: "No social presence"
- holder_count < 100 → downgrade: "Low holder count"
- liquidity 10000-50000 → downgrade: "Moderate liquidity"
- smart_wallets 1-2 → downgrade: "Weak smart money signal"

### Step 5: 输出 JSON

```json
{
  "schema_version": "1.0",
  "skill_name": "meme-token-panel",
  "task_id": "{CA}_{时间戳}",
  "token_address": "{CA}",
  "chain": "sol",
  "timestamp": "{ISO 8601}",
  "status": "PASS/WARN/BLOCK/NEED_MORE_DATA",
  "basic_info": { ... },
  "security": { ... },
  "wallet_tags_stat": { ... },
  "dev_info": { ... },
  "social": { ... },
  "kline_summary": { ... },
  "risk_score_card": { ... },
  "evidence": [ {"claim":"...", "source":"gmgn-cli token security", "value":"...", "weight":"high/medium/low"} ],
  "counter_evidence": [],
  "confidence_score": 0.0,
  "downgrade_reasons": [],
  "blocker_reasons": [],
  "missing_fields": [],
  "valid_until": "{30分钟后}",
  "next_action": "meme-wallet-roles",
  "handoff_to": "meme-wallet-roles"
}
```

### Step 6: 同时输出中文 Markdown 报告

标题格式：`# Token Panel: {symbol} ({name})`
包含：基础信息、安全评分卡、Smart Money 统计、Dev 信息、K线摘要、风险警告、判定结果。

## 禁止

- 不编造 API 没返回的字段，缺失就放 missing_fields
- 不给买卖建议
- BLOCK 状态下 next_action 必须是 "STOP"
```
