"""
Binance API integration for cryptocurrency price data.
Free public API endpoint access.
"""
import requests
from utils.logging import debug_log
from utils.http_utils import make_rate_limited_request


def try_binance():
    """Try to get prices from Binance"""
    print("🔍 DEBUG: Starting try_binance() function")
    
    try:
        symbols = [("BTC", "BTCUSDT"), ("ETH", "ETHUSDT"), ("BNB", "BNBUSDT"), ("POL", "POLUSDT")]
        prices = {}
        errors = []
        
        print(f"🔍 DEBUG: Will process {len(symbols)} symbols: {[s[0] for s in symbols]}")
        
        for i, (symbol, pair) in enumerate(symbols):
            print(f"🔍 DEBUG: Processing {i+1}/{len(symbols)}: {symbol} ({pair})")
            try:
                print(f"🔍 DEBUG: Calling get_binance_price('{pair}')...")
                price = get_binance_price(pair)
                print(f"📊 DEBUG: get_binance_price returned: {price} (type: {type(price)})")
                
                if price is not None and price > 0:
                    prices[symbol] = price
                    print(f"✅ DEBUG: Binance {symbol} price accepted: {price}")
                else:
                    prices[symbol] = None
                    error_msg = f"{symbol}: Invalid price returned: {price}"
                    errors.append(error_msg)
                    print(f"❌ DEBUG: Binance {symbol} invalid price: {price}")
                    
            except Exception as e:
                prices[symbol] = None
                error_msg = f"{symbol}: {str(e)}"
                errors.append(error_msg)
                print(f"❌ DEBUG: Binance {symbol} exception: {str(e)} (type: {type(e)})")
        
        result = {
            'prices': prices,
            'errors': errors,
            'success_count': len([p for p in prices.values() if p is not None]),
            'source': 'Binance'
        }
        
        print(f"🏁 DEBUG: Binance result - Success: {result['success_count']}/4")
        print(f"🏁 DEBUG: Binance prices: {prices}")
        print(f"🏁 DEBUG: Binance errors: {errors}")
        
        return result
        
    except Exception as e:
        error_msg = f"Binance unexpected error: {str(e)}"
        print(f"❌ DEBUG: Binance unexpected error: {error_msg}")
        raise Exception(error_msg)


def get_binance_crypto_prices():
    """
    Get cryptocurrency prices from Binance API
    
    Returns:
        dict: Dictionary with price data and metadata
    """
    return try_binance()


def get_binance_price(symbol):
    """
    Fetches the latest price for a symbol from Binance.
    Optimized for Streamlit Community Cloud deployment.
    Raises exceptions for transparent error reporting.
    Returns price as float if successful.
    """
    try:
        # Cloud-optimized settings
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        
        # Shorter timeout for cloud environments + explicit headers
        headers = {
            'User-Agent': 'StreamlitApp/1.0',
            'Accept': 'application/json',
            'Connection': 'close'  # Important for cloud environments
        }
        
        response = requests.get(
            url, 
            timeout=5,  # Reduced from 10s for cloud
            headers=headers
        )
        
        # Log detailed response info for cloud debugging
        print(f"🌐 {symbol} API Response: Status={response.status_code}, Content-Length={len(response.text)}")
        
        response.raise_for_status()
        
        try:
            data = response.json()
        except Exception as json_err:
            raise Exception(f"JSON parse failed - Raw response: {response.text[:100]}")
        
        if 'price' not in data:
            raise Exception(f"Missing 'price' field in API response: {data}")
        
        try:
            price = float(data['price'])
        except (ValueError, TypeError) as conv_err:
            raise Exception(f"Price conversion failed - Raw price: '{data['price']}' ({type(data['price'])})")
        
        if price <= 0:
            raise Exception(f"Invalid price value: {price}")
            
        print(f"✅ {symbol}: ${price:,.2f}")
        return price
        
    except requests.exceptions.Timeout:
        raise Exception(f"{symbol} API timeout after 5s (cloud limit)")
    except requests.exceptions.ConnectionError:
        raise Exception(f"{symbol} network connection failed (cloud connectivity issue)")
    except requests.exceptions.HTTPError as e:
        status_code = getattr(e.response, 'status_code', 'unknown')
        response_text = getattr(e.response, 'text', 'no response text')[:100]
        raise Exception(f"{symbol} HTTP error {status_code} - Response: {response_text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"{symbol} request failed: {str(e)}")
    except Exception as e:
        # Catch any other exceptions and make them transparent
        raise Exception(f"{symbol} unexpected error: {str(e)}")

def test_binance_api():
    """
    Test function to diagnose Binance API issues.
    Returns detailed diagnostic information.
    """
    import json
    
    test_results = {}
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "POLUSDT"]
    
    for symbol in symbols:
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            response = requests.get(url, timeout=5)
            
            test_results[symbol] = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'raw_content': response.text[:200],  # First 200 chars
                'content_length': len(response.text),
                'url': url
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    test_results[symbol]['json_data'] = data
                    test_results[symbol]['price_field'] = data.get('price', 'MISSING')
                except:
                    test_results[symbol]['json_error'] = 'Failed to parse JSON'
            
        except Exception as e:
            test_results[symbol] = {'error': str(e)}
    
    return test_results

def cloud_diagnostics():
    """
    Cloud-specific diagnostics for Streamlit Community Cloud debugging.
    This function provides detailed environment and API information.
    """
    import sys
    import os
    import platform
    
    diagnostics = {
        'environment': {
            'python_version': sys.version,
            'platform': platform.platform(),
            'working_directory': os.getcwd(),
            'environment_vars': {
                'USER': os.environ.get('USER', 'unknown'),
                'HOME': os.environ.get('HOME', 'unknown'),
                'PATH': os.environ.get('PATH', 'unknown')[:100] + '...'  # Truncated
            }
        },
        'api_tests': {}
    }
    
    # Test each API endpoint with detailed logging
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "POLUSDT"]
    
    for symbol in symbols:
        try:
            print(f"🔍 Testing {symbol} on cloud environment...")
            
            # Use the same exact call as the main function
            price = get_binance_price(symbol)
            
            diagnostics['api_tests'][symbol] = {
                'status': 'SUCCESS',
                'price': price,
                'price_type': str(type(price)),
                'price_valid': price > 0 if price else False
            }
            
        except Exception as e:
            diagnostics['api_tests'][symbol] = {
                'status': 'FAILED', 
                'error': str(e),
                'error_type': str(type(e))
            }
            print(f"❌ {symbol} failed: {e}")
    
    return diagnostics
