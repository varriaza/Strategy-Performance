"""Helper functions for initializing data"""
from fractions import Fraction as frac
import time
import datetime
import numpy as np
import pandas as pd
import lib.base_strategy as bs

def compare_dataset_timestamps(df1, df2, debug=False):
    """
    Take in two dataframes, and find the values where timestamps are unique.
    Print those values and the indexes that they're at for both dataframes.
    """
    df1_unique = df1['timestamp'].loc[~df1['timestamp'].isin(df2['timestamp'])]
    df2_unique = df2['timestamp'].loc[~df2['timestamp'].isin(df1['timestamp'])]
    print(f'df1_unique:\nindex, timestamp\n{df1_unique}\n')
    print(f'df2_unique:\nindex, timestamp\n{df2_unique}')
    if debug:
        return df1_unique, df2_unique

def check_missing_timestamp(df, debug=False):
    """
    Validate that we are not missing any timestamps by checking that the next timestamp is sixty seconds in the future
    """
    # Find values where there is no timestamp equal to the current one +60 seconds
    # Then add 60 to the current timestamp so we can see which timestamp is missing
    df_missing = df['timestamp'].loc[~(df['timestamp'].astype(int)+60).isin(df['timestamp'])].astype(int)+60
    # Drop the last value as that will always not have a timestamp 60 seconds after it
    df_missing = df_missing.drop(index=df_missing.index.values[-1])
    print(f'Number of missing timestamps: {len(df_missing.index)}')
    print(f'Missing timestamps: \n{df_missing.values}')
    if debug:
        return df_missing

def check_price_jump(df, debug=False):
    """
    See if we have any instances where price fluctuates rapidly.
    This could be a sign of bad data, or a really hot market.
    """
    # Find values where the price after the current is + or - 10%
    # A 10% move over a minute is pretty big so false positives from hot/bad markets shouldn't be caught too often
    difference = .1
    # Make a shifted decimal_price column to compare against
    df['next_decimal_price'] = df['decimal_price'].shift(-1)
    # Drop the first and last rows since we won't have prices to compare against
    df = df.dropna()
    # Find values and reset index to be accurate for the new dataframe
    df = df.loc[
        (df['next_decimal_price'] >= df['decimal_price']*(1+difference)) |
        (df['next_decimal_price'] <= df['decimal_price']*(1-difference))
    ].reset_index(drop=True)
    # Show how big the jump is (aka decimal_price*multiplier=next_decimal_price)
    df['multiplier'] = round(df['next_decimal_price']/df['decimal_price'], 2)

    print(f'Looking for a difference of {difference*100}% or more.')
    print(f'Number of jumps: {len(df.index)}')
    print(f'Big Jumps: \n{df.to_string()}')
    if debug:
        return df

def make_average(df_row, new_row_name):
    # if the first column is null, use the second
    if pd.isnull(df_row[new_row_name+'_1']):
        # Don't use frac if we want a decimal
        if new_row_name == 'decimal_price':
            df_row[new_row_name] = df_row[new_row_name+'_2']
        else:
            df_row[new_row_name] = frac(df_row[new_row_name+'_2'])
    # if the second column is null, use the first
    elif pd.isnull(df_row[new_row_name+'_2']):
        # Don't use frac if we want a decimal
        if new_row_name == 'decimal_price':
            df_row[new_row_name] = df_row[new_row_name+'_1']
        else:
            df_row[new_row_name] = frac(df_row[new_row_name+'_1'])
    # If we need fraction_price, make the values fractions type
    elif new_row_name == 'fraction_price':
        df_row[new_row_name] = (frac(df_row[new_row_name+'_1']) + frac(df_row[new_row_name+'_2']))/2
    # If we need decimals, round to the fourth digit
    elif new_row_name == 'decimal_price':
        df_row[new_row_name] = round((df_row[new_row_name+'_1'] + df_row[new_row_name+'_2'])/2, 4)
    else:
        raise ValueError('new_row_name misspelt!')
    return df_row

def combine_datasets(df1, df2):
    """
    Combine dataframes into one massive one, return output.
    Average fraction_price and decimal_price for all duplicates.
    Keep average price, drop the rest of the duplicates
    """
    # Combine the dataframes
    combined_dataframes = df1.set_index('timestamp').join(
        df2.set_index('timestamp'), how='outer', lsuffix='_1', rsuffix='_2'
    )
    # Set average fraction_price
    combined_dataframes['fraction_price'] = np.nan
    combined_dataframes = combined_dataframes.apply(lambda x: make_average(x, 'fraction_price'), axis=1)

    # Set average decimal_price
    combined_dataframes['decimal_price'] = np.nan
    combined_dataframes = combined_dataframes.apply(lambda x: make_average(x, 'decimal_price'), axis=1)

    # Reset the index so we can get regular numbers instead of timestamps
    # and make timestamp a column instead of the index
    combined_dataframes = combined_dataframes.reset_index(level='timestamp')
    # Make index a column using the dataframe's new index
    combined_dataframes['index'] = combined_dataframes.index
    # Drop all columns we don't want
    combined_dataframes = combined_dataframes.filter(['index', 'timestamp', 'fraction_price', 'decimal_price'])
    return combined_dataframes

def create_price_period(start, end, name, csv='Combined_ETH_all_price_data.csv'):
    """
    Loops through csv until time > start and continue until end < time.
    If the end of a file is reached, open the next one.
    Save the resulting data as a new csv called 'name.csv'
    """
    # If we get a date, turn it to a timestamp, otherwise just continue
    if not isinstance(start, int):
        start = int(time.mktime(datetime.datetime.strptime(start, "%m/%d/%Y").timetuple()))
    if not isinstance(end, int):
        end = int(time.mktime(datetime.datetime.strptime(end, "%m/%d/%Y").timetuple()))
    print(f'Start timestamp: {start} | End timestamp: {end}')
    new_df = pd.DataFrame(columns=['timestamp'])

    # read data in
    data = pd.read_csv(bs.full_path(csv))
    data = data.drop(['index'], axis=1)
    # Add all rows that are between start and end to new_df
    new_df = new_df.append(
        data.loc[
            (data['timestamp'] > start) &
            (data['timestamp'] < end)
        ], ignore_index=True
    )

    if data['timestamp'].values[-1] < end:
        print(f'WARNING! - End of current price data reached: {data["timestamp"].values[-1]}')
        print(f'Ending timestamp given: {end}! Script will continue, just using all available data.')

    # Rename the actual index to 'index'
    new_df.index.names = ['index']

    # Save df as csv
    if not new_df.empty:
        new_df.to_csv(bs.period_path(name+'.csv'))

    # Pretty spacing
    print('\n')
