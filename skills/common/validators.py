from __future__ import annotations

from datetime import datetime
from typing import Any

from .file_io import save_json

STANDARD_REQUIRED_FIELDS = [
    'schema_version',
    'skill_name',
    'task_id',
    'token_address',
    'chain',
    'timestamp',
    'status',
    'evidence',
    'counter_evidence',
    'confidence_score',
    'downgrade_reasons',
    'blocker_reasons',
    'missing_fields',
    'valid_until',
    'next_action',
    'handoff_to',
]

VALID_STATUS = {'PASS', 'WARN', 'BLOCK', 'ERROR', 'NEED_MORE_DATA'}
PHASE1_GATE_DECISIONS = {'BLOCK', 'WATCH', 'PAPER_ONLY', 'NEED_MORE_DATA'}


def validate_skill_output(output: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(output, dict):
        return ['output must be a dict']

    for field in STANDARD_REQUIRED_FIELDS:
        if field not in output:
            errors.append(f'missing required field: {field}')

    if output.get('schema_version') != '1.0':
        errors.append('schema_version must be 1.0')
    if output.get('chain') != 'sol':
        errors.append('chain must be sol')
    if output.get('status') not in VALID_STATUS:
        errors.append(f'status must be one of {sorted(VALID_STATUS)}')

    for field in ['evidence', 'counter_evidence', 'downgrade_reasons', 'blocker_reasons', 'missing_fields']:
        if field in output and not isinstance(output[field], list):
            errors.append(f'{field} must be a list')

    confidence = output.get('confidence_score')
    if confidence is not None:
        try:
            c = float(confidence)
            if not 0.0 <= c <= 1.0:
                errors.append('confidence_score must be between 0 and 1')
        except Exception:
            errors.append('confidence_score must be numeric')

    for field in ['timestamp', 'valid_until']:
        if field in output:
            try:
                datetime.fromisoformat(str(output[field]).replace('Z', '+00:00'))
            except Exception:
                errors.append(f'{field} must be ISO-8601 parseable')

    return errors


def validate_trade_gate_output(output: dict[str, Any]) -> list[str]:
    errors = validate_skill_output(output)
    for field in ['gate_decision', 'decision_reasons', 'gate_score', 'phase_permission', 'next_review_conditions']:
        if field not in output:
            errors.append(f'missing trade gate field: {field}')

    if output.get('gate_decision') not in PHASE1_GATE_DECISIONS:
        errors.append('gate_decision must be Phase 1 decision: BLOCK/WATCH/PAPER_ONLY/NEED_MORE_DATA')

    if 'decision_reasons' in output and not isinstance(output['decision_reasons'], list):
        errors.append('decision_reasons must be a list')
    if 'next_review_conditions' in output and not isinstance(output['next_review_conditions'], list):
        errors.append('next_review_conditions must be a list')
    if 'gate_score' in output and not isinstance(output['gate_score'], dict):
        errors.append('gate_score must be a dict')
    if 'phase_permission' in output:
        pp = output['phase_permission']
        if not isinstance(pp, dict):
            errors.append('phase_permission must be a dict')
        else:
            if pp.get('semi_auto_allowed') is not False:
                errors.append('phase_permission.semi_auto_allowed must be false in Phase 1')
            if pp.get('auto_allowed') is not False:
                errors.append('phase_permission.auto_allowed must be false in Phase 1')
    return errors


def validate_controller_summary(summary: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ['schema_version', 'skill_name', 'token_address', 'timestamp', 'workflow_status', 'gate_decision', 'summary_file', 'next_action', 'forbidden']
    for field in required:
        if field not in summary:
            errors.append(f'missing controller summary field: {field}')
    if summary.get('skill_name') != 'meme-workflow-controller':
        errors.append('skill_name must be meme-workflow-controller')
    if summary.get('gate_decision') not in PHASE1_GATE_DECISIONS:
        errors.append('gate_decision must be Phase 1 decision')
    if 'forbidden' in summary and not isinstance(summary['forbidden'], list):
        errors.append('forbidden must be a list')
    return errors


def save_validated_json(output: dict[str, Any], path) -> str:
    errors = validate_controller_summary(output) if output.get('skill_name') == 'meme-workflow-controller' else (
        validate_trade_gate_output(output) if output.get('skill_name') == 'meme-trade-gate' else validate_skill_output(output)
    )
    if errors:
        raise AssertionError('; '.join(errors))
    return save_json(output, path)


def assert_valid_skill_output(output: dict[str, Any]) -> None:
    errors = validate_trade_gate_output(output) if output.get('skill_name') == 'meme-trade-gate' else validate_skill_output(output)
    if errors:
        raise AssertionError('; '.join(errors))
