"""
Simplified Portfolio Value Calculator
Retains only the portfolio functionality from the original app.
"""
import streamlit as st
import time
from datetime import datetime

# Debug logging functions
def debug_log(message, level="INFO", context=None, data=None):
    """Enhanced debug logging with full session instrumentation"""
    if 'debug_logs' not in st.session_state:
        st.session_state.debug_logs = []
        session_start = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            'level': 'SYSTEM',
            'message': '🚀 Debug session initialized',
            'context': 'session_start',
            'session_id': id(st.session_state),
            'timestamp_full': datetime.now().isoformat(),
            'log_sequence': 1
        }
        st.session_state.debug_logs.append(session_start)
    
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    timestamp_full = datetime.now().isoformat()
    
    log_entry = {
        'timestamp': timestamp,
        'timestamp_full': timestamp_full,
        'level': level,
        'message': str(message),
        'context': context,
        'session_id': id(st.session_state),
        'log_sequence': len(st.session_state.debug_logs) + 1
    }
    
    if data is not None:
        log_entry['data'] = data
    
    st.session_state.debug_logs.append(log_entry)
    
    if level == "ERROR":
        print(f"❌ [{timestamp}] ERROR: {message}")
    elif level == "SUCCESS":
        print(f"✅ [{timestamp}] SUCCESS: {message}")
    else:
        print(f"ℹ️ [{timestamp}] {level}: {message}")

def debug_log_api_call(exchange_name, endpoint, status, response_time=None, data=None):
    """Log API call details with standardized format"""
    context = f"api_call_{exchange_name.lower().replace(' ', '_')}"
    
    if status == "STARTING":
        message = f"🚀 {exchange_name} API call starting: {endpoint}"
    elif status == "SUCCESS":
        time_msg = f" ({response_time:.2f}s)" if response_time else ""
        message = f"✅ {exchange_name} API call successful{time_msg}: {endpoint}"
    elif status == "ERROR":
        time_msg = f" ({response_time:.2f}s)" if response_time else ""
        message = f"❌ {exchange_name} API call failed{time_msg}: {endpoint}"
    else:
        message = f"ℹ️ {exchange_name} API call {status}: {endpoint}"
    
    debug_log(message, status, context, data)

def debug_log_user_action(action, data=None):
    """Log user interaction with enhanced data capture"""
    debug_log(f"👤 User action: {action}", "USER", "user_interaction", data)

