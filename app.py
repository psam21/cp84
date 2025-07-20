"""
Minimal Portfolio Value Calculator - Modular Version
All utilities imported from modular structure.
"""
import streamlit as st

# Import modular components
from utils.logging import debug_log
from utils.rate_limiter import RateLimiter
from utils.portfolio_calculator import process_complete_portfolio
from pages.portfolio_ui import (
    initialize_portfolio_session,
    get_portfolio_css,
    display_portfolio_summary_boxes,
    display_portfolio_input_cards
)
from pages.exchange_rates_ui import (
    get_usdt_inr_rate,
    get_usd_eur_rate,
    get_usd_aed_rate
)
from pages.api_status_ui import display_rate_limit_status
from pages.price_control_ui import handle_price_loading

# Global rate limiter instance
rate_limiter = RateLimiter()

def main():
    # Streamlit page configuration
    st.set_page_config(page_title="Portfolio Value Calculator", page_icon="💼", layout="wide", initial_sidebar_state="collapsed")

    # Initialize portfolio session state
    initialize_portfolio_session()
    
    # Add custom CSS
    st.markdown(get_portfolio_css(), unsafe_allow_html=True)

    debug_log(f"📱 Page config set: Portfolio Value Calculator", "INFO", "app_config")

    # Get cryptocurrency prices
    binance_prices = handle_price_loading()

    # Main Portfolio Interface
    st.header("💼 Portfolio Value Calculator")
    
    # Display rate limiting status in sidebar
    display_rate_limit_status(rate_limiter)
    
    # Display portfolio input cards and get updated amounts
    portfolio_amounts = display_portfolio_input_cards(binance_prices)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Process complete portfolio calculation and display
    exchange_rate_functions = {'usdt_inr': get_usdt_inr_rate, 'usd_eur': get_usd_eur_rate, 'usd_aed': get_usd_aed_rate}
    portfolio_result = process_complete_portfolio(portfolio_amounts, binance_prices, exchange_rate_functions)
    
    if portfolio_result['success']:
        # Handle failed APIs
        if portfolio_result['failed_apis']:
            st.error(f"❌ Portfolio calculation incomplete: {', '.join(portfolio_result['failed_apis'])} price APIs failed")
            st.info("💡 Values shown are partial calculations. Use 'Force Refresh Prices' button above to retry failed APIs.")
        
        # Display portfolio summary using processed data
        display_portfolio_summary_boxes(
            portfolio_result['portfolio_values']['total_value'], portfolio_result['valid_values'],
            portfolio_result['exchange_rates'], portfolio_result['crypto_equivalents'],
            binance_prices, portfolio_result['portfolio_amounts_with_values']
        )
    else:
        st.error(f"❌ Error calculating portfolio values: {portfolio_result['error']}")
        st.info("🔄 Please try refreshing prices or check API connectivity.")
    
    # Portfolio management buttons with price controls (hidden from users)
    # display_portfolio_management_buttons(binance_prices)

if __name__ == "__main__":
    main()
