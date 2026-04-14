"""Databricks SQL dialect adapter.

Databricks SQL (Spark SQL) uses DATE_TRUNC with the unit first,
DATEDIFF(end, start) for days, TIMESTAMPDIFF for other units,
CONCAT_WS + COLLECT_LIST for string aggregation, and
CREATE OR REPLACE TEMPORARY VIEW for temp tables.
"""

from __future__ import annotations

from helpers.dialects.base import SQLDialect


class DatabricksDialect(SQLDialect):
    """SQL dialect for Databricks SQL / Spark SQL."""

    name: str = "databricks"

    def date_trunc(self, field: str, unit: str) -> str:
        """Databricks DATE_TRUNC — unit string first, then field.

        >>> DatabricksDialect().date_trunc('order_date', 'month')
        "DATE_TRUNC('MONTH', order_date)"
        """
        return f"DATE_TRUNC('{unit.upper()}', {field})"

    def date_diff(self, unit: str, start: str, end: str) -> str:
        """Databricks date difference.

        DATEDIFF for days (native), TIMESTAMPDIFF for other units
        (Databricks Runtime 10.0+).

        >>> DatabricksDialect().date_diff('day', 'start_date', 'end_date')
        'DATEDIFF(end_date, start_date)'
        >>> DatabricksDialect().date_diff('month', 'start_date', 'end_date')
        'TIMESTAMPDIFF(MONTH, start_date, end_date)'
        """
        if unit.lower() == "day":
            return f"DATEDIFF({end}, {start})"
        return f"TIMESTAMPDIFF({unit.upper()}, {start}, {end})"

    def string_agg(self, column: str, delimiter: str = ",") -> str:
        """Databricks CONCAT_WS + COLLECT_LIST for string aggregation.

        >>> DatabricksDialect().string_agg('category')
        "CONCAT_WS(',', COLLECT_LIST(category))"
        """
        return f"CONCAT_WS('{delimiter}', COLLECT_LIST({column}))"

    def current_timestamp(self) -> str:
        """Databricks CURRENT_TIMESTAMP() — function call syntax.

        >>> DatabricksDialect().current_timestamp()
        'CURRENT_TIMESTAMP()'
        """
        return "CURRENT_TIMESTAMP()"

    def create_temp_table(self, name: str, query: str) -> str:
        """Databricks CREATE OR REPLACE TEMPORARY VIEW.

        >>> DatabricksDialect().create_temp_table('tmp_agg', 'SELECT 1')
        'CREATE OR REPLACE TEMPORARY VIEW tmp_agg AS (SELECT 1)'
        """
        return f"CREATE OR REPLACE TEMPORARY VIEW {name} AS ({query})"

    def sample_rows(self, table: str, n: int) -> str:
        """Databricks TABLESAMPLE (n ROWS).

        >>> DatabricksDialect().sample_rows('orders', 100)
        'SELECT * FROM orders TABLESAMPLE (100 ROWS)'
        """
        return f"SELECT * FROM {table} TABLESAMPLE ({int(n)} ROWS)"

    def describe_table(self, table: str) -> str:
        """Databricks DESCRIBE TABLE EXTENDED.

        >>> DatabricksDialect().describe_table('customers')
        'DESCRIBE TABLE EXTENDED customers'
        """
        return f"DESCRIBE TABLE EXTENDED {table}"
