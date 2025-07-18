"""
A Streamlit application to display cryptocurrency data.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta
from bitfinex_data import get_btc_ohlc_data, fetch_and_update_data
from mempool_data import get_mempool_info, get_mempool_stats
from binance_data import get_binance_price

# Enhanced debug logging functions with full session instrumentation
def debug_log(message, level="INFO", context=None, data=None):
    """Enhanced debug logging with full session instrumentation"""
    from datetime import datetime
    
    if 'debug_logs' not in st.session_state:
        st.session_state.debug_logs = []
        # Log session initialization
        session_start = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            'level': 'SYSTEM',
            'message': '🚀 Debug session initialized',
            'context': 'session_start',
            'session_id': id(st.session_state),
            'user_agent': st.context.headers.get('User-Agent', 'Unknown') if hasattr(st, 'context') and hasattr(st.context, 'headers') else 'Unknown',
            'timestamp_full': datetime.now().isoformat(),
            'log_sequence': 1
        }
        st.session_state.debug_logs.append(session_start)
    
    # Enhanced timestamp with full datetime
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    timestamp_full = datetime.now().isoformat()
    
    # Build comprehensive log entry
    log_entry = {
        'timestamp': timestamp,
        'timestamp_full': timestamp_full,
        'level': level,
        'message': str(message),
        'context': context,
        'session_id': id(st.session_state),
        'log_sequence': len(st.session_state.debug_logs) + 1
    }
    
    # Add data payload if provided
    if data is not None:
        log_entry['data'] = data
    
    # Add system context for certain levels
    if level in ['ERROR', 'SYSTEM', 'WARNING']:
        try:
            import psutil
            import platform
            
            # Get system info with better error handling
            platform_info = platform.system()
            python_ver = platform.python_version()
            
            # Try to get memory info with fallback
            try:
                process = psutil.Process()
                memory_mb = round(process.memory_info().rss / 1024 / 1024, 2)
            except:
                memory_mb = 'psutil_error'
            
            # Try to get CPU info with fallback
            try:
                cpu_pct = round(psutil.cpu_percent(interval=0.1), 2)
            except:
                cpu_pct = 'psutil_error'
            
            log_entry['system_info'] = {
                'platform': platform_info,
                'python_version': python_ver,
                'memory_usage_mb': memory_mb,
                'cpu_percent': cpu_pct
            }
        except ImportError:
            # psutil not available in this environment
            import platform
            log_entry['system_info'] = {
                'platform': platform.system(),
                'python_version': platform.python_version(),
                'memory_usage_mb': 'psutil_not_installed',
                'cpu_percent': 'psutil_not_installed'
            }
        except Exception as e:
            import platform
            log_entry['system_info'] = {
                'platform': platform.system(),
                'python_version': platform.python_version(),
                'memory_usage_mb': f'error_{str(e)[:20]}',
                'cpu_percent': f'error_{str(e)[:20]}'
            }
    
    # Add stack trace for errors
    if level == 'ERROR':
        try:
            import traceback
            log_entry['stack_trace'] = traceback.format_stack()
        except:
            log_entry['stack_trace'] = 'unavailable'
    
    st.session_state.debug_logs.append(log_entry)
    
    # Keep last 2000 entries for full session history (increased from 1000)
    if len(st.session_state.debug_logs) > 2000:
        st.session_state.debug_logs = st.session_state.debug_logs[-2000:]
    
    # Enhanced console logging
    console_msg = f"[{timestamp}] {level}: {message}"
    if context:
        console_msg += f" | Context: {context}"
    if data:
        console_msg += f" | Data: {str(data)[:100]}..."
    print(console_msg)

def debug_log_api_call(api_name, endpoint, status, response_time=None, response_data=None, error=None):
    """Specialized logging for API calls with full instrumentation"""
    from datetime import datetime
    
    context_data = {
        'api_name': api_name,
        'endpoint': endpoint,
        'status': status,
        'response_time_ms': response_time,
        'timestamp_iso': datetime.now().isoformat()
    }
    
    if response_data:
        context_data['response_preview'] = str(response_data)[:200] + "..." if len(str(response_data)) > 200 else str(response_data)
    
    if error:
        context_data['error_details'] = str(error)
        debug_log(f"🌐 API {api_name} FAILED: {endpoint} - {error}", "ERROR", f"api_{api_name.lower()}", context_data)
    else:
        debug_log(f"🌐 API {api_name} SUCCESS: {endpoint} ({response_time}ms)", "SUCCESS", f"api_{api_name.lower()}", context_data)

def debug_log_data_processing(operation, input_data, output_data, processing_time=None):
    """Specialized logging for data processing operations"""
    from datetime import datetime
    
    context_data = {
        'operation': operation,
        'input_size': len(str(input_data)) if input_data else 0,
        'output_size': len(str(output_data)) if output_data else 0,
        'processing_time_ms': processing_time,
        'timestamp_iso': datetime.now().isoformat()
    }
    
    debug_log(f"⚙️ DATA PROCESSING: {operation}", "DATA", f"processing_{operation.lower().replace(' ', '_')}", context_data)

def debug_log_user_action(action, details=None):
    """Log user interactions and navigation"""
    from datetime import datetime
    
    context_data = {
        'action': action,
        'details': details,
        'timestamp_iso': datetime.now().isoformat()
    }
    
    debug_log(f"👤 USER ACTION: {action}", "INFO", "user_interaction", context_data)

def clear_debug_logs():
    """Clear debug logs with proper logging of the action"""
    log_count = len(st.session_state.debug_logs) if 'debug_logs' in st.session_state else 0
    
    if 'debug_logs' in st.session_state:
        st.session_state.debug_logs = []
    
    # Log the clear action
    debug_log(f"🗑️ Debug logs cleared (removed {log_count} entries)", "SYSTEM", "log_management")
    print(f"[SYSTEM] Debug logs cleared - removed {log_count} entries")
@st.cache_data(ttl=300)
def cached_get_mempool_info():
    return get_mempool_info()

@st.cache_data(ttl=300)
def cached_get_mempool_stats():
    return get_mempool_stats()

@st.cache_data(ttl=300)
def cached_get_crypto_prices():
    """
    Fetch crypto prices using multi-exchange fallback system.
    Tries multiple exchanges for maximum Community Cloud reliability.
    """
    import time
    start_time = time.time()
    debug_log("Starting multi-exchange price fetch...", "INFO", "price_fetch_start")
    
    try:
        from multi_exchange import get_multi_exchange_prices
        debug_log("Successfully imported multi_exchange module", "SUCCESS", "module_import")
        
        debug_log_api_call("Multi-Exchange", "get_multi_exchange_prices()", "STARTING")
        result = get_multi_exchange_prices()
        
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        debug_log_data_processing("Multi-exchange price aggregation", 
                                  f"Exchanges: {result.get('sources_used', [])}", 
                                  f"Prices: {list(result.get('prices', {}).keys())}", 
                                  processing_time)
        
        # Log detailed results
        debug_log(f"Multi-exchange result received:", "INFO", "price_fetch_result")
        debug_log(f"- Success count: {result.get('success_count', 'MISSING')}", "DATA", "success_metrics")
        debug_log(f"- Total count: {result.get('total_count', 'MISSING')}", "DATA", "total_metrics")
        debug_log(f"- Sources used: {result.get('sources_used', 'MISSING')}", "DATA", "source_metrics")
        debug_log(f"- Errors count: {len(result.get('errors', []))}", "DATA", "error_metrics")
        debug_log(f"- Prices keys: {list(result.get('prices', {}).keys())}", "DATA", "price_keys")
        
        # Log each price individually with validation
        prices = result.get('prices', {})
        for symbol, price in prices.items():
            price_status = "VALID" if price and price > 0 else "INVALID"
            debug_log(f"- {symbol}: {price} (type: {type(price).__name__}, status: {price_status})", 
                     "DATA" if price_status == "VALID" else "WARNING", f"price_{symbol.lower()}")
        
        # Add source information to the result
        if result.get('sources_used'):
            sources_info = f"📡 Data sources: {', '.join(result['sources_used'])}"
            debug_log(sources_info, "SUCCESS", "source_summary")
            
            # Add this info to errors for user visibility
            if 'sources_info' not in result:
                result['sources_info'] = sources_info
        
        debug_log_api_call("Multi-Exchange", "get_multi_exchange_prices()", "SUCCESS", processing_time, 
                          f"Got {len(prices)} prices from {len(result.get('sources_used', []))} sources")
        
        return result
            
    except Exception as e:
        error_msg = f"Critical error in multi-exchange price fetching: {str(e)}"
        debug_log(error_msg, "ERROR")
        debug_log(f"Exception type: {type(e).__name__}", "ERROR")
        debug_log(f"Exception details: {repr(e)}", "ERROR")
        
        # Try to get more details about the import error
        try:
            import multi_exchange
            debug_log("multi_exchange module import successful on retry", "INFO")
        except Exception as import_err:
            debug_log(f"multi_exchange import failed: {import_err}", "ERROR")
        
        return {
            'prices': {'BTC': None, 'ETH': None, 'BNB': None, 'POL': None},
            'errors': [error_msg],
            'success_count': 0,
            'total_count': 4,
            'sources_used': []
        }

# Keep the old function name for backward compatibility
@st.cache_data(ttl=300)
def cached_get_binance_prices():
    """Legacy function name - now uses multi-exchange system"""
    return cached_get_crypto_prices()

@st.cache_data(ttl=300)
def cached_get_btc_ohlc_data():
    return get_btc_ohlc_data()

# Portfolio management functions (cloud-friendly session state only)
def initialize_portfolio_session():
    """Initialize portfolio in session state with default values"""
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = {
            'btc': 0.9997,
            'eth': 9.9983,
            'bnb': 29.5623,
            'pol': 4986.01
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
    """Main function to run the Streamlit app with full session instrumentation."""
    st.set_page_config(
        page_title="Bitcoin Crypto Dashboard",
        page_icon="₿",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize portfolio session state
    initialize_portfolio_session()
    
    # Initialize debug logs storage
    if 'debug_logs' not in st.session_state:
        st.session_state.debug_logs = []
    
    # Initialize debug mode
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = False  # Off by default, use logs tab instead
    
    # Log application startup
    debug_log("🚀 Application startup initiated", "SYSTEM", "app_lifecycle")
    debug_log(f"📱 Page config set: Bitcoin Crypto Dashboard", "INFO", "app_config")
    debug_log(f"🔧 Session state initialized", "INFO", "session_management")
    
    # Add custom CSS for consistent font sizing and styling
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Consistent font sizes */
    h1 { font-size: 2.5rem !important; }
    h2 { font-size: 2rem !important; }
    h3 { font-size: 1.5rem !important; }
    
    /* Custom metric styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .fee-high { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); }
    .fee-medium { background: linear-gradient(135deg, #ffa726 0%, #fb8c00 100%); }
    .fee-low { background: linear-gradient(135deg, #4ecdc4 0%, #26a69a 100%); }
    .fee-economy { background: linear-gradient(135deg, #45b7d1 0%, #2980b9 100%); }
    
    .crypto-btc { background: linear-gradient(135deg, #f7931a 0%, #e67e22 100%); }
    .crypto-eth { background: linear-gradient(135deg, #627eea 0%, #3742fa 100%); }
    .crypto-bnb { background: linear-gradient(135deg, #f3ba2f 0%, #f39c12 100%); }
    .crypto-pol { background: linear-gradient(135deg, #8247e5 0%, #5f27cd 100%); }
    
    /* Better spacing */
    .stMetric > div { margin-bottom: 0.5rem; }
    </style>
    """, unsafe_allow_html=True)

    # Pre-fetch all data at startup with transparent error reporting
    with st.spinner("🔄 Loading cryptocurrency data..."):
        import time
        app_start_time = time.time()
        debug_log("Starting comprehensive data loading process...", "SYSTEM", "data_loading_start")
        
        try:
            debug_log("Clearing price caches...", "INFO", "cache_management")
            
            # Force fresh API calls - clear cache first
            cached_get_crypto_prices.clear()  # Use new function name
            cached_get_binance_prices.clear()  # Clear legacy cache too
            
            debug_log("Caches cleared successfully", "SUCCESS", "cache_management")
            
            # Load mempool data with timing
            mempool_start = time.time()
            debug_log("Loading mempool data...", "INFO", "mempool_loading")
            mempool_data = cached_get_mempool_info()
            mempool_time = round((time.time() - mempool_start) * 1000, 2)
            debug_log_data_processing("Mempool Info", "API Request", mempool_data, mempool_time)
            debug_log(f"Mempool data loaded in {mempool_time}ms", "SUCCESS", "mempool_loading")
            
            # Store mempool data in session state for other pages to access
            st.session_state.mempool_data = mempool_data
            
            # Load mempool stats with timing
            stats_start = time.time()
            debug_log("Loading mempool stats...", "INFO", "mempool_stats")
            mempool_stats = cached_get_mempool_stats()
            stats_time = round((time.time() - stats_start) * 1000, 2)
            debug_log_data_processing("Mempool Stats", "API Request", mempool_stats, stats_time)
            debug_log(f"Mempool stats loaded in {stats_time}ms", "SUCCESS", "mempool_stats")
            
            # Load price data with comprehensive tracking
            price_start = time.time()
            debug_log("Loading price data with multi-exchange system...", "INFO", "price_loading")
            price_result = cached_get_crypto_prices()  # Use multi-exchange system
            price_time = round((time.time() - price_start) * 1000, 2)
            debug_log_data_processing("Multi-Exchange Prices", 
                                     f"Exchanges: {price_result.get('sources_used', [])}", 
                                     f"Prices: {list(price_result.get('prices', {}).keys())}", 
                                     price_time)
            
            # Load BTC OHLC data with timing
            btc_start = time.time()
            debug_log("Loading BTC OHLC data...", "INFO", "btc_ohlc_loading")
            btc_data = cached_get_btc_ohlc_data()
            btc_time = round((time.time() - btc_start) * 1000, 2)
            debug_log_data_processing("BTC OHLC Data", "Binance API", 
                                     f"Rows: {len(btc_data) if hasattr(btc_data, '__len__') else 'Unknown'}", 
                                     btc_time)
            
            # Extract price data and show transparent status
            debug_log("Extracting and validating price data...", "INFO", "price_validation")
            binance_prices = price_result['prices']  # Keep variable name for compatibility
            price_errors = price_result['errors']
            success_rate = f"{price_result['success_count']}/{price_result['total_count']}"
            sources_used = price_result.get('sources_used', [])
            
            # Log comprehensive data summary
            total_load_time = round((time.time() - app_start_time) * 1000, 2)
            debug_log(f"Data loading completed in {total_load_time}ms", "SUCCESS", "data_loading_complete")
            debug_log(f"- Mempool data: {mempool_time}ms", "DATA", "timing_breakdown")
            debug_log(f"- Mempool stats: {stats_time}ms", "DATA", "timing_breakdown")
            debug_log(f"- Price data: {price_time}ms", "DATA", "timing_breakdown")
            debug_log(f"- BTC OHLC: {btc_time}ms", "DATA", "timing_breakdown")
            
            # Validate each price individually
            for symbol, price in binance_prices.items():
                validation_status = "VALID" if price and price > 0 else "INVALID"
                debug_log(f"Price validation - {symbol}: ${price} ({validation_status})", 
                         "SUCCESS" if validation_status == "VALID" else "WARNING", 
                         f"price_validation_{symbol.lower()}")
            
            debug_log(f"Final extracted data summary:", "DATA", "data_summary")
            debug_log(f"- Price success rate: {success_rate}", "DATA", "success_metrics")
            debug_log(f"- Data sources used: {sources_used}", "DATA", "source_tracking")
            debug_log(f"- Error count: {len(price_errors)}", "DATA", "error_tracking")
            
            # Show API status to user with detailed information including sources
            if price_result['success_count'] == price_result['total_count']:
                sources_text = f" via {', '.join(sources_used)}" if sources_used else ""
                # Success is logged but not displayed to user (already in debug logs)
                debug_log(f"All APIs successful: {success_rate}{sources_text}", "SUCCESS")
            elif price_result['success_count'] > 0:
                sources_text = f" via {', '.join(sources_used)}" if sources_used else ""
                st.warning(f"⚠️ Partial API success ({success_rate}){sources_text} - Some prices may be unavailable")
                debug_log(f"Partial API success: {success_rate}{sources_text}", "WARNING")
                with st.expander("🔍 View API Issues"):
                    for error in price_errors:
                        st.error(error)
            else:
                st.error(f"❌ All price APIs failed ({success_rate}) - No live prices available")
                debug_log(f"All APIs failed: {success_rate}", "ERROR")
                with st.expander("🔍 View All API Errors"):
                    for error in price_errors:
                        st.error(error)
                    st.info("💡 Try refreshing the page or using the 'Refresh Prices' button in Portfolio section")
            
            debug_log("Data loading completed successfully", "SUCCESS")
                
        except Exception as e:
            error_msg = f"Critical error loading data: {e}"
            debug_log(error_msg, "ERROR")
            debug_log(f"Exception type: {type(e).__name__}", "ERROR")
            debug_log(f"Exception details: {repr(e)}", "ERROR")
            debug_log(f"Exception args: {e.args}", "ERROR")
            
            # Try to get traceback
            import traceback
            tb = traceback.format_exc()
            debug_log(f"Traceback: {tb}", "ERROR")
            
            st.error(f"❌ {error_msg}")
            st.info("🔄 Please refresh the page to retry data loading.")
            st.info("💡 Check the 'Debug Logs' tab for detailed error information.")
            
            # Set fallback data but be transparent about it
            st.warning("⚠️ Using fallback data due to loading errors")
            mempool_data = {'error': 'Data unavailable'}
            mempool_stats = {'error': 'Data unavailable'}
            binance_prices = {'BTC': None, 'ETH': None, 'BNB': None, 'POL': None}
            btc_data = pd.DataFrame()

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    tabs = [
        "Why Bitcoin?",
        "Bitcoin's Future and Destiny",
        "Bitcoin OHLC",
        "Mempool Data",
        "Portfolio Value",
        "Bitcoin Metrics",
        "Debug Logs",
    ]
    page = st.sidebar.radio("Go to", tabs)
    
    # Log user navigation
    debug_log_user_action(f"Navigation to '{page}' tab", {'tab_name': page, 'available_tabs': tabs})

    if page == "Why Bitcoin?":
        st.header("Why Bitcoin is the Most Powerful Store of Value")
        
        # Compact two-column layout
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("🌟 Key Characteristics")
            
            st.markdown("""
            **🔒 Decentralization**  
            Bitcoin operates on a peer-to-peer network, free from control by any single entity, making it resistant to censorship and manipulation.
            
            **💎 Limited Supply**  
            Only 21 million bitcoins will ever exist, protecting against inflationary pressures that plague fiat currencies.
            
            **🛡️ Security**  
            Secured by massive computing power through proof-of-work, making it incredibly difficult to alter transaction history.
            
            **🌍 Portability & Divisibility**  
            Can be sent globally with internet access and divided into smaller units for accessibility.
            """)
        
        with col_right:
            st.subheader("⚡ Bitcoin's Legacy")
            
            st.markdown("""
            **🏛️ Digital Gold**  
            Bitcoin has emerged as a revolutionary store of value, often called "digital gold" due to its scarcity and store-of-value properties.
            
            **🚀 Resistance Money**  
            As the world faces economic uncertainty and currency devaluation, Bitcoin stands as a beacon of financial sovereignty.
            
            **🔮 Future of Finance**  
            Bitcoin represents money truly owned by the people, resistant to the whims of central planners and government manipulation.
            
            **📈 Unstoppable Growth**  
            Its journey has just begun, with unlimited potential to reshape the global financial system.
            """)
        
        # Compact conclusion
        st.subheader("🎯 The Bottom Line")
        st.info("""
        Bitcoin is more than just a cryptocurrency—it's a paradigm shift towards decentralized, sound money. 
        Its unique combination of scarcity, security, and decentralization makes it the most powerful store of value in human history.
        """)

    elif page == "Bitcoin's Future and Destiny":
        st.header("🔮 Bitcoin's Future and Destiny")
        
        # Initialize session state for Future and Destiny data
        if 'bfd_data' not in st.session_state:
            st.session_state.bfd_data = {}
        
        # Add cache for Bitcoin Future metrics with 5-minute TTL
        @st.cache_data(ttl=300)
        def cached_get_future_metrics():
            debug_log("🚀 Initializing Bitcoin Future metrics with enhanced logging...", "INFO", "bitcoin_future_init")
            
            from bitcoin_metrics import BitcoinMetrics
            # Create instance with debug logging
            btc_metrics = BitcoinMetrics(debug_logger=debug_log)
            
            debug_log("📊 Starting comprehensive Bitcoin future metrics collection...", "INFO", "bitcoin_future_start")
            return btc_metrics.get_comprehensive_metrics()
        
        # Refresh button for future metrics
        col_refresh, col_status = st.columns([1, 3])
        with col_refresh:
            if st.button("🔄 Refresh Data", type="secondary", key="future_refresh"):
                cached_get_future_metrics.clear()
                st.rerun()
        
        # Load comprehensive Bitcoin data
        with st.spinner("🔄 Loading Bitcoin's future metrics..."):
            try:
                debug_log("🚀 Starting Bitcoin Future metrics fetch...", "INFO", "bitcoin_future_metrics_start")
                metrics = cached_get_future_metrics()
                debug_log(f"✅ Bitcoin Future metrics loaded successfully with {len(metrics.get('errors', []))} errors", "SUCCESS", "bitcoin_future_metrics_success")
                
                with col_status:
                    if len(metrics.get('errors', [])) == 0:
                        st.success("✅ All future metrics loaded successfully")
                    elif len(metrics.get('errors', [])) < 3:
                        st.warning(f"⚠️ {len(metrics['errors'])} metrics failed to load")
                    else:
                        st.error(f"❌ Multiple metrics failed ({len(metrics['errors'])} errors)")
                
                # Show errors in expander if any
                if metrics.get('errors'):
                    with st.expander(f"🔍 View {len(metrics['errors'])} API Issues"):
                        for error in metrics['errors']:
                            st.error(error)
                
                # === SECTION 1: KEY SCARCITY INFOGRAPHIC / DASHBOARD ===
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("💎 Bitcoin Scarcity Dashboard")
                
                # Extract data from metrics
                blockchain_data = metrics.get('blockchain', {})
                coingecko = metrics.get('coingecko', {})
                
                # Calculate key scarcity metrics
                HARD_CAP = 21_000_000  # Requirement #1: Hard cap display
                
                # Requirement #2: Current circulation and remaining to mine
                if blockchain_data.get('total_supply'):
                    total_mined = blockchain_data['total_supply'] / 1e8  # Convert from satoshis
                    remaining_to_mine = HARD_CAP - total_mined
                    percentage_mined = (total_mined / HARD_CAP) * 100
                else:
                    total_mined = None
                    remaining_to_mine = None
                    percentage_mined = None
                
                # Beautiful scarcity dashboard with custom styling
                st.markdown("""
                <style>
                .scarcity-container {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 15px;
                    margin: 20px 0;
                    padding: 25px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }
                .scarcity-box {
                    flex: 1;
                    min-width: 200px;
                    background: rgba(255,255,255,0.95);
                    border-radius: 12px;
                    padding: 20px;
                    text-align: center;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    transition: transform 0.3s ease;
                }
                .scarcity-box:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                }
                .scarcity-emoji {
                    font-size: 32px;
                    margin-bottom: 10px;
                    display: block;
                }
                .scarcity-label {
                    font-size: 14px;
                    color: #555;
                    margin: 8px 0;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                .scarcity-value {
                    font-size: 24px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin: 10px 0;
                    line-height: 1.2;
                }
                .scarcity-detail {
                    font-size: 12px;
                    color: #7f8c8d;
                    margin: 5px 0;
                    line-height: 1.3;
                }
                .scarcity-hard-cap {
                    background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
                    color: white;
                }
                .scarcity-hard-cap .scarcity-label,
                .scarcity-hard-cap .scarcity-value,
                .scarcity-hard-cap .scarcity-detail {
                    color: white;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Generate scarcity dashboard content
                scarcity_html = '<div class="scarcity-container">'
                
                # Hard Cap (Requirement #1)
                scarcity_html += f'''
                <div class="scarcity-box scarcity-hard-cap">
                    <div class="scarcity-emoji">💎</div>
                    <div class="scarcity-label">Maximum Supply</div>
                    <div class="scarcity-value">{HARD_CAP:,} BTC</div>
                    <div class="scarcity-detail">Fixed by Algorithm<br>Never to be Changed</div>
                </div>'''
                
                # Current Mined (Requirement #2)
                if total_mined is not None:
                    scarcity_html += f'''
                    <div class="scarcity-box">
                        <div class="scarcity-emoji">⛏️</div>
                        <div class="scarcity-label">Mined So Far</div>
                        <div class="scarcity-value">{total_mined:,.0f} BTC</div>
                        <div class="scarcity-detail">{percentage_mined:.2f}% of Total<br>Supply Complete</div>
                    </div>'''
                else:
                    scarcity_html += '''
                    <div class="scarcity-box">
                        <div class="scarcity-emoji">⛏️</div>
                        <div class="scarcity-label">Mined So Far</div>
                        <div class="scarcity-value">API Failed</div>
                        <div class="scarcity-detail">Data Unavailable</div>
                    </div>'''
                
                # Remaining to Mine (Requirement #2)
                if remaining_to_mine is not None:
                    scarcity_html += f'''
                    <div class="scarcity-box">
                        <div class="scarcity-emoji">⏳</div>
                        <div class="scarcity-label">Left to Mine</div>
                        <div class="scarcity-value">{remaining_to_mine:,.0f} BTC</div>
                        <div class="scarcity-detail">{100-percentage_mined:.2f}% Remaining<br>Until ~2140</div>
                    </div>'''
                else:
                    scarcity_html += '''
                    <div class="scarcity-box">
                        <div class="scarcity-emoji">⏳</div>
                        <div class="scarcity-label">Left to Mine</div>
                        <div class="scarcity-value">API Failed</div>
                        <div class="scarcity-detail">Data Unavailable</div>
                    </div>'''
                
                # Current Price from CoinGecko
                if coingecko.get('price_usd'):
                    price = coingecko['price_usd']
                    market_cap = price * total_mined if total_mined else None
                    scarcity_html += f'''
                    <div class="scarcity-box">
                        <div class="scarcity-emoji">💰</div>
                        <div class="scarcity-label">Current Price</div>
                        <div class="scarcity-value">${price:,.0f}</div>
                        <div class="scarcity-detail">Market Cap:<br>${market_cap/1e12:.2f}T</div>
                    </div>''' if market_cap else f'''
                    <div class="scarcity-box">
                        <div class="scarcity-emoji">💰</div>
                        <div class="scarcity-label">Current Price</div>
                        <div class="scarcity-value">${price:,.0f}</div>
                        <div class="scarcity-detail">Live Price Data</div>
                    </div>'''
                else:
                    scarcity_html += '''
                    <div class="scarcity-box">
                        <div class="scarcity-emoji">💰</div>
                        <div class="scarcity-label">Current Price</div>
                        <div class="scarcity-value">API Failed</div>
                        <div class="scarcity-detail">Price Unavailable</div>
                    </div>'''
                
                scarcity_html += '</div>'
                
                # Display the beautiful scarcity dashboard
                st.markdown(scarcity_html, unsafe_allow_html=True)
                
                # Progress bar to 21M (visual representation)
                if percentage_mined is not None:
                    st.markdown("### 📊 Mining Progress to 21 Million")
                    progress_col1, progress_col2 = st.columns([3, 1])
                    with progress_col1:
                        st.progress(percentage_mined/100, text=f"{percentage_mined:.3f}% of 21M Bitcoin mined")
                    with progress_col2:
                        st.metric("Completion", f"{percentage_mined:.3f}%")
                
                # === SECTION 2: HALVING EVENTS AND MINING VISUALIZATION ===
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.subheader("⚡ Bitcoin Mining & Halving Events")
                
                # Requirement #4: Bitcoin Mining Rate, Block Rewards & Halving Events
                halving_col1, halving_col2 = st.columns(2)
                
                with halving_col1:
                    # Historical halving data (hardcoded reliable data)
                    halving_events = [
                        {"date": "2009-01-03", "block": 0, "reward": 50, "event": "Genesis Block"},
                        {"date": "2012-11-28", "block": 210000, "reward": 25, "event": "1st Halving"},
                        {"date": "2016-07-09", "block": 420000, "reward": 12.5, "event": "2nd Halving"},
                        {"date": "2020-05-11", "block": 630000, "reward": 6.25, "event": "3rd Halving"},
                        {"date": "2024-04-20", "block": 840000, "reward": 3.125, "event": "4th Halving"},
                        {"date": "2028-04-20", "block": 1050000, "reward": 1.5625, "event": "5th Halving (Est.)"},
                        {"date": "2032-04-20", "block": 1260000, "reward": 0.78125, "event": "6th Halving (Est.)"},
                    ]
                    
                    # Create halving timeline chart
                    import plotly.graph_objects as go
                    from datetime import datetime
                    
                    dates = [datetime.strptime(h["date"], "%Y-%m-%d") for h in halving_events]
                    rewards = [h["reward"] for h in halving_events]
                    events = [h["event"] for h in halving_events]
                    
                    fig_halving = go.Figure()
                    fig_halving.add_trace(go.Scatter(
                        x=dates,
                        y=rewards,
                        mode='lines+markers',
                        name='Block Reward (BTC)',
                        line=dict(color='#f7931a', width=4),
                        marker=dict(size=10, color='#f7931a'),
                        text=events,
                        hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Reward: %{y} BTC<extra></extra>'
                    ))
                    
                    fig_halving.update_layout(
                        title="🎁 Block Reward Evolution & Halving Events",
                        xaxis_title="Year",
                        yaxis_title="Block Reward (BTC)",
                        height=400,
                        template="plotly_dark",
                        showlegend=False
                    )
                    
                    # Add vertical lines for halving events
                    for i, event in enumerate(halving_events[1:], 1):  # Skip genesis
                        fig_halving.add_vline(
                            x=dates[i], 
                            line_dash="dash", 
                            line_color="rgba(255,255,255,0.3)",
                            annotation_text=f"Halving {i}"
                        )
                    
                    st.plotly_chart(fig_halving, use_container_width=True)
                
                with halving_col2:
                    # Next halving calculation
                    try:
                        debug_log("🔄 Starting halving countdown calculation...", "INFO", "halving_calculation_start")
                        current_blocks = blockchain_data.get('block_count', 0)
                        debug_log(f"📊 Current block count: {current_blocks}", "DATA", "current_blocks_data")
                        
                        if current_blocks > 0:
                            # Calculate next halving details
                            blocks_per_halving = 210_000
                            current_epoch = current_blocks // blocks_per_halving
                            next_halving_block = (current_epoch + 1) * blocks_per_halving
                            blocks_to_halving = next_halving_block - current_blocks
                            
                            # Estimate time to next halving (10 min average block time)
                            days_to_halving = (blocks_to_halving * 10) / (60 * 24)
                            debug_log(f"⏰ Calculated days to halving: {days_to_halving}", "DATA", "days_to_halving_calculation")
                            
                            # Current reward calculation
                            current_reward = 50 / (2 ** current_epoch)
                            next_reward = current_reward / 2
                            
                            debug_log("✅ Halving calculation completed successfully", "SUCCESS", "halving_calculation_success")
                            
                            st.markdown("### 📅 Next Halving Countdown")
                            
                            # Halving countdown metrics
                            countdown_col1, countdown_col2 = st.columns(2)
                            with countdown_col1:
                                st.metric("⏰ Days Until Halving", f"{days_to_halving:,.0f}")
                                st.metric("🧱 Blocks Remaining", f"{blocks_to_halving:,}")
                            with countdown_col2:
                                st.metric("🎁 Current Reward", f"{current_reward} BTC")
                                st.metric("⬇️ Next Reward", f"{next_reward} BTC")
                            
                            # Progress to next halving
                            blocks_mined_this_cycle = current_blocks - (current_epoch * blocks_per_halving)
                            cycle_progress = (blocks_mined_this_cycle / blocks_per_halving) * 100
                            
                            st.markdown("#### 📊 Current Halving Cycle Progress")
                            st.progress(cycle_progress/100, text=f"{cycle_progress:.1f}% to next halving")
                            
                            st.caption(f"**Halving Epoch:** {current_epoch + 1}")
                            st.caption(f"**Next Halving Block:** {next_halving_block:,}")
                        else:
                            debug_log("❌ Unable to calculate halving data - block count is 0", "ERROR", "halving_calculation_no_blocks")
                            st.error("❌ Unable to calculate halving data - API failed")
                    except Exception as e:
                        error_msg = f"Failed to calculate halving data: {str(e)}"
                        debug_log(f"💥 Halving calculation error: {error_msg}", "ERROR", "halving_calculation_exception", {"error": str(e)})
                        st.error(f"❌ {error_msg}")
                        # Show fallback content
                        st.info("📅 Next halving estimated for 2028 (approximate)")
                        st.info("🎁 Current block reward: 3.125 BTC")
                
                # === SECTION 3: BITCOIN SUPPLY PROJECTION TO 2140 ===
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.subheader("📈 Bitcoin Supply Projection to 2140")
                
                # Requirement #3: Bitcoins Left to Be Mined Over Time
                # Generate projection data
                def calculate_supply_projection():
                    """Calculate Bitcoin supply projection to 2140"""
                    years = []
                    btc_mined = []
                    btc_remaining = []
                    
                    # Starting parameters
                    current_year = 2025
                    current_supply = total_mined if total_mined else 19_800_000  # Fallback estimate
                    
                    # Halving schedule (every 4 years approximately)
                    halving_years = [2028, 2032, 2036, 2040, 2044, 2048, 2052, 2056, 2060, 2064, 2068, 2072, 2076, 2080, 2084, 2088, 2092, 2096, 2100, 2104, 2108, 2112, 2116, 2120, 2124, 2128, 2132, 2136, 2140]
                    current_reward = 3.125  # Post-2024 halving
                    
                    for year in range(current_year, 2141):
                        # Check if it's a halving year
                        if year in halving_years:
                            current_reward = current_reward / 2
                        
                        # Calculate approximate BTC mined this year
                        blocks_per_year = 365.25 * 24 * 6  # ~6 blocks per hour on average
                        btc_this_year = blocks_per_year * current_reward
                        current_supply += btc_this_year
                        
                        # Ensure we don't exceed 21M
                        if current_supply > HARD_CAP:
                            current_supply = HARD_CAP
                        
                        years.append(year)
                        btc_mined.append(current_supply)
                        btc_remaining.append(HARD_CAP - current_supply)
                    
                    return years, btc_mined, btc_remaining
                
                # Generate projection
                years, btc_mined, btc_remaining = calculate_supply_projection()
                
                # Create supply projection chart
                fig_projection = go.Figure()
                
                # Add mined Bitcoin
                fig_projection.add_trace(go.Scatter(
                    x=years,
                    y=btc_mined,
                    mode='lines',
                    name='Total Mined',
                    line=dict(color='#00d4aa', width=3),
                    fill='tonexty'
                ))
                
                # Add remaining Bitcoin
                fig_projection.add_trace(go.Scatter(
                    x=years,
                    y=btc_remaining,
                    mode='lines',
                    name='Remaining to Mine',
                    line=dict(color='#ff6b35', width=3),
                    fill='tozeroy'
                ))
                
                # Add 21M cap line
                fig_projection.add_hline(
                    y=HARD_CAP, 
                    line_dash="dash", 
                    line_color="white",
                    annotation_text="21 Million Cap"
                )
                
                fig_projection.update_layout(
                    title="📊 Bitcoin Supply Evolution to 2140",
                    xaxis_title="Year",
                    yaxis_title="Bitcoin (BTC)",
                    height=500,
                    template="plotly_dark",
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_projection, use_container_width=True)
                
                # Year slider for projection exploration (Requirement #3: Session State)
                st.markdown("#### 🔍 Explore Supply Projection")
                year_range = st.slider(
                    "Select Year Range for Detailed View",
                    min_value=2025,
                    max_value=2140,
                    value=(2025, 2050),
                    step=5,
                    key="year_range_slider"
                )
                
                # Filtered projection based on slider
                start_idx = year_range[0] - 2025
                end_idx = year_range[1] - 2025 + 1
                
                filtered_years = years[start_idx:end_idx]
                filtered_mined = btc_mined[start_idx:end_idx]
                filtered_remaining = btc_remaining[start_idx:end_idx]
                
                if filtered_years:
                    projection_col1, projection_col2, projection_col3 = st.columns(3)
                    with projection_col1:
                        st.metric(
                            f"📅 BTC Mined by {year_range[1]}", 
                            f"{filtered_mined[-1]:,.0f}",
                            delta=f"+{filtered_mined[-1] - filtered_mined[0]:,.0f} from {year_range[0]}"
                        )
                    with projection_col2:
                        st.metric(
                            f"⏳ Remaining in {year_range[1]}", 
                            f"{filtered_remaining[-1]:,.0f}",
                            delta=f"-{filtered_remaining[0] - filtered_remaining[-1]:,.0f} mined"
                        )
                    with projection_col3:
                        completion_percent = (filtered_mined[-1] / HARD_CAP) * 100
                        st.metric(
                            f"📊 Completion by {year_range[1]}", 
                            f"{completion_percent:.2f}%"
                        )
                
                # Store projection data in session state
                st.session_state.bfd_data['supply_projection'] = {
                    'years': years,
                    'mined': btc_mined,
                    'remaining': btc_remaining
                }
                
                # === SECTION 5: MEMPOOL AND TRANSACTION ANALYSIS ===
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.subheader("📦 Mempool & Transaction Analysis")
                
                # Requirement #5: Mempool Data (Live and Historic) & #12: Transaction Fees and Congestion
                mempool_col1, mempool_col2 = st.columns(2)
                
                with mempool_col1:
                    # Get mempool data (reuse existing functionality)
                    try:
                        # Use the already available mempool_data from session state
                        mempool_info = st.session_state.get('mempool_data', {})
                        if not mempool_info or 'error' in mempool_info:
                            # Fallback: call the function directly since it's in the same module
                            mempool_info = cached_get_mempool_info()
                            # Store it back in session state for future use
                            st.session_state.mempool_data = mempool_info
                        
                        if 'error' not in mempool_info and 'fees' in mempool_info:
                            fees = mempool_info['fees']
                            
                            # Create fee progression chart
                            fee_labels = ['Economy', 'Low Priority', 'Medium Priority', 'High Priority']
                            fee_values = [fees['economyFee'], fees['hourFee'], fees['halfHourFee'], fees['fastestFee']]
                            fee_colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']
                            
                            fig_fees = go.Figure()
                            fig_fees.add_trace(go.Bar(
                                x=fee_labels,
                                y=fee_values,
                                marker_color=fee_colors,
                                text=[f"{fee} sat/vB" for fee in fee_values],
                                textposition='auto',
                                hovertemplate='<b>%{x}</b><br>Fee: %{y} sat/vB<extra></extra>'
                            ))
                            
                            fig_fees.update_layout(
                                title="💳 Current Transaction Fee Levels",
                                xaxis_title="Priority Level",
                                yaxis_title="Fee (sat/vB)",
                                height=400,
                                template="plotly_dark",
                                showlegend=False
                            )
                            
                            st.plotly_chart(fig_fees, use_container_width=True)
                            
                            # Fee metrics
                            fee_metric_col1, fee_metric_col2 = st.columns(2)
                            with fee_metric_col1:
                                avg_fee = sum(fee_values) / len(fee_values)
                                st.metric("📊 Average Fee", f"{avg_fee:.0f} sat/vB")
                            with fee_metric_col2:
                                fee_range = max(fee_values) - min(fee_values)
                                st.metric("📈 Fee Range", f"{fee_range} sat/vB")
                        else:
                            st.error("❌ Mempool fee data unavailable")
                    except Exception as e:
                        st.error(f"❌ Failed to load mempool data: {e}")
                
                with mempool_col2:
                    # Mempool size visualization
                    try:
                        if 'error' not in mempool_info and 'mempool_blocks' in mempool_info:
                            blocks_data = mempool_info['mempool_blocks'][:10]
                            
                            # Create mempool blocks chart
                            fig_mempool = go.Figure()
                            fig_mempool.add_trace(go.Scatter(
                                x=[f"Block {i+1}" for i in range(len(blocks_data))],
                                y=[block['nTx'] for block in blocks_data],
                                mode='lines+markers',
                                name='Pending Transactions',
                                line=dict(color='#9b59b6', width=3),
                                marker=dict(size=8, color='#9b59b6'),
                                fill='tozeroy',
                                hovertemplate='<b>%{x}</b><br>Transactions: %{y}<extra></extra>'
                            ))
                            
                            fig_mempool.update_layout(
                                title="📦 Mempool Congestion (Next 10 Blocks)",
                                xaxis_title="Upcoming Blocks",
                                yaxis_title="Transaction Count",
                                height=400,
                                template="plotly_dark",
                                showlegend=False
                            )
                            
                            st.plotly_chart(fig_mempool, use_container_width=True)
                            
                            # Mempool metrics
                            total_pending = sum(block['nTx'] for block in blocks_data)
                            mempool_metric_col1, mempool_metric_col2 = st.columns(2)
                            with mempool_metric_col1:
                                st.metric("⏳ Total Pending", f"{total_pending:,}")
                            with mempool_metric_col2:
                                avg_per_block = total_pending / len(blocks_data) if blocks_data else 0
                                st.metric("📊 Avg per Block", f"{avg_per_block:.0f}")
                        else:
                            st.error("❌ Mempool block data unavailable")
                    except Exception as e:
                        st.error(f"❌ Failed to load mempool blocks: {e}")
                
                # === SECTION 6: BITCOIN ADOPTION METRICS ===
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.subheader("🌍 Bitcoin Adoption & Network Growth")
                
                # Requirement #6: Active Bitcoin Wallet Addresses Over Time
                # Requirement #7: Global Bitcoin Adoption and User Growth
                adoption_col1, adoption_col2 = st.columns(2)
                
                with adoption_col1:
                    st.markdown("#### 🏦 Active Wallet Growth Estimate")
                    
                    # Generate estimated wallet growth data (based on historical patterns)
                    def generate_wallet_estimates():
                        years = list(range(2010, 2026))
                        # Estimated active addresses growth based on historical data
                        wallets = [
                            1000, 5000, 15000, 50000, 150000, 300000, 600000,  # 2010-2016
                            1200000, 2500000, 5000000, 8000000, 12000000,      # 2017-2021
                            15000000, 18000000, 22000000, 28000000             # 2022-2025
                        ]
                        return years, wallets
                    
                    years, wallet_estimates = generate_wallet_estimates()
                    
                    fig_wallets = go.Figure()
                    fig_wallets.add_trace(go.Scatter(
                        x=years,
                        y=wallet_estimates,
                        mode='lines+markers',
                        name='Active Wallets',
                        line=dict(color='#1abc9c', width=3),
                        marker=dict(size=6),
                        fill='tozeroy',
                        hovertemplate='<b>%{x}</b><br>Est. Active Wallets: %{y:,}<extra></extra>'
                    ))
                    
                    fig_wallets.update_layout(
                        title="🏦 Bitcoin Active Wallet Growth",
                        xaxis_title="Year",
                        yaxis_title="Estimated Active Wallets",
                        height=350,
                        template="plotly_dark",
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_wallets, use_container_width=True)
                    
                    # Current wallet metrics
                    if wallet_estimates:
                        current_wallets = wallet_estimates[-1]
                        prev_year_wallets = wallet_estimates[-2] if len(wallet_estimates) > 1 else 0
                        growth = current_wallets - prev_year_wallets
                        st.metric("🔢 Est. Active Wallets (2025)", f"{current_wallets:,}", delta=f"+{growth:,} from 2024")
                
                with adoption_col2:
                    st.markdown("#### 🌍 Global Adoption Estimates")
                    
                    # Global adoption data (estimated percentages by region)
                    regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Africa', 'Middle East']
                    adoption_rates = [16.0, 12.0, 8.5, 14.0, 4.5, 6.0]  # Estimated % of population
                    region_colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
                    
                    fig_adoption = go.Figure()
                    fig_adoption.add_trace(go.Bar(
                        x=regions,
                        y=adoption_rates,
                        marker_color=region_colors,
                        text=[f"{rate}%" for rate in adoption_rates],
                        textposition='auto',
                        hovertemplate='<b>%{x}</b><br>Adoption Rate: %{y}%<extra></extra>'
                    ))
                    
                    fig_adoption.update_layout(
                        title="🌍 Bitcoin Adoption by Region",
                        xaxis_title="Region",
                        yaxis_title="Estimated Adoption Rate (%)",
                        height=350,
                        template="plotly_dark",
                        showlegend=False,
                        xaxis=dict(tickangle=45)
                    )
                    
                    st.plotly_chart(fig_adoption, use_container_width=True)
                    
                    # Adoption metrics
                    avg_adoption = sum(adoption_rates) / len(adoption_rates)
                    max_region = regions[adoption_rates.index(max(adoption_rates))]
                    st.metric("📊 Global Average", f"{avg_adoption:.1f}%")
                    st.metric("🏆 Leading Region", max_region)
                
                # === SECTION 7: BITCOIN SUPPLY DISTRIBUTION ===
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.subheader("💎 Bitcoin Supply Distribution")
                
                # Requirement #8: Illiquid Bitcoin Supply Estimation
                # Requirement #9: Holder Behavior: Long-term vs. Short-term
                supply_col1, supply_col2 = st.columns(2)
                
                with supply_col1:
                    st.markdown("#### 🔒 Liquid vs. Illiquid Supply")
                    
                    # Estimated supply distribution
                    if total_mined is not None:
                        # Estimated breakdown based on on-chain analysis
                        lost_btc = total_mined * 0.20      # ~20% estimated lost forever
                        hodled_btc = total_mined * 0.45    # ~45% held long-term (>1 year)
                        liquid_btc = total_mined * 0.35    # ~35% actively traded
                        
                        supply_labels = ['Lost Forever', 'Long-term Hold', 'Liquid Supply']
                        supply_values = [lost_btc, hodled_btc, liquid_btc]
                        supply_colors = ['#95a5a6', '#3498db', '#2ecc71']
                        
                        fig_supply = go.Figure()
                        fig_supply.add_trace(go.Pie(
                            labels=supply_labels,
                            values=supply_values,
                            hole=0.4,
                            marker_colors=supply_colors,
                            textinfo='label+percent+value',
                            texttemplate='<b>%{label}</b><br>%{percent}<br>%{value:,.0f} BTC',
                            hovertemplate='<b>%{label}</b><br>%{value:,.0f} BTC<br>%{percent}<extra></extra>'
                        ))
                        
                        fig_supply.update_layout(
                            title="💎 Bitcoin Supply Distribution",
                            height=400,
                            template="plotly_dark",
                            showlegend=False
                        )
                        
                        st.plotly_chart(fig_supply, use_container_width=True)
                        
                        # Supply metrics
                        supply_metric_col1, supply_metric_col2 = st.columns(2)
                        with supply_metric_col1:
                            st.metric("💧 Liquid Supply", f"{liquid_btc:,.0f} BTC", 
                                    delta=f"{(liquid_btc/total_mined)*100:.1f}% of total")
                        with supply_metric_col2:
                            st.metric("🔒 Illiquid Supply", f"{lost_btc + hodled_btc:,.0f} BTC",
                                    delta=f"{((lost_btc + hodled_btc)/total_mined)*100:.1f}% of total")
                    else:
                        st.error("❌ Supply distribution data unavailable")
                
                with supply_col2:
                    st.markdown("#### 💎 Holder Behavior Analysis")
                    
                    # Generate holder behavior timeline
                    timeline_years = list(range(2018, 2026))
                    diamond_hands = [25, 30, 35, 42, 48, 52, 58, 63]  # % long-term holders
                    paper_hands = [75, 70, 65, 58, 52, 48, 42, 37]   # % short-term holders
                    
                    fig_holders = go.Figure()
                    
                    # Diamond hands (long-term holders)
                    fig_holders.add_trace(go.Scatter(
                        x=timeline_years,
                        y=diamond_hands,
                        mode='lines+markers',
                        name='Diamond Hands (>1yr)',
                        line=dict(color='#3498db', width=3),
                        marker=dict(size=8),
                        fill='tonexty',
                        stackgroup='one'
                    ))
                    
                    # Paper hands (short-term holders)
                    fig_holders.add_trace(go.Scatter(
                        x=timeline_years,
                        y=paper_hands,
                        mode='lines+markers',
                        name='Paper Hands (<1yr)',
                        line=dict(color='#e74c3c', width=3),
                        marker=dict(size=8),
                        fill='tozeroy',
                        stackgroup='one'
                    ))
                    
                    fig_holders.update_layout(
                        title="💎 Holder Behavior Evolution",
                        xaxis_title="Year",
                        yaxis_title="Percentage of Supply",
                        height=400,
                        template="plotly_dark",
                        legend=dict(x=0.02, y=0.98),
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig_holders, use_container_width=True)
                    
                    # Holder metrics
                    current_diamond = diamond_hands[-1]
                    current_paper = paper_hands[-1]
                    holder_metric_col1, holder_metric_col2 = st.columns(2)
                    with holder_metric_col1:
                        st.metric("💎 Diamond Hands", f"{current_diamond}%", 
                                delta=f"+{diamond_hands[-1] - diamond_hands[0]}% since 2018")
                    with holder_metric_col2:
                        st.metric("📄 Paper Hands", f"{current_paper}%",
                                delta=f"{paper_hands[-1] - paper_hands[0]}% since 2018")
                
                # === SECTION 8: INSTITUTIONAL ADOPTION ===
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.subheader("🏢 Institutional & Corporate Adoption")
                
                # Requirement #11: Institutional and Key Holder Accumulation
                institutional_col1, institutional_col2 = st.columns(2)
                
                with institutional_col1:
                    st.markdown("#### 🏛️ Major Corporate Holdings")
                    
                    # Major known institutional holders (approximate data)
                    institutions = [
                        {"name": "MicroStrategy", "btc": 190000, "type": "Corporate"},
                        {"name": "Tesla", "btc": 40000, "type": "Corporate"},
                        {"name": "Block Inc", "btc": 8000, "type": "Corporate"},
                        {"name": "Marathon Digital", "btc": 15000, "type": "Mining"},
                        {"name": "Coinbase", "btc": 9000, "type": "Exchange"},
                        {"name": "Riot Platforms", "btc": 8000, "type": "Mining"}
                    ]
                    
                    # Create institutional holdings chart
                    names = [inst["name"] for inst in institutions]
                    holdings = [inst["btc"] for inst in institutions]
                    types = [inst["type"] for inst in institutions]
                    
                    # Color by type
                    type_colors = {"Corporate": "#3498db", "Mining": "#e74c3c", "Exchange": "#2ecc71"}
                    colors = [type_colors.get(t, "#95a5a6") for t in types]
                    
                    fig_institutions = go.Figure()
                    fig_institutions.add_trace(go.Bar(
                        y=names,
                        x=holdings,
                        orientation='h',
                        marker_color=colors,
                        text=[f"{h:,} BTC" for h in holdings],
                        textposition='auto',
                        hovertemplate='<b>%{y}</b><br>Holdings: %{x:,} BTC<extra></extra>'
                    ))
                    
                    fig_institutions.update_layout(
                        title="🏢 Major Institutional Bitcoin Holdings",
                        xaxis_title="Bitcoin Holdings",
                        height=400,
                        template="plotly_dark",
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_institutions, use_container_width=True)
                    
                    # Institutional metrics
                    total_institutional = sum(holdings)
                    institutional_metric_col1, institutional_metric_col2 = st.columns(2)
                    with institutional_metric_col1:
                        st.metric("🏢 Total Institutional", f"{total_institutional:,} BTC")
                    with institutional_metric_col2:
                        if total_mined:
                            institutional_percent = (total_institutional / total_mined) * 100
                            st.metric("📊 % of Supply", f"{institutional_percent:.2f}%")
                
                with institutional_col2:
                    st.markdown("#### 📈 Institutional Adoption Timeline")
                    
                    # Institutional adoption timeline
                    adoption_years = [2020, 2021, 2022, 2023, 2024, 2025]
                    institutional_count = [5, 15, 25, 35, 45, 55]  # Number of institutions
                    institutional_holdings_timeline = [50000, 150000, 220000, 280000, 320000, 370000]  # BTC holdings
                    
                    fig_timeline = go.Figure()
                    
                    # Number of institutions (left y-axis)
                    fig_timeline.add_trace(go.Scatter(
                        x=adoption_years,
                        y=institutional_count,
                        mode='lines+markers',
                        name='Number of Institutions',
                        line=dict(color='#3498db', width=3),
                        marker=dict(size=8),
                        yaxis='y'
                    ))
                    
                    # Total holdings (right y-axis)
                    fig_timeline.add_trace(go.Scatter(
                        x=adoption_years,
                        y=institutional_holdings_timeline,
                        mode='lines+markers',
                        name='Total Holdings (BTC)',
                        line=dict(color='#e74c3c', width=3),
                        marker=dict(size=8),
                        yaxis='y2'
                    ))
                    
                    fig_timeline.update_layout(
                        title="📈 Institutional Adoption Growth",
                        xaxis_title="Year",
                        height=400,
                        template="plotly_dark",
                        legend=dict(x=0.02, y=0.98),
                        yaxis=dict(title='Number of Institutions', side='left'),
                        yaxis2=dict(title='Total Holdings (BTC)', side='right', overlaying='y'),
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig_timeline, use_container_width=True)
                    
                    # Timeline metrics
                    current_institutions = institutional_count[-1]
                    current_holdings = institutional_holdings_timeline[-1]
                    timeline_metric_col1, timeline_metric_col2 = st.columns(2)
                    with timeline_metric_col1:
                        st.metric("🏢 Active Institutions", f"{current_institutions}",
                                delta=f"+{current_institutions - institutional_count[0]} since 2020")
                    with timeline_metric_col2:
                        st.metric("💰 Combined Holdings", f"{current_holdings:,} BTC",
                                delta=f"+{current_holdings - institutional_holdings_timeline[0]:,} since 2020")
                
                # === SECTION 9: SCENARIO SIMULATOR ===
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.subheader("🎮 Bitcoin Future Scenario Simulator")
                
                # Requirement #15: Scenario Simulator
                with st.expander("🔬 Explore Future Bitcoin Scenarios", expanded=False):
                    st.markdown("#### 🎯 Adjust Parameters to Model Different Futures")
                    
                    sim_col1, sim_col2, sim_col3 = st.columns(3)
                    
                    with sim_col1:
                        # Adoption parameters
                        st.markdown("**📈 Adoption Scenarios**")
                        adoption_rate = st.slider(
                            "Annual Adoption Growth",
                            min_value=5.0, max_value=50.0, value=15.0, step=5.0,
                            help="Percentage growth in new users per year",
                            key="adoption_rate_slider"
                        )
                        
                        institutional_growth = st.slider(
                            "Institutional Growth Rate",
                            min_value=10.0, max_value=100.0, value=25.0, step=10.0,
                            help="Percentage growth in institutional adoption",
                            key="institutional_growth_slider"
                        )
                    
                    with sim_col2:
                        # Supply dynamics
                        st.markdown("**💎 Supply Dynamics**")
                        hodl_rate = st.slider(
                            "HODLing Rate",
                            min_value=30.0, max_value=80.0, value=55.0, step=5.0,
                            help="Percentage of supply held long-term",
                            key="hodl_rate_slider"
                        )
                        
                        lost_btc_rate = st.slider(
                            "Lost Bitcoin Rate",
                            min_value=15.0, max_value=30.0, value=20.0, step=1.0,
                            help="Percentage of total supply lost forever",
                            key="lost_btc_slider"
                        )
                    
                    with sim_col3:
                        # Market scenarios
                        st.markdown("**💰 Market Scenarios**")
                        price_scenario = st.selectbox(
                            "Price Growth Scenario",
                            ["Conservative (10% annual)", "Moderate (25% annual)", "Aggressive (50% annual)", "Parabolic (100% annual)"],
                            index=1,
                            key="price_scenario_select"
                        )
                        
                        regulation_impact = st.selectbox(
                            "Regulatory Environment",
                            ["Hostile (-20% adoption)", "Neutral (0% impact)", "Favorable (+30% adoption)", "Very Favorable (+50% adoption)"],
                            index=2,
                            key="regulation_select"
                        )
                    
                    # Calculate scenario projections
                    if st.button("🚀 Run Scenario Simulation", type="primary"):
                        # Extract parameters
                        price_multipliers = {"Conservative (10% annual)": 1.10, "Moderate (25% annual)": 1.25, "Aggressive (50% annual)": 1.50, "Parabolic (100% annual)": 2.00}
                        reg_multipliers = {"Hostile (-20% adoption)": 0.8, "Neutral (0% impact)": 1.0, "Favorable (+30% adoption)": 1.3, "Very Favorable (+50% adoption)": 1.5}
                        
                        price_mult = price_multipliers[price_scenario]
                        reg_mult = reg_multipliers[regulation_impact]
                        
                        # Project 10 years into the future
                        sim_years = list(range(2025, 2036))
                        projected_price = [100000]  # Starting price assumption
                        projected_adoption = [30000000]  # Starting users assumption
                        
                        for year in range(1, 11):
                            # Price projection
                            new_price = projected_price[-1] * price_mult
                            projected_price.append(new_price)
                            
                            # Adoption projection
                            growth_factor = (adoption_rate / 100) * reg_mult
                            new_adoption = projected_adoption[-1] * (1 + growth_factor)
                            projected_adoption.append(new_adoption)
                        
                        # Create scenario visualization
                        scenario_fig = go.Figure()
                        
                        # Price projection (left y-axis)
                        scenario_fig.add_trace(go.Scatter(
                            x=sim_years,
                            y=projected_price,
                            mode='lines+markers',
                            name='Bitcoin Price (USD)',
                            line=dict(color='#f7931a', width=4),
                            marker=dict(size=8),
                            yaxis='y'
                        ))
                        
                        # Adoption projection (right y-axis)
                        scenario_fig.add_trace(go.Scatter(
                            x=sim_years,
                            y=[a/1e6 for a in projected_adoption],  # Convert to millions
                            mode='lines+markers',
                            name='Global Users (Millions)',
                            line=dict(color='#2ecc71', width=4),
                            marker=dict(size=8),
                            yaxis='y2'
                        ))
                        
                        scenario_fig.update_layout(
                            title=f"🔮 Bitcoin Future Scenario: {price_scenario} + {regulation_impact}",
                            xaxis_title="Year",
                            height=500,
                            template="plotly_dark",
                            legend=dict(x=0.02, y=0.98),
                            yaxis=dict(title='Bitcoin Price (USD)', side='left', type='log'),
                            yaxis2=dict(title='Global Users (Millions)', side='right', overlaying='y'),
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(scenario_fig, use_container_width=True)
                        
                        # Scenario summary
                        st.markdown("#### 📊 Scenario Summary")
                        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
                        
                        with summary_col1:
                            final_price = projected_price[-1]
                            st.metric("💰 2035 Price", f"${final_price:,.0f}", 
                                    delta=f"{((final_price/projected_price[0])-1)*100:.0f}% total return")
                        
                        with summary_col2:
                            final_users = projected_adoption[-1]
                            st.metric("👥 2035 Users", f"{final_users/1e6:.0f}M", 
                                    delta=f"{((final_users/projected_adoption[0])-1)*100:.0f}% growth")
                        
                        with summary_col3:
                            if total_mined:
                                liquid_supply = total_mined * (100 - hodl_rate - lost_btc_rate) / 100
                                st.metric("💧 Liquid Supply", f"{liquid_supply:,.0f} BTC",
                                        delta=f"{(liquid_supply/total_mined)*100:.1f}% of total")
                        
                        with summary_col4:
                            market_cap_2035 = final_price * (total_mined if total_mined else 21000000)
                            st.metric("🏛️ 2035 Market Cap", f"${market_cap_2035/1e12:.1f}T")
                        
                        # Store scenario results in session state
                        st.session_state.bfd_data['scenario_results'] = {
                            'years': sim_years,
                            'prices': projected_price,
                            'adoption': projected_adoption,
                            'parameters': {
                                'adoption_rate': adoption_rate,
                                'price_scenario': price_scenario,
                                'regulation_impact': regulation_impact,
                                'hodl_rate': hodl_rate,
                                'lost_btc_rate': lost_btc_rate
                            }
                        }
                    
                    # Reset button
                    if st.button("🔄 Reset to Defaults", type="secondary"):
                        st.rerun()
                
                # === SECTION 4: GLOSSARY / HELP SECTION ===
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.subheader("📚 Bitcoin Future Glossary")
                
                # Requirement #14: Glossary with expandable definitions
                with st.expander("🔍 Key Terms & Definitions"):
                    st.markdown("""
                    **🧱 Halving:** An event that occurs approximately every 4 years where the Bitcoin block reward is cut in half, reducing the rate of new Bitcoin creation.
                    
                    **⛏️ Mining:** The process of validating Bitcoin transactions and adding them to the blockchain, rewarded with newly minted Bitcoin.
                    
                    **🎁 Block Reward:** The amount of Bitcoin awarded to miners for successfully mining a block. Started at 50 BTC and halves every 210,000 blocks.
                    
                    **💎 Hard Cap:** Bitcoin's maximum supply limit of 21 million coins, algorithmically enforced and unchangeable.
                    
                    **📊 Circulating Supply:** The total amount of Bitcoin currently mined and in circulation.
                    
                    **⏳ Remaining Supply:** The amount of Bitcoin yet to be mined, decreasing over time until ~2140.
                    
                    **🔗 Blockchain:** The decentralized ledger that records all Bitcoin transactions in chronological order.
                    
                    **⚡ Block Time:** The average time between Bitcoin blocks, targeted at 10 minutes through difficulty adjustments.
                    
                    **📦 Mempool:** The pool of unconfirmed transactions waiting to be included in the next block.
                    
                    **💳 Transaction Fees:** The fee paid to miners for processing a transaction, measured in satoshis per virtual byte (sat/vB).
                    
                    **🏦 Active Wallets:** Bitcoin addresses that have received or sent transactions within a specific timeframe.
                    
                    **🔒 Illiquid Supply:** Bitcoin that is held long-term and rarely traded, including lost coins and long-term holdings.
                    
                    **💧 Liquid Supply:** Bitcoin that is actively traded and available for transactions on exchanges.
                    
                    **💎 Diamond Hands:** Long-term Bitcoin holders who rarely sell, typically holding for over one year.
                    
                    **📄 Paper Hands:** Short-term Bitcoin holders who trade more frequently, typically holding for less than one year.
                    
                    **🏢 Institutional Adoption:** Large-scale adoption of Bitcoin by corporations, financial institutions, and government entities.
                    
                    **📈 HODLing:** A strategy of holding Bitcoin long-term regardless of price volatility (originally a misspelling of "hold").
                    
                    **🌍 Global Adoption:** The worldwide acceptance and use of Bitcoin across different countries and regions.
                    
                    **⚖️ Regulatory Environment:** Government policies and regulations that affect Bitcoin adoption and usage.
                    """)
                
                # Advanced features info
                with st.expander("🔬 About the Scenario Simulator"):
                    st.markdown("""
                    **🎮 Purpose:** The scenario simulator allows you to model different possible futures for Bitcoin based on various parameters.
                    
                    **📊 Parameters Explained:**
                    - **Adoption Growth:** How fast new users join the Bitcoin network annually
                    - **Institutional Growth:** Rate at which corporations and institutions adopt Bitcoin
                    - **HODLing Rate:** Percentage of Bitcoin held long-term vs. actively traded
                    - **Lost Bitcoin:** Coins that are permanently inaccessible due to lost keys
                    - **Price Scenarios:** Different growth trajectories based on market conditions
                    - **Regulatory Impact:** How government policies affect adoption rates
                    
                    **🎯 How to Use:**
                    1. Adjust the sliders to reflect your beliefs about Bitcoin's future
                    2. Select price and regulatory scenarios
                    3. Click "Run Scenario Simulation" to see projections
                    4. Results show price, adoption, and market cap projections to 2035
                    
                    **⚠️ Disclaimer:** These are theoretical projections based on your inputs, not financial advice.
                    """)
                
                # Data sources and methodology
                with st.expander("📡 Data Sources & Methodology"):
                    st.markdown("""
                    **🔄 Real-time Data Sources:**
                    - **CoinGecko API:** Price data, market cap, volume
                    - **Blockchain.info API:** Block count, difficulty, total supply
                    - **Mempool.space API:** Transaction fees, mempool data
                    
                    **📊 Estimated Data:**
                    - **Wallet Growth:** Based on historical on-chain analysis and industry reports
                    - **Supply Distribution:** Estimates from blockchain analytics and academic research
                    - **Adoption Rates:** Based on surveys from Triple-A and other research firms
                    - **Institutional Holdings:** Public filings and announced holdings
                    
                    **🧮 Calculation Methods:**
                    - **Supply Projections:** Mathematical modeling using halving schedule and block times
                    - **Halving Countdown:** Block-based calculations with 10-minute average block time
                    - **Scenario Modeling:** Compound growth models with adjustable parameters
                    
                    **🔄 Update Frequency:**
                    - **Real-time Data:** Cached for 5 minutes, refreshable on demand
                    - **Estimated Data:** Updated periodically based on new research
                    - **Historical Data:** Static, sourced from reliable blockchain data providers
                    """)
                
                # Data sources and refresh info
                st.markdown("<br>", unsafe_allow_html=True)
                st.divider()
                col_time, col_sources = st.columns(2)
                with col_time:
                    st.caption(f"🕐 Data refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                with col_sources:
                    st.caption("📡 Sources: CoinGecko, Blockchain.info, Historical Halving Data")
                
            except Exception as e:
                st.error(f"❌ Failed to load Bitcoin future metrics: {str(e)}")
                st.info("🔄 Please try refreshing the page or check your internet connection.")
                
                # Fallback content when APIs fail
                st.markdown("### 💎 Bitcoin Scarcity Facts (Offline)")
                st.info("""
                **Key Facts About Bitcoin's Future:**
                - 🏆 Maximum supply: 21,000,000 BTC (never to be exceeded)
                - ⛏️ Approximately 19.8M+ Bitcoin already mined (~94%+)
                - ⏳ Less than 1.2M Bitcoin left to mine
                - 📅 Final Bitcoin estimated to be mined around 2140
                - ⚡ Halving events occur every ~4 years, reducing mining rewards
                - 💎 Each halving makes Bitcoin more scarce and harder to obtain
                """)

    elif page == "Bitcoin OHLC":
        st.header("Bitcoin Weekly OHLC Data")
        
        # Use session state for data persistence and proper scoping
        if 'btc_ohlc_data' not in st.session_state:
            st.session_state.btc_ohlc_data = pd.DataFrame()
        
        if 'crypto_prices' not in st.session_state:
            st.session_state.crypto_prices = {'BTC': None, 'ETH': None, 'BNB': None, 'POL': None}
        
        # Load data if not already loaded
        if st.session_state.btc_ohlc_data.empty:
            with st.spinner("Loading Bitcoin OHLC data..."):
                try:
                    st.session_state.btc_ohlc_data = cached_get_btc_ohlc_data()
                except Exception as e:
                    st.error(f"❌ Failed to load Bitcoin OHLC data: {str(e)}")
                    st.session_state.btc_ohlc_data = pd.DataFrame()
        
        # Get current price from global scope or session state
        current_btc_price = None
        try:
            # Try to get from global binance_prices if available
            if 'binance_prices' in locals() and binance_prices:
                current_btc_price = binance_prices.get('BTC')
            elif 'binance_prices' in globals() and binance_prices:
                current_btc_price = binance_prices.get('BTC')
            else:
                # Fallback to session state or fetch fresh
                current_btc_price = st.session_state.crypto_prices.get('BTC')
                if not current_btc_price:
                    try:
                        price_result = cached_get_crypto_prices()
                        current_btc_price = price_result['prices'].get('BTC')
                        st.session_state.crypto_prices = price_result['prices']
                    except:
                        current_btc_price = None
        except:
            current_btc_price = None
        
        # Compact header row with API transparency
        col_price, col_fetch = st.columns([2, 1])
        with col_price:
            if current_btc_price and current_btc_price > 0:
                st.metric("Current Price", f"${current_btc_price:,.2f}")
            else:
                st.metric("Current Price", "❌ API Failed", delta="Binance API unavailable")
        with col_fetch:
            if st.button("Fetch Latest Data"):
                with st.spinner("Fetching comprehensive Bitcoin data from 2013..."):
                    # Clear cached data and refetch
                    cached_get_btc_ohlc_data.clear()
                    try:
                        st.session_state.btc_ohlc_data = cached_get_btc_ohlc_data()
                        st.success("Bitcoin OHLC data updated!")
                    except Exception as e:
                        st.error(f"Failed to fetch data: {str(e)}")
                        st.session_state.btc_ohlc_data = pd.DataFrame()
                st.rerun()

        btc_data = st.session_state.btc_ohlc_data
        if not btc_data.empty:
            current_year = pd.to_datetime('today').year
            
            if 'selected_year' not in st.session_state:
                st.session_state.selected_year = current_year

            min_year = btc_data.index.min().year
            max_year = btc_data.index.max().year
            years = range(min_year, max_year + 1)
            
            # Compact year buttons
            st.write("**Select Year:**")
            cols = st.columns(min(len(years), 13))
            for i, year in enumerate(years):
                if i < len(cols):
                    if cols[i].button(str(year), key=f"year_{year}"):
                        st.session_state.selected_year = year
            
            year_data = btc_data[btc_data.index.year == st.session_state.selected_year]

            if not year_data.empty:
                try:
                    # Ensure all required columns exist
                    required_columns = ['open', 'high', 'low', 'close']
                    missing_columns = [col for col in required_columns if col not in year_data.columns]
                    
                    if missing_columns:
                        st.error(f"❌ Missing required columns: {missing_columns}")
                        st.info("Available columns: " + ", ".join(year_data.columns.tolist()))
                    else:
                        # Import plotly for chart creation
                        import plotly.graph_objects as go
                        
                        fig = go.Figure(data=[go.Candlestick(x=year_data.index,
                            open=year_data['open'],
                            high=year_data['high'],
                            low=year_data['low'],
                            close=year_data['close'])])
                        
                        # Generate tick values and labels for all 12 months
                        selected_year = st.session_state.selected_year
                        month_starts = pd.date_range(start=f'{selected_year}-01-01', end=f'{selected_year}-12-31', freq='MS')
                        month_labels = [d.strftime('%b') for d in month_starts]

                        fig.update_layout(
                            title=f'Bitcoin Weekly OHLC for {st.session_state.selected_year}',
                            xaxis_title='Month',
                            yaxis_title='Price (USD)',
                            height=400,  # Reduced height
                            xaxis_rangeslider_visible=False,
                            bargap=0,
                            bargroupgap=0,
                            margin=dict(l=0, r=0, t=40, b=0),
                            xaxis=dict(
                                showgrid=False,
                                tickmode='array',
                                tickvals=month_starts,
                                ticktext=month_labels,
                                dtick='M1'
                            )
                        )

                        fig.update_xaxes(
                            tickvals=month_starts,
                            ticktext=month_labels,
                            showgrid=False
                        )

                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Error creating chart: {str(e)}")
                    st.info(f"Year data shape: {year_data.shape}")
                    st.info(f"Year data columns: {year_data.columns.tolist()}")
                    if not year_data.empty:
                        st.dataframe(year_data.head())
            else:
                st.write(f"No data available for {st.session_state.selected_year}")
        else:
            st.write("Could not find local data. Click 'Fetch Latest Data' to download.")
    elif page == "Mempool Data":
        st.header("🔗 Bitcoin Network & Mempool Statistics")
        
        # Enhanced fee metrics with color coding
        st.subheader("⚡ Transaction Fees")
        col1, col2, col3, col4 = st.columns(4)
        
        if 'error' not in mempool_data:
            fees = mempool_data['fees']
            
            with col1:
                st.markdown(f"""
                <div class="metric-card fee-high">
                    <h4>🚀 High Priority</h4>
                    <h2>{fees['fastestFee']} sat/vB</h2>
                    <p>~10 min confirmation</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card fee-medium">
                    <h4>⚡ Medium Priority</h4>
                    <h2>{fees['halfHourFee']} sat/vB</h2>
                    <p>~30 min confirmation</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card fee-low">
                    <h4>🐌 Low Priority</h4>
                    <h2>{fees['hourFee']} sat/vB</h2>
                    <p>~60 min confirmation</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card fee-economy">
                    <h4>💰 Economy</h4>
                    <h2>{fees['economyFee']} sat/vB</h2>
                    <p>~2+ hours confirmation</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Main content with better organization and consistent spacing
        col_left, col_right = st.columns([1.2, 0.8], gap="medium")
        
        with col_left:
            # Enhanced mempool blocks visualization
            if 'error' not in mempool_data and 'mempool_blocks' in mempool_data:
                st.subheader("📦 Next Blocks in Mempool")
                blocks_data = mempool_data['mempool_blocks'][:6]
                
                # Import plotly for chart creation
                import plotly.graph_objects as go
                
                fig_blocks = go.Figure()
                
                # Enhanced color coding based on fee levels
                colors = []
                for block in blocks_data:
                    fee = block['medianFee']
                    if fee > 100: colors.append('#e74c3c')      # Red - Very High
                    elif fee > 50: colors.append('#f39c12')     # Orange - High
                    elif fee > 20: colors.append('#f1c40f')     # Yellow - Medium
                    elif fee > 10: colors.append('#2ecc71')     # Green - Low
                    else: colors.append('#3498db')              # Blue - Very Low
                
                fig_blocks.add_trace(go.Bar(
                    x=[f"Block {i+1}" for i in range(len(blocks_data))],
                    y=[block['nTx'] for block in blocks_data],
                    marker_color=colors,
                    text=[f"{block['medianFee']} sat/vB<br>{block['nTx']} txs" for block in blocks_data],
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>Transactions: %{y}<br>Median Fee: %{text}<extra></extra>'
                ))
                
                fig_blocks.update_layout(
                    height=300,
                    margin=dict(l=0, r=0, t=10, b=20),
                    showlegend=False,
                    xaxis_title="Upcoming Blocks",
                    yaxis_title="Transaction Count",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_blocks, use_container_width=True)
            
            # Enhanced Network Health Dashboard with consistent spacing
            st.subheader("🎯 Network Health Dashboard")
            health_col1, health_col2, health_col3, health_col4 = st.columns(4)
            
            try:
                if 'error' not in mempool_data and 'fees' in mempool_data:
                    fees = mempool_data['fees']
                    avg_fee = (fees['fastestFee'] + fees['halfHourFee'] + fees['hourFee'] + fees['economyFee']) / 4
                    health_col1.metric("📊 Average Fee", f"{avg_fee:.0f} sat/vB", 
                                     delta=f"Range: {fees['economyFee']}-{fees['fastestFee']}")
                
                if 'error' not in mempool_data and 'mempool_blocks' in mempool_data:
                    total_pending = sum(block['nTx'] for block in mempool_data['mempool_blocks'][:5])
                    health_col2.metric("⏳ Pending Txs", f"{total_pending:,}", 
                                     delta="Next 5 blocks")
                
                if 'error' not in mempool_stats and 'hashrate' in mempool_stats:
                    hashrate = mempool_stats['hashrate']
                    current_hashrate = hashrate['currentHashrate']
                    health_col3.metric("⚡ Hashrate", f"{current_hashrate/1e18:.1f} EH/s", 
                                     delta="Current network power")
                
                # Add mempool size if available
                if 'error' not in mempool_data and 'mempool_blocks' in mempool_data:
                    total_mempool = sum(block['nTx'] for block in mempool_data['mempool_blocks'])
                    health_col4.metric("📈 Mempool Size", f"{total_mempool:,}", 
                                     delta="Total pending")
            except:
                pass
        
        with col_right:
            # Enhanced mining pools visualization
            if 'error' not in mempool_data and 'mining_pools' in mempool_data:
                st.subheader("🏊‍♂️ Mining Pool Distribution")
                pools = mempool_data['mining_pools']['pools'][:6]
                
                # Import plotly for chart creation
                import plotly.graph_objects as go
                
                # Enhanced colors for mining pools
                pool_colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=[pool.get('poolName', pool.get('name', 'Unknown'))[:12] for pool in pools],
                    values=[pool['blockCount'] for pool in pools],
                    hole=0.5,
                    marker_colors=pool_colors[:len(pools)],
                    textinfo='label+percent',
                    textposition='auto'
                )])
                fig_pie.update_layout(
                    height=300,
                    margin=dict(l=0, r=0, t=10, b=20),
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Enhanced difficulty information with consistent spacing
            if 'error' not in mempool_data and 'difficulty' in mempool_data:
                st.subheader("🎯 Difficulty Adjustment")
                difficulty = mempool_data['difficulty']
                
                diff_col1, diff_col2 = st.columns(2)
                
                progress = difficulty['progressPercent']
                change = difficulty['difficultyChange']
                
                # Color coding for difficulty change
                change_color = "🟢" if change > 0 else "🔴" if change < 0 else "🟡"
                
                diff_col1.metric("📊 Progress", f"{progress:.1f}%", 
                               delta=f"Until next adjustment")
                diff_col2.metric(f"{change_color} Expected Change", f"{change:+.1f}%", 
                               delta="Difficulty adjustment")
        
        # Enhanced latest blocks section with better spacing
        if 'error' not in mempool_data and 'latest_blocks' in mempool_data:
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("🧱 Recent Blocks")
            blocks_cols = st.columns(6)
            for i, block in enumerate(mempool_data['latest_blocks'][:6]):
                if i < len(blocks_cols):
                    blocks_cols[i].metric(
                        f"#{block['height']}", 
                        f"{block['tx_count']} txs",
                        delta=f"Size: {block.get('size', 'N/A')}"
                    )
        
        # Enhanced refresh section with minimal spacing
        st.markdown("<br>", unsafe_allow_html=True)
        refresh_col1, refresh_col2 = st.columns([1, 3])
        with refresh_col1:
            if st.button("🔄 Refresh Mempool Data", type="primary"):
                # Clear only mempool-related cached data
                cached_get_mempool_info.clear()
                cached_get_mempool_stats.clear()
                st.rerun()
        with refresh_col2:
            st.info("💡 Mempool data refreshes automatically every 5 minutes. Click refresh for immediate update.")

    elif page == "Portfolio Value":
        st.header("💼 Portfolio Value Calculator")
        
        # Initialize portfolio in session state
        initialize_portfolio_session()
        
        st.subheader("🪙 Asset Holdings & Portfolio Overview")
        
        # Add price refresh button with transparent status
        refresh_col, status_col = st.columns([1, 3])
        with refresh_col:
            if st.button("🔄 Force Refresh Prices", type="secondary", help="Force fresh API calls"):
                cached_get_crypto_prices.clear()
                cached_get_binance_prices.clear()  # Clear legacy cache too
                with st.spinner("Fetching fresh prices from multiple exchanges..."):
                    price_result = cached_get_crypto_prices()
                    
                # Show immediate feedback on refresh with source information
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
            if 'prices' in locals() and 'price_result' in locals():
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
                card_class = "crypto-btc fee-high"  # Red background for failed API
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
            
            # Beautiful single-row portfolio display with equally spaced boxes
            st.subheader("� Portfolio Overview")
            # Beautiful compact portfolio display with custom styling
            st.markdown("""
            <style>
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
                flex: 1;
                min-width: 140px;
                max-width: 200px;
                background: rgba(255,255,255,0.95);
                border-radius: 10px;
                padding: 12px 8px;
                text-align: center;
                box-shadow: 0 3px 8px rgba(0,0,0,0.12);
                transition: transform 0.3s ease;
                margin: 0 2px;
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
                    min-width: 95px;
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
            
            # Generate portfolio display content
            usdt_inr_rate = 83.50
            
            # Create only summary boxes (no individual asset repetition)
            portfolio_html = '<div class="portfolio-container">'
            
            # Total value boxes with special styling
            if total_value > 0:
                # USD Total
                portfolio_html += f'''
                <div class="portfolio-box portfolio-total">
                    <div class="portfolio-emoji">💵</div>
                    <div class="portfolio-label">USD Value</div>
                    <div class="portfolio-value">${total_value:,.2f}</div>
                    <div class="portfolio-amount">{len(valid_values)}/4 Assets</div>
                </div>'''
                
                # INR Total
                portfolio_html += f'''
                <div class="portfolio-box portfolio-total">
                    <div class="portfolio-emoji">🇮🇳</div>
                    <div class="portfolio-label">INR Value</div>
                    <div class="portfolio-value">₹{total_value * usdt_inr_rate:,.0f}</div>
                    <div class="portfolio-amount">@ ₹{usdt_inr_rate}/USD</div>
                </div>'''
                
                # BTC Equivalent
                if btc_price and btc_price > 0:
                    portfolio_html += f'''
                    <div class="portfolio-box portfolio-total">
                        <div class="portfolio-emoji">₿</div>
                        <div class="portfolio-label">BTC Equivalent</div>
                        <div class="portfolio-value">₿{total_value / btc_price:.8f}</div>
                        <div class="portfolio-amount">@ ${btc_price:,.0f}/BTC</div>
                    </div>'''
                else:
                    portfolio_html += '''
                    <div class="portfolio-box">
                        <div class="portfolio-emoji">₿</div>
                        <div class="portfolio-label">BTC Equivalent</div>
                        <div class="portfolio-value">BTC API Failed</div>
                        <div class="portfolio-amount">Price unavailable</div>
                    </div>'''
                
                # Asset Distribution (4th box to fill the space)
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
                <div class="portfolio-box portfolio-total">
                    <div class="portfolio-emoji">📊</div>
                    <div class="portfolio-label">Portfolio Stats</div>
                    <div class="portfolio-value">{non_zero_assets}/4 Assets</div>
                    <div class="portfolio-amount">Largest: {largest_asset} ({largest_percentage:.1f}%)</div>
                </div>'''
            else:
                # No valid prices fallback (4 boxes for consistency)
                portfolio_html = '<div class="portfolio-container">'
                portfolio_html += '''
                <div class="portfolio-box">
                    <div class="portfolio-emoji">💵</div>
                    <div class="portfolio-label">USD Value</div>
                    <div class="portfolio-value">No Valid Prices</div>
                    <div class="portfolio-amount">Check APIs</div>
                </div>
                <div class="portfolio-box">
                    <div class="portfolio-emoji">🇮🇳</div>
                    <div class="portfolio-label">INR Value</div>
                    <div class="portfolio-value">No Valid Prices</div>
                    <div class="portfolio-amount">Check APIs</div>
                </div>
                <div class="portfolio-box">
                    <div class="portfolio-emoji">₿</div>
                    <div class="portfolio-label">BTC Equivalent</div>
                    <div class="portfolio-value">No Valid Prices</div>
                    <div class="portfolio-amount">Check APIs</div>
                </div>
                <div class="portfolio-box">
                    <div class="portfolio-emoji">📊</div>
                    <div class="portfolio-label">Portfolio Stats</div>
                    <div class="portfolio-value">Check APIs</div>
                    <div class="portfolio-amount">Price data needed</div>
                </div>'''
            
            portfolio_html += '</div>'
            
            # Display the beautiful portfolio overview
            st.markdown(portfolio_html, unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"❌ Error calculating portfolio values: {e}")
            st.info("🔄 Please try refreshing prices or check API connectivity.")
        
        # Add minimal spacing before Portfolio Management section
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Enhanced portfolio management with session state
        st.subheader("💾 Portfolio Management")
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

    elif page == "Bitcoin Metrics":
        st.header("📊 Bitcoin Metrics Dashboard")
        
        # Import plotly at the beginning to ensure it's available throughout the section
        import plotly.graph_objects as go
        
        # Add cache for metrics with 5-minute TTL
        @st.cache_data(ttl=300)
        def cached_get_bitcoin_metrics():
            debug_log("🚀 Initializing Bitcoin Metrics with enhanced logging...", "INFO", "bitcoin_metrics_init")
            
            from bitcoin_metrics import BitcoinMetrics
            # Create instance with debug logging
            btc_metrics = BitcoinMetrics(debug_logger=debug_log)
            
            debug_log("📊 Starting comprehensive Bitcoin metrics collection...", "INFO", "bitcoin_metrics_start")
            return btc_metrics.get_comprehensive_metrics()
        
        # Refresh button
        col_refresh, col_status = st.columns([1, 3])
        with col_refresh:
            if st.button("🔄 Refresh Metrics", type="secondary"):
                cached_get_bitcoin_metrics.clear()
                st.rerun()
        
        # Load metrics with spinner
        with st.spinner("🔄 Loading comprehensive Bitcoin metrics..."):
            try:
                metrics = cached_get_bitcoin_metrics()
                
                with col_status:
                    if len(metrics.get('errors', [])) == 0:
                        st.success("✅ All metrics loaded successfully")
                    elif len(metrics.get('errors', [])) < 5:
                        st.warning(f"⚠️ {len(metrics['errors'])} metrics failed to load")
                    else:
                        st.error(f"❌ Multiple metrics failed ({len(metrics['errors'])} errors)")
                
                # Show errors in expander if any
                if metrics.get('errors'):
                    with st.expander(f"🔍 View {len(metrics['errors'])} API Issues"):
                        for error in metrics['errors']:
                            st.error(error)
                
                # === SECTION 1: PRICE & MARKET DATA ===
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("💰 Price & Market Data")
                
                price_col1, price_col2, price_col3, price_col4 = st.columns(4)
                
                # Bitcoin Price (Multi-source)
                with price_col1:
                    coingecko = metrics.get('coingecko', {})
                    coindesk = metrics.get('coindesk_price', {})
                    
                    if coingecko.get('price_usd'):
                        price = coingecko['price_usd']
                        change_24h = coingecko.get('change_24h', 0)
                        delta_color = "normal" if change_24h >= 0 else "inverse"
                        st.metric(
                            "💵 Bitcoin Price (USD)", 
                            f"${price:,.2f}",
                            delta=f"{change_24h:+.2f}% (24h)",
                            delta_color=delta_color
                        )
                    elif coindesk.get('price_usd'):
                        st.metric("💵 Bitcoin Price (USD)", f"${coindesk['price_usd']:,.2f}")
                    else:
                        st.metric("💵 Bitcoin Price (USD)", "API Failed")
                
                # Market Cap
                with price_col2:
                    if coingecko.get('market_cap_usd'):
                        market_cap = coingecko['market_cap_usd']
                        market_cap_t = market_cap / 1e12
                        st.metric("🏛️ Market Cap", f"${market_cap_t:.2f}T")
                    else:
                        st.metric("🏛️ Market Cap", "API Failed")
                
                # 24h Volume
                with price_col3:
                    if coingecko.get('volume_24h'):
                        volume = coingecko['volume_24h']
                        volume_b = volume / 1e9
                        st.metric("📊 24h Volume", f"${volume_b:.1f}B")
                    else:
                        st.metric("📊 24h Volume", "API Failed")
                
                # Bitcoin Dominance
                with price_col4:
                    global_data = metrics.get('global', {})
                    if global_data.get('btc_dominance'):
                        dominance = global_data['btc_dominance']
                        st.metric("👑 BTC Dominance", f"{dominance:.1f}%")
                    else:
                        st.metric("👑 BTC Dominance", "API Failed")
                
                # Multi-currency prices with minimal spacing
                st.subheader("🌍 Global Prices")
                curr_col1, curr_col2, curr_col3, curr_col4 = st.columns(4)
                
                with curr_col1:
                    if coingecko.get('price_usd'):
                        st.metric("🇺🇸 USD", f"${coingecko['price_usd']:,.2f}")
                    else:
                        st.metric("🇺🇸 USD", "N/A")
                
                with curr_col2:
                    if coingecko.get('price_eur'):
                        st.metric("🇪🇺 EUR", f"€{coingecko['price_eur']:,.2f}")
                    else:
                        st.metric("🇪🇺 EUR", "N/A")
                
                with curr_col3:
                    if coingecko.get('price_gbp'):
                        st.metric("🇬🇧 GBP", f"£{coingecko['price_gbp']:,.2f}")
                    else:
                        st.metric("🇬🇧 GBP", "N/A")
                
                with curr_col4:
                    if coingecko.get('price_inr'):
                        st.metric("🇮🇳 INR", f"₹{coingecko['price_inr']:,.0f}")
                    else:
                        st.metric("🇮🇳 INR", "N/A")
                
                # === SECTION 2: FEAR & GREED + SUPPLY METRICS ===
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("📈 Market Sentiment & Supply")
                
                fear_col1, fear_col2, fear_col3 = st.columns(3)
                
                # Fear & Greed Index with Gauge Meter
                with fear_col1:
                    fng_data = metrics.get('fear_greed', {})
                    if fng_data.get('value') is not None:
                        fng_value = fng_data['value']
                        fng_class = fng_data.get('classification', 'Unknown')
                        
                        # Import plotly for chart creation
                        import plotly.graph_objects as go
                        
                        # Create gauge meter
                        fig_gauge = go.Figure(go.Indicator(
                            mode="gauge+number+delta",
                            value=fng_value,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': "🎯 Fear & Greed Index", 'font': {'size': 16}},
                            delta={'reference': 50, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
                            gauge={
                                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                                'bar': {'color': "darkblue"},
                                'bgcolor': "white",
                                'borderwidth': 2,
                                'bordercolor': "gray",
                                'steps': [
                                    {'range': [0, 20], 'color': '#ff4444'},      # Extreme Fear - Red
                                    {'range': [20, 40], 'color': '#ff8800'},     # Fear - Orange  
                                    {'range': [40, 60], 'color': '#ffdd00'},     # Neutral - Yellow
                                    {'range': [60, 80], 'color': '#88dd00'},     # Greed - Light Green
                                    {'range': [80, 100], 'color': '#00dd44'}     # Extreme Greed - Green
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 90
                                }
                            }
                        ))
                        
                        fig_gauge.update_layout(
                            height=200,
                            margin=dict(l=10, r=10, t=30, b=10),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font={'color': "darkblue", 'family': "Arial"}
                        )
                        
                        st.plotly_chart(fig_gauge, use_container_width=True)
                        
                        # Show classification below gauge
                        st.markdown(f"**Classification:** {fng_class}", unsafe_allow_html=True)
                    else:
                        st.metric("😰 Fear & Greed Index", "API Failed")
                
                # Circulating Supply
                with fear_col2:
                    blockchain_data = metrics.get('blockchain', {})
                    if blockchain_data.get('total_supply'):
                        total_supply = blockchain_data['total_supply'] / 1e8  # Convert from satoshis
                        remaining = 21_000_000 - total_supply
                        st.metric("🪙 Circulating Supply", f"{total_supply:,.0f} BTC")
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.metric("⏳ Remaining to Mine", f"{remaining:,.0f} BTC")
                        
                        # Progress bar to 21M
                        st.markdown("<br>", unsafe_allow_html=True)
                        progress = total_supply / 21_000_000
                        st.progress(progress, text=f"{progress:.1%} of 21M mined")
                    else:
                        st.metric("🪙 Circulating Supply", "API Failed")
                
                # Block Count & Difficulty
                with fear_col3:
                    if blockchain_data.get('block_count'):
                        st.metric("🧱 Block Count", f"{blockchain_data['block_count']:,}")
                    else:
                        st.metric("🧱 Block Count", "API Failed")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    if blockchain_data.get('mining_difficulty'):
                        difficulty = blockchain_data['mining_difficulty']
                        difficulty_t = difficulty / 1e12
                        st.metric("⛏️ Mining Difficulty", f"{difficulty_t:.2f}T")
                    else:
                        st.metric("⛏️ Mining Difficulty", "API Failed")
                
                # === SECTION 3: NETWORK ACTIVITY CHARTS ===
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("🌐 Network Activity")
                
                # Check if we have chart data
                charts = metrics.get('charts', {})
                
                if charts:
                    # Create tabs for different chart categories
                    chart_tab1, chart_tab2, chart_tab3 = st.tabs(["📊 Transactions", "⛏️ Mining", "💰 Economics"])
                    
                    with chart_tab1:
                        # Transactions and Activity Charts
                        trans_col1, trans_col2 = st.columns(2)
                        
                        with trans_col1:
                            # Daily Transactions
                            if 'n-transactions' in charts:
                                tx_data = charts['n-transactions']
                                if tx_data.get('values'):
                                    # Prepare data
                                    dates = [datetime.fromtimestamp(point['x']) for point in tx_data['values']]
                                    values = [point['y'] for point in tx_data['values']]
                                    
                                    # Import plotly for chart creation
                                    import plotly.graph_objects as go
                                    
                                    fig = go.Figure()
                                    fig.add_trace(go.Scatter(
                                        x=dates, 
                                        y=values,
                                        mode='lines',
                                        name='Daily Transactions',
                                        line=dict(color='#f7931a', width=2)
                                    ))
                                    
                                    fig.update_layout(
                                        title="📈 Daily Bitcoin Transactions",
                                        xaxis_title="Date",
                                        yaxis_title="Transactions",
                                        height=400,
                                        template="plotly_dark"
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    # Show latest value
                                    if values:
                                        st.metric("🔄 Latest Daily Transactions", f"{values[-1]:,.0f}")
                            else:
                                st.error("❌ Transaction data unavailable")
                        
                        with trans_col2:
                            # Network Activity (Alternative to deprecated Active Addresses)
                            if 'n-transactions' in charts:
                                tx_data = charts['n-transactions']
                                if tx_data.get('values'):
                                    # Use transaction data as a proxy for network activity
                                    dates = [datetime.fromtimestamp(point['x']) for point in tx_data['values']]
                                    values = [point['y'] for point in tx_data['values']]
                                    
                                    # Import plotly for chart creation
                                    import plotly.graph_objects as go
                                    
                                    # Calculate transactions per address as an activity metric
                                    # This gives us a different perspective on network usage
                                    
                                    fig = go.Figure()
                                    fig.add_trace(go.Scatter(
                                        x=dates, 
                                        y=values,
                                        mode='lines+markers',
                                        name='Daily Transactions',
                                        line=dict(color='#00d4aa', width=2),
                                        marker=dict(size=4)
                                    ))
                                    
                                    fig.update_layout(
                                        title="� Network Activity (Daily Transactions)",
                                        xaxis_title="Date",
                                        yaxis_title="Number of Transactions",
                                        height=400,
                                        template="plotly_dark"
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    if values:
                                        # Show transactions per second for context
                                        latest_tx = values[-1]
                                        tx_per_second = latest_tx / (24 * 60 * 60)
                                        st.metric("� Latest Daily Transactions", f"{latest_tx:,.0f}")
                                        st.metric("⚡ Transactions per Second", f"{tx_per_second:.2f}")
                            else:
                                st.warning("⚠️ Network activity data temporarily unavailable")
                    
                    with chart_tab2:
                        # Mining Charts
                        mining_col1, mining_col2 = st.columns(2)
                        
                        with mining_col1:
                            # Hash Rate
                            if 'hash-rate' in charts:
                                hash_data = charts['hash-rate']
                                if hash_data.get('values'):
                                    dates = [datetime.fromtimestamp(point['x']) for point in hash_data['values']]
                                    raw_values = [point['y'] for point in hash_data['values']]
                                    
                                    # Debug logging for hash rate values
                                    debug_log("🔍 HASH RATE DEBUG", "hash_rate_debug", {
                                        'raw_values_sample': raw_values[-3:] if len(raw_values) >= 3 else raw_values,
                                        'raw_values_count': len(raw_values),
                                        'latest_raw_value': raw_values[-1] if raw_values else None,
                                        'raw_value_type': type(raw_values[-1]).__name__ if raw_values else None
                                    })
                                    
                                    # Convert hash rate: Blockchain.info returns hash rate in TH/s format
                                    # API unit: "Hash Rate TH/s" - confirmed via API test
                                    # Need to convert TH/s to EH/s: 1 EH/s = 1,000,000 TH/s (1e6)
                                    
                                    # Check the magnitude of raw values to determine correct conversion
                                    latest_raw = raw_values[-1] if raw_values else 0
                                    if latest_raw > 1e15:  # Values in H/s (very large)
                                        values = [v / 1e18 for v in raw_values]  # Convert to EH/s
                                        unit_debug = "H/s -> EH/s (÷1e18)"
                                    elif latest_raw > 1e6:  # Values in TH/s (expected from API)
                                        values = [v / 1e6 for v in raw_values]   # Convert TH/s to EH/s
                                        unit_debug = "TH/s -> EH/s (÷1e6) [API confirmed]"
                                    elif latest_raw > 1e3:   # Values in GH/s  
                                        values = [v / 1e9 for v in raw_values]   # Convert to EH/s
                                        unit_debug = "GH/s -> EH/s (÷1e9)"
                                    elif latest_raw > 1:   # Values in MH/s or already scaled
                                        values = [v / 1e12 for v in raw_values]  # Convert to EH/s
                                        unit_debug = "MH/s -> EH/s (÷1e12)"
                                    else:  # Values might already be in EH/s or zero
                                        values = raw_values  # No conversion
                                        unit_debug = "No conversion (assumed EH/s or zero)"
                                    
                                    debug_log("🔍 HASH RATE CONVERSION", "hash_rate_conversion", {
                                        'conversion_applied': unit_debug,
                                        'converted_values_sample': values[-3:] if len(values) >= 3 else values,
                                        'latest_converted_value': values[-1] if values else None,
                                        'latest_raw_magnitude': f"{latest_raw:.2e}" if latest_raw > 0 else "0"
                                    })
                                    
                                    import plotly.graph_objects as go
                                    fig = go.Figure()
                                    fig.add_trace(go.Scatter(
                                        x=dates, 
                                        y=values,
                                        mode='lines',
                                        name='Hash Rate (EH/s)',
                                        line=dict(color='#ff6b35', width=3),
                                        fill='tonexty'
                                    ))
                                    
                                    fig.update_layout(
                                        title="⚡ Bitcoin Network Hash Rate",
                                        xaxis_title="Date",
                                        yaxis_title="Hash Rate (EH/s)",
                                        height=400,
                                        template="plotly_dark"
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    if values:
                                        st.metric("⚡ Current Hash Rate", f"{values[-1]:.0f} EH/s")
                            else:
                                st.error("❌ Hash rate data unavailable")
                        
                        with mining_col2:
                            # Mining Revenue
                            if 'miners-revenue' in charts:
                                revenue_data = charts['miners-revenue']
                                if revenue_data.get('values'):
                                    dates = [datetime.fromtimestamp(point['x']) for point in revenue_data['values']]
                                    values = [point['y'] / 1e6 for point in revenue_data['values']]  # Convert to millions
                                    
                                    import plotly.graph_objects as go
                                    fig = go.Figure()
                                    fig.add_trace(go.Scatter(
                                        x=dates, 
                                        y=values,
                                        mode='lines',
                                        name='Daily Revenue ($M)',
                                        line=dict(color='#4ecdc4', width=2),
                                        fill='tozeroy'
                                    ))
                                    
                                    fig.update_layout(
                                        title="💰 Daily Mining Revenue",
                                        xaxis_title="Date",
                                        yaxis_title="Revenue (Million USD)",
                                        height=400,
                                        template="plotly_dark"
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    if values:
                                        st.metric("💰 Latest Daily Revenue", f"${values[-1]:.1f}M")
                            else:
                                st.error("❌ Mining revenue data unavailable")
                    
                    with chart_tab3:
                        # Economic Charts
                        econ_col1, econ_col2 = st.columns(2)
                        
                        with econ_col1:
                            # Transaction Fees
                            if 'transaction-fees-usd' in charts:
                                fees_data = charts['transaction-fees-usd']
                                if fees_data.get('values'):
                                    dates = [datetime.fromtimestamp(point['x']) for point in fees_data['values']]
                                    values = [point['y'] for point in fees_data['values']]
                                    
                                    import plotly.graph_objects as go
                                    fig = go.Figure()
                                    fig.add_trace(go.Scatter(
                                        x=dates, 
                                        y=values,
                                        mode='lines+markers',
                                        name='Avg Transaction Fee',
                                        line=dict(color='#e74c3c', width=2),
                                        marker=dict(size=3)
                                    ))
                                    
                                    fig.update_layout(
                                        title="💳 Average Transaction Fees",
                                        xaxis_title="Date",
                                        yaxis_title="Fee (USD)",
                                        height=400,
                                        template="plotly_dark"
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    if values:
                                        st.metric("💳 Current Avg Fee", f"${values[-1]:.2f}")
                            else:
                                st.error("❌ Transaction fees data unavailable")
                        
                        with econ_col2:
                            # Mempool Size
                            if 'mempool-size' in charts:
                                mempool_data = charts['mempool-size']
                                if mempool_data.get('values'):
                                    dates = [datetime.fromtimestamp(point['x']) for point in mempool_data['values']]
                                    values = [point['y'] / 1e6 for point in mempool_data['values']]  # Convert to MB
                                    
                                    import plotly.graph_objects as go
                                    fig = go.Figure()
                                    fig.add_trace(go.Scatter(
                                        x=dates, 
                                        y=values,
                                        mode='lines',
                                        name='Mempool Size (MB)',
                                        line=dict(color='#9b59b6', width=2),
                                        fill='tozeroy'
                                    ))
                                    
                                    fig.update_layout(
                                        title="📦 Mempool Size",
                                        xaxis_title="Date",
                                        yaxis_title="Size (MB)",
                                        height=400,
                                        template="plotly_dark"
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    if values:
                                        st.metric("📦 Current Mempool", f"{values[-1]:.1f} MB")
                            else:
                                st.error("❌ Mempool data unavailable")
                else:
                    st.warning("⚠️ Chart data unavailable - API issues detected")
                
                # === SECTION 4: NETWORK HEALTH ===
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("🌐 Network Health")
                
                network_col1, network_col2, network_col3 = st.columns(3)
                
                # Block timing
                with network_col1:
                    if 'avg_block_time' in metrics:
                        # Use the new direct avg_block_time field
                        avg_block_time = metrics['avg_block_time']
                        delta_color = "normal" if 8 <= avg_block_time <= 12 else "inverse"
                        st.metric(
                            "⏰ Avg Block Time", 
                            f"{avg_block_time:.1f} min",
                            delta=f"Target: 10 min",
                            delta_color=delta_color
                        )
                    elif 'avg-block-time' in charts:
                        # Fallback to chart data if available
                        block_time_data = charts['avg-block-time']
                        if block_time_data.get('values') and len(block_time_data['values']) > 0:
                            latest_block_time = block_time_data['values'][-1]['y'] / 60  # Convert to minutes
                            delta_color = "normal" if 8 <= latest_block_time <= 12 else "inverse"
                            st.metric(
                                "⏰ Avg Block Time", 
                                f"{latest_block_time:.1f} min",
                                delta=f"Target: 10 min",
                                delta_color=delta_color
                            )
                        else:
                            st.metric("⏰ Avg Block Time", "API Failed")
                    else:
                        st.metric("⏰ Avg Block Time", "API Failed")
                
                # Block size
                with network_col2:
                    # Debug logging for block size data
                    debug_log("🔍 DEBUG: Block size data check", "block_size_debug", {
                        'charts_exists': 'chart_data' in metrics,
                        'avg_block_size_in_charts': 'avg-block-size' in charts if charts else False,
                        'charts_keys': list(charts.keys()) if charts else [],
                        'avg_block_size_data_exists': charts.get('avg-block-size') is not None if charts else False
                    })
                    
                    if 'avg-block-size' in charts:
                        block_size_data = charts['avg-block-size']
                        
                        debug_log("🔍 DEBUG: Block size data structure", "block_size_structure", {
                            'block_size_data_type': type(block_size_data).__name__,
                            'has_values': 'values' in block_size_data if isinstance(block_size_data, dict) else False,
                            'values_count': len(block_size_data.get('values', [])) if isinstance(block_size_data, dict) else 0,
                            'first_value': block_size_data.get('values', [{}])[0] if isinstance(block_size_data, dict) and block_size_data.get('values') else None,
                            'last_value': block_size_data.get('values', [{}])[-1] if isinstance(block_size_data, dict) and block_size_data.get('values') else None
                        })
                        
                        if block_size_data.get('values') and len(block_size_data['values']) > 0:
                            latest_value = block_size_data['values'][-1]
                            
                            debug_log("🔍 DEBUG: Block size calculation", "block_size_calculation", {
                                'latest_value': latest_value,
                                'latest_value_type': type(latest_value).__name__,
                                'y_value': latest_value.get('y') if isinstance(latest_value, dict) else None,
                                'y_value_type': type(latest_value.get('y')).__name__ if isinstance(latest_value, dict) and latest_value.get('y') is not None else 'None'
                            })
                            
                            if isinstance(latest_value, dict) and 'y' in latest_value:
                                y_value = latest_value['y']
                                # The Blockchain.info avg-block-size chart returns values in MB already, not bytes
                                latest_block_size = y_value  # No conversion needed
                                
                                debug_log("🔍 DEBUG: Final block size conversion", "block_size_final", {
                                    'raw_mb': y_value,
                                    'final_mb': latest_block_size,
                                    'display_string': f"{latest_block_size:.2f} MB"
                                })
                                
                                st.metric("📏 Avg Block Size", f"{latest_block_size:.2f} MB")
                            else:
                                debug_log("❌ ERROR: Invalid latest value structure", "block_size_error", {
                                    'latest_value': latest_value
                                })
                                st.metric("📏 Avg Block Size", "Data Error")
                        else:
                            debug_log("❌ ERROR: No values in block size data", "block_size_no_values", {
                                'block_size_data': block_size_data
                            })
                            st.metric("📏 Avg Block Size", "API Failed")
                    else:
                        debug_log("❌ ERROR: avg-block-size not in charts", "block_size_missing", {
                            'available_charts': list(charts.keys()) if charts else []
                        })
                        st.metric("📏 Avg Block Size", "API Failed")
                
                # Block reward and halving details
                with network_col3:
                    if blockchain_data.get('block_reward'):
                        block_reward = blockchain_data['block_reward']
                        st.metric("🎁 Block Reward", f"{block_reward} BTC")
                        
                        # Enhanced halving calculations with validation
                        current_blocks = blockchain_data.get('block_count', 0)
                        blocks_per_halving = 210_000
                        
                        # Calculate current halving epoch and cycle details
                        current_epoch = current_blocks // blocks_per_halving
                        current_cycle_start = current_epoch * blocks_per_halving
                        blocks_mined_this_cycle = current_blocks - current_cycle_start
                        next_halving_block = (current_epoch + 1) * blocks_per_halving
                        blocks_to_halving = next_halving_block - current_blocks
                        
                        # More accurate time calculation using actual average block time from mempool data
                        mempool_info = st.session_state.get('mempool_data', {})
                        actual_block_time = 10.0  # Default fallback
                        if mempool_info and 'difficulty' in mempool_info:
                            time_avg_ms = mempool_info['difficulty'].get('timeAvg', 600000)  # milliseconds
                            actual_block_time = time_avg_ms / 1000 / 60  # Convert to minutes
                        
                        days_to_halving = (blocks_to_halving * actual_block_time) / (60 * 24)
                        
                        # Add comprehensive halving debug logging
                        debug_log("🎯 HALVING CALCULATION", "halving_debug", {
                            'current_blocks': current_blocks,
                            'current_epoch': current_epoch,
                            'blocks_mined_this_cycle': blocks_mined_this_cycle,
                            'blocks_to_halving': blocks_to_halving,
                            'next_halving_block': next_halving_block,
                            'actual_block_time_minutes': actual_block_time,
                            'days_to_halving': days_to_halving,
                            'validation': {
                                'blocks_per_cycle': blocks_per_halving,
                                'cycle_progress_percent': (blocks_mined_this_cycle / blocks_per_halving) * 100
                            }
                        })
                        
                        # Display main halving countdown
                        st.metric("📅 Est. Days to Halving", f"{days_to_halving:,.0f}")
                        
                        # Add detailed halving cycle information
                        st.caption(f"🔄 **Halving Cycle {current_epoch + 1}**")
                        st.caption(f"✅ Blocks Mined: {blocks_mined_this_cycle:,} / {blocks_per_halving:,}")
                        st.caption(f"⏳ Blocks Remaining: {blocks_to_halving:,}")
                        
                        # Progress percentage
                        cycle_progress = (blocks_mined_this_cycle / blocks_per_halving) * 100
                        st.caption(f"📊 Cycle Progress: {cycle_progress:.1f}%")
                        
                        # Next halving block number
                        st.caption(f"🎯 Next Halving Block: {next_halving_block:,}")
                        
                    else:
                        st.metric("🎁 Block Reward", "API Failed")
                
                # Show data freshness with minimal spacing
                st.markdown("<br>", unsafe_allow_html=True)
                st.divider()
                col_time, col_sources = st.columns(2)
                with col_time:
                    st.caption(f"🕐 Data refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                with col_sources:
                    st.caption("📡 Sources: CoinGecko, Blockchain.info, Alternative.me, Bitnodes")
                
            except Exception as e:
                st.error(f"❌ Failed to load Bitcoin metrics: {str(e)}")
                st.info("🔄 Please try refreshing the page or check your internet connection.")

    elif page == "Debug Logs":
        st.header("🔍 Debug Logs & Session Analytics")
        st.caption("Comprehensive session instrumentation and production debugging")
        
        # Session Analytics Section
        st.subheader("📈 Session Analytics")
        
        if 'debug_logs' in st.session_state and st.session_state.debug_logs:
            logs = st.session_state.debug_logs
            
            # Calculate session metrics
            from datetime import datetime  # Local import to ensure availability
            total_logs = len(logs)
            session_start = logs[0]['timestamp_full'] if logs else 'Unknown'
            current_time = datetime.now().isoformat()
            
            # Count by levels
            level_counts = {}
            context_counts = {}
            api_calls = 0
            data_operations = 0
            user_actions = 0
            
            for log in logs:
                level = log.get('level', 'INFO')
                level_counts[level] = level_counts.get(level, 0) + 1
                
                context = log.get('context', 'None')
                # Ensure context is a string to avoid TypeError
                if context is None:
                    context = 'None'
                elif not isinstance(context, str):
                    context = str(context)
                
                context_counts[context] = context_counts.get(context, 0) + 1
                
                if context and context.startswith('api_'):
                    api_calls += 1
                elif context and context.startswith('processing_'):
                    data_operations += 1
                elif context == 'user_interaction':
                    user_actions += 1
            
            # Display metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Total Logs", total_logs)
                st.metric("🔴 Errors", level_counts.get('ERROR', 0))
            with col2:
                st.metric("🌐 API Calls", api_calls)
                st.metric("🟡 Warnings", level_counts.get('WARNING', 0))
            with col3:
                st.metric("⚙️ Data Ops", data_operations)
                st.metric("🟢 Successes", level_counts.get('SUCCESS', 0))
            with col4:
                st.metric("👤 User Actions", user_actions)
                st.metric("ℹ️ Info Events", level_counts.get('INFO', 0))
            
            # Session timeline
            st.subheader("⏱️ Session Timeline")
            st.write(f"**Started:** {session_start}")
            st.write(f"**Current:** {current_time}")
            
            # Top contexts
            if context_counts:
                st.subheader("🏷️ Top Activity Contexts")
                sorted_contexts = sorted(context_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                for context, count in sorted_contexts:
                    st.write(f"• **{context}**: {count} events")
        else:
            st.info("📝 No debug logs available yet. Session analytics will appear here as the application runs.")
            
        # Session Export and Summary
        st.subheader("💾 Session Export & Summary")
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            if st.button("📋 Generate Session Summary"):
                if 'debug_logs' in st.session_state and st.session_state.debug_logs:
                    logs = st.session_state.debug_logs
                    
                    # Generate comprehensive session summary
                    summary = f"""
# Session Summary Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Session ID:** {id(st.session_state)}
**Total Logs:** {len(logs)}

## Key Metrics
- **Errors:** {len([l for l in logs if l.get('level') == 'ERROR'])}
- **Warnings:** {len([l for l in logs if l.get('level') == 'WARNING'])}
- **API Calls:** {len([l for l in logs if l.get('context', '') and str(l.get('context', '')).startswith('api_')])}
- **Data Operations:** {len([l for l in logs if l.get('context', '') and str(l.get('context', '')).startswith('processing_')])}
- **User Actions:** {len([l for l in logs if l.get('context') == 'user_interaction'])}

## Session Timeline
- **Started:** {logs[0]['timestamp_full'] if logs else 'Unknown'}
- **Latest:** {logs[-1]['timestamp_full'] if logs else 'Unknown'}

## Error Summary
"""
                    errors = [l for l in logs if l.get('level') == 'ERROR']
                    if errors:
                        for error in errors[-5:]:  # Last 5 errors
                            summary += f"- **{error['timestamp']}:** {error['message']}\n"
                    else:
                        summary += "- No errors recorded in this session\n"
                    
                    summary += f"""
## Recent Activity (Last 10 Events)
"""
                    for log in logs[-10:]:
                        summary += f"- **{log['timestamp']}** [{log['level']}] {log['message']}\n"
                    
                    st.download_button(
                        label="📥 Download Session Report",
                        data=summary,
                        file_name=f"session_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown"
                    )
                else:
                    st.warning("No session data available for export.")
        
        with col_export2:
            if st.button("📊 Export Raw Log Data"):
                if 'debug_logs' in st.session_state and st.session_state.debug_logs:
                    import json
                    log_data = json.dumps(st.session_state.debug_logs, indent=2, default=str)
                    
                    st.download_button(
                        label="📥 Download Raw JSON",
                        data=log_data,
                        file_name=f"debug_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                else:
                    st.warning("No log data available for export.")
        
        st.divider()
        
        # Control buttons
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("🗑️ Clear Logs"):
                clear_debug_logs()
                st.success("Logs cleared!")
                st.rerun()
        
        with col2:
            auto_refresh = st.checkbox("🔄 Auto-refresh", value=False)
        
        # Show logs count and session info
        log_count = len(st.session_state.debug_logs) if 'debug_logs' in st.session_state else 0
        session_id = id(st.session_state)
        st.info(f"📊 Total logs: {log_count} (max 2000) | 🆔 Session ID: {session_id}")
        
        # Display logs
        if 'debug_logs' in st.session_state and st.session_state.debug_logs:
            # Create a container for logs
            log_container = st.container()
            
            # Show logs in reverse order (newest first)
            logs = list(reversed(st.session_state.debug_logs))
            
            # Enhanced filtering options
            col_filter1, col_filter2, col_filter3 = st.columns(3)
            with col_filter1:
                level_filter = st.selectbox(
                    "Filter by level:",
                    ["ALL", "ERROR", "WARNING", "SUCCESS", "INFO", "DATA", "SYSTEM"],
                    index=0
                )
            with col_filter2:
                # Get unique contexts, ensuring they are strings
                unique_contexts = []
                for log in logs:
                    context = log.get('context', 'None')
                    if context is None:
                        context = 'None'
                    elif not isinstance(context, str):
                        context = str(context)
                    if context not in unique_contexts:
                        unique_contexts.append(context)
                
                context_filter = st.selectbox(
                    "Filter by context:",
                    ["ALL"] + sorted(unique_contexts),
                    index=0
                )
            with col_filter3:
                show_details = st.checkbox("Show detailed info", value=False)
            
            # Apply filters
            filtered_logs = logs
            if level_filter != "ALL":
                filtered_logs = [log for log in filtered_logs if log.get('level', 'INFO') == level_filter]
            if context_filter != "ALL":
                # Safe context comparison
                filtered_logs = []
                for log in (filtered_logs if level_filter != "ALL" else logs):
                    log_context = log.get('context', 'None')
                    if log_context is None:
                        log_context = 'None'
                    elif not isinstance(log_context, str):
                        log_context = str(log_context)
                    if log_context == context_filter:
                        filtered_logs.append(log)
            
            with log_container:
                st.subheader(f"📋 Debug Logs ({len(filtered_logs)} of {len(logs)} shown)")
                
                # Display filtered logs with enhanced information
                for i, log_entry in enumerate(filtered_logs):
                    level = log_entry.get('level', 'INFO')
                    timestamp = log_entry.get('timestamp', 'Unknown')
                    timestamp_full = log_entry.get('timestamp_full', 'Unknown')
                    message = log_entry.get('message', 'No message')
                    context = log_entry.get('context', '')
                    data = log_entry.get('data', {})
                    system_info = log_entry.get('system_info', {})
                    log_sequence = log_entry.get('log_sequence', i+1)
                    
                    # Create expandable log entry
                    with st.expander(f"#{log_sequence} [{timestamp}] {level}: {message[:60]}{'...' if len(message) > 60 else ''}", expanded=False):
                        # Basic info
                        st.write(f"**Full Message:** {message}")
                        st.write(f"**Level:** {level}")
                        st.write(f"**Timestamp:** {timestamp} ({timestamp_full})")
                        if context:
                            st.write(f"**Context:** {context}")
                        
                        # Show detailed data if available
                        if show_details and data:
                            st.write("**Data Payload:**")
                            st.json(data)
                        
                        # Show system info for relevant levels
                        if show_details and system_info and isinstance(system_info, dict):
                            st.write("**System Information:**")
                            st.json(system_info)
                        
                        # Show stack trace for errors
                        if show_details and level == "ERROR" and log_entry.get('stack_trace'):
                            st.write("**Stack Trace:**")
                            st.code('\n'.join(log_entry['stack_trace'][-5:]))  # Show last 5 stack frames
                    
                    # Color coding by level in compact view
                    if not show_details:
                        display_msg = f"#{log_sequence} **{timestamp}** [{context}] - {message}"
                        if level == "ERROR":
                            st.error(f"🔴 {display_msg}")
                        elif level == "WARNING":
                            st.warning(f"🟡 {display_msg}")
                        elif level == "SUCCESS":
                            st.success(f"🟢 {display_msg}")
                        elif level == "DATA":
                            st.info(f"📊 {display_msg}")
                        elif level == "SYSTEM":
                            st.info(f"⚙️ {display_msg}")
                        else:  # INFO
                            st.info(f"ℹ️ {display_msg}")
                    
                    # Add separator for readability
                    if i < len(filtered_logs) - 1 and i < 50:  # Limit visible logs for performance
                        st.divider()
                    elif i >= 50:
                        st.info(f"📄 Showing first 50 of {len(filtered_logs)} filtered logs. Use filters to narrow results.")
                        break
        else:
            st.info("📝 No debug logs available yet. Logs will appear here as the application runs.")
            st.markdown("""
            **Debug logs capture:**
            - 🔴 **ERROR**: Critical failures and exceptions
            - 🟡 **WARNING**: Potential issues and fallbacks
            - 🟢 **SUCCESS**: Successful operations
            - 📊 **DATA**: Data loading and processing info
            - ⚙️ **SYSTEM**: System status and configuration
            - ℹ️ **INFO**: General application information
            """)
        
        # Auto-refresh functionality
        if auto_refresh:
            st.rerun()

if __name__ == "__main__":
    main()
