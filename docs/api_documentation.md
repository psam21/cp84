# API Documentation

This document provides detailed information about the cryptocurrency exchange APIs used in the portfolio calculator.

## Overview

The application uses a multi-exchange approach for maximum reliability. Each exchange has different characteristics, rate limits, and response formats.

## Exchange APIs

### 1. Binance API (Primary)

**Endpoint**: `https://api.binance.com/api/v3/ticker/price`
**Rate Limit**: 1200 requests per minute (weight-based)
**Authentication**: None required for public endpoints

#### Usage
```python
from apis.binance_api import try_binance, get_binance_price

# Get all supported prices
result = try_binance()

# Get individual price
price = get_binance_price("BTCUSDT")
```

#### Symbol Format
- BTC: `BTCUSDT`
- ETH: `ETHUSDT`
- BNB: `BNBUSDT`
- POL: `POLUSDT`

#### Response Format
```json
{
  "prices": {
    "BTC": 50000.0,
    "ETH": 3000.0,
    "BNB": 300.0,
    "POL": 0.5
  },
  "errors": [],
  "success_count": 4,
  "source": "Binance"
}
```

### 2. KuCoin API (Secondary)

**Endpoint**: `https://api.kucoin.com/api/v1/market/orderbook/level1`
**Rate Limit**: 100 requests per 10 seconds
**Authentication**: None required for public endpoints

#### Usage
```python
from apis.kucoin_api import try_kucoin, get_kucoin_price

# Get all supported prices
result = try_kucoin()

# Get individual price
price = get_kucoin_price("BTC-USDT")
```

#### Symbol Format
- BTC: `BTC-USDT`
- ETH: `ETH-USDT`
- BNB: `BNB-USDT`
- POL: `MATIC-USDT` (Polygon uses MATIC symbol)

### 3. Coinbase API (Tertiary)

**Endpoint**: `https://api.exchange.coinbase.com/products/{symbol}/ticker`
**Rate Limit**: 10 requests per second
**Authentication**: None required for public endpoints

#### Usage
```python
from apis.coinbase_api import try_coinbase, get_coinbase_price

# Get all supported prices
result = try_coinbase()

# Get individual price
price = get_coinbase_price("BTC-USD")
```

#### Symbol Format
- BTC: `BTC-USD`
- ETH: `ETH-USD`
- BNB: Not available on Coinbase
- POL: `MATIC-USD`

#### Limitations
- BNB is not available on Coinbase
- Uses MATIC symbol for Polygon

### 4. CoinGecko API (Fallback)

**Endpoint**: `https://api.coingecko.com/api/v3/simple/price`
**Rate Limit**: 10-50 requests per minute (free tier)
**Authentication**: None required

#### Usage
```python
from apis.coingecko_api import try_coingecko, get_coingecko_exchange_rate

# Get all supported prices
result = try_coingecko()

# Get exchange rate
rate = get_coingecko_exchange_rate("tether", "inr")
```

#### Symbol Format
Uses CoinGecko IDs:
- BTC: `bitcoin`
- ETH: `ethereum`
- BNB: `binancecoin`
- POL: `polygon`

## Multi-Exchange Coordination

### Priority Order
1. **Binance** - Highest reliability and speed
2. **KuCoin** - Good cloud compatibility
3. **Coinbase** - Excellent for available coins
4. **CoinGecko** - Always available fallback

### Parallel Processing
```python
from apis.multi_exchange import get_multi_exchange_prices

# Gets prices from all exchanges in parallel
result = get_multi_exchange_prices()
```

The system tries all exchanges simultaneously and returns the best available data.

## Rate Limiting

### Implementation
```python
from utils.rate_limiter import rate_limiter

# Check if request is allowed
if rate_limiter.can_make_request("binance"):
    # Make request
    response = requests.get(url)
    # Record successful request
    rate_limiter.record_request("binance")
```

### Service Limits
- **CoinGecko**: 10 requests/minute
- **Binance**: 100 requests/minute
- **Default**: 30 requests/minute

### Backoff Strategy
When rate limited, the system uses exponential backoff:
- **CoinGecko**: [1, 2, 5, 10] seconds
- **Binance**: [0.5, 1, 2, 3] seconds
- **Default**: [1, 3, 5, 10] seconds

## Error Handling

### Common Errors
1. **Network timeout**: Automatic retry with exponential backoff
2. **Rate limiting**: Automatic backoff and retry
3. **Invalid response**: Falls back to next exchange
4. **API unavailable**: Uses cached data or emergency fallback

### Error Response Format
```json
{
  "prices": {
    "BTC": null,
    "ETH": 3000.0,
    "BNB": null,
    "POL": 0.5
  },
  "errors": [
    "BTC: API timeout",
    "BNB: Rate limited"
  ],
  "success_count": 2,
  "source": "Multi-Exchange"
}
```

## Exchange Rate APIs

### USDT to INR
**Source**: CoinGecko
**Endpoint**: `/simple/price?ids=tether&vs_currencies=inr`

### USD to EUR/AED
**Source**: CoinGecko
**Endpoint**: `/simple/price?ids=tether&vs_currencies=eur`

## Caching Strategy

### Price Caching
- **TTL**: 5 minutes for cryptocurrency prices
- **TTL**: 5 minutes for exchange rates
- **Storage**: In-memory cache with automatic cleanup

### Cache Usage
```python
from utils.cache import cache

# Set cached value
cache.set("btc_price", 50000.0)

# Get cached value
price = cache.get("btc_price", default=0)

# Cache info
info = cache.get_cache_info()
```

## Testing APIs

### Connectivity Test
```python
from apis.multi_exchange import test_all_exchanges

# Test all exchanges
results = test_all_exchanges()
```

### Individual Exchange Tests
```python
from tests.test_apis import test_exchange_apis

# Run API tests
test_exchange_apis()
```

## Best Practices

### For Developers
1. Always check rate limits before making requests
2. Use the multi-exchange system for redundancy
3. Handle errors gracefully with fallbacks
4. Cache responses to reduce API calls
5. Monitor API performance and success rates

### For Deployment
1. Monitor rate limit usage
2. Set up health checks for API endpoints
3. Configure proper timeouts
4. Use connection pooling for better performance
5. Implement logging for debugging

## API Status Monitoring

### Real-time Status
The application provides real-time API status monitoring:
- Working API count
- Individual price availability
- Error reporting
- Response time tracking

### Health Checks
Built-in connectivity testing:
- Tests all exchanges simultaneously
- Reports individual success/failure
- Shows detailed error information
- Measures response times

## Troubleshooting

### Common Issues
1. **All APIs down**: Check internet connectivity
2. **Partial failures**: Normal behavior, fallbacks will work
3. **Rate limiting**: Temporary, will resolve automatically
4. **Stale data**: Cache TTL may need adjustment

### Debug Information
Enable debug logging to see detailed API interactions:
- Request/response details
- Rate limiting decisions
- Cache hit/miss information
- Error details and stack traces
