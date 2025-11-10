"""
SwiftStorage
============

Copyright (c) 2025 Sean Yeatts. All rights reserved.

A simple way to interact with local and remote file systems. Easily extendable to support custom endpoints.
"""

from __future__ import annotations


# IMPORTS ( STANDARD )
import logging

# IMPORTS ( MODULE )
from .swiftstorage import *
from .core.specification import *
from .core.stream import *


# NULL LOGGER
logging.getLogger(__name__).addHandler(logging.NullHandler())
