"""
A Streamlit application to display cryptocurrency data.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime
from bitfinex_data import get_btc_ohlc_data, fetch_and_update_data
from mempool_data import get_mempool_info, get_mempool_stats
from binance_data import get_binance_price

# Cache API calls for 5 minutes
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
    # Use session state to check debug mode
    debug_mode = getattr(st.session_state, 'debug_mode', True)
    
    if debug_mode:
        st.write("🔍 **DEBUG**: Starting multi-exchange price fetch...")
    
    try:
        from multi_exchange import get_multi_exchange_prices
        
        if debug_mode:
            st.write("✅ **DEBUG**: Successfully imported multi_exchange module")
        
        print("🔄 Starting multi-exchange price fetch...")
        if debug_mode:
            st.write("🔄 **DEBUG**: Calling get_multi_exchange_prices()...")
        
        result = get_multi_exchange_prices()
        
        if debug_mode:
            st.write(f"📊 **DEBUG**: Multi-exchange result received:")
            st.write(f"- Success count: {result.get('success_count', 'MISSING')}")
            st.write(f"- Total count: {result.get('total_count', 'MISSING')}")
            st.write(f"- Sources used: {result.get('sources_used', 'MISSING')}")
            st.write(f"- Errors count: {len(result.get('errors', []))}")
            st.write(f"- Prices keys: {list(result.get('prices', {}).keys())}")
            
            # Log each price individually
            prices = result.get('prices', {})
            for symbol, price in prices.items():
                st.write(f"- {symbol}: {price} (type: {type(price)})")
        
        # Add source information to the result
        if result.get('sources_used'):
            sources_info = f"📡 Data sources: {', '.join(result['sources_used'])}"
            print(sources_info)
            if debug_mode:
                st.write(f"📡 **DEBUG**: {sources_info}")
            
            # Add this info to errors for user visibility
            if 'sources_info' not in result:
                result['sources_info'] = sources_info
        
        if debug_mode:
            st.write("✅ **DEBUG**: Multi-exchange fetch completed successfully")
        return result
            
    except Exception as e:
        error_msg = f"❌ Critical error in multi-exchange price fetching: {str(e)}"
        print(error_msg)
        if debug_mode:
            st.error(f"🚨 **DEBUG ERROR**: {error_msg}")
            st.write(f"📋 **DEBUG**: Exception type: {type(e)}")
            st.write(f"📋 **DEBUG**: Exception details: {repr(e)}")
            
            # Try to get more details about the import error
            try:
                import multi_exchange
                st.write("✅ **DEBUG**: multi_exchange module import successful")
            except Exception as import_err:
                st.error(f"❌ **DEBUG**: multi_exchange import failed: {import_err}")
        
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
    """Main function to run the Streamlit app."""
    st.set_page_config(
        page_title="Bitcoin Crypto Dashboard",
        page_icon="₿",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize portfolio session state
    initialize_portfolio_session()
    
    # DEBUG MODE TOGGLE (for production debugging)
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = True  # Enable debug by default for Community Cloud debugging
    
    # Add debug toggle in sidebar (will be added later after sidebar creation)
    
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
        debug_mode = st.session_state.get('debug_mode', True)
        
        if debug_mode:
            st.write("🔍 **DEBUG**: Starting data loading process...")
        
        try:
            if debug_mode:
                st.write("🔍 **DEBUG**: Clearing price caches...")
            
            # Force fresh API calls - clear cache first
            cached_get_crypto_prices.clear()  # Use new function name
            cached_get_binance_prices.clear()  # Clear legacy cache too
            
            if debug_mode:
                st.write("✅ **DEBUG**: Caches cleared successfully")
            
            if debug_mode:
                st.write("🔍 **DEBUG**: Loading mempool data...")
            mempool_data = cached_get_mempool_info()
            if debug_mode:
                st.write(f"📊 **DEBUG**: Mempool data type: {type(mempool_data)}")
            
            if debug_mode:
                st.write("🔍 **DEBUG**: Loading mempool stats...")
            mempool_stats = cached_get_mempool_stats()
            if debug_mode:
                st.write(f"📊 **DEBUG**: Mempool stats type: {type(mempool_stats)}")
            
            if debug_mode:
                st.write("🔍 **DEBUG**: Loading price data with multi-exchange system...")
            price_result = cached_get_crypto_prices()  # Use multi-exchange system
            if debug_mode:
                st.write(f"📊 **DEBUG**: Price result type: {type(price_result)}")
                st.write(f"📊 **DEBUG**: Price result keys: {list(price_result.keys()) if isinstance(price_result, dict) else 'NOT A DICT'}")
            
            if debug_mode:
                st.write("🔍 **DEBUG**: Loading BTC OHLC data...")
            btc_data = cached_get_btc_ohlc_data()
            if debug_mode:
                st.write(f"📊 **DEBUG**: BTC data type: {type(btc_data)}")
            
            # Extract price data and show transparent status
            if debug_mode:
                st.write("🔍 **DEBUG**: Extracting price data from result...")
            binance_prices = price_result['prices']  # Keep variable name for compatibility
            price_errors = price_result['errors']
            success_rate = f"{price_result['success_count']}/{price_result['total_count']}"
            sources_used = price_result.get('sources_used', [])
            
            if debug_mode:
                st.write(f"📊 **DEBUG**: Extracted data:")
                st.write(f"- binance_prices: {binance_prices}")
                st.write(f"- price_errors: {price_errors}")
                st.write(f"- success_rate: {success_rate}")
                st.write(f"- sources_used: {sources_used}")
            
            # Show API status to user with detailed information including sources
            if price_result['success_count'] == price_result['total_count']:
                sources_text = f" via {', '.join(sources_used)}" if sources_used else ""
                st.success(f"✅ All price APIs successful ({success_rate}){sources_text}")
            elif price_result['success_count'] > 0:
                sources_text = f" via {', '.join(sources_used)}" if sources_used else ""
                st.warning(f"⚠️ Partial API success ({success_rate}){sources_text} - Some prices may be unavailable")
                with st.expander("🔍 View API Issues"):
                    for error in price_errors:
                        st.error(error)
            else:
                st.error(f"❌ All price APIs failed ({success_rate}) - No live prices available")
                with st.expander("🔍 View All API Errors"):
                    for error in price_errors:
                        st.error(error)
                    st.info("💡 Try refreshing the page or using the 'Refresh Prices' button in Portfolio section")
            
            if debug_mode:
                st.write("✅ **DEBUG**: Data loading completed successfully")
                
        except Exception as e:
            st.error(f"❌ Critical error loading data: {e}")
            st.error(f"🚨 **DEBUG ERROR**: Exception type: {type(e)}")
            st.error(f"🚨 **DEBUG ERROR**: Exception details: {repr(e)}")
            st.error(f"🚨 **DEBUG ERROR**: Exception args: {e.args}")
            
            # Try to get traceback
            import traceback
            tb = traceback.format_exc()
            st.error(f"🚨 **DEBUG TRACEBACK**:")
            st.code(tb)
            
            st.info("🔄 Please refresh the page to retry data loading.")
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
        "Bitcoin OHLC",
        "Mempool Data",
        "Portfolio Value",
        "Bitcoin Metrics",
    ]
    page = st.sidebar.radio("Go to", tabs)
    
    # Add debug toggle in sidebar
    st.sidebar.divider()
    debug_toggle = st.sidebar.checkbox("🔍 Production Debug", value=st.session_state.debug_mode, help="Show detailed logs for Community Cloud debugging")
    st.session_state.debug_mode = debug_toggle
    if debug_toggle:
        st.sidebar.warning("⚠️ Debug mode ON")
    st.sidebar.divider()

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
        
        # Add some Bitcoin stats using cached data with API transparency
        st.subheader("📊 Live Bitcoin Metrics")
        
        if binance_prices.get('BTC') and binance_prices['BTC'] > 0:
            metrics_cols = st.columns(3)
            
            try:
                current_btc_price = binance_prices['BTC']
                metrics_cols[0].metric("Current Price", f"${current_btc_price:,.2f}")
                
                # Calculate market cap with more accurate circulating supply (as of 2025)
                circulating_supply = 19_800_000  # More accurate current circulating supply
                market_cap = current_btc_price * circulating_supply
                metrics_cols[1].metric("Market Cap", f"${market_cap/1e12:.2f}T")
                
                # Show accurate scarcity - much less remaining now
                remaining_btc = 21_000_000 - circulating_supply
                metrics_cols[2].metric("Remaining to Mine", f"{remaining_btc:,.0f} BTC")
                
            except Exception as e:
                st.error(f"❌ Error calculating Bitcoin metrics: {e}")
        else:
            st.error("❌ Bitcoin Price API Failed")
            st.info("💡 Live Bitcoin metrics unavailable due to API failure. The price data from Binance API could not be retrieved.")
            
            # Show a retry button
            if st.button("🔄 Retry Bitcoin Price API", key="retry_btc_main"):
                cached_get_crypto_prices.clear()
                cached_get_binance_prices.clear()
                st.rerun()

    elif page == "Bitcoin OHLC":
        st.header("Bitcoin Weekly OHLC Data")
        
        # Compact header row with API transparency
        col_price, col_fetch = st.columns([2, 1])
        with col_price:
            current_btc_price = binance_prices.get('BTC')
            if current_btc_price and current_btc_price > 0:
                st.metric("Current Price", f"${current_btc_price:,.2f}")
            else:
                st.metric("Current Price", "❌ API Failed", delta="Binance API unavailable")
        with col_fetch:
            if st.button("Fetch Latest Data"):
                with st.spinner("Fetching comprehensive Bitcoin data from 2013..."):
                    # Clear only OHLC cached data
                    cached_get_btc_ohlc_data.clear()
                    fetch_and_update_data()
                st.success("Bitcoin OHLC data updated!")
                st.rerun()

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
        
        # Main content with better organization
        col_left, col_right = st.columns([1.2, 0.8])
        
        with col_left:
            # Enhanced mempool blocks visualization
            if 'error' not in mempool_data and 'mempool_blocks' in mempool_data:
                st.subheader("📦 Next Blocks in Mempool")
                blocks_data = mempool_data['mempool_blocks'][:6]
                
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
                    height=280,
                    margin=dict(l=0, r=0, t=20, b=0),
                    showlegend=False,
                    xaxis_title="Upcoming Blocks",
                    yaxis_title="Transaction Count",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_blocks, use_container_width=True)
            
            # Enhanced Network Health Dashboard
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
                    margin=dict(l=0, r=0, t=20, b=0),
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Enhanced difficulty information
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
        
        # Enhanced latest blocks section
        if 'error' not in mempool_data and 'latest_blocks' in mempool_data:
            st.subheader("🧱 Recent Blocks")
            blocks_cols = st.columns(6)
            for i, block in enumerate(mempool_data['latest_blocks'][:6]):
                if i < len(blocks_cols):
                    blocks_cols[i].metric(
                        f"#{block['height']}", 
                        f"{block['tx_count']} txs",
                        delta=f"Size: {block.get('size', 'N/A')}"
                    )
        
        # Enhanced refresh section
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
        
        # Enhanced portfolio management with session state
        st.subheader("💾 Portfolio Management")
        load_col, clear_col, spacer = st.columns([1, 1, 1])
        
        with load_col:
            if st.button("📂 Reset to Default", type="secondary", use_container_width=True):
                reset_to_default_portfolio()
                st.success("✅ Reset to default portfolio")
                st.rerun()
        
        with clear_col:
            if st.button("�️ Clear All", type="primary", use_container_width=True):
                clear_portfolio()
                st.success("✅ Cleared all holdings")
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Enhanced input layout with crypto icons and live prices
        st.subheader("🪙 Asset Holdings")
        
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
        
        with col1:
            if btc_price and btc_price > 0:
                price_display = f"${btc_price:,.0f}"
                card_class = "crypto-btc"
            else:
                price_display = "API Failed"
                card_class = "crypto-btc fee-high"  # Red background for failed API
            
            st.markdown(f"""
            <div class="metric-card {card_class}">
                <h4>₿ Bitcoin (BTC)</h4>
                <h2>{price_display}</h2>
                <p>{'Current Price' if btc_price and btc_price > 0 else 'Price Unavailable'}</p>
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
            else:
                price_display = "API Failed"
                card_class = "crypto-eth fee-high"
                
            st.markdown(f"""
            <div class="metric-card {card_class}">
                <h4>⟠ Ethereum (ETH)</h4>
                <h2>{price_display}</h2>
                <p>{'Current Price' if eth_price and eth_price > 0 else 'Price Unavailable'}</p>
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
            else:
                price_display = "API Failed"
                card_class = "crypto-bnb fee-high"
                
            st.markdown(f"""
            <div class="metric-card {card_class}">
                <h4>🔸 Binance Coin (BNB)</h4>
                <h2>{price_display}</h2>
                <p>{'Current Price' if bnb_price and bnb_price > 0 else 'Price Unavailable'}</p>
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
            else:
                price_display = "API Failed"
                card_class = "crypto-pol fee-high"
                
            st.markdown(f"""
            <div class="metric-card {card_class}">
                <h4>🔷 Polygon (POL)</h4>
                <h2>{price_display}</h2>
                <p>{'Current Price' if pol_price and pol_price > 0 else 'Price Unavailable'}</p>
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
            
            # Create main layout - compact but rich
            main_col1, main_col2 = st.columns([1, 1])
            
            with main_col1:
                # Enhanced portfolio values with API status
                st.subheader("💰 Your Asset Values")
                value_row1 = st.columns(2)
                
                # BTC Value
                if btc_value is not None:
                    value_row1[0].metric("₿ Bitcoin Value", f"${btc_value:,.2f}", 
                                       delta=f"{btc_amount:.8f} BTC" if btc_amount > 0 else None)
                else:
                    value_row1[0].metric("₿ Bitcoin Value", "API Failed", 
                                       delta="Price unavailable")
                
                # ETH Value  
                if eth_value is not None:
                    value_row1[1].metric("⟠ Ethereum Value", f"${eth_value:,.2f}", 
                                       delta=f"{eth_amount:.4f} ETH" if eth_amount > 0 else None)
                else:
                    value_row1[1].metric("⟠ Ethereum Value", "API Failed",
                                       delta="Price unavailable")
                
                value_row2 = st.columns(2)
                
                # BNB Value
                if bnb_value is not None:
                    value_row2[0].metric("🔸 BNB Value", f"${bnb_value:,.2f}", 
                                       delta=f"{bnb_amount:.4f} BNB" if bnb_amount > 0 else None)
                else:
                    value_row2[0].metric("� BNB Value", "API Failed",
                                       delta="Price unavailable")
                
                # POL Value
                if pol_value is not None:
                    value_row2[1].metric("🔷 POL Value", f"${pol_value:,.2f}", 
                                       delta=f"{pol_amount:.2f} POL" if pol_amount > 0 else None)
                else:
                    value_row2[1].metric("🔷 POL Value", "API Failed",
                                       delta="Price unavailable")
            
            with main_col2:
                # Enhanced total value section with API transparency
                st.subheader("🎯 Total Portfolio Value")
                usdt_inr_rate = 83.50
                
                if failed_apis:
                    st.warning(f"⚠️ Partial calculation - {len(failed_apis)} API(s) failed")
                
                total_row = st.columns(1)
                if total_value > 0:
                    st.metric("💵 USD Value", f"${total_value:,.2f}",
                             delta=f"From {len(valid_values)}/4 assets" if failed_apis else None)
                    st.metric("🇮🇳 INR Value", f"₹{total_value * usdt_inr_rate:,.2f}")
                    if btc_price and btc_price > 0:
                        st.metric("₿ BTC Equivalent", f"₿{total_value / btc_price:.8f}")
                    else:
                        st.metric("₿ BTC Equivalent", "BTC API Failed")
                else:
                    st.metric("💵 USD Value", "No Valid Prices")
                    st.metric("🇮🇳 INR Value", "No Valid Prices")
                    st.metric("₿ BTC Equivalent", "APIs Failed")
        
        except Exception as e:
            st.error(f"❌ Error calculating portfolio values: {e}")
            st.info("🔄 Please try refreshing prices or check API connectivity.")

    elif page == "Bitcoin Metrics":
        st.header("📊 Bitcoin Metrics Dashboard")
        
        # Add cache for metrics with 5-minute TTL
        @st.cache_data(ttl=300)
        def cached_get_bitcoin_metrics():
            from bitcoin_metrics import bitcoin_metrics
            return bitcoin_metrics.get_comprehensive_metrics()
        
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
                
                # Multi-currency prices
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
                st.subheader("📈 Market Sentiment & Supply")
                
                fear_col1, fear_col2, fear_col3 = st.columns(3)
                
                # Fear & Greed Index
                with fear_col1:
                    fng_data = metrics.get('fear_greed', {})
                    if fng_data.get('value') is not None:
                        fng_value = fng_data['value']
                        fng_class = fng_data.get('classification', 'Unknown')
                        
                        # Color based on fear/greed
                        if fng_value < 25:
                            color = "🔴"
                        elif fng_value < 45:
                            color = "🟠"
                        elif fng_value < 55:
                            color = "🟡"
                        elif fng_value < 75:
                            color = "🟢"
                        else:
                            color = "🚀"
                        
                        st.metric(f"{color} Fear & Greed Index", f"{fng_value}/100", delta=fng_class)
                        
                        # Add a progress bar
                        st.progress(fng_value / 100)
                    else:
                        st.metric("😰 Fear & Greed Index", "API Failed")
                
                # Circulating Supply
                with fear_col2:
                    blockchain_data = metrics.get('blockchain', {})
                    if blockchain_data.get('total_supply'):
                        total_supply = blockchain_data['total_supply'] / 1e8  # Convert from satoshis
                        remaining = 21_000_000 - total_supply
                        st.metric("🪙 Circulating Supply", f"{total_supply:,.0f} BTC")
                        st.metric("⏳ Remaining to Mine", f"{remaining:,.0f} BTC")
                        
                        # Progress bar to 21M
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
                    
                    if blockchain_data.get('mining_difficulty'):
                        difficulty = blockchain_data['mining_difficulty']
                        difficulty_t = difficulty / 1e12
                        st.metric("⛏️ Mining Difficulty", f"{difficulty_t:.2f}T")
                    else:
                        st.metric("⛏️ Mining Difficulty", "API Failed")
                
                # === SECTION 3: NETWORK ACTIVITY CHARTS ===
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
                            # Active Addresses
                            if 'n-active-addresses' in charts:
                                addr_data = charts['n-active-addresses']
                                if addr_data.get('values'):
                                    # Similar plotting for active addresses
                                    dates = [datetime.fromtimestamp(point['x']) for point in addr_data['values']]
                                    values = [point['y'] for point in addr_data['values']]
                                    
                                    fig = go.Figure()
                                    fig.add_trace(go.Scatter(
                                        x=dates, 
                                        y=values,
                                        mode='lines+markers',
                                        name='Active Addresses',
                                        line=dict(color='#00d4aa', width=2),
                                        marker=dict(size=4)
                                    ))
                                    
                                    fig.update_layout(
                                        title="👥 Daily Active Addresses",
                                        xaxis_title="Date",
                                        yaxis_title="Active Addresses",
                                        height=400,
                                        template="plotly_dark"
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    if values:
                                        st.metric("👤 Latest Active Addresses", f"{values[-1]:,.0f}")
                            else:
                                st.error("❌ Active addresses data unavailable")
                    
                    with chart_tab2:
                        # Mining Charts
                        mining_col1, mining_col2 = st.columns(2)
                        
                        with mining_col1:
                            # Hash Rate
                            if 'hash-rate' in charts:
                                hash_data = charts['hash-rate']
                                if hash_data.get('values'):
                                    dates = [datetime.fromtimestamp(point['x']) for point in hash_data['values']]
                                    values = [point['y'] / 1e18 for point in hash_data['values']]  # Convert to EH/s
                                    
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
                st.subheader("🌐 Network Health")
                
                network_col1, network_col2, network_col3 = st.columns(3)
                
                # Block timing
                with network_col1:
                    if 'avg-block-time' in charts:
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
                    if 'avg-block-size' in charts:
                        block_size_data = charts['avg-block-size']
                        if block_size_data.get('values') and len(block_size_data['values']) > 0:
                            latest_block_size = block_size_data['values'][-1]['y'] / 1e6  # Convert to MB
                            st.metric("📏 Avg Block Size", f"{latest_block_size:.2f} MB")
                        else:
                            st.metric("📏 Avg Block Size", "API Failed")
                    else:
                        st.metric("📏 Avg Block Size", "API Failed")
                
                # Block reward
                with network_col3:
                    if blockchain_data.get('block_reward'):
                        block_reward = blockchain_data['block_reward']
                        st.metric("🎁 Block Reward", f"{block_reward} BTC")
                        
                        # Calculate next halving (rough estimate)
                        current_blocks = blockchain_data.get('block_count', 0)
                        blocks_per_halving = 210_000
                        next_halving_block = ((current_blocks // blocks_per_halving) + 1) * blocks_per_halving
                        blocks_to_halving = next_halving_block - current_blocks
                        days_to_halving = (blocks_to_halving * 10) / (60 * 24)  # ~10 min blocks
                        
                        st.metric("📅 Est. Days to Halving", f"{days_to_halving:,.0f}")
                    else:
                        st.metric("🎁 Block Reward", "API Failed")
                
                # Show data freshness
                st.divider()
                col_time, col_sources = st.columns(2)
                with col_time:
                    st.caption(f"🕐 Data refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                with col_sources:
                    st.caption("📡 Sources: CoinGecko, Blockchain.info, Alternative.me, Bitnodes")
                
            except Exception as e:
                st.error(f"❌ Failed to load Bitcoin metrics: {str(e)}")
                st.info("🔄 Please try refreshing the page or check your internet connection.")

if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
