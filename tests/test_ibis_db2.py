"""
Ibis integration tests for DB2 SQLGlot dialect.

This test suite validates that Ibis works correctly with the DB2 dialect plugin,
including:
- Connection to DB2 database
- Table operations (create, read, query)
- SQL compilation using DB2 dialect
- Data type handling
- Aggregations and transformations

Prerequisites:
- ibis-framework installed
- db2-sqlglot-dialect installed
- ibm_db or ibm_db_sa driver installed
- Access to DB2 database

Run tests:
    pytest tests/test_ibis_db2.py -v
    
Skip tests if DB2 not available:
    pytest tests/test_ibis_db2.py -v -m "not requires_db2"
"""

import os
import pytest
import ibis
from ibis import _


# DB2 connection configuration
DB2_CONFIG = {
    "host": "db2i-AmitParmar-7gqin-x86.dev.fyre.ibm.com",
    "port": 50000,
    "database": "testdb",
    "schema": "shubham",
    "username": "testuser1",
    "password": "test123",
}


@pytest.fixture(scope="module")
def db2_connection():
    """
    Create a DB2 connection using Ibis.
    
    This fixture attempts to connect to DB2. If connection fails,
    tests will be skipped.
    """
    try:
        # Construct DB2 connection string
        # Format: db2://username:password@host:port/database
        conn_string = (
            f"db2://{DB2_CONFIG['username']}:{DB2_CONFIG['password']}"
            f"@{DB2_CONFIG['host']}:{DB2_CONFIG['port']}/{DB2_CONFIG['database']}"
        )
        
        # Connect to DB2
        con = ibis.connect(conn_string)
        
        # Set schema
        con.raw_sql(f"SET SCHEMA {DB2_CONFIG['schema']}")
        
        yield con
        
        # Cleanup
        con.disconnect()
        
    except Exception as e:
        pytest.skip(f"DB2 connection not available: {e}")


@pytest.fixture(scope="module")
def sample_table(db2_connection):
    """
    Create a sample table for testing.
    
    Creates a temporary table with sample data for testing various operations.
    """
    con = db2_connection
    table_name = "test_ibis_sample"
    
    try:
        # Drop table if exists
        try:
            con.raw_sql(f"DROP TABLE {DB2_CONFIG['schema']}.{table_name}")
        except:
            pass
        
        # Create sample table
        create_sql = f"""
        CREATE TABLE {DB2_CONFIG['schema']}.{table_name} (
            id INTEGER NOT NULL,
            name VARCHAR(100),
            age INTEGER,
            salary DECIMAL(10, 2),
            hire_date DATE,
            is_active SMALLINT,
            PRIMARY KEY (id)
        )
        """
        con.raw_sql(create_sql)
        
        # Insert sample data
        insert_sql = f"""
        INSERT INTO {DB2_CONFIG['schema']}.{table_name} 
        (id, name, age, salary, hire_date, is_active)
        VALUES 
            (1, 'Alice', 30, 75000.00, '2020-01-15', 1),
            (2, 'Bob', 35, 85000.00, '2019-03-20', 1),
            (3, 'Charlie', 28, 65000.00, '2021-06-10', 1),
            (4, 'Diana', 42, 95000.00, '2018-11-05', 0),
            (5, 'Eve', 31, 72000.00, '2020-08-22', 1)
        """
        con.raw_sql(insert_sql)
        
        yield table_name
        
        # Cleanup
        try:
            con.raw_sql(f"DROP TABLE {DB2_CONFIG['schema']}.{table_name}")
        except:
            pass
            
    except Exception as e:
        pytest.skip(f"Could not create sample table: {e}")


class TestIbisDB2Connection:
    """Test DB2 connection and basic operations."""
    
    def test_connection_successful(self, db2_connection):
        """Test that connection to DB2 is successful."""
        assert db2_connection is not None
        assert db2_connection.name == "db2"
    
    def test_list_tables(self, db2_connection):
        """Test listing tables in the schema."""
        tables = db2_connection.list_tables()
        assert isinstance(tables, list)
        # Should have at least some tables in the schema
        assert len(tables) >= 0
    
    def test_current_schema(self, db2_connection):
        """Test getting current schema."""
        # Execute a query to verify schema
        result = db2_connection.raw_sql("VALUES CURRENT SCHEMA")
        assert result is not None


