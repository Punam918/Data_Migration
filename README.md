# Self-Healing Migration Intelligence Platform

This repository implements the first production foundation for a combined data migration, data engineering, and ML/LLM intelligence system.

## What is included now
- Baseline project scaffolding for Phases 2 and 3
- Metadata and mapping registry modules
- Phase 4 incremental ingestion with connector + checkpoints + idempotent manifests
- Starter transformation and quality components
- ML anomaly detection baseline module
- LLM incident explanation interface
- FastAPI status endpoint
- CI workflow with lint and tests

## Quick start
1. Create a virtual environment:
   - Windows PowerShell: `python -m venv .venv; .\.venv\Scripts\Activate.ps1`
2. Install dependencies:
   - `pip install -e .[dev]`
3. Run tests:
   - `pytest`
4. Run API:
   - `uvicorn migration_platform.api.main:app --reload`

## Phase 4 incremental ingestion
- Connector: `PostgresTableConnector`
- Checkpoint store: JSON files under `artifacts/bronze/_checkpoints`
- Snapshot strategy: immutable `snapshot_<run_id>.csv` files in each dataset folder
- Idempotency: rerun with same `run_id` returns `idempotent_reuse` and avoids duplicate writes

Example run:
- `python scripts/run_ingestion.py --dataset orders --connection-url postgresql+psycopg://user:pass@host:5432/db --table public.orders --cursor-column order_id --limit 50000`

## Project layout
- `src/migration_platform`: core platform modules
- `configs`: app configuration templates and mapping specs
- `tests`: unit tests
- `.github/workflows`: CI automation

## Next implementation increment
- Add real source connector (e.g., Postgres)
- Add bronze/silver/gold file or table writers
- Integrate Great Expectations checks
- Add model training and scoring job orchestration
