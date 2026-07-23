from __future__ import annotations

import argparse
from pathlib import Path

from migration_platform.config import load_config
from migration_platform.pipelines.checkpointing import JsonCheckpointStore
from migration_platform.pipelines.connectors import PostgresTableConnector
from migration_platform.pipelines.ingestion import IngestionPipeline


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run incremental ingestion into bronze storage")
    parser.add_argument("--config", default="configs/app.example.yaml", help="Path to app config")
    parser.add_argument("--dataset", required=True, help="Dataset name under bronze directory")
    parser.add_argument("--connection-url", required=True, help="SQLAlchemy connection URL")
    parser.add_argument("--table", required=True, help="Source table name")
    parser.add_argument("--cursor-column", required=True, help="Incremental cursor column")
    parser.add_argument("--limit", type=int, default=10000, help="Max rows per run")
    parser.add_argument(
        "--columns",
        default="",
        help="Comma-separated source columns. Empty means select all.",
    )
    parser.add_argument(
        "--extra-where",
        default=None,
        help="Additional SQL predicate, example: is_deleted = false",
    )
    parser.add_argument("--run-id", default=None, help="Optional idempotent run identifier")
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    config = load_config(args.config)
    bronze_path = Path(config.storage.bronze_path)
    checkpoint_store = JsonCheckpointStore(bronze_path / "_checkpoints")

    columns = [c.strip() for c in args.columns.split(",") if c.strip()] or None

    connector = PostgresTableConnector(
        connection_url=args.connection_url,
        table_name=args.table,
        cursor_column=args.cursor_column,
        selected_columns=columns,
        extra_where=args.extra_where,
    )

    pipeline = IngestionPipeline(bronze_root=bronze_path)
    result = pipeline.ingest_incremental(
        dataset_name=args.dataset,
        connector=connector,
        checkpoint_store=checkpoint_store,
        batch_size=args.limit,
        run_id=args.run_id,
    )

    print("status={0}".format(result.status))
    print("rows={0}".format(result.row_count))
    print("snapshot={0}".format(result.snapshot_path))
    print("manifest={0}".format(result.manifest_path))
    print("cursor_start={0}".format(result.cursor_start))
    print("cursor_end={0}".format(result.cursor_end))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
