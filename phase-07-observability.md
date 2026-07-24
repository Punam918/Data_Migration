# Phase 7 — Observability, Lineage & Incident Signals

## Goal
Provide visibility into pipeline/data health with actionable alerts and lineage.

## Scope
- Metrics: run duration, throughput, failure rate, freshness
- Lineage capture at table and transform level
- Alert policies for SLA breaches, quality drops, anomaly spikes

## Key Tasks
- Implement metrics emitter
- Persist lineage metadata for datasets and transforms
- Create alert definitions and incident timeline
- Build minimal dashboard endpoints for ops

## Deliverables
- Metrics + lineage modules
- Alerting rules and dashboard endpoints

## Exit Criteria
- Failed run diagnosis available via metrics + lineage
- Alerts trigger on synthetic failure tests
