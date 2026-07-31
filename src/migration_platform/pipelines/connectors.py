from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, Sequence

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


class SourceConnector(Protocol):
    cursor_column: str

    def fetch_batch(self, cursor: Optional[str], limit: int) -> pd.DataFrame:
        """Fetch the next incremental batch after the provided cursor."""


@dataclass
class PostgresTableConnector:
    """Simple incremental connector for Postgres-compatible sources."""

    connection_url: str
    table_name: str
    cursor_column: str
    selected_columns: Optional[Sequence[str]] = None
    extra_where: Optional[str] = None

    def __post_init__(self) -> None:
        self._engine: Engine = create_engine(self.connection_url)

    def fetch_batch(self, cursor: Optional[str], limit: int) -> pd.DataFrame:
        columns = self._render_columns()
        sql_parts: List[str] = [
            "SELECT {0}".format(columns),
            "FROM {0}".format(self.table_name),
        ]

        conditions: List[str] = []
        params: Dict[str, Any] = {"limit": limit}

        if self.extra_where:
            conditions.append("({0})".format(self.extra_where))

        if cursor is not None:
            conditions.append("{0} > :cursor".format(self.cursor_column))
            params["cursor"] = cursor

        if conditions:
            sql_parts.append("WHERE " + " AND ".join(conditions))

        sql_parts.append("ORDER BY {0} ASC".format(self.cursor_column))
        sql_parts.append("LIMIT :limit")
        statement = text("\n".join(sql_parts))

        with self._engine.connect() as conn:
            return pd.read_sql_query(statement, conn, params=params)

    def _render_columns(self) -> str:
        if not self.selected_columns:
            return "*"
        return ", ".join(self.selected_columns)
