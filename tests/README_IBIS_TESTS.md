# Ibis DB2 Integration Tests

This directory contains integration tests for using Ibis with the DB2 SQLGlot dialect plugin.

## Prerequisites

### 1. Install Required Packages

Make sure you have the following packages installed in your `ibis-db2` conda environment:

```bash
conda activate ibis-db2

# Install Ibis with DB2 backend
pip install 'ibis-framework[db2]'

# Install IBM DB2 driver
pip install ibm_db ibm_db_sa

# Install pytest for running tests
pip install pytest

# Install the DB2 SQLGlot dialect (from this project)
pip install -e /path/to/db2-sqlglot-dialect
```

### 2. DB2 Database Access

The tests connect to a DB2 database with the following credentials (already configured in `test_ibis_db2.py`):

- **Host**: db2i-awanishgupta-ph2q8-x86.dev.fyre.ibm.com
- **Port**: 50000
- **Database**: ALPHA
- **Schema**: analytics_dev
- **Username**: testuser1
- **Password**: db2password@123

## Running the Tests

### Run All Ibis Tests

```bash
conda activate ibis-db2
cd db2-sqlglot-dialect
pytest tests/test_ibis_db2.py -v
```

### Run Specific Test Classes

```bash
# Test connection only
pytest tests/test_ibis_db2.py::TestIbisDB2Connection -v

# Test dialect integration
pytest tests/test_ibis_db2.py::TestIbisDB2Dialect -v

# Test operations
pytest tests/test_ibis_db2.py::TestIbisDB2Operations -v

# Test functions
pytest tests/test_ibis_db2.py::TestIbisDB2Functions -v

# Test type mapping
pytest tests/test_ibis_db2.py::TestIbisDB2TypeMapping -v

# Test SQL compilation
pytest tests/test_ibis_db2.py::TestIbisDB2SQLCompilation -v
```

### Run Specific Tests

```bash
# Test connection
pytest tests/test_ibis_db2.py::TestIbisDB2Connection::test_connection_successful -v

# Test filtering
pytest tests/test_ibis_db2.py::TestIbisDB2Operations::test_filter_operation -v

# Test aggregation
pytest tests/test_ibis_db2.py::TestIbisDB2Operations::test_aggregation -v
```

### Run with Detailed Output

```bash
# Show print statements and detailed output
pytest tests/test_ibis_db2.py -v -s

# Show test coverage
pytest tests/test_ibis_db2.py -v --cov=db2_sqlglot
```

## Test Structure

### Test Classes

1. **TestIbisDB2Connection**: Tests basic DB2 connection and schema operations
2. **TestIbisDB2Dialect**: Validates that Ibis uses the DB2 SQLGlot dialect correctly
3. **TestIbisDB2Operations**: Tests common Ibis operations (filter, project, aggregate, join, etc.)
4. **TestIbisDB2Functions**: Tests DB2-specific functions (string, date, NULL handling)
5. **TestIbisDB2TypeMapping**: Validates data type mapping between Ibis and DB2
6. **TestIbisDB2SQLCompilation**: Tests SQL compilation with DB2 dialect features

### Sample Table

The tests automatically create a temporary table `test_ibis_sample` with the following structure:

```sql
CREATE TABLE analytics_dev.test_ibis_sample (
    id INTEGER NOT NULL PRIMARY KEY,
    name VARCHAR(100),
    age INTEGER,
    salary DECIMAL(10, 2),
    hire_date DATE,
    is_active SMALLINT
)
```

Sample data includes 5 employees with various attributes for testing.

## What the Tests Validate

### ✅ DB2 Dialect Integration
- DB2 dialect is properly loaded and registered
- Ibis compiles SQL using DB2 syntax (FETCH FIRST instead of LIMIT)
- Boolean values are handled correctly (SMALLINT 0/1 instead of TRUE/FALSE)

### ✅ Ibis Operations
- **Selection**: SELECT with column projection
- **Filtering**: WHERE clauses with various conditions
- **Aggregation**: COUNT, SUM, AVG, MIN, MAX
- **Grouping**: GROUP BY with aggregations
- **Sorting**: ORDER BY with ASC/DESC
- **Limiting**: LIMIT and OFFSET (compiled to FETCH FIRST and OFFSET ROWS)
- **Joins**: INNER, LEFT, RIGHT joins
- **Case Expressions**: CASE WHEN statements

### ✅ DB2-Specific Features
- **FETCH FIRST syntax**: Proper compilation of LIMIT to FETCH FIRST n ROWS ONLY
- **OFFSET ROWS syntax**: Proper compilation of OFFSET
- **Boolean handling**: SMALLINT (0/1) instead of BOOLEAN
- **Date functions**: YEAR, MONTH, DAY extraction
- **String functions**: UPPER, LOWER, LENGTH, etc.
- **NULL handling**: COALESCE, IS NULL, IS NOT NULL

### ✅ Data Type Mapping
- INTEGER types
- DECIMAL types with precision
- VARCHAR/STRING types
- DATE types
- SMALLINT for booleans

## Troubleshooting

### Connection Issues

If you get connection errors:

1. **Check network access**: Ensure you can reach the DB2 host
   ```bash
   ping db2i-awanishgupta-ph2q8-x86.dev.fyre.ibm.com
   telnet db2i-awanishgupta-ph2q8-x86.dev.fyre.ibm.com 50000
   ```

2. **Verify credentials**: Ensure username/password are correct

3. **Check IBM DB2 driver**: Ensure `ibm_db` is properly installed
   ```bash
   python -c "import ibm_db; print('IBM DB2 driver installed')"
   ```

### Import Errors

If you get import errors:

```bash
# Ensure all packages are installed
conda activate ibis-db2
pip install 'ibis-framework[db2]' ibm_db ibm_db_sa pytest

# Ensure DB2 dialect is installed
cd /path/to/db2-sqlglot-dialect
pip install -e .
```

### Test Failures

If tests fail:

1. **Check DB2 availability**: The database must be accessible
2. **Check schema permissions**: User must have CREATE/DROP table permissions in `analytics_dev` schema
3. **Check existing tables**: Ensure `test_ibis_sample` table doesn't exist or can be dropped

### Skip Tests if DB2 Not Available

The tests will automatically skip if DB2 connection fails. You can also skip them manually:

```bash
# Skip all DB2 integration tests
pytest tests/test_ibis_db2.py -v -m "not requires_db2"
```

## Example Usage

Here's how to use Ibis with DB2 in your own code:

```python
import ibis

# Connect to DB2
con = ibis.connect(
    "db2://testuser1:db2password@123@"
    "db2i-awanishgupta-ph2q8-x86.dev.fyre.ibm.com:50000/ALPHA"
)

# Set schema
con.raw_sql("SET SCHEMA analytics_dev")

# Get a table
table = con.table("your_table_name")

# Query with Ibis
result = (
    table
    .filter(table.age > 30)
    .group_by('department')
    .aggregate(
        count=table.count(),
        avg_salary=table.salary.mean()
    )
    .order_by('avg_salary', ascending=False)
    .limit(10)
    .execute()
)

print(result)

# The SQL will be compiled using DB2 dialect automatically!
```

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Use descriptive test names
3. Add docstrings explaining what the test validates
4. Clean up any created resources in fixtures
5. Handle connection failures gracefully with `pytest.skip()`

## References

- [Ibis Documentation](https://ibis-project.org/)
- [DB2 SQL Reference](https://www.ibm.com/docs/en/db2/11.5?topic=reference-sql)
- [SQLGlot Documentation](https://github.com/tobymao/sqlglot)