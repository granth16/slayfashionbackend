"""
Simple in-memory rate limiter
For production, use Redis-based rate limiting
"""
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Tuple


class RateLimiter:
    """
    Simple rate limiter to prevent OTP spam
    
    Usage:
        limiter = RateLimiter(max_requests=5, window_seconds=3600)
        if limiter.is_allowed("phone_number"):
            # Process request
        else:
            # Rate limit exceeded
    """
    
    def __init__(self, max_requests: int = 5, window_seconds: int = 3600):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests allowed in time window
            window_seconds: Time window in seconds (default: 1 hour)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        
        # Store: identifier -> list of request timestamps
        self.requests: Dict[str, list[datetime]] = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> Tuple[bool, str]:
        """
        Check if request is allowed
        
        Args:
            identifier: Unique identifier (e.g., phone number, IP address)
        
        Returns:
            (is_allowed, message)
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > window_start
        ]
        
        # Check limit
        if len(self.requests[identifier]) >= self.max_requests:
            return False, f"Rate limit exceeded. Max {self.max_requests} requests per {self.window_seconds // 60} minutes"
        
        # Add current request
        self.requests[identifier].append(now)
        
        return True, "OK"
    
    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests allowed"""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Count recent requests
        recent_requests = [
            req_time for req_time in self.requests.get(identifier, [])
            if req_time > window_start
        ]
        
        return max(0, self.max_requests - len(recent_requests))
    
    def clear(self, identifier: str):
        """Clear rate limit for identifier"""
        if identifier in self.requests:
            del self.requests[identifier]


# Global rate limiters
otp_rate_limiter = RateLimiter(max_requests=5, window_seconds=3600)  # 5 OTPs per hour
verify_rate_limiter = RateLimiter(max_requests=10, window_seconds=600)  # 10 verify attempts per 10 min

