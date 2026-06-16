# Db2 SQLGlot Dialect Plugin

A Db2 dialect plugin for [SQLGlot](https://github.com/tobymao/sqlglot) - a powerful SQL parser, transpiler, and optimizer.

## Requirements

- **Python:** 3.10 or higher
- **SQLGlot:** 30.8.0 - 30.9.x (compatible with SQLMesh and other tools using SQLGlot 30.8.0)

## Features

- Full Db2 SQL syntax support
- Cross-dialect transpilation (Db2 ↔ PostgreSQL, MySQL, Snowflake, etc.)
- Type mapping (BOOLEAN → SMALLINT, NCHAR/NVARCHAR support, etc.)
- Db2-specific functions (POSSTR, VARCHAR_FORMAT, DAYOFWEEK, DAYOFYEAR)
- FETCH FIRST syntax support
- NULL ordering support

## ✅ Test Results

All tests passing: **10 tests** with **87% code coverage**

```bash
$ python3 -m pytest tests/test_db2_dialect.py -v
============================= test session starts ==============================
tests/test_db2_dialect.py ..........                                     [100%]
============================== 10 passed in 0.09s ==============================
```

**Code Coverage:**
```
Name                       Stmts   Miss  Cover
----------------------------------------------
db2_sqlglot/__init__.py        8      2    75%
db2_sqlglot/dialect.py        13      0   100%
db2_sqlglot/generator.py      57      9    84%
db2_sqlglot/parser.py          6      0   100%
----------------------------------------------
TOTAL                         84     11    87%
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

### From PyPI

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

1. **Unit Tests** (`.github/workflows/unit-tests.yml`)
   - **Triggers:** Push to main, Pull Requests, Manual dispatch
   - **Platforms:** Ubuntu, macOS, Windows
   - **Python versions:** 3.10, 3.11, 3.12
   - **Features:**
     - Concurrency control (cancels outdated runs)
     - Unit tests with coverage reporting
     - Code quality checks (ruff, flake8)
     - Codecov integration

2. **Build and Publish Release** (`.github/workflows/build_release.yaml`)
   - **Triggers:**
     - Version tag push (e.g., `v1.0.1`) - **Publishes to Test PyPI only**
     - Manual workflow dispatch (with choice: Test PyPI or PyPI, plus optional ref)
   - **Features:**
     - Authorized release gating (only ShubhamKapoor992 and amitkumar293)
     - Builds distribution packages (wheel + sdist)
     - Tests installation on multiple platforms before publish
     - **Tag push**: Automatically publishes to Test PyPI for testing
     - **Production release**: Requires manual workflow dispatch to publish to PyPI
     - Supports approval-gated publishing through environment protection rules

### Creating a Release

#### Step 1: Update Version
```bash
# Edit pyproject.toml
version = "1.0.1"

# Commit and push
git commit -am "Bump version to 1.0.1"
git push origin main
```

#### Step 2: Trigger the Release Workflow

You can trigger the release workflow in either of these ways:

##### Option A: Push a Version Tag
```bash
git tag v1.0.1
git push origin v1.0.1
```

This triggers [`.github/workflows/build_release.yaml`](db2-sqlglot-dialect/.github/workflows/build_release.yaml).

##### Option B: Run Manually from GitHub Actions
1. Go to **Actions** tab → **Build and Publish Release**
2. Click **"Run workflow"**
3. Select:
   - **Where to publish?** → `test-pypi` or `pypi`
   - **Git ref** → tag or branch (for example, `v1.0.1` or `main`)
4. Click **"Run workflow"**

#### Step 3: What Happens Next

**When you push a tag (e.g., `v1.0.1`):**
1. Workflow checks authorization (only ShubhamKapoor992 and amitkumar293)
2. Builds the package
3. Validates with `twine check`
4. Tests wheel installation on Ubuntu, macOS, Windows
5. **Publishes to Test PyPI automatically** for testing

**To publish to production PyPI:**
1. Go to **Actions** tab → **Build and Publish Release**
2. Click **"Run workflow"**
3. Select:
   - **Where to publish?** → `pypi`
   - **Git ref** → tag (e.g., `v1.0.1`)
4. Click **"Run workflow"**
5. Approve if environment protection is configured

#### Step 4: Verify Installation

**Test PyPI** (after tag push):
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ db2-sqlglot-dialect
```

**Production PyPI** (after manual release):
```bash
pip install db2-sqlglot-dialect
```

### Why This Approach Works Well

✅ **Authorized releases only:** Release workflow checks allowed GitHub users
✅ **Build verification first:** Package is built and validated before publish
✅ **Install verification:** Wheel is tested before publish
✅ **Approval support:** GitHub environments can require approval before publish
✅ **Flexible triggering:** Supports both version tags and manual dispatch

## Development

### Running Tests

```bash
pytest tests/
```

### Running Tests with Coverage

```bash
pytest tests/ -v --cov=db2_sqlglot --cov-report=term --cov-report=html
```

### Code Quality

The project uses ruff for formatting and linting:

```bash
# Run formatting
ruff format .

# Run linting
ruff check .

# Run formatting and repository checks
pre-commit run --all-files
```

Contributors should always run [`pre-commit run --all-files`](.pre-commit-config.yaml:1) before opening a pull request.

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

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run [`pre-commit run --all-files`](.pre-commit-config.yaml:1)
6. Ensure all tests pass and code passes linting
7. Submit a pull request

All pull requests will automatically run:
- Linting checks (ruff, flake8)
- Unit tests across multiple Python versions and platforms
- Code quality validation

## Credits

Built on top of [SQLGlot](https://github.com/tobymao/sqlglot) by Toby Mao.