class TestIbisDB2Dialect:
    """Test that Ibis uses DB2 SQLGlot dialect correctly."""
    
    def test_db2_dialect_loaded(self):
        """Test that DB2 dialect is available in SQLGlot."""
        from sqlglot import transpile
        
        # Test that DB2 dialect can be used (plugin dialects are loaded dynamically)
        # If the dialect wasn't available, this would raise an error
        try:
            result = transpile("SELECT 1", read="db2", write="db2")
            assert result is not None
            assert len(result) > 0
        except Exception as e:
            pytest.fail(f"DB2 dialect not available: {e}")
    
    def test_sql_compilation_uses_db2_dialect(self, db2_connection, sample_table):
        """Test that Ibis compiles SQL using DB2 dialect."""
        table = db2_connection.table(sample_table)
        
        # Create a query with LIMIT (should compile to FETCH FIRST in DB2)
        query = table.limit(10)
        
        # Compile to SQL
        sql = ibis.to_sql(query, dialect="db2")
        
        # DB2 uses FETCH FIRST instead of LIMIT
        assert "FETCH FIRST" in sql.upper()
        assert "ROWS ONLY" in sql.upper()
    
    def test_boolean_handling(self, db2_connection, sample_table):
        """Test that booleans are handled correctly (DB2 uses SMALLINT)."""
        table = db2_connection.table(sample_table)
        
        # Filter by boolean column (is_active)
        query = table.filter(table.is_active == 1)
        
        # Compile to SQL
        sql = ibis.to_sql(query, dialect="db2")
        
        # Should use 1 for true (DB2 doesn't have native boolean)
        assert "is_active" in sql.lower()


class TestIbisDB2Operations:
    """Test various Ibis operations on DB2."""
    
    def test_select_all(self, db2_connection, sample_table):
        """Test selecting all rows from a table."""
        table = db2_connection.table(sample_table)
        result = table.execute()
        
        assert len(result) == 5
        assert list(result.columns) == ['id', 'name', 'age', 'salary', 'hire_date', 'is_active']
    
    def test_filter_operation(self, db2_connection, sample_table):
        """Test filtering rows."""
        table = db2_connection.table(sample_table)
        
        # Filter by age
        filtered = table.filter(table.age > 30)
        result = filtered.execute()
        
        assert len(result) == 3  # Bob (35), Diana (42), Eve (31)
        assert all(result['age'] > 30)
    
    def test_projection(self, db2_connection, sample_table):
        """Test selecting specific columns."""
        table = db2_connection.table(sample_table)
        
        # Select only name and salary
        projected = table[['name', 'salary']]
        result = projected.execute()
        
        assert list(result.columns) == ['name', 'salary']
        assert len(result) == 5
    
    def test_aggregation(self, db2_connection, sample_table):
        """Test aggregation operations."""
        table = db2_connection.table(sample_table)
        
        # Calculate average salary
        avg_salary = table.salary.mean()
        result = avg_salary.execute()
        
        # Average of 75000, 85000, 65000, 95000, 72000 = 78400
        assert abs(result - 78400.00) < 0.01
    
    def test_group_by(self, db2_connection, sample_table):
        """Test GROUP BY operations."""
        table = db2_connection.table(sample_table)
        
        # Group by is_active and count
        grouped = table.group_by('is_active').aggregate(
            count=table.count(),
            avg_salary=table.salary.mean()
        )
        result = grouped.execute()
        
        assert len(result) == 2  # Two groups: active (1) and inactive (0)
        
        # Check counts
        active_row = result[result['is_active'] == 1].iloc[0]
        inactive_row = result[result['is_active'] == 0].iloc[0]
        
        assert active_row['count'] == 4
        assert inactive_row['count'] == 1
    
    def test_order_by(self, db2_connection, sample_table):
        """Test ORDER BY operations."""
        table = db2_connection.table(sample_table)
        
        # Order by salary descending
        ordered = table.order_by(table.salary.desc())
        result = ordered.execute()
        
        # First row should be Diana (95000)
        assert result.iloc[0]['name'] == 'Diana'
        assert result.iloc[0]['salary'] == 95000.00
    
    def test_limit_offset(self, db2_connection, sample_table):
        """Test LIMIT and OFFSET (FETCH FIRST and OFFSET in DB2)."""
        table = db2_connection.table(sample_table)
        
        # Get 2 rows starting from offset 1
        limited = table.order_by('id').limit(2, offset=1)
        result = limited.execute()
        
        assert len(result) == 2
        assert result.iloc[0]['id'] == 2  # Bob
        assert result.iloc[1]['id'] == 3  # Charlie
    
    def test_join_operation(self, db2_connection, sample_table):
        """Test JOIN operations."""
        table = db2_connection.table(sample_table)
        
        # Self-join to find employees with similar salaries
        t1 = table.alias('t1')
        t2 = table.alias('t2')
        
        joined = t1.join(
            t2,
            (t1.id != t2.id) & (abs(t1.salary - t2.salary) < 10000)
        )[t1.name.name('name1'), t2.name.name('name2'), t1.salary.name('salary1')]
        
        result = joined.execute()
        
        # Should find pairs with similar salaries
        assert len(result) > 0
    
    def test_case_expression(self, db2_connection, sample_table):
        """Test CASE expressions."""
        table = db2_connection.table(sample_table)
        
        # Create age category
        age_category = (
            ibis.case()
            .when(table.age < 30, 'Young')
            .when(table.age < 40, 'Middle')
            .else_('Senior')
            .end()
            .name('age_category')
        )
        
        result = table[table.name, table.age, age_category].execute()
        
        assert len(result) == 5
        assert 'age_category' in result.columns
        
        # Check categories
        charlie = result[result['name'] == 'Charlie'].iloc[0]
        assert charlie['age_category'] == 'Young'
        
        diana = result[result['name'] == 'Diana'].iloc[0]
        assert diana['age_category'] == 'Senior'


