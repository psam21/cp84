"""
Rate limiting utilities for API calls.
Thread-safe rate limiter with service-specific limits and exponential backoff.
"""
import time
import threading
from collections import defaultdict
from datetime import datetime, timedelta
from .logging import debug_log

class RateLimiter:
    """
    Thread-safe rate limiter for API calls with different limits per service
    """
    def __init__(self):
        self._calls = defaultdict(list)
        self._lock = threading.Lock()
        
        # Rate limits per service (calls per minute)
        self.limits = {
            'coingecko': 10,     # CoinGecko free tier: 10-50 calls/min
            'binance': 100,      # Binance: 1200 calls/min (weight-based)
            'default': 30        # Conservative default
        }
        
        # Backoff delays (seconds) when rate limited
        self.backoff_delays = {
            'coingecko': [1, 2, 5, 10],
            'binance': [0.5, 1, 2, 3],
            'default': [1, 3, 5, 10]
        }
    
    def can_make_request(self, service_name):
        """Check if we can make a request to the service"""
        with self._lock:
            now = time.time()
            service_key = service_name.lower()
            
            # Clean old entries (older than 1 minute)
            self._calls[service_key] = [
                call_time for call_time in self._calls[service_key] 
                if now - call_time < 60
            ]
            
            # Check if we're under the limit
            limit = self.limits.get(service_key, self.limits['default'])
            current_calls = len(self._calls[service_key])
            
            debug_log(f"🔍 Rate limit check for {service_name}: {current_calls}/{limit} calls in last minute", 
                     "INFO", "rate_limiter")
            
            return current_calls < limit
    
    def record_request(self, service_name):
        """Record a successful request"""
        with self._lock:
            self._calls[service_name.lower()].append(time.time())
            debug_log(f"📝 Recorded API call for {service_name}", "INFO", "rate_limiter")
    
    def get_backoff_delay(self, service_name, attempt=0):
        """Get backoff delay for rate limited service"""
        service_key = service_name.lower()
        delays = self.backoff_delays.get(service_key, self.backoff_delays['default'])
        delay_index = min(attempt, len(delays) - 1)
        return delays[delay_index]

    def get_status(self):
        """Get current rate limiting status for display"""
        status = {}
        services = ['coingecko', 'binance']
        
        for service in services:
            with self._lock:
                now = time.time()
                # Clean old entries
                self._calls[service] = [
                    call_time for call_time in self._calls[service] 
                    if now - call_time < 60
                ]
                
                current_calls = len(self._calls[service])
                limit = self.limits.get(service, self.limits['default'])
                
                status[service] = {
                    'current': current_calls,
                    'limit': limit,
                    'percentage': (current_calls / limit) * 100,
                    'available': limit - current_calls
                }
        
        return status

# Global rate limiter instance
rate_limiter = RateLimiter()
