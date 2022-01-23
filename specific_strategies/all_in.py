"""
All in strategy class.
Inherits base_strategy.
Goes all in right away.
"""
import time
import base_strategy as bs

class base_all_in(bs.Strategy):
    """
    All in strategy class. Doesn't take any modifiers.
    """
    def __init__(self, starting_usd, time_between_action, price_period_name, starting_eth = 0, save_results = True):
        super().__init__(
            name='All in',
            starting_usd=starting_usd,
            time_between_action=time_between_action,
            price_period_name=price_period_name,
            starting_eth=starting_eth,
            save_results=save_results
        )
        self.done_buying = False

    def run_logic(self):
        """
        Holds the strategies main logic function.
        Overrides the Strategy version's function.
        """
        print(f'{self.name} started.')
        # Give a rough measure of how long this took
        real_start_time = time.time()
        # Do 100% initial buy
        usd_eth_to_buy = self.starting_usd
        self.buy_eth(usd_eth_to_buy=usd_eth_to_buy)

        # loop until we hit the LoopComplete exception
        while not self.done_buying:
            try:
                self.go_to_next_action()
            except bs.LoopComplete:
                self.done_buying = True

        # Now add data to the results csv files
        self.add_data_to_results()
        print(f'{self.name} completed!')
        print(f'Seconds taken: {round(time.time()-real_start_time, 2)}\n')
