"""
Utility functions
"""

from typing import TypeVar, Dict, Any, List

T = TypeVar("T")


def get_or_else(d: Dict[str, Any], path: List[str], default: T = None) -> T:
    """
    Get or else
    """
    current = d
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def num_to_id(num: int) -> str:
    """
    Convert the given integer to a meshtastic identifier
    string.
    """
    return "!" + hex(num)[2:]


def is_non_primitive(val):
    return not isinstance(val, (int, float, str, bool, type(None)))


def flat_dict(d, parent_key="", sep="."):
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flat_dict(v, new_key, sep))
        if is_non_primitive(v):
            continue
        else:
            items[new_key] = v
    return items
