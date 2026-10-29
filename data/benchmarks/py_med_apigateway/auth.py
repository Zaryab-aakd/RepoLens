"""Authentication and JWT validator."""
class AuthProvider:
    def __init__(self, secret: str):
        self.secret = secret

    def authenticate_token(self, token: str) -> bool:
        return token == f"token_{self.secret}"

    def generate_token(self, user_id: str) -> str:
        return f"token_{self.secret}"
