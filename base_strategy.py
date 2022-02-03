"""
Base strategy class.
Gets inherited by specific strategies.
"""
from fractions import Fraction as frac
import pandas as pd

class LoopComplete(Exception):
    """
    Raised to indicate that the loop has reached the end of the price_period csv.
    """

def unfrac(fraction, round_to=4):
    """Turn a fraction into a float rounded to the fourth decimal."""
    float_num = round(float(fraction), round_to)
    # # To avoid a DeprecationWarning from directly going from fractions to floats,
    # # do the calculation explicitly.
    # numerator = fraction.numerator
    # denominator = fraction.denominator
    # float_num = round(numerator/denominator, round_to)
    return float_num

def price_period_results_path(csv):
    """Path to price_periods results csv files."""
    # Make sure we have the file ending
    if csv[-4:] != '.csv':
        csv = csv + '.csv'
    return f'results\\price_periods\\{csv}'

def returns_history_path(csv):
    """Path to returns_history results csv files."""
    # Make sure we have the file ending
    if csv[-4:] != '.csv':
        csv = csv + '.csv'
    return f'results\\returns_history\\{csv}'

def strategy_results_path(csv):
    """Path to strategy results csv files."""
    # Make sure we have the file ending
    if csv[-4:] != '.csv':
        csv = csv + '.csv'
    return f'results\\strategies\\{csv}'

def period_path(csv):
    """Path to price_period csv files."""
    # Make sure we have the file ending
    if csv[-4:] != '.csv':
        csv = csv + '.csv'
    return f'price_period_csv\\{csv}'

