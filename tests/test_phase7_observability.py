
import pandas as pd

from migration_platform.metadata.mapping_loader import MappingSpec
from migration_platform.observability.alerts import AlertManager
from migration_platform.observability.lineage import LineageStore
from migration_platform.observability.metrics import MetricEmitter
from migration_platform.orchestration.runner import OrchestrationRunner


def test_observability_integration(tmp_path):
    # prepare var directory
    var_dir = tmp_path / "observability"
    var_dir.mkdir(parents=True)

    # small sample dataframe
    df = pd.DataFrame({"id": [1, 2, 3], "value": [10.0, 12.0, 11.0]})

    mapping_payload = {
        "mapping_name": "test_map",
        "source": {"system": "src_sys", "table": "src_table"},
        "target": {"system": "tgt_sys", "table": "tgt_table"},
        "column_mappings": {"id": "id", "value": "value"},
        "required_columns": ["id", "value"],
        "primary_key": ["id"],
    }
    mapping = MappingSpec.model_validate(mapping_payload)

    # run orchestration with var dir overridden by env-like behavior
    # instantiate runner and replace observability stores with test ones
    runner = OrchestrationRunner()
    runner.metrics = MetricEmitter(var_dir)
    runner.lineage = LineageStore(var_dir)
    runner.alerts = AlertManager(var_dir)

    result = runner.execute(df, mapping)

    # verify metrics
    metrics = runner.metrics.tail(100)
    assert any(m["name"] == "transformed_rows" and int(m["value"]) == len(df) for m in metrics)

    # verify lineage
    lineage = runner.lineage.tail(100)
    assert any(e.get("dataset") == "test_map" for e in lineage)

    # verify alerts file exists and has valid JSON lines (may be empty or contain alerts)
    alerts = runner.alerts.tail(100)
    assert isinstance(alerts, list)

    # basic result structure
    assert result.transformed_rows == len(df)
    assert result.incident_report is not None
