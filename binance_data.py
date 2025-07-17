"""
Module to fetch data from Binance.
"""
import requests

def get_binance_price(symbol):
    """
    Fetches the latest price for a symbol from Binance.
    Returns 0.0 if there's an error.
    """
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        print(f"Fetching {symbol} from: {url}")  # Debug log
        
        response = requests.get(url, timeout=15)  # Increased timeout
        print(f"Response status for {symbol}: {response.status_code}")  # Debug log
        
        response.raise_for_status()
        data = response.json()
        print(f"Response data for {symbol}: {data}")  # Debug log
        
        if 'price' in data:
            price = float(data['price'])
            print(f"Successfully got {symbol} price: {price}")  # Debug log
            return price
        else:
            print(f"Warning: No price data for {symbol}")
            return 0.0
            
    except requests.exceptions.Timeout as e:
        print(f"Timeout error fetching {symbol}: {e}")
        return 0.0
    except requests.exceptions.RequestException as e:
        print(f"Request error fetching {symbol}: {e}")
        return 0.0
    except (ValueError, KeyError) as e:
        print(f"Data parsing error for {symbol}: {e}")
        return 0.0
    except Exception as e:
        print(f"Unexpected error fetching {symbol}: {e}")
        return 0.0
