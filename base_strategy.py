# Base strategy class
import pandas as pd

class strategy:
    """Base strategy class, specific strategies should inherent this."""
    def __init__(self, name, starting_usd, time_between_action, price_period_name, price_df) -> None:
        # Name of the strategy
        self.name = name
        # Name of the price period given
        self.price_period_name = price_period_name
        # Holds the historical price data
        self.price_df = price_df
        self.start_time = price_df['timestamp'].iloc[0]
        self.end_time = price_df['timestamp'].iloc[-1]
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
        self.current_price = None
        self.trades_made = 0
        self.returns_df = pd.DataFrame(
            {
                'Time':self.start_time,
                '# of USD':starting_usd,
                '# of ETH':0,
                'Total Value':starting_usd,
                '% Return':0
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
        # TODO - Create price column as average of high and low? Not perfect but good enough.
        self.current_price = self.price_df['price'].iloc[self.current_index]

    def buy_eth(self, eth_to_buy):
        """
        Buy ETH with USD.
        Raises ValueError if the action would result in negative USD.
        """
        self.current_eth += eth_to_buy
        self.current_usd -= eth_to_buy*self.current_price
        if self.current_usd < 0:
            raise ValueError(
                'Current USD cannot be negative. There is a logic error in this strategy.'
            )

    def sell_eth(self, eth_to_sell):
        """
        Sell ETH for USD.
        Raises ValueError if the action would result in negative ETH.
        """
        self.current_eth -= eth_to_sell
        self.current_usd += eth_to_sell*self.current_price
        if self.current_eth < 0:
            raise ValueError(
                'Current ETH cannot be negative. There is a logic error in this strategy.'
            )
