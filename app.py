"""
A Streamlit application to display cryptocurrency data.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
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
def cached_get_binance_prices():
    return {
        'BTC': get_binance_price("BTCUSDT"),
        'ETH': get_binance_price("ETHUSDT"),
        'BNB': get_binance_price("BNBUSDT"),
        'POL': get_binance_price("POLUSDT")
    }

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

    # Pre-fetch all data at startup with better error handling
    with st.spinner("🔄 Loading cryptocurrency data..."):
        try:
            mempool_data = cached_get_mempool_info()
            mempool_stats = cached_get_mempool_stats()
            binance_prices = cached_get_binance_prices()
            btc_data = cached_get_btc_ohlc_data()
            
            # Validate critical data
            if not binance_prices or 'BTC' not in binance_prices:
                st.warning("⚠️ Some price data may be unavailable. Retrying...")
                binance_prices = {'BTC': 0, 'ETH': 0, 'BNB': 0, 'POL': 0}
                
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            st.info("🔄 Please refresh the page to retry data loading.")
            # Set fallback data to prevent crashes
            mempool_data = {'error': 'Data unavailable'}
            mempool_stats = {'error': 'Data unavailable'}
            binance_prices = {'BTC': 0, 'ETH': 0, 'BNB': 0, 'POL': 0}
            btc_data = pd.DataFrame()

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    tabs = [
        "Why Bitcoin?",
        "Bitcoin OHLC",
        "Mempool Data",
        "Portfolio Value",
    ]
    page = st.sidebar.radio("Go to", tabs)

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
        
        # Add some Bitcoin stats using cached data
        if 'BTC' in binance_prices:
            st.subheader("📊 Live Bitcoin Metrics")
            metrics_cols = st.columns(3)
            
            try:
                metrics_cols[0].metric("Current Price", f"${binance_prices['BTC']:,.2f}")
                
                # Calculate market cap with more accurate circulating supply (as of 2025)
                circulating_supply = 19_800_000  # More accurate current circulating supply
                market_cap = binance_prices['BTC'] * circulating_supply
                metrics_cols[1].metric("Market Cap", f"${market_cap/1e12:.2f}T")
                
                # Show accurate scarcity - much less remaining now
                remaining_btc = 21_000_000 - circulating_supply
                metrics_cols[2].metric("Remaining to Mine", f"{remaining_btc:,.0f} BTC")
                
            except:
                st.info("Live metrics temporarily unavailable")

    elif page == "Bitcoin OHLC":
        st.header("Bitcoin Weekly OHLC Data")
        
        # Compact header row
        col_price, col_fetch = st.columns([2, 1])
        with col_price:
            try:
                st.metric("Current Price", f"${binance_prices['BTC']:,.2f}")
            except:
                st.metric("Current Price", "Loading...")
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
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card crypto-btc">
                <h4>₿ Bitcoin (BTC)</h4>
                <h2>${binance_prices['BTC']:,.0f}</h2>
                <p>Current Price</p>
            </div>
            """, unsafe_allow_html=True)
            btc_amount = st.number_input("", 
                                       value=st.session_state.portfolio['btc'], 
                                       step=0.01, format="%.8f", key="btc_input",
                                       help="Enter your Bitcoin holdings")
        
        with col2:
            st.markdown(f"""
            <div class="metric-card crypto-eth">
                <h4>⟠ Ethereum (ETH)</h4>
                <h2>${binance_prices['ETH']:,.0f}</h2>
                <p>Current Price</p>
            </div>
            """, unsafe_allow_html=True)
            eth_amount = st.number_input("", 
                                       value=st.session_state.portfolio['eth'], 
                                       step=0.1, format="%.4f", key="eth_input",
                                       help="Enter your Ethereum holdings")
        
        with col3:
            st.markdown(f"""
            <div class="metric-card crypto-bnb">
                <h4>🔸 Binance Coin (BNB)</h4>
                <h2>${binance_prices['BNB']:,.0f}</h2>
                <p>Current Price</p>
            </div>
            """, unsafe_allow_html=True)
            bnb_amount = st.number_input("", 
                                       value=st.session_state.portfolio['bnb'], 
                                       step=0.1, format="%.4f", key="bnb_input",
                                       help="Enter your BNB holdings")
        
        with col4:
            st.markdown(f"""
            <div class="metric-card crypto-pol">
                <h4>🔷 Polygon (POL)</h4>
                <h2>${binance_prices['POL']:,.4f}</h2>
                <p>Current Price</p>
            </div>
            """, unsafe_allow_html=True)
            pol_amount = st.number_input("", 
                                       value=st.session_state.portfolio['pol'], 
                                       step=1.0, format="%.2f", key="pol_input",
                                       help="Enter your Polygon holdings")
        
        # Update session state portfolio
        st.session_state.portfolio['btc'] = btc_amount
        st.session_state.portfolio['eth'] = eth_amount
        st.session_state.portfolio['bnb'] = bnb_amount
        st.session_state.portfolio['pol'] = pol_amount
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        try:
            # Calculate values
            btc_value = btc_amount * binance_prices['BTC']
            eth_value = eth_amount * binance_prices['ETH']
            bnb_value = bnb_amount * binance_prices['BNB']
            pol_value = pol_amount * binance_prices['POL']
            total_value = btc_value + eth_value + bnb_value + pol_value
            
            # Create main layout - compact but rich
            main_col1, main_col2 = st.columns([1, 1])
            
            with main_col1:
                # Enhanced portfolio values
                st.subheader("💰 Your Asset Values")
                value_row1 = st.columns(2)
                value_row1[0].metric("₿ Bitcoin Value", f"${btc_value:,.2f}", 
                                   delta=f"{btc_amount:.8f} BTC" if btc_amount > 0 else None)
                value_row1[1].metric("⟠ Ethereum Value", f"${eth_value:,.2f}", 
                                   delta=f"{eth_amount:.4f} ETH" if eth_amount > 0 else None)
                
                value_row2 = st.columns(2)
                value_row2[0].metric("🔸 BNB Value", f"${bnb_value:,.2f}", 
                                   delta=f"{bnb_amount:.4f} BNB" if bnb_amount > 0 else None)
                value_row2[1].metric("🔷 POL Value", f"${pol_value:,.2f}", 
                                   delta=f"{pol_amount:.2f} POL" if pol_amount > 0 else None)
            
            with main_col2:
                # Enhanced total value section
                st.subheader("🎯 Total Portfolio Value")
                usdt_inr_rate = 83.50
                
                total_row = st.columns(1)
                st.metric("💵 USD Value", f"${total_value:,.2f}")
                st.metric("🇮🇳 INR Value", f"₹{total_value * usdt_inr_rate:,.2f}")
                if binance_prices['BTC'] > 0 and total_value > 0:
                    st.metric("₿ BTC Equivalent", f"₿{total_value / binance_prices['BTC']:.8f}")
        
        except Exception as e:
            st.error(f"❌ Error calculating portfolio values: {e}")
            st.info("Please ensure all price data is loaded correctly.")

if __name__ == "__main__":
    main()
