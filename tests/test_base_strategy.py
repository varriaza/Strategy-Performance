"""
Testing for the default/base strategy class
"""
import os
from fractions import Fraction as frac
import numpy as np
import pytest as pt
import pandas as pd
import base_strategy as bs

def compare(value1, value2):
    """
    Helpful testing function that prints values if there are a mismatch.
    """
    if value1 != value2:
        print(f'Value1: {value1}')
        print(f'Value2: {value2}')
    return bool(value1 == value2)

def compare_df(df1, df2):
    """
    Helpful testing function that prints values if there are a mismatch.
    """
    if not df1.equals(df2):
        print('df1:')
        print(df1.to_string())
        # print(df1.shape)
        # print(df1.values[-1])
        # for i in df1:
        #     print(f"{i}'s type: {type(df1[i].values[0])}")
        print('---')
        print('df2:')
        print(df2.to_string())
        # print(df2.shape)
        # print(df2.values[-1])
        # for i in df2:
        #     print(f"{i}'s type: {type(df2[i].values[0])}")
        # print('---')

        print(df1.where(df1.values!=df2.values).notna().to_string())
        # values_not_equal = df1.values!=df2.values
        # print(f'values_not_equal:\n{values_not_equal}')
        # print(df1.loc[values_not_equal].notna())

    return df1.equals(df2)

def compare_dicts(dict1, dict2):
    """
    Show values that differ between dictionaries. Return true if the dictionaries are equal.
    """
    set1 = set(dict1.items())
    set2 = set(dict2.items())
    if dict1 != dict2:
        # Do a symmetric diff to find values that don't match
        sorted_values = sorted(set1^set2)
        # Print the values sorted and nicely for debuging
        for value in sorted_values:
            print(value)
            print(f'var type: {type(value[1])}')
        return False
    return True

def delete_test_files():
    """
    Make sure that there are no extra result files BEFORE and after we start the tests.
    """
    price_period_name = 'test'
    try:
        os.remove(bs.price_period_results_path(price_period_name))
    except FileNotFoundError:
        pass

    name = 'Testing'
    try:
        os.remove(bs.strategy_results_path(name))
    except FileNotFoundError:
        pass

    returns_history = f'{name}_{price_period_name}_returns_history.csv'
    try:
        os.remove(bs.returns_history_path(returns_history))
    except FileNotFoundError:
        pass

def create_strat_class():
    """
    Create a default strategy class instance for tests.
    """
    # Variable setup
    name = 'Testing'
    starting_usd = 100.0
    time_between_action = 5
    price_period_name = 'test_period'
    price_df = pd.DataFrame({'timestamp':[1,2,3,4,5], 'fraction_price':[frac(1),frac(2),frac(3),frac(4),frac(5)]})

    # Call the class init
    testing_strat = bs.Strategy(
        name=name,
        starting_usd=starting_usd,
        time_between_action=time_between_action,
        price_period_name=price_period_name,
        price_df=price_df
    )
    return testing_strat

def test_init_blank():
    """
    Test that calling strategy() without arguments will fail.
    """
    try:
        bs.Strategy()
        failed = False
    except TypeError:
        # Strategy correctly failed with no arguments
        failed = True
    assert failed

def test_init():
    """
    Test initialization of parameters.
    """
    # Variable setup
    name = 'Testing'
    starting_usd = 100.0
    time_between_action = 5
    price_period_name = 'test_period'
    price_df = pd.DataFrame({'timestamp':[1,2,3,4,5], 'fraction_price':[frac(1),frac(2),frac(3),frac(4),frac(5)]})

    # Call the class init
    testing_strat = bs.Strategy(
        name=name,
        starting_usd=starting_usd,
        time_between_action=time_between_action,
        price_period_name=price_period_name,
        price_df=price_df
    )
    # Test the class init results
    # Name of the strategy
    assert testing_strat.name == name
    # Name of the price period given
    assert testing_strat.price_period_name == price_period_name
    # Holds the historical price data
    assert testing_strat.price_df.equals(price_df)
    assert testing_strat.start_time == price_df['timestamp'].iloc[0]
    assert testing_strat.end_time == price_df['timestamp'].iloc[-1]
    # Index of price_df
    assert testing_strat.current_index == 0
    # This will be in timestamp units.
    # Time between when the strategy will check if it wants to buy or sell.
    assert testing_strat.time_between_action == time_between_action
    assert testing_strat.starting_usd == starting_usd
    assert testing_strat.current_usd == starting_usd
    # We assume that no eth is currently held
    assert testing_strat.current_eth == 0
    assert testing_strat.current_time == testing_strat.start_time
    assert testing_strat.get_total_value() == testing_strat.starting_usd
    # Get price at the first time period
    assert testing_strat.current_price == price_df['fraction_price'].iloc[0]
    assert testing_strat.trades_made == 0
    # Get timestamps from price_df
    expected_returns_df = pd.DataFrame(price_df['timestamp'])
    # Add other columns we need
    expected_returns_df = expected_returns_df.append(pd.DataFrame(columns=[
        '# of USD',
        '# of ETH',
        'Total Value',
        '% Return'
    ]))
    expected_returns_df.loc[0,[
        '# of USD',
        '# of ETH',
        'Total Value',
        '% Return'
    ]] = [
        starting_usd,
        0,
        testing_strat.get_total_value(),
        testing_strat.get_returns()
    ]
    assert compare_df(testing_strat.returns_df, expected_returns_df)

