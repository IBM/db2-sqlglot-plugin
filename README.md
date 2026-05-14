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

## CI/CD

### GitHub Actions Workflows

This project includes two automated CI/CD workflows:

1. **Unit Tests** (`.github/workflows/test.yml`)
   - **Triggers:** Push to main, Pull Requests, Manual dispatch
   - **Platforms:** Ubuntu, macOS, Windows
   - **Python versions:** 3.8, 3.9, 3.10, 3.11, 3.12
   - **Features:**
     - Concurrency control (cancels outdated runs)
     - Unit tests with coverage reporting
     - Code quality checks (black, isort, ruff)
     - Codecov integration

2. **Build and Publish Release** (`.github/workflows/release.yml`)
   - **Triggers:**
     - GitHub Release published (builds only, no auto-publish)
     - Manual workflow dispatch (with choice: Test PyPI or PyPI)
   - **Features:**
     - Builds distribution packages (wheel + sdist)
     - Tests installation on multiple platforms (Ubuntu, macOS, Windows)
     - Manual control over where to publish (Test PyPI or PyPI)
     - Prevents accidental production releases

### Creating a Release (Safe Workflow)

#### Step 1: Update Version
```bash
# Edit pyproject.toml
version = "1.0.1"

# Commit and push
git commit -am "Bump version to 1.0.1"
git push origin main
```

#### Step 2: Create GitHub Release
1. Go to GitHub → Releases → "Draft a new release"
2. Create a new tag (e.g., `v1.0.1`)
3. Add release notes
4. Click "Publish release"

**Result:** Package is built and tested, but **NOT automatically published**

#### Step 3: Choose Where to Publish (Manual Control)

After the release is published, you have two options:

##### Option A: Test on Test PyPI First (Recommended)
1. Go to **Actions** tab → **Build and Publish Release**
2. Click **"Run workflow"** button
3. Select:
   - **Branch:** `main` (or your release tag)
   - **Where to publish?** → Select **`test-pypi`**
4. Click **"Run workflow"**
5. Verify installation from Test PyPI:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ db2-sqlglot-dialect
   ```

##### Option B: Publish to Production PyPI
1. Go to **Actions** tab → **Build and Publish Release**
2. Click **"Run workflow"** button
3. Select:
   - **Branch:** `main` (or your release tag)
   - **Where to publish?** → Select **`pypi`**
4. Click **"Run workflow"**
5. Package is live on PyPI!

### Why This Approach is Safer

✅ **No accidental releases:** Publishing requires manual action
✅ **Test first:** Can test on Test PyPI before production
✅ **Explicit choice:** You choose Test PyPI or PyPI each time
✅ **Mistake recovery:** If wrong tag created, just don't publish
✅ **Review opportunity:** Time to review build artifacts before publishing

## Development

### Running Tests

```bash
pytest tests/
```

### Running Tests with Coverage

```bash
pytest tests/ -v --cov=db2_sqlglot --cov-report=term --cov-report=html
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