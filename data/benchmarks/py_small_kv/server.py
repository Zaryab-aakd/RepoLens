"""KV Server Interface."""
from storage import StorageEngine
from serializer import serialize_payload, deserialize_payload

class KVServer:
    def __init__(self):
        self.engine = StorageEngine()

    def handle_request(self, command: str, key: str, value: str = None) -> str:
        if command == "SET":
            self.engine.set(key, value)
            return "OK"
        elif command == "GET":
            val = self.engine.get(key)
            return val or "NIL"
        return "ERR"
