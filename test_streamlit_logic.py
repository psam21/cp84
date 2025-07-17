#!/usr/bin/env python3
"""Test script to simulate the exact Streamlit app logic"""

from binance_data import get_binance_price

def test_streamlit_price_logic():
    """Simulate the exact loop from cached_get_binance_prices()"""
    symbols = [("BTC", "BTCUSDT"), ("ETH", "ETHUSDT"), ("BNB", "BNBUSDT"), ("POL", "POLUSDT")]
    prices = {}
    errors = []
    
    for symbol, pair in symbols:
        try:
            price = get_binance_price(pair)
            print(f"Raw price for {symbol}: {price} (type: {type(price)})")
            
            # This is the exact condition from the Streamlit app
            if price and price > 0:
                prices[symbol] = price
                print(f"✅ {symbol}: ${price:,.2f}")
            else:
                error_msg = f"❌ {symbol}: Invalid price returned (got: {price})"
                errors.append(error_msg)
                print(error_msg)
                prices[symbol] = None
        except Exception as e:
            error_msg = f"❌ {symbol}: API call failed - {str(e)}"
            errors.append(error_msg)
            print(error_msg)
            prices[symbol] = None
    
    print()
    print("Final results:")
    print(f"Prices: {prices}")
    print(f"Errors: {errors}")
    print(f"Success count: {len([p for p in prices.values() if p is not None])}")
    
    return {
        'prices': prices,
        'errors': errors,
        'success_count': len([p for p in prices.values() if p is not None]),
        'total_count': len(symbols)
    }

if __name__ == "__main__":
    result = test_streamlit_price_logic()