def test_run_logic():
    """
    This should get a NotImplementedError.
    This should be overridden by classes that inherent it.
    """
    try:
        test_strat = create_strat_class()
        test_strat.run_logic()
        failed = False
    except NotImplementedError:
        failed = True
    assert failed

def test_go_to_next_action():
    """
    Test that the time stepping function works and that total value/price is updated correctly.
    """
    # Variable setup
    name = 'Testing'
    starting_usd = 100.0
    time_between_action = 1
    price_file_name = 'test.csv'
    price_period_name = price_file_name[:-4]
    price_df = pd.read_csv(bs.period_path(price_file_name), index_col='index')

    # Call the class init
    testing_strat = bs.Strategy(
        name=name,
        starting_usd=starting_usd,
        time_between_action=time_between_action,
        price_period_name=price_period_name,
        price_df=price_df
    )
    # Give the strategy 1 eth for testing
    testing_strat.current_eth = frac(1)

    # Collect data before we step
    old_time = testing_strat.current_time
    old_price = testing_strat.current_price
    old_index = testing_strat.current_index
    old_total = testing_strat.get_total_value()
    start_time = testing_strat.start_time

    # Make sure we are at the beggining
    assert start_time == testing_strat.current_time

    # Step forward twice in time as returns_df is in the past by 1 index
    # print(f'current time 1: {testing_strat.current_time}')
    testing_strat.go_to_next_action()
    testing_strat.go_to_next_action()

    # Test that time is updated when stepped
    assert int(testing_strat.current_time) == price_df['timestamp'].iloc[2]
    assert int(old_time)+120 == int(testing_strat.current_time)
    # Test that price updates
    assert old_price != testing_strat.current_price
    assert testing_strat.current_price == frac(price_df['fraction_price'].iloc[2])
    # Test that total value updates
    # Total must decrease as price goes from 753.76 to 753.74
    assert old_total > testing_strat.get_total_value()

    # Test that index updates
    assert old_index == 0
    assert testing_strat.current_index == 2
    # make var as we will use in two places
    total_value = frac(price_df['fraction_price'].iloc[1]) + testing_strat.current_usd
    delta_t = float(testing_strat.current_time-60 - testing_strat.start_time)
    # convert seconds to year (account for a fourth of a leap year day)
    seconds_in_year = 60*60*24*365.25
    fraction_of_year = frac(delta_t)/frac(seconds_in_year)
    return_val = (total_value*frac(100)/testing_strat.starting_total_value)-frac(100)
    # Test that retruns_df updates
    expected_returns_df = pd.DataFrame({
        'timestamp': [price_df['timestamp'].iloc[1]],
        '# of USD': [testing_strat.starting_usd],
        '# of ETH': [frac(1)],
        'Total Value': [bs.unfrac(total_value)],
        '% Return': [bs.unfrac(return_val/fraction_of_year)]
    })
    assert compare_df(testing_strat.returns_df.iloc[testing_strat.current_index-1],expected_returns_df.iloc[-1])

def test_go_to_end():
    """
    Test that when we try to go past the last index LoopComplete is raised
    """
    # Variable setup
    name = 'Testing'
    starting_usd = 100.0
    # Skip ahead until we reach the end
    time_between_action = 60*999999999
    price_file_name = 'test.csv'
    price_period_name = price_file_name[:-4]
    price_df = pd.read_csv(bs.period_path(price_file_name), index_col='index')

    # Call the class init
    testing_strat = bs.Strategy(
        name=name,
        starting_usd=starting_usd,
        time_between_action=time_between_action,
        price_period_name=price_period_name,
        price_df=price_df
    )

    # Step forward in time
    try:
        testing_strat.go_to_next_action()
        completed = False
    except bs.LoopComplete:
        completed = True
    # Test that we caught the LoopComplete error
    assert completed

