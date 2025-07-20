"""
Exchange rates UI components for currency conversion display.
"""
import streamlit as st
from utils.logging import debug_log
from utils.http_utils import make_rate_limited_request, simple_api_request


@st.cache_data(ttl=300)  # 5-minute cache for exchange rates
def get_usdt_inr_rate():
    """Get USDT/INR exchange rate from multiple sources with rate limiting"""
    
    # Try multiple sources for USDT/INR rate
    sources = [
        {
            'name': 'CoinGecko',
            'service': 'coingecko',
            'url': 'https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=inr',
            'parser': lambda data: data.get('tether', {}).get('inr')
        },
        {
            'name': 'Binance',
            'service': 'binance',
            'url': 'https://api.binance.com/api/v3/ticker/price?symbol=USDTINR',
            'parser': lambda data: float(data.get('price', 0)) if data.get('price') else None
        }
    ]
    
    for source in sources:
        try:
            debug_log(f"🔄 Fetching USDT/INR rate from {source['name']}", "INFO", "usdt_inr_fetch")
            
            # Use rate-limited request
            response = make_rate_limited_request(
                url=source['url'], 
                service_name=source['service'],
                timeout=8,
                max_retries=2
            )
            
            # If rate-limited request fails, try simple fallback
            if not response:
                debug_log(f"🚨 Rate-limited request failed for {source['name']}, trying simple fallback", "WARNING", "usdt_inr_fallback")
                response = simple_api_request(source['url'], timeout=10)
            
            if response and response.status_code == 200:
                data = response.json()
                rate = source['parser'](data)
                
                if rate and rate > 0:
                    debug_log(f"✅ {source['name']} USDT/INR rate: ₹{rate:.2f}", "SUCCESS", "usdt_inr_success")
                    return {
                        'rate': rate,
                        'source': source['name'],
                        'success': True
                    }
            
            debug_log(f"❌ {source['name']} USDT/INR failed to get valid data", "ERROR", "usdt_inr_error")
            
        except Exception as e:
            debug_log(f"❌ {source['name']} USDT/INR error: {e}", "ERROR", "usdt_inr_error")
    
    # Fallback to hardcoded rate
    debug_log("⚠️ Using fallback USDT/INR rate: ₹83.50", "WARNING", "usdt_inr_fallback")
    return {
        'rate': 83.50,
        'source': 'Fallback',
        'success': False
    }


@st.cache_data(ttl=300)  # 5-minute cache for exchange rates
def get_usd_eur_rate():
    """Get USD/EUR exchange rate from multiple sources with rate limiting"""
    
    # Try multiple sources for USD/EUR rate
    sources = [
        {
            'name': 'CoinGecko',
            'service': 'coingecko',
            'url': 'https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=eur',
            'parser': lambda data: data.get('tether', {}).get('eur')
        },
        {
            'name': 'Binance',
            'service': 'binance',
            'url': 'https://api.binance.com/api/v3/ticker/price?symbol=EURUSDT',
            'parser': lambda data: 1 / float(data.get('price', 1)) if data.get('price') and float(data.get('price', 1)) > 0 else None
        }
    ]
    
    for source in sources:
        try:
            debug_log(f"🔄 Fetching USD/EUR rate from {source['name']}", "INFO", "usd_eur_fetch")
            
            # Use rate-limited request
            response = make_rate_limited_request(
                url=source['url'], 
                service_name=source['service'],
                timeout=8,
                max_retries=2
            )
            
            # If rate-limited request fails, try simple fallback
            if not response:
                debug_log(f"🚨 Rate-limited request failed for {source['name']}, trying simple fallback", "WARNING", "usd_eur_fallback")
                response = simple_api_request(source['url'], timeout=10)
            
            if response and response.status_code == 200:
                data = response.json()
                rate = source['parser'](data)
                
                if rate and rate > 0:
                    debug_log(f"✅ {source['name']} USD/EUR rate: €{rate:.4f}", "SUCCESS", "usd_eur_success")
                    return {
                        'rate': rate,
                        'source': source['name'],
                        'success': True
                    }
            
            debug_log(f"❌ {source['name']} USD/EUR failed to get valid data", "ERROR", "usd_eur_error")
            
        except Exception as e:
            debug_log(f"❌ {source['name']} USD/EUR error: {e}", "ERROR", "usd_eur_error")
    
    # Fallback to hardcoded rate
    debug_log("⚠️ Using fallback USD/EUR rate: €0.92", "WARNING", "usd_eur_fallback")
    return {
        'rate': 0.92,
        'source': 'Fallback',
        'success': False
    }


