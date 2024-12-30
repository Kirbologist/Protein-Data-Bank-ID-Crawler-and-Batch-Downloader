"""
This script contains integration tests for testing the integration of
database.py with its dependent modules, such as table.py, attributes.py and sqlite3.
Make sure to run from the Phase 2 directory for the correct relative paths.

To run a specific test module, use the command "pytest test/integration/test_something.py".
To run all tests in the test directory, use the command "pytest test/".
Output verbosity can be adjusted by using the relevant flags in the command (e.g. -q, -v, -vv).
"""
import pytest
import sqlite3
import database
from database import table_schemas

table_names = [table.name for table in table_schemas]

@pytest.fixture
def setup_database(database_table_schemas, database_test_data):
    # set up database connection  
    con = sqlite3.connect(':memory:')
    cur = con.cursor()

    # create all tables 
    for table in database_table_schemas:
        cur.execute(table.create_table())

    # insert data into all tables 
    for table_name, test_data in database_test_data.items():
        args = ', '.join(['?' for i in range(len(test_data))])
        query = f'INSERT INTO {table_name} VALUES({args})'
        cur.execute(query, test_data)
    con.commit()

    yield cur
    # Close database connection after all tests are run
    con.close() 


@pytest.fixture
def setup_database_multiple_rows(database_table_schemas, database_test_data_multiple_rows):
    # set up database connection  
    con = sqlite3.connect(':memory:')
    cur = con.cursor()

    # create all tables 
    for table in database_table_schemas:
        cur.execute(table.create_table())

    # insert data into all tables 
    for table_name, test_data in database_test_data_multiple_rows.items():
        for data in test_data:
            args = ', '.join(['?' for i in range(len(data))])
            query = f'INSERT INTO {table_name} VALUES({args})'
            cur.execute(query, data)
    con.commit()

    yield cur
    # Close database connection after all tests are run
    con.close() 


def test_create_tables_with_valid_schemas(database_table_schemas):
    """
    Test that the table schemas defined in database.py 
    contain the expected attributes when created in SQLite. 
    """
    # set up database connection
    con = sqlite3.connect(':memory:')
    cur = con.cursor()

    # create all tables 
    for table in database_table_schemas:
        cur.execute(table.create_table())

    # verify structure of each table 
    for table in database_table_schemas:
        cur.execute(f"PRAGMA table_info({table.name})")
        schema_info = cur.fetchall()

        column_names = [row[1] for row in schema_info]
        column_types = [row[2] for row in schema_info]
        is_not_null = [row[3] for row in schema_info]

        expected_column_names = list(table.attributes.attribute_names)
        expected_column_types = [attr_type.replace(" NOT NULL", "") for attr_type in table.attributes.attribute_types]
        expected_is_not_null = ["NOT NULL" in attr_type for attr_type in table.attributes.attribute_types]

        assert column_names == expected_column_names, f"{table.name}"
        assert column_types == expected_column_types, f"{table.name}"
        assert is_not_null == expected_is_not_null, f"{table.name}"

    # close database connection 
    con.close()


@pytest.mark.parametrize("table_name", table_names)
def test_insert_into_table(table_name, database_test_data, database_table_schemas):
    """
    Test that the insert_into_table function correctly 
    inserts data into the database for each table in table_schemas. 
    """
    # set up database connection  
    con = sqlite3.connect(':memory:')
    cur = con.cursor()

    # create all tables 
    for table in database_table_schemas:
        cur.execute(table.create_table())

    # insert data into table
    test_data = database_test_data[table_name]
    database.insert_into_table(cur, table_name, test_data)

    res = cur.execute(f"SELECT * FROM {table_name}")
    inserted_data = res.fetchone()

    assert test_data == inserted_data, f"{table_name}"


@pytest.mark.parametrize("table_name", table_names)
def test_insert_into_table_invalid_data(table_name, database_test_data, database_table_schemas):
    """
    Test that an OperationalError is raised if the number of data values 
    given does not match the number of columns in the table. 
    """
    # set up database connection  
    con = sqlite3.connect(':memory:')
    cur = con.cursor()

    # create all tables 
    for table in database_table_schemas:
        cur.execute(table.create_table())

    with pytest.raises(sqlite3.OperationalError):
        # insert incomplete data into a table
        test_data = database_test_data[table_name][:-1]
        database.insert_into_table(cur, table_name, test_data)


def test_insert_into_table_invalid_table(database_table_schemas):
    """
    Test that an OperationalError is raised if data is inserted 
    into a table that does not exist. 
    """
    # set up database connection  
    con = sqlite3.connect(':memory:')
    cur = con.cursor()

    # create all tables 
    for table in database_table_schemas:
        cur.execute(table.create_table())

    with pytest.raises(sqlite3.OperationalError):
        # insert data into an invalid table
        table_name = "invalid_table"
        test_data = ("1A00", "NucleicAcid", "mock_title", "mock_org", "2000-01-01", "A A", "P 1",
            1, 1.0, 1.0, 1.0, 90.0, 90.0, 90.0)
        database.insert_into_table(cur, table_name, test_data)


@pytest.mark.parametrize("table_name", table_names)
def test_retrieve_from_table_single_row(table_name, setup_database, database_test_data):
    """
    Test that the retrieve_table function retrieves the correct data 
    for every table in table_schemas, each containing a single row with a given entry_id. 
    """
    cur = setup_database
    entry_id = "1A00"

    result = database.retrieve_from_table(cur, table_name, entry_id)
    expected = database_test_data[table_name]

    assert result == [expected], f"{table_name}"


@pytest.mark.parametrize("table_name", table_names[2:])
def test_retrieve_from_table_multiple_rows(table_name, setup_database_multiple_rows, database_test_data_multiple_rows):
    """
    Test that the retrieve_table function returns the correct data 
    for tables containing multiple rows with the same entry_id 
    (all tables in table_schemas excluding main and experimental). 
    """
    cur = setup_database_multiple_rows
    entry_id = "1A00"

    result = database.retrieve_from_table(cur, table_name, entry_id)
    expected = database_test_data_multiple_rows[table_name]

    assert result == expected, f"{table_name}"


def test_retrieve_from_table_invalid_table(setup_database):
    """
    Test that an OperationalError is raised if data is retrieved 
    from a table that does not exist. 
    """
    table_name = "invalid_table"
    cur = setup_database
    entry_id = "1A00"

    with pytest.raises(sqlite3.OperationalError):
        database.retrieve_from_table(cur, table_name, entry_id)


@pytest.mark.parametrize("table_name", table_names)
def test_retrieve_from_table_invalid_entry_id(table_name, setup_database):
    """
    Test that the retrieve_from_table function returns an empty list
    if data is retrieved for an entry ID that does not exist in each table in table_schemas.   
    """
    cur = setup_database
    entry_id = "invalid_id"

    
    result = database.retrieve_from_table(cur, table_name, entry_id)
    expected = []

    assert result == expected
