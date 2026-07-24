import pandas as pd
from pathlib import Path

from migration_platform.pipelines.transforms.operators import cast_columns, apply_defaults, normalize_strings, derive_columns
from migration_platform.contracts.validator import ContractSpec, ContractViolation
from migration_platform.pipelines.writers import write_silver, write_gold


def test_transform_and_contract(tmp_path: Path) -> None:
    df = pd.DataFrame({
        "order_id": ["1", "2"],
        "customer_id": ["100", "101"],
        "amount": ["10.5", None],
        "note": ["  hello ", None],
    })

    casts = {"order_id": "int64", "customer_id": "int64", "amount": "float64"}
    defaults = {"amount": 0.0, "note": ""}

    df2 = cast_columns(df, casts)
    df3 = apply_defaults(df2, defaults)
    df4 = normalize_strings(df3, ["note"])
    df5 = derive_columns(df4, {"amount_with_tax": lambda d: d["amount"] * 1.1})

    # Contract: required columns and unique key
    spec = ContractSpec(required=["order_id", "customer_id"], unique_keys=["order_id"], dtypes={"amount": "float64"})
    spec.validate(df5)

    root = tmp_path / "out"
    silver_path = write_silver(df5, root, "orders")
    gold_path = write_gold(df5, root, "orders")

    assert silver_path.exists()
    assert gold_path.exists()


def test_contract_violation_missing(tmp_path: Path) -> None:
    df = pd.DataFrame({"a": [1]})
    spec = ContractSpec(required=["b"]) 
    try:
        spec.validate(df)
        assert False
    except ContractViolation:
        assert True
