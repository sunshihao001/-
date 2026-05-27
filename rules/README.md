# Rules v1

Authoritative machine-readable rules for Phase 1 safe-mode gate decisions.

- `gate_rules_v1.json`: BLOCK/WATCH/PAPER_ONLY/NEED_MORE_DATA gate contract from `design/phase1-skill-06-trade-gate.md`.
- `downgrade_rules_v1.json`: cross-skill downgrade and missing-data contract.

These files are contracts. Threshold changes require PM/review approval and a new freeze record or change request.

Safety: Phase 1 rules never authorize live trading, swap, signing, transaction broadcast, private key handling, or auto deploy.
