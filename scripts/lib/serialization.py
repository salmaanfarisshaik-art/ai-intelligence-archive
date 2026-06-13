import json
import yaml
from typing import Any, Dict, List

def save_json_deterministic(filepath: str, data: Any):
    """
    Saves JSON deterministically:
    - sorted keys
    - UTF-8 encoding
    - 2 space indent
    - trailing newline
    """
    from scripts.lib.file_utils import atomic_write
    content = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    atomic_write(filepath, content)

def save_yaml_deterministic(filepath: str, data: Any):
    """
    Saves YAML deterministically.
    """
    from scripts.lib.file_utils import atomic_write
    content = yaml.dump(data, default_flow_style=False, sort_keys=True, allow_unicode=True)
    if not content.endswith("\n"):
        content += "\n"
    atomic_write(filepath, content)

def save_markdown_deterministic(filepath: str, content: str):
    """
    Saves Markdown deterministically:
    - ensures UTF-8 encoding
    - trailing newline
    """
    from scripts.lib.file_utils import atomic_write
    if not content.endswith("\n"):
        content += "\n"
    atomic_write(filepath, content)
