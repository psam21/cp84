# Cryptocurrency Portfolio Calculator

Real-time cryptocurrency portfolio tracking with multi-exchange price data and currency conversions.

## 🎯 Key Features

- **Live Price Data**: Multi-exchange API support (Binance, KuCoin, Coinbase, CoinGecko)
- **Real-time Updates**: Portfolio values update instantly on input changes (including Tab navigation)
- **Multi-Currency Display**: USD, EUR, AED, INR, and crypto equivalents (BTC, ETH, BNB)
- **Market Sentiment**: Real-time Fear & Greed Index with visual indicators
- **Professional UI**: Clean, center-aligned interface optimized for user experience
- **Performance Optimized**: Parallel API calls with intelligent caching (~1s response time)
- **Production Ready**: Comprehensive error handling and graceful API fallbacks

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

# Run production readiness check
chmod +x deploy_check.sh
./deploy_check.sh

# Run application
streamlit run app.py
# Access at http://localhost:8501
```

## 🚀 Production Deployment

The application is production-ready with comprehensive testing:

```bash
# Quick deployment verification
./deploy_check.sh

# Deploy to Streamlit Cloud
# 1. Push to GitHub
# 2. Connect to Streamlit Cloud
# 3. Deploy with one click
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

- **Multi-Exchange**: Binance, KuCoin, Coinbase, CoinGecko APIs with 4-tier fallback
- **Market Psychology**: Alternative.me Fear & Greed Index integration
- **Parallel Processing**: Concurrent API calls (~1s response time)
- **Rate Limiting**: Smart throttling with usage monitoring
- **Real-time Updates**: Tab/focus change handling for instant portfolio calculations
- **Caching**: 60s crypto prices, 5min forex rates, 5min sentiment data
- **Error Handling**: Graceful degradation with partial data display
- **UI Optimization**: Center-aligned cards, hidden management controls, professional layout

## Dependencies

```txt
streamlit>=1.28.0
requests>=2.31.0
```

## License

MIT License - see repository for details.

### Project Evolution
- **Original**: Comprehensive Bitcoin dashboard with extensive market data
- **v2.0**: Focused portfolio calculator with multi-currency and exchange rate support  
- **v2.1**: UI optimization with center alignment, hidden management controls, real-time updates
- **Production**: Enhanced error handling, parallel API processing, comprehensive testing

## 🧪 Testing & Quality Assurance

```bash
# Run production readiness tests
./deploy_check.sh

# Manual testing checklist:
# ✅ All 4 cryptocurrencies display correctly
# ✅ Portfolio values update in real-time on input changes
# ✅ Tab navigation triggers immediate recalculations
# ✅ Currency conversions work (USD, EUR, AED, INR)
# ✅ Crypto equivalents display (BTC, ETH, BNB)
# ✅ API fallbacks work when services are down
# ✅ Fear & Greed Index displays correctly
# ✅ Responsive design works on different screen sizes
```

## Contributing

Feel free to fork this repository and submit pull requests for improvements. The codebase is designed to be simple and maintainable.

### Potential Enhancements
- Additional cryptocurrency support
- More fiat currency options  
- Historical portfolio tracking
- Export/import portfolio data
- Price alerts and notifications
- Historical Fear & Greed Index trends
- Advanced sentiment analysis features

## License

MIT License - Free to use and modify for personal and commercial projects.

---

**🎯 Production Status**: Ready for deployment  
**🔧 Latest Updates**: Real-time portfolio calculations, optimized UI, hidden admin controls  
**⚡ Performance**: ~1s API response time with 4-exchange fallback  
**🛡️ Reliability**: Comprehensive error handling and graceful degradation  
**📱 UI/UX**: Professional center-aligned interface optimized for user experience
