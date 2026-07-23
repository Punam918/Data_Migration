from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class CheckResult:
    check_name: str
    passed: bool
    details: str


def check_min_rows(frame: pd.DataFrame, minimum: int) -> CheckResult:
    count = len(frame)
    passed = count >= minimum
    return CheckResult(
        check_name="min_rows",
        passed=passed,
        details=f"rows={count}, minimum={minimum}",
    )


def check_null_rate(frame: pd.DataFrame, column: str, max_null_rate: float) -> CheckResult:
    if column not in frame.columns:
        return CheckResult("null_rate", False, f"missing_column={column}")

    null_rate = float(frame[column].isna().mean())
    passed = null_rate <= max_null_rate
    return CheckResult(
        check_name="null_rate",
        passed=passed,
        details=f"column={column}, null_rate={null_rate:.4f}, max={max_null_rate:.4f}",
    )


def check_unique_key(frame: pd.DataFrame, key_columns: list[str]) -> CheckResult:
    missing = [c for c in key_columns if c not in frame.columns]
    if missing:
        return CheckResult("unique_key", False, f"missing_columns={','.join(missing)}")

    duplicates = int(frame.duplicated(subset=key_columns).sum())
    passed = duplicates == 0
    return CheckResult(
        check_name="unique_key",
        passed=passed,
        details=f"key={key_columns}, duplicates={duplicates}",
    )


def run_quality_suite(
    frame: pd.DataFrame,
    min_rows: int,
    null_checks: dict[str, float],
    key_columns: list[str],
) -> list[CheckResult]:
    results: list[CheckResult] = [check_min_rows(frame, min_rows)]
    for column, threshold in null_checks.items():
        results.append(check_null_rate(frame, column, threshold))
    results.append(check_unique_key(frame, key_columns))
    return results
