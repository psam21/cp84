"""
Portfolio UI components for displaying cryptocurrency portfolio information.
"""
import streamlit as st
from utils.logging import debug_log
from utils.portfolio_calculator import calculate_portfolio_values, get_failed_apis, calculate_crypto_equivalents
from apis.fear_greed_api import get_fear_greed_index
from utils.fear_greed_utils import format_fear_greed_display


def display_portfolio_input_cards(binance_prices):
    """Display the 4-column cryptocurrency input cards with price displays and portfolio values"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Extract individual prices with None checking
    btc_price = binance_prices.get('BTC')
    eth_price = binance_prices.get('ETH')
    bnb_price = binance_prices.get('BNB')
    pol_price = binance_prices.get('POL')
    
    # Calculate portfolio values first for enhanced display
    btc_amount = st.session_state.portfolio['btc']
    eth_amount = st.session_state.portfolio['eth']
    bnb_amount = st.session_state.portfolio['bnb']
    pol_amount = st.session_state.portfolio['pol']
    
    btc_value = btc_amount * btc_price if btc_price and btc_price > 0 else None
    eth_value = eth_amount * eth_price if eth_price and eth_price > 0 else None
    bnb_value = bnb_amount * bnb_price if bnb_price and bnb_price > 0 else None
    pol_value = pol_amount * pol_price if pol_price and pol_price > 0 else None
    
    with col1:
        if btc_price and btc_price > 0:
            price_display = f"${btc_price:,.0f}"
            card_class = "crypto-btc"
            portfolio_value = f"${btc_value:,.2f}" if btc_value else "$0.00"
        else:
            price_display = "API Failed"
            card_class = "crypto-btc fee-high"
            portfolio_value = "N/A"
        
        st.markdown(f"""
        <div class="metric-card {card_class}">
            <h4>₿ Bitcoin (BTC)</h4>
            <h2>{price_display}</h2>
            <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.2);">
                <small>Portfolio Value: <strong>{portfolio_value}</strong></small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        btc_amount = st.number_input("BTC Holdings", 
                                   value=st.session_state.portfolio['btc'], 
                                   step=0.01, format="%.8f", key="btc_input",
                                   help="Enter your Bitcoin holdings",
                                   label_visibility="collapsed")
    
    with col2:
        if eth_price and eth_price > 0:
            price_display = f"${eth_price:,.0f}"
            card_class = "crypto-eth"
            portfolio_value = f"${eth_value:,.2f}" if eth_value else "$0.00"
        else:
            price_display = "API Failed"
            card_class = "crypto-eth fee-high"
            portfolio_value = "N/A"
            
        st.markdown(f"""
        <div class="metric-card {card_class}">
            <h4>⟠ Ethereum (ETH)</h4>
            <h2>{price_display}</h2>
            <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.2);">
                <small>Portfolio Value: <strong>{portfolio_value}</strong></small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        eth_amount = st.number_input("ETH Holdings", 
                                   value=st.session_state.portfolio['eth'], 
                                   step=0.1, format="%.4f", key="eth_input",
                                   help="Enter your Ethereum holdings",
                                   label_visibility="collapsed")
    
    with col3:
        if bnb_price and bnb_price > 0:
            price_display = f"${bnb_price:,.0f}"
            card_class = "crypto-bnb"
            portfolio_value = f"${bnb_value:,.2f}" if bnb_value else "$0.00"
        else:
            price_display = "API Failed"
            card_class = "crypto-bnb fee-high"
            portfolio_value = "N/A"
            
        st.markdown(f"""
        <div class="metric-card {card_class}">
            <h4>🔸 Binance Coin (BNB)</h4>
            <h2>{price_display}</h2>
            <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.2);">
                <small>Portfolio Value: <strong>{portfolio_value}</strong></small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        bnb_amount = st.number_input("BNB Holdings", 
                                   value=st.session_state.portfolio['bnb'], 
                                   step=0.1, format="%.4f", key="bnb_input",
                                   help="Enter your BNB holdings",
                                   label_visibility="collapsed")
    
    with col4:
        if pol_price and pol_price > 0:
            price_display = f"${pol_price:,.4f}"
            card_class = "crypto-pol"
            portfolio_value = f"${pol_value:,.2f}" if pol_value else "$0.00"
        else:
            price_display = "API Failed"
            card_class = "crypto-pol fee-high"
            portfolio_value = "N/A"
            
        st.markdown(f"""
        <div class="metric-card {card_class}">
            <h4>🔷 Polygon (POL)</h4>
            <h2>{price_display}</h2>
            <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.2);">
                <small>Portfolio Value: <strong>{portfolio_value}</strong></small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        pol_amount = st.number_input("POL Holdings", 
                                   value=st.session_state.portfolio['pol'], 
                                   step=1.0, format="%.2f", key="pol_input",
                                   help="Enter your Polygon holdings",
                                   label_visibility="collapsed")
    
    # Update session state portfolio
    st.session_state.portfolio['btc'] = btc_amount
    st.session_state.portfolio['eth'] = eth_amount
    st.session_state.portfolio['bnb'] = bnb_amount
    st.session_state.portfolio['pol'] = pol_amount
    
    # Return the updated amounts for further processing
    return {
        'btc': btc_amount,
        'eth': eth_amount,
        'bnb': bnb_amount,
        'pol': pol_amount
    }


def initialize_portfolio_session():
    """Initialize portfolio in session state with default values"""
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = {
            'btc': 0.9997,      # 0.9997 BTC
            'eth': 9.9983,      # 9.9983 ETH
            'bnb': 29.5623,     # 29.5623 BNB
            'pol': 4986.01      # 4986.01 POL
        }


def reset_to_default_portfolio():
    """Reset portfolio to default values"""
    st.session_state.portfolio = {
        'btc': 0.9997,
        'eth': 9.9983,
        'bnb': 29.5623,
        'pol': 4986.01
    }


def clear_portfolio():
    """Clear all portfolio holdings"""
    st.session_state.portfolio = {
        'btc': 0.0,
        'eth': 0.0,
        'bnb': 0.0,
        'pol': 0.0
    }


def get_portfolio_css():
    """Return the CSS styles for portfolio components"""
    return """
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .metric-card h4 {
        margin: 0 0 10px 0;
        text-align: center;
        width: 100%;
    }
    .metric-card h2 {
        margin: 0 0 10px 0;
        text-align: center;
        width: 100%;
    }
    .metric-card p {
        margin: 0 0 10px 0;
        text-align: center;
        width: 100%;
    }
    .metric-card div {
        text-align: center;
        width: 100%;
    }
    .metric-card small {
        text-align: center;
        display: block;
        width: 100%;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    .crypto-btc { background: linear-gradient(135deg, #f7931e 0%, #ff6b35 100%); }
    .crypto-eth { background: linear-gradient(135deg, #627eea 0%, #3c4d84 100%); }
    .crypto-bnb { background: linear-gradient(135deg, #f3ba2f 0%, #e8a317 100%); }
    .crypto-pol { background: linear-gradient(135deg, #8247e5 0%, #5d3fbc 100%); }
    .fee-high { background: linear-gradient(135deg, #ff416c 0%, #ff4757 100%); }
    
    .portfolio-container {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin: 10px 0;
        padding: 12px;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 12px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.1);
    }
    .portfolio-box {
        flex: 0 0 calc(11.11% - 6px);
        width: calc(11.11% - 6px);
        min-width: 110px;
        max-width: 110px;
        height: 120px;
        background: rgba(255,255,255,0.95);
        border-radius: 10px;
        padding: 10px 6px;
        text-align: center;
        box-shadow: 0 3px 8px rgba(0,0,0,0.12);
        transition: transform 0.3s ease;
        margin: 0 2px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .portfolio-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .portfolio-emoji {
        font-size: 20px;
        margin-bottom: 4px;
        display: block;
        text-align: center;
        width: 100%;
    }
    .portfolio-label {
        font-size: 11px;
        color: #555;
        margin: 2px 0;
        font-weight: 600;
        line-height: 1.2;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        text-align: center;
        width: 100%;
    }
    .portfolio-value {
        font-size: 16px;
        font-weight: bold;
        color: #2c3e50;
        margin: 4px 0;
        line-height: 1.2;
        text-align: center;
        width: 100%;
    }
    .portfolio-amount {
        font-size: 10px;
        color: #7f8c8d;
        margin: 0;
        line-height: 1.2;
        text-align: center;
        width: 100%;
    }
    .portfolio-total {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    .portfolio-total .portfolio-label,
    .portfolio-total .portfolio-value,
    .portfolio-total .portfolio-amount {
        color: white;
    }
    @media (max-width: 768px) {
        .portfolio-container {
            gap: 3px;
            padding: 8px;
        }
        .portfolio-box {
            flex: 0 0 calc(25% - 6px);
            width: calc(25% - 6px);
            min-width: 100px;
            max-width: 100px;
            height: 100px;
            padding: 6px 4px;
        }
        .portfolio-value {
            font-size: 11px;
        }
        .portfolio-label {
            font-size: 9px;
        }
        .portfolio-amount {
            font-size: 8px;
        }
    }
    </style>
    """


def display_portfolio_header():
    """Display the main portfolio header with title and description"""
    st.title("🚀 Cryptocurrency Portfolio Calculator")
    st.markdown("""
    Calculate your cryptocurrency portfolio values in multiple currencies with live exchange rates.
    Select your cryptocurrencies and enter your holdings to see real-time values.
    """)


def display_portfolio_grid(crypto_symbols, holdings, prices, selected_currency):
    """
    Display the 9-box portfolio grid with cryptocurrency information
    
    Args:
        crypto_symbols (list): List of cryptocurrency symbols
        holdings (dict): Dictionary of holdings for each symbol
        prices (dict): Dictionary of prices for each symbol
        selected_currency (str): Currently selected display currency
    """
    # Create 3x3 grid for 9 cryptocurrencies
    grid_size = 3
    
    for row in range(grid_size):
        cols = st.columns(grid_size)
        for col in range(grid_size):
            idx = row * grid_size + col
            if idx < len(crypto_symbols):
                symbol = crypto_symbols[idx]
                
                with cols[col]:
                    display_crypto_card(symbol, holdings, prices, selected_currency)


def display_crypto_card(symbol, holdings, prices, selected_currency):
    """
    Display individual cryptocurrency card with holdings and value
    
    Args:
        symbol (str): Cryptocurrency symbol (e.g., 'BTC')
        holdings (dict): Holdings dictionary
        prices (dict): Prices dictionary  
        selected_currency (str): Display currency
    """
    # Get price and calculate value
    price = prices.get(symbol, 0) if prices else 0
    holding = holdings.get(symbol, 0)
    value = price * holding if price and holding else 0
    
    # Display crypto card
    st.markdown(f"**{symbol}**")
    
    # Price display with status indicator
    if price and price > 0:
        st.success(f"${price:,.2f}")
    else:
        st.error("Price unavailable")
    
    # Holdings input
    new_holding = st.number_input(
        f"Holdings",
        value=float(holding),
        min_value=0.0,
        step=0.01,
        key=f"holding_{symbol}",
        label_visibility="collapsed"
    )
    
    # Update holdings if changed
    if new_holding != holding:
        holdings[symbol] = new_holding
        value = price * new_holding if price else 0
    
    # Value display
    if value > 0:
        st.metric(
            label="Value",
            value=f"{selected_currency} {value:,.2f}",
            delta=None
        )
    else:
        st.metric(
            label="Value", 
            value=f"{selected_currency} 0.00"
        )


def display_portfolio_summary(holdings, prices, selected_currency):
    """
    Display portfolio summary with total value and distribution
    
    Args:
        holdings (dict): Holdings dictionary
        prices (dict): Prices dictionary
        selected_currency (str): Display currency
    """
    # Calculate total portfolio value
    total_value = 0
    valid_holdings = 0
    
    for symbol, holding in holdings.items():
        if holding > 0:
            price = prices.get(symbol, 0) if prices else 0
            if price > 0:
                total_value += price * holding
                valid_holdings += 1
    
    # Display summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Portfolio Value",
            value=f"{selected_currency} {total_value:,.2f}"
        )
    
    with col2:
        st.metric(
            label="Active Holdings",
            value=f"{valid_holdings} assets"
        )
    
    with col3:
        working_apis = len([p for p in prices.values() if p and p > 0]) if prices else 0
        st.metric(
            label="API Status",
            value=f"{working_apis}/4 working"
        )


def display_portfolio_distribution(holdings, prices):
    """
    Display portfolio distribution chart
    
    Args:
        holdings (dict): Holdings dictionary
        prices (dict): Prices dictionary
    """
    import pandas as pd
    
    # Calculate portfolio distribution
    distribution_data = []
    
    for symbol, holding in holdings.items():
        if holding > 0:
            price = prices.get(symbol, 0) if prices else 0
            if price > 0:
                value = price * holding
                distribution_data.append({
                    'Symbol': symbol,
                    'Value': value,
                    'Holdings': holding,
                    'Price': price
                })
    
    if distribution_data:
        df = pd.DataFrame(distribution_data)
        df = df.sort_values('Value', ascending=False)
        
        # Display as bar chart
        st.subheader("📊 Portfolio Distribution")
        st.bar_chart(df.set_index('Symbol')['Value'])
        
        # Display as data table
        st.subheader("📋 Holdings Details")
        st.dataframe(
            df[['Symbol', 'Holdings', 'Price', 'Value']].round(4),
            use_container_width=True
        )
    else:
        st.info("Add some holdings to see portfolio distribution")


def display_portfolio_management_buttons(binance_prices=None):
    """Display portfolio management buttons with price controls (Reset to Default, Clear All, Force Refresh, Test APIs, Status)"""
    import streamlit as st
    from utils.cache import clear_price_cache, cached_get_crypto_prices
    from utils.diagnostics import test_api_connectivity
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Create 5 columns for all controls in one row
    # Equal width for all buttons, larger for status
    reset_col, clear_col, refresh_col, test_col, status_col = st.columns([1, 1, 1, 1, 1.6])
    
    with reset_col:
        if st.button("📂 Reset to Default", type="secondary", help="Reset to default portfolio holdings"):
            reset_to_default_portfolio()
            st.success("✅ Reset to default portfolio")
            st.rerun()
    
    with clear_col:
        if st.button("🗑️ Clear All", type="primary", help="Clear all portfolio holdings"):
            clear_portfolio()
            st.success("✅ Cleared all holdings")
            st.rerun()
    
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
        if binance_prices:
            valid_prices = len([p for p in binance_prices.values() if p is not None and p > 0])
            total_prices = len(binance_prices)
            if valid_prices == total_prices:
                st.info(f"🟢 Live Prices: {valid_prices}/{total_prices} APIs working")
            elif valid_prices > 0:
                st.warning(f"🟡 Live Prices: {valid_prices}/{total_prices} APIs working")
            else:
                st.error(f"🔴 Live Prices: {valid_prices}/{total_prices} APIs working")
        else:
            st.info("🔄 Loading price status...")


def generate_portfolio_summary_boxes(
    total_value, 
    valid_values, 
    exchange_rates, 
    crypto_equivalents, 
    binance_prices, 
    portfolio_amounts
):
    """
    Generate HTML for portfolio summary boxes display.
    
    Creates the complete portfolio overview with currency conversions,
    crypto equivalents, and portfolio statistics in a grid layout.
    
    Args:
        total_value (float): Total portfolio value in USD
        valid_values (list): List of valid portfolio values
        exchange_rates (dict): Exchange rate data (usdt_inr, usd_eur, usd_aed)
        crypto_equivalents (dict): Crypto equivalent calculations
        binance_prices (dict): Current crypto prices
        portfolio_amounts (dict): Portfolio amounts (btc_amount, eth_amount, etc.)
    
    Returns:
        str: Complete HTML for portfolio summary boxes
    """
    # Extract exchange rate data
    usdt_inr_data = exchange_rates.get('usdt_inr', {})
    usdt_inr_rate = usdt_inr_data.get('rate', 0)
    usdt_source = usdt_inr_data.get('source', 'Unknown')
    
    usd_eur_data = exchange_rates.get('usd_eur', {})
    usd_eur_rate = usd_eur_data.get('rate', 0)
    
    usd_aed_data = exchange_rates.get('usd_aed', {})
    usd_aed_rate = usd_aed_data.get('rate', 0)
    
    # Extract portfolio amounts
    btc_amount = portfolio_amounts.get('btc', 0)
    eth_amount = portfolio_amounts.get('eth', 0)
    bnb_amount = portfolio_amounts.get('bnb', 0)
    pol_amount = portfolio_amounts.get('pol', 0)
    
    # Extract crypto values for portfolio stats
    btc_value = portfolio_amounts.get('btc_value', 0)
    eth_value = portfolio_amounts.get('eth_value', 0)
    bnb_value = portfolio_amounts.get('bnb_value', 0)
    pol_value = portfolio_amounts.get('pol_value', 0)
    
    portfolio_html = '<div class="portfolio-container">'
    
    # Total value boxes with special styling
    if total_value > 0:
        # USD Total
        portfolio_html += f'''
        <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
            <div class="portfolio-emoji">💵</div>
            <div class="portfolio-label" style="color: #333;">USD Value</div>
            <div class="portfolio-value" style="color: #333;">${total_value:,.2f}</div>
            <div class="portfolio-amount" style="color: #555;">{len(valid_values)}/4 Assets</div>
        </div>'''
        
        # EUR Total
        portfolio_html += f'''
        <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
            <div class="portfolio-emoji">🇪🇺</div>
            <div class="portfolio-label" style="color: #333;">EUR Value</div>
            <div class="portfolio-value" style="color: #333;">€{total_value * usd_eur_rate:,.2f}</div>
            <div class="portfolio-amount" style="color: #555;">@ €{usd_eur_rate:.4f}/USD</div>
        </div>'''
        
        # AED Total
        portfolio_html += f'''
        <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
            <div class="portfolio-emoji">🇦🇪</div>
            <div class="portfolio-label" style="color: #333;">AED Value</div>
            <div class="portfolio-value" style="color: #333;">د.إ{total_value * usd_aed_rate:,.2f}</div>
            <div class="portfolio-amount" style="color: #555;">@ د.إ{usd_aed_rate:.2f}/USD</div>
        </div>'''
        
        # INR Total
        portfolio_html += f'''
        <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
            <div class="portfolio-emoji">🇮🇳</div>
            <div class="portfolio-label" style="color: #333;">INR Value</div>
            <div class="portfolio-value" style="color: #333;">₹{total_value * usdt_inr_rate:,.0f}</div>
            <div class="portfolio-amount" style="color: #555;">@ ₹{usdt_inr_rate}/USD</div>
        </div>'''
        
        # USDT/INR exchange rate box
        portfolio_html += f'''
        <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
            <div class="portfolio-emoji">💱</div>
            <div class="portfolio-label" style="color: #333;">USDT/INR Rate</div>
            <div class="portfolio-value" style="color: #333;">₹{usdt_inr_rate:.2f}</div>
            <div class="portfolio-amount" style="color: #555;">Source: {usdt_source}</div>
        </div>'''
        
        # BTC Equivalent
        btc_equivalent = crypto_equivalents.get('BTC')
        btc_price = binance_prices.get('BTC')
        if btc_equivalent is not None and btc_equivalent > 0:
            portfolio_html += f'''
            <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
                <div class="portfolio-emoji">₿</div>
                <div class="portfolio-label" style="color: #333;">BTC Equivalent</div>
                <div class="portfolio-value" style="color: #333;">₿{btc_equivalent:.8f}</div>
                <div class="portfolio-amount" style="color: #555;">@ ${btc_price:,.0f}/BTC</div>
            </div>'''
        else:
            portfolio_html += '''
            <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
                <div class="portfolio-emoji">₿</div>
                <div class="portfolio-label" style="color: #333;">BTC Equivalent</div>
                <div class="portfolio-value" style="color: #333;">BTC API Failed</div>
                <div class="portfolio-amount" style="color: #555;">Price unavailable</div>
            </div>'''
        
        # ETH Equivalent
        eth_equivalent = crypto_equivalents.get('ETH')
        eth_price = binance_prices.get('ETH')
        if eth_equivalent is not None and eth_equivalent > 0:
            portfolio_html += f'''
            <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
                <div class="portfolio-emoji">⟠</div>
                <div class="portfolio-label" style="color: #333;">ETH Equivalent</div>
                <div class="portfolio-value" style="color: #333;">⟠{eth_equivalent:.4f}</div>
                <div class="portfolio-amount" style="color: #555;">@ ${eth_price:,.0f}/ETH</div>
            </div>'''
        else:
            portfolio_html += '''
            <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
                <div class="portfolio-emoji">⟠</div>
                <div class="portfolio-label" style="color: #333;">ETH Equivalent</div>
                <div class="portfolio-value" style="color: #333;">ETH API Failed</div>
                <div class="portfolio-amount" style="color: #555;">Price unavailable</div>
            </div>'''
        
        # BNB Equivalent
        bnb_equivalent = crypto_equivalents.get('BNB')
        bnb_price = binance_prices.get('BNB')
        if bnb_equivalent is not None and bnb_equivalent > 0:
            portfolio_html += f'''
            <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
                <div class="portfolio-emoji">🔸</div>
                <div class="portfolio-label" style="color: #333;">BNB Equivalent</div>
                <div class="portfolio-value" style="color: #333;">🔸{bnb_equivalent:.2f}</div>
                <div class="portfolio-amount" style="color: #555;">@ ${bnb_price:,.0f}/BNB</div>
            </div>'''
        else:
            portfolio_html += '''
            <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
                <div class="portfolio-emoji">🔸</div>
                <div class="portfolio-label" style="color: #333;">BNB Equivalent</div>
                <div class="portfolio-value" style="color: #333;">BNB API Failed</div>
                <div class="portfolio-amount" style="color: #555;">Price unavailable</div>
            </div>'''
        
        # Fear & Greed Index
        fear_greed_data = get_fear_greed_index()
        fear_greed_display = format_fear_greed_display(fear_greed_data)
        
        # Create progress bar for visual representation
        progress_value = fear_greed_display.get('progress_value', 0)
        progress_color = fear_greed_display.get('progress_color', 'gray')
        progress_width = f"{progress_value}%" if progress_value > 0 else "0%"
        
        portfolio_html += f'''
        <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
            <div class="portfolio-emoji">{fear_greed_display['emoji']}</div>
            <div class="portfolio-label" style="color: #333;">Fear & Greed</div>
            <div class="portfolio-value" style="color: #333;">{fear_greed_display['value']}</div>
            <div class="portfolio-amount" style="color: #555;">{fear_greed_display['subtitle']}</div>
            <div style="margin-top: 5px; width: 100%; background-color: #e0e0e0; border-radius: 6px; height: 6px; overflow: hidden;">
                <div style="width: {progress_width}; background-color: {progress_color}; height: 100%; transition: width 0.3s ease;"></div>
            </div>
        </div>'''
        
        # Asset Distribution/Portfolio Stats
        non_zero_assets = sum(1 for amount in [btc_amount, eth_amount, bnb_amount, pol_amount] if amount > 0)
        largest_asset = "N/A"
        largest_percentage = 0
        
        if total_value > 0:
            asset_values = {
                'BTC': btc_value if btc_value else 0,
                'ETH': eth_value if eth_value else 0,
                'BNB': bnb_value if bnb_value else 0,
                'POL': pol_value if pol_value else 0
            }
            if asset_values:
                largest_asset = max(asset_values, key=lambda k: asset_values[k])
                largest_percentage = (asset_values[largest_asset] / total_value) * 100
        
        portfolio_html += f'''
        <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
            <div class="portfolio-emoji">📊</div>
            <div class="portfolio-label" style="color: #333;">Portfolio Stats</div>
            <div class="portfolio-value" style="color: #333;">{non_zero_assets}/4 Assets</div>
            <div class="portfolio-amount" style="color: #555;">Largest: {largest_asset} ({largest_percentage:.1f}%)</div>
        </div>'''
    else:
        # No valid prices fallback - but Fear & Greed should still work
        # First add the regular failed API boxes
        for emoji, label in [("💵", "USD Value"), ("🇪🇺", "EUR Value"), ("🇦🇪", "AED Value"), ("🇮🇳", "INR Value"), ("💱", "USDT/INR Rate"), ("₿", "BTC Equivalent"), ("⟠", "ETH Equivalent"), ("🔸", "BNB Equivalent")]:
            portfolio_html += f'''
            <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
                <div class="portfolio-emoji">{emoji}</div>
                <div class="portfolio-label" style="color: #333;">{label}</div>
                <div class="portfolio-value" style="color: #333;">No Valid Prices</div>
                <div class="portfolio-amount" style="color: #555;">Check APIs</div>
            </div>'''
        
        # Fear & Greed Index (should work even when crypto prices fail)
        fear_greed_data = get_fear_greed_index()
        fear_greed_display = format_fear_greed_display(fear_greed_data)
        
        progress_value = fear_greed_display.get('progress_value', 0)
        progress_color = fear_greed_display.get('progress_color', 'gray')
        progress_width = f"{progress_value}%" if progress_value > 0 else "0%"
        
        portfolio_html += f'''
        <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
            <div class="portfolio-emoji">{fear_greed_display['emoji']}</div>
            <div class="portfolio-label" style="color: #333;">Fear & Greed</div>
            <div class="portfolio-value" style="color: #333;">{fear_greed_display['value']}</div>
            <div class="portfolio-amount" style="color: #555;">{fear_greed_display['subtitle']}</div>
            <div style="margin-top: 5px; width: 100%; background-color: #e0e0e0; border-radius: 6px; height: 6px; overflow: hidden;">
                <div style="width: {progress_width}; background-color: {progress_color}; height: 100%; transition: width 0.3s ease;"></div>
            </div>
        </div>'''
        
        # Portfolio Stats box
        portfolio_html += f'''
        <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
            <div class="portfolio-emoji">📊</div>
            <div class="portfolio-label" style="color: #333;">Portfolio Stats</div>
            <div class="portfolio-value" style="color: #333;">No Valid Prices</div>
            <div class="portfolio-amount" style="color: #555;">Check APIs</div>
        </div>'''
    
    portfolio_html += '</div>'
    return portfolio_html


def display_portfolio_summary_boxes(
    total_value, 
    valid_values, 
    exchange_rates, 
    crypto_equivalents, 
    binance_prices, 
    portfolio_amounts
):
    """
    Display portfolio summary boxes using the generated HTML.
    
    This is a convenience function that generates and displays
    the portfolio summary boxes in one call.
    """
    portfolio_html = generate_portfolio_summary_boxes(
        total_value, 
        valid_values, 
        exchange_rates, 
        crypto_equivalents, 
        binance_prices, 
        portfolio_amounts
    )
    st.markdown(portfolio_html, unsafe_allow_html=True)
