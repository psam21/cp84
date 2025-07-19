# Portfolio Value Calculator

A streamlined cryptocurrency portfolio calculator built with Streamlit, featuring real-time price tracking and multi-currency support.

## Features

- **Real-time Price Data**: Fetches live cryptocurrency prices from multiple exchanges with parallel processing
- **Multi-currency Portfolio**: View portfolio value in USD, EUR, AED, INR, and crypto equivalents (BTC, ETH, BNB)
- **Live Exchange Rates**: Real-time USDT/INR, USD/EUR, and USD/AED exchange rates
- **9-Box Dashboard**: Clean, uniform layout with equal-sized value boxes
- **Robust API System**: Multi-exchange fallback system (Binance → KuCoin → Coinbase → CoinGecko)
- **Optimized Performance**: Concurrent API calls with intelligent caching (60s crypto prices, 5min forex rates)

## Portfolio Display

The application features a clean 9-box layout showing:

**Portfolio Values:**
- 💰 USD Value - Total portfolio in US Dollars
- 💶 EUR Value - Total portfolio in Euros  
- 🏛️ AED Value - Total portfolio in UAE Dirhams
- 🇮🇳 INR Value - Total portfolio in Indian Rupees

**Crypto Equivalents:**
- ₿ BTC Equivalent - Portfolio value in Bitcoin
- ⟠ ETH Equivalent - Portfolio value in Ethereum
- 🟡 BNB Equivalent - Portfolio value in Binance Coin

**Live Rates:**
- 💱 USDT/INR Rate - Real-time Tether to Indian Rupee exchange rate
- 🔄 Last Updated - Timestamp of latest price refresh

## Default Portfolio

The application comes with preset holdings:
- **Bitcoin (BTC)**: 0.9997
- **Ethereum (ETH)**: 9.9983
- **Binance Coin (BNB)**: 29.5623
- **Polygon (POL)**: 4986.01

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/psam21/cp.git
   cd cp
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

4. **Access the app**: Open your browser to `http://localhost:8501`

## Project Structure

```
cp/
├── app.py                 # Main Streamlit application
├── multi_exchange.py      # Multi-exchange price fetching system
├── binance_data.py        # Binance API integration
├── coinbase_data.py       # Coinbase API integration  
├── kucoin_data.py         # KuCoin API integration
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## Technical Details

### Dependencies
- `streamlit>=1.28.0` - Web application framework
- `requests>=2.31.0` - HTTP library for API calls

### API Architecture
- **Primary Source**: Binance API for crypto prices
- **Fallback Chain**: KuCoin → Coinbase → CoinGecko APIs
- **Parallel Processing**: Concurrent API calls for faster response times
- **Exchange Rates**: CoinGecko for USD/EUR & USD/AED, Binance P2P for USDT/INR
- **Caching Strategy**: 60-second TTL for crypto prices, 5-minute TTL for forex rates

### Performance Optimizations
- Concurrent futures for parallel API execution
- Streamlit session state for portfolio persistence
- Intelligent error handling and graceful API fallbacks
- Minimal dependencies for faster cloud deployment

## Usage

### Portfolio Management
1. **View Real-time Values**: The 9-box dashboard displays live portfolio values in multiple currencies
2. **Edit Holdings**: Click any cryptocurrency amount to modify your holdings
3. **Refresh Data**: Click "🔄 Force Refresh Prices" for latest market data
4. **Portfolio Controls**: Use "Reset to Default" or "Clear All" buttons to manage holdings

### Interface Features
- **Responsive Design**: Uniform 110px × 120px boxes with mobile-friendly layout
- **Live Updates**: Automatic refresh every 60 seconds for crypto prices
- **Visual Indicators**: Color-coded boxes with currency symbols and emojis
- **Error Handling**: Clear status messages for API failures or connectivity issues

## API Sources & Reliability

The application uses a robust multi-source approach for maximum uptime:

**Cryptocurrency Prices:**
- Binance API (Primary) - Highest reliability and speed
- KuCoin API (Fallback) - Secondary data source
- Coinbase API (Fallback) - Additional reliability layer
- CoinGecko API (Final fallback) - Free tier, no authentication required

**Exchange Rates:**
- CoinGecko API - USD/EUR and USD/AED rates
- Binance P2P API - Live USDT/INR trading rates
## Development Notes

This is a streamlined version of the original Bitcoin dashboard, optimized for:
- **Portfolio-focused functionality** - Removed Bitcoin metrics, mempool data, and market analysis
- **Multi-currency support** - Added EUR, AED currencies alongside USD, INR
- **Performance optimization** - Reduced from 150KB+ to ~67KB essential files only
- **Cloud deployment** - Optimized for Streamlit Community Cloud with robust API fallbacks

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
