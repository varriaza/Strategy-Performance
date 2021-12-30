"""
Testing for the default/base strategy class
"""

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
        print(f'df1: {df1}')
        print('---')
        print(f'df2: {df2}')
        print('---')
        print(df1.where(df1.values==df2.values).notna())
    return df1.equals(df2)

def create_strat_class():
    """
    Create a default strategy class instance for tests.
    """
    # Variable setup
    name = 'Testing'
    starting_usd = 100.0
    time_between_action = 5
    price_period_name = 'test_period'
    price_df = pd.DataFrame({'timestamp':[1,2,3,4,5], 'price':[1,2,3,4,5]})

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
    price_df = pd.DataFrame({'timestamp':[1,2,3,4,5], 'price':[1,2,3,4,5]})

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
    assert testing_strat.current_price == price_df['price'].iloc[0]
    assert testing_strat.trades_made == 0
    assert testing_strat.returns_df.equals(pd.DataFrame(
        {
            'Time':[testing_strat.start_time],
            '# of USD':[starting_usd],
            '# of ETH':[0],
            'Total Value':[testing_strat.get_total_value()],
            '% Return':[testing_strat.get_returns()]
        },
        columns=[
            'Time',
            '# of USD',
            '# of ETH',
            'Total Value',
            '% Return'
        ]
    ))

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
    price_df = pd.read_csv(f'csv_files\\{price_file_name}', index_col='index')

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
    old_total = testing_strat.get_total_value()
    start_time = testing_strat.start_time

    # Make sure we are at the beggining
    assert start_time == testing_strat.current_time

    # Step forward twice in time as returns_df is in the past by 1 index
    testing_strat.go_to_next_action()
    testing_strat.go_to_next_action()

    # Test that time is updated when stepped
    assert int(testing_strat.current_time) == 1514880180
    assert int(old_time)+120 == int(testing_strat.current_time)
    # Test that price updates
    assert old_price != testing_strat.current_price
    assert testing_strat.current_price == 849.2925
    # Test that total value updates
    # Total must decrease as price goes from 849.4812499999999 to 849.2925
    assert old_total > testing_strat.get_total_value()

    # Test that index updates
    assert old_index == 0
    assert testing_strat.current_index == 2
    # Test that retruns_df updates
    expected_returns_df = pd.DataFrame({
        'Time': [1514880120.0],
        '# of USD': [testing_strat.starting_usd],
        '# of ETH': [1],
        'Total Value': [949.65],
        '% Return': [(949.65*100.0/testing_strat.starting_usd)-100.0]
    })
    assert compare_df(testing_strat.returns_df.iloc[-1],expected_returns_df.iloc[-1])

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
    price_df = pd.read_csv(f'csv_files\\{price_file_name}', index_col='index')

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
    price_df = pd.read_csv(f'csv_files\\{price_file_name}', index_col='index')

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

    # Test that time is updated when stepped
    assert int(testing_strat.current_time) == 1514880600
    assert int(old_time)+(60*9) == int(testing_strat.current_time)
    # Test that price updates
    assert old_price != testing_strat.current_price
    assert testing_strat.current_price == 849.4662500000001
    # Test that total value updates
    # Total should match exactly
    assert testing_strat.get_total_value() == round(949.4662500000001, 2)

    # Test that index updates
    assert old_index == 0
    assert testing_strat.current_index == 9
    # Test that retruns_df updates
    expected_returns_df = pd.DataFrame({
        'Time': [1514880540],
        '# of USD': [testing_strat.starting_usd],
        '# of ETH': [1],
        'Total Value': [round(949.6975, 2)],
        '% Return': [(round(949.6975, 2)*100.0/testing_strat.starting_usd)-100.0]
    })
    # print(f'Time real: {testing_strat.returns_df["Time"].iloc[-1]}')
    # print(f'Time ex:   {expected_returns_df["Time"].iloc[-1]}')
    # print(f'Total_val real: {testing_strat.returns_df["Total Value"].iloc[-1]}')
    # print(f'Total_val ex: {expected_returns_df["Total Value"].iloc[-1]}')
    # print(f'Return real: {testing_strat.returns_df["% Return"].iloc[-1]}')
    # print(f'Return ex: {expected_returns_df["% Return"].iloc[-1]}')
    assert compare_df(testing_strat.returns_df.iloc[-1],expected_returns_df.iloc[-1])
    # Make sure we have 9 NEW entries in returns_df (one for each minute) + 1 starting entry
    assert len(testing_strat.returns_df.index) == 10

def setup_buy_and_sell_strat():
    """
    Setup the class for buy and sell tests
    """
    test_strat = create_strat_class()
    # Set the current price for testing
    test_strat.current_price = 25.1034
    # Current/starting USD is 100
    # Set the current ETH for testing
    test_strat.current_eth = 5.12045
    return test_strat

def test_buy_usd_eth():
    """
    Test that buying ETH denominated in USD works.
    """
    test_strat = setup_buy_and_sell_strat()
    usd_buy = 55.12051
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
    test_strat.current_usd = 100.0
    test_strat.current_eth = 1.0
    test_strat.current_price = 25.0
    assert compare(test_strat.get_total_value(), 125.0)

    test_strat.current_usd = 113.41
    test_strat.current_eth = 3.51023
    test_strat.current_price = 5135.12305
    assert compare(test_strat.get_total_value(), round(113.41+(3.51023*5135.12305), 2))

def test_get_returns():
    """
    Test that the current return % value is calculated correctly
    """
    test_strat = setup_buy_and_sell_strat()
    test_strat.starting_usd = 10.0
    test_strat.current_usd = 20.0
    test_strat.current_eth = 0.0
    test_strat.starting_total_value = test_strat.starting_usd
    test_strat.current_price = 20.0
    assert compare(test_strat.get_returns(), 100.0)

    test_strat.starting_usd = 10.0
    test_strat.starting_total_value = test_strat.starting_usd
    test_strat.current_usd = 20.0
    test_strat.current_eth = 1.0
    test_strat.current_price = 10.0
    assert compare(test_strat.get_returns(), 200.0)

    test_strat.starting_usd = 1000.0
    test_strat.starting_total_value = test_strat.starting_usd
    test_strat.current_usd = 1267.52
    test_strat.current_eth = 6.839087
    test_strat.current_price = 6439.872035
    # print(f'Total value is: {test_strat.get_total_value()}')
    assert compare(test_strat.get_returns(), 4431.037)


def test_buy_eth():
    """
    Test that buying ETH denominated in ETH works.
    """
    test_strat = setup_buy_and_sell_strat()
    eth_buy = 2.5104
    starting_usd = test_strat.current_usd
    starting_eth = test_strat.current_eth
    starting_trade_num = test_strat.trades_made
    starting_total_value = test_strat.get_total_value()
    test_strat.buy_eth(eth_to_buy=eth_buy)

    # assert ending USD = start-buy
    assert test_strat.current_usd == starting_usd-(eth_buy*test_strat.current_price)
    # assert ending ETH = start+buy
    assert test_strat.current_eth == starting_eth + eth_buy
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
        test_strat.buy_eth(usd_eth_to_buy=test_strat.current_usd+.0000001)
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
        test_strat.buy_eth(eth_to_buy=(test_strat.current_usd/test_strat.current_price)+.0000001)
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
    usd_sell = 57.12034
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
    eth_sell = 2.12034
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
        test_strat.sell_eth(eth_to_sell=test_strat.current_eth+0.000001)
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
        test_strat.sell_eth(usd_eth_to_sell=(test_strat.current_eth*test_strat.current_price)+0.000001)
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

if __name__ == "__main__":
    pt.main()
