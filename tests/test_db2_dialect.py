"""
Tests for DB2 SQLGlot dialect plugin.

This test suite validates the DB2 dialect implementation including:
- Basic SQL parsing and generation
- Type conversions (BOOLEAN, NCHAR, NVARCHAR)
- DB2-specific functions (POSSTR, DAYOFWEEK, VARCHAR_FORMAT)
- FETCH FIRST and OFFSET syntax
- NULL ordering and typed division
"""

import unittest
from sqlglot import parse_one, ErrorLevel

# Import the dialect to ensure it's registered
from db2_sqlglot import Db2  # noqa: F401


class Validator(unittest.TestCase):
    """Base test validator with helper methods."""
    
    dialect = "db2"

    def parse_one(self, sql, **kwargs):
        return parse_one(sql, read=self.dialect, **kwargs)

    def validate_identity(
        self, sql, write_sql=None, pretty=False, identify=False
    ):
        """Validate that SQL round-trips correctly."""
        expression = self.parse_one(sql)
        self.assertEqual(
            write_sql or sql, 
            expression.sql(dialect=self.dialect, pretty=pretty, identify=identify)
        )
        return expression

    def validate_all(self, sql, read=None, write=None, pretty=False, identify=False):
        """
        Validate that:
        1. Everything in `read` transpiles to `sql`
        2. `sql` transpiles to everything in `write`
        """
        expression = self.parse_one(sql)

        for read_dialect, read_sql in (read or {}).items():
            with self.subTest(f"{read_dialect} -> {sql}"):
                self.assertEqual(
                    parse_one(read_sql, read_dialect).sql(
                        self.dialect,
                        unsupported_level=ErrorLevel.IGNORE,
                        pretty=pretty,
                        identify=identify,
                    ),
                    sql,
                )

        for write_dialect, write_sql in (write or {}).items():
            with self.subTest(f"{sql} -> {write_dialect}"):
                self.assertEqual(
                    expression.sql(
                        write_dialect,
                        unsupported_level=ErrorLevel.IGNORE,
                        pretty=pretty,
                        identify=identify,
                    ),
                    write_sql,
                )


