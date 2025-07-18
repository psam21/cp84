# 🪙 Bitcoin Crypto Dashboard

A comprehensive Streamlit application displaying real-time Bitcoin and cryptocurrency data with advanced portfolio management, network analytics, and interactive visualizations.

## 🚀 Live Demo

🌐 **[View Live App](https://psam21.streamlit.app/)** - *Deployed on Streamlit Community Cloud*

## ✨ Key Features

### 📊 **Six Comprehensive Dashboards**
🪙 **Why Bitcoin?** - Educational content about Bitcoin as the ultimate store of value  
� **Bitcoin OHLC** - Interactive weekly Bitcoin price charts with 12+ years of historical data (2013-present)  
🔗 **Mempool Data** - Real-time Bitcoin network statistics, transaction fees, and mining analytics  
💼 **Portfolio Calculator** - Multi-cryptocurrency portfolio tracker with live market data  
� **Bitcoin Metrics** - Advanced dashboard with 30+ metrics from multiple data sources  
🔍 **Debug Logs** - Comprehensive session analytics and troubleshooting tools  

### 🎯 **Advanced Visualizations**
- **Interactive Gauge Meters**: Fear & Greed Index with color-coded zones
- **Real-time Charts**: Mempool blocks, mining pools, hash rate trends
- **Portfolio Overview**: Custom-styled boxes with gradient themes and hover effects
- **Responsive Design**: Mobile-optimized with adaptive layouts

### 💡 **Smart Features**
- **Multi-Exchange Price System**: Binance → KuCoin → Coinbase → CoinGecko fallback chain
- **Session-Based Portfolio**: Cloud-friendly data persistence without file dependencies
- **API Status Monitoring**: Real-time tracking of data source health with transparent error handling
- **Custom CSS Styling**: Modern gradient themes with consistent typography

## 🏗️ Architecture & Data Sources

### Multi-Exchange Price System
- **Primary**: Binance API (real-time prices)
- **Fallback Chain**: KuCoin → Coinbase → CoinGecko (automatic failover)
- **Coverage**: BTC, ETH, BNB, POL with robust error handling
- **Status Tracking**: Live API health monitoring with user feedback

### Bitcoin Network Data
- **OHLC Data**: Bitfinex API (2013-present, 12+ years of weekly data)
- **Network Stats**: Mempool.space API (fees, blocks, difficulty, mining pools)
- **Hash Rate**: Blockchain.info API with proper TH/s to EH/s conversion
- **Comprehensive Metrics**: CoinGecko, Alternative.me (Fear & Greed), Global market data

### Portfolio Management
- **Session-Based**: Cloud-friendly data persistence using Streamlit session state
- **Multi-Currency**: USD, INR, BTC equivalent calculations with live exchange rates
- **Real-Time Valuation**: Live portfolio tracking with API status indicators
- **Smart Analytics**: Asset distribution, largest holdings, portfolio statistics

## 🛠️ Local Development

```bash
# Clone the repository
git clone https://github.com/psam21/cp.git
cd cp

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## 🚀 Automated Deployment System

This project features an enterprise-grade deployment automation script with comprehensive logging and error handling:

```bash
# Quick deployment (automated)
python deploy.py --quick

# Interactive deployment (step-by-step)
python deploy.py

# Check repository status
python deploy.py --status

# View deployment logs
python deploy.py --logs
```

### 🎯 Deployment Features
- 📊 **Comprehensive Logging**: All operations logged to `deployment_logs/` with timestamps
- 🛡️ **Error Recovery**: Robust error handling with actionable suggestions and retry logic
- 🎯 **Smart Commits**: Intelligent commit message generation based on file changes
- 📈 **Session Analytics**: Track deployment performance, success rates, and operation history
- 🔄 **Interactive Menu**: Step-by-step deployment control with validation checks
- ⚡ **Performance Optimization**: Efficient git operations with connection reuse

## ✨ Enhanced Features & User Experience

### 🎨 **Modern UI/UX**
- **Interactive Charts**: Plotly-powered visualizations with custom styling and hover effects
- **Smart Portfolio Display**: 4-box layout with gradient themes and responsive design
- **Fear & Greed Gauge**: Interactive meter with color-coded sentiment zones
- **Mobile-Optimized**: Adaptive layouts for all device sizes with consistent typography
- **Custom CSS**: Gradient themes, hover animations, and professional styling

### 🔧 **Technical Excellence**
- **API Resilience**: Multi-exchange fallback system prevents data outages
- **Advanced Analytics**: 30+ Bitcoin metrics with historical trends and real-time updates
- **Comprehensive Error Handling**: Graceful degradation for all network and API failures
- **Debug Tools**: Session monitoring, log filtering, export capabilities
- **Performance Optimization**: Smart caching, optimized data fetching, and memory management

### 🌐 **Cloud-Ready Architecture**
- **Zero File Dependencies**: Everything API-based for seamless cloud deployment
- **Session State Management**: Efficient data persistence without local storage
- **Headless Optimized**: Streamlit configuration for cloud environments
- **Security Best Practices**: No hardcoded secrets, environment-based configuration
- **Scalable Design**: Efficient resource usage and horizontal scaling support

### � **Advanced Analytics & Monitoring**
- **Real-Time Network Health**: Mempool size, hash rate, difficulty adjustments
- **Mining Pool Distribution**: Visual pie charts with top 6 mining pools
- **Transaction Fee Analysis**: Color-coded priority levels with confirmation times
- **Bitcoin Halving Countdown**: Precise calculations with cycle progress tracking
- **Portfolio Statistics**: Asset distribution, largest holdings, performance metrics

## 🎯 Feature Highlights by Page

### 🪙 Why Bitcoin?
- **Educational Content**: Comprehensive explanation of Bitcoin's value proposition
- **Two-Column Layout**: Key characteristics and Bitcoin's legacy
- **Investment Case**: Digital gold, resistance money, and future of finance

### �📈 Bitcoin OHLC
- **Historical Data**: 12+ years of weekly Bitcoin price data (2013-present)
- **Interactive Charts**: Plotly candlestick charts with yearly navigation
- **Year Selection**: Easy navigation through Bitcoin's price history
- **Data Refresh**: Manual data refresh with loading indicators

### 🔗 Mempool Data
- **Real-Time Fees**: Color-coded transaction fee recommendations
- **Network Health**: 4-metric dashboard with current network status
- **Mempool Visualization**: Upcoming blocks with fee levels and transaction counts
- **Mining Analytics**: Pool distribution and difficulty adjustment tracking
- **Recent Blocks**: Latest 6 blocks with transaction counts and sizes

### 💼 Portfolio Calculator
- **Multi-Asset Support**: BTC, ETH, BNB, POL with live price tracking
- **Beautiful UI**: Custom-styled boxes with gradient backgrounds
- **Real-Time Valuation**: USD, INR, and BTC equivalent calculations
- **Portfolio Management**: Save/load defaults, clear all functionality
- **API Status**: Transparent tracking of price feed health

### 📊 Bitcoin Metrics Dashboard
- **Comprehensive Data**: 30+ metrics from multiple reliable sources
- **Interactive Gauge**: Fear & Greed Index with color-coded sentiment zones
- **Global Prices**: Multi-currency support (USD, EUR, GBP, INR)
- **Supply Metrics**: Circulating supply, mining difficulty, block rewards
- **Network Charts**: Transaction trends, hash rate evolution, economic indicators
- **Halving Tracker**: Precise countdown with cycle progress and statistics

### 🔍 Debug Logs
- **Session Analytics**: Comprehensive tracking of user interactions and system events
- **Log Filtering**: Filter by level, context, and detailed information
- **Export Capabilities**: Download session reports and raw JSON data
- **Real-Time Monitoring**: Live log updates with auto-refresh option
- **Performance Insights**: API call tracking, data operation monitoring

## 🛠️ Technical Stack

- **Frontend Framework**: Streamlit 1.39.0
- **Data Visualization**: Plotly 5.24.1 (Interactive charts, gauges, candlestick plots)
- **Data Processing**: Pandas 2.2.3 (Data manipulation and analysis)
- **HTTP Requests**: Requests 2.32.3 (API communication with timeout handling)
- **Date/Time**: DateTime (Built-in Python module for time calculations)

## 🌐 Data Sources & APIs

### Real-Time Cryptocurrency Data
- **Binance API**: Primary source for BTC, ETH, BNB, POL prices
- **KuCoin API**: Secondary fallback for price data
- **Coinbase API**: Tertiary fallback for price reliability
- **CoinGecko API**: Final fallback with comprehensive market data

### Bitcoin Network & Blockchain Data
- **Mempool.space API**: Real-time Bitcoin network statistics, mempool analysis
- **Blockchain.info API**: Historical data, hash rate, mining difficulty
- **Bitfinex API**: 12+ years of OHLC data (2013-present)

### Market Sentiment & Analysis
- **Alternative.me API**: Fear & Greed Index with sentiment analysis
- **CoinGecko Global API**: Market dominance and global cryptocurrency statistics
- **CoinDesk API**: Bitcoin price index and market data

## 🚀 Deployment & Production

### Streamlit Community Cloud Optimizations
- **Headless Configuration**: Optimized for cloud deployment
- **Session State Management**: Efficient data persistence
- **Error Handling**: Comprehensive API failure recovery
- **Performance Caching**: Smart data caching with TTL
- **Mobile Responsive**: Cross-device compatibility

### Production Features
- **Automated Deployment**: Enterprise-grade deployment automation
- **Comprehensive Logging**: All operations tracked with timestamps
- **Error Recovery**: Robust handling with actionable error messages
- **Session Analytics**: Performance metrics and success rate tracking
- **Health Monitoring**: Real-time API status and connectivity checks

## 🔧 Configuration

### Environment Setup
```bash
# Required Python version
Python 3.8+

# Core dependencies
streamlit>=1.39.0
plotly>=5.24.1
pandas>=2.2.3
requests>=2.32.3
```

### Streamlit Configuration
```toml
[theme]
primaryColor = "#f7931a"  # Bitcoin orange
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[server]
headless = true
enableCORS = false
enableXsrfProtection = false
```

## 📈 Performance & Scalability

### Expected Performance
- **Load Time**: 3-5 seconds (due to API calls)
- **Memory Usage**: ~100-150MB (typical for Streamlit apps)
- **API Calls**: Rate-limited and cached for optimal performance
- **Data Refresh**: Configurable TTL caching (5-minute default)
- **Uptime**: High reliability with multi-exchange fallbacks

### Scalability Features
- **API Rate Limiting**: Respectful API usage with proper delays
- **Connection Pooling**: Efficient HTTP connection reuse
- **Memory Management**: Optimized data structures and garbage collection
- **Error Boundaries**: Isolated failures don't crash the entire app
- **Graceful Degradation**: Partial functionality during API outages

## 🛡️ Security & Best Practices

- **No Hardcoded Secrets**: Environment-based configuration
- **API Key Management**: Secure handling of authentication tokens
- **Input Validation**: Proper sanitization of user inputs
- **Error Sanitization**: No sensitive information in error messages
- **HTTPS Only**: Secure communication with all APIs
- **Rate Limiting**: Respectful API usage patterns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit Team**: For the amazing framework
- **Plotly**: For powerful visualization capabilities
- **API Providers**: Binance, Mempool.space, CoinGecko, and others for reliable data
- **Bitcoin Community**: For inspiration and continuous innovation

---

**Built with ❤️ for the Bitcoin community**

*Empowering users with comprehensive Bitcoin and cryptocurrency analytics through modern web technology.*
