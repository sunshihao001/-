# Task Card

task_id: TASK-STATE-001
title: Deepen controller stale/resume/force_refresh/blocker_report behavior
owner_terminal: skill-backend
status: READY

## Input Files
- `skills/meme-workflow-controller/scripts/run.py`
- `skills/common/phase_state.py`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`

## Allowed Write Paths
- `skills/meme-workflow-controller/scripts/run.py`
- `skills/common/phase_state.py`
- `tests/test_controller_state_deepening.py`
- `reports/TASK-STATE-001/result.md`

## Forbidden
- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Change unrelated files
- Expand scope beyond this task card
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, cooking, or auto deploy

## Acceptance Criteria
- [ ] BLOCK/ERROR writes blocker_report.md
- [ ] force_refresh records reset reason
- [ ] resume_from respects missing prior phases
- [ ] stale phase metadata is exposed
- [ ] Full pytest passes

## Dependencies
- rules / fixtures / validators baseline exists.

## Blocked By
- none
