# Phase 6 — Data Quality & Reconciliation

## Goal
Implement a rule-driven quality engine and source-target reconciliation to ensure trust.

## Scope
- Quality rule registry and executor
- Reconciliation at partition/table level
- Quarantine path and run-level scoring

## Key Tasks
- Extend quality checks (row counts, null rates, uniqueness, referential integrity)
- Implement reconciliation service (counts, checksums, aggregates)
- Quarantine writer with reason codes and metadata
- Quality scoring and severity tags
- Integrate quality gate before gold publish

## Deliverables
- Rule engine and reconciliation reports
- Quarantine dataset
- Quality score artifact per run

## Exit Criteria
- Quality failures block promotion and generate actionable reports
