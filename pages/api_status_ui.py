"""
API status monitoring UI components for displaying real-time exchange health.
"""
import streamlit as st
from utils.logging import debug_log


def display_api_status(api_results):
    """
    Display current API status with working/failing indicators
    
    Args:
        api_results (dict): Dictionary containing API results and status
    """
    st.subheader("🔌 API Status")
    
    if api_results:
        # Count working APIs
        total_apis = len(api_results.get('prices', {}))
        working_apis = len([p for p in api_results.get('prices', {}).values() if p and p > 0])
        
        # Overall status
        col1, col2 = st.columns(2)
        
        with col1:
            if working_apis == total_apis:
                st.success(f"✅ All APIs Working ({working_apis}/{total_apis})")
            elif working_apis > 0:
                st.warning(f"⚠️ Partial API Issues ({working_apis}/{total_apis})")
            else:
                st.error(f"❌ All APIs Down ({working_apis}/{total_apis})")
        
        with col2:
            sources_used = api_results.get('sources_used', [])
            if sources_used:
                st.info(f"📡 Sources: {', '.join(sources_used)}")
            else:
                st.error("📡 No active sources")
        
        # Individual API status
        prices = api_results.get('prices', {})
        if prices:
            st.write("**Individual API Status:**")
            
            cols = st.columns(4)
            symbols = ['BTC', 'ETH', 'BNB', 'POL']
            
            for i, symbol in enumerate(symbols):
                with cols[i]:
                    price = prices.get(symbol)
                    if price and price > 0:
                        st.success(f"{symbol}\n${price:,.2f}")
                    else:
                        st.error(f"{symbol}\nUnavailable")
        
        # Error details
        errors = api_results.get('errors', [])
        if errors:
            with st.expander("🐛 Error Details"):
                for error in errors:
                    st.text(f"• {error}")
    else:
        st.error("❌ No API data available")


def display_connectivity_test():
    """
    Display API connectivity test interface with test button
    """
    st.subheader("🧪 API Connectivity Test")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("Test all cryptocurrency APIs to verify connectivity and response times.")
    
    with col2:
        if st.button("🔍 Test APIs", type="primary"):
            test_api_connectivity()


def test_api_connectivity():
    """
    Test API connectivity and display results
    """
    with st.spinner("Testing API connectivity..."):
        debug_log("Starting API connectivity test", "INFO", "connectivity_test")
        
        try:
            # Import the multi-exchange test function
            from ..apis.multi_exchange import test_all_exchanges
            
            # Run the test
            test_results = test_all_exchanges()
            
            # Display results
            st.success("✅ API connectivity test completed!")
            
            # Show results for each exchange
            for exchange_name, result in test_results.items():
                with st.expander(f"📊 {exchange_name} Results"):
                    if 'error' in result:
                        st.error(f"❌ Error: {result['error']}")
                    else:
                        success_count = result.get('success_count', 0)
                        total_count = result.get('total_count', 4)
                        
                        if success_count == total_count:
                            st.success(f"✅ All working ({success_count}/{total_count})")
                        elif success_count > 0:
                            st.warning(f"⚠️ Partial ({success_count}/{total_count})")
                        else:
                            st.error(f"❌ Not working ({success_count}/{total_count})")
                        
                        # Show individual prices
                        prices = result.get('prices', {})
                        if prices:
                            for symbol, price in prices.items():
                                if price and price > 0:
                                    st.text(f"  • {symbol}: ${price:,.2f}")
                                else:
                                    st.text(f"  • {symbol}: ❌ Failed")
                        
                        # Show errors
                        errors = result.get('errors', [])
                        if errors:
                            st.text("Errors:")
                            for error in errors:
                                st.text(f"  • {error}")
            
            debug_log("API connectivity test completed successfully", "SUCCESS", "connectivity_test")
            
        except Exception as e:
            st.error(f"❌ Connectivity test failed: {str(e)}")
            debug_log(f"API connectivity test failed: {str(e)}", "ERROR", "connectivity_test")


def display_api_metrics(api_results):
    """
    Display detailed API performance metrics
    
    Args:
        api_results (dict): API results dictionary
    """
    if not api_results:
        return
    
    st.subheader("📈 API Performance Metrics")
    
    # Success rate metrics
    col1, col2, col3, col4 = st.columns(4)
    
    prices = api_results.get('prices', {})
    total_symbols = len(prices)
    successful_prices = len([p for p in prices.values() if p and p > 0])
    
    with col1:
        success_rate = (successful_prices / total_symbols * 100) if total_symbols > 0 else 0
        st.metric(
            label="Success Rate",
            value=f"{success_rate:.1f}%"
        )
    
    with col2:
        st.metric(
            label="Working APIs",
            value=f"{successful_prices}/{total_symbols}"
        )
    
    with col3:
        sources_count = len(api_results.get('sources_used', []))
        st.metric(
            label="Active Sources",
            value=sources_count
        )
    
    with col4:
        error_count = len(api_results.get('errors', []))
        st.metric(
            label="Errors",
            value=error_count
        )


def display_rate_limit_status(rate_limiter_instance):
    """
    Display rate limiting status in the sidebar.
    
    Shows current API usage, rate limits, and visual indicators
    for different service thresholds with color coding.
    
    Args:
        rate_limiter_instance: Instance of RateLimiter class
    """
    if st.sidebar.checkbox("🔍 Show API Rate Limits", value=False):
        st.sidebar.subheader("📊 API Rate Limits")
        
        status = rate_limiter_instance.get_status()
        
        for service, data in status.items():
            # Color coding based on usage
            if data['percentage'] > 80:
                color = "🔴"
            elif data['percentage'] > 60:
                color = "🟡"
            else:
                color = "🟢"
            
            st.sidebar.write(f"{color} **{service.title()}**")
            st.sidebar.write(f"   📈 {data['current']}/{data['limit']} calls/min")
            st.sidebar.write(f"   📉 {data['available']} calls available")
            
            # Progress bar
            progress = data['current'] / data['limit']
            st.sidebar.progress(progress)
            st.sidebar.write("---")
