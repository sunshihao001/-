# GMGN Canonical Bytes — 已算好，不需 L1 计算

> 来源：gmgn-byte-decomposition-v0.1.md (Part 0)
> 共 12 子类，约 120 字段
> 这些字段从 GMGN API 直接返回，不需要你做任何组合计算

---

## 0.1 价格/市值

| field | source | meaning |
|-------|--------|---------|
| price | token info / trending | 当前价格 (USD) |
| market_cap | trending | 市值 (USD) |
| usd_market_cap | trenches | 市值 (USD) |
| ath_price | token info | 历史最高价 (USD) |
| history_highest_market_cap | trending | 历史最高市值 (USD) |
| liquidity | token info / trending | 流动性 (USD) |
| initial_liquidity | trending | 初始流动性 (USD) |
| price_change_percent | trending | 区间价格变化 (%) |
| price_change_percent1m | trending | 1分钟变化 (%) |
| price_change_percent5m | trending | 5分钟变化 (%) |
| price_change_percent1h | trending | 1小时变化 (%) |

---

## 0.2 交易量

| field | source | meaning |
|-------|--------|---------|
| volume_{1m,5m,1h,6h,24h} | token info (price.*) | 各窗口交易量 (USD) |
| buy_volume_{1m,5m,1h,6h,24h} | token info (price.*) | 各窗口买入量 (USD) |
| sell_volume_{1m,5m,1h,6h,24h} | token info (price.*) | 各窗口卖出量 (USD) |
| swaps_{1m,5m,1h,6h,24h} | token info (price.*) | 各窗口 swap 数 |
| buys_{1m,5m,1h,6h,24h} | token info (price.*) | 各窗口买入笔数 |
| sells_{1m,5m,1h,6h,24h} | token info (price.*) | 各窗口卖出笔数 |
| volume | trending | 区间交易量 (USD) |
| volume_1h | trenches | 1h交易量 (USD) |
| volume_24h | trenches | 24h交易量 (USD) |
| net_buy_24h | trenches | 24h净买入量 (USD) |
| swaps | trending | 区间 swap 数 |
| buys / sells | trending | 区间买卖数 |
| swaps_1m / swaps_1h / swaps_24h | trenches | 各窗口 swap 数 |
| buys_24h / sells_24h | trenches | 24h 买卖数 |
| gas_fee | trending | 平均 gas 费 |

---

## 0.3 持有人/钱包

| field | source | meaning |
|-------|--------|---------|
| holder_count | token info / trending | 持有者数量 |
| smart_degen_count | trending / wallet_tags_stat | 聪明钱钱包数 |
| renowned_count | trending / wallet_tags_stat | KOL 钱包数 |
| sniper_wallets | wallet_tags_stat | 狙击手钱包数 |
| rat_trader_wallets | wallet_tags_stat | 内部人钱包数 |
| bundler_wallets | wallet_tags_stat | 捆绑买入钱包数 |
| whale_wallets | wallet_tags_stat | 鲸鱼钱包数 |
| fresh_wallets | wallet_tags_stat | 新钱包数 |
| bluechip_owner_percentage | trending | 蓝筹持有者比例 |

---

## 0.4 持仓集中度

| field | source | meaning |
|-------|--------|---------|
| top_10_holder_rate | token security / stat | Top 10 持仓比 (0-1) |
| dev_team_hold_rate | token security / stat | 开发团队持仓比 (0-1) |
| creator_balance_rate | token security | 创建者持仓比 (0-1) |
| creator_hold_rate | stat | 创建者持仓比 |
| suspected_insider_hold_rate | token security | 疑似内部人持仓比 |
| stat.private_vault_hold_rate | stat | vanish 持仓比 |
| stat.bot_degen_rate | stat | Bot degen 比 |
| stat.fresh_wallet_rate | stat | 新钱包比例 |

---

## 0.5 安全/风险

| field | source | meaning |
|-------|--------|---------|
| rug_ratio | token security / trending | Rug 风险分 (0-1) |
| is_honeypot | token security | 是否貔貅 (BSC/Base) |
| is_wash_trading | token security / trending | 是否刷量 |
| open_source | token security | 合约是否开源 |
| owner_renounced | token security | 所有权是否放弃 |
| renounced_mint | token security | Mint 权限放弃 (SOL) |
| renounced_freeze_account | token security | Freeze 权限放弃 (SOL) |
| buy_tax | token security | 买入税 |
| sell_tax | token security | 卖出税 |
| burn_status | token security | LP 燃烧状态 |
| lock_percent | trending | 锁仓比例 |
| sniper_count | token security | 狙击手数 |
| rat_trader_amount_rate | token security | 内部人交易比 |
| bundler_trader_amount_rate | token security | 捆绑交易比 |
| bundler_rate | trending | 捆绑交易比 (trending版) |
| entrapment_ratio | trending | 诱捕交易比 |
| top70_sniper_hold_rate | trending | Top70 sniper 持仓比 |
| bot_degen_count | trending | Bot degen 数 |
| bot_degen_rate | trending | Bot degen 比 |

---

