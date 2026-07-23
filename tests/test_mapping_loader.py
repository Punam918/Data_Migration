from pathlib import Path

import pytest

from migration_platform.metadata.mapping_loader import load_mapping


def test_load_mapping_success() -> None:
    path = Path("configs/mappings/customer_orders.yaml")
    spec = load_mapping(path)

    assert spec.mapping_name == "customer_orders"
    assert "order_id" in spec.column_mappings


def test_load_mapping_missing_required(tmp_path: Path) -> None:
    content = """
mapping_name: bad_mapping
source:
  table: t1
target:
  table: t2
column_mappings:
  a: b
required_columns:
  - missing_col
"""
    file_path = tmp_path / "bad.yaml"
    file_path.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match="Required columns"):
        load_mapping(file_path)
