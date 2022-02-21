"""
All in at the bottom strategy class.
Inherits base_strategy.
Rough approximate of the worst case scenario.
This is only an approximate due to tradeoffs with runtime.
Decrease the time_between_action to increase the accuracy.
"""
import time
import lib.base_strategy as bs
import pandas as pd

class base_all_in_bottom(bs.Strategy):
    """
    All in bottom strategy class. Doesn't take any modifiers.
    """
    def __init__(self, starting_usd, time_between_action, price_period_name, price_df=pd.DataFrame(), starting_eth = 0, save_results = True):
        super().__init__(
            name='All in bottom',
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

        # Find the index with the min price for this price_period
        index_at_min = self.price_df['decimal_price'].idxmin()
        # Find the min price for this price_period
        min_price = self.price_df['decimal_price'].min()

        # loop until we hit the LoopComplete exception
        while not self.done_looping:
            # Using this implementation we aren't guaranteed to get the exact minimum price.
            # However, we can skip large amounts of time without having to worry about
            # accidentally missing the minimum price. We should still get a price very close to where we want it.
            if not self.done_buying and self.current_index >= index_at_min:
                # Do a 100% buy
                self.buy_eth(usd_eth_to_buy=self.starting_usd)
                self.done_buying = True
                # Show how far off our buy price is from the min price
                print(f'Min price for this price_period: {min_price}')
                print(f'Price bought at: {bs.unfrac(self.current_price)}')
            try:
                self.go_to_next_action()
            except bs.LoopComplete:
                self.done_looping = True

        # In case the index_at_min is in the final time loop, check if we still need to buy
        if not self.done_buying:
            # Do a 100% buy
            self.buy_eth(usd_eth_to_buy=self.starting_usd)
            # Show how far off our buy price is from the min price
            print(f'Min price for this price_period: {min_price}')
            print(f'Price bought at: {bs.unfrac(self.current_price)}')

        # Now add data to the results csv files
        self.add_data_to_results()
        print(f'{self.name} completed!')
        print(f'Seconds taken: {round(time.time()-real_start_time, 2)}\n')
