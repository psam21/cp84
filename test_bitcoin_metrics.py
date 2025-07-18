#!/usr/bin/env python3
"""Test Bitcoin Metrics with enhanced logging"""

from bitcoin_metrics import BitcoinMetrics
import time

def test_debug_log(msg, level='INFO', context=None):
    """Simple debug logger for testing"""
    timestamp = time.strftime("%H:%M:%S")
    print(f'[{timestamp}] {level}: {msg}')
    if context:
        print(f'    Context: {context}')

def test_bitcoin_metrics():
    """Test Bitcoin Metrics with logging"""
    print("🚀 Testing Bitcoin Metrics with enhanced logging...")
    
    # Create instance with debug logging
    btc = BitcoinMetrics(debug_logger=test_debug_log)
    print("✅ BitcoinMetrics instance created\n")
    
    # Test individual API calls
    print("🏦 Testing CoinDesk API...")
    coindesk_result = btc.get_price_coindesk()
    print(f"Result: {coindesk_result}\n")
    
    print("🔗 Testing Blockchain.info simple call...")
    difficulty = btc.get_blockchain_info_simple('getdifficulty')
    print(f"Difficulty: {difficulty}\n")
    
    print("📊 Testing Blockchain.info chart call...")
    chart = btc.get_blockchain_chart('n-active-addresses', '7days')
    print(f"Chart result: {'SUCCESS' if chart else 'FAILED'}\n")
    
    return True

if __name__ == "__main__":
    test_bitcoin_metrics()
