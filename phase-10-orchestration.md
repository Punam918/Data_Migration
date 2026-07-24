# Phase 10 — Orchestration, Approvals & Human-in-the-Loop

## Goal
Orchestrate the full pipeline, with approvals, replay, and rollback controls.

## Scope
- DAG orchestration across ingestion, transforms, quality, ML, LLM
- Approval gates for production-impacting actions
- Replay and rollback tooling

## Key Tasks
- Model DAG and implement orchestration jobs
- Add approval checkpoints and audit logs
- Implement replay controller and rollback to last good snapshot
- Define RBAC for operational actions

## Deliverables
- Orchestrated workflows and approval components
- Replay and rollback tooling

## Exit Criteria
- Replay and rollback tests pass in staging
- Approval paths enforce audit and least privilege
