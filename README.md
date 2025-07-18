# Bitcoin Crypto Dashboard

A comprehensive Streamlit application displaying real-time Bitcoin and cryptocurrency data with advanced portfolio management and network analytics.

## 🚀 Features

🪙 **Why Bitcoin?** - Educational content about Bitcoin as the ultimate store of value  
📊 **Bitcoin OHLC** - Weekly Bitcoin price charts with 12+ years of historical data  
🔗 **Mempool Data** - Real-time Bitcoin network statistics, fees, and mining analytics  
💼 **Portfolio Calculator** - Track multiple cryptocurrencies with live market data  
📈 **Bitcoin Metrics** - Comprehensive dashboard with 27+ metrics from multiple sources  
🔍 **Debug Logs** - Advanced session analytics and troubleshooting tools

## 🎯 Live Demo

🚀 **[View Live App](https://your-app-name.streamlit.app)** *(Ready for Streamlit Community Cloud)*

## 🏗️ Architecture & Data Sources

### Multi-Exchange Price System
- **Primary**: Binance API (real-time prices)
- **Fallback**: KuCoin → Coinbase → CoinGecko (automatic failover)
- **Coverage**: BTC, ETH, BNB, POL with robust error handling

### Bitcoin Network Data
- **OHLC Data**: Bitfinex API (2013-present)
- **Network Stats**: Mempool.space API (fees, blocks, difficulty)
- **Hash Rate**: Blockchain.info API (TH/s to EH/s conversion)
- **Metrics**: CoinGecko, CoinDesk, Fear & Greed Index, Global data

### Portfolio Management
- **Session-based**: Cloud-friendly data persistence
- **Multi-currency**: USD, INR, BTC equivalent calculations
- **Real-time**: Live portfolio valuation with API status tracking

## 🛠️ Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd cpweb

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## 🚀 Automated Deployment

This project includes an advanced deployment automation script with comprehensive logging and error handling:

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

### Deployment Features
- 📊 **Comprehensive Logging**: All operations logged to `deployment_logs/`
- 🛡️ **Error Recovery**: Robust error handling with actionable suggestions  
- 🎯 **Smart Commits**: Intelligent commit message generation
- 📈 **Session Analytics**: Track deployment performance and success rates
- 🔄 **Interactive Menu**: Step-by-step deployment control

## ✨ Features Highlights

### User Experience
- 📈 **Interactive Charts**: Plotly-powered visualizations with custom styling
- 💾 **Smart Portfolio**: Auto-save/load functionality with session persistence
- ⚡ **Real-time Updates**: Live cryptocurrency prices with multi-source reliability
- 🎨 **Modern UI**: Custom CSS with gradient themes and responsive design
- 📱 **Mobile-Friendly**: Optimized for all device sizes

### Technical Excellence
- 🔄 **API Resilience**: Multi-exchange fallback system prevents data outages
- 📊 **Advanced Analytics**: 27+ Bitcoin metrics with historical trends
- 🛡️ **Error Handling**: Graceful degradation for all network and API failures
- 🔍 **Debug Tools**: Comprehensive logging and session monitoring
- ⚡ **Performance**: Smart caching and optimized data fetching

### Cloud-Ready Architecture
- 🌐 **No File Dependencies**: Everything API-based for cloud deployment
- 💨 **Headless Optimized**: Streamlit configuration for cloud environments
- 🔒 **Secure**: No hardcoded secrets, environment-based configuration
- 📈 **Scalable**: Efficient resource usage and memory management

## Technical Stack

- **Frontend**: Streamlit
- **Visualization**: Plotly
- **Data Processing**: Pandas
- **APIs**: Bitfinex, Mempool.space, Binance
- **Deployment**: Streamlit Community Cloud
