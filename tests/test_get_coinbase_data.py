"""
Testing for getting data from coinbase
"""
from fractions import Fraction as frac
import pytest as pt
from lib.get_coinbase_data import get_coinbase_data

def test_connection():
    """
    Test that we can connect at all and get data back
    """
    cb_data = get_coinbase_data(start_date='2018-01-01-00-00', end_date='2018-01-1-01-00')
    assert not cb_data.empty

def test_results():
    """
    Test that the results are in the expected output format
    """
    cb_data = get_coinbase_data(start_date='2018-01-01-00-00', end_date='2018-01-1-01-00')
    # assert columns are expected 
    assert list(cb_data.columns) == ['index', 'timestamp', 'fraction_price', 'decimal_price']


def test_data():
    """
    Verify that we get the expected amount of data from a repeated query
    """
    cb_data = get_coinbase_data(start_date='2018-01-01-00-00', end_date='2018-01-1-05-00')
    # assert columns are expected
    # index,timestamp,fraction_price,decimal_price
    # 0,1514764800,30539155363803955/70368744177664,433.9875
    expected_timestamp = 1514764860
    expected_fraction_price = frac('30539155363803955/70368744177664')
    expected_decimal_price = 433.9875
    assert cb_data['timestamp'].values[0] == expected_timestamp
    assert cb_data['fraction_price'].values[0] == expected_fraction_price
    assert cb_data['decimal_price'].values[0] == expected_decimal_price

if __name__ == "__main__":
    pt.main(['tests/test_get_coinbase_data.py'])
