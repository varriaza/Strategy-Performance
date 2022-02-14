"""
Testing for getting data from binance
"""
from fractions import Fraction as frac
import pytest as pt
from lib.get_binance_data import get_binance_data

def test_connection_and_results():
    """
    Test that we can connect at all and get data back in roughly the format we want
    """
    binance_data = get_binance_data(start_date='2018-01-01-00-00-00', end_date='2018-01-01-01-00-00')
    # assert we have enough expected rows in our list of lists
    assert len(binance_data) > 0
    # make sure we have data in the first list, we only use the first 5 values
    assert len(binance_data[0]) > 4

def test_data():
    """
    Verify that we get the expected amount of data from a repeated query
    """
    binance_data = get_binance_data(start_date='2018-01-01-00-00-00', end_date='2018-01-01-05-00-00')
    # assert columns are expected
    # index,timestamp,fraction_price,decimal_price
    # [1514793600000, '751.77000000', '751.77000000', '750.01000000', '750.01000000', ...]
    expected_timestamp = 1514793600000
    expected_fraction_price = frac((751.77000000 + 751.77000000 + 750.01000000 + 750.01000000)/4)
    assert binance_data[0][0] == expected_timestamp
    binance_price = frac(
        float(binance_data[0][1])+
        float(binance_data[0][2])+
        float(binance_data[0][3])+
        float(binance_data[0][4])
    )/4
    assert binance_price == expected_fraction_price

if __name__ == "__main__":
    pt.main(['tests/test_get_binance_data.py'])