def test_go_to_next_action_big_skip():
    """
    Test that skipping large amounts of time works as expected.
    """
    # Variable setup
    name = 'Testing'
    starting_usd = 100.0
    # Skip ahead 9 minutes
    time_between_action = 60*9
    price_file_name = 'test.csv'
    price_period_name = price_file_name[:-4]
    price_df = pd.read_csv(bs.period_path(price_file_name), index_col='index')

    # Call the class init
    testing_strat = bs.Strategy(
        name=name,
        starting_usd=starting_usd,
        time_between_action=time_between_action,
        price_period_name=price_period_name,
        price_df=price_df
    )
    # Give the strategy 1 eth for testing
    testing_strat.current_eth = 1

    # Collect data before we step
    old_time = testing_strat.current_time
    old_price = testing_strat.current_price
    old_index = testing_strat.current_index
    start_time = testing_strat.start_time

    # Make sure we are at the beggining
    assert start_time == testing_strat.current_time

    # Step forward in time
    testing_strat.go_to_next_action()
    testing_strat.go_to_next_action()
    testing_strat.go_to_next_action()

    # Test that time is updated when stepped
    assert int(testing_strat.current_time) == price_df['timestamp'].iloc[27]
    # We do three steps
    assert int(old_time)+(time_between_action*3) == int(testing_strat.current_time)
    # Test that price updates
    assert old_price != testing_strat.current_price
    assert testing_strat.current_price == frac(price_df['fraction_price'].iloc[27])
    # Test that total value updates
    # Total should match exactly
    assert testing_strat.get_total_value() == (
        testing_strat.current_usd + frac(price_df['fraction_price'].iloc[27])*testing_strat.current_eth
    )

    # Test that index updates
    assert old_index == 0
    assert testing_strat.current_index == 27
    # make var as we will use in two places
    total_value = frac(price_df['fraction_price'].iloc[26]) + testing_strat.current_usd
    delta_t = float(testing_strat.current_time-60 - testing_strat.start_time)
    # convert seconds to year (account for a fourth of a leap year day)
    seconds_in_year = 60*60*24*365.25
    fraction_of_year = frac(delta_t)/frac(seconds_in_year)
    return_val = (total_value*frac(100)/testing_strat.starting_total_value)-frac(100)
    # Test that retruns_df updates
    expected_returns_df = pd.DataFrame({
        'timestamp': [price_df['timestamp'].iloc[26]],
        '# of USD': [testing_strat.starting_usd],
        '# of ETH': [bs.unfrac(frac(1))],
        'Total Value': [bs.unfrac(total_value)],
        '% Return': [bs.unfrac(return_val/fraction_of_year)]
    })
    assert compare_df(testing_strat.returns_df.iloc[testing_strat.current_index-1],expected_returns_df.iloc[-1])

def setup_buy_and_sell_strat():
    """
    Setup the class for buy and sell tests
    """
    test_strat = create_strat_class()
    # Set the current price for testing
    test_strat.current_price = frac(25.1034)
    # Current/starting USD is 100
    # Set the current ETH for testing
    test_strat.current_eth = frac(5.12045)
    return test_strat

def test_buy_usd_eth():
    """
    Test that buying ETH denominated in USD works.
    """
    test_strat = setup_buy_and_sell_strat()
    usd_buy = frac(55.12051)
    starting_usd = test_strat.current_usd
    starting_eth = test_strat.current_eth
    starting_trade_num = test_strat.trades_made
    starting_total_value = test_strat.get_total_value()
    test_strat.buy_eth(usd_eth_to_buy=usd_buy)

    # assert ending USD = start-buy
    assert test_strat.current_usd == starting_usd-usd_buy
    # assert ending ETH = start+buy
    assert test_strat.current_eth == starting_eth + (usd_buy/test_strat.current_price)
    # assert total value doesn't change when buying
    assert test_strat.get_total_value() == starting_total_value
    # assert trades_made is incremented by 1
    assert test_strat.trades_made == starting_trade_num+1

def test_get_total_value():
    """
    Test that total value is calculated correctly.
    """
    test_strat = setup_buy_and_sell_strat()
    test_strat.current_usd = frac(100.0)
    test_strat.current_eth = frac(1.0)
    test_strat.current_price = frac(25.0)
    assert compare(test_strat.get_total_value(), frac(125.0))

    test_strat.current_usd = frac(113.41)
    test_strat.current_eth = frac(3.51023)
    test_strat.current_price = frac(5135.12305)
    assert compare(test_strat.get_total_value(), frac(113.41)+(frac(3.51023)*frac(5135.12305)))

    test_strat.current_usd = frac('467891/6751')
    test_strat.current_eth = frac('781870987/123874')
    test_strat.current_price = frac('1678023612304/6771251')
    assert compare(
        test_strat.get_total_value(),
        frac('467891/6751')+(frac('781870987/123874')*frac('1678023612304/6771251'))
    )

