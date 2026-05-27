# Pytest Failure Attribution — Baseline 2026-05-25

## Baseline
Command: `pytest -q`
Observed before task execution: 8 failed, 5 passed.

## Root Cause Class A — pytest import collision
Multiple skill test files used `from run import run` while inserting different `skills/*/scripts` dirs into `sys.path`. In a single pytest process, Python reused the first loaded `run` module, causing unrelated skill tests to execute `meme-candidate-entry` or other stale run modules. This explains the false failures where token-panel/trade-gate/wallet-structure/evidence-chain targeted tests passed in isolation but failed in the full suite.

Mapped task: `TASK-QA-001` fixed test import isolation by loading each skill `run.py` via `importlib.util.spec_from_file_location`.

## Failure Mapping
- `skills/meme-token-panel/tests/test_token_panel.py::test_token_panel_pass` → import collision false failure; targeted test passed before code changes. Related card: `TASK-BE-001`, closed as no backend code change needed.
- `skills/meme-token-panel/tests/test_token_panel.py::test_token_panel_honeypot_block` → import collision false failure; targeted test passed before code changes. Related card: `TASK-BE-001`, closed as no backend code change needed.
- `skills/meme-trade-gate/tests/test_trade_gate.py::test_trade_gate_paper_only` → import collision false failure; targeted test passed before code changes. Related card: `TASK-BE-002`, closed as no backend code change needed.
- `skills/meme-trade-gate/tests/test_trade_gate.py::test_trade_gate_honeypot_block` → import collision false failure; targeted test passed before code changes. Related card: `TASK-BE-002`, closed as no backend code change needed.
- `skills/meme-wallet-roles/tests/test_wallet_roles.py::test_wallet_roles_pass` → import collision false failure; full-suite imported `meme-candidate-entry` run. Related card: `TASK-BE-003`; import isolation should resolve before backend changes.
- `skills/meme-wallet-structure/tests/test_wallet_structure.py::test_wallet_structure_high_risk` → import collision false failure; targeted task should be rechecked after import isolation. Related card: `TASK-BE-004`.
- `skills/meme-wallet-structure/tests/test_wallet_structure_exclusions.py::test_wallet_structure_excludes_pool_address_from_concentration` → import collision false failure; targeted task should be rechecked after import isolation. Related card: `TASK-BE-004`.
- `skills/meme-evidence-chain/tests/test_evidence_chain.py::test_evidence_chain_accumulation` → import collision false failure; targeted task should be rechecked after import isolation. Related card: `TASK-BE-005`.

## Recommendation
Run `pytest -q` after import isolation. If remaining failures exist, treat them as real backend contract issues and execute corresponding task cards.
