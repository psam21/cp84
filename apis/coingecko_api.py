"""
CoinGecko API integration for cryptocurrency price data.
Free tier API with no authentication required.
"""
import requests
from utils.logging import debug_log
from utils.http_utils import make_rate_limited_request


def get_coingecko_crypto_prices():
    """
    Get cryptocurrency prices from CoinGecko API
    Free tier, no authentication required
    
    Returns:
        dict: Dictionary with price data and metadata
    """
    return try_coingecko()


def try_coingecko():
    """Try to get prices from CoinGecko (free API, no auth required)"""
    try:
        # CoinGecko free API - very reliable for cloud deployments
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': 'bitcoin,ethereum,binancecoin,polygon',  # CoinGecko IDs
            'vs_currencies': 'usd'
        }
        
        headers = {
            'User-Agent': 'StreamlitApp/1.0',
            'Accept': 'application/json',
            'Connection': 'close'
        }
        
        # Use rate-limited request
        response = make_rate_limited_request(
            f"{url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}",
            'coingecko',
            headers=headers,
            timeout=10
        )
        
        if not response:
            debug_log("CoinGecko API request failed - no response", "ERROR", "coingecko")
            raise Exception("CoinGecko API request failed")
        
        response.raise_for_status()
        data = response.json()
        
        # Map CoinGecko IDs to our symbol names
        price_mapping = {
            'bitcoin': 'BTC',
            'ethereum': 'ETH', 
            'binancecoin': 'BNB',
            'polygon': 'POL'
        }
        
        prices = {}
        errors = []
        
        for coingecko_id, symbol in price_mapping.items():
            if coingecko_id in data and 'usd' in data[coingecko_id]:
                price = float(data[coingecko_id]['usd'])
                if price > 0:
                    prices[symbol] = price
                    debug_log(f"CoinGecko {symbol}: ${price:,.2f}", "SUCCESS", "coingecko")
                else:
                    prices[symbol] = None
                    errors.append(f"{symbol}: Invalid price {price}")
                    debug_log(f"Invalid price for {symbol}: {price}", "WARNING", "coingecko")
            else:
                prices[symbol] = None
                errors.append(f"{symbol}: Missing from CoinGecko response")
                debug_log(f"Missing {symbol} from CoinGecko response", "WARNING", "coingecko")
        
        success_count = len([p for p in prices.values() if p is not None])
        debug_log(f"CoinGecko API success: {success_count}/4 prices", "INFO", "coingecko")
        
        return {
            'prices': prices,
            'errors': errors,
            'success_count': success_count,
            'source': 'CoinGecko'
        }
        
    except Exception as e:
        debug_log(f"CoinGecko API failed: {str(e)}", "ERROR", "coingecko")
        raise Exception(f"CoinGecko API failed: {str(e)}")


def get_coingecko_exchange_rate(from_currency, to_currency):
    """
    Get exchange rate from CoinGecko
    
    Args:
        from_currency (str): Source currency (e.g., 'tether' for USDT)
        to_currency (str): Target currency (e.g., 'inr', 'eur', 'aed')
        
    Returns:
        float or None: Exchange rate if successful, None if failed
    """
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': from_currency,
            'vs_currencies': to_currency
        }
        
        headers = {
            'User-Agent': 'StreamlitApp/1.0',
            'Accept': 'application/json',
            'Connection': 'close'
        }
        
        response = make_rate_limited_request(
            f"{url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}",
            'coingecko',
            headers=headers,
            timeout=10
        )
        
        if not response:
            debug_log(f"CoinGecko exchange rate request failed: {from_currency} to {to_currency}", 
                     "ERROR", "coingecko")
            return None
            
        response.raise_for_status()
        data = response.json()
        
        if from_currency in data and to_currency in data[from_currency]:
            rate = float(data[from_currency][to_currency])
            debug_log(f"CoinGecko exchange rate {from_currency}/{to_currency}: {rate}", 
                     "SUCCESS", "coingecko")
            return rate
        else:
            debug_log(f"Missing exchange rate data: {from_currency} to {to_currency}", 
                     "WARNING", "coingecko")
            return None
            
    except Exception as e:
        debug_log(f"CoinGecko exchange rate error: {str(e)}", "ERROR", "coingecko")
        return None
