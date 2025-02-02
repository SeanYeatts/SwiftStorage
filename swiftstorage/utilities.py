# Copyright (c) 2025 Sean Yeatts, Inc. All rights reserved.

from __future__ import annotations


# FUNCTIONS
def pretty_print_bytes(byte_value: bytes, decimals: int = 3) -> tuple[float, str]:
    """Auto-scales a raw byte value to be represented in a human-readable format.
    Returns a tuple containing the result and its unit suffix."""
    if not isinstance(byte_value, (int, float)):  # Ensure it's a number
        raise TypeError("Input must be a numerical type (int or float).")
    
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(byte_value)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return round(size, decimals), units[unit_index]
