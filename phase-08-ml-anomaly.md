# Phase 8 — ML Anomaly Detection

## Goal
Detect subtle data issues beyond static rules using ML models.

## Scope
- Feature engineering from run stats
- Baseline model training and scoring
- Explanations for anomalies

## Key Tasks
- Define run-level features (null rates, percentiles, unique counts, volume deltas)
- Train baseline models from historical run metadata
- Persist models and integrate scoring in pipeline
- Emit anomaly records with explanation fields

## Deliverables
- Training + scoring modules
- Model registry entries
- Anomaly results artifacts

## Exit Criteria
- Model detects representative drift incidents with acceptable FP rate
