# DB2 SQLGlot Dialect Plugin

A DB2 dialect plugin for [SQLGlot](https://github.com/tobymao/sqlglot) - a powerful SQL parser, transpiler, and optimizer.

## Features

- Full DB2 SQL syntax support
- Cross-dialect transpilation (DB2 ↔ PostgreSQL, MySQL, Snowflake, etc.)
- Type mapping (BOOLEAN → SMALLINT, NCHAR/NVARCHAR support, etc.)
- DB2-specific functions (POSSTR, VARCHAR_FORMAT, DAYOFWEEK, DAYOFYEAR)
- FETCH FIRST syntax support
- NULL ordering support

## ✅ Test Results

All tests passing: **6 tests, 28 subtests**

```bash
$ python3 -m pytest tests/test_db2_dialect.py -v
============================= test session starts ==============================
tests/test_db2_dialect.py::TestDB2::test_db2 PASSED                      [ 16%]
tests/test_db2_dialect.py::TestDB2::test_nchar_nvarchar_transpilation PASSED [ 33%]
tests/test_db2_dialect.py::TestDB2::test_null_ordering PASSED            [ 50%]
tests/test_db2_dialect.py::TestDB2::test_strip_modifiers PASSED          [ 66%]
tests/test_db2_dialect.py::TestDB2::test_typed_division PASSED           [ 83%]
tests/test_db2_dialect.py::TestDB2::test_variable_tokens PASSED          [100%]
==================== 6 passed, 28 subtests passed in 0.28s =====================
```

### Test Coverage

The test suite validates:
- ✅ **Basic SQL**: SELECT, INSERT, UPDATE, DELETE, CREATE/DROP TABLE
- ✅ **Type conversions**: INTEGER→INT, NCHAR→GRAPHIC, NVARCHAR→VARGRAPHIC, DBCLOB→CLOB
- ✅ **Functions**: POSSTR, VARCHAR_FORMAT, DAYOFWEEK, DAYOFYEAR, GREATEST, LEAST
- ✅ **Boolean handling**: TRUE/FALSE → 1/0
- ✅ **Date/Time**: CURRENT DATE, CURRENT TIMESTAMP, DATEDIFF→DAYS
- ✅ **FETCH FIRST**: Pagination with FETCH FIRST n ROWS ONLY
- ✅ **OFFSET**: OFFSET n ROWS syntax
- ✅ **NULL ordering**: NULLS FIRST, NULLS LAST
- ✅ **Joins**: INNER, LEFT, RIGHT joins
- ✅ **Aggregations**: COUNT, SUM, AVG, MIN, MAX
- ✅ **Subqueries & CTEs**: WITH clause support
- ✅ **CASE expressions**: Simple and searched CASE
- ✅ **Operators**: IN, BETWEEN, LIKE, IS NULL
- ✅ **Set operations**: UNION, UNION ALL
- ✅ **Variable tokens**: @var syntax
- ✅ **Typed division**: Proper numeric division handling

## Installation

### From Source (Development)

```bash
cd db2-sqlglot-dialect
pip install -e .
```

### From PyPI (Once Published)

```bash
pip install db2-sqlglot-dialect
```

## Usage

Once installed, the Db2 dialect is automatically discovered by SQLGlot:

```python
from sqlglot import transpile

# Transpile from PostgreSQL to Db2 (LIMIT → FETCH FIRST)
result = transpile(
    "SELECT * FROM table1 LIMIT 10",
    read="postgres",
    write="db2"
)
print(result[0])
# Output: SELECT * FROM table1 FETCH FIRST 10 ROWS ONLY

# Transpile from Db2 to PostgreSQL
# Note: FETCH FIRST is preserved (PostgreSQL supports it natively - SQL standard)
result = transpile(
    "SELECT * FROM table1 FETCH FIRST 10 ROWS ONLY",
    read="db2",
    write="postgres"
)
print(result[0])
# Output: SELECT * FROM table1 FETCH FIRST 10 ROWS ONLY

# Both LIMIT and FETCH FIRST work in PostgreSQL
# If you need LIMIT specifically, use it in the source query
result = transpile(
    "SELECT * FROM table1 LIMIT 10",
    read="db2",
    write="postgres"
)
print(result[0])
# Output: SELECT * FROM table1 LIMIT 10
```

## Supported Features

### Data Types

#### Native Db2 Types (Perfect Roundtrip)
- **Standard types**: INTEGER, BIGINT, SMALLINT, DECIMAL, VARCHAR, CHAR, DATE, TIMESTAMP, CLOB, BLOB, BOOLEAN
- **Db2-specific types**: GRAPHIC, VARGRAPHIC, DBCLOB, DATALINK, ROWID, DECFLOAT, XML

#### Cross-Dialect Type Conversions
When transpiling from other databases to Db2:
- ✅ **TEXT** → CLOB
- ✅ **BYTEA/BINARY** → BLOB
- ✅ **TINYINT** → SMALLINT
- ✅ **TIMESTAMPTZ** → TIMESTAMP
- ⚠️ **SERIAL/BIGSERIAL** → Preserved as-is (may need manual conversion)
- ⚠️ **LONGTEXT/MEDIUMTEXT** → Preserved as-is (may need manual conversion)

**Note**: Unsupported or dialect-specific constructs may be preserved as-is during transpilation. This behavior prioritizes syntax preservation over potentially lossy or incorrect transformations. Users should review and adjust preserved types as needed for their specific Db2 version and requirements.

### Functions
- `POSSTR(haystack, needle)` - String position
- `VARCHAR_FORMAT(timestamp, format)` - Time to string conversion
- `DAYOFWEEK(date)` - Extract day of week
- `DAYOFYEAR(date)` - Extract day of year
- `CURRENT DATE`, `CURRENT TIMESTAMP`
- Date arithmetic with `+` and `-`

### SQL Features
- `FETCH FIRST n ROWS ONLY` syntax
- `OFFSET n ROWS` syntax
- NULL ordering (`NULLS FIRST`, `NULLS LAST`)
- Typed division
- Variable tokens (`@var`)

## Development

### Running Tests

```bash
pytest tests/
```

### Project Structure

```
db2-sqlglot-dialect/
├── db2_sqlglot/
│   ├── __init__.py
│   ├── dialect.py      # Main dialect class
│   ├── generator.py    # SQL generation logic
│   └── parser.py       # SQL parsing logic
├── tests/
│   └── test_db2_dialect.py
├── pyproject.toml      # Modern Python packaging (PEP 517/518/621)
└── README.md
```

**Note:** This project uses modern Python packaging with `pyproject.toml` only (no `setup.py` needed). Entry points are defined in `pyproject.toml` and work seamlessly with SQLGlot's plugin discovery system.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Credits

Built on top of [SQLGlot](https://github.com/tobymao/sqlglot) by Toby Mao.