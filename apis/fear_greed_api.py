"""
Crypto Fear & Greed Index API Integration
========================================

Fetches the Fear & Greed Index from Alternative.me API
Provides current market sentiment data (0-100 scale)
"""

import requests
import time
from typing import Dict, Optional, Tuple, Any
from utils.logging import debug_log
from utils.rate_limiter import rate_limiter

# Cache for Fear & Greed data (updates daily, so we can cache longer)
_fear_greed_cache = {
    'data': None,
    'timestamp': 0,
    'cache_duration': 300  # 5 minutes cache
}

def get_fear_greed_index() -> Optional[Dict[str, Any]]:
    """
    Fetch the current Fear & Greed Index from Alternative.me API
    
    Returns:
        Dict with keys: value, value_classification, timestamp, time_until_update
        None if API fails
    """
    try:
        # Check cache first
        current_time = time.time()
        if (_fear_greed_cache['data'] and 
            current_time - _fear_greed_cache['timestamp'] < _fear_greed_cache['cache_duration']):
            debug_log("🔄 Using cached Fear & Greed data", "INFO", "fear_greed_cache")
            return _fear_greed_cache['data']
        
        # Check rate limit
        if not rate_limiter.can_make_request("fear_greed"):
            debug_log("⚠️ Fear & Greed API rate limit reached", "WARNING", "fear_greed_rate_limit")
            return _fear_greed_cache['data']  # Return cached data if available
        
        debug_log("🔍 Fetching Fear & Greed Index from Alternative.me", "INFO", "fear_greed_fetch")
        
        # API request
        url = "https://api.alternative.me/fng/"
        headers = {
            'User-Agent': 'Crypto Portfolio Calculator/1.0',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            rate_limiter.record_request("fear_greed")
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                latest_data = data['data'][0]
                
                # Extract relevant information
                result = {
                    'value': int(latest_data['value']),
                    'value_classification': latest_data['value_classification'],
                    'timestamp': latest_data['timestamp'],
                    'time_until_update': latest_data.get('time_until_update', 'Unknown')
                }
                
                # Update cache
                _fear_greed_cache['data'] = result
                _fear_greed_cache['timestamp'] = current_time
                
                debug_log(f"✅ Fear & Greed Index: {result['value']} - {result['value_classification']}", 
                         "SUCCESS", "fear_greed_success")
                return result
            else:
                debug_log("❌ Invalid response format from Fear & Greed API", "ERROR", "fear_greed_parse")
                return None
                
        else:
            debug_log(f"❌ Fear & Greed API HTTP {response.status_code}: {response.text[:100]}", 
                     "ERROR", "fear_greed_http")
            return None
            
    except requests.exceptions.RequestException as e:
        debug_log(f"❌ Fear & Greed API network error: {str(e)}", "ERROR", "fear_greed_network")
        return None
    except Exception as e:
        debug_log(f"❌ Fear & Greed API unexpected error: {str(e)}", "ERROR", "fear_greed_unexpected")
        return None

def test_fear_greed_connectivity() -> Tuple[bool, str]:
    """
    Test connectivity to the Fear & Greed API
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        url = "https://api.alternative.me/fng/"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return True, f"✅ Alternative.me Fear & Greed API (HTTP {response.status_code})"
        else:
            return False, f"⚠️ Alternative.me Fear & Greed API (HTTP {response.status_code})"
            
    except Exception as e:
        return False, f"❌ Alternative.me Fear & Greed API: {str(e)}"

def clear_fear_greed_cache():
    """Clear the Fear & Greed Index cache"""
    global _fear_greed_cache
    _fear_greed_cache['data'] = None
    _fear_greed_cache['timestamp'] = 0
    debug_log("🔄 Fear & Greed cache cleared", "INFO", "fear_greed_cache_clear")