## 0.6 Dev / Creator

| field | source | meaning |
|-------|--------|---------|
| creator_token_status | token security / trending | 开发者持仓状态 (hold/close) |
| creator_close | trending | 是否已清仓 (boolean) |
| dev_token_burn_ratio | trending | Dev token 燃烧比 |
| dev.creator_open_count | token info | 历史发币数 |
| dev.twitter_name_change_history | token info | 改名历史 (array) |
| dev.twitter_del_post_token_count | token info | 删推数 |
| dev.twitter_create_token_count | token info | 推广 token 数 |
| dev.dexscr_ad | token info | 是否投放广告 |
| dev.dexscr_update_link | token info | 是否更新 DexScreener 链接 |
| dev.dexscr_boost_fee | token info | 是否使用 Boost |
| dev.dexscr_trending_bar | token info | 是否上 trending bar |
| dev.ath_token_info.ath_mc | token info | 历史最好 token ATH 市值 |
| dev.cto_flag | token info | 社区接管标志 |
| dev.fund_from | token info | 创建者资金来源 |
| dev.offchain | token info | 是否 offchain |

---

## 0.7 Token 生命周期

| field | source | meaning |
|-------|--------|---------|
| creation_timestamp | token info | 创建时间 (unix) |
| open_timestamp | token info | 开交易时间 (unix) |
| launchpad | token info | Launchpad 标识 |
| launchpad_status | token info | 状态 (0=未开,1=进行中,2=已迁移) |
| launchpad_progress | token info | Bonding curve 进度 (0-1) |
| launchpad_platform | token info / trending | 平台名 |
| is_on_curve | token holders | 是否仍在 bonding curve |
| migrated_pool | token info | 迁移后池地址 |
| migration_market_cap | token info | 迁移时市值 |
| locked_ratio | token info | 锁定比例 |
| og | token info | 是否 OG token |
| total_supply | token info | 总供应量 |
| circulating_supply | token info | 流通供应量 |

---

## 0.8 池子

| field | source | meaning |
|-------|--------|---------|
| pool.liquidity | token info | 池子流动性 (USD) |
| pool.exchange | token info | DEX 名 |
| pool.quote_symbol | token info | 报价 token 代号 |
| pool.base_reserve_value | token info | 基础储备 USD |
| pool.quote_reserve_value | token info | 报价储备 USD |
| pool.fee_ratio | token info | 费率 |
| pool.creation_timestamp | token info | 池创建时间 |

---

## 0.9 社交/注意力

| field | source | meaning |
|-------|--------|---------|
| link.twitter_username | token info | X 用户名 |
| link.telegram | token info | TG 链接 |
| link.website | token info | 网站 |
| link.description | token info | 描述文本 |
| link.verify_status | token info | 社交验证状态 |
| cto_flag | trending / trenches | 社区接管 |
| has_at_least_one_social | trenches | 是否有社交 |
| x_user_follower | trenches | X 粉丝数 |

---

## 0.10 热度

| field | source | meaning |
|-------|--------|---------|
| hot_level | trending / price.hot_level | 热度等级 |
| rank | trending | 排名位置 |

---

## 0.11 单个 Holder/Trader（遍历 list 时使用）

| field | source | meaning |
|-------|--------|---------|
| address | holders/traders | 钱包地址 |
| balance / amount_cur | holders/traders | 持有量 |
| usd_value | holders/traders | 持有 USD 价值 |
| amount_percentage | holders/traders | 持有总供应比 (0-1) |
| buy_volume_cur | holders/traders | 总买入量 USD |
| sell_volume_cur | holders/traders | 总卖出量 USD |
| buy_tx_count_cur | holders/traders | 买入笔数 |
| sell_tx_count_cur | holders/traders | 卖出笔数 |
| sell_amount_percentage | holders/traders | 已卖出比例 (0-1) |
| profit | holders/traders | 总利润 USD |
| realized_profit | holders/traders | 已实现利润 USD |
| unrealized_profit | holders/traders | 未实现利润 USD |
| avg_cost | holders/traders | 平均买入价 USD |
| avg_sold | holders/traders | 平均卖出价 USD |
| start_holding_at | holders/traders | 首次持有时间 (unix) |
| last_active_timestamp | holders/traders | 最近活动时间 (unix) |
| tags | holders/traders | 平台级标签 [kol, smart_degen...] |
| maker_token_tags | holders/traders | Token 级行为标签 [bundler, top_holder...] |
| native_transfer.address | holders/traders | 资金来源地址 |
| created_at | holders/traders | 钱包创建时间 (unix) |

---

## 0.12 K 线

| field | source | meaning |
|-------|--------|---------|
| time | kline | 开盘时间 (ms) |
| open | kline | 开盘价 |
| close | kline | 收盘价 |
| high | kline | 最高价 |
| low | kline | 最低价 |
| volume (kline) | kline | USD 交易量 |
| amount (kline) | kline | Token 单位交易量 |

---

> 以上字段全部从 GMGN API 直接返回，不需要做任何 L1 计算。
> 它们作为 L1 Features 的输入字节使用。
