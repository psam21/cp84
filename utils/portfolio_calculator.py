"""
Portfolio calculation utilities for cryptocurrency portfolio management.
Handles portfolio value calculations, currency conversions, and statistics.
"""
from .logging import debug_log


def calculate_portfolio_values(portfolio_amounts, prices):
    """
    Calculate portfolio values for each cryptocurrency
    
    Args:
        portfolio_amounts (dict): Portfolio holdings {'btc': amount, 'eth': amount, ...}
        prices (dict): Current prices {'BTC': price, 'ETH': price, ...}
    
    Returns:
        dict: Portfolio values and metadata
    """
    debug_log("🧮 Starting portfolio value calculations", "INFO", "portfolio_calc")
    
    # Calculate individual values
    symbol_map = {'btc': 'BTC', 'eth': 'ETH', 'bnb': 'BNB', 'pol': 'POL'}
    values = {}
    
    for holding_key, amount in portfolio_amounts.items():
        symbol = symbol_map.get(holding_key)
        if symbol and symbol in prices:
            price = prices[symbol]
            if price and price > 0:
                values[holding_key] = amount * price
                debug_log(f"💰 {symbol}: {amount} × ${price:,.2f} = ${values[holding_key]:,.2f}", 
                         "INFO", "portfolio_calc")
            else:
                values[holding_key] = None
                debug_log(f"❌ {symbol}: Price unavailable", "WARNING", "portfolio_calc")
        else:
            values[holding_key] = None
    
    # Calculate totals
    valid_values = [v for v in values.values() if v is not None]
    total_value = sum(valid_values) if valid_values else 0
    
    # Calculate statistics
    non_zero_assets = sum(1 for amount in portfolio_amounts.values() if amount > 0)
    largest_asset = "N/A"
    largest_percentage = 0
    
    if total_value > 0:
        asset_values = {
            'BTC': values.get('btc', 0) or 0,
            'ETH': values.get('eth', 0) or 0,
            'BNB': values.get('bnb', 0) or 0,
            'POL': values.get('pol', 0) or 0
        }
        largest_asset = max(asset_values, key=asset_values.get)
        largest_percentage = (asset_values[largest_asset] / total_value) * 100
    
    result = {
        'btc_value': values.get('btc'),
        'eth_value': values.get('eth'), 
        'bnb_value': values.get('bnb'),
        'pol_value': values.get('pol'),
        'total_value': total_value,
        'valid_count': len(valid_values),
        'total_count': len(portfolio_amounts),
        'individual_values': values,
        'statistics': {
            'non_zero_assets': non_zero_assets,
            'largest_asset': largest_asset,
            'largest_percentage': largest_percentage
        }
    }
    
    debug_log(f"✅ Portfolio calculation complete: ${total_value:,.2f} total, {len(valid_values)}/4 assets", 
             "SUCCESS", "portfolio_calc")
    
    return result


def calculate_currency_conversions(usd_value, exchange_rates):
    """
    Convert portfolio value to multiple currencies
    
    Args:
        usd_value (float): Portfolio value in USD
        exchange_rates (dict): Exchange rates {'inr': rate, 'eur': rate, 'aed': rate}
    
    Returns:
        dict: Converted values and rate information
    """
    if usd_value <= 0:
        return {
            'usd': 0,
            'eur': 0,
            'inr': 0,
            'aed': 0,
            'rates': exchange_rates
        }
    
    conversions = {
        'usd': usd_value,
        'eur': usd_value * exchange_rates.get('eur', 0.92),
        'inr': usd_value * exchange_rates.get('inr', 83.5),
        'aed': usd_value * exchange_rates.get('aed', 3.67),
        'rates': exchange_rates
    }
    
    debug_log(f"💱 Currency conversions: USD ${usd_value:,.2f} → EUR €{conversions['eur']:,.2f}, INR ₹{conversions['inr']:,.0f}, AED د.إ{conversions['aed']:,.2f}", 
             "INFO", "currency_conversion")
    
    return conversions