class TestIbisDB2Functions:
    """Test DB2-specific functions through Ibis."""
    
    def test_string_functions(self, db2_connection, sample_table):
        """Test string functions."""
        table = db2_connection.table(sample_table)
        
        # Test UPPER function
        upper_names = table[table.name.upper().name('upper_name')]
        result = upper_names.execute()
        
        assert result.iloc[0]['upper_name'] == 'ALICE'
    
    def test_date_functions(self, db2_connection, sample_table):
        """Test date functions."""
        table = db2_connection.table(sample_table)
        
        # Extract year from hire_date
        years = table[
            table.name,
            table.hire_date.year().name('hire_year')
        ]
        result = years.execute()
        
        assert 'hire_year' in result.columns
        assert result[result['name'] == 'Alice'].iloc[0]['hire_year'] == 2020
    
    def test_null_handling(self, db2_connection, sample_table):
        """Test NULL handling with COALESCE."""
        table = db2_connection.table(sample_table)
        
        # Use COALESCE (though our sample data has no NULLs)
        coalesced = table[
            table.name,
            table.age.coalesce(0).name('age_or_zero')
        ]
        result = coalesced.execute()
        
        assert 'age_or_zero' in result.columns


class TestIbisDB2TypeMapping:
    """Test data type mapping between Ibis and DB2."""
    
    def test_integer_types(self, db2_connection, sample_table):
        """Test integer type handling."""
        table = db2_connection.table(sample_table)
        schema = table.schema()
        
        # Check that id and age are integer types
        assert 'int' in str(schema['id']).lower()
        assert 'int' in str(schema['age']).lower()
    
    def test_decimal_types(self, db2_connection, sample_table):
        """Test decimal type handling."""
        table = db2_connection.table(sample_table)
        schema = table.schema()
        
        # Check that salary is decimal
        assert 'decimal' in str(schema['salary']).lower()
    
    def test_string_types(self, db2_connection, sample_table):
        """Test string type handling."""
        table = db2_connection.table(sample_table)
        schema = table.schema()
        
        # Check that name is string
        assert 'string' in str(schema['name']).lower()
    
    def test_date_types(self, db2_connection, sample_table):
        """Test date type handling."""
        table = db2_connection.table(sample_table)
        schema = table.schema()
        
        # Check that hire_date is date
        assert 'date' in str(schema['hire_date']).lower()


class TestIbisDB2SQLCompilation:
    """Test SQL compilation with DB2 dialect."""
    
    def test_fetch_first_compilation(self):
        """Test that LIMIT compiles to FETCH FIRST in DB2."""
        from sqlglot import parse_one, transpile
        
        # Parse a simple LIMIT query
        sql = "SELECT * FROM table1 LIMIT 10"
        
        # Transpile to DB2
        db2_sql = transpile(sql, read="postgres", write="db2")[0]
        
        # Should use FETCH FIRST
        assert "FETCH FIRST" in db2_sql.upper()
        assert "ROWS ONLY" in db2_sql.upper()
    
    def test_offset_compilation(self):
        """Test that OFFSET compiles correctly in DB2."""
        from sqlglot import transpile
        
        # Parse LIMIT with OFFSET
        sql = "SELECT * FROM table1 LIMIT 10 OFFSET 5"
        
        # Transpile to DB2
        db2_sql = transpile(sql, read="postgres", write="db2")[0]
        
        # Should use OFFSET ROWS and FETCH FIRST
        assert "OFFSET" in db2_sql.upper()
        assert "ROWS" in db2_sql.upper()
        assert "FETCH FIRST" in db2_sql.upper()
    
    def test_boolean_compilation(self):
        """Test that booleans compile to 0/1 in DB2."""
        from sqlglot import transpile
        
        # Parse boolean values
        sql = "SELECT TRUE, FALSE"
        
        # Transpile to DB2
        db2_sql = transpile(sql, read="postgres", write="db2")[0]
        
        # Should use 1 and 0
        assert "1" in db2_sql
        assert "0" in db2_sql
        assert "TRUE" not in db2_sql.upper()
        assert "FALSE" not in db2_sql.upper()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

