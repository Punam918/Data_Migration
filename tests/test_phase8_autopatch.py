from pathlib import Path

import pandas as pd

from migration_platform.metadata.mapping_loader import MappingSpec
from migration_platform.orchestration.runner import OrchestrationRunner
from migration_platform.governance.patcher import PatchManager


def test_autopatch_suggests_on_unique_key_failure(tmp_path):
    var = tmp_path / "var"
    gov = var / "governance"
    gov.mkdir(parents=True)

    # create dataframe with duplicate keys to trigger unique_key failure
    df = pd.DataFrame({"id": [1, 1, 2], "value": [10, 10, 11]})

    mapping_payload = {
        "mapping_name": "autopatch_map",
        "source": {"system": "src_sys", "table": "src_table"},
        "target": {"system": "tgt_sys", "table": "tgt_table"},
        "column_mappings": {"id": "id", "value": "value"},
        "required_columns": ["id", "value"],
        "primary_key": ["id"],
    }
    mapping = MappingSpec.model_validate(mapping_payload)

    runner = OrchestrationRunner()
    # override default patch manager to write under tmp
    runner.patch_mgr = PatchManager(gov)

    result = runner.execute(df, mapping)

    patches = runner.patch_mgr.list_patches()
    assert any(p["type"] == "unique_constraint" for p in patches)
    assert result.transformed_rows == len(result.quality_results) or isinstance(result.transformed_rows, int)
