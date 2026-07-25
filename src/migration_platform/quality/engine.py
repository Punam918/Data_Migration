from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import pandas as pd

from migration_platform.quality.checks import CheckResult, check_min_rows, check_null_rate, check_unique_key


@dataclass
class QualityRule:
    name: str
    func: Callable[[pd.DataFrame], CheckResult]
    severity: str = "error"


class QualityEngine:
    """Register and run quality rules against a DataFrame."""

    def __init__(self) -> None:
        self.rules: List[QualityRule] = []

    def register(self, rule: QualityRule) -> None:
        self.rules.append(rule)

    def run(self, frame: pd.DataFrame) -> List[CheckResult]:
        results: List[CheckResult] = []
        for r in self.rules:
            try:
                res = r.func(frame)
            except Exception as err:
                results.append(CheckResult(check_name=r.name, passed=False, details=str(err)))
                continue
            results.append(res)
        return results


# Helper factory functions for common rules
def rule_min_rows(minimum: int) -> QualityRule:
    return QualityRule(name=f"min_rows_{minimum}", func=lambda df: check_min_rows(df, minimum), severity="error")


def rule_null_rate(column: str, max_null_rate: float) -> QualityRule:
    return QualityRule(name=f"null_rate_{column}", func=lambda df: check_null_rate(df, column, max_null_rate), severity="error")


def rule_unique_key(columns: List[str]) -> QualityRule:
    return QualityRule(name=f"unique_key_{'_'.join(columns)}", func=lambda df: check_unique_key(df, columns), severity="error")