class TestDB2(Validator):
    """Test suite for DB2 dialect."""
    
    dialect = "db2"

    def test_db2(self):
        # Test basic identity
        self.validate_identity("SELECT * FROM table1")
        self.validate_identity("SELECT a, b, c FROM table1")
        # Note: SQLGlot 30.x normalizes INT to INTEGER (both are valid DB2 synonyms)
        self.validate_identity("CREATE TABLE t (a SMALLINT, b INTEGER, c BIGINT)")
        self.validate_identity("CREATE TABLE t (a CHAR(10), b VARCHAR(100))")
        self.validate_identity("CREATE TABLE t (a DECIMAL(10, 2))")
        self.validate_identity("CREATE TABLE t (a TIMESTAMP)")
        # Note: SQLGlot 30.x preserves types as-is (no automatic NCHAR→GRAPHIC conversion)
        self.validate_identity("CREATE TABLE t (a NCHAR(10))")
        self.validate_identity("CREATE TABLE t (a NVARCHAR(100))")
        self.validate_identity("CREATE TABLE t (a GRAPHIC(10))")
        self.validate_identity("CREATE TABLE t (a VARGRAPHIC(100))")
        self.validate_identity("CREATE TABLE t (a DBCLOB)")
        self.validate_identity("CREATE TABLE t (a CLOB)")
        self.validate_identity("CREATE TABLE t (a CHAR(10), b GRAPHIC(10))")
        self.validate_identity("CREATE TABLE t (a VARCHAR(100), b VARGRAPHIC(100))")

        # Test FETCH FIRST syntax
        self.validate_identity("SELECT * FROM t FETCH FIRST 10 ROWS ONLY")
        self.validate_identity("SELECT * FROM t FETCH FIRST ROW ONLY")

        # Test OFFSET syntax
        self.validate_identity("SELECT * FROM t OFFSET 5 ROWS")
        self.validate_identity("SELECT * FROM t OFFSET 5 ROWS FETCH FIRST 10 ROWS ONLY")

        # Test CURRENT_DATE and CURRENT_TIMESTAMP
        self.validate_all(
            "SELECT CURRENT_DATE",
            write={
                "db2": "SELECT CURRENT DATE",
            },
        )
        self.validate_all(
            "SELECT CURRENT_TIMESTAMP",
            write={
                "db2": "SELECT CURRENT TIMESTAMP",
            },
        )

        # Test concatenation with ||
        self.validate_identity("SELECT a || b FROM t")
        self.validate_identity("SELECT a || b || c FROM t")

        # Test POSSTR function (Db2's string position function)
        self.validate_all(
            "SELECT STRPOS(haystack, needle)",
            write={
                "db2": "SELECT POSSTR(haystack, needle)",
            },
        )

        # Test boolean conversion (DB2 uses 0/1 for boolean)
        self.validate_all(
            "SELECT TRUE, FALSE",
            write={
                "db2": "SELECT 1, 0",
            },
        )

        # Test DAYOFWEEK and DAYOFYEAR extracts
        self.validate_all(
            "SELECT EXTRACT(DAYOFWEEK FROM date_col)",
            write={
                "db2": "SELECT DAYOFWEEK(date_col)",
            },
        )

        self.validate_all(
            "SELECT EXTRACT(DAYOFYEAR FROM date_col)",
            write={
                "db2": "SELECT DAYOFYEAR(date_col)",
            },
        )

        # Test VARCHAR_FORMAT (Db2's time to string function)
        self.validate_all(
            "SELECT TIME_TO_STR(timestamp_col, 'YYYY-MM-DD')",
            write={
                "db2": "SELECT VARCHAR_FORMAT(timestamp_col, 'YYYY-MM-DD')",
            },
        )

        # Test DATEDIFF conversion
        self.validate_all(
            "SELECT DATEDIFF(date1, date2)",
            write={
                "db2": "SELECT DAYS(date1) - DAYS(date2)",
            },
        )

        # Test joins
        self.validate_identity("SELECT * FROM t1 INNER JOIN t2 ON t1.id = t2.id")
        self.validate_identity("SELECT * FROM t1 LEFT JOIN t2 ON t1.id = t2.id")
        self.validate_identity("SELECT * FROM t1 RIGHT JOIN t2 ON t1.id = t2.id")

        # Test subqueries
        self.validate_identity("SELECT * FROM (SELECT a, b FROM t1) AS subq")

        # Test aggregations
        self.validate_identity("SELECT COUNT(*) FROM t")
        self.validate_identity("SELECT SUM(amount) FROM t")
        self.validate_identity("SELECT AVG(amount) FROM t")
        self.validate_identity("SELECT MIN(amount), MAX(amount) FROM t")

        # Test GROUP BY and HAVING
        self.validate_identity("SELECT category, COUNT(*) FROM t GROUP BY category")
        self.validate_identity(
            "SELECT category, COUNT(*) FROM t GROUP BY category HAVING COUNT(*) > 5"
        )

        # Test ORDER BY
        self.validate_identity("SELECT * FROM t ORDER BY a")
        self.validate_identity("SELECT * FROM t ORDER BY a DESC")
        self.validate_identity("SELECT * FROM t ORDER BY a, b DESC")

        # Test CASE expressions
        self.validate_identity("SELECT CASE WHEN a > 0 THEN 'positive' ELSE 'negative' END FROM t")
        self.validate_identity(
            "SELECT CASE a WHEN 1 THEN 'one' WHEN 2 THEN 'two' ELSE 'other' END FROM t"
        )

        # Test IN clause
        self.validate_identity("SELECT * FROM t WHERE a IN (1, 2, 3)")
        self.validate_all(
            "SELECT * FROM t WHERE a NOT IN (1, 2, 3)",
            write={
                "db2": "SELECT * FROM t WHERE NOT a IN (1, 2, 3)",
            },
        )

        # Test BETWEEN
        self.validate_identity("SELECT * FROM t WHERE a BETWEEN 1 AND 10")

        # Test LIKE
        self.validate_identity("SELECT * FROM t WHERE name LIKE 'John%'")

        # Test NULL handling
        self.validate_identity("SELECT * FROM t WHERE a IS NULL")
        self.validate_all(
            "SELECT * FROM t WHERE a IS NOT NULL",
            write={
                "db2": "SELECT * FROM t WHERE NOT a IS NULL",
            },
        )
        self.validate_identity("SELECT COALESCE(a, b, c) FROM t")

        # Test UNION
        self.validate_identity("SELECT a FROM t1 UNION SELECT a FROM t2")
        self.validate_identity("SELECT a FROM t1 UNION ALL SELECT a FROM t2")

        # Test WITH (CTE)
        self.validate_identity("WITH cte AS (SELECT * FROM t1) SELECT * FROM cte")

        # Test INSERT
        self.validate_identity("INSERT INTO t (a, b) VALUES (1, 2)")

        # Test UPDATE
        self.validate_identity("UPDATE t SET a = 1 WHERE b = 2")

        # Test DELETE
        self.validate_identity("DELETE FROM t WHERE a = 1")

        # Test CREATE TABLE (Note: SQLGlot 30.x normalizes INT to INTEGER)
        self.validate_identity("CREATE TABLE t (id INTEGER, name VARCHAR(100))")

        # Test DROP TABLE
        self.validate_identity("DROP TABLE t")

        # Test MAX/MIN with GREATEST/LEAST
        self.validate_all(
            "SELECT MAX(a, b, c)",
            write={
                "db2": "SELECT GREATEST(a, b, c)",
            },
        )

        self.validate_all(
            "SELECT MIN(a, b, c)",
            write={
                "db2": "SELECT LEAST(a, b, c)",
            },
        )

    def test_null_ordering(self):
        self.validate_identity("SELECT * FROM t ORDER BY x ASC")
        self.validate_identity("SELECT * FROM t ORDER BY x")
        self.validate_identity("SELECT * FROM t ORDER BY x DESC")
        self.validate_identity("SELECT * FROM t ORDER BY x ASC NULLS FIRST")
        self.validate_identity("SELECT * FROM t ORDER BY x DESC NULLS LAST")

    def test_typed_division(self):
        self.validate_identity("SELECT 5 / 2")
        self.validate_identity("SELECT a / b FROM t")
        self.validate_identity("SELECT 5.0 / 2.0")
        self.validate_identity("SELECT CAST(5 AS DECIMAL) / CAST(2 AS DECIMAL)")

    def test_strip_modifiers(self):
        # Note: SQLGlot 30.x strips these Spark-specific modifiers when generating DB2 SQL
        # This is correct behavior as DB2 doesn't support these clauses
        self.validate_all(
            "SELECT * FROM t CLUSTER BY x",
            write={
                "db2": "SELECT * FROM t",
                "spark": "SELECT * FROM t CLUSTER BY x NULLS LAST",
            },
        )

        self.validate_all(
            "SELECT * FROM t DISTRIBUTE BY x",
            write={
                "db2": "SELECT * FROM t",
                "spark": "SELECT * FROM t DISTRIBUTE BY x NULLS LAST",
            },
        )

        self.validate_all(
            "SELECT * FROM t SORT BY x",
            write={
                "db2": "SELECT * FROM t",
                "spark": "SELECT * FROM t SORT BY x NULLS LAST",
            },
        )

        self.validate_all(
            "SELECT * FROM t CLUSTER BY y DISTRIBUTE BY x SORT BY z",
            write={
                "db2": "SELECT * FROM t",
                "spark": "SELECT * FROM t CLUSTER BY y NULLS LAST DISTRIBUTE BY x NULLS LAST SORT BY z NULLS LAST",
            },
        )

    def test_nchar_nvarchar_transpilation(self):
        # Test that NCHAR/NVARCHAR are preserved as-is in SQLGlot 30.x
        # Both NCHAR and GRAPHIC are valid DB2 types
        self.validate_all(
            "CREATE TABLE t (a NCHAR(10))",
            write={
                "db2": "CREATE TABLE t (a NCHAR(10))",  # Preserved as-is
                "postgres": "CREATE TABLE t (a CHAR(10))",
                "mysql": "CREATE TABLE t (a CHAR(10))",
                "snowflake": "CREATE TABLE t (a CHAR(10))",
            },
        )

        # Test that NVARCHAR is preserved as-is in SQLGlot 30.x
        # Both NVARCHAR and VARGRAPHIC are valid DB2 types
        self.validate_all(
            "CREATE TABLE t (a NVARCHAR(100))",
            write={
                "db2": "CREATE TABLE t (a NVARCHAR(100))",  # Preserved as-is
                "postgres": "CREATE TABLE t (a VARCHAR(100))",
                "mysql": "CREATE TABLE t (a VARCHAR(100))",
                "snowflake": "CREATE TABLE t (a VARCHAR(100))",
            },
        )

    def test_variable_tokens(self):
        self.validate_identity("SELECT @var")
        self.validate_identity("SET @var = 1")


if __name__ == "__main__":
    unittest.main()
