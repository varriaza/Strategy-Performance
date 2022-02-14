"""
Testing for the base dca strategy class
"""
import pytest as pt
import pandas as pd
from test_all_tests import get_test_data_path
import lib.base_strategy as bs
from specific_strategies import dca

def test_1_day():
    """
    Test that buying every day returns expected results
    """
    # Set default buy size to be 10k
    starting_usd = 10000
    # Seconds in a day
    seconds_in_a_day = 60*60*24
    # Number of days between dollar cost average buys
    days = 1
    # Turns days into seconds
    days = days*seconds_in_a_day
    price_df = pd.read_csv(get_test_data_path('test'))
    dca_strategy = dca.base_dca(
        starting_usd=starting_usd,
        time_between_action=days,
        price_period_name='test',
        price_df=price_df,
        save_results=False
    )
    dca_strategy.run_logic()
    # begin tests
    # make sure we are at the end of the time period
    assert dca_strategy.current_time == dca_strategy.price_df['timestamp'].values[-1]
    assert dca_strategy.current_index == dca_strategy.price_df.index[-1]
    # we should always end up with no USD left
    assert dca_strategy.current_usd == 0
    # make sure we end up with the expected amount of ETH
    expected_eth = 11.8226
    assert bs.unfrac(dca_strategy.current_eth) == bs.unfrac(expected_eth)

def test_longer_than_price_period():
    """
    Test that trying to buy with a period of longer than the price period returns an error
    """
    # Set default buy size to be 10k
    starting_usd = 10000
    # Seconds in a day
    seconds_in_a_day = 60*60*24
    # Number of days between dollar cost average buys
    days = 28
    # Turns days into seconds
    days = days*seconds_in_a_day
    price_df = pd.read_csv(get_test_data_path('test'))
    dca_strategy = dca.base_dca(
        starting_usd=starting_usd,
        time_between_action=days,
        price_period_name='test',
        price_df=price_df,
        save_results=False
    )
    try:
        dca_strategy.run_logic()
        passed = False
    except ValueError:
        passed = True
    assert passed

def test_28_days():
    """
    Test that buying every 28 days returns expected results
    """
    # Set default buy size to be 10k
    starting_usd = 10000
    # Seconds in a day
    seconds_in_a_day = 60*60*24
    # Number of days between dollar cost average buys
    days = 28
    # Turns days into seconds
    days = days*seconds_in_a_day
    price_df = pd.read_csv(get_test_data_path('test_month'))
    dca_strategy = dca.base_dca(
        starting_usd=starting_usd,
        time_between_action=days,
        price_period_name='test_month',
        price_df=price_df,
        save_results=False
    )
    dca_strategy.run_logic()
    # begin tests
    # make sure we are at the end of the time period
    assert dca_strategy.current_time == dca_strategy.price_df['timestamp'].values[-1]
    assert dca_strategy.current_index == dca_strategy.price_df.index[-1]
    # we should always end up with no USD left
    assert dca_strategy.current_usd == 0
    # make sure we end up with the expected amount of ETH
    expected_eth = 9.9468
    assert bs.unfrac(dca_strategy.current_eth) == bs.unfrac(expected_eth)

if __name__ == "__main__":
    pt.main(['tests/test_dca.py'])
