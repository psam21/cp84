# Cryptocurrency Portfolio Calculator

Real-time cryptocurrency portfolio tracking with multi-exchange price data and currency conversions.

## Features

- **Live Price Data**: Multi-exchange API support (Binance, KuCoin, Coinbase, CoinGecko)
- **Multi-Currency Display**: USD, EUR, AED, INR, and crypto equivalents (BTC, ETH, BNB)
- **Real-time Exchange Rates**: Live USDT/INR, USD/EUR, USD/AED rates
- **Performance Optimized**: Parallel API calls with intelligent caching
- **Responsive UI**: Clean 9-box dashboard layout

## Supported Assets

- **Bitcoin (BTC)** - Digital gold
- **Ethereum (ETH)** - Smart contract platform  
- **Binance Coin (BNB)** - Exchange utility token
- **Polygon (POL)** - Layer 2 scaling solution

## Quick Start

```bash
# Clone and setup
git clone https://github.com/psam21/cp84.git
cd cp84
pip install -r requirements.txt

# Run application
streamlit run app.py
# Access at http://localhost:8501
```

## Architecture

```
cp84/
├── app.py                 # Main application (82 lines)
├── apis/                  # Exchange API integrations
├── utils/                 # Business logic & calculations
├── pages/                 # UI components
└── tests/                 # Test suite
```

## Technical Features

- **Multi-Exchange**: Binance, KuCoin, Coinbase, CoinGecko APIs
- **Parallel Processing**: Concurrent API calls (~1s response time)
- **Rate Limiting**: Smart throttling with usage monitoring
- **Caching**: 60s crypto prices, 5min forex rates
- **Error Handling**: Graceful degradation with partial data

## Dependencies

```txt
streamlit>=1.28.0
requests>=2.31.0
```

## License

MIT License - see repository for details.

### Project Evolution
- **Original**: Comprehensive Bitcoin dashboard with extensive market data
- **Current**: Focused portfolio calculator with multi-currency and exchange rate support
- **Optimization**: Essential files only, improved caching, parallel API processing

## Contributing

Feel free to fork this repository and submit pull requests for improvements. The codebase is designed to be simple and maintainable.

### Potential Enhancements
- Additional cryptocurrency support
- More fiat currency options  
- Historical portfolio tracking
- Export/import portfolio data
- Price alerts and notifications

## License

MIT License - Free to use and modify for personal and commercial projects.

---

**Live Demo**: Deploy to Streamlit Community Cloud with one click!  
**File Size**: Optimized ~67KB (essential files only)  
**API Reliability**: 4-tier fallback system for maximum uptime
