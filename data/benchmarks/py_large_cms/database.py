"""Database ORM abstraction."""
class DatabaseConnection:
    def __init__(self, uri: str):
        self.uri = uri
        self.connected = False

    def connect(self) -> bool:
        self.connected = True
        return True

    def query(self, sql: str) -> list:
        return [{"id": 1, "query": sql}]
