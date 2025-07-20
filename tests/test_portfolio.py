"""
Tests for portfolio calculation and currency conversion functionality.
"""
import unittest
from ..utils import debug_log


class TestPortfolio(unittest.TestCase):
    """Test suite for portfolio calculations"""
    
    def test_portfolio_calculations(self):
        """Test portfolio value calculations"""
        debug_log("Testing portfolio calculations", "INFO", "test")
        
        # Sample data
        holdings = {
            'BTC': 0.5,
            'ETH': 2.0,
            'BNB': 10.0,
            'POL': 1000.0
        }
        
        prices = {
            'BTC': 50000.0,
            'ETH': 3000.0,
            'BNB': 300.0,
            'POL': 0.5
        }
        
        # Calculate expected total value
        expected_total = (0.5 * 50000) + (2.0 * 3000) + (10.0 * 300) + (1000.0 * 0.5)
        expected_total = 25000 + 6000 + 3000 + 500  # = 34500
        
        # Calculate actual total
        total_value = calculate_portfolio_value(holdings, prices)
        
        self.assertAlmostEqual(total_value, expected_total, places=2)
        
        debug_log(f"Portfolio calculation test passed: {total_value}", "SUCCESS", "test")
    
    def test_currency_conversion(self):
        """Test currency conversion calculations"""
        debug_log("Testing currency conversion", "INFO", "test")
        
        # Test simple USD to INR conversion
        usd_amount = 100.0
        usd_to_inr_rate = 83.0
        
        converted = convert_currency_simple(usd_amount, "USD", "INR", usd_to_inr_rate)
        expected_inr = usd_amount * usd_to_inr_rate
        
        self.assertAlmostEqual(converted, expected_inr, places=2)
        
        # Test same currency conversion
        same_currency = convert_currency_simple(100.0, "USD", "USD", 1.0)
        self.assertEqual(same_currency, 100.0)
        
        debug_log("Currency conversion test passed", "SUCCESS", "test")


def calculate_portfolio_value(holdings, prices):
    """
    Calculate total portfolio value
    
    Args:
        holdings (dict): Holdings dictionary
        prices (dict): Prices dictionary
        
    Returns:
        float: Total portfolio value
    """
    total = 0.0
    
    for symbol, holding in holdings.items():
        price = prices.get(symbol, 0)
        if price > 0 and holding > 0:
            total += holding * price
    
    return total


def convert_currency_simple(amount, from_currency, to_currency, exchange_rate):
    """
    Simple currency conversion
    
    Args:
        amount (float): Amount to convert
        from_currency (str): Source currency
        to_currency (str): Target currency
        exchange_rate (float): Exchange rate
        
    Returns:
        float: Converted amount
    """
    if from_currency == to_currency:
        return amount
    
    return amount * exchange_rate


def test_portfolio_calculations():
    """Standalone function to test portfolio calculations"""
    test = TestPortfolio()
    test.test_portfolio_calculations()


def test_currency_conversion():
    """Standalone function to test currency conversion"""
    test = TestPortfolio()
    test.test_currency_conversion()


if __name__ == '__main__':
    unittest.main()
