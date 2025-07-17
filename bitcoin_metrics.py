"""
Bitcoin Metrics API Module
Fetches comprehensive Bitcoin data from multiple sources for professional visualization.
Optimized for Streamlit Community Cloud deployment.
"""
import requests
import json
from datetime import datetime, timedelta

class BitcoinMetrics:
    """Class to fetch and manage Bitcoin metrics from various APIs"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'StreamlitApp/1.0',
            'Accept': 'application/json',
            'Connection': 'close'
        }
        self.timeout = 8
    
    def safe_request(self, url, params=None):
        """Make a safe API request with error handling"""
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ API request failed for {url}: {str(e)}")
            return None
    
    def get_price_coindesk(self):
        """Get Bitcoin price from CoinDesk API"""
        url = "https://api.coindesk.com/v1/bpi/currentprice.json"
        data = self.safe_request(url)
        if data and 'bpi' in data and 'USD' in data['bpi']:
            return {
                'price_usd': float(data['bpi']['USD']['rate'].replace(',', '')),
                'last_updated': data.get('time', {}).get('updated', 'Unknown'),
                'source': 'CoinDesk'
            }
        return None
    
    def get_coingecko_data(self):
        """Get comprehensive Bitcoin data from CoinGecko"""
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': 'bitcoin',
            'vs_currencies': 'usd,eur,gbp,inr',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true',
            'include_last_updated_at': 'true'
        }
        data = self.safe_request(url, params)
        if data and 'bitcoin' in data:
            btc_data = data['bitcoin']
            return {
                'price_usd': btc_data.get('usd'),
                'price_eur': btc_data.get('eur'),
                'price_gbp': btc_data.get('gbp'),
                'price_inr': btc_data.get('inr'),
                'market_cap_usd': btc_data.get('usd_market_cap'),
                'volume_24h': btc_data.get('usd_24h_vol'),
                'change_24h': btc_data.get('usd_24h_change'),
                'last_updated': btc_data.get('last_updated_at'),
                'source': 'CoinGecko'
            }
        return None
    
    def get_fear_greed_index(self):
        """Get Fear & Greed Index"""
        url = "https://api.alternative.me/fng/"
        data = self.safe_request(url)
        if data and 'data' in data and len(data['data']) > 0:
            fng_data = data['data'][0]
            return {
                'value': int(fng_data.get('value', 0)),
                'classification': fng_data.get('value_classification', 'Unknown'),
                'timestamp': fng_data.get('timestamp', ''),
                'source': 'Alternative.me'
            }
        return None
    
    def get_blockchain_info_simple(self, endpoint):
        """Get simple data from blockchain.info"""
        url = f"https://blockchain.info/q/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return float(response.text.strip())
        except Exception as e:
            print(f"❌ Blockchain.info {endpoint} failed: {str(e)}")
            return None
    
    def get_blockchain_chart(self, chart_type, timespan="1weeks"):
        """Get chart data from blockchain.info"""
        url = f"https://api.blockchain.info/charts/{chart_type}"
        params = {'timespan': timespan, 'format': 'json'}
        data = self.safe_request(url, params)
        if data and 'values' in data:
            return {
                'values': data['values'],
                'name': data.get('name', chart_type),
                'unit': data.get('unit', ''),
                'description': data.get('description', ''),
                'source': 'Blockchain.info'
            }
        return None
    
    def get_bitnodes_data(self):
        """Get Bitcoin node data from Bitnodes"""
        url = "https://bitnodes.io/api/v1/snapshots/latest/"
        data = self.safe_request(url)
        if data:
            return {
                'total_nodes': data.get('total_nodes', 0),
                'timestamp': data.get('timestamp', 0),
                'nodes_by_country': data.get('nodes', {}),
                'source': 'Bitnodes'
            }
        return None
    
    def get_lightning_network_data(self):
        """Get Lightning Network statistics"""
        url = "https://1ml.com/statistics?json=true"
        data = self.safe_request(url)
        if data:
            return {
                'total_capacity': data.get('total_capacity', 0),
                'node_count': data.get('node_count', 0),
                'channel_count': data.get('channel_count', 0),
                'avg_capacity': data.get('avg_capacity', 0),
                'source': '1ML'
            }
        return None
    
    def get_global_crypto_data(self):
        """Get global cryptocurrency market data"""
        url = "https://api.coingecko.com/api/v3/global"
        data = self.safe_request(url)
        if data and 'data' in data:
            global_data = data['data']
            return {
                'total_market_cap_usd': global_data.get('total_market_cap', {}).get('usd', 0),
                'total_volume_24h': global_data.get('total_volume', {}).get('usd', 0),
                'btc_dominance': global_data.get('market_cap_percentage', {}).get('btc', 0),
                'active_cryptocurrencies': global_data.get('active_cryptocurrencies', 0),
                'markets': global_data.get('markets', 0),
                'source': 'CoinGecko'
            }
        return None
    
    def get_btc_historical_data(self, days=30):
        """Get historical Bitcoin price data"""
        url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'daily' if days <= 90 else 'weekly'
        }
        data = self.safe_request(url, params)
        if data:
            return {
                'prices': data.get('prices', []),
                'market_caps': data.get('market_caps', []),
                'total_volumes': data.get('total_volumes', []),
                'source': 'CoinGecko'
            }
        return None
    
    def get_all_basic_metrics(self):
        """Get all basic blockchain metrics in one call"""
        metrics = {}
        
        # Simple blockchain.info queries
        simple_metrics = {
            'mining_difficulty': 'getdifficulty',
            'block_reward': 'bcperblock', 
            'block_count': 'getblockcount',
            'total_supply': 'totalbc'
        }
        
        for metric_name, endpoint in simple_metrics.items():
            value = self.get_blockchain_info_simple(endpoint)
            if value is not None:
                metrics[metric_name] = value
        
        return metrics
    
    def get_comprehensive_metrics(self):
        """Get all Bitcoin metrics for the dashboard"""
        print("🔄 Fetching comprehensive Bitcoin metrics...")
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'errors': []
        }
        
        # Price data
        try:
            coindesk_price = self.get_price_coindesk()
            if coindesk_price:
                metrics['coindesk_price'] = coindesk_price
            else:
                metrics['errors'].append("CoinDesk price API failed")
        except Exception as e:
            metrics['errors'].append(f"CoinDesk error: {str(e)}")
        
        # CoinGecko comprehensive data
        try:
            coingecko_data = self.get_coingecko_data()
            if coingecko_data:
                metrics['coingecko'] = coingecko_data
            else:
                metrics['errors'].append("CoinGecko API failed")
        except Exception as e:
            metrics['errors'].append(f"CoinGecko error: {str(e)}")
        
        # Fear & Greed Index
        try:
            fng_data = self.get_fear_greed_index()
            if fng_data:
                metrics['fear_greed'] = fng_data
            else:
                metrics['errors'].append("Fear & Greed Index API failed")
        except Exception as e:
            metrics['errors'].append(f"Fear & Greed error: {str(e)}")
        
        # Basic blockchain metrics
        try:
            basic_metrics = self.get_all_basic_metrics()
            if basic_metrics:
                metrics['blockchain'] = basic_metrics
            else:
                metrics['errors'].append("Blockchain.info basic metrics failed")
        except Exception as e:
            metrics['errors'].append(f"Blockchain.info error: {str(e)}")
        
        # Global crypto data
        try:
            global_data = self.get_global_crypto_data()
            if global_data:
                metrics['global'] = global_data
            else:
                metrics['errors'].append("Global crypto data failed")
        except Exception as e:
            metrics['errors'].append(f"Global crypto error: {str(e)}")
        
        # Chart data (optional - might be slower)
        chart_types = ['hash-rate', 'n-transactions', 'estimated-transaction-volume-usd', 
                      'miners-revenue', 'transaction-fees-usd', 'mempool-size', 
                      'n-active-addresses', 'avg-block-time', 'avg-block-size']
        
        metrics['charts'] = {}
        for chart_type in chart_types:
            try:
                chart_data = self.get_blockchain_chart(chart_type)
                if chart_data:
                    metrics['charts'][chart_type] = chart_data
                else:
                    metrics['errors'].append(f"{chart_type} chart failed")
            except Exception as e:
                metrics['errors'].append(f"{chart_type} chart error: {str(e)}")
        
        print(f"✅ Metrics collection complete. Errors: {len(metrics['errors'])}")
        return metrics

# Create a global instance
bitcoin_metrics = BitcoinMetrics()
