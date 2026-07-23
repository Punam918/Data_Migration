from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from migration_platform.llm.explainer import IncidentExplainer, IncidentReport
from migration_platform.metadata.mapping_loader import MappingSpec
from migration_platform.ml.anomaly import TableAnomalyDetector
from migration_platform.pipelines.transformation import TransformationPipeline
from migration_platform.quality.checks import CheckResult, run_quality_suite


@dataclass
class OrchestrationResult:
    transformed_rows: int
    quality_results: list[CheckResult]
    incident_report: IncidentReport


class OrchestrationRunner:
    """Runs transform, quality checks, anomaly detection, and incident reporting."""

    def __init__(self) -> None:
        self.transformer = TransformationPipeline()
        self.detector = TableAnomalyDetector()
        self.explainer = IncidentExplainer()

    def execute(self, frame: pd.DataFrame, mapping: MappingSpec) -> OrchestrationResult:
        transformed = self.transformer.transform(frame, mapping)
        quality = run_quality_suite(
            transformed,
            min_rows=1,
            null_checks={
                col: 0.1
                for col in transformed.columns[: min(3, len(transformed.columns))]
            },
            key_columns=mapping.primary_key,
        )

        self.detector.fit(transformed)
        anomaly_scores = self.detector.score(transformed)
        report = self.explainer.build_report(mapping.mapping_name, quality, anomaly_scores)

        return OrchestrationResult(
            transformed_rows=len(transformed),
            quality_results=quality,
            incident_report=report,
        )
