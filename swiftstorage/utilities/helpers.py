# Copyright (c) 2025 Sean Yeatts, Inc. All rights reserved.

from __future__ import annotations


# IMPORTS ( STANDARD )
from dataclasses import dataclass


# NAMESPACES
class PrettyPrint:

    # CLASSES
    @dataclass
    class PrettyBytes:
        number: int
        units: str

    # STATIC METHODS
    @staticmethod
    def format_bytes(byte_value: bytes, precision: int = 3) -> PrettyBytes:
        if not isinstance(byte_value, (int, float)):
            raise TypeError("Input must be a numerical type (int or float).")
        
        units = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]
        size = float(byte_value)
        unit_index = 0

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
            
        number = round(size, precision)
        units = units[unit_index]
        return PrettyPrint.PrettyBytes(number, units)
