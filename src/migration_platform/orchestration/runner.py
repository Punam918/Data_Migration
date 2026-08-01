from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from migration_platform.governance.patcher import PatchManager
from migration_platform.llm.explainer import IncidentExplainer, IncidentReport
from migration_platform.metadata.mapping_loader import MappingSpec
from migration_platform.ml.anomaly import TableAnomalyDetector
from migration_platform.observability.alerts import AlertManager
from migration_platform.observability.lineage import LineageStore
from migration_platform.observability.metrics import MetricEmitter
from migration_platform.pipelines.transformation import TransformationPipeline
from migration_platform.quality.checks import CheckResult, run_quality_suite


@dataclass
class OrchestrationResult:
    transformed_rows: int
    quality_results: List[CheckResult]
    incident_report: IncidentReport
    suggested_patches: List[Dict[str, Any]]


class OrchestrationRunner:
    """Runs transform, quality checks, anomaly detection, and incident reporting."""

    def __init__(self) -> None:
        self.transformer = TransformationPipeline()
        self.detector = TableAnomalyDetector()
        self.explainer = IncidentExplainer()
        root = Path("./var/observability")
        self.metrics = MetricEmitter(root)
        self.lineage = LineageStore(root)
        self.alerts = AlertManager(root)
        gov_root = Path("./var/governance")
        self.patch_mgr = PatchManager(gov_root)

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

        # Emit basic metrics
        self.metrics.emit(
            "transformed_rows",
            float(len(transformed)),
            tags={"mapping": mapping.mapping_name},
        )
        for chk in quality:
            self.metrics.emit(
                "quality_check",
                1.0 if chk.passed else 0.0,
                tags={"mapping": mapping.mapping_name, "check": chk.check_name},
            )

        anomalies_count = sum(1 for a in anomaly_scores if a.is_anomaly)
        self.metrics.emit(
            "anomalies_count",
            float(anomalies_count),
            tags={"mapping": mapping.mapping_name},
        )

        # Capture lineage
        src_table = getattr(mapping.source, "table", "unknown") or "unknown"
        tgt_table = getattr(mapping.target, "table", "unknown") or "unknown"
        self.lineage.add(
            dataset=mapping.mapping_name,
            operation="transform",
            inputs=[src_table],
            outputs=[tgt_table],
            metadata={"rows": len(transformed)},
        )

        # Create alerts for failed quality checks or anomalies and suggest patches
        suggested: List[Dict[str, Any]] = []

        for chk in quality:
            if not chk.passed:
                self.alerts.create_alert(
                    name=f"quality:{chk.check_name}",
                    severity="high",
                    message=chk.details,
                    metadata={"mapping": mapping.mapping_name},
                )

                # Suggest governance patches for common failures
                try:
                    if chk.check_name == "unique_key":
                        title = f"add-unique-constraint-{mapping.mapping_name}"
                        desc = (
                            f"Suggest adding unique constraint on {mapping.primary_key} "
                            f"for mapping {mapping.mapping_name}"
                        )
                        patch_meta_unique: Dict[str, Any] = {
                            "mapping": mapping.mapping_name,
                            "type": "unique_constraint",
                            "columns": mapping.primary_key,
                        }
                        rec_unique = self.patch_mgr.suggest_patch(
                            title, desc, metadata=patch_meta_unique
                        )
                        suggested.append(asdict(rec_unique))
                    elif chk.check_name == "null_rate":
                        # Parse the column from details strings like
                        # "column=colname, null_rate=0.1234".
                        parts = chk.details.split(",")
                        col = None
                        for p in parts:
                            if p.strip().startswith("column="):
                                col = p.split("=", 1)[1].strip()
                                break
                        title = f"backfill-or-notnull-{mapping.mapping_name}-{col or 'unknown'}"
                        desc = (
                            f"Suggest backfilling or enforcing NOT NULL on column {col} "
                            f"for mapping {mapping.mapping_name}"
                        )
                        patch_meta_not_null: Dict[str, Any] = {
                            "mapping": mapping.mapping_name,
                            "type": "not_null",
                            "column": col,
                        }
                        rec_not_null = self.patch_mgr.suggest_patch(
                            title, desc, metadata=patch_meta_not_null
                        )
                        suggested.append(asdict(rec_not_null))
                except Exception:
                    # non-fatal if patch suggestion fails
                    pass

        if anomalies_count > 0:
            self.alerts.create_alert(
                name="anomaly:detection",
                severity="medium",
                message=f"{anomalies_count} anomalies detected",
                metadata={"mapping": mapping.mapping_name, "anomalies": anomalies_count},
            )
            try:
                title = f"investigate-anomalies-{mapping.mapping_name}"
                desc = (
                    f"Investigate {anomalies_count} anomalies detected for mapping "
                    f"{mapping.mapping_name}"
                )
                patch_meta_investigation: Dict[str, Any] = {
                    "mapping": mapping.mapping_name,
                    "type": "investigation",
                    "anomalies": anomalies_count,
                }
                rec_investigation = self.patch_mgr.suggest_patch(
                    title, desc, metadata=patch_meta_investigation
                )
                suggested.append(asdict(rec_investigation))
            except Exception:
                pass

        return OrchestrationResult(
            transformed_rows=len(transformed),
            quality_results=quality,
            incident_report=report,
            suggested_patches=suggested,
        )