def test_get_returns():
    """
    Test that the current return % value is calculated correctly
    """
    # Standardize our time passed as 1 day in seconds
    delta_t = float(60*60*24)
    # convert seconds to year (account for a fourth of a leap year day)
    seconds_in_year = 60*60*24*365.25
    fraction_of_year = frac(delta_t)/frac(seconds_in_year)
    
    test_strat = setup_buy_and_sell_strat()
    # Standardize our time passed as 1 day in seconds
    test_strat.current_time += int(60*60*24)

    test_strat.starting_usd = frac(10.0)
    test_strat.current_usd = frac(20.0)
    test_strat.current_eth = frac(0.0)
    test_strat.starting_total_value = test_strat.starting_usd
    test_strat.current_price = frac(20.0)
    return_val = (test_strat.get_total_value()*frac(100)/test_strat.starting_total_value)-frac(100)
    annual_returns = return_val/fraction_of_year
    assert compare(test_strat.get_returns(), annual_returns)

    test_strat.starting_usd = frac(10.0)
    test_strat.starting_total_value = test_strat.starting_usd
    test_strat.current_usd = frac(20.0)
    test_strat.current_eth = frac(1.0)
    test_strat.current_price = frac(10.0)
    return_val = (test_strat.get_total_value()*frac(100)/test_strat.starting_total_value)-frac(100)
    annual_returns = return_val/fraction_of_year
    assert compare(test_strat.get_returns(), annual_returns)

    test_strat.starting_usd = frac('1234078960/871207')
    test_strat.starting_total_value = test_strat.starting_usd
    test_strat.current_usd = frac('691239/180')
    test_strat.current_eth = frac('377812074/70861')
    test_strat.current_price = frac('371741231423/981173440')
    # (self.get_total_value()*frac(100)/self.starting_total_value)-frac(100)
    return_val = (test_strat.get_total_value()*frac(100)/test_strat.starting_total_value)-frac(100)
    annual_returns = return_val/fraction_of_year
    assert compare(test_strat.get_returns(), annual_returns)

def test_buy_eth():
    """
    Test that buying ETH denominated in ETH works.
    """
    test_strat = setup_buy_and_sell_strat()
    eth_buy = frac(2.5104)
    starting_usd = test_strat.current_usd
    starting_eth = test_strat.current_eth
    starting_trade_num = test_strat.trades_made
    starting_total_value = test_strat.get_total_value()
    test_strat.buy_eth(eth_to_buy=eth_buy)

    # assert ending USD = start-buy
    assert test_strat.current_usd == starting_usd-(frac(eth_buy)*test_strat.current_price)
    # assert ending ETH = start+buy
    assert test_strat.current_eth == starting_eth + frac(eth_buy)
    # assert total value doesn't change when buying
    assert test_strat.get_total_value() == starting_total_value
    # assert trades_made is incremented by 1
    assert test_strat.trades_made == starting_trade_num+1

def test_buy_too_much():
    """
    Test that we can't buy more ETH than we have money for.
    """
    # Try first with usd_eth_to_buy
    try:
        test_strat = setup_buy_and_sell_strat()
        test_strat.buy_eth(usd_eth_to_buy=test_strat.current_usd+frac(.0000001))
        failed = False
    except ValueError as ex:
        expected_msg = 'Current USD cannot be negative. There is a logic error in this strategy.'
        # ex.args should only have one value
        # Make sure it failed the expected way
        failed = bool(expected_msg == ex.args[0])
        if not failed:
            print(ex.args[0])
    if not failed:
        print(f'USD: {test_strat.current_usd}')
        print(f'ETH: {test_strat.current_eth}')
    assert failed

    # Try second with eth_to_buy
    try:
        test_strat = setup_buy_and_sell_strat()
        test_strat.buy_eth(eth_to_buy=(test_strat.current_usd/test_strat.current_price)+frac(.0000001))
        failed = False
    except ValueError as ex:
        expected_msg = 'Current USD cannot be negative. There is a logic error in this strategy.'
        # ex.args should only have one value
        # Make sure it failed the expected way
        failed = bool(expected_msg == ex.args[0])
        if not failed:
            print(ex.args[0])
    if not failed:
        print(f'USD: {test_strat.current_usd}')
        print(f'ETH: {test_strat.current_eth}')
    assert failed

def test_buy_with_usd_and_eth():
    """
    Test that we can't supply USD and ETH amounts to buy.
    """
    try:
        test_strat = setup_buy_and_sell_strat()
        test_strat.buy_eth(eth_to_buy = 1, usd_eth_to_buy = 1)
        failed = False
    except ValueError as ex:
        expected_msg = "Only supply USD amount or ETH amount, not both."
        # ex.args should only have one value
        failed = bool(expected_msg == ex.args[0])
    assert failed

def test_buy_with_none():
    """
    Make sure if no arguments are supplied that the buy fails.
    """
    try:
        test_strat = setup_buy_and_sell_strat()
        test_strat.buy_eth()
        failed = False
    except ValueError as ex:
        expected_msg = "Must buy non-zero amounts"
        # ex.args should only have one value
        failed = bool(expected_msg == ex.args[0])
    assert failed


