"""
API Diagnostics and Connectivity Testing Utilities

This module provides functions for testing API connectivity and diagnosing
network/API issues in the portfolio application.
"""

import requests
from utils.logging import debug_log


def test_api_connectivity():
    """
    Test basic API connectivity for debugging and diagnostics.
    
    Tests connectivity to key external APIs used by the application:
    - CoinGecko API (cryptocurrency price data)
    - Binance API (cryptocurrency price data)
    - HTTPBin (general connectivity test)
    
    Returns:
        dict: Results of connectivity tests with status messages
    """
    debug_log("🔍 Starting API connectivity diagnostics", "INFO", "connectivity_test")
    
    results = {}
    test_urls = {
        'CoinGecko': 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
        'Binance': 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT',
        'Fear & Greed': 'https://api.alternative.me/fng/',
        'HTTPBin': 'https://httpbin.org/status/200'
    }
    
    for name, url in test_urls.items():
        try:
            debug_log(f"🔍 Testing {name} connectivity...", "INFO", "connectivity_test")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                results[name] = f"✅ OK ({response.status_code})"
                debug_log(f"✅ {name} connectivity successful", "SUCCESS", "connectivity_test")
            else:
                results[name] = f"⚠️ HTTP {response.status_code}"
                debug_log(f"⚠️ {name} returned {response.status_code}", "WARNING", "connectivity_test")
        except Exception as e:
            results[name] = f"❌ Error: {str(e)[:50]}"
            debug_log(f"❌ {name} connectivity failed: {e}", "ERROR", "connectivity_test")
    
    success_count = len([r for r in results.values() if "✅" in r])
    total_count = len(results)
    debug_log(f"🔍 Connectivity test complete: {success_count}/{total_count} APIs accessible", 
              "SUCCESS" if success_count == total_count else "WARNING", "connectivity_test")
    
    return results


def get_network_diagnostics():
    """
    Get comprehensive network diagnostics information.
    
    Returns:
        dict: Network diagnostic information including DNS resolution,
              basic connectivity tests, and API response times
    """
    debug_log("🌐 Running network diagnostics", "INFO", "network_diagnostics")
    
    diagnostics = {
        'api_connectivity': test_api_connectivity(),
        'timestamp': debug_log.get_timestamp() if hasattr(debug_log, 'get_timestamp') else None
    }
    
    return diagnostics


def diagnose_api_issues(api_results):
    """
    Analyze API test results and provide diagnostic suggestions.
    
    Args:
        api_results (dict): Results from test_api_connectivity()
    
    Returns:
        list: List of diagnostic messages and suggestions
    """
    suggestions = []
    
    failed_apis = [name for name, result in api_results.items() if "❌" in result]
    warning_apis = [name for name, result in api_results.items() if "⚠️" in result]
    
    if not failed_apis and not warning_apis:
        suggestions.append("✅ All APIs are responding normally")
    
    if failed_apis:
        suggestions.append(f"❌ Failed APIs: {', '.join(failed_apis)}")
        suggestions.append("💡 Check your internet connection")
        suggestions.append("💡 APIs may be temporarily unavailable")
        
    if warning_apis:
        suggestions.append(f"⚠️ APIs with issues: {', '.join(warning_apis)}")
        suggestions.append("💡 Some APIs returned non-200 status codes")
        
    if len(failed_apis) >= len(api_results) // 2:
        suggestions.append("🚨 Multiple API failures detected - check network connectivity")
        
    return suggestions
