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
    # assert we get data
    assert not binance_data.empty

def test_data():
    """
    Verify that we get the expected amount of data from a repeated query
    """
    binance_data = get_binance_data(start_date='2018-01-01-00-00-00', end_date='2018-01-01-05-00-00')
    # Limit data to first 3 returned values for simplicity
    binance_data = binance_data.head(3)
    
    # assert column names are expected
    assert binance_data.columns.tolist() == ['timestamp', 'fraction_price', 'decimal_price']
    assert binance_data.index.name == 'index'
    # assert data is expected
    assert binance_data['timestamp'].tolist() == [1514793600, 1514793660, 1514793720]
    assert binance_data['fraction_price'].tolist() == [
        frac('3302449144722883/4398046511104'),
        frac('6598037336888443/8796093022208'),
        frac('3298754785653555/4398046511104')
    ]
    assert binance_data['decimal_price'].tolist() == [750.890, 750.110, 750.050]

if __name__ == "__main__":
    pt.main(['tests/test_get_binance_data.py'])
