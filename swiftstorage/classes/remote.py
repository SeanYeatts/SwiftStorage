# Copyright (c) 2025 Sean Yeatts. All rights reserved.

from __future__ import annotations


# IMPORTS ( STANDARD )
from abc import ABC as Abstract
from dataclasses import dataclass

# IMPORTS ( MODULE )
from swiftstorage.core.specification import StorageSpecification


# CLASSES
@dataclass(frozen=True)
class RemoteSpecification(StorageSpecification, Abstract):
    """Base class for non-local datastores ( ex: AWS S3 )."""
    
    delim: str = "/"
