"""
Testing for the base all_in_top strategy class
"""
import pytest as pt
import pandas as pd
import lib.base_strategy as bs
from specific_strategies import all_in_top
from test_all_tests import get_test_data_path

def test_all_in_top_start_max():
    """
    Test that having a max at the start returns expected results
    """
    # Set default buy size to be 10k
    starting_usd = 10000
    # Seconds in a day
    seconds_in_a_day = 60*60*24
    # Number of days
    days = 1
    # Turns days into seconds
    days = days*seconds_in_a_day
    price_df = pd.read_csv(get_test_data_path('test_start_max_end_min'))
    all_in_top_strategy = all_in_top.base_all_in_top(
        starting_usd=starting_usd,
        time_between_action=days,
        price_period_name='test_start_max_end_min',
        price_df=price_df,
        save_results=False
    )
    all_in_top_strategy.run_logic()
    # begin tests
    # make sure we are at the end of the time period
    assert all_in_top_strategy.current_time == all_in_top_strategy.price_df['timestamp'].values[-1]
    assert all_in_top_strategy.current_index == all_in_top_strategy.price_df.index[-1]
    # we should start with no USD left
    assert all_in_top_strategy.returns_df['# of USD'].iloc[0] == 0
    # we should always end up with no USD left
    assert all_in_top_strategy.current_usd == 0
    # make sure we end up with the expected amount of ETH
    expected_eth = 1.0095
    assert bs.unfrac(all_in_top_strategy.current_eth) == expected_eth

def test_all_in_top_end_max():
    """
    Test that having a max at the end returns expected results
    """
    # Set default buy size to be 10k
    starting_usd = 10000
    # Seconds in a day
    seconds_in_a_day = 60*60*24
    # Number of days
    days = 1
    # Turns days into seconds
    days = days*seconds_in_a_day
    price_df = pd.read_csv(get_test_data_path('test_start_min_end_max'))
    all_in_top_strategy = all_in_top.base_all_in_top(
        starting_usd=starting_usd,
        time_between_action=days,
        price_period_name='test_start_min_end_max',
        price_df=price_df,
        save_results=False
    )
    all_in_top_strategy.run_logic()
    # begin tests
    # make sure we are at the end of the time period
    assert all_in_top_strategy.current_time == all_in_top_strategy.price_df['timestamp'].values[-1]
    assert all_in_top_strategy.current_index == all_in_top_strategy.price_df.index[-1]
    # we should always end up with no USD left
    assert all_in_top_strategy.current_usd == 0
    # make sure we end up with the expected amount of ETH
    expected_eth = 1.0095
    assert bs.unfrac(all_in_top_strategy.current_eth) == expected_eth

def test_all_in_top_middle_max():
    """
    Test that having a max in the middle returns expected results
    Uses test_month.csv as data.
    """
    # Set default buy size to be 10k
    starting_usd = 10000
    # Seconds in a day
    seconds_in_a_day = 60*60*24
    # Number of days
    days = .5
    # Turns days into seconds
    days = days*seconds_in_a_day
    price_df = pd.read_csv(get_test_data_path('test_month'))
    all_in_top_strategy = all_in_top.base_all_in_top(
        starting_usd=starting_usd,
        time_between_action=days,
        price_period_name='test_month',
        price_df=price_df,
        save_results=False
    )
    all_in_top_strategy.run_logic()
    # begin tests
    # make sure we are at the end of the time period
    assert all_in_top_strategy.current_time == all_in_top_strategy.price_df['timestamp'].values[-1]
    assert all_in_top_strategy.current_index == all_in_top_strategy.price_df.index[-1]
    # we should always end up with no USD left
    assert all_in_top_strategy.current_usd == 0
    # make sure we end up with the expected amount of ETH
    expected_eth = 6.9993
    assert bs.unfrac(all_in_top_strategy.current_eth) == expected_eth

if __name__ == "__main__":
    pt.main(['tests/test_all_in_top.py'])
