"""
Price control UI components for managing cryptocurrency price refreshing and API testing.
"""
import streamlit as st
from utils.cache import clear_price_cache, cached_get_crypto_prices
from utils.diagnostics import test_api_connectivity


def display_price_control_bar(binance_prices):
    """Display the price refresh button, API test button, and status indicator"""
    
    # Add price refresh button with transparent status
    refresh_col, test_col, status_col = st.columns([1, 1, 2])
    
    with refresh_col:
        if st.button("🔄 Force Refresh Prices", type="secondary", help="Force fresh API calls"):
            clear_price_cache()
            with st.spinner("Fetching fresh prices from multiple exchanges..."):
                price_result = cached_get_crypto_prices()
                
            sources_used = price_result.get('sources_used', [])
            sources_text = f" via {', '.join(sources_used)}" if sources_used else ""
            
            if price_result['success_count'] == price_result['total_count']:
                st.success(f"✅ All prices refreshed successfully{sources_text}!")
            else:
                st.error(f"❌ Price refresh failed ({price_result['success_count']}/{price_result['total_count']} successful){sources_text}")
                for error in price_result.get('errors', []):
                    st.error(error)
            st.rerun()
    
    with test_col:
        if st.button("🔍 Test APIs", type="secondary", help="Test API connectivity"):
            with st.spinner("Testing API connectivity..."):
                connectivity_results = test_api_connectivity()
            
            st.write("**API Connectivity Test Results:**")
            for api_name, status in connectivity_results.items():
                if "✅" in status:
                    st.success(f"{api_name}: {status}")
                elif "⚠️" in status:
                    st.warning(f"{api_name}: {status}")
                else:
                    st.error(f"{api_name}: {status}")
    
    with status_col:
        # Show current API status
        valid_prices = len([p for p in binance_prices.values() if p is not None and p > 0])
        total_prices = len(binance_prices)
        if valid_prices == total_prices:
            st.info(f"🟢 Live Prices: {valid_prices}/{total_prices} APIs working")
        elif valid_prices > 0:
            st.warning(f"🟡 Live Prices: {valid_prices}/{total_prices} APIs working")
        else:
            st.error(f"🔴 Live Prices: {valid_prices}/{total_prices} APIs working")


def handle_price_loading():
    """Handle the cryptocurrency price loading process"""
    from utils.logging import debug_log
    
    try:
        with st.spinner("🔄 Loading cryptocurrency prices..."):
            price_result = cached_get_crypto_prices()
            binance_prices = price_result['prices']
            
        debug_log(f"✅ Prices loaded successfully: {list(binance_prices.keys())}", "SUCCESS", "price_load")
        
        for symbol, price in binance_prices.items():
            if price and price > 0:
                debug_log(f"💰 {symbol}: ${price:,.2f}", "INFO", "price_display")
            else:
                debug_log(f"❌ {symbol}: Price unavailable", "ERROR", "price_display")
                
        return binance_prices
        
    except Exception as e:
        debug_log(f"❌ Error loading prices: {e}", "ERROR", "price_load")
        return {'BTC': None, 'ETH': None, 'BNB': None, 'POL': None}
