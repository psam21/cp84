"""
Tests for utility functions including caching and HTTP utilities.
"""
import unittest
import time
from ..utils import cache, debug_log
from ..utils.fear_greed_utils import (
    get_sentiment_details, 
    format_fear_greed_display, 
    get_sentiment_interpretation,
    create_progress_bar_html,
    get_market_context
)


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

    def test_fear_greed_sentiment_details(self):
        """Test Fear & Greed sentiment classification"""
        debug_log("Testing Fear & Greed sentiment details", "INFO", "test")
        
        # Test extreme fear (0-24)
        extreme_fear = get_sentiment_details(10)
        self.assertEqual(extreme_fear['description'], 'Extreme Fear')
        self.assertEqual(extreme_fear['emoji'], '😰')
        self.assertEqual(extreme_fear['color'], '#FF4444')
        
        # Test fear (25-49)
        fear = get_sentiment_details(35)
        self.assertEqual(fear['description'], 'Fear')
        self.assertEqual(fear['emoji'], '😨')
        
        # Test neutral (50-74)
        neutral = get_sentiment_details(60)
        self.assertEqual(neutral['description'], 'Neutral')
        self.assertEqual(neutral['emoji'], '😐')
        
        # Test greed (75-89)
        greed = get_sentiment_details(80)
        self.assertEqual(greed['description'], 'Greed')
        self.assertEqual(greed['emoji'], '😊')
        
        # Test extreme greed (90-100)
        extreme_greed = get_sentiment_details(95)
        self.assertEqual(extreme_greed['description'], 'Extreme Greed')
        self.assertEqual(extreme_greed['emoji'], '🤑')
        
        debug_log("Fear & Greed sentiment details test passed", "SUCCESS", "test")

    def test_fear_greed_display_formatting(self):
        """Test Fear & Greed display formatting"""
        debug_log("Testing Fear & Greed display formatting", "INFO", "test")
        
        # Test with valid data
        test_data = {
            'value': 72,
            'value_classification': 'Greed',
            'timestamp': '1642781234'
        }
        
        display = format_fear_greed_display(test_data)
        
        self.assertIsInstance(display, dict)
        self.assertIn('title', display)
        self.assertIn('value', display)
        self.assertIn('subtitle', display)
        self.assertIn('emoji', display)
        self.assertIn('progress_value', display)
        
        # Check that the value is formatted correctly
        self.assertEqual(display['value'], '72')
        self.assertEqual(display['progress_value'], 72)
        
        # Test with None (API failure)
        display_none = format_fear_greed_display(None)
        self.assertEqual(display_none['value'], 'API Failed')
        self.assertEqual(display_none['emoji'], '❌')
        
        debug_log("Fear & Greed display formatting test passed", "SUCCESS", "test")

    def test_fear_greed_progress_bar(self):
        """Test Fear & Greed progress bar HTML generation"""
        debug_log("Testing Fear & Greed progress bar HTML", "INFO", "test")
        
        # Test progress bar creation
        html = create_progress_bar_html(75, 'green', '100%')
        
        self.assertIsInstance(html, str)
        self.assertIn('75%', html)  # Progress width
        self.assertIn('green', html)  # Color
        self.assertIn('100%', html)  # Container width
        
        debug_log("Fear & Greed progress bar test passed", "SUCCESS", "test")

    def test_fear_greed_market_context(self):
        """Test Fear & Greed market context and advice"""
        debug_log("Testing Fear & Greed market context", "INFO", "test")
        
        # Test different value ranges
        test_cases = [
            (10, 'Extreme Fear Zone', 'Accumulate'),
            (35, 'Fear Zone', 'Buy Dips'),
            (60, 'Neutral Zone', 'Hold/Monitor'),
            (80, 'Greed Zone', 'Reduce Position'),
            (95, 'Extreme Greed Zone', 'Take Profits')
        ]
        
        for value, expected_context, expected_action in test_cases:
            context = get_market_context(value)
            
            self.assertIsInstance(context, dict)
            self.assertIn('context', context)
            self.assertIn('advice', context)
            self.assertIn('action', context)
            
            self.assertEqual(context['context'], expected_context)
            self.assertEqual(context['action'], expected_action)
        
        debug_log("Fear & Greed market context test passed", "SUCCESS", "test")


def test_cache_functionality():
    """Standalone function to test cache functionality"""
    test = TestUtils()
    test.test_cache_functionality()


def test_fear_greed_sentiment():
    """Standalone function to test Fear & Greed sentiment details"""
    test = TestUtils()
    test.test_fear_greed_sentiment_details()


def test_fear_greed_display():
    """Standalone function to test Fear & Greed display formatting"""
    test = TestUtils()
    test.test_fear_greed_display_formatting()


def test_fear_greed_progress():
    """Standalone function to test Fear & Greed progress bar"""
    test = TestUtils()
    test.test_fear_greed_progress_bar()


def test_fear_greed_context():
    """Standalone function to test Fear & Greed market context"""
    test = TestUtils()
    test.test_fear_greed_market_context()


if __name__ == '__main__':
    unittest.main()
