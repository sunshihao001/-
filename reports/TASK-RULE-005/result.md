# TASK-RULE-005 Result

task_id: TASK-RULE-005
status: INTERNAL_PASS
completed_at: 2026-05-26T03:50:37Z
owner_terminal: skill-backend

## Summary

Created the machine-loadable Five-Forces entry rule file for S01 `meme-candidate-entry`:

```text
rules/entry_five_forces_rules_v1.json
```

This file converts the GMGN field-combination theory into a controlled entry-layer rule contract. It is a research / candidate-screening hint layer only and does not authorize live trading, swap, signing, broadcast, private-key access, or final trade decisions.

## Files Written

- `rules/entry_five_forces_rules_v1.json`
- `reports/TASK-RULE-005/result.md`

No other rules JSON files were modified.

## Acceptance Criteria Check

- [x] File exists at `rules/entry_five_forces_rules_v1.json`.
- [x] JSON is machine-loadable with `json.load`.
- [x] Contains keys: `schema_version`, `basic_gate`, `forces`, `risk_density`, `entry_aux_decision`, `safety`.
- [x] `basic_gate` defines numeric thresholds for:
  - `min_liquidity`
  - `min_market_cap`
  - `min_volume`
  - `min_holder_count`
  - `min_swaps`
- [x] `forces` defines classification thresholds for:
  - `absorption_power`
  - `diffusion_power`
  - `control_power`
  - `camouflage_power`
  - `exit_power`
- [x] Each force has explicit source fields and bin edges.
- [x] `risk_density` defines weighted contributions, level edges, and reason labels.
- [x] `entry_aux_decision` defines deterministic mapping from `basic_gate`, five forces, and `risk_density` to `PASS / CAUTION / SKIP / FILTERED_OUT / UNKNOWN`.
- [x] `safety` block reaffirms paper-only and forbids final trade-decision semantics.

## Validation Command

Executed:

```bash
python3 - <<'PY'
import json
from pathlib import Path
p=Path('rules/entry_five_forces_rules_v1.json')
data=json.load(p.open())
required={'schema_version','basic_gate','forces','risk_density','entry_aux_decision','safety'}
missing=required-set(data)
assert not missing, missing
assert {'absorption_power','diffusion_power','control_power','camouflage_power','exit_power'} <= set(data['forces'])
for k in ['min_liquidity','min_market_cap','min_volume','min_holder_count','min_swaps']:
    assert k in data['basic_gate']['thresholds'], k
print('json_ok')
print('top_keys', sorted(data.keys()))
PY
```

Result:

```text
json_ok
top_keys ['basic_gate', 'basis', 'entry_aux_decision', 'forces', 'owner_skill', 'phase', 'risk_density', 'rule_set', 'safety', 'schema_version', 'source_documents']
```

## One-Page Rationale Per Threshold Group

### 1. Basic Gate Thresholds

The basic gate answers only one question: whether a candidate token has enough market thickness to justify running the full S02-S06 workflow.

Configured thresholds:

- `min_liquidity = 50000 USD`
- `min_market_cap = 50000 USD`
- `min_volume = 10000 USD in 1h or closest available window`
- `min_holder_count = 100`
- `min_swaps = 100 in 1h or closest available window`

Rationale:

- Liquidity below 50k means a small trade can dominate price, so wallet-structure analysis can become misleading.
- Market cap below 50k is usually a noise zone where one wallet can distort the candidate.
- Volume and swaps provide activity samples; without activity, the system cannot distinguish broad participation from isolated wallet behavior.
- Holder count below 100 means distribution has not formed, so top-holder concentration and wallet-role logic are fragile.

Decision semantics:

- Missing critical fields ⇒ `UNKNOWN`
- Any minimum threshold failure ⇒ `FILTERED_OUT`
- All thresholds satisfied ⇒ `PASS`

This gate is not a final strategy decision. It only controls whether the candidate deserves deeper analysis.

### 2. Absorption Power

Absorption Power measures whether the market can absorb buying and selling pressure.

Source fields include:

- `liquidity`
- `pool.liquidity`
- `market_cap`
- `usd_market_cap`
- `volume_*`
- `buy_volume_*`
- `net_buy_24h`
- pool reserve values

Classification:

- `unknown`: liquidity or market cap missing
- `weak`: liquidity / market cap / liquidity-market-cap ratio too low
- `normal`: minimum depth exists
- `strong`: strong liquidity, market cap, and volume-liquidity relation

Rationale:

Meme tokens without sufficient absorption become noise-dominated. High heat without sufficient pool depth can become thin-pump behavior. Absorption is positive, but it is not a buy signal.

### 3. Diffusion Power

Diffusion Power measures whether participation spreads beyond a few actors.

Source fields include:

