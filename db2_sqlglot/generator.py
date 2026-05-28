#-------------------------------------------------------------------------------------------------#
#                      DISCLAIMER OF WARRANTIES AND LIMITATION OF LIABILITY                       #
#                                                                                                 #
#  (C) COPYRIGHT International Business Machines Corp. 2026 All Rights Reserved             #
#  Licensed Materials - Property of IBM                                                           #
#                                                                                                 #
#  US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP   #
#  Schedule Contract with IBM Corp.                                                               #
#                                                                                                 #
#  The following source code ("Sample") is owned by International Business Machines Corporation   #
#  or one of its subsidiaries ("IBM") and is copyrighted and licensed, not sold. You may use,     #
#  copy, modify, and distribute the Sample in any form without payment to IBM, for the purpose    #
#  of assisting you in the creation of Python applications using the ibm_db library.              #
#                                                                                                 #
#  The Sample code is provided to you on an "AS IS" basis, without warranty of any kind. IBM      #
#  HEREBY EXPRESSLY DISCLAIMS ALL WARRANTIES, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT       #
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.    #
#  Some jurisdictions do not allow for the exclusion or limitation of implied warranties, so the  #
#  above limitations or exclusions may not apply to you. IBM shall not be liable for any damages  #
#  you suffer as a result of using, copying, modifying or distributing the Sample, even if IBM    #
#  has been advised of the possibility of such damages.                                           #
#-------------------------------------------------------------------------------------------------#

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


def _add_sysibm_dual(expression: exp.Select) -> exp.Select:
    """
    Add SYSIBM.SYSDUMMY1 table for SELECT statements without FROM clause.
    Db2 requires a FROM clause in SELECT statements.
    """
    # Note: SQLGlot uses 'from_' (with underscore) as the key for FROM clauses
    if not expression.args.get("from_"):
        expression.set(
            "from_",
            exp.From(
                this=exp.Table(
                    this=exp.Identifier(this="SYSDUMMY1"),
                    db=exp.Identifier(this="SYSIBM")
                )
            )
        )
    return expression


def _date_add_sql(
    kind: str,
) -> t.Callable[[generator.Generator, exp.DateAdd | exp.DateSub], str]:
    def func(
        self: generator.Generator, expression: exp.DateAdd | exp.DateSub
    ) -> str:
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
        # Db2 has native BOOLEAN type (since Db2 11.1)
        exp.DType.BOOLEAN: "BOOLEAN",
        # Db2 uses INTEGER, not INT
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
        # UUID is not a native Db2 type, use CHAR(36)
        exp.DType.UUID: "CHAR(36)",
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
        exp.DateDiff: lambda self, e: (
            f"{self.func('DAYS', e.this)} - "
            f"{self.func('DAYS', e.expression)}"
        ),
        exp.CurrentDate: lambda self, e: "CURRENT DATE",
        exp.CurrentTimestamp: lambda self, e: "CURRENT TIMESTAMP",
        exp.ILike: no_ilike_sql,
        exp.Max: max_or_greatest,
        exp.Min: min_or_least,
        exp.Pivot: no_pivot_sql,
        exp.Select: transforms.preprocess([transforms.eliminate_distinct_on, _add_sysibm_dual]),
        exp.StrPosition: rename_func("POSSTR"),
        exp.TimeToStr: rename_func("VARCHAR_FORMAT"),
        exp.TryCast: no_trycast_sql,
        exp.Trim: trim_sql,
    }
    
    # Note: Db2-specific types (GRAPHIC, VARGRAPHIC, DBCLOB) are automatically
    # handled by SQLGlot's default datatype_sql() when parsed as USERDEFINED
    # types. The 'kind' field preserves the original type name, so no custom
    # override needed.
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

    def cast_sql(self, expression: exp.Cast, safe_prefix: t.Optional[str] = None) -> str:
        """
        Override cast_sql to handle UUID casts.
        Since Db2 doesn't have native UUID type, we use CHAR(36).
        When casting to UUID, we just return the value without the cast.
        """
        # Check if casting to UUID
        to_type = expression.to
        if isinstance(to_type, exp.DataType) and to_type.this == exp.DataType.Type.UUID:
            # Just return the expression being cast, without the CAST
            return self.sql(expression.this)

        # For all other casts, use the default behavior
        return super().cast_sql(expression, safe_prefix)

    def columnconstraint_sql(self, expression: exp.ColumnConstraint) -> str:
        """
        Override columnconstraint_sql to handle UUID DEFAULT values.
        Db2 doesn't have UUID generation functions, so we replace
        gen_random_uuid() and similar functions with a placeholder.
        """
        kind = expression.args.get("kind")

        # Check if this is a DEFAULT constraint with UUID generation
        if isinstance(kind, exp.DefaultColumnConstraint):
            default_value = kind.this
            # Check if the default is a Uuid() function call
            if isinstance(default_value, exp.Uuid):
                # Replace with a simple string default
                # Note: In production, this should be handled with a trigger or application logic
                kind.set("this", exp.Literal.string("0"))

        return super().columnconstraint_sql(expression)

    def boolean_sql(self, expression: exp.Boolean) -> str:
        return "1" if expression.this else "0"
