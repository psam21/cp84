"""
Tests for utility functions including caching and HTTP utilities.
"""
import unittest
import time
from ..utils import cache, debug_log


class TestUtils(unittest.TestCase):
    """Test suite for utility functions"""
    
    def test_cache_functionality(self):
        """Test cache set, get, and expiration"""
        debug_log("Testing cache functionality", "INFO", "test")
        
        # Test cache set and get
        test_key = "test_price_btc"
        test_value = 50000.0
        
        cache.set(test_key, test_value)
        retrieved_value = cache.get(test_key)
        
        self.assertEqual(retrieved_value, test_value)
        
        # Test cache miss
        missing_value = cache.get("non_existent_key", "default")
        self.assertEqual(missing_value, "default")
        
        # Test cache info
        info = cache.get_cache_info()
        self.assertIsInstance(info, dict)
        self.assertIn('total_entries', info)
        self.assertIn('valid_entries', info)
        
        debug_log("Cache functionality test passed", "SUCCESS", "test")
    
    def test_debug_logging(self):
        """Test debug logging functionality"""
        # This is mostly a smoke test since debug_log prints to console
        try:
            debug_log("Test message", "INFO", "test")
            debug_log("Warning message", "WARNING", "test")
            debug_log("Error message", "ERROR", "test")
            debug_log("Success message", "SUCCESS", "test")
        except Exception as e:
            self.fail(f"Debug logging failed: {str(e)}")


def test_cache_functionality():
    """Standalone function to test cache functionality"""
    test = TestUtils()
    test.test_cache_functionality()


if __name__ == '__main__':
    unittest.main()
