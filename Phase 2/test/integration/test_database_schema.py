

import pytest
import sqlite3

import commands

@pytest.fixture(scope="module")
def setup_database():
    # set up database 
    con = sqlite3.connect(':memory:')
    cur = con.cursor()
    commands.init_database(cur)

    yield cur
    # Close database connection after all tests are run
    con.close() 


def test_create_tables_with_valid_schemas(setup_database, database_table_schemas):
    """
    Test that database schema matches the expected structure. 
    """
    cur = setup_database

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
