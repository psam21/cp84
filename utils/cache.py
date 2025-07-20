"""
Cache utilities for storing and retrieving cached data.
"""
import time
import streamlit as st
from datetime import datetime, timedelta

try:
    from .logging import debug_log
    from apis.multi_exchange import get_multi_exchange_prices
except ImportError:
    # Fallback for direct execution
    from logging import debug_log
    try:
        from apis.multi_exchange import get_multi_exchange_prices
    except ImportError:
        def get_multi_exchange_prices():
            return {'prices': {}, 'success_count': 0, 'total_count': 0}

class SimpleCache:
    """
    Simple in-memory cache with TTL (time-to-live) support
    """
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key, default=None):
        """Get cached value if it exists and hasn't expired"""
        if key not in self._cache:
            return default
            
        # Check if expired (default 5 minutes TTL for crypto prices)
        cache_time = self._timestamps.get(key, 0)
        if time.time() - cache_time > 300:  # 5 minutes
            debug_log(f"Cache expired for key: {key}", "INFO", "cache")
            self._cache.pop(key, None)
            self._timestamps.pop(key, None)
            return default
            
        debug_log(f"Cache hit for key: {key}", "INFO", "cache")
        return self._cache[key]
    
    def set(self, key, value):
        """Set cached value with current timestamp"""
        self._cache[key] = value
        self._timestamps[key] = time.time()
        debug_log(f"Cache set for key: {key}", "INFO", "cache")
    
    def clear(self):
        """Clear all cached data"""
        self._cache.clear()
        self._timestamps.clear()
        debug_log("Cache cleared", "INFO", "cache")
    
    def get_cache_info(self):
        """Get information about current cache state"""
        current_time = time.time()
        valid_entries = 0
        expired_entries = 0
        
        for key, timestamp in self._timestamps.items():
            if current_time - timestamp > 300:  # 5 minutes
                expired_entries += 1
            else:
                valid_entries += 1
                
        return {
            'total_entries': len(self._cache),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries
        }

# Global cache instance
cache = SimpleCache()


# Streamlit caching functions
@st.cache_data(ttl=60)
def cached_get_crypto_prices():
    """
    Cache cryptocurrency prices with 1-minute TTL.
    
    This function fetches cryptocurrency prices from multiple exchanges
    and caches the results for 60 seconds to reduce API calls and
    improve application performance.
    
    Returns:
        dict: Price data with structure:
            {
                'prices': {'BTC': float, 'ETH': float, 'BNB': float, 'POL': float},
                'errors': list of error messages,
                'success_count': int number of successful API calls,
                'total_count': int total number of attempted API calls,
                'sources_used': list of exchange names used
            }
    """
    debug_log("🚀 Starting cached_get_crypto_prices with multi-exchange fallback", "INFO", "price_fetch_start")
    
    try:
        debug_log("Starting multi-exchange price fetching", "INFO", "multi_exchange_start")
        result = get_multi_exchange_prices()
        
        if result and result.get('success_count', 0) > 0:
            debug_log(f"Multi-exchange success: {result.get('success_count')}/{result.get('total_count')} prices", "SUCCESS", "multi_exchange_success")
            
            prices = result.get('prices', {})
            debug_log(f"✅ Multi-exchange prices obtained: {list(prices.keys())}", "SUCCESS", "price_fetch")
            
            return result
        else:
            debug_log("❌ Multi-exchange system returned no valid prices", "ERROR", "price_fetch")
            return {
                'prices': {'BTC': None, 'ETH': None, 'BNB': None, 'POL': None},
                'errors': ['Multi-exchange system failed'],
                'success_count': 0,
                'total_count': 4,
                'sources_used': []
            }
            
    except Exception as e:
        debug_log(f"❌ Error in cached_get_crypto_prices: {e}", "ERROR", "price_fetch")
        return {
            'prices': {'BTC': None, 'ETH': None, 'BNB': None, 'POL': None},
            'errors': [f'System error: {e}'],
            'success_count': 0,
            'total_count': 4,
            'sources_used': []
        }


def clear_price_cache():
    """
    Clear the cached cryptocurrency prices.
    
    This forces fresh API calls on the next price fetch request.
    Useful when forcing price refresh or when API issues are detected.
    """
    debug_log("🔄 Clearing cryptocurrency price cache", "INFO", "cache_clear")
    try:
        cached_get_crypto_prices.clear()
        debug_log("✅ Price cache cleared successfully", "SUCCESS", "cache_clear")
    except Exception as e:
        debug_log(f"❌ Error clearing price cache: {e}", "ERROR", "cache_clear")


# Global cache instance
cache = SimpleCache()


# Test functionality when run directly
if __name__ == "__main__":
    print("Testing cache module...")
    
    # Test basic cache operations
    cache.set("test_key", "test_value")
    retrieved = cache.get("test_key")
    print(f"✅ Cache set/get test: {retrieved == 'test_value'}")
    
    # Test cache miss
    missing = cache.get("missing_key", "default_value")
    print(f"✅ Cache miss test: {missing == 'default_value'}")
    
    # Test cache info
    info = cache.get_cache_info()
    print(f"✅ Cache info test: {isinstance(info, dict)}")
    print(f"Cache info: {info}")
    
    print("✅ Cache module test completed!")
