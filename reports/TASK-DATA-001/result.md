# Result

task_id: TASK-DATA-001
status: IMPLEMENTED

## Summary
Defined missing_fields / downgrade taxonomy with severity, recovery, and decision impact semantics.

## Files Changed
- docs/missing_data_policy.md
- `reports/TASK-DATA-001/result.md`

## Commands Run
- `pytest -q tests/test_rule_contracts.py tests/test_fixture_matrix_contract.py tests/test_skill_output_contracts.py -q`
- `python -m json.tool rules/gate_rules_v1.json`
- `python -m json.tool rules/downgrade_rules_v1.json`
- `pytest -q`

## Validation
- Targeted contract tests passed.
- Rule JSON files parse.
- Fixture JSON files parse.
- Full pytest passes: `22 passed in 0.08s`.

## Evidence
- Final verification output recorded in this session.

## Deviations
- None.

## Known Gaps
- Fixture contents are contract-grade skeletons; future work can make them executable end-to-end mock pipeline tests.

## Needs PM Clarification
- none
