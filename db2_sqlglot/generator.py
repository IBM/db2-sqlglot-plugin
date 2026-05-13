from __future__ import annotations

import typing as t

from sqlglot import exp, generator, transforms
from sqlglot.dialects.dialect import (
    max_or_greatest,
    min_or_least,
    no_ilike_sql,
    no_pivot_sql,
    no_trycast_sql,
    rename_func,
    trim_sql,
)


def _date_add_sql(
    kind: str,
) -> t.Callable[[generator.Generator, exp.DateAdd | exp.DateSub], str]:
    def func(self: generator.Generator, expression: exp.DateAdd | exp.DateSub) -> str:
        this = self.sql(expression, "this")
        unit = expression.args.get("unit")
        value = self._simplify_unless_literal(expression.expression)

        if not isinstance(value, exp.Literal):
            self.unsupported("Cannot add non literal")

        value_sql = self.sql(value)
        unit_sql = self.sql(unit) if unit else "DAY"

        return f"{this} {kind} {value_sql} {unit_sql}"

    return func


class Db2(generator.Generator):
    LIMIT_FETCH = "FETCH"
    JOIN_HINTS = False
    TABLE_HINTS = False
    QUERY_HINTS = False
    NVL2_SUPPORTED = False
    LAST_DAY_SUPPORTS_DATE_PART = False

    CONCAT_COALESCE = True

    TYPE_MAPPING = {
        **generator.Generator.TYPE_MAPPING,
        # DB2 has native BOOLEAN type (since DB2 11.1)
        exp.DType.BOOLEAN: "BOOLEAN",
        # DB2 uses INTEGER, not INT
        exp.DType.INT: "INTEGER",
        # Other type mappings
        exp.DType.TINYINT: "SMALLINT",
        exp.DType.BINARY: "BLOB",
        exp.DType.VARBINARY: "BLOB",
        exp.DType.TEXT: "CLOB",
        exp.DType.NCHAR: "NCHAR",
        exp.DType.NVARCHAR: "NVARCHAR",
        exp.DType.TIMESTAMPTZ: "TIMESTAMP",
        exp.DType.DATETIME: "TIMESTAMP",
    }

    AFTER_HAVING_MODIFIER_TRANSFORMS = {
        "cluster": lambda self, e: "",
        "distribute": lambda self, e: "",
        "sort": lambda self, e: "",
    }

    TRANSFORMS = {
        **generator.Generator.TRANSFORMS,
        exp.ArgMax: rename_func("MAX"),
        exp.ArgMin: rename_func("MIN"),
        exp.DateAdd: _date_add_sql("+"),
        exp.DateSub: _date_add_sql("-"),
        exp.DateDiff: lambda self, e: f"{self.func('DAYS', e.this)} - {self.func('DAYS', e.expression)}",
        exp.CurrentDate: lambda self, e: "CURRENT DATE",
        exp.CurrentTimestamp: lambda self, e: "CURRENT TIMESTAMP",
        exp.ILike: no_ilike_sql,
        exp.Max: max_or_greatest,
        exp.Min: min_or_least,
        exp.Pivot: no_pivot_sql,
        exp.Select: transforms.preprocess([transforms.eliminate_distinct_on]),
        exp.StrPosition: rename_func("POSSTR"),
        exp.TimeToStr: rename_func("VARCHAR_FORMAT"),
        exp.TryCast: no_trycast_sql,
        exp.Trim: trim_sql,
    }
    
    # Note: DB2-specific types (GRAPHIC, VARGRAPHIC, DBCLOB) are automatically
    # handled by SQLGlot's default datatype_sql() when parsed as USERDEFINED types.
    # The 'kind' field preserves the original type name, so no custom override needed.

    def extract_sql(self, expression: exp.Extract) -> str:
        this = self.sql(expression, "this")
        expression_sql = self.sql(expression, "expression")

        if this.upper() in ("DAYOFWEEK", "DAYOFYEAR"):
            return f"{this.upper()}({expression_sql})"

        return f"EXTRACT({this} FROM {expression_sql})"

    def offset_sql(self, expression: exp.Offset) -> str:
        return f"{super().offset_sql(expression)} ROWS"

    def fetch_sql(self, expression: exp.Fetch) -> str:
        count = expression.args.get("count")
        if count:
            return f" FETCH FIRST {self.sql(count)} ROWS ONLY"
        return " FETCH FIRST ROW ONLY"

    def boolean_sql(self, expression: exp.Boolean) -> str:
        return "1" if expression.this else "0"
