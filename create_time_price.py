"""
Create the time price periods used for strategies here. Then import them for use elsewhere.
"""

import time
import datetime
import pandas as pd
# Create a new csv file for each new time period.
# Aka bear_to_bear would be its own file.
# bull_to_bear would be another csv file.

# Run specific functions in this file to create the csv's
sorted_list_of_csv = [
    'sorted_full_data_2018.csv',
    'sorted_full_data_2019.csv',
    'sorted_full_data_2020.csv',
    'sorted_full_data_2021.csv'
]

# Create arbitrary plot
# def create_time_period(start, end, name):
#     """
#     Loops through csv until time > start and continue until end < time.
#     If the end of a file is reached, open the next one.
#     Save the resulting data as a new csv called 'name.csv'
#     """
#     start = int(time.mktime(datetime.datetime.strptime(start, "%m/%d/%Y").timetuple()))
#     print(f'Start timestamp: {start}')
#     end = int(time.mktime(datetime.datetime.strptime(end, "%m/%d/%Y").timetuple()))
#     print(f'End timestamp: {start}')
#     new_df = pd.DataFrame(columns=['timestamp','price'])

#     for csv in sorted_list_of_csv:
#         # read data in
#         data = pd.read_csv(f'csv_files\\{csv}')
#         end_time_of_csv = data['timestamp'].iloc[-1]
#         # Check if end_of_csv_time < start: go to next csv
#         if end_time_of_csv < start:
#             continue
#         # Add all rows that are between start and end to new_df
#         new_df = new_df.append(
#             data.loc[
#                 (data['timestamp'] > start) &
#                 (data['timestamp'] < end)
#             ], ignore_index=True
#         )
#         # check if end_of_csv_time > end: stop collecting data
#         if end_time_of_csv > end:
#             break

#     print(new_df)
#     # Save df as csv
#     if not new_df.empty:
#         new_df.to_csv(f'csv_files\\{name}.csv')

def create_testing_time_period():
    pass
    # read csv in as df
    # read part of a csv in as a df?
