import json
from typing import Any, Dict

class CustomJSONEncoder(json.JSONEncoder):
    """Deterministic JSON serialization for API responses."""
    def default(self, obj: Any) -> Any:
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

def serialize_response(data: Any) -> str:
    """
    Serializes data deterministically.
    Always uses sorted keys and consistent indentation.
    """
    return json.dumps(
        data,
        cls=CustomJSONEncoder,
        sort_keys=True,
        indent=2,
        ensure_ascii=False
    )
