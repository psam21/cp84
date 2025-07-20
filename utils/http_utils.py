"""
HTTP request utilities with error handling and retry logic.
"""
import requests
import time
from .logging import debug_log
from .rate_limiter import rate_limiter

def simple_api_request(url, headers=None, timeout=10, max_retries=3):
    """
    Simple API request function with retry logic - bypasses rate limiting for emergency use
    
    Args:
        url (str): URL to make request to
        headers (dict): Optional headers dictionary
        timeout (int): Request timeout in seconds
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        requests.Response or None: Response object if successful, None if failed
    """
    if headers is None:
        headers = {}
        
    for attempt in range(max_retries):
        try:
            debug_log(f"Making simple API request to {url} (attempt {attempt + 1}/{max_retries})", 
                     "INFO", "simple_api")
            
            response = requests.get(url, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                debug_log(f"✅ Simple API request successful", "SUCCESS", "simple_api")
                return response
            else:
                debug_log(f"❌ API request failed with status {response.status_code}", 
                         "WARNING", "simple_api")
                
        except requests.RequestException as e:
            debug_log(f"❌ Request exception: {str(e)}", "ERROR", "simple_api")
            
        if attempt < max_retries - 1:
            wait_time = (attempt + 1) * 2  # Exponential backoff
            debug_log(f"⏱️ Retrying in {wait_time} seconds...", "INFO", "simple_api")
            time.sleep(wait_time)
    
    debug_log(f"❌ All retry attempts failed for {url}", "ERROR", "simple_api")
    return None

def make_rate_limited_request(url, service_name, headers=None, timeout=10, max_retries=3):
    """
    Make an API request with rate limiting
    
    Args:
        url (str): URL to make request to
        service_name (str): Name of the service for rate limiting
        headers (dict): Optional headers dictionary
        timeout (int): Request timeout in seconds
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        requests.Response or None: Response object if successful, None if failed
    """
    if headers is None:
        headers = {}
        
    # Check if we can make request
    if not rate_limiter.can_make_request(service_name):
        debug_log(f"⏸️ Rate limited for {service_name}, skipping request", "WARNING", "rate_limited_api")
        return None
    
    for attempt in range(max_retries):
        try:
            debug_log(f"Making rate-limited API request to {service_name} (attempt {attempt + 1}/{max_retries})", 
                     "INFO", "rate_limited_api")
            
            response = requests.get(url, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                rate_limiter.record_request(service_name)
                debug_log(f"✅ Rate-limited API request successful", "SUCCESS", "rate_limited_api")
                return response
            elif response.status_code == 429:  # Rate limited
                backoff_delay = rate_limiter.get_backoff_delay(service_name, attempt)
                debug_log(f"⏸️ Rate limited by server, backing off {backoff_delay}s", 
                         "WARNING", "rate_limited_api")
                time.sleep(backoff_delay)
            else:
                debug_log(f"❌ API request failed with status {response.status_code}", 
                         "WARNING", "rate_limited_api")
                
        except requests.RequestException as e:
            debug_log(f"❌ Request exception: {str(e)}", "ERROR", "rate_limited_api")
            
        if attempt < max_retries - 1:
            wait_time = (attempt + 1) * 2
            debug_log(f"⏱️ Retrying in {wait_time} seconds...", "INFO", "rate_limited_api")
            time.sleep(wait_time)
    
    debug_log(f"❌ All retry attempts failed for {service_name}", "ERROR", "rate_limited_api")
    return None
