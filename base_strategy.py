"""
Base strategy class.
Gets inherited by specific strategies.
"""
import pandas as pd

class Strategy:
    """Base strategy class, specific strategies should inherent this."""
    def __init__(self, name, starting_usd, time_between_action, price_period_name, price_df) -> None:
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
        # This will be in timestamp units. Time between when the strategy will check if it wants to buy or sell.
        self.time_between_action = time_between_action
        self.starting_usd = starting_usd
        self.current_usd = starting_usd
        # We assume that no eth is currently held
        self.current_eth = 0
        self.current_time = self.start_time
        # Get price at the first time period
        self.current_price = price_df['price'].iloc[0]
        self.trades_made = 0
        self.returns_df = pd.DataFrame(
            {
                'Time': [self.start_time],
                '# of USD': [starting_usd],
                '# of ETH': [0],
                'Total Value': [self.get_total_value()],
                '% Return': [self.get_returns()]
            },
            columns=[
                'Time',
                '# of USD',
                '# of ETH',
                'Total Value',
                '% Return'
            ]
        )

    def run_logic(self):
        """
        Override this.
        Holds the strategies main logic function.
        """
        raise NotImplementedError('Override this.')

    def go_to_next_action(self):
        """
        Move time forward until the next buy period.
        """
        stepping_start = self.current_time
        # Loop until we find a value past our time+delta time.
        while self.current_time < stepping_start+self.time_between_action:
            self.current_index += 1
            self.current_time = self.price_df['timestamp'].iloc[self.current_index]
            # Update price so we can update total value/total returns
            self.current_price = self.price_df['price'].iloc[self.current_index]
            # Update returns
            self.add_to_returns()

    def get_total_value(self):
        """
        Returns the total USD+ETH portfolio value in USD
        """
        return round(self.current_usd + (self.current_eth*self.current_price), 2)

    def get_returns(self):
        """
        Returns % returns since the start of the time period.
        """
        return (self.get_total_value()*100.0/self.starting_usd)-100.0

    def add_to_returns(self):
        """
        Called on buy or sell. Adds current values to returns df.
        """
        new_row = {
            'Time': self.current_time,
            '# of USD': self.current_usd,
            '# of ETH': self.current_eth,
            'Total Value': self.get_total_value(),
            '% Return': self.get_returns()
        }
        self.returns_df = self.returns_df.append(new_row, ignore_index=True)
        # print(f'returns:\n{self.returns_df}')

    def buy_eth(self, eth_to_buy=0, usd_eth_to_buy=0):
        """
        Buy ETH with USD.
        Raises ValueError if the action would result in negative USD or there are bad inputs.
        """
        if eth_to_buy == 0 and usd_eth_to_buy == 0:
            raise ValueError("Must buy non-zero amounts")
        if eth_to_buy != 0 and usd_eth_to_buy != 0:
            raise ValueError("Only supply USD amount or ETH amount, not both.")
        # If we are supplied eth amounts, convert to USD amounts to allow for standardization.
        if eth_to_buy != 0:
            usd_eth_to_buy = eth_to_buy*self.current_price

        if self.current_usd-usd_eth_to_buy < 0:
            raise ValueError(
                'Current USD cannot be negative. There is a logic error in this strategy.'
            )
        self.current_eth += usd_eth_to_buy/self.current_price
        self.current_usd -= usd_eth_to_buy
        self.trades_made += 1
        # Update returns even though it will be net zero to show that a transaction was done.
        self.add_to_returns()

    def sell_eth(self, eth_to_sell=0, usd_eth_to_sell=0):
        """
        Sell ETH for USD.
        Raises ValueError if the action would result in negative ETH or there are bad inputs.
        """
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
