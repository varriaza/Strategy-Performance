"""
Testing for the init_data_helper.py script
"""
from fractions import Fraction as frac
import pandas as pd
import numpy as np
import pytest as pt
from test_all_tests import get_test_data_path
import lib.init_data_helper as idh

def test_compare_dataset_timestamps():
    """
    Make sure that we can find where timestamps are unique between two df.
    """
    df1 = pd.read_csv(get_test_data_path('test_final_csv_df1.csv'))
    df2 = pd.read_csv(get_test_data_path('test_final_csv_df2.csv'))
    df1_unique, df2_unique = idh.compare_dataset_timestamps(df1, df2, debug=True)
    assert list(df1_unique.values) == [1514765160, 1514765220, 1514765340]
    assert list(df2_unique.values) == [1514765040, 1514765100, 1514765400]

def test_check_missing_timestamp_1():
    """
    See if each timestamp has another one sixty seconds after it except for the last one.
    Looks at file: test_timestamp_gaps_1.csv
    """
    # df3 = pd.read_csv(get_test_data_path('test_initial_price_df.csv'))
    df3 = pd.read_csv(get_test_data_path('test_timestamp_gaps_1.csv'))
    results = idh.check_missing_timestamp(df3, debug=True)
    assert list(results.values) == [180, 300]

def test_check_missing_timestamp_2():
    """
    See if each timestamp has another one sixty seconds after it except for the last one.
    Looks at file: test_timestamp_gaps_2.csv
    """
    df4 = pd.read_csv(get_test_data_path('test_timestamp_gaps_2.csv'))
    results = idh.check_missing_timestamp(df4, debug=True)
    assert list(results.values) == [360, 536]

def test_fraction_make_average():
    """fraction_price scenarios"""
    # Test if first one is null
    frac_null_1 = pd.Series({'index':0,'timestamp_1':1514764860,'timestamp_2':1514764860,
        'fraction_price_1':np.nan, 'fraction_price_2':'25/10',
        'decimal_price_1':30.1, 'decimal_price_2':30.1})
    result = idh.make_average(frac_null_1, 'fraction_price')
    assert result['fraction_price'] == frac('25/10')
    # Test if second one is null
    frac_null_2 = pd.Series({'index':0,'timestamp_1':1514764860,'timestamp_2':1514764860,
        'fraction_price_1':'25/10', 'fraction_price_2':np.nan,
        'decimal_price_1':30.1, 'decimal_price_2':30.1})
    result = idh.make_average(frac_null_2, 'fraction_price')
    assert result['fraction_price'] == frac('25/10')
    # Test if both are not null
    frac_both = pd.Series({'index':0,'timestamp_1':1514764860,'timestamp_2':1514764860,
        'fraction_price_1':'20/10', 'fraction_price_2':'30/10',
        'decimal_price_1':30.1, 'decimal_price_2':30.1})
    result = idh.make_average(frac_both, 'fraction_price')
    assert result['fraction_price'] == frac('5/2')

def test_decimal_make_average():
    """decimal_price scenarios"""
    # Test if first one is null
    deci_null_1 = pd.Series({'index':0,'timestamp_1':1514764860,'timestamp_2':1514764860,
        'fraction_price_1':'25/10', 'fraction_price_2':'25/10',
        'decimal_price_1':np.nan, 'decimal_price_2':30.1})
    result = idh.make_average(deci_null_1, 'decimal_price')
    assert result['decimal_price'] == 30.1
    # Test if second one is null
    deci_null_2 = pd.Series({'index':0,'timestamp_1':1514764860,'timestamp_2':1514764860,
        'fraction_price_1':'25/10', 'fraction_price_2':'25/10',
        'decimal_price_1':30.1, 'decimal_price_2':np.nan})
    result = idh.make_average(deci_null_2, 'decimal_price')
    assert result['decimal_price'] == 30.1
    # Test if both are not null
    deci_both = pd.Series({'index':0,'timestamp_1':1514764860,'timestamp_2':1514764860,
        'fraction_price_1':'25/10', 'fraction_price_2':'25/10',
        'decimal_price_1':29, 'decimal_price_2':28})
    result = idh.make_average(deci_both, 'decimal_price')
    assert result['decimal_price'] == 28.5

def test_combine_datasets():
    """
    Test that when we combine two dataframes, we get null values replaces correctly
    and averages done correctly.
    """
    df1 = pd.read_csv(get_test_data_path('test_final_csv_df1.csv'))
    df2 = pd.read_csv(get_test_data_path('test_final_csv_df2.csv'))
    results = idh.combine_datasets(df1, df2)
    print(f'Results:\n{results}\n')
    # Make sure we only get the columns that we expect back, index is not returned by columns
    assert list(results.columns) == ['index', 'timestamp', 'fraction_price', 'decimal_price']
    # Assert timestamps values are what we expect
    assert list(results['timestamp'].values) == [
        1514764860, 1514764920, 1514764980, 1514765040, 1514765100,
        1514765160, 1514765220, 1514765280, 1514765340, 1514765400
    ]
    # Assert fraction_price values are what we expect
    assert list(results['fraction_price'].values) == [
        frac('25/10'), frac('26/10'), frac('25/10'), frac('31/10'), frac('27/10'),
        frac('27/10'), frac('28/10'), frac('5/2'), frac('30/10'), frac('20/10')
    ]
    # Assert decimal_price values are what we expect
    assert list(results['decimal_price'].values) == [
        30.1, 31.1, round((20.5+32.1)/2, 4), 33.1, 34.1, 35.1, 36.1, 25.0, 30.4, 20.2
    ]

if __name__ == "__main__":
    pt.main(['tests/test_init_data_helper.py'])
