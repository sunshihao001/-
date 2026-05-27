# CR-2026-05-25-002 Canonical Bytes Evidence Addendum

date: 2026-05-26
change_id: CR-2026-05-25-002
status: EVIDENCE_ADDENDUM_READY
human_approval_status: PENDING

## 1. Purpose

This addendum attaches `00b-GMGN-Canonical-Bytes` as the Layer 0 raw-byte dictionary for CR-2026-05-25-002.

CR-2026-05-25-002 proposes landing GMGN field-combination theory into S01 `meme-candidate-entry` as a Five-Forces Gate. The uploaded Canonical Bytes document clarifies which GMGN fields are already directly available and therefore can be used as raw inputs for rule construction.

## 2. Source Evidence

Uploaded document:

```text
/root/.hermes/profiles/cangweizhixingbot/cache/documents/doc_732f84d37c37_00b-GMGN-Canonical-Bytes.txt
```

Project copies already present:

```text
/root/sikk-gmgn/design/phase1-research/00b-GMGN-Canonical-Bytes.txt
/root/sikk-gmgn/design/phase1-research/00b-GMGN-Canonical-Bytes.md
```

Verification:

```text
cmp_txt_exit:0
cmp_md_exit:0
```

Interpretation:

```text
Uploaded document matches the project research asset exactly.
```

## 3. Evidence Level

Evidence level for this asset:

```text
E3_FILE_READ_OR_SCHEMA_VALID
```

Reason:

- file exists in uploaded cache
- file exists in project research directory
- file content was read
- uploaded copy was byte-compared against both project copies

This does not imply runtime implementation proof. Runtime proof would require task execution and tests after CR approval.

## 4. Field Categories Available for Five-Forces Rule Design

Canonical bytes provide raw GMGN source fields for:

### Absorption Power

Likely raw fields:
- `liquidity`
- `initial_liquidity`
- `pool.liquidity`
- `market_cap`
- `usd_market_cap`
- `volume_{1m,5m,1h,6h,24h}`
- `buy_volume_{1m,5m,1h,6h,24h}`
- `net_buy_24h`
- `pool.base_reserve_value`
- `pool.quote_reserve_value`

Use:
- depth / liquidity / value-absorption hint

Forbidden interpretation:
- not a direct buy signal

### Diffusion Power

Likely raw fields:
- `holder_count`
- `smart_degen_count`
- `renowned_count`
- `bluechip_owner_percentage`
- `swaps_{1m,5m,1h,6h,24h}`
- `buys_{1m,5m,1h,6h,24h}`
- `sells_{1m,5m,1h,6h,24h}`
- `hot_level`
- `rank`
- `x_user_follower`
- `has_at_least_one_social`

Use:
- participant breadth / attention spread hint

Forbidden interpretation:
- GMGN tags and hot/rank must not be hard gates by themselves

### Control Power

Likely raw fields:
- `top_10_holder_rate`
- `dev_team_hold_rate`
- `creator_balance_rate`
- `creator_hold_rate`
- `suspected_insider_hold_rate`
- `sniper_wallets`
- `bundler_wallets`
- `whale_wallets`
- `top70_sniper_hold_rate`
- individual holder `amount_percentage`
- individual holder `native_transfer.address`

Use:
- concentration / coordination / source-risk hint

Forbidden interpretation:
- must not claim 确定庄家 / 确定内幕

### Camouflage Power

Likely raw fields:
- `is_wash_trading`
- `bot_degen_count`
- `bot_degen_rate`
- `stat.bot_degen_rate`
- `fresh_wallets`
- `stat.fresh_wallet_rate`
- `link.verify_status`
- `dev.twitter_name_change_history`
- `dev.twitter_del_post_token_count`
- `dev.dexscr_ad`
- `dev.dexscr_boost_fee`
- `dev.dexscr_trending_bar`

Use:
- forgeability / attention manipulation / wash-risk hint

Forbidden interpretation:
- not a final fraud verdict unless supported by downstream evidence

### Exit Power

Likely raw fields:
- individual holder `sell_amount_percentage`
- individual holder `realized_profit`
- individual holder `unrealized_profit`
- individual holder `avg_cost`
- individual holder `avg_sold`
- individual holder `last_active_timestamp`
- `creator_token_status`
- `creator_close`
- `rat_trader_amount_rate`
- `bundler_trader_amount_rate`
- `price_change_percent{1m,5m,1h}`
- `sell_volume_{1m,5m,1h,6h,24h}`

Use:
- early actor exit incentive / sell-pressure hint

Forbidden interpretation:
- not a final sell command or execution signal

## 5. Required Rule-Mapping Discipline for TASK-RULE-005

When `rules/entry_five_forces_rules_v1.json` is authored after approval, each threshold rule should include:

```json
{
  "source_fields": [],
  "field_group": "canonical_bytes_0_x",
  "raw_or_derived": "raw_gmgn_byte",
  "force_target": "absorption_power | diffusion_power | control_power | camouflage_power | exit_power | risk_density | basic_gate",
  "allowed_use": "entry_hint_or_filter",
  "forbidden_use": "final_trade_decision"
}
```

## 6. CR Impact

This addendum strengthens CR-2026-05-25-002 because it proves the proposed Five-Forces layer has an existing Layer 0 raw-byte source dictionary.

It does not approve the CR.
It does not modify frozen docs.
It does not unblock task execution by itself.

## 7. Recommended Human Decision

Recommended PM/human decision wording:

```text
Approve CR-2026-05-25-002 for frozen-doc update only, with 00b-GMGN-Canonical-Bytes as the Layer 0 source-field registry. Do not authorize live trading, swap, signing, broadcast, or final trade-decision semantics.
```

## 8. Final Status

```text
CR_EVIDENCE_ADDENDUM_READY
HUMAN_APPROVAL_PENDING
TASK_DOC_002_STILL_BLOCKED
NO_LIVE_EXECUTION_AUTHORIZED
```
