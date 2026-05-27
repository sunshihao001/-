# Fixture Matrix

Mock-only fixture matrix for Solana Meme Workflow OS. These files are not trading recommendations and must not trigger live trading.

Each fixture includes:
- full `mock_inputs` GMGN response categories used by candidate/token/wallet skills
- `expected_outputs` for candidate_entry, token_panel, wallet_roles, wallet_structure, evidence_chain, trade_gate

Coverage:
- 场景01: PAPER_ONLY
- 场景02: BLOCK
- 场景03: WATCH
- 场景04: NEED_MORE_DATA with missing_fields and downgrade_reasons
- 场景05: WATCH with conflicting signals
