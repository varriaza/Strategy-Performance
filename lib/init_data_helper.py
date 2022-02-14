"""Helper functions for initializing data"""
from fractions import Fraction as frac
import time
import datetime
import numpy as np
import pandas as pd
import lib.base_strategy as bs

# Write function to merge binance and kaggle data
# (don't take duplicate, drop unneeded kaggle columns, save result as one file.)
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

# df1 = pd.read_csv('csv_files/test_c_df.csv')
# df2 = pd.read_csv('csv_files/test_c_df2.csv')
# compare_dataset_timestamps(df1, df2)

# validate that we are not missing any timestamps by checking that the next timestamp is sixty seconds in the future
def check_missing_timestamp(df, debug=False):
    """
    Validate that we are not missing any timestamps by checking that the next timestamp is sixty seconds in the future
    The last timestamp will always fail so print that out for human visual removal
    """
    df_missing = df['timestamp'].loc[~(df['timestamp'].astype(int)+60).isin(df['timestamp'])].astype(int)
    print(f'Missing timestamps (add 60 sec): \n{df_missing.to_string()}')
    print(f'Number of missing timestamps: {len(df_missing.index)}')
    print(f'Ignore last timestamp of: {df["timestamp"].values[-1]}\n')
    if debug:
        return df_missing

# df3 = pd.read_csv('csv_files/test_c_df3.csv')
# check_missing_timestamp(df3)

def make_average(df_row, new_row_name):
    # if the first column is null, use the second
    if pd.isnull(df_row[new_row_name+'_1']):
        df_row[new_row_name] = frac(df_row[new_row_name+'_2'])
    # if the second column is null, use the first
    elif pd.isnull(df_row[new_row_name+'_2']):
        df_row[new_row_name] = frac(df_row[new_row_name+'_1'])
    # If we need fraction_price, make the values fractions type
    elif new_row_name == 'fraction_price':
        df_row[new_row_name] = (frac(df_row[new_row_name+'_1']) + frac(df_row[new_row_name+'_2']))/2
    # If we need decimals, round to the fourth digit
    elif new_row_name == 'decimal_price':
        df_row[new_row_name] = round((df_row[new_row_name+'_1'] + df_row[new_row_name+'_2'])/2, 4)
    # Just default to column_1 for timestamps
    elif new_row_name == 'timestamp':
        df_row[new_row_name] = df_row[new_row_name+'_1']
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
    combined_dataframes = df1.set_index('index').join(df2.set_index('index'), how='outer', lsuffix='_1', rsuffix='_2')
    # Make 'index' a regular column after we got rid of it above
    combined_dataframes['index'] = combined_dataframes.index

    # Set average fraction_price
    combined_dataframes['fraction_price'] = np.nan
    combined_dataframes = combined_dataframes.apply(lambda x: make_average(x, 'fraction_price'), axis=1)

    # Set average decimal_price
    combined_dataframes['decimal_price'] = np.nan
    combined_dataframes = combined_dataframes.apply(lambda x: make_average(x, 'decimal_price'), axis=1)

    # Reset timestamp due to merge
    combined_dataframes['timestamp'] = np.nan
    combined_dataframes = combined_dataframes.apply(lambda x: make_average(x, 'timestamp'), axis=1)

    # drop all columns we don't want
    combined_dataframes = combined_dataframes.filter(['index', 'timestamp', 'fraction_price', 'decimal_price'])
    # Drop duplicates and sort
    combined_dataframes = combined_dataframes.drop_duplicates(
        subset=['timestamp']).sort_values(by=['timestamp'], ignore_index=True
    )
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
    print(f'Start timestamp: {start}')
    print(f'End timestamp: {end}')
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

    # Rename the actual index to 'index'
    new_df.index.names = ['index']

    # Save df as csv
    if not new_df.empty:
        new_df.to_csv(bs.period_path(name+'.csv'))
