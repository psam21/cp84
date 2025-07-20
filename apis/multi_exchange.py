"""
Multi-exchange API fallback system for cryptocurrency prices.
Tries multiple exchanges in order until successful.
Optimized for Streamlit Community Cloud reliability.
"""
import concurrent.futures
import time
from utils.logging import debug_log
from .binance_api import try_binance
from .kucoin_api import try_kucoin
from .coinbase_api import try_coinbase
from .coingecko_api import try_coingecko

def get_multi_exchange_prices():
    """
    Attempts to fetch prices from multiple exchanges with parallel processing.
    Uses concurrent.futures for faster response times.
    Priority order: Binance -> KuCoin -> Coinbase -> CoinGecko
    Returns the best available price data.
    """
    import sys
    import os
    import concurrent.futures
    import time
    
    start_time = time.time()
    print("� DEBUG: Starting PARALLEL get_multi_exchange_prices() function")
    print(f"🔍 DEBUG: Python executable: {sys.executable}")
    print(f"🔍 DEBUG: Working directory: {os.getcwd()}")
    
    # Add current directory to path for imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
        print(f"✅ DEBUG: Added {current_dir} to sys.path")
    
    results = {
        'prices': {'BTC': None, 'ETH': None, 'BNB': None, 'POL': None},
        'errors': [],
        'success_count': 0,
        'total_count': 4,
        'sources_used': []
    }
    
    # Define exchanges with timeout limits for parallel execution
    exchanges = [
        ('Binance', try_binance),
        ('KuCoin', try_kucoin),
        ('Coinbase', try_coinbase),
        ('CoinGecko', try_coingecko)
    ]
    
    print(f"🔍 DEBUG: Will try {len(exchanges)} exchanges in PARALLEL: {[ex[0] for ex in exchanges]}")
    
    # Execute all exchanges in parallel with timeout
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all futures
        future_to_exchange = {
            executor.submit(exchange_func): exchange_name 
            for exchange_name, exchange_func in exchanges
        }
        
        print("🔄 DEBUG: All exchange requests submitted in parallel")
        
        # Collect results as they complete (with timeout)
        for future in concurrent.futures.as_completed(future_to_exchange, timeout=10):
            exchange_name = future_to_exchange[future]
            
            try:
                print(f"⏱️ DEBUG: {exchange_name} completed")
                exchange_result = future.result(timeout=5)  # 5s timeout per exchange
                
                print(f"📊 DEBUG: {exchange_name} returned: {type(exchange_result)}")
                print(f"📊 DEBUG: {exchange_name} success_count: {exchange_result.get('success_count', 'MISSING')}")
                
                if exchange_result['success_count'] > 0:
                    results['sources_used'].append(exchange_name)
                    print(f"✅ DEBUG: {exchange_name} had {exchange_result['success_count']} successful prices")
                    
                    # Fill in any missing prices
                    for symbol in ['BTC', 'ETH', 'BNB', 'POL']:
                        if (results['prices'][symbol] is None and 
                            exchange_result['prices'].get(symbol) is not None):
                            results['prices'][symbol] = exchange_result['prices'][symbol]
                            print(f"✅ DEBUG: Got {symbol} price from {exchange_name}: {exchange_result['prices'][symbol]}")
                    
                    # Update success count
                    results['success_count'] = len([p for p in results['prices'].values() if p is not None])
                    print(f"📊 DEBUG: Updated total success_count to: {results['success_count']}")
                else:
                    print(f"❌ DEBUG: {exchange_name} had 0 successful prices")
                    
            except concurrent.futures.TimeoutError:
                error_msg = f"❌ {exchange_name} timeout (>5s)"
                results['errors'].append(error_msg)
                print(f"⏰ DEBUG: {error_msg}")
            except Exception as e:
                error_msg = f"❌ {exchange_name} failed: {str(e)}"
                results['errors'].append(error_msg)
                print(f"❌ DEBUG: {error_msg}")
    
    # Add any remaining errors for missing prices
    for symbol in ['BTC', 'ETH', 'BNB', 'POL']:
        if results['prices'][symbol] is None:
            error_msg = f"❌ {symbol}: All exchanges failed"
            results['errors'].append(error_msg)
    
    elapsed_time = round((time.time() - start_time) * 1000, 2)
    print(f"🏁 DEBUG: PARALLEL execution completed in {elapsed_time}ms")
    print(f"🏁 DEBUG: Final results - Success: {results['success_count']}/4, Sources: {results['sources_used']}")
    return results


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
