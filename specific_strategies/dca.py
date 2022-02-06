"""
DCA strategy class.
Inherits base_strategy.
Takes in how often you want to DCA in days as an input.
"""
from fractions import Fraction as frac
import time
import base_strategy as bs
import pandas as pd

def display_time(seconds, granularity=1):
    """ Turns seconds into weeks, days, hours, minutes and seconds.
    Granularity determines how many time units should be returned. EG:
    # 2 time unites, week and day
    1934815, 2 = '3 weeks, 1 day'
    # 4 time units
    1934815, 4 = '3 weeks, 1 day, 9 hours, 26 minutes'
    """
    result = []
    intervals = (
        # weeks weren't necessary so I removed them
        ('days', 86400),    # 60 * 60 * 24
        ('hours', 3600),    # 60 * 60
        ('minutes', 60),
        ('seconds', 1),
    )
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ' '.join(result[:granularity])

class base_dca(bs.Strategy):
    """
    Base dca strategy class. Specific strategies should just change the time_between_action variable.
    """
    def __init__(self, starting_usd, time_between_action, price_period_name, price_df=pd.DataFrame(), starting_eth = 0, save_results = True):
        self.dca_period = display_time(time_between_action)
        super().__init__(
            name=f'DCA every {self.dca_period}',
            starting_usd=starting_usd,
            time_between_action=time_between_action,
            price_period_name=price_period_name,
            price_df=price_df,
            starting_eth=starting_eth,
            save_results=save_results
        )
        self.number_of_buys = None
        self.dca_buy_amount = None
        self.done_buying = False

    def run_logic(self):
        """
        Holds the strategies main logic function.
        Overrides the Strategy version's function.
        """
        print(f'{self.name} started.')
        # Give a rough measure of how long this took
        real_start_time = time.time()
        # Do 30% initial buy
        initial_buy_percent = frac(30, 100)
        usd_eth_to_buy = self.starting_usd*initial_buy_percent
        self.buy_eth(usd_eth_to_buy=usd_eth_to_buy)

        # Then do x% of remaining total per time_between_action
        total_time_in_period = self.price_df['timestamp'].iloc[-1] - self.price_df['timestamp'].iloc[0]
        # Find out how many buy periods are in our price_period
        self.number_of_buys = total_time_in_period/self.time_between_action
        # Round the number of buy periods down to an int to find how many buy actions
        # we will actually do
        self.number_of_buys = int(self.number_of_buys)
        if self.number_of_buys == 0:
            print('\nERROR info:')
            print(f'Time in price_period: {display_time(total_time_in_period)}')
            print(f'Price_period not long enough for dca period of {self.dca_period}')
            raise ValueError(f'Price_period not long enough for dca period of {self.dca_period}')
        # We want to have zero USD by the end of the DCA period so buy enough to make that happen
        self.dca_buy_amount = self.current_usd/self.number_of_buys

        # loop until we hit the LoopComplete exception
        while not self.done_buying:
            try:
                self.go_to_next_action()
                self.buy_eth(self.dca_buy_amount)
            except bs.LoopComplete:
                self.done_buying = True

        # Now add data to the results csv files
        self.add_data_to_results()
        print(f'{self.name} completed!')
        print(f'Seconds taken: {round(time.time()-real_start_time, 2)}\n')
