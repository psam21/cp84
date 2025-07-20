"""
API tests for cryptocurrency exchanges and rate limiting.
"""
import unittest
import time
from ..apis import get_multi_exchange_prices
from ..utils import rate_limiter, debug_log


class TestAPIs(unittest.TestCase):
    """Test suite for API functionality"""
    
    def test_api_connectivity(self):
        """Test basic API connectivity for all exchanges"""
        debug_log("Testing API connectivity", "INFO", "test")
        
        try:
            result = get_multi_exchange_prices()
            
            # Check that we got a valid response structure
            self.assertIsInstance(result, dict)
            self.assertIn('prices', result)
            self.assertIn('success_count', result)
            self.assertIn('sources_used', result)
            
            # Check that at least one API is working
            self.assertGreater(result['success_count'], 0, "No APIs are working")
            
            debug_log(f"API connectivity test passed: {result['success_count']}/4 APIs working", 
                     "SUCCESS", "test")
            
        except Exception as e:
            self.fail(f"API connectivity test failed: {str(e)}")
    
    def test_exchange_apis(self):
        """Test individual exchange APIs"""
        from ..apis.binance_api import try_binance
        from ..apis.kucoin_api import try_kucoin
        from ..apis.coinbase_api import try_coinbase
        from ..apis.coingecko_api import try_coingecko
        
        exchanges = [
            ('Binance', try_binance),
            ('KuCoin', try_kucoin),
            ('Coinbase', try_coinbase),
            ('CoinGecko', try_coingecko)
        ]
        
        working_exchanges = 0
        
        for exchange_name, exchange_func in exchanges:
            try:
                result = exchange_func()
                
                # Check response structure
                self.assertIsInstance(result, dict)
                self.assertIn('prices', result)
                self.assertIn('success_count', result)
                self.assertIn('source', result)
                
                if result['success_count'] > 0:
                    working_exchanges += 1
                    debug_log(f"{exchange_name} API test passed", "SUCCESS", "test")
                else:
                    debug_log(f"{exchange_name} API returned no prices", "WARNING", "test")
                    
            except Exception as e:
                debug_log(f"{exchange_name} API test failed: {str(e)}", "ERROR", "test")
        
        # At least one exchange should be working
        self.assertGreater(working_exchanges, 0, "No exchange APIs are working")
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        debug_log("Testing rate limiting", "INFO", "test")
        
        # Test rate limiter with a test service
        test_service = "test_service"
        
        # Should be able to make first request
        self.assertTrue(rate_limiter.can_make_request(test_service))
        
        # Record the request
        rate_limiter.record_request(test_service)
        
        # Should still be able to make more requests (within limit)
        self.assertTrue(rate_limiter.can_make_request(test_service))
        
        # Test backoff delay
        delay = rate_limiter.get_backoff_delay(test_service, 0)
        self.assertIsInstance(delay, (int, float))
        self.assertGreater(delay, 0)
        
        debug_log("Rate limiting test passed", "SUCCESS", "test")


def test_api_connectivity():
    """Standalone function to test API connectivity"""
    test = TestAPIs()
    test.test_api_connectivity()


def test_exchange_apis():
    """Standalone function to test individual exchange APIs"""
    test = TestAPIs()
    test.test_exchange_apis()


def test_rate_limiting():
    """Standalone function to test rate limiting"""
    test = TestAPIs()
    test.test_rate_limiting()


if __name__ == '__main__':
    unittest.main()
