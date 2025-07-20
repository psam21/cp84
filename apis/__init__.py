"""
API integration modules for cryptocurrency exchanges.
"""
from .binance_api import get_binance_crypto_prices, try_binance
from .kucoin_api import get_kucoin_crypto_prices, try_kucoin  
from .coinbase_api import get_coinbase_crypto_prices, try_coinbase
from .coingecko_api import get_coingecko_crypto_prices, try_coingecko
from .multi_exchange import get_multi_exchange_prices

__all__ = [
    'get_binance_crypto_prices',
    'try_binance',
    'get_kucoin_crypto_prices', 
    'try_kucoin',
    'get_coinbase_crypto_prices',
    'try_coinbase',
    'get_coingecko_crypto_prices',
    'try_coingecko',
    'get_multi_exchange_prices'
]
