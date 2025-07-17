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
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'price' in data:
            return float(data['price'])
        else:
            print(f"Warning: No price data for {symbol}")
            return 0.0
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {symbol} price: {e}")
        return 0.0
    except (ValueError, KeyError) as e:
        print(f"Error parsing {symbol} price data: {e}")
        return 0.0