# Sell tests
def test_sell_usd_eth():
    """
    Test that selling ETH works.
    """
    test_strat = setup_buy_and_sell_strat()
    usd_sell = frac(57.12034)
    starting_usd = test_strat.current_usd
    starting_eth = test_strat.current_eth
    starting_trade_num = test_strat.trades_made
    starting_total_value = test_strat.get_total_value()
    test_strat.sell_eth(usd_eth_to_sell=usd_sell)

    # assert ending USD = start+sell
    assert test_strat.current_usd == starting_usd+usd_sell
    # assert ending ETH = start-sell
    assert test_strat.current_eth == starting_eth - (usd_sell/test_strat.current_price)
    # assert total value doesn't change when selling
    # This check is only to make sure no value is lost on a transaction
    assert test_strat.get_total_value() == starting_total_value
    # assert trades_made is incremented by 1
    assert test_strat.trades_made == starting_trade_num+1

def test_sell_eth():
    """
    Test that selling ETH works.
    """
    test_strat = setup_buy_and_sell_strat()
    eth_sell = frac(2.12034)
    starting_usd = test_strat.current_usd
    starting_eth = test_strat.current_eth
    starting_trade_num = test_strat.trades_made
    starting_total_value = test_strat.get_total_value()
    test_strat.sell_eth(eth_to_sell=eth_sell)

    # assert ending USD = start+sell
    assert test_strat.current_usd == starting_usd+(eth_sell*test_strat.current_price)
    # assert ending ETH = start-sell
    assert test_strat.current_eth == starting_eth - eth_sell
    # assert total value doesn't change when selling
    # This check is only to make sure no value is lost on a transaction
    assert test_strat.get_total_value() == starting_total_value
    # assert trades_made is incremented by 1
    assert test_strat.trades_made == starting_trade_num+1

def test_sell_too_much():
    """
    Test that we can't sell more ETH than we have.
    """
    # Try first with eth
    try:
        test_strat = setup_buy_and_sell_strat()
        test_strat.sell_eth(eth_to_sell=test_strat.current_eth+frac(0.000001))
        failed = False
    except ValueError as ex:
        expected_msg = 'Current ETH cannot be negative. There is a logic error in this strategy.'
        # ex.args should only have one value
        # Make sure it failed the expected way
        failed = bool(expected_msg == ex.args[0])
        if not failed:
            print(ex.args[0])
    if not failed:
        print(f'USD: {test_strat.current_usd}')
        print(f'ETH: {test_strat.current_eth}')
    assert failed

    # Try second with usd_eth
    try:
        test_strat = setup_buy_and_sell_strat()
        test_strat.sell_eth(usd_eth_to_sell=(test_strat.current_eth*test_strat.current_price)+frac(0.000001))
        failed = False
    except ValueError as ex:
        expected_msg = 'Current ETH cannot be negative. There is a logic error in this strategy.'
        # ex.args should only have one value
        # Make sure it failed the expected way
        failed = bool(expected_msg == ex.args[0])
        if not failed:
            print(ex.args[0])
    if not failed:
        print(f'USD: {test_strat.current_usd}')
        print(f'ETH: {test_strat.current_eth}')
    assert failed

def test_sell_with_usd_and_eth():
    """
    Test that we can't supply USD and ETH amounts to sell.
    """
    try:
        test_strat = setup_buy_and_sell_strat()
        test_strat.sell_eth(eth_to_sell = 1, usd_eth_to_sell = 1)
        failed = False
    except ValueError as ex:
        expected_msg = "Only supply USD amount or ETH amount, not both."
        # ex.args should only have one value
        failed = bool(expected_msg == ex.args[0])
    assert failed

def test_sell_with_none():
    """
    Make sure if no arguments are supplied that the sell fails.
    """
    try:
        test_strat = setup_buy_and_sell_strat()
        test_strat.sell_eth()
        failed = False
    except ValueError as ex:
        expected_msg = "Must sell non-zero amounts"
        # ex.args should only have one value
        failed = bool(expected_msg == ex.args[0])
    assert failed

