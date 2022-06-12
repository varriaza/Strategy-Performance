"""
Testing for the base all_in strategy class
"""
import pytest as pt
import pandas as pd
import lib.base_strategy as bs
from specific_strategies import all_in_start
from test_all_tests import get_test_data_path

def test_all_in_start():
    """
    Test that buying right away returns expected results
    """
    # Set default buy size to be 10k
    starting_usd = 10000
    # Seconds in a day
    seconds_in_a_day = 60*60*24
    # Number of days doesn't really matter
    days = 2
    # Turns days into seconds
    days = days*seconds_in_a_day
    price_df = pd.read_csv(get_test_data_path('test'))
    all_in_strategy = all_in_start.base_all_in(
        starting_usd=starting_usd,
        time_between_action=days,
        price_period_name='test',
        price_df=price_df,
        save_results=False
    )
    all_in_strategy.run_logic()
    # begin tests
    # make sure we are at the end of the time period
    assert all_in_strategy.current_time == all_in_strategy.price_df['timestamp'].values[-1]
    assert all_in_strategy.current_index == all_in_strategy.price_df.index[-1]
    # we should start with no USD left
    assert all_in_strategy.returns_df['# of USD'].iloc[0] == 0
    # we should always end up with no USD left
    assert all_in_strategy.current_usd == 0
    # make sure we end up with the expected amount of ETH
    expected_eth = 13.2004
    assert bs.unfrac(all_in_strategy.current_eth) == expected_eth

if __name__ == "__main__":
    pt.main(['tests/test_all_in.py'])
