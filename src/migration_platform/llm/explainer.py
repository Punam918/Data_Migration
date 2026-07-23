from __future__ import annotations

from dataclasses import dataclass

from migration_platform.ml.anomaly import AnomalyScore
from migration_platform.quality.checks import CheckResult


@dataclass
class IncidentReport:
    title: str
    summary: str
    suggested_actions: list[str]


class IncidentExplainer:
    """Placeholder interface for future LLM-backed incident explanations."""

    def build_report(
        self,
        dataset_name: str,
        quality_results: list[CheckResult],
        anomaly_scores: list[AnomalyScore],
    ) -> IncidentReport:
        failed_checks = [r for r in quality_results if not r.passed]
        anomaly_count = sum(1 for a in anomaly_scores if a.is_anomaly)

        summary = (
            f"Dataset={dataset_name}; failed_checks={len(failed_checks)}; "
            f"anomalies={anomaly_count}."
        )

        actions: list[str] = []
        if failed_checks:
            actions.append("Review failed quality checks and quarantine affected rows.")
        if anomaly_count > 0:
            actions.append("Inspect anomaly rows and compare against prior partition statistics.")
        if not actions:
            actions.append("No immediate remediation required.")

        return IncidentReport(
            title=f"Incident summary for {dataset_name}",
            summary=summary,
            suggested_actions=actions,
        )
