# Self-Healing Migration Intelligence Platform

This repository implements the first production foundation for a combined data migration, data engineering, and ML/LLM intelligence system.

## What is included now
- Baseline project scaffolding for Phases 2 and 3
- Metadata and mapping registry modules
- Starter ingestion, transformation, and quality components
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
