"""
Multi-exchange API fallback system for cryptocurrency prices.
Tries multiple exchanges in order until successful.
Optimized for Streamlit Community Cloud reliability.
"""

def get_multi_exchange_prices():
    """
    Attempts to fetch prices from multiple exchanges with fallback.
    Priority order: Binance -> KuCoin -> Coinbase -> CoinGecko
    Returns the best available price data.
    """
    import sys
    import os
    
    # Add current directory to path for imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    
    results = {
        'prices': {'BTC': None, 'ETH': None, 'BNB': None, 'POL': None},
        'errors': [],
        'success_count': 0,
        'total_count': 4,
        'sources_used': []
    }
    
    # Try exchanges in order of preference
    exchanges = [
        ('Binance', try_binance),
        ('KuCoin', try_kucoin),
        ('Coinbase', try_coinbase),
        ('CoinGecko', try_coingecko)
    ]
    
    for exchange_name, exchange_func in exchanges:
        print(f"🔄 Trying {exchange_name} API...")
        
        try:
            exchange_result = exchange_func()
            
            if exchange_result['success_count'] > 0:
                results['sources_used'].append(exchange_name)
                
                # Fill in any missing prices
                for symbol in ['BTC', 'ETH', 'BNB', 'POL']:
                    if (results['prices'][symbol] is None and 
                        exchange_result['prices'].get(symbol) is not None):
                        results['prices'][symbol] = exchange_result['prices'][symbol]
                        print(f"✅ Got {symbol} price from {exchange_name}")
                
                # Update success count
                results['success_count'] = len([p for p in results['prices'].values() if p is not None])
                
                # If we have all prices, we can stop
                if results['success_count'] == 4:
                    print(f"🎉 All prices obtained! Sources: {', '.join(results['sources_used'])}")
                    break
                    
        except Exception as e:
            error_msg = f"❌ {exchange_name} failed: {str(e)}"
            results['errors'].append(error_msg)
            print(error_msg)
    
    # Add any remaining errors for missing prices
    for symbol in ['BTC', 'ETH', 'BNB', 'POL']:
        if results['prices'][symbol] is None:
            results['errors'].append(f"❌ {symbol}: All exchanges failed")
    
    return results

def try_binance():
    """Try to get prices from Binance"""
    try:
        from binance_data import get_binance_price
        
        symbols = [("BTC", "BTCUSDT"), ("ETH", "ETHUSDT"), ("BNB", "BNBUSDT"), ("POL", "POLUSDT")]
        prices = {}
        errors = []
        
        for symbol, pair in symbols:
            try:
                price = get_binance_price(pair)
                prices[symbol] = price
            except Exception as e:
                prices[symbol] = None
                errors.append(f"{symbol}: {str(e)}")
        
        return {
            'prices': prices,
            'errors': errors,
            'success_count': len([p for p in prices.values() if p is not None]),
            'source': 'Binance'
        }
    except ImportError:
        raise Exception("Binance module not available")

def try_kucoin():
    """Try to get prices from KuCoin"""
    try:
        from kucoin_data import get_kucoin_prices
        return get_kucoin_prices()
    except ImportError:
        raise Exception("KuCoin module not available")

def try_coinbase():
    """Try to get prices from Coinbase"""
    try:
        from coinbase_data import get_coinbase_prices
        return get_coinbase_prices()
    except ImportError:
        raise Exception("Coinbase module not available")

def try_coingecko():
    """Try to get prices from CoinGecko (free API, no auth required)"""
    import requests
    
    try:
        # CoinGecko free API - very reliable for cloud deployments
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': 'bitcoin,ethereum,binancecoin,polygon',  # CoinGecko IDs
            'vs_currencies': 'usd'
        }
        
        headers = {
            'User-Agent': 'StreamlitApp/1.0',
            'Accept': 'application/json',
            'Connection': 'close'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Map CoinGecko IDs to our symbol names
        price_mapping = {
            'bitcoin': 'BTC',
            'ethereum': 'ETH', 
            'binancecoin': 'BNB',
            'polygon': 'POL'
        }
        
        prices = {}
        errors = []
        
        for coingecko_id, symbol in price_mapping.items():
            if coingecko_id in data and 'usd' in data[coingecko_id]:
                price = float(data[coingecko_id]['usd'])
                if price > 0:
                    prices[symbol] = price
                    print(f"✅ CoinGecko {symbol}: ${price:,.2f}")
                else:
                    prices[symbol] = None
                    errors.append(f"{symbol}: Invalid price {price}")
            else:
                prices[symbol] = None
                errors.append(f"{symbol}: Missing from CoinGecko response")
        
        return {
            'prices': prices,
            'errors': errors,
            'success_count': len([p for p in prices.values() if p is not None]),
            'source': 'CoinGecko'
        }
        
    except Exception as e:
        raise Exception(f"CoinGecko API failed: {str(e)}")

# Test function for the multi-exchange system
def test_all_exchanges():
    """Test all available exchanges and return detailed results"""
    print("🔍 Testing all exchange APIs...")
    
    results = {}
    
    # Test each exchange individually
    exchanges = [
        ('Binance', try_binance),
        ('KuCoin', try_kucoin), 
        ('Coinbase', try_coinbase),
        ('CoinGecko', try_coingecko)
    ]
    
    for exchange_name, exchange_func in exchanges:
        print(f"\n--- Testing {exchange_name} ---")
        try:
            result = exchange_func()
            results[exchange_name] = result
            print(f"✅ {exchange_name}: {result['success_count']}/4 prices successful")
        except Exception as e:
            results[exchange_name] = {'error': str(e)}
            print(f"❌ {exchange_name}: {str(e)}")
    
    # Test the multi-exchange fallback
    print(f"\n--- Testing Multi-Exchange Fallback ---")
    try:
        multi_result = get_multi_exchange_prices()
        results['Multi-Exchange'] = multi_result
        print(f"✅ Multi-Exchange: {multi_result['success_count']}/4 prices successful")
        print(f"Sources used: {', '.join(multi_result['sources_used'])}")
    except Exception as e:
        results['Multi-Exchange'] = {'error': str(e)}
        print(f"❌ Multi-Exchange: {str(e)}")
    
    return results
