"""
Easy way to run all tests.
"""
import pytest as pt

# not a test
def get_test_data_path(csv):
    """Path to test data csv files."""
    # Make sure we have the file ending
    if csv[-4:] != '.csv':
        csv = csv + '.csv'
    return f'tests\\test_data\\{csv}'

if __name__ == "__main__":
    pt.main()
