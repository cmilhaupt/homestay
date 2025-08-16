import pytest
import time
from datetime import datetime, timedelta
from src.rate_limiting import ExponentialBackoffLimiter

def test_basic_rate_limit():
    limiter = ExponentialBackoffLimiter()
    ip = "127.0.0.1"
    
    # First 3 requests should succeed
    for _ in range(3):
        assert limiter.check_rate_limit(ip) == True
    
    # 4th request within same second should fail
    assert limiter.check_rate_limit(ip) == False
    
    # Wait 1 second and try again
    time.sleep(1.1)
    assert limiter.check_rate_limit(ip) == True

def test_extended_rate_limit():
    limiter = ExponentialBackoffLimiter()
    ip = "127.0.0.2"
    
    # Make 100 requests (should all succeed)
    for _ in range(100):
        assert limiter.check_rate_limit(ip) == True
        time.sleep(0.4)  # Space out requests to avoid per-second limit
    
    # 101st request should fail
    assert limiter.check_rate_limit(ip) == False

def test_exponential_backoff():
    limiter = ExponentialBackoffLimiter()
    ip = "127.0.0.3"
    
    # Trigger first violation
    for _ in range(4):  # Exceed per-second limit
        limiter.check_rate_limit(ip)
    
    assert limiter.is_banned(ip) == True
    first_ban = limiter.ban_until[ip]
    
    # Wait for ban to expire
    time.sleep(1.1)
    
    # Trigger second violation
    for _ in range(4):
        limiter.check_rate_limit(ip)
    
    # Second ban should be longer
    second_ban = limiter.ban_until[ip]
    assert (second_ban - datetime.now()) > (first_ban - datetime.now())

def test_ban_duration():
    limiter = ExponentialBackoffLimiter()
    ip = "127.0.0.4"
    
    # Trigger violation
    for _ in range(4):
        limiter.check_rate_limit(ip)
    
    assert limiter.is_banned(ip) == True
    
    # Wait for ban to expire
    time.sleep(1.1)
    assert limiter.is_banned(ip) == False

def test_multiple_ips():
    limiter = ExponentialBackoffLimiter()
    ip1 = "127.0.0.5"
    ip2 = "127.0.0.6"
    
    # Ban first IP
    for _ in range(4):
        limiter.check_rate_limit(ip1)
    
    # Second IP should still work
    assert limiter.check_rate_limit(ip2) == True
    assert limiter.is_banned(ip1) == True
    assert limiter.is_banned(ip2) == False

def test_request_cleanup():
    limiter = ExponentialBackoffLimiter()
    ip = "127.0.0.7"
    
    # Add some old requests
    old_time = datetime.now() - timedelta(minutes=2)
    limiter.request_times[ip] = [old_time for _ in range(10)]
    
    # Make a new request
    assert limiter.check_rate_limit(ip) == True
    
    # Old requests should be cleaned up
    assert len(limiter.request_times[ip]) == 1
