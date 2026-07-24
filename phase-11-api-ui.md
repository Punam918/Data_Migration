# Phase 11 — API, UI & Analyst Experience

## Goal
Expose platform insights and controls via APIs and a usable UI for analysts.

## Scope
- Backend APIs: runs, quality, anomalies, lineage, incidents
- Dashboard for pipeline and dataset health
- Natural-language assistant endpoint for diagnostics

## Key Tasks
- Implement FastAPI endpoints for run status, quality, anomaly, lineage
- Build dashboard views (health overview, dataset drilldown, incident detail)
- Add assistant endpoint with retrieval-backed responses
- Capture analyst feedback for model/LLM improvement

## Deliverables
- API contracts and dashboard MVP
- Assistant endpoint and feedback pipeline

## Exit Criteria
- Analysts can self-serve common diagnostics without engineering help
- API response times meet SLAs for dashboard queries