def test_add_data_to_results():
    """
    Test that the data in add_data_to_results is generated correctly.
    """
    # Variable setup
    name = 'Testing'
    starting_usd = 100
    # Skip ahead 9 minutes
    time_between_action = 60*9
    price_file_name = 'test.csv'
    price_period_name = price_file_name[:-4]
    price_df = pd.read_csv(bs.period_path(price_file_name), index_col='index')

    # Call the class init
    testing_strat = bs.Strategy(
        name=name,
        starting_usd=starting_usd,
        time_between_action=time_between_action,
        price_period_name=price_period_name,
        price_df=price_df
    )
    # Give the strategy 1 eth for testing
    testing_strat.current_eth = frac(1)
    # Set trades
    testing_strat.trades_made = 10
    start_price = frac('6643518635371397/8796093022208')
    final_price = frac('8862206656386171/8796093022208')
    # If we are calling this function, we should be at the end of the price_df
    testing_strat.current_price = final_price

    expected_value_dict = {
            # - Price delta (start to end)
            'Price Delta': bs.unfrac(frac(final_price)-frac(start_price)),
            # - % Price delta
            '% Price Delta': bs.unfrac((final_price/start_price)*frac(100)),
            # Starting USD
            'Starting USD': bs.unfrac(starting_usd),
            # Starting ETH
            'Starting ETH': bs.unfrac(frac(0)),
            'Ending ETH': bs.unfrac(testing_strat.current_eth),
            # - Total ending value in USD (aka ending ETH+USD)
            'Returns in USD': bs.unfrac(frac(100)+final_price-frac(100)),
            # - Returns in # ETH (aka ending ETH+USD in ETH value)
            'Returns in ETH': bs.unfrac(frac(1)),
            # Mean Annual % Return (aka average)
            'Mean Annual % Return': round(testing_strat.returns_df['% Return'].mean(), 4),
            # Median Annual % Return (aka middle number)
            'Median Annual % Return': round(testing_strat.returns_df['% Return'].median(), 4),
            # - % Total Returns (in USD)
            'Final Annual % Return': bs.unfrac(testing_strat.get_returns()),
            # Median-Mean % Return (aka different is the positional average from the numerical average)
            'Median-Mean % Return': round(
                testing_strat.returns_df['% Return'].median()-testing_strat.returns_df['% Return'].mean(),
                4
            ),
            # - Total trades made
            'Trades Made': 10,
            # Average dollar amount made per trade
            'Flat Return Per Trade': bs.unfrac((frac(100-100)+final_price)/10),
            # - % return per trade (Helps show how intensive a strategy might be, also can be used for fee estimation)
            '% Return Per Trade': bs.unfrac((testing_strat.get_returns())/10),
            # # - Risk vs Rewards of returns (Sharpe Ratio)
            # 'Sharpe of Returns': nan, # we have no real returns
            # # - (Negative) Risk vs Rewards of returns (Sortino Ratio)
            # 'Sortino of Returns': nan, # we have no real returns
            # - Volatility of price for time period (standard deviation)
            'Std of Price': testing_strat.price_df['decimal_price'].std()
    }

    real_values = testing_strat.add_data_to_results(testing=True)
    # drop NA values (Sharpe and Sortino) due to no real returns
    real_values = {k: v for k, v in real_values.items() if pd.Series(v).notna().all()}
    assert compare_dicts(expected_value_dict, real_values)