def calculate_crypto_equivalents(usd_value, crypto_prices):
    """
    Calculate how much of each cryptocurrency the portfolio is worth
    
    Args:
        usd_value (float): Portfolio value in USD
        crypto_prices (dict): Current crypto prices
    
    Returns:
        dict: Equivalent amounts in each cryptocurrency
    """
    if usd_value <= 0:
        return {'BTC': 0, 'ETH': 0, 'BNB': 0}
    
    equivalents = {}
    
    for symbol in ['BTC', 'ETH', 'BNB']:
        price = crypto_prices.get(symbol)
        if price and price > 0:
            equivalents[symbol] = usd_value / price
            debug_log(f"₿ Portfolio equivalent in {symbol}: {equivalents[symbol]:.8f} {symbol}", 
                     "INFO", "crypto_equivalent")
        else:
            equivalents[symbol] = None
            debug_log(f"❌ {symbol} equivalent calculation failed: price unavailable", 
                     "WARNING", "crypto_equivalent")
    
    return equivalents


def get_failed_apis(prices):
    """
    Identify which APIs failed to provide valid prices
    
    Args:
        prices (dict): Price data from APIs
    
    Returns:
        list: List of failed API symbols
    """
    failed = []
    for symbol in ['BTC', 'ETH', 'BNB', 'POL']:
        if prices.get(symbol) is None or prices.get(symbol) <= 0:
            failed.append(symbol)
    
    if failed:
        debug_log(f"⚠️ Failed APIs detected: {', '.join(failed)}", "WARNING", "api_status")
    
    return failed


def process_complete_portfolio(portfolio_amounts, binance_prices, exchange_rate_functions):
    """
    Complete portfolio processing including calculations, validation, and data preparation
    
    Args:
        portfolio_amounts (dict): Portfolio holdings {'btc': amount, 'eth': amount, ...}
        binance_prices (dict): Current prices {'BTC': price, 'ETH': price, ...}
        exchange_rate_functions (dict): Exchange rate getter functions
    
    Returns:
        dict: Complete portfolio processing results including values, rates, and display data
    """
    debug_log("🏗️ Starting complete portfolio processing", "INFO", "portfolio_process")
    
    try:
        # Calculate portfolio values
        portfolio_values = calculate_portfolio_values(portfolio_amounts, binance_prices)
        
        btc_value = portfolio_values.get('btc_value')
        eth_value = portfolio_values.get('eth_value')
        bnb_value = portfolio_values.get('bnb_value')
        pol_value = portfolio_values.get('pol_value')
        total_value = portfolio_values.get('total_value', 0)
        
        # Get failed APIs for error handling
        failed_apis = get_failed_apis(binance_prices)
        
        # Calculate valid values count for statistics
        valid_values = [v for v in [btc_value, eth_value, bnb_value, pol_value] if v is not None]
        
        # Get live exchange rates
        usdt_inr_data = exchange_rate_functions['usdt_inr']()
        usd_eur_data = exchange_rate_functions['usd_eur']()
        usd_aed_data = exchange_rate_functions['usd_aed']()
        
        # Calculate crypto equivalents
        crypto_equivalents = calculate_crypto_equivalents(total_value, binance_prices)
        
        # Prepare structured data for display
        processing_result = {
            'portfolio_values': {
                'btc_value': btc_value,
                'eth_value': eth_value,
                'bnb_value': bnb_value,
                'pol_value': pol_value,
                'total_value': total_value
            },
            'failed_apis': failed_apis,
            'valid_values': valid_values,
            'exchange_rates': {
                'usdt_inr': usdt_inr_data,
                'usd_eur': usd_eur_data,
                'usd_aed': usd_aed_data
            },
            'crypto_equivalents': crypto_equivalents,
            'portfolio_amounts_with_values': {
                'btc': portfolio_amounts['btc'],
                'eth': portfolio_amounts['eth'],
                'bnb': portfolio_amounts['bnb'],
                'pol': portfolio_amounts['pol'],
                'btc_value': btc_value,
                'eth_value': eth_value,
                'bnb_value': bnb_value,
                'pol_value': pol_value
            },
            'success': True,
            'error': None
        }
        
        debug_log(f"✅ Portfolio processing complete: Total ${total_value:,.2f}", "SUCCESS", "portfolio_process")
        return processing_result
        
    except Exception as e:
        debug_log(f"❌ Portfolio processing failed: {e}", "ERROR", "portfolio_process")
        return {
            'success': False,
            'error': str(e),
            'portfolio_values': None,
            'failed_apis': [],
            'valid_values': [],
            'exchange_rates': {},
            'crypto_equivalents': {},
            'portfolio_amounts_with_values': {}
        }
