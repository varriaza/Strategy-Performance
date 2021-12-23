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
        print(f'df2: {df2}')
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
    testing_strat = bs.strategy(
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
        bs.strategy()
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
    testing_strat = bs.strategy(
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
    assert testing_strat.total_value == testing_strat.starting_usd
    # Get price at the first time period
    assert testing_strat.current_price == price_df['price'].iloc[0]
    assert testing_strat.trades_made == 0
    assert testing_strat.returns_df.equals(pd.DataFrame(
        {
            'Time':[testing_strat.start_time],
            '# of USD':[starting_usd],
            '# of ETH':[0],
            'Total Value':[testing_strat.total_value],
            '% Return':[0]
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

# def test_go_to_next_action():
    # TODO - Add nest after time test is created

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
    starting_total_value = test_strat.total_value
    test_strat.buy_eth(usd_eth_to_buy=usd_buy)

    # assert ending USD = start-buy
    assert test_strat.current_usd == starting_usd-usd_buy
    ## assert ending ETH = start+buy
    assert test_strat.current_eth == starting_eth + (usd_buy/test_strat.current_price)
    ## assert total value doesn't change when buying
    assert test_strat.total_value == starting_total_value
    ## assert trades_made is incremented by 1
    assert test_strat.trades_made == starting_trade_num+1
    ## assert returns_df has correct info
    expected_returns_df = pd.DataFrame({
        'Time': [test_strat.current_time],
        '# of USD': [starting_usd-usd_buy],
        '# of ETH': [starting_eth + (usd_buy/test_strat.current_price)],
        'Total Value': [starting_total_value],
        '% Return': [(starting_total_value*100.0/test_strat.starting_usd)-100.0]
    })
    assert compare_df(test_strat.returns_df.iloc[-1],expected_returns_df.iloc[-1])

def test_buy_eth():
    """
    Test that buying ETH denominated in ETH works.
    """
    test_strat = setup_buy_and_sell_strat()
    eth_buy = 2.5104
    starting_usd = test_strat.current_usd
    starting_eth = test_strat.current_eth
    starting_trade_num = test_strat.trades_made
    starting_total_value = test_strat.total_value
    test_strat.buy_eth(eth_to_buy=eth_buy)

    # assert ending USD = start-buy
    assert test_strat.current_usd == starting_usd-(eth_buy*test_strat.current_price)
    ## assert ending ETH = start+buy
    assert test_strat.current_eth == starting_eth + eth_buy
    ## assert total value doesn't change when buying
    assert test_strat.total_value == starting_total_value
    ## assert trades_made is incremented by 1
    assert test_strat.trades_made == starting_trade_num+1
    ## assert returns_df has correct info
    expected_returns_df = pd.DataFrame({
        'Time': [test_strat.current_time],
        '# of USD': [starting_usd-(eth_buy*test_strat.current_price)],
        '# of ETH': [starting_eth + eth_buy],
        'Total Value': [starting_total_value],
        '% Return': [(starting_total_value*100.0/test_strat.starting_usd)-100.0]
    })
    assert compare_df(test_strat.returns_df.iloc[-1],expected_returns_df.iloc[-1])

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
    starting_total_value = test_strat.total_value
    test_strat.sell_eth(usd_eth_to_sell=usd_sell)

    # assert ending USD = start+sell
    assert test_strat.current_usd == starting_usd+usd_sell
    # assert ending ETH = start-sell
    assert test_strat.current_eth == starting_eth - (usd_sell/test_strat.current_price)
    # assert total value doesn't change when selling
    # This check is only to make sure no value is lost on a transaction
    assert test_strat.total_value == starting_total_value
    # assert trades_made is incremented by 1
    assert test_strat.trades_made == starting_trade_num+1
    # assert returns_df has correct info
    expected_returns_df = pd.DataFrame({
        'Time': [test_strat.current_time],
        '# of USD': [starting_usd+usd_sell],
        '# of ETH': [starting_eth - (usd_sell/test_strat.current_price)],
        'Total Value': [starting_total_value],
        '% Return': [(starting_total_value*100.0/test_strat.starting_usd)-100.0]
    })
    assert compare_df(test_strat.returns_df.iloc[-1],expected_returns_df.iloc[-1])

def test_sell_eth():
    """
    Test that selling ETH works.
    """
    test_strat = setup_buy_and_sell_strat()
    eth_sell = 2.12034
    starting_usd = test_strat.current_usd
    starting_eth = test_strat.current_eth
    starting_trade_num = test_strat.trades_made
    starting_total_value = test_strat.total_value
    test_strat.sell_eth(eth_to_sell=eth_sell)

    # assert ending USD = start+sell
    assert test_strat.current_usd == starting_usd+(eth_sell*test_strat.current_price)
    # assert ending ETH = start-sell
    assert test_strat.current_eth == starting_eth - eth_sell
    # assert total value doesn't change when selling
    # This check is only to make sure no value is lost on a transaction
    assert test_strat.total_value == starting_total_value
    # assert trades_made is incremented by 1
    assert test_strat.trades_made == starting_trade_num+1
    # assert returns_df has correct info
    expected_returns_df = pd.DataFrame({
        'Time': [test_strat.current_time],
        '# of USD': [starting_usd+(eth_sell*test_strat.current_price)],
        '# of ETH': [starting_eth - eth_sell],
        'Total Value': [starting_total_value],
        '% Return': [(starting_total_value*100.0/test_strat.starting_usd)-100.0]
    })
    assert compare_df(test_strat.returns_df.iloc[-1],expected_returns_df.iloc[-1])


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
