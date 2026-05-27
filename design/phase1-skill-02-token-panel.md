# Skill 2: meme-token-panel

## 定位

Token 基础数据面板。对标 DexScreener。负责回答：这个 token 基础状态能不能看。

## 输入

```json
{
  "token_address": "<address>",
  "chain": "sol",
  "candidate_entry": "<candidate_entry.json 路径>"
}
```

## GMGN 命令映射

| 用途 | 命令 |
|------|------|
| 基础信息 + 价格 | `gmgn-cli token info --chain sol --address <addr> --raw` |
| 安全审计 | `gmgn-cli token security --chain sol --address <addr> --raw` |
| 流动性池 | `gmgn-cli token pool --chain sol --address <addr> --raw` |
| K 线（最近 1h） | `gmgn-cli market kline --chain sol --address <addr> --resolution 5m --from <1h_ago> --to <now> --raw` |

## 输出

```json
{
  "schema_version": "1.0",
  "skill_name": "meme-token-panel",
  "task_id": "<token_address>_<timestamp>",
  "token_address": "<address>",
  "chain": "sol",
  "timestamp": "<ISO 8601>",
  "status": "PASS | WARN | BLOCK | NEED_MORE_DATA",

  "basic_info": {
    "symbol": "",
    "name": "",
    "price": 0.0,
    "market_cap": 0.0,
    "liquidity": 0.0,
    "holder_count": 0,
    "total_supply": 0,
    "pair_age_seconds": 0,
    "launchpad": "",
    "launchpad_status": 0,
    "pool_address": "",
    "pool_exchange": "",
    "ath_price": 0.0
  },

  "security": {
    "is_honeypot": "",
    "renounced_mint": false,
    "renounced_freeze_account": false,
    "open_source": "",
    "owner_renounced": "",
    "buy_tax": 0.0,
    "sell_tax": 0.0,
    "rug_ratio": 0.0,
    "top_10_holder_rate": 0.0,
    "creator_token_status": "",
    "creator_balance_rate": 0.0,
    "dev_team_hold_rate": 0.0,
    "suspected_insider_hold_rate": 0.0,
    "is_wash_trading": false,
    "rat_trader_amount_rate": 0.0,
    "bundler_trader_amount_rate": 0.0,
    "sniper_count": 0,
    "burn_status": ""
  },

  "wallet_tags_stat": {
    "smart_wallets": 0,
    "renowned_wallets": 0,
    "sniper_wallets": 0,
    "rat_trader_wallets": 0,
    "bundler_wallets": 0,
    "whale_wallets": 0,
    "fresh_wallets": 0
  },

  "dev_info": {
    "creator_address": "",
    "creator_token_balance": "",
    "creator_open_count": 0,
    "fund_from": "",
    "cto_flag": 0,
    "dexscr_ad": 0,
    "dexscr_update_link": 0
  },

  "social": {
    "twitter_username": "",
    "website": "",
    "telegram": ""
  },

  "kline_summary": {
    "resolution": "5m",
    "period": "1h",
    "open": 0.0,
    "close": 0.0,
    "high": 0.0,
    "low": 0.0,
    "total_volume_usd": 0.0,
    "trend": "up | down | sideways | volatile"
  },

  "risk_score_card": {
    "honeypot": "safe | danger | na",
    "mint_authority": "safe | danger",
    "freeze_authority": "safe | danger",
    "rug_ratio_level": "low | medium | high",
    "concentration_level": "low | medium | high",
    "dev_status": "safe | risk",
    "wash_trading": "clean | detected",
    "overall_risk": "low | medium | high | critical"
  },

  "evidence": [],
  "counter_evidence": [],
  "confidence_score": 0.0,
  "downgrade_reasons": [],
  "blocker_reasons": [],
  "missing_fields": [],
  "valid_until": "<30min>",
  "next_action": "meme-wallet-roles",
  "handoff_to": "meme-wallet-roles"
}
```

## 判断规则

### 安全硬停（BLOCK）

| 条件 | 动作 |
|------|------|
| is_honeypot = "yes" | BLOCK: "Honeypot detected" |
| rug_ratio > 0.5 | BLOCK: "Extreme rug risk" |
| renounced_mint = false AND renounced_freeze_account = false | BLOCK: "Neither mint nor freeze renounced" |
| buy_tax > 0.10 OR sell_tax > 0.10 | BLOCK: "Tax > 10%" |

### 安全警告（WARN）

| 条件 | 动作 |
|------|------|
| rug_ratio 0.3-0.5 | WARN: "High rug ratio" |
| top_10_holder_rate > 0.50 | WARN: "Top 10 hold > 50%" |
| creator_token_status = "creator_hold" | WARN: "Dev still holding" |
| sniper_count > 20 | WARN: "High sniper count" |
| is_wash_trading = true | WARN: "Wash trading detected" |
| smart_wallets = 0 | WARN: "No smart money" |
| liquidity < 10000 | WARN: "Low liquidity < $10k" |

### PASS 条件

全部硬停条件不触发，且：
- renounced_mint = true
- renounced_freeze_account = true
- rug_ratio < 0.3
- top_10_holder_rate < 0.50
- liquidity >= 10000

### risk_score_card 生成规则

| 字段 | safe | danger/high |
|------|------|-------------|
| honeypot | is_honeypot != "yes" | is_honeypot = "yes" |
| mint_authority | renounced_mint = true | renounced_mint = false |
| freeze_authority | renounced_freeze_account = true | false |
| rug_ratio_level | < 0.10 low; 0.10-0.30 medium | > 0.30 high |
| concentration_level | < 0.20 low; 0.20-0.50 medium | > 0.50 high |
| dev_status | creator_close | creator_hold |
| wash_trading | is_wash_trading = false | true |
| overall_risk | 0 high + ≤1 medium = low; 2+ medium = medium | 任何 danger/high = high; honeypot = critical |

## 降级规则

| 条件 | 降级动作 |
|------|---------|
| kline 数据不足 | downgrade: "Insufficient kline data"; kline_summary 设为 null |
| social 全部为空 | downgrade: "No social presence" |
| holder_count < 100 | downgrade: "Low holder count" |
| liquidity 10000-50000 | downgrade: "Moderate liquidity" |
| smart_wallets 1-2 | downgrade: "Weak smart money signal" |

## 阻塞规则

| 条件 | 阻塞动作 |
|------|---------|
| token info 返回错误 | ERROR + blocker_report |
| token security 返回错误 | ERROR + blocker_report |
| honeypot 检测为 yes | BLOCK + 立即停止 |
| rug_ratio > 0.5 | BLOCK + 立即停止 |

## Markdown 报告模板

同时生成 `token_panel.md`：

```markdown
# Token Panel: {symbol} ({name})

## 基础信息
- Price: ${price}
- Market Cap: ${market_cap}
- Liquidity: ${liquidity}
- Holders: {holder_count}
- Pool: {pool_exchange}
- Age: {pair_age}

## 安全评分
{risk_score_card 表格}

## Smart Money
- Smart Money Holders: {smart_wallets}
- KOL Holders: {renowned_wallets}

## Dev 信息
- Creator: {creator_address}
- Status: {creator_token_status}
- 历史发币数: {creator_open_count}

## 1h K线
- Open → Close: ${open} → ${close}
- Range: ${low} - ${high}
- Volume: ${total_volume_usd}
- Trend: {trend}

## 风险警告
{blocker_reasons + downgrade_reasons 列表}

## 判定
Status: {status}
Next: {next_action}
```
