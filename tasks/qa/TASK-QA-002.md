# Task Card

task_id: TASK-QA-002
title: Create fixture matrix skeleton
owner_terminal: qa-ci
status: READY

## Input Files
- `docs/specs.md`
- `docs/acceptance.md`
- `design/工程完善计划书.md`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`

## Allowed Write Paths
- `fixtures/README.md`
- `fixtures/场景01-正常通过.json`
- `fixtures/场景02-蜜罐拦截.json`
- `fixtures/场景03-结构风险高.json`
- `fixtures/场景04-数据缺失.json`
- `fixtures/场景05-信号冲突.json`
- `reports/TASK-QA-002/result.md`

## Forbidden
- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Change unrelated files
- Expand scope
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, or auto deploy

## Acceptance Criteria
- [ ] fixtures cover BLOCK / WATCH / PAPER_ONLY / NEED_MORE_DATA
- [ ] fixtures are mock data, not real token recommendations
- [ ] JSON files parse with python json.load
- [ ] result.md written

## Dependencies
- none

## Blocked By
- none

## Failure / Work Details
Create skeleton fixtures sufficient for future tests. Do not use live trading data.

