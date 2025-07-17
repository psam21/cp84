"""
Module to fetch Bitcoin OHLC data from Bitfinex.
"""
import os
import time
import pandas as pd
import requests

DATA_FILE = "btc_ohlc_weekly_data.csv"
API_ENDPOINT = "https://api-pub.bitfinex.com/v2/candles/trade:7D:tBTCUSD/hist"

def get_btc_ohlc_data():
    """
    Reads weekly Bitcoin OHLC data from the local CSV file.
    If the file doesn't exist, it fetches all data from 2013.
    """
    if not os.path.exists(DATA_FILE):
        fetch_and_update_data()
    
    return pd.read_csv(DATA_FILE, index_col='date', parse_dates=True)

def fetch_and_update_data():
    """
    Fetches new weekly Bitcoin OHLC data and appends it to the local CSV.
    Fetches in chunks of 100 weeks.
    """
    all_new_data = []
    start_time = int(pd.Timestamp('2013-01-01').value / 1_000_000)

    existing_df = None
    if os.path.exists(DATA_FILE):
        existing_df = pd.read_csv(DATA_FILE, index_col='date', parse_dates=True)
        if 'volume' in existing_df.columns:
            existing_df.drop(columns=['volume'], inplace=True)
            existing_df.to_csv(DATA_FILE) # Save the file back without the volume column
        if not existing_df.empty:
            start_time = int(existing_df.index.max().value / 1_000_000) + 1

    current_start = start_time
    limit = 100 # 100 weeks per request

    while True:
        params = {
            'start': current_start,
            'limit': limit,
            'sort': 1 # Sort from oldest to newest
        }
        response = requests.get(API_ENDPOINT, params=params, timeout=30)
        data = response.json()

        if data:
            all_new_data.extend(data)
            # The last timestamp in the response is the newest
            last_timestamp_ms = data[-1][0]
            current_start = last_timestamp_ms + 1
        else:
            # No more data to fetch
            break
        
        # Stop if we have fetched up to the current time
        if current_start > int(time.time() * 1000):
            break
        
        time.sleep(1) # To avoid hitting rate limits

    if all_new_data:
        new_df = pd.DataFrame(all_new_data, columns=['mts', 'open', 'close', 'high', 'low', 'volume'])
        new_df['date'] = pd.to_datetime(new_df['mts'], unit='ms')
        new_df = new_df.drop(columns=['mts', 'volume'])
        new_df = new_df.set_index('date')
        
        if existing_df is not None:
            combined_df = pd.concat([existing_df, new_df])
            combined_df = combined_df[~combined_df.index.duplicated(keep='last')]
        else:
            combined_df = new_df
            
        combined_df.sort_index(inplace=True)
        combined_df.to_csv(DATA_FILE)

    return True
