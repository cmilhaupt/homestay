from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
from collections import defaultdict
import threading

class ExponentialBackoffLimiter:
    def __init__(self):
        self.violations = defaultdict(int)
        self.ban_until = defaultdict(lambda: datetime.min)
        self.request_times = defaultdict(list)
        self._lock = threading.Lock()

    def calculate_ban_duration(self, violations):
        """Calculate exponential backoff duration in seconds"""
        return 2 ** (violations - 1)  # 1s, 2s, 4s, 8s, 16s, etc.

    def is_banned(self, ip):
        with self._lock:
            return datetime.now() < self.ban_until[ip]

    def check_rate_limit(self, ip):
        with self._lock:
            now = datetime.now()
            
            # Clean up old request times
            self.request_times[ip] = [t for t in self.request_times[ip] 
                                    if now - t < timedelta(seconds=60)]
            
            # Add current request
            self.request_times[ip].append(now)
            
            # Check last 60 seconds
            if len(self.request_times[ip]) > 100:
                self.violations[ip] += 1
                ban_duration = self.calculate_ban_duration(self.violations[ip])
                self.ban_until[ip] = now + timedelta(seconds=ban_duration)
                return False
            
            # Check last second
            recent_requests = len([t for t in self.request_times[ip] 
                                 if now - t < timedelta(seconds=1)])
            if recent_requests > 3:
                self.violations[ip] += 1
                ban_duration = self.calculate_ban_duration(self.violations[ip])
                self.ban_until[ip] = now + timedelta(seconds=ban_duration)
                return False
            
            return True

limiter = ExponentialBackoffLimiter()
