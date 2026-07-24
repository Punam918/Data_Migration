# Phase 5 — Transformation Layer (Bronze → Silver → Gold)

## Goal
Build deterministic transformation pipelines to standardize, model, and publish curated datasets.

## Scope
- Bronze to silver normalization
- Silver to gold business modeling
- Partitioning and incremental merge strategy
- Data contracts for gold outputs

## Key Tasks
- Create `src/migration_platform/pipelines/transforms` and `src/migration_platform/contracts`
- Add declarative transform specs per dataset (cast rules, null/default rules, renames, derived cols)
- Implement reusable operators (casting, normalization, date parsing)
- Implement layer writers: `write_silver`, `write_gold` with partitioning
- Add contract validation and fail-fast promotion
- Build E2E pipeline for a sample dataset (orders)

## Deliverables
- Transform modules and dataset specs
- Silver/gold writers and contract validator
- Unit + integration tests for one dataset

## Exit Criteria
- One dataset reproducibly runs from bronze → gold
- Contract violations block gold publish

## Risks
- Silent schema drift — mitigate with strict casts and schema diffs
