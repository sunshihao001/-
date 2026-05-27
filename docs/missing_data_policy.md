# Missing Data / Downgrade Policy

## Purpose

This policy turns `missing_fields` and `downgrade_reasons` from loose text into recoverable state.

## Severity Levels

- `low`: output can continue; confidence is reduced.
- `medium`: output can continue only with explicit downgrade and review condition.
- `high`: output should become `NEED_MORE_DATA` unless downstream has enough counter-evidence.
- `critical`: output must stop or gate to `BLOCK` / `NEED_MORE_DATA`.

## Required Semantics

Every missing-data case should preserve:

```json
{
  "missing_field": "<json path or input name>",
  "source_skill": "<skill>",
  "source_command": "<gmgn command or upstream file>",
  "severity": "low | medium | high | critical",
  "recovery_action": "<rerun/refresh/manual review>",
  "decision_impact": "<confidence cap / WATCH cap / NEED_MORE_DATA>"
}
```

Current v1 implementation stores this primarily through:

- `rules/downgrade_rules_v1.json`
- skill output `missing_fields`
- skill output `downgrade_reasons`
- trade gate `next_review_conditions`

## Skill Mapping

- `meme-candidate-entry`: token info / pool / liquidity absence can block or downgrade candidate entry.
- `meme-token-panel`: missing kline/social/holder/security fields lowers confidence and may cap downstream gate.
- `meme-wallet-roles`: unavailable holder list or portfolio stats means wallet roles may be `UNABLE_TO_CLASSIFY` or downgraded.
- `meme-wallet-structure`: missing funding source or timing data caps structure confidence.
- `meme-evidence-chain`: conflicting signals or weak evidence lowers confidence and may return `NEED_MORE_DATA`.
- `meme-trade-gate`: critical missing evidence should return `NEED_MORE_DATA`; low confidence caps to `WATCH`.
- `meme-workflow-controller`: stale phase output should be refreshed before final summary when possible.

## Recovery Rules

- Stale data: rerun stale phase before final gate when safe.
- Missing non-critical optional data: continue with downgrade reason.
- Missing structure-critical fields: continue only with confidence cap or `NEED_MORE_DATA`.
- Upstream `ERROR`: gate must return `NEED_MORE_DATA` or stop.
- Upstream `BLOCK`: inherit `BLOCK`.

## Safety Boundary

Missing data never authorizes live trading, swap, private key access, signing, transaction broadcast, or auto deploy.
