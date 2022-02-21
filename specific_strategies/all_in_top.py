"""
All in at the top strategy class.
Inherits base_strategy.
Rough approximate of the worst case scenario.
This is only an approximate due to tradeoffs with runtime.
Decrease the time_between_action to increase the accuracy.
"""
import time
import lib.base_strategy as bs
import pandas as pd

class base_all_in_top(bs.Strategy):
    """
    All in top strategy class. Doesn't take any modifiers.
    """
    def __init__(self, starting_usd, time_between_action, price_period_name, price_df=pd.DataFrame(), starting_eth = 0, save_results = True):
        super().__init__(
            name='All in top',
            starting_usd=starting_usd,
            time_between_action=time_between_action,
            price_period_name=price_period_name,
            price_df=price_df,
            starting_eth=starting_eth,
            save_results=save_results
        )
        self.done_buying = False
        self.done_looping = False

    def run_logic(self):
        """
        Holds the strategies main logic function.
        Overrides the Strategy version's function.
        """
        print(f'{self.name} started.')
        # Give a rough measure of how long this took
        real_start_time = time.time()

        # Find the index with the max price for this price_period
        index_at_max = self.price_df['decimal_price'].idxmax()
        # Find the max price for this price_period
        max_fraction_price = bs.frac(self.price_df['fraction_price'].iloc[index_at_max])

        # loop until we hit the LoopComplete exception
        while not self.done_looping:
            # Using this implementation, we aren't guaranteed to get a 100% accurate returns_df.
            # The time we buy is going to be some time AFTER the max price was achieved.
            # However, over long periods of time, this impact should be minimal.
            # Reduce the time_between_actions to increase the accuracy of returns_df.
            # We have to balance looking at every value to see if we are at the max vs making the code not
            # take 12 hours to run for one time period.
            if not self.done_buying and self.current_index >= index_at_max:
                # Set the current_price before we buy to artificially get the max price
                self.current_price = max_fraction_price
                # Do a 100% buy
                self.buy_eth(usd_eth_to_buy=self.starting_usd)
                self.done_buying = True
                print(f'Price bought at: {bs.unfrac(self.current_price)}')
            try:
                self.go_to_next_action()
            except bs.LoopComplete:
                self.done_looping = True

        # In case the index_at_max is in the final time loop, check if we still need to buy
        if not self.done_buying:
            # Set the current_price before we buy to artificially get the max price
            self.current_price = max_fraction_price
            # Do a 100% buy
            self.buy_eth(usd_eth_to_buy=self.starting_usd)
            print(f'Price bought at: {bs.unfrac(self.current_price)}')

        # Now add data to the results csv files
        self.add_data_to_results()
        print(f'{self.name} completed!')
        print(f'Seconds taken: {round(time.time()-real_start_time, 2)}\n')
