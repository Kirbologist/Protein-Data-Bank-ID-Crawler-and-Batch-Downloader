"""
This script contains integration tests for testing the integration of
the Table class with its dependent modules, such as attributes.py and polymer_sequence.py.
Make sure to run from the Phase 2 directory for the correct relative paths.

To run a specific test module, use the command "pytest test/integration/test_something.py".
To run all tests in the test directory, use the command "pytest test/".
Output verbosity can be adjusted by using the relevant flags in the command (e.g. -q, -v, -vv).
"""
from unittest.mock import MagicMock
import pytest

from table import Table

def test_table_initialisation(test_table, test_attributes, test_extractor):
    assert test_table.name == "test_table"
    assert test_table.attributes == test_attributes
    assert test_table.extractor == test_extractor


def test_attributes_string(test_table):
    result = test_table.attributes_string()
    expected = "(entry_id, chain_id, start_id, end_id)"

    assert result == expected


def test_attributes_string_attributes_with_one_attribute(attributes_with_one_attribute):
    mock_extractor = MagicMock()
    test_table = Table("test_table", attributes_with_one_attribute, mock_extractor)
    result = test_table.attributes_string()
    expected = "(entry_id)"

    assert result == expected
    
    
def test_create_table(test_table):
    expected = (
        "CREATE TABLE IF NOT EXISTS test_table (entry_id VARCHAR, chain_id VARCHAR, start_id INT, end_id INT, " 
        "PRIMARY KEY (entry_id, chain_id), FOREIGN KEY (entry_id) REFERENCES\
                                        main (entry_id))"
    )
    result = test_table.create_table()

    assert result == expected


def test_retrieve_default_columns(test_table):
    expected = "SELECT * FROM test_table"
    result = test_table.retrieve()

    assert result == expected


def test_retrieve_columns_specified(test_table):
    test_columns = ("entry_id", "chain_id")
    expected = "SELECT entry_id, chain_id FROM test_table"
    result = test_table.retrieve(test_columns)

    assert result == expected


def test_retrieve_invalid_columns(test_table):
    test_columns = (1, 2)  # invalid as it is a tuple of ints
    with pytest.raises(TypeError):
        test_table.retrieve(test_columns)


def test_extract_data(test_table, test_structure, test_document, test_polymer_sequence, test_extractor):
    result = test_table.extract_data(test_structure, test_document, test_polymer_sequence)
    expected = [
        ("1A00", "1", 1, 2),
        ("1A00", "2", 1, 2)
    ]
    
    assert result == expected 


def test_insert_row(test_table):
    test_data = ("1A00", "1", 1, 2)
    result = test_table.insert_row(test_data)
    expected = "INSERT INTO test_table VALUES(?, ?, ?, ?)"

    assert result == expected 
    

def test_update_row(test_table):
    test_data = {"start_id": "value1", "end_id": "value2"}
    test_primary_key_values = ["1", "1"]
    expected = "UPDATE test_table SET start_id = value1, end_id = value2\
            WHERE entry_id = 1 AND chain_id = 1"
    result = test_table.update_row(test_data, test_primary_key_values)

    assert result == expected


def test_update_row_invalid_columns(test_table):
    test_data = {"start_id": "value1", "invalid_col": "value2"}
    test_primary_key_values = ["1", "1"]
    with pytest.raises(ValueError, match="Argument contains columns not part of the table"):
        test_table.update_row(test_data, test_primary_key_values)


def test_update_row_invalid_primary_keys(test_table):
    test_data = {"start_id": "value1", "end_id": "value2"}
    test_primary_key_values = ["1", "1", "1"]
    with pytest.raises(ValueError, match="Number of values given does not match number of keys"):
        test_table.update_row(test_data, test_primary_key_values)