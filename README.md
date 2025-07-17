# Bitcoin Crypto Dashboard

A comprehensive Streamlit application displaying real-time Bitcoin and cryptocurrency data.

## Features

🪙 **Why Bitcoin?** - Educational content about Bitcoin as a store of value
📊 **Bitcoin OHLC** - Weekly Bitcoin price charts with historical data  
🔗 **Mempool Data** - Real-time Bitcoin network statistics and mempool analysis
💼 **Portfolio Calculator** - Calculate and track your cryptocurrency portfolio value

## Live Demo

🚀 **[View Live App](https://your-app-name.streamlit.app)**

## Data Sources

- **Bitcoin OHLC Data**: Bitfinex API
- **Network Stats**: Mempool.space API  
- **Price Data**: Binance API

## Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd cpweb

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Deployment

This app is configured for deployment on Streamlit Community Cloud. Simply connect your GitHub repository to Streamlit Cloud and deploy.

## Features Highlights

- 📈 **Interactive Charts**: Plotly-powered visualizations
- 💾 **Portfolio Persistence**: Save/load portfolio data via CSV
- ⚡ **Real-time Data**: Live cryptocurrency prices and network stats
- 🎨 **Modern UI**: Custom CSS styling with gradient themes
- 📱 **Responsive**: Works on desktop and mobile devices

## Technical Stack

- **Frontend**: Streamlit
- **Visualization**: Plotly
- **Data Processing**: Pandas
- **APIs**: Bitfinex, Mempool.space, Binance
- **Deployment**: Streamlit Community Cloud
