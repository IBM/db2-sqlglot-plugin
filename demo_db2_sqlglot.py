"""Lightweight demo script for the Db2 SQLGlot dialect plugin."""

from __future__ import annotations

import sqlglot
from db2_sqlglot import Db2


def section(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def show_query(title: str, query: str, read: str | None = None, write: str = "db2") -> None:
    print(f"\n{title}")
    print(f"Input SQL:  {query}")

    try:
        if read:
            output = sqlglot.transpile(query, read=read, write=write)[0]
        else:
            parsed = sqlglot.parse_one(query, dialect=write)
            output = parsed.sql(dialect=write)

        print(f"Output SQL: {output}")
    except Exception as exc:
        print(f"Output SQL: ❌ Error: {exc}")


def main() -> None:
    section("Db2 SQLGlot Dialect Plugin - Demo")

    print(f"SQLGlot version: {sqlglot.__version__}")
    print(f"Db2 dialect module: {Db2.__module__}")

    section("1. Db2 dialect round-trip parsing")

    db2_queries = [
        "SELECT * FROM employee FETCH FIRST 10 ROWS ONLY",
        "SELECT * FROM employee ORDER BY salary DESC OFFSET 5 ROWS FETCH FIRST 10 ROWS ONLY",
        "SELECT CURRENT DATE, CURRENT TIMESTAMP FROM sysibm.sysdummy1",
        "SELECT POSSTR(lastname, 'son') AS match_pos FROM employee",
        "SELECT TIME_TO_STR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS') AS formatted_ts",
    ]

    for index, query in enumerate(db2_queries, start=1):
        show_query(f"Db2 Query {index}", query)

    section("2. Cross-dialect transpilation to Db2")

    transpilation_examples = [
        (
            "PostgreSQL LIMIT to Db2 FETCH FIRST",
            "SELECT * FROM employee ORDER BY salary DESC LIMIT 5",
            "postgres",
        ),
        (
            "MySQL LIMIT/OFFSET to Db2",
            "SELECT * FROM employee ORDER BY salary DESC LIMIT 5 OFFSET 10",
            "mysql",
        ),
        (
            "PostgreSQL POSITION to Db2 POSSTR",
            "SELECT POSITION('son' IN lastname) FROM employee",
            "postgres",
        ),
        (
            "MySQL DATEDIFF to Db2 DAYS arithmetic",
            "SELECT DATEDIFF(order_date, ship_date) AS days_between FROM orders",
            "mysql",
        ),
        (
            "PostgreSQL boolean handling to Db2",
            "SELECT TRUE AS is_active, FALSE AS is_deleted",
            "postgres",
        ),
    ]

    for title, query, source in transpilation_examples:
        show_query(title, query, read=source, write="db2")

    section("3. Db2 to other dialects")

    db2_to_other = [
        (
            "Db2 FETCH FIRST to PostgreSQL",
            "SELECT * FROM employee FETCH FIRST 3 ROWS ONLY",
            "postgres",
        ),
        (
            "Db2 FETCH FIRST to MySQL",
            "SELECT * FROM employee OFFSET 2 ROWS FETCH FIRST 4 ROWS ONLY",
            "mysql",
        ),
        (
            "Db2 CURRENT DATE to Snowflake",
            "SELECT CURRENT DATE FROM sysibm.sysdummy1",
            "snowflake",
        ),
    ]

    for title, query, target in db2_to_other:
        show_query(title, query, read="db2", write=target)

    section("4. Data type mapping examples")

    create_table_queries = [
        (
            "PostgreSQL types to Db2",
            "CREATE TABLE demo (id INT, is_active BOOLEAN, notes TEXT, created_at TIMESTAMPTZ)",
            "postgres",
        ),
        (
            "MySQL types to Db2",
            "CREATE TABLE demo (flag TINYINT, payload VARBINARY(100), created_at DATETIME)",
            "mysql",
        ),
    ]

    for title, query, source in create_table_queries:
        show_query(title, query, read=source, write="db2")

    section("Demo complete")
    print("This script demonstrates parsing, round-trip SQL generation, and transpilation.")
    print("It does not require a live Db2 connection.")


if __name__ == "__main__":
    main()
