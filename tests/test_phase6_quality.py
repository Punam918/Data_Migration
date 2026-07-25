import pandas as pd
from pathlib import Path

from migration_platform.quality.engine import QualityEngine, rule_min_rows, rule_null_rate, rule_unique_key
from migration_platform.quality.reconciliation import reconcile_counts, reconcile_keys_checksum
from migration_platform.quality.quarantine import QuarantineWriter


def test_quality_engine_and_quarantine(tmp_path: Path) -> None:
    df = pd.DataFrame({"id": [1, 2, 3], "x": [10, None, 30]})
    engine = QualityEngine()
    engine.register(rule_min_rows(2))
    engine.register(rule_null_rate("x", 0.2))
    engine.register(rule_unique_key(["id"]))

    results = engine.run(df)

    # min_rows passes, null_rate fails because 1/3 ~ 0.333 > 0.2
    assert any(r.check_name.startswith("min_rows") and r.passed for r in results)
    assert any(r.check_name.startswith("null_rate_x") and not r.passed for r in results)

    # Quarantine failing rows
    failing = df[df["x"].isna()]
    writer = QuarantineWriter(tmp_path / "quarantine")
    out = writer.write("dataset1", failing, reason="null_rate_fail")
    assert out.exists()


def test_reconciliation_counts_and_checksum() -> None:
    src = pd.DataFrame({"id": [1, 2, 3], "val": [10, 20, 30]})
    tgt = pd.DataFrame({"id": [1, 2], "val": [10, 20]})
    s, t, diff = reconcile_counts(src, tgt)
    assert s == 3 and t == 2 and diff == 1

    src2 = pd.DataFrame({"id": [1, 2], "val": [10, 20]})
    t_equal = pd.DataFrame({"id": [1, 2], "val": [10, 20]})
    s_hash, t_hash, ok = reconcile_keys_checksum(src2, t_equal, ["id"])
    assert ok is True
