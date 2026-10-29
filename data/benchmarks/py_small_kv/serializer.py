"""Serialization helpers."""
import json

def serialize_payload(obj: dict) -> str:
    return json.dumps(obj)

def deserialize_payload(raw: str) -> dict:
    return json.loads(raw)
