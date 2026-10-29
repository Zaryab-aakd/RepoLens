"""Sliding window rate limiter."""
class RateLimiter:
    def __init__(self, max_requests: int):
        self.max_requests = max_requests
        self.counts = {}

    def is_allowed(self, client_ip: str) -> bool:
        count = self.counts.get(client_ip, 0)
        if count >= self.max_requests:
            return False
        self.counts[client_ip] = count + 1
        return True
