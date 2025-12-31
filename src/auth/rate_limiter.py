"""
Rate limiting using Decorator Pattern.
"""
import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import HTTPException, Request, status
from functools import wraps

# In-memory storage for rate limiting
# Format: {identifier: [(timestamp, count)]}
_rate_limit_storage: Dict[str, list] = defaultdict(list)


class RateLimiter:
    """
    Rate limiter using sliding window algorithm.
    Stores request timestamps in memory.
    """

    def __init__(self, calls: int, period: int):
        """
        Initialize rate limiter.
        
        Args:
            calls: Maximum number of calls allowed
            period: Time period in seconds
        """
        self.calls = calls
        self.period = period

    def _get_identifier(self, request: Request) -> str:
        """
        Get identifier for rate limiting (IP address or user ID).
        
        Args:
            request: FastAPI request
            
        Returns:
            Identifier string
        """
        # Try to get user from request state (set by auth middleware)
        if hasattr(request.state, "user"):
            return f"user:{request.state.user.id}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

    def _clean_old_requests(self, requests: list, current_time: float):
        """
        Remove requests older than the time window.
        
        Args:
            requests: List of request timestamps
            current_time: Current timestamp
        """
        cutoff_time = current_time - self.period
        return [req_time for req_time in requests if req_time > cutoff_time]

    async def __call__(self, request: Request):
        """
        Check rate limit for the request.
        
        Args:
            request: FastAPI request
            
        Raises:
            HTTPException: If rate limit exceeded
        """
        identifier = self._get_identifier(request)
        current_time = time.time()
        
        # Get and clean old requests
        requests = _rate_limit_storage[identifier]
        requests = self._clean_old_requests(requests, current_time)
        
        # Check if limit exceeded
        if len(requests) >= self.calls:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.calls} requests per {self.period} seconds."
            )
        
        # Add current request
        requests.append(current_time)
        _rate_limit_storage[identifier] = requests


def rate_limit(calls: int = 60, period: int = 60):
    """
    Decorator for rate limiting endpoints.
    
    Args:
        calls: Maximum number of calls allowed
        period: Time period in seconds
        
    Returns:
        Decorated function
        
    Example:
        @app.get("/api/endpoint")
        @rate_limit(calls=10, period=60)
        async def my_endpoint():
            return {"message": "Hello"}
    """
    limiter = RateLimiter(calls, period)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            await limiter(request)
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