class Strategy:
    """Base strategy class, specific strategies should inherent this."""
    def __init__(
        self,
        name,
        starting_usd,
        time_between_action,
        price_period_name,
        price_df = pd.DataFrame(),
        starting_eth = 0,
        save_results = True
    ):
        # Save if we should save the results of this run (used to stop tests adding info)
        self.save_results = save_results
        # Name of the strategy
        self.name = name
        # Name of the price period given
        self.price_period_name = price_period_name
        print(f'Running strategy for: {name}')
        print(f'For price period of: {price_period_name}')
        # Holds the historical price data, open file using price_period_name.csv if no df given
        if price_df.empty:
            self.price_df = pd.read_csv(period_path(price_period_name))
        else:
            self.price_df = price_df
        self.start_time = int(self.price_df['timestamp'].iloc[0])
        self.end_time = int(self.price_df['timestamp'].iloc[-1])
        self.max_index = int(self.price_df.index.values[-1])
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
        self.current_price = frac(self.price_df['fraction_price'].iloc[0])
        self.starting_total_value = self.starting_usd + (self.starting_eth*self.current_price)
        self.trades_made = 0
        # set trading fee, using uniswap's 0.3%. Aka 100-0.3=99.7
        self.trading_fee = frac(99.7/100)
        # Keep track of fees paid
        self.fees_paid = frac(0)
        # Create all of the rows for price_df so we don't have to append rows, just add data
        # Get timestamps and fraction_price from price_df
        self.returns_df = pd.DataFrame(self.price_df[['timestamp', 'fraction_price', 'decimal_price']])
        # Add other columns we need
        self.returns_df = self.returns_df.append(pd.DataFrame(columns=[
            '# of USD',
            '# of ETH',
            'Total Value',
            '% Return'
        ]))
        # Rename the index to 'index'
        self.returns_df.index.names = ['index']
        # Make sure the first row has initial data
        self.add_to_returns(time_slice=(self.price_df['timestamp'] == self.current_time))

    def run_logic(self):
        """
        Override this.
        Holds the strategies main logic function.
        """
        raise NotImplementedError('Override this.')

    def go_to_next_action(self):
        """
        Move time forward until the next buy period in an optimized way.
        Raise LoopComplete when we reach the last index.
        Optimized version.
        """
        # get all values between time+delta_time
        time_slice = ((self.price_df['timestamp'] >= self.current_time) &
            (self.price_df['timestamp'] < self.current_time+self.time_between_action))

        # add_to_returns for all values given
        self.add_to_returns(time_slice)
        # Go to the final index + 1
        self.current_index = int(self.price_df.loc[time_slice].index[-1])+1
        # stop if done looping
        if self.current_index > self.price_df.index[-1]: # pylint: disable=no-member
            # set index to last value
            self.current_index = int(self.price_df.index[-1]) # pylint: disable=no-member
            # update current time/price for last values
            self.current_time = self.price_df['timestamp'].iloc[self.current_index]
            # Update price so we can update total value/total returns
            self.current_price = frac(self.price_df['fraction_price'].iloc[self.current_index])
            raise LoopComplete('All done')
        # update current time/price for latest index values
        self.current_time = self.price_df['timestamp'].iloc[self.current_index]
        # Update price so we can update total value/total returns
        self.current_price = frac(self.price_df['fraction_price'].iloc[self.current_index])

    def add_to_returns(self, time_slice):
        """
        Called on buy or sell. Adds current values to returns df.
        Optimized version.
        """
        self.returns_df.loc[time_slice, [
            '# of USD',
            '# of ETH'
        ]] = [
            unfrac(self.current_usd),
            unfrac(self.current_eth),
        ]

    def get_total_value(self):
        """
        Returns the total USD+ETH portfolio value in USD
        """
        return self.current_usd + (self.current_eth*self.current_price)

    def get_returns(self):
        """
        Returns annualized % Return
        """
        # annualized returns should be returns/year
        # delta_t is seconds
        delta_t = float(self.current_time - self.start_time)
        # convert seconds to year (account for a fourth of a leap year day)
        seconds_in_year = 60*60*24*365.25
        fraction_of_year = frac(delta_t)/frac(seconds_in_year)
        return_val = (self.get_total_value()*frac(100)/self.starting_total_value)-frac(100)
        # Avoid divide by zero and numerator is zero
        if fraction_of_year == 0 or return_val == 0:
            returns = 0
        else:
            returns = return_val/fraction_of_year
        return returns

    def sharpe_ratio_of_returns(self):
        """
        Calculate the sharpe ratio of a column for a dataframe. This is a measure of risk vs reward.
        Higher numbers offer better reward for how risky (volatile) they are.
        Formula is as follows:
        sharpe ratio = ((average_annual_expected_return)-(annual_risk_free_return))/(sigma)
        annual_expected_return = annual expected return of the strategy
        risk free rate = set by as default of 3% (0.03) (stable coin lp-ing, Aave lending and etc)
        sigma = standard deviation of anualized returns
        """
        # Drop na values in case we are not at the end of the price period
        returns = self.returns_df['% Return'].dropna()
        # Divide by 100 to turn % return into decimal version
        # eg 14% -> .14
        average_annual_expected_return = (returns/100).mean()
        annual_risk_free_return = .03
        sigma = (self.returns_df['% Return']/100).std()
        # If we have all the same return, like 0, then the std is 0.
        # This makes the sharpe ratio undefined due to dividing by zero
        if pd.isna(sigma):
            return 'undefined'
        return round((average_annual_expected_return-annual_risk_free_return)/sigma, 4)

    def sortino_ratio_of_returns(self):
        """
        Calculate the sortino ratio of a column for a dataframe. This is a measure of risk vs reward.
        However, sortino only uses negative volatility as risk/sigma.
        Higher numbers offer better reward for how risky (volatile) they are.
        Formula is as follows:
        sortino ratio = ((average_annual_expected_return)-(annual_risk_free_return))/(sigma)
        annual_expected_return = annual expected return of the strategy
        risk free rate = set by as default of 3% (0.03) (stable coin lp-ing, Aave lending and etc)
        sigma = downside only standard deviation of anualized returns
        """
        # Drop na values in case we are not at the end of the price period
        returns = self.returns_df['% Return'].dropna()
        # Divide by 100 to turn % return into decimal version
        # eg 14% -> .14
        average_annual_expected_return = (returns/100).mean()
        annual_risk_free_return = .03
        # Only use returns that are less than 0
        sigma = (self.returns_df['% Return'].loc[self.returns_df['% Return'] < 0]/100).std()
        # If we have no negative returns, the sortino ratio is undefined due to dividing by zero
        if pd.isna(sigma):
            return 'undefined'
        return round((average_annual_expected_return-annual_risk_free_return)/sigma, 4)

    def buy_eth(self, usd_eth_to_buy=0, eth_to_buy=0,):
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
            print(f'Buy was for: {unfrac(usd_eth_to_buy)} USD')
            print(f'Current USD is: {unfrac(self.current_usd)}')
            print(f'Current time is: {self.current_time}')
            print(f'Current index is: {self.current_index}')
            raise ValueError(
                'Current USD cannot be negative. There is a logic error in this strategy.'
            )
        # deduct the trading fee from the ETH that is returned
        # trading_fee is formatted as x/100, where x=100-fee
        eth_amount_to_buy = usd_eth_to_buy/self.current_price
        # Make the fee denominated in USD and ETH for each use case
        eth_fee = (eth_amount_to_buy*(frac(1)-self.trading_fee))
        usd_fee = usd_eth_to_buy*(frac(1)-self.trading_fee)
        self.fees_paid += usd_fee
        self.current_eth += eth_amount_to_buy-eth_fee
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
        # deduct the trading fee from the USD that is returned
        # trading_fee is formatted as x/100, where x=100-fee
        amount_to_sell = eth_to_sell*self.current_price
        # The fee only needs to be denominated in USD for sells
        usd_fee = amount_to_sell*(frac(1)-self.trading_fee)
        self.fees_paid += usd_fee
        self.current_eth -= eth_to_sell
        self.current_usd += amount_to_sell-usd_fee
        self.trades_made += 1

    def add_data_to_results(self, testing=False):
        """
        Calculates the following values and adds them to csv's in the results folder
        """
        def new_results_row(value_dict, table_name, row_name, row_value):
            """
            Performs the specific logic to update/create a results table.
            Used for both 'Strategy' tables and 'Time Period' tables.
            """
            if row_name == 'Strategy':
                path_to_results = price_period_results_path(table_name)
            elif row_name == 'Price Period':
                path_to_results = strategy_results_path(table_name)
            else:
                print(f'Unexpected value passed to new row: {row_name}')
                raise ValueError()
            # Price_period results update
            new_price_period_row = {
                row_name: row_value,
            }
            new_price_period_row.update(value_dict)
            price_period_columns = list(new_price_period_row.keys())
            # turn dictionary into dataframe
            new_price_period_row = pd.DataFrame(new_price_period_row, index=[0], columns=price_period_columns)

            # Check if csv file with price period name exists in results/price_periods
            try:
                # If it exists, read it in
                price_period_df = pd.read_csv(path_to_results)
            except FileNotFoundError:
                # If not, create it. Name = time period name
                price_period_df = pd.DataFrame(columns=price_period_columns)

            # Check if the strategy name already has a row
            if not price_period_df.empty and row_value in price_period_df[row_name].values:
                # If it does, delete the row and append the new data
                drop_index = price_period_df.loc[price_period_df[row_name].values == row_value].index[0] # pylint: disable=no-member
                price_period_df = price_period_df.drop([drop_index]) # pylint: disable=no-member

            # No matter what we will want to add the row
            price_period_df = price_period_df.append(new_price_period_row)
            # Rename index so we can call it easily
            price_period_df.index.names = ['index']

            # Sort rows by defining column
            price_period_df.sort_values(by=[row_name])
            # save df as csv
            price_period_df.to_csv(path_to_results, index=False)
            # END of function

        # Now, at the end in vector calculate Total Value and yearly_%_return
        # Use lambda function to make sure we have a fraction and not a string
        self.returns_df['Total Value'] = self.returns_df['# of USD']+(
            self.returns_df['# of ETH']*self.returns_df['fraction_price'].apply(lambda x: frac(x)))
        # Convert seconds to year (account for a fourth of a leap year day)
        seconds_in_year = 60*60*24*365.25
        # figure out how far into a year we are so we can annualize the returns
        # Use lambda as dataframes don't play nicely with fractions
        fraction_of_year = self.returns_df['timestamp'].apply(lambda x:
            frac(x-self.start_time)/
            frac(seconds_in_year)
        )
        # Remove the first entry in fraction_of_year as it will be 0
        fraction_of_year = fraction_of_year.drop([0])
        # Set first yearly return to zero so we don't have to divide by 0 in the next section
        self.returns_df.loc[0, ('% Return')] = 0
        # Then don't change the first entry
        self.returns_df.loc[1:, ('% Return')] = (
            (self.returns_df['Total Value'].drop([0])*100/self.starting_total_value)-100
            )/fraction_of_year
            # ^ be careful of dividing by 0

        # Round the new columns, Total Value and % Return
        # Break into two columns so we can use astype, otherwise we can get problems due to typing
        self.returns_df['Total Value'] = self.returns_df['Total Value'].astype(float).round(4)
        self.returns_df['% Return'] = self.returns_df['% Return'].astype(float).round(4)

        # drop fraction_price
        self.returns_df = self.returns_df.drop(['fraction_price'], axis = 1)
        # rename decimal_price to price
        self.returns_df.rename(columns = {'decimal_price':'price'}, inplace = True)

        # Calculate values
        # Make this a dictionary that we can add where needed
        value_dict = {
            # - Price delta (start to end)
            'Price Delta': unfrac(
                frac(self.price_df['fraction_price'].iloc[-1])-frac(self.price_df['fraction_price'].iloc[0])
            ),
            # - % Price delta
            '% Price Delta': unfrac(
                (frac(self.price_df['fraction_price'].iloc[-1])/frac(self.price_df['fraction_price'].iloc[0]))*frac(100)
            ),
            # Starting USD
            'Starting USD': unfrac(self.starting_usd),
            # Starting ETH
            'Starting ETH': unfrac(self.starting_eth),
            # Ending USD
            'Ending USD': unfrac(self.current_usd),
            # Ending ETH
            'Ending ETH': unfrac(self.current_eth),
            # Final total value in USD (USD + ETH)
            'Total Value in USD': unfrac(self.get_total_value()),
            # - Total ending value in USD (aka ending ETH+USD-starting_usd-starting_eth)
            'Returns in USD': unfrac(self.get_total_value()-self.starting_total_value),
            # Mean Annual % Return (aka average)
            'Mean Annual % Return': round(self.returns_df['% Return'].mean(), 4),
            # Median Annual % Return (aka middle number)
            'Median Annual % Return': round(self.returns_df['% Return'].median(), 4),
            # - % Total Returns (in USD)
            'Final Annual % Return': unfrac(self.get_returns()),
            # Median-Mean % Return (aka different is the positional average from the numerical average)
            'Median-Mean % Return': round(self.returns_df['% Return'].median()-self.returns_df['% Return'].mean(), 4),
            # - Total trades made (Helps show how intensive a strategy might be, also can be used for gas fee estimation later)
            'Trades Made': self.trades_made,
            # Fees paid
            'Fees Paid': unfrac(self.fees_paid),
            # Average dollar amount made per trade
            'Flat Return Per Trade': unfrac((self.get_total_value()-self.starting_total_value)/self.trades_made),
            # - % return per trade
            '% Return Per Trade': unfrac((self.get_returns())/self.trades_made),
            # - Risk vs Rewards of returns (Sharpe Ratio)
            'Sharpe of Returns': self.sharpe_ratio_of_returns(),
            # - (Negative) Risk vs Rewards of returns (Sortino Ratio)
            'Sortino of Returns': self.sortino_ratio_of_returns(),
            # - Volatility of price for time period (standard deviation)
            'Std of Price': round(self.price_df['decimal_price'].std(), 2)
        }

        # Return the values above if we are testing
        if testing:
            print(f'Real Values:\n{value_dict}')
            print(f'keys: \n{value_dict.keys()}')
            return value_dict

        # See if we need to save the results
        if self.save_results:
            # Add values to price_period df, or update row if it exists
                # Rows = strategy
                # Columns = values
            new_results_row(value_dict, table_name=self.price_period_name, row_name='Strategy', row_value=self.name)

            # Add values to strategy df, or update row if it exists
                # Rows = price periods
                # Columns = values
            new_results_row(value_dict, table_name=self.name, row_name='Price Period', row_value=self.price_period_name)

            # Save the returns history for use later
            returns_history_file_name = f'{self.name}_{self.price_period_name}_returns_history.csv'
            # save df as csv
            self.returns_df.to_csv(returns_history_path(returns_history_file_name), index=False)