def test_add_data_new_row():
    """
    Test that a new row in add_data_to_results is generated correctly.
    For both strategy and price_period.
    """
    # Variable setup
    name = 'Testing'
    starting_usd = 100
    # Skip ahead 19 minutes
    time_between_action = 60*19
    price_file_name = 'test.csv'
    price_period_name = price_file_name[:-4]
    price_df = pd.read_csv(bs.period_path(price_file_name), index_col='index')

    # Call the class init
    testing_strat = bs.Strategy(
        name=name,
        starting_usd=starting_usd,
        time_between_action=time_between_action,
        price_period_name=price_period_name,
        price_df=price_df
    )

    try:
        # make sure we don't start with a file already generated from previous tests
        os.remove(bs.price_period_results_path(testing_strat.price_period_name))
    except FileNotFoundError:
        pass

    # Start with an initial buy
    testing_strat.buy_eth(usd_eth_to_buy=10)
    # Move forward in time
    testing_strat.go_to_next_action()
    # Repeat
    testing_strat.buy_eth(usd_eth_to_buy=10)
    testing_strat.go_to_next_action()
    testing_strat.go_to_next_action()
    testing_strat.buy_eth(usd_eth_to_buy=10)
    testing_strat.go_to_next_action()
    testing_strat.go_to_next_action()
    testing_strat.go_to_next_action()
    testing_strat.buy_eth(usd_eth_to_buy=10)
    # Go to the end
    try:
        while True:
            testing_strat.go_to_next_action()
    except bs.LoopComplete:
        pass
    # Call the data consolidation
    testing_strat.add_data_to_results()

    # test price_periods
    price_periods_expected_row = pd.DataFrame({
        'Strategy':['Testing'], 'Price Delta': [252.2356],
        '% Price Delta': [133.3963], 'Starting USD': [100.0], 'Starting ETH': [0.0],
        'Ending ETH': [0.0531], 'Returns in USD': [13.4971], 'Returns in ETH': [0.0134],
        'Mean Annual % Return': [round(testing_strat.returns_df['% Return'].mean(), 4)],
        'Median Annual % Return': [round(testing_strat.returns_df['% Return'].median(), 4)],
        'Final Annual % Return': [bs.unfrac(testing_strat.get_returns())],
        'Median-Mean % Return': [round(
            testing_strat.returns_df['% Return'].median()-testing_strat.returns_df['% Return'].mean(),
            4
        )],
        'Trades Made': [testing_strat.trades_made],
        'Flat Return Per Trade': [
            bs.unfrac((testing_strat.get_total_value()-testing_strat.starting_total_value)/testing_strat.trades_made)
        ],
        '% Return Per Trade': [bs.unfrac(testing_strat.get_returns()/testing_strat.trades_made)],
        'Sharpe of Returns': [testing_strat.sharpe_ratio_of_returns()],
        'Sortino of Returns': [testing_strat.sortino_ratio_of_returns()],
        'Std of Price': [testing_strat.price_df['decimal_price'].std()]
    })
    # Open resulting file and see if the row was added as expected
    real_price_periods_data = pd.read_csv(bs.price_period_results_path(testing_strat.price_period_name))
    assert compare_df(price_periods_expected_row.reset_index(drop=True), real_price_periods_data.reset_index(drop=True))

    # test strategy
    strategy_expected_row = pd.DataFrame({
        'Price Period':['test'], 'Price Delta': [252.2356],
        '% Price Delta': [133.3963], 'Starting USD': [100.0], 'Starting ETH': [0.0],
        'Ending ETH': [0.0531], 'Returns in USD': [13.4971], 'Returns in ETH': [0.0134],
        'Mean Annual % Return': [round(testing_strat.returns_df['% Return'].mean(), 4)],
        'Median Annual % Return': [round(testing_strat.returns_df['% Return'].median(), 4)],
        'Final Annual % Return': [bs.unfrac(testing_strat.get_returns())],
        'Median-Mean % Return': [round(
            testing_strat.returns_df['% Return'].median()-testing_strat.returns_df['% Return'].mean(),
            4
        )],
        'Trades Made': [testing_strat.trades_made],
        'Flat Return Per Trade': [
            bs.unfrac((testing_strat.get_total_value()-testing_strat.starting_total_value)/testing_strat.trades_made)
        ],
        '% Return Per Trade': [bs.unfrac(testing_strat.get_returns()/testing_strat.trades_made)],
        'Sharpe of Returns': [testing_strat.sharpe_ratio_of_returns()],
        'Sortino of Returns': [testing_strat.sortino_ratio_of_returns()],
        'Std of Price': [testing_strat.price_df['decimal_price'].std()]
    })
    # Open resulting file and see if the row was added as expected
    real_strategy_data = pd.read_csv(bs.strategy_results_path(testing_strat.name))
    assert compare_df(strategy_expected_row.reset_index(drop=True), real_strategy_data.reset_index(drop=True))


