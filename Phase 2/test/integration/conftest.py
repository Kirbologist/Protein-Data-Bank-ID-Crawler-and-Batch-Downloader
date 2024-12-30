import pytest
from unittest.mock import MagicMock
import gemmi
from gemmi import cif
import sqlite3

import database
from database import table_schemas
from table import Table
from attributes import Attributes
from polymer_sequence import PolymerSequence


@pytest.fixture(scope="module")
def database_test_data():
    test_data = {
        "main": ('1A00', "NucleicAcid", "mock_title", "mock_org", "2000-01-01", "A A", "P 1",
            1, 1.0, 1.0, 1.0, 90.0, 90.0, 90.0),
        "experimental": ('1A00', 1.0, 1.0, 'mock_growth_method', 'mock_growth_proc', 'mock_growth_apparatus', 
            'mock_growth_atmosophere', 7.0, 200.0),
        "entities": ('1A00', '1', 'mock_entity_one', 'Polymer', 'PeptideD', 'A'), 
        "chains": ('1A00', 'A', 'A A', 0, 'ARNDCQEGHIX', 'ARNDCQEGHIX', 1, 11, 11),
        "subchains": ('1A00', '1', 'A', 'A', 'ARNDCQEGHIX', 'ARNDCQEGHIX', 1, 11, 11),
        "helices": ('1A00', 1, 'A', 'ARNDCQEGHIX', 1, 11, 11),
        "sheets": ('1A00', 'A', 1, 'P'),
        "strands": ('1A00', 'A', '1', 'A', 'ARNDCQEGHIX', 1, 11, 11),
        "coils": ('1A00', 1, "A", 0, "SUBSEQ", "SUBSEQ", 6, 10, 6)
    }
    return test_data


@pytest.fixture(scope="module") 
def database_test_data_multiple_rows():
    # main and experimental cannot have rows with duplicate entry ID 
    test_data = {
        "main": [('1A00', "NucleicAcid", "mock_title", "mock_org", "2000-01-01", "A A", "P 1",
            1, 1.0, 1.0, 1.0, 90.0, 90.0, 90.0)],
        "experimental": [('1A00', 1.0, 1.0, 'mock_growth_method', 'mock_growth_proc', 'mock_growth_apparatus', 
            'mock_growth_atmosophere', 7.0, 200.0)],
        "entities": [('1A00', '1', 'mock_entity_one', 'Polymer', 'PeptideD', 'A'),
                     ('1A00', '2', 'mock_entity_two', 'Polymer', 'PeptideD', 'A')], 
        "chains": [('1A00', 'A', 'A A', 0, 'ARNDCQEGHIX', 'ARNDCQEGHIX', 1, 11, 11),
                   ('1A00', 'B', 'A A', 0, 'ARNDCQEGHIX', 'ARNDCQEGHIX', 1, 11, 11)],
        "subchains": [('1A00', '1', 'A', 'A', 'ARNDCQEGHIX', 'ARNDCQEGHIX', 1, 11, 11),
                      ('1A00', '1', 'B', 'B', 'ARNDCQEGHIX', 'ARNDCQEGHIX', 1, 11, 11)],
        "helices": [('1A00', 1, 'A', 'ARNDCQEGHIX', 1, 11, 11),
                    ('1A00', 2, 'A', 'ARNDCQEGHIX', 1, 11, 11)],
        "sheets": [('1A00', 'A', 1, 'P'),
                   ('1A00', 'B', 1, 'P')],
        "strands": [('1A00', 'A', '1', 'A', 'ARNDCQEGHIX', 1, 11, 11),
                    ('1A00', 'A', '2', 'A', 'ARNDCQEGHIX', 1, 11, 11)],
        "coils": [('1A00', 1, "A", 0, "SUBSEQ", "SUBSEQ", 6, 10, 6),
                  ('1A00', 2, "A", 0, "SUBSEQ", "SUBSEQ", 6, 10, 6)]
    }
    return test_data


@pytest.fixture(scope="module") 
def database_table_schemas():
    return table_schemas


@pytest.fixture
def test_structure():
    gemmi_structure = gemmi.Structure()
    return gemmi_structure


@pytest.fixture
def test_document():
    cif_document = cif.read_string("""
        data_test
        loop_
        _pdbx_poly_seq_scheme.pdb_strand_id
        _pdbx_poly_seq_scheme.entity_id
        _pdbx_poly_seq_scheme.seq_id
        _pdbx_poly_seq_scheme.mon_id
        _pdbx_poly_seq_scheme.pdb_mon_id
        _pdbx_poly_seq_scheme.hetero
        A 1 1 MET MET n
        A 1 2 ALA ALA n
        A 1 3 GLY GLY y
    """)
    return cif_document


def test_polymer_sequence(test_document):
    return PolymerSequence(test_document)

@pytest.fixture
def test_attributes():
    attribute_pairs = [
        ("entry_id", "VARCHAR"), 
        ("chain_id", "VARCHAR"),
        ("start_id", "INT"), 
        ("end_id", "INT")
    ]
    primary_keys = ["entry_id", "chain_id"]
    foreign_keys = {"entry_id": ("main", "entry_id")}

    return Attributes(attribute_pairs, primary_keys, foreign_keys)


@pytest.fixture 
def attributes_with_one_attribute():
    attribute_pairs = [("entry_id", "VARCHAR")]
    primary_keys = ["entry_id"]
    foreign_keys = {"entry_id": ("main", "entry_id")}

    return Attributes(attribute_pairs, primary_keys, foreign_keys)


@pytest.fixture
def test_extractor():
    def extractor_stub(struct: gemmi.Structure, doc: cif.Document, sequence: PolymerSequence):
        return [
            ("1A00", "1", 1, 2),
            ("1A00", "2", 1, 2)
        ]
    return extractor_stub


@pytest.fixture
def test_table(test_attributes, test_extractor):
    return Table("test_table", test_attributes, test_extractor)