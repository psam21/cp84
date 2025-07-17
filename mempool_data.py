"""
Module to fetch mempool data.
"""
import requests

def get_mempool_info():
    """
    Fetches comprehensive mempool information.
    """
    try:
        # Get recommended fees
        fees_response = requests.get("https://mempool.space/api/v1/fees/recommended", timeout=10)
        fees_response.raise_for_status()
        fees = fees_response.json()
        
        # Get mempool statistics
        mempool_response = requests.get("https://mempool.space/api/v1/fees/mempool-blocks", timeout=10)
        mempool_response.raise_for_status()
        mempool_blocks = mempool_response.json()
        
        # Get difficulty adjustment
        difficulty_response = requests.get("https://mempool.space/api/v1/difficulty-adjustment", timeout=10)
        difficulty_response.raise_for_status()
        difficulty = difficulty_response.json()
        
        # Get latest block information
        blocks_response = requests.get("https://mempool.space/api/v1/blocks", timeout=10)
        blocks_response.raise_for_status()
        latest_blocks = blocks_response.json()
        
        # Get mining pool stats
        mining_response = requests.get("https://mempool.space/api/v1/mining/pools/1w", timeout=10)
        mining_response.raise_for_status()
        mining_pools = mining_response.json()
        
        # Get fee histogram - this endpoint might not exist, so handle gracefully
        fee_histogram = []
        try:
            fee_hist_response = requests.get("https://mempool.space/api/v1/fees/histogram", timeout=10)
            if fee_hist_response.status_code == 200:
                fee_histogram = fee_hist_response.json()
        except:
            pass
        
        return {
            'fees': fees,
            'mempool_blocks': mempool_blocks,
            'difficulty': difficulty,
            'latest_blocks': latest_blocks[:5],  # Show only latest 5 blocks
            'mining_pools': mining_pools,
            'fee_histogram': fee_histogram
        }
    except requests.exceptions.RequestException as e:
        return {'error': f'Network error: {str(e)}'}
    except ValueError as e:
        return {'error': f'JSON parsing error: {str(e)}'}
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}

def get_mempool_stats():
    """
    Fetches additional mempool statistics.
    """
    try:
        # Get network statistics - this endpoint might not exist
        network_stats = {}
        try:
            stats_response = requests.get("https://mempool.space/api/v1/statistics", timeout=10)
            if stats_response.status_code == 200:
                network_stats = stats_response.json()
        except:
            pass
        
        # Get hashrate
        hashrate_response = requests.get("https://mempool.space/api/v1/mining/hashrate/1w", timeout=10)
        hashrate_response.raise_for_status()
        hashrate = hashrate_response.json()
        
        # Get mempool size over time - this endpoint might not exist
        mempool_size = []
        try:
            mempool_size_response = requests.get("https://mempool.space/api/v1/statistics/2h", timeout=10)
            if mempool_size_response.status_code == 200:
                mempool_size = mempool_size_response.json()
        except:
            pass
        
        return {
            'network_stats': network_stats,
            'hashrate': hashrate,
            'mempool_size': mempool_size
        }
    except requests.exceptions.RequestException as e:
        return {'error': f'Network error: {str(e)}'}
    except ValueError as e:
        return {'error': f'JSON parsing error: {str(e)}'}
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}