def test_add_data_update_row():
    """
    Test that updating a row in add_data_to_results is done correctly.
    For both strategy and price_period. Uses the files generated in test_add_data_to_results.
    """

    # Variable setup
    name = 'Testing'
    starting_usd = 100
    # Skip ahead 9 minutes
    time_between_action = 60*19
    price_file_name = 'test.csv'
    price_period_name = price_file_name[:-4]
    price_df = pd.read_csv(bs.period_path(price_file_name), index_col='index')

    # Call the class init
    testing_strat = bs.Strategy(
        name=name,
        starting_usd=starting_usd,
        time_between_action=time_between_action,
        price_period_name=price_period_name,
        price_df=price_df
    )

    # Start with an initial buy
    testing_strat.buy_eth(usd_eth_to_buy=10)
    # Move forward in time
    testing_strat.go_to_next_action()
    # Repeat
    testing_strat.buy_eth(usd_eth_to_buy=10)
    testing_strat.go_to_next_action()
    testing_strat.go_to_next_action()
    testing_strat.buy_eth(usd_eth_to_buy=10)
    testing_strat.go_to_next_action()
    testing_strat.go_to_next_action()
    testing_strat.go_to_next_action()
    testing_strat.buy_eth(usd_eth_to_buy=10)
    # Go to the end
    try:
        while True:
            testing_strat.go_to_next_action()
    except bs.LoopComplete:
        pass
    # Call the data consolidation
    testing_strat.add_data_to_results()

    # define expected values
    price_periods_expected_row = pd.DataFrame({
        'Strategy':['Testing'], 'Price Delta': [252.2356],
        '% Price Delta': [133.3963], 'Starting USD': [100.0], 'Starting ETH': [0.0],
        'Ending ETH': [0.0531], 'Returns in USD': [13.4971], 'Returns in ETH': [0.0134],
        'Mean Annual % Return': [round(testing_strat.returns_df['% Return'].mean(), 4)],
        'Median Annual % Return': [round(testing_strat.returns_df['% Return'].median(), 4)],
        'Final Annual % Return': [bs.unfrac(testing_strat.get_returns())],
        'Median-Mean % Return': [round(
            testing_strat.returns_df['% Return'].median()-testing_strat.returns_df['% Return'].mean(),
            4
        )],
        'Trades Made': [testing_strat.trades_made],
        'Flat Return Per Trade': [
            bs.unfrac((testing_strat.get_total_value()-testing_strat.starting_total_value)/testing_strat.trades_made)
        ],
        '% Return Per Trade': [bs.unfrac(testing_strat.get_returns()/testing_strat.trades_made)],
        'Sharpe of Returns': [testing_strat.sharpe_ratio_of_returns()],
        'Sortino of Returns': [testing_strat.sortino_ratio_of_returns()],
        'Std of Price': [testing_strat.price_df['decimal_price'].std()]
    })
    strategy_expected_row = pd.DataFrame({
        'Price Period':['test'], 'Price Delta': [252.2356],
        '% Price Delta': [133.3963], 'Starting USD': [100.0], 'Starting ETH': [0.0],
        'Ending ETH': [0.0531], 'Returns in USD': [13.4971], 'Returns in ETH': [0.0134],
        'Mean Annual % Return': [round(testing_strat.returns_df['% Return'].mean(), 4)],
        'Median Annual % Return': [round(testing_strat.returns_df['% Return'].median(), 4)],
        'Final Annual % Return': [bs.unfrac(testing_strat.get_returns())],
        'Median-Mean % Return': [round(
            testing_strat.returns_df['% Return'].median()-testing_strat.returns_df['% Return'].mean(),
            4
        )],
        'Trades Made': [testing_strat.trades_made],
        'Flat Return Per Trade': [
            bs.unfrac((testing_strat.get_total_value()-testing_strat.starting_total_value)/testing_strat.trades_made)
        ],
        '% Return Per Trade': [bs.unfrac(testing_strat.get_returns()/testing_strat.trades_made)],
        'Sharpe of Returns': [testing_strat.sharpe_ratio_of_returns()],
        'Sortino of Returns': [testing_strat.sortino_ratio_of_returns()],
        'Std of Price': [testing_strat.price_df['decimal_price'].std()]
    })

    # Open resulting file and see if the row was added as expected
    real_price_period_data = pd.read_csv(bs.price_period_results_path(testing_strat.price_period_name))
    # real_data = pd.read_csv(bs.price_period_results_path(testing_strat.price_period_name), index_col='index')
    assert compare_df(price_periods_expected_row.reset_index(drop=True), real_price_period_data.reset_index(drop=True))
    # Delete file when finished
    os.remove(bs.price_period_results_path(testing_strat.price_period_name))

    # Now for for strategy
    real_strategy_data = pd.read_csv(bs.strategy_results_path(testing_strat.name))
    assert compare_df(
        strategy_expected_row.reset_index(drop=True),
        real_strategy_data.reset_index(drop=True)
    )
    os.remove(bs.strategy_results_path(testing_strat.name))

def test_returns_history():
    """
    Make sure returns history matches returns_df
    """
        # Variable setup
    name = 'Testing'
    starting_usd = 100
    # Skip ahead 9 minutes
    time_between_action = 60*19
    price_file_name = 'test.csv'
    price_period_name = price_file_name[:-4]
    price_df = pd.read_csv(bs.period_path(price_file_name), index_col='index')

    # Call the class init
    testing_strat = bs.Strategy(
        name=name,
        starting_usd=starting_usd,
        time_between_action=time_between_action,
        price_period_name=price_period_name,
        price_df=price_df
    )
    # we have to do at least one trade so that trades made is not zero
    # we divide by it at the end
    testing_strat.buy_eth(usd_eth_to_buy=10)
    # Go to the end
    try:
        while True:
            testing_strat.go_to_next_action()
    except bs.LoopComplete:
        pass
    # Call the data consolidation
    testing_strat.add_data_to_results()
    # returns_history file name
    returns_history = f'{name}_{price_period_name}_returns_history.csv'
    # get the saved data
    real_history_data = pd.read_csv(
        bs.returns_history_path(returns_history),
        # explicitly set the types so that they are equal
        dtype={
            'timestamp': float,
            '# of USD': float,
            '# of ETH': float,
            'Total Value': float,
            '% Return': float
        }
    )
    # explicitly set the types so that they are equal
    testing_strat.returns_df = testing_strat.returns_df.astype({
            'timestamp': float,
            '# of USD': float,
            '# of ETH': float,
            'Total Value': float,
            '% Return': float
    })

    assert compare_df(
        real_history_data, # pylint: disable=no-member
        testing_strat.returns_df
    )
    delete_test_files()

if __name__ == "__main__":
    # Start clean
    delete_test_files()
    pt.main()
    # Clean up
    delete_test_files()
