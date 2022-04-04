"""
Testing for the base FOMO strategy class
"""
import pytest as pt
import pandas as pd
import lib.base_strategy as bs
from specific_strategies import FOMO
from test_all_tests import get_test_data_path

def test_FOMO_1():
    """
    Test that FOMO returns as expected
    """
    # Set default buy size to be 10k
    starting_usd = 10000
    # Seconds in a day
    seconds_in_a_day = 60*60*24
    # Number of days
    days = 1
    # Turns days into seconds
    days = days*seconds_in_a_day
    price_df = pd.read_csv(get_test_data_path('test_daily'))
    FOMO_strategy = FOMO.base_FOMO(
        starting_usd=starting_usd,
        time_between_action=days,
        price_period_name='test_daily',
        price_df=price_df,
        save_results=False,
        fear_and_greed_path=get_test_data_path('test_daily_fng')
    )
    FOMO_strategy.run_logic()
    # begin tests
    # make sure we are at the end of the time period
    assert FOMO_strategy.current_time == FOMO_strategy.price_df['timestamp'].values[-1]
    assert FOMO_strategy.current_index == FOMO_strategy.price_df.index[-1]
    # make sure we end up with the expected amount of ETH and USD
    expected_eth = 0
    expected_usd = 6000+((4000*(1-.003))*(1-.003))
    assert bs.unfrac(FOMO_strategy.current_eth) == expected_eth
    assert bs.unfrac(FOMO_strategy.current_usd) == expected_usd
    assert FOMO_strategy.trades_made == 2

def test_FOMO_2():
    """
    Test that FOMO returns as expected
    """
    # Set default buy size to be 10k
    starting_usd = 10000
    # Seconds in a day
    seconds_in_a_day = 60*60*24
    # Number of days
    days = 1
    # Turns days into seconds
    days = days*seconds_in_a_day
    price_df = pd.read_csv(get_test_data_path('test_daily_2'))
    FOMO_strategy = FOMO.base_FOMO(
        starting_usd=starting_usd,
        time_between_action=days,
        price_period_name='test_daily_2',
        price_df=price_df,
        save_results=False,
        fear_and_greed_path=get_test_data_path('test_daily_fng_2')
    )
    FOMO_strategy.run_logic()
    # begin tests
    # make sure we are at the end of the time period
    assert FOMO_strategy.current_time == FOMO_strategy.price_df['timestamp'].values[-1]
    assert FOMO_strategy.current_index == FOMO_strategy.price_df.index[-1]
    # make sure we end up with the expected amount of ETH and USD
    expected_eth = bs.unfrac((14925.1125*(1-.003))+(2500*(1-.003)))
    expected_usd = bs.unfrac(29850.225-14925.1125)
    assert bs.unfrac(FOMO_strategy.current_eth) == expected_eth
    assert bs.unfrac(FOMO_strategy.current_usd) == expected_usd
    assert FOMO_strategy.trades_made == 3

def test_out_of_FOMO_data():
    """
    Test that if we try to run FOMO on dates where there is no FnG data, we get an error.
    """
    # Set default buy size to be 10k
    starting_usd = 10000
    # Seconds in a day
    seconds_in_a_day = 60*60*24
    # Number of days
    days = 1
    # Turns days into seconds
    days = days*seconds_in_a_day
    price_df = pd.read_csv(get_test_data_path('test'))
    FOMO_strategy = FOMO.base_FOMO(
        starting_usd=starting_usd,
        time_between_action=days,
        price_period_name='test',
        price_df=price_df,
        save_results=False
    )

    failed_as_expected = False
    try:
        FOMO_strategy.run_logic()
        failed_as_expected = False
    except LookupError:
        failed_as_expected = True
    
    assert(failed_as_expected)

# def test_FOMO_start_max():
#     """
#     Test that having a max at the start returns expected results
#     """
#     # Set default buy size to be 10k
#     starting_usd = 10000
#     # Seconds in a day
#     seconds_in_a_day = 60*60*24
#     # Number of days
#     days = 1
#     # Turns days into seconds
#     days = days*seconds_in_a_day
#     price_df = pd.read_csv(get_test_data_path('test_'))
#     FOMO_strategy = FOMO.base_FOMO(
#         starting_usd=starting_usd,
#         time_between_action=days,
#         price_period_name='test_',
#         price_df=price_df,
#         save_results=False
#     )
#     FOMO_strategy.run_logic()
#     # begin tests
#     # make sure we are at the end of the time period
#     assert FOMO_strategy.current_time == FOMO_strategy.price_df['timestamp'].values[-1]
#     assert FOMO_strategy.current_index == FOMO_strategy.price_df.index[-1]
#     # we should start with no USD left
#     assert FOMO_strategy.returns_df['# of USD'].iloc[0] == 0
#     # we should always end up with no USD left
#     assert FOMO_strategy.current_usd == 0
#     # make sure we end up with the expected amount of ETH
#     expected_eth = 1.0095
#     assert bs.unfrac(FOMO_strategy.current_eth) == expected_eth

if __name__ == "__main__":
    pt.main(['tests/test_FOMO.py'])
