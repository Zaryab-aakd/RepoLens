"""REST route dispatcher with decorators."""
from auth import AuthProvider
from rate_limiter import RateLimiter

class APIGateway:
    def __init__(self, secret: str, rate_limit: int = 100):
        self.auth = AuthProvider(secret)
        self.limiter = RateLimiter(rate_limit)

    def route_get(self, path: str, token: str, ip: str) -> str:
        if not self.limiter.is_allowed(ip):
            return "429 Too Many Requests"
        if not self.auth.authenticate_token(token):
            return "401 Unauthorized"
        return f"200 OK for {path}"

    def route_post(self, path: str, payload: dict, token: str) -> str:
        if not self.auth.authenticate_token(token):
            return "401 Unauthorized"
        return f"201 Created at {path}"
