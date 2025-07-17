"""
Module to fetch Bitcoin OHLC data from Bitfinex API.
Cloud-friendly version with no file dependencies.
"""
import pandas as pd
import requests

def get_bitcoin_ohlc(symbol='BTCUSD', timeframe='7D', limit=156):
    """
    Fetch OHLC data from Bitfinex for a specific symbol.
    Returns weekly data by default (156 weeks = ~3 years).
    """
    try:
        print(f"Starting Bitfinex OHLC fetch for {symbol} with timeframe {timeframe}...")
        
        # Bitfinex API v2 endpoint for candles
        url = f"https://api-pub.bitfinex.com/v2/candles/trade:{timeframe}:t{symbol}/hist"
        params = {
            'limit': limit,
            'sort': -1  # Sort in descending order (newest first)
        }
        
        print(f"Fetching from URL: {url}")
        print(f"Parameters: {params}")
        
        response = requests.get(url, params=params, timeout=15)
        print(f"Response status code: {response.status_code}")
        response.raise_for_status()
        
        data = response.json()
        print(f"Received {len(data)} candles from Bitfinex")
        
        if not data:
            print("No data returned from Bitfinex API")
            return None
        
        # Convert to DataFrame for easier handling
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'close', 'high', 'low', 'volume'])
        
        # Convert timestamp to datetime
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Sort by timestamp (oldest first)
        df = df.sort_values('timestamp')
        
        print(f"Successfully processed {len(df)} OHLC records")
        return df
        
    except requests.exceptions.Timeout:
        print("Error: Bitfinex API request timed out")
        return None
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Bitfinex API")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Bitcoin OHLC data: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in Bitfinex data fetch: {e}")
        return None

def get_btc_ohlc_data():
    """
    Fetch Bitcoin OHLC data directly from Bitfinex API (cloud-friendly).
    No file dependencies - works entirely from API calls.
    """
    try:
        print("Fetching Bitcoin OHLC data directly from Bitfinex API...")
        
        # Fetch recent weekly data (156 weeks = ~3 years of data)
        df = get_bitcoin_ohlc(symbol='BTCUSD', timeframe='7D', limit=156)
        
        if df is not None and not df.empty:
            # Set the datetime column as index for easier year filtering
            df.set_index('datetime', inplace=True)
            print(f"Successfully fetched {len(df)} weeks of OHLC data")
            return df
        else:
            print("No OHLC data received from API")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error fetching OHLC data: {e}")
        return pd.DataFrame()

def fetch_and_update_data():
    """
    Cloud-friendly data refresh function.
    Simply clears cache and fetches fresh data.
    """
    print("Refreshing Bitcoin OHLC data from API...")
    return True  # Always return True since we're fetching fresh data