# USDT/INR rate fetching
@st.cache_data(ttl=300)  # 5-minute cache for exchange rates
def get_usdt_inr_rate():
    """Get USDT/INR exchange rate from multiple sources"""
    import requests
    
    # Try multiple sources for USDT/INR rate
    sources = [
        {
            'name': 'CoinGecko',
            'url': 'https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=inr',
            'parser': lambda data: data.get('tether', {}).get('inr')
        },
        {
            'name': 'Binance',
            'url': 'https://api.binance.com/api/v3/ticker/price?symbol=USDTINR',
            'parser': lambda data: float(data.get('price', 0)) if data.get('price') else None
        }
    ]
    
    for source in sources:
        try:
            debug_log(f"🔄 Fetching USDT/INR rate from {source['name']}", "INFO", "usdt_inr_fetch")
            response = requests.get(source['url'], timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                rate = source['parser'](data)
                
                if rate and rate > 0:
                    debug_log(f"✅ {source['name']} USDT/INR rate: ₹{rate:.2f}", "SUCCESS", "usdt_inr_success")
                    return {
                        'rate': rate,
                        'source': source['name'],
                        'success': True
                    }
            
            debug_log(f"❌ {source['name']} USDT/INR failed: HTTP {response.status_code}", "ERROR", "usdt_inr_error")
            
        except Exception as e:
            debug_log(f"❌ {source['name']} USDT/INR error: {e}", "ERROR", "usdt_inr_error")
    
    # Fallback to hardcoded rate
    debug_log("⚠️ Using fallback USDT/INR rate: ₹83.50", "WARNING", "usdt_inr_fallback")
    return {
        'rate': 83.50,
        'source': 'Fallback',
        'success': False
    }

# USD/EUR rate fetching
@st.cache_data(ttl=300)  # 5-minute cache for exchange rates
def get_usd_eur_rate():
    """Get USD/EUR exchange rate from multiple sources"""
    import requests
    
    # Try multiple sources for USD/EUR rate
    sources = [
        {
            'name': 'CoinGecko',
            'url': 'https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=eur',
            'parser': lambda data: data.get('tether', {}).get('eur')
        },
        {
            'name': 'Binance',
            'url': 'https://api.binance.com/api/v3/ticker/price?symbol=EURUSDT',
            'parser': lambda data: 1 / float(data.get('price', 1)) if data.get('price') and float(data.get('price', 1)) > 0 else None
        }
    ]
    
    for source in sources:
        try:
            debug_log(f"🔄 Fetching USD/EUR rate from {source['name']}", "INFO", "usd_eur_fetch")
            response = requests.get(source['url'], timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                rate = source['parser'](data)
                
                if rate and rate > 0:
                    debug_log(f"✅ {source['name']} USD/EUR rate: €{rate:.4f}", "SUCCESS", "usd_eur_success")
                    return {
                        'rate': rate,
                        'source': source['name'],
                        'success': True
                    }
            
            debug_log(f"❌ {source['name']} USD/EUR failed: HTTP {response.status_code}", "ERROR", "usd_eur_error")
            
        except Exception as e:
            debug_log(f"❌ {source['name']} USD/EUR error: {e}", "ERROR", "usd_eur_error")
    
    # Fallback to hardcoded rate
    debug_log("⚠️ Using fallback USD/EUR rate: €0.92", "WARNING", "usd_eur_fallback")
    return {
        'rate': 0.92,
        'source': 'Fallback',
        'success': False
    }

# USD/AED rate fetching
@st.cache_data(ttl=300)  # 5-minute cache for exchange rates
def get_usd_aed_rate():
    """Get USD/AED exchange rate from multiple sources"""
    import requests
    
    # Try multiple sources for USD/AED rate
    sources = [
        {
            'name': 'CoinGecko',
            'url': 'https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=aed',
            'parser': lambda data: data.get('tether', {}).get('aed')
        },
        {
            'name': 'Binance',
            'url': 'https://api.binance.com/api/v3/ticker/price?symbol=AEDUSDT',
            'parser': lambda data: 1 / float(data.get('price', 1)) if data.get('price') and float(data.get('price', 1)) > 0 else None
        }
    ]
    
    for source in sources:
        try:
            debug_log(f"🔄 Fetching USD/AED rate from {source['name']}", "INFO", "usd_aed_fetch")
            response = requests.get(source['url'], timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                rate = source['parser'](data)
                
                if rate and rate > 0:
                    debug_log(f"✅ {source['name']} USD/AED rate: د.إ{rate:.2f}", "SUCCESS", "usd_aed_success")
                    return {
                        'rate': rate,
                        'source': source['name'],
                        'success': True
                    }
            
            debug_log(f"❌ {source['name']} USD/AED failed: HTTP {response.status_code}", "ERROR", "usd_aed_error")
            
        except Exception as e:
            debug_log(f"❌ {source['name']} USD/AED error: {e}", "ERROR", "usd_aed_error")
    
    # Fallback to hardcoded rate
    debug_log("⚠️ Using fallback USD/AED rate: د.إ3.67", "WARNING", "usd_aed_fallback")
    return {
        'rate': 3.67,
        'source': 'Fallback',
        'success': False
    }

# Multi-exchange price fetching
@st.cache_data(ttl=60)
def cached_get_crypto_prices():
    """Cache cryptocurrency prices with 1-minute TTL"""
    debug_log("🚀 Starting cached_get_crypto_prices with multi-exchange fallback", "INFO", "price_fetch_start")
    
    try:
        from multi_exchange import get_multi_exchange_prices
        debug_log("Successfully imported multi_exchange module", "SUCCESS", "module_import")
        
        debug_log_api_call("Multi-Exchange", "get_multi_exchange_prices()", "STARTING")
        result = get_multi_exchange_prices()
        
        processing_time = time.time() - time.time()  # Placeholder for actual timing
        
        if result and result.get('success_count', 0) > 0:
            debug_log_api_call("Multi-Exchange", "get_multi_exchange_prices()", "SUCCESS", processing_time, 
                             {'success_count': result.get('success_count'), 
                              'total_count': result.get('total_count'),
                              'sources_used': result.get('sources_used', [])})
            
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
            
    except ImportError as e:
        debug_log(f"❌ Could not import multi_exchange: {e}", "ERROR", "module_import")
        return {
            'prices': {'BTC': None, 'ETH': None, 'BNB': None, 'POL': None},
            'errors': [f'Import error: {e}'],
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

# Legacy function for compatibility
@st.cache_data(ttl=60)
def cached_get_binance_prices():
    """Legacy function - redirects to multi-exchange system"""
    return cached_get_crypto_prices()

# Portfolio management functions
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

def main():
    # Streamlit page configuration
    st.set_page_config(
        page_title="Portfolio Value Calculator",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Initialize portfolio session state
    initialize_portfolio_session()
    
    # Add custom CSS for portfolio cards
    st.markdown("""
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
    }
    .portfolio-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .portfolio-emoji {
        font-size: 20px;
        margin-bottom: 4px;
        display: block;
    }
    .portfolio-label {
        font-size: 11px;
        color: #555;
        margin: 2px 0;
        font-weight: 600;
        line-height: 1.2;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .portfolio-value {
        font-size: 16px;
        font-weight: bold;
        color: #2c3e50;
        margin: 4px 0;
        line-height: 1.2;
    }
    .portfolio-amount {
        font-size: 10px;
        color: #7f8c8d;
        margin: 0;
        line-height: 1.2;
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
    """, unsafe_allow_html=True)

    debug_log(f"📱 Page config set: Portfolio Value Calculator", "INFO", "app_config")

    # Get cryptocurrency prices
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
    except Exception as e:
        debug_log(f"❌ Error loading prices: {e}", "ERROR", "price_load")
        binance_prices = {'BTC': None, 'ETH': None, 'BNB': None, 'POL': None}

    # Main Portfolio Interface
    st.header("💼 Portfolio Value Calculator")
    
    # Initialize portfolio in session state
    initialize_portfolio_session()
    
    # Add price refresh button with transparent status
    refresh_col, status_col = st.columns([1, 3])
    with refresh_col:
        if st.button("🔄 Force Refresh Prices", type="secondary", help="Force fresh API calls"):
            cached_get_crypto_prices.clear()
            cached_get_binance_prices.clear()
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
            <p>{'Current Price' if btc_price and btc_price > 0 else 'Price Unavailable'}</p>
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
            <p>{'Current Price' if eth_price and eth_price > 0 else 'Price Unavailable'}</p>
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
            <p>{'Current Price' if bnb_price and bnb_price > 0 else 'Price Unavailable'}</p>
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
            <p>{'Current Price' if pol_price and pol_price > 0 else 'Price Unavailable'}</p>
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
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    try:
        # Calculate values with transparent API status checking
        btc_value = btc_amount * btc_price if btc_price and btc_price > 0 else None
        eth_value = eth_amount * eth_price if eth_price and eth_price > 0 else None
        bnb_value = bnb_amount * bnb_price if bnb_price and bnb_price > 0 else None
        pol_value = pol_amount * pol_price if pol_price and pol_price > 0 else None
        
        # Calculate total only from available values
        valid_values = [v for v in [btc_value, eth_value, bnb_value, pol_value] if v is not None]
        total_value = sum(valid_values) if valid_values else 0
        
        # Show detailed API status for calculations
        failed_apis = []
        if btc_price is None or btc_price <= 0: failed_apis.append("BTC")
        if eth_price is None or eth_price <= 0: failed_apis.append("ETH") 
        if bnb_price is None or bnb_price <= 0: failed_apis.append("BNB")
        if pol_price is None or pol_price <= 0: failed_apis.append("POL")
        
        if failed_apis:
            st.error(f"❌ Portfolio calculation incomplete: {', '.join(failed_apis)} price APIs failed")
            st.info("💡 Values shown are partial calculations. Use 'Force Refresh Prices' button above to retry failed APIs.")
        
        # Get live exchange rates
        usdt_inr_data = get_usdt_inr_rate()
        usdt_inr_rate = usdt_inr_data['rate']
        usdt_source = usdt_inr_data['source']
        
        usd_eur_data = get_usd_eur_rate()
        usd_eur_rate = usd_eur_data['rate']
        eur_source = usd_eur_data['source']
        
        usd_aed_data = get_usd_aed_rate()
        usd_aed_rate = usd_aed_data['rate']
        aed_source = usd_aed_data['source']
        
        # Create portfolio summary boxes
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
            
            # USDT/INR exchange rate box (moved next to INR value)
            portfolio_html += f'''
            <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
                <div class="portfolio-emoji">💱</div>
                <div class="portfolio-label" style="color: #333;">USDT/INR Rate</div>
                <div class="portfolio-value" style="color: #333;">₹{usdt_inr_rate:.2f}</div>
                <div class="portfolio-amount" style="color: #555;">Source: {usdt_source}</div>
            </div>'''
            
            # BTC Equivalent
            if btc_price and btc_price > 0:
                portfolio_html += f'''
                <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
                    <div class="portfolio-emoji">₿</div>
                    <div class="portfolio-label" style="color: #333;">BTC Equivalent</div>
                    <div class="portfolio-value" style="color: #333;">₿{total_value / btc_price:.8f}</div>
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
            if eth_price and eth_price > 0:
                portfolio_html += f'''
                <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
                    <div class="portfolio-emoji">⟠</div>
                    <div class="portfolio-label" style="color: #333;">ETH Equivalent</div>
                    <div class="portfolio-value" style="color: #333;">⟠{total_value / eth_price:.4f}</div>
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
            if bnb_price and bnb_price > 0:
                portfolio_html += f'''
                <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
                    <div class="portfolio-emoji">🔸</div>
                    <div class="portfolio-label" style="color: #333;">BNB Equivalent</div>
                    <div class="portfolio-value" style="color: #333;">🔸{total_value / bnb_price:.2f}</div>
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
            
            # Asset Distribution
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
                largest_asset = max(asset_values, key=asset_values.get)
                largest_percentage = (asset_values[largest_asset] / total_value) * 100
            
            portfolio_html += f'''
            <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
                <div class="portfolio-emoji">📊</div>
                <div class="portfolio-label" style="color: #333;">Portfolio Stats</div>
                <div class="portfolio-value" style="color: #333;">{non_zero_assets}/4 Assets</div>
                <div class="portfolio-amount" style="color: #555;">Largest: {largest_asset} ({largest_percentage:.1f}%)</div>
            </div>'''
        else:
            # No valid prices fallback (9 boxes for consistency)
            for emoji, label in [("💵", "USD Value"), ("🇪🇺", "EUR Value"), ("🇦🇪", "AED Value"), ("🇮🇳", "INR Value"), ("💱", "USDT/INR Rate"), ("₿", "BTC Equivalent"), ("⟠", "ETH Equivalent"), ("🔸", "BNB Equivalent"), ("📊", "Portfolio Stats")]:
                portfolio_html += f'''
                <div class="portfolio-box" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333;">
                    <div class="portfolio-emoji">{emoji}</div>
                    <div class="portfolio-label" style="color: #333;">{label}</div>
                    <div class="portfolio-value" style="color: #333;">No Valid Prices</div>
                    <div class="portfolio-amount" style="color: #555;">Check APIs</div>
                </div>'''
        
        portfolio_html += '</div>'
        
        # Display the beautiful portfolio overview
        st.markdown(portfolio_html, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"❌ Error calculating portfolio values: {e}")
        st.info("🔄 Please try refreshing prices or check API connectivity.")
    
    # Portfolio management
    st.markdown("<br>", unsafe_allow_html=True)
    load_col, clear_col, spacer = st.columns([1, 1, 1])
    
    with load_col:
        if st.button("📂 Reset to Default", type="secondary", use_container_width=True):
            reset_to_default_portfolio()
            st.success("✅ Reset to default portfolio")
            st.rerun()
    
    with clear_col:
        if st.button("🗑️ Clear All", type="primary", use_container_width=True):
            clear_portfolio()
            st.success("✅ Cleared all holdings")
            st.rerun()

if __name__ == "__main__":
    main()
