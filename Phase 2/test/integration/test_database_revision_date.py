"""
This file contains integration tests for validating that the database is up to date, 
using data fetched from PDB's RESTful API.
Make sure to run from the Phase 2 directory for the correct relative paths.

To run a specific test module, use the command "pytest test/integration/test_something.py.
To run all tests in the test directory, use the command "pytest test/".
Output verbosity can be adjusted by using the relevant flags in the command (e.g. -q, -v, -vv).
For this test, the progress bar can be shown by adding the -s flag i.e. pytest -s test/integration/test_something.py
"""
import pytest
import sqlite3
import requests
from tqdm import tqdm
import requests_cache
import concurrent.futures

# from main import sql_database

sql_database = "./records/pdb_database_records_1.4.db"  # Location of SQL database 

# Cache data for repeated calls
requests_cache.install_cache('api_cache', expire_after=7200)  

@pytest.fixture(scope="module")
def main_data():
    """
    Fixture to select all (or a specified number of rows) from the main table in the database.
    """
    # Connect to the database
    con = sqlite3.connect(sql_database)
    try:
        rows = 1000
        # select all rows from main
        cursor = con.cursor()
        cursor.execute("SELECT * FROM main")  
        data = cursor.fetchall()
        return data[:rows] 
        
    except Exception as error:
        print(error)
    finally:
        # Ensure the connection is closed
        con.close()


def make_request(entry_id: str = ""):
    """
    Make a request to retrieve PDB entry data through an endpoint.
    """
    try:
        url = f"https://data.rcsb.org/rest/v1/core/entry/{entry_id}"
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed for {entry_id}: ", e)
        return {}
    

def fetch_revision_date(entry_id: str):
    """
    Fetch the latest revision date for a given entry id. 
    Return an empty string if not found in the JSON records.
    """
    main_data = make_request(entry_id=entry_id)

    revision_history = main_data.get("pdbx_audit_revision_history", [])
    if revision_history:
        latest_revision_history = revision_history[-1]
        latest_revision_date = latest_revision_history["revision_date"]
        return latest_revision_date.partition('T')[0]  # retrieve only the date and ignore the time 
    return ''


def validate_revision_date(entry_id: str, revision_date: str):
    """
    Validate the revision date stored in the database against the
    date retrieved from the API, for a given entry ID.
    """
    expected_revision_date = fetch_revision_date(entry_id)
    result_revision_date = revision_date
    assert expected_revision_date <= result_revision_date, f"Entry ID {entry_id}: Remote: {expected_revision_date}, Database: {result_revision_date}"


def test_database_is_up_to_date(main_data):
    errors = []
    
    with tqdm(total=len(main_data), desc="Validating database entries") as progress:
        for row in main_data:
            entry_id, revision_date = row[0], row[4]
            try:
                expected_revision_date = fetch_revision_date(entry_id)
                result_revision_date = revision_date
                assert expected_revision_date <= result_revision_date, f"Remote: {expected_revision_date}, Database: {result_revision_date}"
            except AssertionError as e:
                errors.append(f"Entry ID {entry_id} failed validation: {str(e)}")
            progress.update(1)
    
    if errors:
        raise AssertionError(f"The following entries failed validation:\n" + "\n".join(errors))