@st.cache_data(ttl=300)  # 5-minute cache for exchange rates
def get_usd_aed_rate():
    """Get USD/AED exchange rate from multiple sources with rate limiting"""
    
    # Try multiple sources for USD/AED rate
    sources = [
        {
            'name': 'CoinGecko',
            'service': 'coingecko',
            'url': 'https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=aed',
            'parser': lambda data: data.get('tether', {}).get('aed')
        },
        {
            'name': 'Binance',
            'service': 'binance',
            'url': 'https://api.binance.com/api/v3/ticker/price?symbol=AEDUSDT',
            'parser': lambda data: 1 / float(data.get('price', 1)) if data.get('price') and float(data.get('price', 1)) > 0 else None
        }
    ]
    
    for source in sources:
        try:
            debug_log(f"🔄 Fetching USD/AED rate from {source['name']}", "INFO", "usd_aed_fetch")
            
            # Use rate-limited request
            response = make_rate_limited_request(
                url=source['url'], 
                service_name=source['service'],
                timeout=8,
                max_retries=2
            )
            
            if response and response.status_code == 200:
                data = response.json()
                rate = source['parser'](data)
                
                if rate and rate > 0:
                    debug_log(f"✅ {source['name']} USD/AED rate: د.إ{rate:.2f}", "SUCCESS", "usd_aed_success")
                    return {
                        'rate': rate,
                        'source': source['name'],
                        'success': True
                    }
            
            debug_log(f"❌ {source['name']} USD/AED failed to get valid data", "ERROR", "usd_aed_error")
            
        except Exception as e:
            debug_log(f"❌ {source['name']} USD/AED error: {e}", "ERROR", "usd_aed_error")
    
    # Fallback to hardcoded rate
    debug_log("⚠️ Using fallback USD/AED rate: د.إ3.67", "WARNING", "usd_aed_fallback")
    return {
        'rate': 3.67,
        'source': 'Fallback',
        'success': False
    }


def display_exchange_rates(rates_data, last_updated):
    """
    Display current exchange rates in a clean format
    
    Args:
        rates_data (dict): Dictionary containing exchange rate information
        last_updated (str): Timestamp of last update
    """
    st.subheader("💱 Live Exchange Rates")
    
    if rates_data:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            usdt_inr = rates_data.get('USDT_INR', 0)
            if usdt_inr > 0:
                st.metric(
                    label="USDT → INR",
                    value=f"₹ {usdt_inr:.2f}",
                    help="1 USDT in Indian Rupees"
                )
            else:
                st.error("USDT/INR rate unavailable")
        
        with col2:
            usd_eur = rates_data.get('USD_EUR', 0)
            if usd_eur > 0:
                st.metric(
                    label="USD → EUR", 
                    value=f"€ {usd_eur:.4f}",
                    help="1 USD in Euros"
                )
            else:
                st.error("USD/EUR rate unavailable")
        
        with col3:
            usd_aed = rates_data.get('USD_AED', 0)
            if usd_aed > 0:
                st.metric(
                    label="USD → AED",
                    value=f"د.إ {usd_aed:.2f}",
                    help="1 USD in UAE Dirhams"
                )
            else:
                st.error("USD/AED rate unavailable")
        
        # Last updated info
        if last_updated:
            st.caption(f"Last updated: {last_updated}")
    else:
        st.warning("Exchange rates not available")


def display_currency_conversion(base_amount=1000, selected_currency="USD"):
    """
    Display currency conversion calculator
    
    Args:
        base_amount (float): Base amount to convert
        selected_currency (str): Selected currency for conversion
    """
    st.subheader("🔄 Currency Converter")
    
    # Currency conversion inputs
    col1, col2 = st.columns(2)
    
    with col1:
        amount = st.number_input(
            "Amount",
            value=float(base_amount),
            min_value=0.01,
            step=1.0,
            format="%.2f"
        )
        
        from_currency = st.selectbox(
            "From Currency",
            ["USD", "EUR", "INR", "AED", "USDT"],
            index=0
        )
    
    with col2:
        to_currency = st.selectbox(
            "To Currency",
            ["USD", "EUR", "INR", "AED", "USDT"],
            index=2  # Default to INR
        )
        
        # Convert button
        if st.button("Convert", type="primary"):
            converted_amount = convert_currency(amount, from_currency, to_currency)
            if converted_amount:
                st.success(f"{amount:.2f} {from_currency} = {converted_amount:.2f} {to_currency}")
            else:
                st.error("Conversion failed - exchange rate not available")


def convert_currency(amount, from_currency, to_currency):
    """
    Convert currency using available exchange rates
    
    Args:
        amount (float): Amount to convert
        from_currency (str): Source currency
        to_currency (str): Target currency
        
    Returns:
        float or None: Converted amount if successful, None if failed
    """
    # This would integrate with the actual exchange rate data
    # For now, return a placeholder
    debug_log(f"Converting {amount} {from_currency} to {to_currency}", "INFO", "currency_converter")
    
    # Placeholder conversion rates (would be replaced with live data)
    rates = {
        'USD_INR': 83.0,
        'USD_EUR': 0.85,
        'USD_AED': 3.67,
        'USDT_INR': 83.0,
        'USDT_USD': 1.0
    }
    
    # Simple conversion logic (would be more sophisticated in practice)
    if from_currency == to_currency:
        return amount
    
    # Convert through USD as base
    if from_currency != 'USD':
        # First convert to USD
        if from_currency == 'INR':
            amount = amount / rates.get('USD_INR', 83.0)
        elif from_currency == 'EUR':
            amount = amount / rates.get('USD_EUR', 0.85)
        elif from_currency == 'AED':
            amount = amount / rates.get('USD_AED', 3.67)
        elif from_currency == 'USDT':
            amount = amount / rates.get('USDT_USD', 1.0)
    
    # Then convert from USD to target currency
    if to_currency != 'USD':
        if to_currency == 'INR':
            amount = amount * rates.get('USD_INR', 83.0)
        elif to_currency == 'EUR':
            amount = amount * rates.get('USD_EUR', 0.85)
        elif to_currency == 'AED':
            amount = amount * rates.get('USD_AED', 3.67)
        elif to_currency == 'USDT':
            amount = amount * rates.get('USDT_USD', 1.0)
    
    return round(amount, 4)
