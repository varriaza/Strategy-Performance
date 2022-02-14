"""Contains the function that gets data from the Binance API"""
# imports
import time
import datetime
from binance import AsyncClient, Client
import lib.api_data as api # for Binance data

def get_binance_data(TRADING_PAIR='ETHUSDT', start_date='', end_date=''):
    # If we get a date, turn it to a timestamp, otherwise just continue
    if start_date != '' and not isinstance(start_date, int):
        start_date = int(time.mktime(datetime.datetime.strptime(start_date, "%Y-%m-%d-%H-%M-%S").timetuple()))
        # Then multiply by 1000 to match the format binance expects
        start_date = start_date*1000
    if end_date != '' and not isinstance(end_date, int):
        end_date = int(time.mktime(datetime.datetime.strptime(end_date, "%Y-%m-%d-%H-%M-%S").timetuple()))
        # Then multiply by 1000 to match the format binance expects
        end_date = end_date*1000

    # Initialise the client
    # NOTE: You will have to supply your OWN api keys to use this
    client = Client(api.get_api_key(), api.get_secret())

    if start_date == '':
        # get timestamp of earliest date data is available
        start_date = client._get_earliest_valid_timestamp(TRADING_PAIR, AsyncClient.KLINE_INTERVAL_1MINUTE)
        print(f'Earliest timestamp found: {int(start_date)/1000}')
        print(f'Human readable format: {time.ctime(int(start_date)/1000)}')

    # if we don't have an end_date, go until current time
    if end_date == '':
        # Get data from the beginning of the Binance data to now
        klines = client.get_historical_klines(
            TRADING_PAIR,
            AsyncClient.KLINE_INTERVAL_1MINUTE,
            start_date
        )
    else:
        # Get data between two specific times
        klines = client.get_historical_klines(
            TRADING_PAIR,
            AsyncClient.KLINE_INTERVAL_1MINUTE,
            start_str=start_date,
            end_str=end_date
        )
    # Print some of the data for reference
    print(f'Historical values found: {len(klines)}')
    print(f'Subset of data:\n{klines[0:5]}')

    return klines
