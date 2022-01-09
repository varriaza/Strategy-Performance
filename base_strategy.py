"""
Base strategy class.
Gets inherited by specific strategies.
"""
from fractions import Fraction as frac
import pandas as pd

class LoopComplete(Exception):
    pass

class Strategy:
    """Base strategy class, specific strategies should inherent this."""
    def __init__(self, name, starting_usd, time_between_action, price_period_name, price_df, starting_eth = 0) -> None:
        # Name of the strategy
        self.name = name
        # Name of the price period given
        self.price_period_name = price_period_name
        # Holds the historical price data
        self.price_df = price_df
        self.start_time = int(price_df['timestamp'].iloc[0])
        self.end_time = int(price_df['timestamp'].iloc[-1])
        # Index of price_df
        self.current_index = 0
        # This will be in timestamp units (aka seconds)
        # Time between when the strategy will check if it wants to buy or sell
        # Each data point is collected 60 seconds apart
        self.time_between_action = time_between_action
        self.starting_usd = frac(starting_usd)
        self.starting_eth = frac(starting_eth)
        self.current_usd = frac(starting_usd)
        # We assume that no eth is currently held
        self.current_eth = frac(starting_eth)
        self.current_time = self.start_time
        # Get price at the first time period
        self.current_price = frac(price_df['fraction_price'].iloc[0])
        self.starting_total_value = self.starting_usd + (self.starting_eth*self.current_price)
        self.trades_made = 0
        # Create all of the rows for price_df so we don't have to append rows, just add data
        # Get timestamps from price_df
        self.returns_df = pd.DataFrame(price_df['timestamp'])
        # Add other columns we need
        self.returns_df = self.returns_df.append(pd.DataFrame(columns=[
            '# of USD',
            '# of ETH',
            'Total Value',
            '% Return']))
        # Rename the index to 'index'
        self.returns_df.index.names = ['index']
        # Make sure the first row has initial data
        self.add_to_returns()

    def run_logic(self):
        """
        Override this.
        Holds the strategies main logic function.
        """
        raise NotImplementedError('Override this.')

    def go_to_next_action(self):
        """
        Move time forward until the next buy period.
        Raise LoopComplete when we reach the last index.
        """
        stepping_start = self.current_time
        # Loop until we find a value past our time+delta time.
        while self.current_time < stepping_start+self.time_between_action:
            # Update returns before we step to capture buys and sells done in current time
            self.add_to_returns()
            self.current_index += 1
            # Stop looping and show the strategy we are finished when we try to go past the last index.
            if self.current_index >= self.price_df.index[-1]:
                raise LoopComplete('All done')
            self.current_time = self.price_df['timestamp'].iloc[self.current_index]
            # Update price so we can update total value/total returns
            self.current_price = frac(self.price_df['fraction_price'].iloc[self.current_index])

    def get_total_value(self):
        """
        Returns the total USD+ETH portfolio value in USD
        """
        return self.current_usd + (self.current_eth*self.current_price)

    def get_returns(self):
        """
        Returns % returns since the start of the time period.
        """
        return (self.get_total_value()*frac(100)/self.starting_total_value)-frac(100)

    def add_to_returns(self):
        """
        Called on buy or sell. Adds current values to returns df.
        """
        self.returns_df.loc[self.current_index, [
            '# of USD',
            '# of ETH',
            'Total Value',
            '% Return'
        ]] = [
            self.current_usd,
            self.current_eth,
            self.get_total_value(),
            self.get_returns()
        ]

    def buy_eth(self, eth_to_buy=0, usd_eth_to_buy=0):
        """
        Buy ETH with USD.
        Raises ValueError if the action would result in negative USD or there are bad inputs.
        """
        # Fraction inputs for math compatibility
        eth_to_buy = frac(eth_to_buy)
        usd_eth_to_buy = frac(usd_eth_to_buy)
        if eth_to_buy == 0 and usd_eth_to_buy == 0:
            raise ValueError("Must buy non-zero amounts")
        if eth_to_buy != 0 and usd_eth_to_buy != 0:
            raise ValueError("Only supply USD amount or ETH amount, not both.")
        # If we are supplied eth amounts, convert to ETH amounts to allow for standardization.
        if eth_to_buy != 0:
            usd_eth_to_buy = eth_to_buy*self.current_price

        if self.current_usd-usd_eth_to_buy < 0:
            raise ValueError(
                'Current USD cannot be negative. There is a logic error in this strategy.'
            )
        self.current_eth += usd_eth_to_buy/self.current_price
        self.current_usd -= usd_eth_to_buy
        self.trades_made += 1

    def sell_eth(self, eth_to_sell=0, usd_eth_to_sell=0):
        """
        Sell ETH for USD.
        Raises ValueError if the action would result in negative ETH or there are bad inputs.
        """
        # Fraction inputs for math compatibility
        eth_to_sell = frac(eth_to_sell)
        usd_eth_to_sell = frac(usd_eth_to_sell)
        if eth_to_sell == 0 and usd_eth_to_sell == 0:
            raise ValueError("Must sell non-zero amounts")
        if eth_to_sell != 0 and usd_eth_to_sell != 0:
            raise ValueError("Only supply USD amount or ETH amount, not both.")
        # If we are supplied usd amounts, convert to eth amounts to keep things simple.
        if usd_eth_to_sell != 0:
            eth_to_sell = usd_eth_to_sell/self.current_price

        if self.current_eth-eth_to_sell < 0:
            raise ValueError(
                'Current ETH cannot be negative. There is a logic error in this strategy.'
            )
        self.current_eth -= eth_to_sell
        self.current_usd += eth_to_sell*self.current_price
        self.trades_made += 1

    @staticmethod
    def unfrac(fraction, round_to=4):
        """Turn a fraction into a float rounded to the fourth decimal."""
        return round(float(fraction), round_to)

    def add_data_to_results(self, testing=False):
        """
        Calculates the following values and adds them to csv's in the results folder
        """
        # Calculate values
        # Make this a dictionary that we can add where needed
        value_dict = {
            # - Price delta (start to end)
            'Price Delta': self.unfrac(
                frac(self.price_df['fraction_price'].iloc[-1])-frac(self.price_df['fraction_price'].iloc[0])
            ),
            # - % Price delta
            '% Price Delta': self.unfrac(
                (frac(self.price_df['fraction_price'].iloc[-1])/frac(self.price_df['fraction_price'].iloc[0]))*frac(100)
            ),
            # Starting USD
            'Starting USD': self.unfrac(self.starting_usd),
            # Starting ETH
            'Starting ETH': self.unfrac(self.starting_eth),
            # Ending ETH
            'Ending ETH': self.unfrac(self.current_eth),
            # - Total ending value in USD (aka ending ETH+USD)
            'Returns in USD': self.unfrac(self.get_total_value()),
            # - Returns in # ETH (aka ending ETH+USD in ETH value)
            'Returns in ETH': self.unfrac(self.get_total_value()/self.current_price),
            # - % Total Returns (in USD)
            '% Return': self.unfrac(self.get_returns()),
            # - Total trades made
            'Trades Made': self.trades_made,
            # Average dollar amount made per trade
            'Flat Return Per Trade': self.unfrac(self.get_total_value()/self.trades_made),
            # - % return per trade (Helps show how intensive a strategy might be, also can be used for fee estimation)
            '% Return Per Trade': self.unfrac(self.get_returns()/self.trades_made),
            # - Volatility of returns (Sharpe Ratio)
            'Sharpe Ratio of Returns': 'TBA', # sharpe(self.returns_df['Total Value'])
            # - Volatility of price for time period (Sharpe Ratio)
            'Sharpe Ratio of Price': 'TBA',
            # - Negative volatility of price (Sortino Ratio)
            'Sortino Ratio of Price': 'TBA'
        }

        # Return the values above if we are testing
        if testing:
            print(f'Real Values:\n{value_dict}')
            return value_dict

        # Check if csv file with time period name exists in results/time_periods
            # If not, create it. Name = time period name
            # If it exists, read it in
        # Add values to time period df, or update row if it exists
            # Rows = strategy
            # Columns = values
        new_time_period_row = {
            'Strategy': self.name,
        }
        new_time_period_row.update(value_dict)
        # save df as csv
        
        # Check if a csv file for the strategy itself in results/strategies
            # If not, create it. Name = strategy name
            # If it exists, read it in
        # Add values to strategy df, or update row if it exists
            # Rows = time periods
            # Columns = values
        new_strategy_row = {
            'Time Period': self.price_period_name,
        }
        new_strategy_row.update(value_dict)
        # save df as csv