- `holder_count`
- `swaps_*`
- `buys_*`
- `sells_*`
- `volume`
- `smart_degen_count`
- `renowned_count`
- `bluechip_owner_percentage`
- `hot_level`
- `rank`
- social presence fields

Classification:

- `unknown`: holder or swaps missing
- `weak`: too few holders/swaps or suspiciously high swaps-per-holder
- `growing`: participation forming
- `broad`: broad activity with meaningful holder and swap base

Rationale:

Diffusion is a positive force, but GMGN tags and heat/rank are hints only. They can support the diffusion story but must never hard-gate by themselves.

### 4. Control Power

Control Power measures whether supply or activity may be dominated by a small set of actors.

Source fields include:

- `top_10_holder_rate`
- dev/creator hold rates
- suspected insider hold rate
- sniper fields
- bundler fields
- whale fields
- holder `amount_percentage`
- holder `native_transfer.address`

Classification:

- `unknown`: concentration fields missing
- `low`: concentration and bundler/sniper indicators low
- `medium`: moderate concentration or bundler/sniper presence
- `high`: high top-holder, bundler, sniper, or suspected-insider concentration

Rationale:

Control Power is a negative force. It helps decide caution or skip, but it cannot claim confirmed controller, confirmed insider, or confirmed庄家.

### 5. Camouflage Power

Camouflage Power measures how forgeable the apparent heat, volume, or narrative shell may be.

Source fields include:

- `is_wash_trading`
- bot/fresh wallet rates
- social verification
- dev social history
- DexScreener ad/boost/trending fields
- heat/rank fields

Classification:

- `unknown`: camouflage fields missing
- `low`: no obvious wash/bot/fresh-wallet density
- `medium`: wash, bot, fresh-wallet, or paid-attention hint
- `high`: wash trading combined with bot/fresh-wallet/social instability

Rationale:

Many meme-market signals can be manufactured. Camouflage Power reduces confidence in volume, heat, and narrative signals. It is not a final fraud verdict.

### 6. Exit Power

Exit Power measures whether early actors have both the capacity and incentive to exit into later participants.

Source fields include:

- holder sell percentage
- realized/unrealized profit
- avg cost / avg sold
- creator status and close flag
- top-holder concentration
- liquidity/market-cap relation
- rat/bundler trader rates
- sell volume and short-window price changes

Classification:

- `unknown`: exit fields missing
- `low`: low concentration and sufficient liquidity relation
- `medium`: concentration, weak liquidity, creator close, or sell-pressure hints
- `high`: high concentration, weak exit liquidity, rat/bundler pressure, or creator closed

Rationale:

Exit Power is a negative force because later participants can become exit liquidity for earlier actors. This is not a sell command; it only informs entry-layer screening.

### 7. Risk Density

Risk Density aggregates GMGN risk hints into a 0.0-1.0 score.

Weighted contributions include:

- unrenounced mint: 0.20
- unrenounced freeze: 0.20
- high rug ratio: 0.20
- wash trading: 0.15
- high bundler density: 0.12
- top10 concentration: 0.10
- creator exit: 0.08
- bot/fresh wallet density: 0.08

Level edges:

- `low`: 0.00-0.25
- `medium`: 0.25-0.50
- `high`: 0.50-0.75
- `extreme`: 0.75-1.00
- `unknown`: no risk-density fields available

Rationale:

A single GMGN risk hint may be noisy, but multiple simultaneous hints create risk density. This is still GMGN-layer hinting, not final chain proof.

### 8. Entry Auxiliary Decision

Decision mapping order:

1. `FILTERED_OUT`
2. `UNKNOWN`
3. `SKIP`
4. `CAUTION`
5. `PASS`

Rules:

- `FILTERED_OUT`: basic gate failed; `next_action=STOP`
- `UNKNOWN`: critical data missing; run full workflow with caution if manually requested
- `SKIP`: high/extreme risk density or high negative force; batch skip only with explicit flag
- `CAUTION`: medium risk or weak positive force
- `PASS`: basic gate passes, positive forces adequate, negative forces not high

Rationale:

The entry auxiliary decision controls resource allocation and warning level. It does not replace S06 `meme-trade-gate.gate_decision`.

## Safety Review

No code was modified.
No thresholds were embedded in Python source.
No live trading, swap, signing, broadcast, private-key, cooking, or auto deploy behavior was added.

Forbidden semantics preserved:

- `PASS` is not a buy signal
- `SKIP` is not a final fraud verdict
- `FILTERED_OUT` is not a permanent token ban
- these thresholds are not final trade decisions

## Next Task

Next dependency in the ai-pro-dev-workflow chain:

```text
TASK-SCHEMA-003 — Extend meme-candidate-entry schema for Five-Forces Gate output
```

`TASK-SCHEMA-003` can be unblocked after PM/review records this task as `INTERNAL_PASS`.
