"""
FOMO (Moving Avg) strategy class.
Buy when market is greedy, sell when it is fearful. Not expected to make money.
Inherits base_strategy.
Takes in how often you want to buy (in days) as an input. 
Fear and Greed data is daily so this should be 1 day or greater.
"""
from datetime import datetime, timezone
import time
import pandas as pd
import lib.base_strategy as bs

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

class base_FOMO(bs.Strategy):
    """
    Base FOMO (Moving Avg) strategy class.
    """
    def __init__(self, starting_usd, time_between_action, price_period_name, price_df=pd.DataFrame(), starting_eth = 0, save_results = True, fear_and_greed_path='default'):
        self.buy_sell_period = display_time(time_between_action)
        super().__init__(
            name=f'FOMO (Moving Avg) every {self.buy_sell_period}',
            starting_usd=starting_usd,
            time_between_action=time_between_action,
            price_period_name=price_period_name,
            price_df=price_df,
            starting_eth=starting_eth,
            save_results=save_results
        )
        self.number_of_buys = None
        self.done_buying = False
        # Test if we should use the default fear and greed csv path or use a new one for testing
        if fear_and_greed_path == 'default':
            self.fng_df = pd.read_csv(bs.full_path('fear_and_greed.csv'), index_col='index')
        else:
            self.fng_df = pd.read_csv(fear_and_greed_path, index_col='index')

    def buy_sell_logic(self):
        """
        Holds the logic of if the strategy should buy or sell at the current moment.
        *** THIS SHOULD NOT MAKE MONEY ***
        Buys if FnG is > 60, buy more the greater, buy 50% of starting money at 100
        Sells if FnG is < 40, sell more the smaller, sell 50% of starting money at 0
        Do nothing if 50 
        This buy and sell logic was made up to simulate high volume swing trading.
        """
        # find FnG for current day
        current_date = datetime.fromtimestamp(self.current_time, tz=timezone.utc).strftime('%m-%d-%Y')

        current_fng = self.fng_df['value'].loc[self.fng_df['date'] == current_date]
        if current_fng.empty:
            print(f'Current date: {current_date}')
            raise ValueError('No Fear and Greed data for date found. Fear and greed data starts 02-01-2018')
        elif len(current_fng.index) > 1:
            raise ValueError('Somehow found more than one Fear and Greed value for a single day')
        else:
            current_fng = current_fng.values[0]

        # buy if > 60, aka greedy
        if current_fng >= 60:
            # Determine how much to buy (buy 50% of money at 100)
            # Buy (.5*FnG)% aka 60 -> buy 30%
            # Buy the greater of starting_usd vs current_usd
            buy_amount_start = self.starting_usd * ((current_fng*.5)/100)
            buy_amount_current = self.current_usd * ((current_fng*.5)/100)
            if buy_amount_start > buy_amount_current:
                buy_amount = buy_amount_start
            else:
                buy_amount = buy_amount_current

            # If buy amount is > than current dollars, set buy to max
            if buy_amount > self.current_usd:
                buy_amount = self.current_usd
            # Buy
            if buy_amount > 0:
                # print(f'Current usd: ${bs.unfrac(self.current_usd)}')
                # print(f'Buy amount: ${buy_amount}')
                self.buy_eth(usd_eth_to_buy=buy_amount)

        # sell if < 40, aka fearful
        elif current_fng <= 40:
            # determine how much to sell (sell 50% of starting money at 0)
            # Sell (50-(.5*FnG))% aka 40 -> sell 30%
            # Sell the greater of starting_usd vs current_usd
            sell_amount_start = self.starting_usd * ((50-(.5*current_fng))/100)
            sell_amount_current = self.current_eth * self.current_price * ((50-(.5*current_fng))/100)
            if sell_amount_start > sell_amount_current:
                sell_amount = sell_amount_start
            else:
                sell_amount = sell_amount_current

            # if sell amount is > than current eth (in dollars), set sell to max
            if sell_amount > self.current_eth*self.current_price:
                sell_amount = self.current_eth*self.current_price
            # sell
            if sell_amount > 0:
                # print(f'Current eth in usd: ${bs.unfrac(self.current_eth * self.current_price)}')
                # print(f'sell amount: ${sell_amount}')
                self.sell_eth(usd_eth_to_sell=sell_amount)
        # return nothing

    def run_logic(self):
        """
        Holds the strategies main logic function.
        Overrides the Strategy version's function.
        """
        print(f'{self.name} started.')
        # Give a rough measure of how long this took
        real_start_time = time.time()
        
        # loop until we hit the LoopComplete exception
        while not self.done_buying:
            try:
                self.buy_sell_logic()
                self.go_to_next_action()
            except bs.LoopComplete:
                self.done_buying = True

        # Now add data to the results csv files
        self.add_data_to_results()
        print(f'{self.name} completed!')
        print(f'Seconds taken: {round(time.time()-real_start_time, 2)}\n')
