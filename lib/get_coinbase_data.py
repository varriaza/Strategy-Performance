"""Contains the function that gets data from the CoinBase Pro API"""
# imports
from fractions import Fraction as frac
from lib.HistoricalData import HistoricalData # for CoinBase Pro

# HistoricalData() info:
# ticker | supply the ticker information which you want to return (str). 
# granularity | please supply a granularity in seconds (60, 300, 900, 3600, 21600, 86400) (int).
# start_date | a string in the format YYYY-MM-DD-HH-MM (str).
# end_date | a string in the format YYYY-MM-DD-HH-MM (str). Optional, Default: Now
# verbose | printing during extraction. Default: True

def get_coinbase_data(start_date, end_date=''):
    """Get data from CoinBase Pro API"""
    # how many seconds between data points
    trade_interval = 60
    if end_date == '':
        # Returns data as a dataframe
        coinbase_data = HistoricalData(
            'ETH-USD',
            trade_interval,
            start_date=start_date,
            # end_date='2019-01-6-00-00', # Comment out to use current time as end
            verbose=False
        ).retrieve_data()
    else:
        # Returns data as a dataframe
        coinbase_data = HistoricalData(
            'ETH-USD',
            trade_interval,
            start_date=start_date,
            end_date=end_date, # Comment out to use current time as end
            verbose=False
        ).retrieve_data()

    # make time no longer the index and rename it
    coinbase_data.reset_index(inplace=True)
    coinbase_data.rename(columns = {'time':'timestamp'}, inplace = True)
    # Make 'index' a regular column
    coinbase_data['index'] = coinbase_data.index

    # turn timestamp from a datetime into a timestamp, divide by 10**9 to get seconds as our units
    coinbase_data['timestamp'] = coinbase_data['timestamp'].apply(lambda x: int(x.value// 10**9))
    # Create price data
    coinbase_data['decimal_price'] = round(
        coinbase_data['open'] +
        coinbase_data['close'] +
        coinbase_data['high'] +
        coinbase_data['low'],
        4
    )
    # Then fractionalize the number to minimize floating point rounding errors
    coinbase_data['fraction_price'] = coinbase_data['decimal_price'].apply(lambda x: frac(x)/4)
    # Average out decimal price
    coinbase_data['decimal_price'] = coinbase_data['decimal_price']/4
    # drop all columns we don't want
    coinbase_data = coinbase_data.filter(['index', 'timestamp', 'fraction_price', 'decimal_price'])

    print(f'\nSubset of data:\n{coinbase_data.head(5)}')
    return coinbase_data
